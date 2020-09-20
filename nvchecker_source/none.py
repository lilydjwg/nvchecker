# MIT licensed
# Copyright (c) 2020 lilydjwg <lilydjwg@gmail.com>, et al.

from __future__ import annotations

from nvchecker.api import (
  BaseWorker, GetVersionError, RawResult,
)

class Worker(BaseWorker):
  async def run(self) -> None:
    exc = GetVersionError('no source specified')
    async with self.task_sem:
      for name, conf in self.tasks:
        await self.result_q.put(
          RawResult(name, exc, conf))
