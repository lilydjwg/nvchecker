# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

async def get_version(name, conf, **kwargs):
  return str(conf.get('manual')).strip() or None
