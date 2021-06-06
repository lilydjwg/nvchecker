# MIT licensed
# Copyright (c) 2020 Chih-Hsuan Yen <yan12125 at gmail dot com>

from typing import Dict, List, NamedTuple, Optional, Tuple
from urllib.request import parse_http_list
from urllib.parse import urljoin

from nvchecker.api import session, HTTPError

class AuthInfo(NamedTuple):
  service: Optional[str]
  realm: str

def parse_www_authenticate_header(header: str) -> Tuple[str, Dict[str, str]]:
  '''
  Parse WWW-Authenticate header used in OAuth2 authentication for container
  registries. This is NOT RFC-compliant!

  Simplified from http.parse_www_authenticate_header in Werkzeug (BSD license)
  '''
  auth_type, auth_info = header.split(None, 1)
  result = {}
  for item in parse_http_list(auth_info):
    name, value = item.split("=", 1)
    if value[:1] == value[-1:] == '"':
      value = value[1:-1]
    result[name] = value
  return auth_type, result

# Inspired by https://stackoverflow.com/a/51921869
# Reference: https://github.com/containers/image/blob/v5.6.0/docker/docker_client.go

class UnsupportedAuthenticationError(NotImplementedError):
  def __init__(self):
    super().__init__('Only Bearer authentication supported for now')

async def get_registry_auth_info(registry_host: str) -> AuthInfo:
  auth_service = auth_realm = None

  try:
    await session.get(f'https://{registry_host}/v2/')
    raise UnsupportedAuthenticationError  # No authentication needed
  except HTTPError as e:
    if e.code != 401:
      raise

    auth_type, auth_info = parse_www_authenticate_header(e.response.headers['WWW-Authenticate'])
    if auth_type.lower() != 'bearer':
      raise UnsupportedAuthenticationError

    # Although 'service' is needed as per https://docs.docker.com/registry/spec/auth/token/,
    # ghcr.io (GitHub container registry) does not provide it
    auth_service = auth_info.get('service')
    auth_realm = auth_info['realm']

    return AuthInfo(auth_service, auth_realm)

async def get_container_tags(info: Tuple[str, str, AuthInfo]) -> List[str]:
  image_path, registry_host, auth_info = info

  auth_params = {
    'scope': f'repository:{image_path}:pull',
  }
  if auth_info.service:
    auth_params['service'] = auth_info.service
  res = await session.get(auth_info.realm, params=auth_params)
  token = res.json()['token']

  tags = []
  url = f'https://{registry_host}/v2/{image_path}/tags/list'

  while True:
    res = await session.get(url, headers={
      'Authorization': f'Bearer {token}',
      'Accept': 'application/json',
    })
    tags += res.json()['tags']
    link = res.headers.get('Link')
    if link is None:
      break
    else:
      url = urljoin(url, parse_next_link(link))

  return tags

def parse_next_link(value: str) -> str:
  ending = '>; rel="next"'
  if value.endswith(ending):
    return value[1:-len(ending)]
  else:
    raise ValueError(value)

async def get_version(name, conf, *, cache, **kwargs):
  image_path = conf.get('container', name)
  registry_host = conf.get('registry', 'docker.io')
  if registry_host == 'docker.io':
    registry_host = 'registry-1.docker.io'

  auth_info = await cache.get(registry_host, get_registry_auth_info)

  key = image_path, registry_host, auth_info
  return await cache.get(key, get_container_tags)
