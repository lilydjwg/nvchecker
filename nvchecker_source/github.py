# MIT licensed
# Copyright (c) 2013-2020, 2024 lilydjwg <lilydjwg@gmail.com>, et al.
#
import time
from urllib.parse import urlencode, parse_qs, urlparse
from typing import List, Tuple, Union, Optional
import asyncio

import structlog


def get_github_token(conf: dict, host: str, keymanager: KeyManager) -> Optional[str]:
    """
    Get GitHub token with the following priority:
    1. Token from config
    2. Token from keymanager
    3. Token from GITHUB_TOKEN environment variable
    
    Args:
        conf: Configuration dictionary
        host: GitHub host (e.g., "github.com")
        keymanager: KeyManager instance for managing tokens
    
    Returns:
        str or None: GitHub token if found, None otherwise
    """
    # Check config first
    token = conf.get('token')
    if token is not None:
        return token
    
    # Then check keymanager
    try:
        token = keymanager.get_key(host.lower(), 'github')
        if token:
            return token
    except Exception:
        pass
    
    # Finally check environment variable
    return os.environ.get('GITHUB_TOKEN')

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

    # Load token from config, keymanager or env GITHUB_TOKEN
    token = get_github_token(conf, host, keymanager)

    headers = {
        'Accept': 'application/vnd.github.quicksilver-preview+json',
    }
    
    if token:
        if token.startswith('github_pat_'):
            headers['Authorization'] = f'Bearer {token}'
        else:
            headers['Authorization'] = f'token {token}'

    use_latest_tag = conf.get('use_latest_tag', False)
    use_latest_release = conf.get('use_latest_release', False)
    include_prereleases = conf.get('include_prereleases', False)
    use_max_tag = conf.get('use_max_tag', False)
    use_release_name = conf.get('use_release_name', False)

    # Token requirement checks
    if any([use_latest_tag, (use_latest_release and include_prereleases), use_max_tag]) and not token:
        raise GetVersionError('token not given but it is required for this operation')

    try:
        if use_latest_tag:
            query = conf.get('query', '')
            result = await cache.get((host, repo, query, token), get_latest_tag)
            return await enhance_version_with_commit_info(result, host, repo, headers, use_commit_info)

        if use_latest_release:
            url = GITHUB_LATEST_RELEASE % (host, repo)
            try:
                data = await cache.get_json(url, headers=headers)
                if 'tag_name' not in data:
                    raise GetVersionError('No release found in upstream repository.')

                version = data['name'] if use_release_name else data['tag_name']
                result = RichResult(
                    version=version,
                    gitref=f"refs/tags/{data['tag_name']}",
                    url=data['html_url'],
                )
                return await enhance_version_with_commit_info(result, host, repo, headers, use_commit_info)
            except HTTPError as e:
                if e.code == 404:
                    raise GetVersionError(f'No releases found for repository {repo}. The repository might not have any releases yet.')
                raise

        if use_max_tag:
            url = GITHUB_MAX_TAG % (host, repo)
            try:
                data = await cache.get_json(url, headers=headers)
                tags: List[Union[str, RichResult]] = [
                    RichResult(
                        version=ref['ref'].split('/', 2)[-1],
                        gitref=ref['ref'],
                        revision=ref['object']['sha'],
                        url=f'https://github.com/{repo}/releases/tag/{ref["ref"].split("/", 2)[-1]}',
                    ) for ref in data
                ]
                if not tags:
                    raise GetVersionError('No tags found in upstream repository.')
                
                if use_commit_info:
                    return [await enhance_version_with_commit_info(
                        tag, host, repo, headers, use_commit_info
                    ) for tag in tags if isinstance(tag, RichResult)]
                return tags
            except HTTPError as e:
                if e.code == 404:
                    raise GetVersionError(f'No tags found for repository {repo}. The repository might not have any tags yet.')
                raise

        # Default: use commits
        br = conf.get('branch')
        path = conf.get('path')
        url = GITHUB_URL % (host, repo)
        parameters = {}
        if br:
            parameters['sha'] = br
        if path:
            parameters['path'] = path
        if parameters:
            url += '?' + urlencode(parameters)

        data = await cache.get_json(url, headers=headers)
        version = data[0]['commit']['committer']['date'].rstrip('Z').replace('-', '').replace(':', '').replace('T', '.')
        
        result = RichResult(
            version=version,
            revision=data[0]['sha'],
            url=data[0]['html_url'],
        )
        return await enhance_version_with_commit_info(result, host, repo, headers, use_commit_info)

    except HTTPError as e:
        if e.code == 404:
            raise GetVersionError(f'Repository {repo} not found or access denied.')
        elif e.code in [403, 429]:
            if n := check_ratelimit(e, name):
                raise GetVersionError(f'Rate limited. Try again in {n} seconds or use an API token.')
            raise GetVersionError('Rate limit exceeded. Please use an API token to increase the allowance.')
        raise

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