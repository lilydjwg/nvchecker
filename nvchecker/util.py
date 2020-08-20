# MIT licensed
# Copyright (c) 2020 lilydjwg <lilydjwg@gmail.com>, et al.

from __future__ import annotations

import asyncio
from asyncio import Queue
import contextlib
from typing import (
  Dict, Optional, List, AsyncGenerator, NamedTuple, Union,
  Any, Tuple, Callable, Coroutine, Hashable,
  TYPE_CHECKING,
)
from pathlib import Path
import contextvars

import toml
import structlog

from .httpclient import session # type: ignore
from .ctxvars import tries as ctx_tries
from .ctxvars import proxy as ctx_proxy
from .ctxvars import user_agent as ctx_ua

logger = structlog.get_logger(logger_name=__name__)

Entry = Dict[str, Any]
Entries = Dict[str, Entry]
VersData = Dict[str, str]
VersionResult = Union[None, str, List[str], Exception]

class KeyManager:
  def __init__(
    self, file: Optional[Path],
  ) -> None:
    if file is not None:
      with file.open() as f:
        keys = toml.load(f)['keys']
    else:
      keys = {}
    self.keys = keys

  def get_key(self, name: str) -> Optional[str]:
    return self.keys.get(name)

class RawResult(NamedTuple):
  name: str
  version: VersionResult
  conf: Entry

class Result(NamedTuple):
  name: str
  version: str
  conf: Entry

class BaseWorker:
  def __init__(
    self,
    token_q: Queue[bool],
    result_q: Queue[RawResult],
    tasks: List[Tuple[str, Entry]],
    keymanager: KeyManager,
  ) -> None:
    self.token_q = token_q
    self.result_q = result_q
    self.keymanager = keymanager
    self.tasks = tasks

  @contextlib.asynccontextmanager
  async def acquire_token(self) -> AsyncGenerator[None, None]:
    token = await self.token_q.get()
    logger.debug('got token')
    try:
      yield
    finally:
      await self.token_q.put(token)
      logger.debug('return token')


class AsyncCache:
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
    key = '_jsonurl', url, tuple(sorted(headers.items()))
    return await self.get(
      key , self._get_json) # type: ignore

  async def get(
    self,
    key: Hashable,
    func: Callable[[Hashable], Coroutine[Any, Any, Any]],
  ) -> Any:
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
      async with self.acquire_token():
        version = await self.func(
          name, entry,
          cache = self.cache,
          keymanager = self.keymanager,
        )
      await self.result_q.put(RawResult(name, version, entry))
    except Exception as e:
      await self.result_q.put(RawResult(name, e, entry))

class GetVersionError(Exception):
  def __init__(self, msg: str, **kwargs: Any) -> None:
    self.msg = msg
    self.kwargs = kwargs
