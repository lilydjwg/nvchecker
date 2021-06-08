# MIT licensed
# Copyright (c) 2021 lilydjwg <lilydjwg@gmail.com>, et al.

import asyncio
import string

from nvchecker.api import entry_waiter

class CombineFormat(string.Template):
  idpattern = '[0-9]+'

async def get_version(
  name, conf, *, cache, keymanager=None
):
  t = CombineFormat(conf['format'])
  from_ = conf['from']
  waiter = entry_waiter.get()
  entries = [waiter.wait(name) for name in from_]
  vers = await asyncio.gather(*entries)
  versdict = {str(i+1): v for i, v in enumerate(vers)}
  return t.substitute(versdict)
