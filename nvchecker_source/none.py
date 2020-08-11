# MIT licensed
# Copyright (c) 2020 lilydjwg <lilydjwg@gmail.com>, et al.

from __future__ import annotations

import structlog
from nvchecker.util import BaseWorker

logger = structlog.get_logger(logger_name=__name__)

class Worker(BaseWorker):
  async def run(self) -> None:
    async with self.acquire_token():
      for name, _ in self.tasks:
        logger.error('no source specified', name=name)
