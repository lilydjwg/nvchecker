# MIT licensed
# Copyright (c) 2020 lilydjwg <lilydjwg@gmail.com>, et al.

from __future__ import annotations

import asyncio
from asyncio import Queue
from typing import (
  Dict, Optional, List, NamedTuple, Union,
  Any, Tuple, Callable, Coroutine, Hashable,
  TYPE_CHECKING,
)
from pathlib import Path
import contextvars
import abc

import toml
import structlog

from .httpclient import session
from .ctxvars import tries as ctx_tries
from .ctxvars import proxy as ctx_proxy
from .ctxvars import user_agent as ctx_ua

logger = structlog.get_logger(logger_name=__name__)

Entry = Dict[str, Any]
Entry.__doc__ = '''The configuration `dict` for an entry.'''
Entries = Dict[str, Entry]
VersData = Dict[str, str]
VersionResult = Union[None, str, List[str], Exception]
VersionResult.__doc__ = '''The result of a `get_version` check.

* `None` - No version found.
* `str` - A single version string is found.
* `List[str]` - Multiple version strings are found. :ref:`list options` will be applied.
* `Exception` - An error occurred.
'''

class FileLoadError(Exception):
  def __init__(self, kind, filename, exc):
    self.kind = kind
    self.filename = filename
    self.exc = exc

  def __str__(self):
    return f'failed to load {self.kind} {self.filename!r}: {self.exc}'

class KeyManager:
  '''Manages data in the keyfile.'''
  def __init__(
    self, file: Optional[Path],
  ) -> None:
    if file is not None:
      try:
        with file.open() as f:
          keys = toml.load(f)['keys']
      except (OSError, toml.TomlDecodeError) as e:
        raise FileLoadError('keyfile', str(file), e)
    else:
      keys = {}
    self.keys = keys

  def get_key(self, name: str) -> Optional[str]:
    '''Get the named key (token) in the keyfile.'''
    return self.keys.get(name)

class RawResult(NamedTuple):
  '''The unprocessed result from a check.'''
  name: str
  version: VersionResult
  conf: Entry

RawResult.name.__doc__ = 'The name (table name) of the entry.'
RawResult.version.__doc__ = 'The result from the check.'
RawResult.conf.__doc__ = 'The entry configuration (table content) of the entry.'

class Result(NamedTuple):
  name: str
  version: str
  conf: Entry

class BaseWorker:
  '''The base class for defining `Worker` classes for source plugins.

  .. py:attribute:: task_sem
      :type: asyncio.Semaphore

      This is the rate-limiting semaphore. Workers should acquire it while doing one unit of work.

  .. py:attribute:: result_q
      :type: Queue[RawResult]

      Results should be put into this queue.

  .. py:attribute:: tasks
      :type: List[Tuple[str, Entry]]

      A list of tasks for the `Worker` to complete. Every task consists of
      a tuple for the task name (table name in the configuration file) and the
      content of that table (as a `dict`).

  .. py:attribute:: keymanager
      :type: KeyManager

      The `KeyManager` for retrieving keys from the keyfile.
  '''
  def __init__(
    self,
    task_sem: asyncio.Semaphore,
    result_q: Queue[RawResult],
    tasks: List[Tuple[str, Entry]],
    keymanager: KeyManager,
  ) -> None:
    self.task_sem = task_sem
    self.result_q = result_q
    self.keymanager = keymanager
    self.tasks = tasks

  @abc.abstractmethod
  async def run(self) -> None:
    '''Run the `tasks`. Subclasses should implement this method.'''
    raise NotImplementedError

class AsyncCache:
  '''A cache for use with async functions.'''
  cache: Dict[Hashable, Any]
  lock: asyncio.Lock

  def __init__(self) -> None:
    self.cache = {}
    self.lock = asyncio.Lock()

  async def _get_json(
    self, key: Tuple[str, str, Tuple[Tuple[str, str], ...]],
  ) -> Any:
    _, url, headers = key
    res = await session.get(url, headers=dict(headers))
    return res.json()

  async def get_json(
    self, url: str, *,
    headers: Dict[str, str] = {},
  ) -> Any:
    '''Get specified ``url`` and return the response content as JSON.

    The returned data will be cached for reuse.
    '''
    key = '_jsonurl', url, tuple(sorted(headers.items()))
    return await self.get(
      key , self._get_json) # type: ignore

  async def get(
    self,
    key: Hashable,
    func: Callable[[Hashable], Coroutine[Any, Any, Any]],
  ) -> Any:
    '''Run async ``func`` and cache its return value by ``key``.

    The ``key`` should be hashable, and the function will be called with it as
    its sole argument. For multiple simultaneous calls with the same key, only
    one will actually be called, and others will wait and return the same
    (cached) value.
    '''
    async with self.lock:
      cached = self.cache.get(key)
      if cached is None:
        coro = func(key)
        fu = asyncio.create_task(coro)
        self.cache[key] = fu

    if asyncio.isfuture(cached): # pending
      return await cached # type: ignore
    elif cached is not None: # cached
      return cached
    else: # not cached
      r = await fu
      self.cache[key] = r
      return r

if TYPE_CHECKING:
  from typing_extensions import Protocol
  class GetVersionFunc(Protocol):
    async def __call__(
      self,
      name: str, conf: Entry,
      *,
      cache: AsyncCache,
      keymanager: KeyManager,
    ) -> VersionResult:
      ...
else:
  GetVersionFunc = Any

class FunctionWorker(BaseWorker):
  func: GetVersionFunc
  cache: AsyncCache

  def initialize(self, func: GetVersionFunc) -> None:
    self.func = func
    self.cache = AsyncCache()

  async def run(self) -> None:
    futures = []
    for name, entry in self.tasks:
      ctx = contextvars.copy_context()
      fu = ctx.run(self.run_one, name, entry)
      futures.append(fu)

    for fu2 in asyncio.as_completed(futures):
      await fu2

  async def run_one(
    self, name: str, entry: Entry,
  ) -> None:
    assert self.func is not None

    tries = entry.get('tries', None)
    if tries is not None:
      ctx_tries.set(tries)
    proxy = entry.get('proxy', None)
    if proxy is not None:
      ctx_proxy.set(proxy)
    ua = entry.get('user_agent', None)
    if ua is not None:
      ctx_ua.set(ua)

    try:
      async with self.task_sem:
        version = await self.func(
          name, entry,
          cache = self.cache,
          keymanager = self.keymanager,
        )
      await self.result_q.put(RawResult(name, version, entry))
    except Exception as e:
      await self.result_q.put(RawResult(name, e, entry))

class GetVersionError(Exception):
  '''An error occurred while getting version information.

  Raise this when a known bad situation happens.

  :param msg: The error message.
  :param kwargs: Arbitrary additional context for the error.
  '''
  def __init__(self, msg: str, **kwargs: Any) -> None:
    self.msg = msg
    self.kwargs = kwargs
