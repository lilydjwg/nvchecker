# MIT licensed
# Copyright (c) 2020 lilydjwg <lilydjwg@gmail.com>, et al.

from __future__ import annotations

import asyncio
from asyncio import Queue
import contextlib
from typing import (
  Dict, Optional, List, AsyncGenerator, NamedTuple, Union,
  Any, Tuple, Coroutine, Callable,
  TYPE_CHECKING,
)
from pathlib import Path

import toml

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
    try:
      yield
    finally:
      await self.token_q.put(token)

if TYPE_CHECKING:
  from typing_extensions import Protocol
  class GetVersionFunc(Protocol):
    async def __call__(
      self,
      name: str, conf: Entry,
      *,
      keymanager: KeyManager,
    ) -> VersionResult:
      ...
else:
  GetVersionFunc = Any

Cacher = Callable[[str, Entry], str]

class FunctionWorker(BaseWorker):
  func = None
  cacher = None

  cache: Dict[str, Union[
    VersionResult,
    asyncio.Task,
  ]]
  lock: asyncio.Lock

  def set_func(
    self,
    func: GetVersionFunc,
    cacher: Optional[Cacher],
  ) -> None:
    self.func = func
    self.cacher = cacher
    if cacher:
      self.cache = {}
      self.lock = asyncio.Lock()

  async def run(self) -> None:
    assert self.func is not None
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
        if self.cacher:
          version = await self.run_one_may_cache(
            name, entry)
        else:
          version = await self.func(
            name, entry, keymanager = self.keymanager,
          )
      await self.result_q.put(RawResult(name, version, entry))
    except Exception as e:
      await self.result_q.put(RawResult(name, e, entry))

  async def run_one_may_cache(
    self, name: str, entry: Entry,
  ) -> VersionResult:
    assert self.cacher is not None
    assert self.func is not None

    key = self.cacher(name, entry)

    async with self.lock:
      cached = self.cache.get(key)
      if cached is None:
        coro = self.func(
          name, entry, keymanager = self.keymanager,
        )
        fu = asyncio.create_task(coro)
        self.cache[key] = fu

    if asyncio.isfuture(cached): # pending
      return await cached # type: ignore
    elif cached is not None: # cached
      return cached # type: ignore
    else: # not cached
      version = await fu
      self.cache[key] = version
      return version
