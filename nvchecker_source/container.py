# MIT licensed
# Copyright (c) 2020 Chih-Hsuan Yen <yan12125 at gmail dot com>

from typing import Dict, List, NamedTuple, Optional, Tuple
from urllib.request import parse_http_list
from urllib.parse import urljoin
import json

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
  token = await get_auth_token(auth_info, image_path)
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


async def get_auth_token(auth_info, image_path):
  auth_params = {
    'scope': f'repository:{image_path}:pull',
  }
  if auth_info.service:
    auth_params['service'] = auth_info.service
  res = await session.get(auth_info.realm, params=auth_params)
  token = res.json()['token']
  return token


def parse_next_link(value: str) -> str:
  ending = '>; rel="next"'
  if value.endswith(ending):
    return value[1:-len(ending)]
  else:
    raise ValueError(value)


async def get_container_tag_update_time(info: Tuple[str, str, str, AuthInfo]):
  '''
  Find the update time of a container tag.

  In fact, it's the creation time of the image ID referred by the tag. Tag itself does not have any update time.
  '''
  image_path, image_tag, registry_host, auth_info = info
  token = await get_auth_token(auth_info, image_path)

  # HTTP headers
  headers = {
    'Authorization': f'Bearer {token}',
    # Prefer Image Manifest Version 2, Schema 2: https://distribution.github.io/distribution/spec/manifest-v2-2/
    'Accept': ', '.join([
      'application/vnd.oci.image.manifest.v1+json',
      'application/vnd.oci.image.index.v1+json',
      'application/vnd.docker.distribution.manifest.v2+json',
      'application/vnd.docker.distribution.manifest.list.v2+json',
      'application/json',
    ]),
  }

  # Get tag manifest
  url = f'https://{registry_host}/v2/{image_path}/manifests/{image_tag}'
  res = await session.get(url, headers=headers)
  data = res.json()
  # Schema 1 returns the creation time in the response
  if data['schemaVersion'] == 1:
    return json.loads(data['history'][0]['v1Compatibility'])['created']

  # For schema 2, we have to fetch the config's blob
  # For multi-arch images, multiple manifests are bounded with the same tag. We should choose one and then request
  # the manifest's detail
  if data.get('manifests'):
    # It's quite hard to find the manifest matching with current CPU architecture and system.
    # For now we just choose the first and it should probably work for most cases
    image_digest = data['manifests'][0]['digest']
    url = f'https://{registry_host}/v2/{image_path}/manifests/{image_digest}'
    res = await session.get(url, headers=headers)
    data = res.json()

  digest = data['config']['digest']
  url = f'https://{registry_host}/v2/{image_path}/blobs/{digest}'
  res = await session.get(url, headers=headers)
  data = res.json()
  return data['created']


async def get_version(name, conf, *, cache, **kwargs):
  image_path = conf.get('container', name)
  image_tag = None
  # image tag is optional
  if ':' in image_path:
    image_path, image_tag = image_path.split(':', 1)
  registry_host = conf.get('registry', 'docker.io')
  if registry_host == 'docker.io':
    registry_host = 'registry-1.docker.io'

  auth_info = await cache.get(registry_host, get_registry_auth_info)

  # if a tag is given, return the tag's update time, otherwise return the image's tag list
  if image_tag:
    key = image_path, image_tag, registry_host, auth_info
    return await cache.get(key, get_container_tag_update_time)
  key = image_path, registry_host, auth_info
  return await cache.get(key, get_container_tags)
