# MIT licensed
# Copyright (c) 2020 lilydjwg <lilydjwg@gmail.com>, et al.

from __future__ import annotations

from asyncio import Queue
import contextlib
from typing import (
  Dict, Optional, List, AsyncGenerator, NamedTuple, Union,
  Any, Tuple,
)
from pathlib import Path

import toml

Entry = Dict[str, Any]
Entries = Dict[str, Entry]
VersData = Dict[str, str]

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

class RawResult(NamedTuple):
  name: str
  version: Union[Exception, List[str], str]
  conf: Entry

class Result(NamedTuple):
  name: str
  version: str
  conf: Entry

def conf_cacheable_with_name(key):
  def get_cacheable_conf(name, conf):
    conf = dict(conf)
    conf[key] = conf.get(key) or name
    return conf
  return get_cacheable_conf
