# MIT licensed
# Copyright (c) 2013-2020, 2024 lilydjwg <lilydjwg@gmail.com>, et al.

import time
from urllib.parse import urlencode, parse_qs, urlparse
from typing import List, Tuple, Union, Optional
import asyncio

import structlog

from nvchecker.api import (
  VersionResult, Entry, AsyncCache, KeyManager,
  HTTPError, session, RichResult, GetVersionError,
)

logger = structlog.get_logger(logger_name=__name__)
ALLOW_REQUEST = None
RATE_LIMITED_ERROR = False

GITHUB_URL = 'https://api.%s/repos/%s/commits'
GITHUB_LATEST_RELEASE = 'https://api.%s/repos/%s/releases/latest'
GITHUB_MAX_TAG = 'https://api.%s/repos/%s/git/refs/tags'
GITHUB_GRAPHQL_URL = 'https://api.%s/graphql'

async def get_commit_count(url: str, headers: dict) -> int:
    """Get the total commit count using pagination."""
    params = {'per_page': '1'}
    
    response = await session.get(
        url,
        params=params,
        headers=headers
    )
    
    commit_count = 1
    if 'Link' in response.headers:
        link_header = response.headers['Link']
        for link in link_header.split(', '):
            if 'rel="last"' in link:
                url = link[link.find("<") + 1:link.find(">")]
                query_params = parse_qs(urlparse(url).query)
                if 'page' in query_params:
                    commit_count = int(query_params['page'][0])
                break
    
    return commit_count

async def get_version(name, conf, **kwargs):
  global RATE_LIMITED_ERROR, ALLOW_REQUEST

  if RATE_LIMITED_ERROR:
    raise RuntimeError('rate limited')

  if ALLOW_REQUEST is None:
    ALLOW_REQUEST = asyncio.Event()
    ALLOW_REQUEST.set()

  for _ in range(2): # retry once
    try:
      await ALLOW_REQUEST.wait()
      return await get_version_real(name, conf, **kwargs)
    except HTTPError as e:
      if e.code in [403, 429]:
        if n := check_ratelimit(e, name):
          ALLOW_REQUEST.clear()
          await asyncio.sleep(n+1)
          ALLOW_REQUEST.set()
          continue
        RATE_LIMITED_ERROR = True
      raise

async def enhance_version_with_commit_info(
    result: RichResult,
    host: str,
    repo: str,
    headers: dict,
    use_commit_info: bool
) -> RichResult:
    """Add commit count and SHA to version if use_commit_info is True."""
    if not use_commit_info:
        return result
        
    url = GITHUB_URL % (host, repo)
    commit_count = await get_commit_count(url, headers)
    
    # Create new version string with commit info
    enhanced_version = f"{result.version}.r{commit_count}.g{result.revision[:9]}"
    
    return RichResult(
        version=enhanced_version,
        gitref=result.gitref,
        revision=result.revision,
        url=result.url
    )

async def get_version_real(
    name: str, conf: Entry, *,
    cache: AsyncCache, keymanager: KeyManager,
    **kwargs,
) -> VersionResult:
    repo = conf['github']
    host = conf.get('host', "github.com")
    use_commit_info = conf.get('use_commit_info', False)

    # Load token from config or keymanager
    token = conf.get('token')
    if token is None:
        token = keymanager.get_key(host.lower(), 'github')

    # Set up headers with proper authentication
    headers = {
        'Accept': 'application/vnd.github.quicksilver-preview+json',
    }
    
    # Now ensure we always add Authorization header if we have a token
    if token:
        if token.startswith('github_pat_'):  # Personal Access Token (Fine-grained)
            headers['Authorization'] = f'Bearer {token}'
        else:
            headers['Authorization'] = f'token {token}'

    use_latest_tag = conf.get('use_latest_tag', False)
    if use_latest_tag:
        if not token:
            raise GetVersionError('token not given but it is required')

        query = conf.get('query', '')
        result = await cache.get((host, repo, query, token), get_latest_tag)
        return await enhance_version_with_commit_info(result, host, repo, headers, use_commit_info)

    use_latest_release = conf.get('use_latest_release', False)
    include_prereleases = conf.get('include_prereleases', False)
    use_release_name = conf.get('use_release_name', False)
    if use_latest_release and include_prereleases:
        if not token:
            raise GetVersionError('token not given but it is required')

        result = await cache.get(
            (host, repo, token, use_release_name),
            get_latest_release_with_prereleases)
        return await enhance_version_with_commit_info(result, host, repo, headers, use_commit_info)

    br = conf.get('branch')
    path = conf.get('path')
    use_max_tag = conf.get('use_max_tag', False)
    
    # Check for token requirement early for max_tag
    if use_max_tag and not token:
        raise GetVersionError('token not given but it is required for max_tag')

    if use_latest_release:
        url = GITHUB_LATEST_RELEASE % (host, repo)
    elif use_max_tag:
        url = GITHUB_MAX_TAG % (host, repo)
    else:
        url = GITHUB_URL % (host, repo)
        parameters = {}
        if br:
            parameters['sha'] = br
        if path:
            parameters['path'] = path
        url += '?' + urlencode(parameters)

    data = await cache.get_json(url, headers=headers)

    if use_max_tag:
        tags: List[Union[str, RichResult]] = [
            RichResult(
                version=ref['ref'].split('/', 2)[-1],
                gitref=ref['ref'],
                revision=ref['object']['sha'],
                url=f'https://github.com/{repo}/releases/tag/{ref["ref"].split("/", 2)[-1]}',
            ) for ref in data
        ]
        if not tags:
            raise GetVersionError('No tag found in upstream repository.')
            
        # Enhance all tags with commit info if enabled
        if use_commit_info:
            enhanced_tags = []
            for tag in tags:
                if isinstance(tag, RichResult):
                    enhanced_tag = await enhance_version_with_commit_info(
                        tag, host, repo, headers, use_commit_info
                    )
                    enhanced_tags.append(enhanced_tag)
                else:
                    enhanced_tags.append(tag)
            return enhanced_tags
        return tags

    if use_latest_release:
        if 'tag_name' not in data:
            raise GetVersionError('No release found in upstream repository.')

        if use_release_name:
            version = data['name']
        else:
            version = data['tag_name']

        result = RichResult(
            version=version,
            gitref=f"refs/tags/{data['tag_name']}",
            url=data['html_url'],
        )
        return await enhance_version_with_commit_info(result, host, repo, headers, use_commit_info)

    else:
        version = data[0]['commit']['committer']['date'].rstrip('Z').replace('-', '').replace(':', '').replace('T', '.')
        
        result = RichResult(
            version=version,
            revision=data[0]['sha'],
            url=data[0]['html_url'],
        )
        return await enhance_version_with_commit_info(result, host, repo, headers, use_commit_info)

def check_ratelimit(exc: HTTPError, name: str) -> Optional[int]:
    res = exc.response
    if not res:
        raise exc

    if v := res.headers.get('retry-after'):
        n = int(v)
        logger.warning('retry-after', n=n)
        return n

    # default -1 is used to re-raise the exception
    n = int(res.headers.get('X-RateLimit-Remaining', -1))
    if n == 0:
        reset = int(res.headers.get('X-RateLimit-Reset'))
        logger.error(f'rate limited, resetting at {time.ctime(reset)}. '
                    'Or get an API token to increase the allowance if not yet',
                    name=name,
                    reset=reset)
        return None

    raise exc