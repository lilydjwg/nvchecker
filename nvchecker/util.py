# MIT licensed
# Copyright (c) 2020 lilydjwg <lilydjwg@gmail.com>, et al.

from __future__ import annotations

import asyncio
from asyncio import Queue
import contextlib
from typing import (
  Dict, Optional, List, AsyncGenerator, NamedTuple, Union,
  Any, Tuple, Callable, TypeVar, Coroutine, Generic,
  TYPE_CHECKING,
)
from pathlib import Path

import toml
import structlog

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
    tries: int,
    keymanager: KeyManager,
  ) -> None:
    self.token_q = token_q
    self.result_q = result_q
    self.tries = tries
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

T = TypeVar('T')
S = TypeVar('S')

class AsyncCache(Generic[T, S]):
  cache: Dict[T, Union[S, asyncio.Task]]
  lock: asyncio.Lock

  def __init__(self) -> None:
    self.cache = {}
    self.lock = asyncio.Lock()

  async def get(
    self,
    key: T,
    func: Callable[[T], Coroutine[None, None, S]],
  ) -> S:
    async with self.lock:
      cached = self.cache.get(key)
      if cached is None:
        coro = func(key)
        fu = asyncio.create_task(coro)
        self.cache[key] = fu

    if asyncio.isfuture(cached): # pending
      return await cached # type: ignore
    elif cached is not None: # cached
      return cached # type: ignore
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
    futures = [
      self.run_one(name, entry)
      for name, entry in self.tasks
    ]
    for fu in asyncio.as_completed(futures):
      await fu

  async def run_one(
    self, name: str, entry: Entry,
  ) -> None:
    assert self.func is not None

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
