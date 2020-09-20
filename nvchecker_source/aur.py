# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

from datetime import datetime
import asyncio
from typing import Iterable, Dict, List, Tuple, Any, Optional

from nvchecker.api import (
  session, GetVersionError, VersionResult,
  Entry, BaseWorker, RawResult,
)

AUR_URL = 'https://aur.archlinux.org/rpc/'

class AurResults:
  cache: Dict[str, Optional[Dict[str, Any]]]

  def __init__(self) -> None:
    self.cache = {}

  async def get_multiple(
    self,
    aurnames: Iterable[str],
  ) -> Dict[str, Optional[Dict[str, Any]]]:
    params = [('v', '5'), ('type', 'info')]
    params.extend(('arg[]', name) for name in aurnames
                  if name not in self.cache)
    res = await session.get(AUR_URL, params=params)
    data = res.json()
    new_results = {r['Name']: r for r in data['results']}

    cache = self.cache
    cache.update(new_results)
    cache.update(
      (name, None)
      for name in set(aurnames) - new_results.keys()
    )

    return {name: cache[name] for name in aurnames
            if name in cache}

class Worker(BaseWorker):
  # https://wiki.archlinux.org/index.php/Aurweb_RPC_interface#Limitations
  batch_size = 100

  async def run(self) -> None:
    tasks = self.tasks
    n_batch, left = divmod(len(tasks), self.batch_size)
    if left > 0:
      n_batch += 1

    aur_results = AurResults()

    ret = []
    for i in range(n_batch):
      s = i * self.batch_size
      batch = tasks[s : s+self.batch_size]
      fu = self._run_batch(batch, aur_results)
      ret.append(fu)

    await asyncio.wait(ret)

  async def _run_batch(
    self,
    batch: List[Tuple[str, Entry]],
    aur_results: AurResults,
  ) -> None:
    task_by_name: Dict[str, Entry] = dict(self.tasks)

    async with self.task_sem:
      results = await _run_batch_impl(batch, aur_results)
      for name, version in results.items():
        r = RawResult(name, version, task_by_name[name])
        await self.result_q.put(r)

async def _run_batch_impl(
  batch: List[Tuple[str, Entry]],
  aur_results: AurResults,
) -> Dict[str, VersionResult]:
  aurnames = {conf.get('aur', name) for name, conf in batch}
  results = await aur_results.get_multiple(aurnames)

  ret: Dict[str, VersionResult] = {}

  for name, conf in batch:
    aurname = conf.get('aur', name)
    use_last_modified = conf.get('use_last_modified', False)
    strip_release = conf.get('strip_release', False)

    result = results.get(aurname)

    if result is None:
      ret[name] = GetVersionError('AUR upstream not found')
      continue

    version = result['Version']
    if use_last_modified:
      version += '-' + datetime.utcfromtimestamp(result['LastModified']).strftime('%Y%m%d%H%M%S')
    if strip_release and '-' in version:
      version = version.rsplit('-', 1)[0]

    ret[name] = version

  return ret

