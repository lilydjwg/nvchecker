# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

def get_version(name, conf, callback):
  callback(name, conf.get('manual'))
