# MIT licensed
# Copyright (c) 2019 lilydjwg <lilydjwg@gmail.com>, et al.

from .. import __version__
from urllib.parse import urlparse
import os

DEFAULT_USER_AGENT = 'lilydjwg/nvchecker %s' % __version__


def use_proxy(url, nv_config):
  """
  determine whether to use the proxy for a url

  get no_proxy from config or environment and return True if
  hostname of url does not match it
  """
  no_proxies =  nv_config.get('no_proxy')
  if no_proxies is None:
    no_proxies = get_environment_no_proxy()
  if no_proxies is None:
    return True
  no_proxies = no_proxies.split(',')
  parsed_url = urlparse(url)
  for no_proxy in no_proxies:
    if parsed_url.hostname.endswith(no_proxy):
      return False
  return True

def get_environment_http_proxy():
  http_proxy = os.environ.get('HTTP_PROXY')
  if http_proxy is None:
    http_proxy = os.environ.get('http_proxy')
  return http_proxy

def get_environment_no_proxy():
  no_proxy = os.environ.get('NO_PROXY')
  if no_proxy is None:
    no_proxy = os.environ.get('no_proxy')
  return no_proxy
