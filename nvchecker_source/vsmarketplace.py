# MIT licensed
# Copyright (c) 2013-2021 Th3Whit3Wolf <the.white.wolf.is.1337@gmail.com>, et al.

from nvchecker.api import (
  VersionResult, Entry, AsyncCache, KeyManager,
  TemporaryError, session, RichResult, GetVersionError,
)

API_URL = 'https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery'

HEADERS = {
  'Accept': 'application/json;api-version=6.1-preview.1',
  'Content-Type': 'application/json'
}

async def get_version(name: str, conf: Entry, *, cache: AsyncCache, **kwargs):
  name = conf.get('vsmarketplace') or name

  q = {
    'filters': [
      {
        'criteria': [
          {
            'filterType': 8,
            'value': 'Microsoft.VisualStudio.Code'
          },
          {
            'filterType': 7,
            'value': name
          },
          {
            'filterType': 12,
            'value': '4096'
          }
        ],
        'pageNumber': 1,
        'pageSize': 2,
        'sortBy': 0,
        'sortOrder': 0
      }
    ],
    'assetTypes': [],
    'flags': 946
  }

  res = await session.post(
    API_URL,
    headers = HEADERS,
    json = q,
  )
  j = res.json()

  version = j['results'][0]['extensions'][0]['versions'][0]['version']
  return RichResult(
    version = version,
    url = f'https://marketplace.visualstudio.com/items?itemName={name}',
  )
