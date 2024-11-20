import os  # Added for environment variable access
import time
from urllib.parse import urlencode
from typing import List, Tuple, Union, Optional
import asyncio
import aiohttp

import structlog
from nvchecker.api import (
    VersionResult, Entry, AsyncCache, KeyManager,
    HTTPError, session, RichResult, GetVersionError,
)
DEFAULT_TIMEOUT = aiohttp.ClientTimeout(total=60)
logger = structlog.get_logger(logger_name=__name__)
ALLOW_REQUEST = None
RATE_LIMITED_ERROR = False
_http_client = None

GITHUB_GRAPHQL_URL = 'https://api.%s/graphql'

async def create_http_client():
    """Create a new aiohttp client session with proper configuration."""
    return aiohttp.ClientSession(timeout=DEFAULT_TIMEOUT)

async def get_http_client():
    """Initialize and return the HTTP client."""
    global _http_client
    if _http_client is not None:
        return _http_client

    # Create a new client session if none exists
    client = await create_http_client()        
    _http_client = client
    return _http_client

def create_rich_result(conf, commits, sha, **kwargs) -> RichResult:
    """
    Helper function to centralize the creation of a RichResult.
    Accepts any keyword arguments and passes them to RichResult.
    """
    if conf.get('use_commit_number', False):
        kwargs['version'] += f"+r{str(commits)}"
    if conf.get('use_commit_hash', False):
        kwargs['version'] += f"+g{sha[:9]}"
    return RichResult(**kwargs)

async def execute_github_query(host: str, owner: str, reponame: str, token: str) -> dict:
    """
    Execute GraphQL query against GitHub API and return the response data.
    Centralizes error handling and query execution.
    """
    client = await get_http_client()
    
    headers = {
        'Authorization': f'bearer {token}',
        'Content-Type': 'application/json',
    }
    query_vars = QUERY_GITHUB.replace("$owner", owner).replace("$name", reponame)
    client = await get_http_client()
    
    try:
        async with client.post(
            GITHUB_GRAPHQL_URL % host,
            headers=headers,
            json={'query': query_vars}
        ) as response:
            # Check response status
            response.raise_for_status()
            
            # Parse JSON response
            data = await response.json() 

            # Handle rate limiting headers
            remaining = response.headers.get('X-RateLimit-Remaining')
            if remaining and int(remaining) == 0:
                reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                logger.warning(
                    "GitHub API rate limit reached",
                    reset_time=time.ctime(reset_time)
                )

            # Check for GraphQL errors            
            if 'errors' in data:
                raise GetVersionError(f"GitHub API error: {data['errors']}")
            await client.close()
            return data['data']['repository']

    except Exception as e:
        logger.error("GitHub API request failed", error=str(e))
        raise

def get_github_token(conf: Entry, host: str, keymanager: KeyManager) -> Optional[str]:
    """Get GitHub token from config, keymanager, or environment."""
    token = conf.get('token')
    if token is None:
        token = keymanager.get_key(host.lower(), 'github')
    if token is None:
        token = os.environ.get('GITHUB_TOKEN')
    return token

async def get_version(name, conf, **kwargs):
    global RATE_LIMITED_ERROR

    if RATE_LIMITED_ERROR:
        raise RuntimeError('rate limited')

    try:
        return await _get_version_with_retry(name, conf, **kwargs)
    finally:
        await _cleanup_http_client()

async def _get_version_with_retry(name, conf, **kwargs):
    global ALLOW_REQUEST
    if ALLOW_REQUEST is None:
        ALLOW_REQUEST = asyncio.Event()
        ALLOW_REQUEST.set()

    for _ in range(2):  # retry once
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

async def _cleanup_http_client():
    """Clean up the global HTTP client if it exists."""
    global _http_client
    if _http_client is not None:
        await _http_client.close()
        _http_client = None

QUERY_GITHUB = """
query {
  rateLimit {
    limit
    remaining
    resetAt    
  }
  repository(owner: "$owner", name: "$name") {
    # Default branch commits
    defaultBranchRef {
      target {
        ... on Commit {
          history(first: 1) {
            totalCount
            edges {
              node {
                oid
                committedDate
              }
            }
          }
        }
      }
    }
    # All tags
    refs(refPrefix: "refs/tags/", first: 1, orderBy: {field: TAG_COMMIT_DATE, direction: DESC}) {
      edges {
        node {
          name          
          target {
            oid
            ... on Commit {              
              url         
            }
          }
        }
      }
    }
    # All releases (can't filter server-side)
releases(first: 100, orderBy: { field: CREATED_AT, direction: DESC }) {
      totalCount
      edges {
        node {
          name
          url          
          tagName
          isPrerelease
          isLatest
          createdAt
        }
      }
      pageInfo {
        hasNextPage
        endCursor
      }
    }
  }
}
"""

async def get_latest_tag(conf: Entry, key: Tuple[str, str, str, str]) -> RichResult:
    host, repo, query, token = key
    owner, reponame = repo.split('/')
    if not token:
        raise GetVersionError('token is required for latest tag query')

    repo_data = await execute_github_query(host, owner, reponame, token)
    refs = repo_data['refs']['edges']
    version = refs[0]['node']['name']
    revision = refs[0]['node']['target']['oid']
    commits = repo_data["defaultBranchRef"]["target"]["history"]["totalCount"]
    sha = repo_data["defaultBranchRef"]["target"]["history"]["edges"][0]["node"]["oid"]
    return create_rich_result(
        conf=conf,
        commits=commits,
        sha=sha,
        version=version,
        gitref=f"refs/tags/{version}",
        revision=revision,
        url=f'https://github.com/{repo}/releases/tag/{version}',
    )

async def get_version_real(
    name: str, conf: Entry, *,
    cache: AsyncCache, keymanager: KeyManager,
    **kwargs,
) -> VersionResult:
    repo = conf['github']
    owner, reponame = repo.split('/')
    host = conf.get('host', "github.com")
    token = get_github_token(conf, host, keymanager)

    use_latest_tag = conf.get('use_latest_tag', False)
    if use_latest_tag:
        if not token:
            raise GetVersionError('token not given but it is required')

        query = conf.get('query', '')
        return await cache.get((host, repo, query, token), get_latest_tag(conf))

    repo_data = await execute_github_query(host, owner, reponame, token)
    commits = repo_data["defaultBranchRef"]["target"]["history"]["totalCount"]
    sha = repo_data["defaultBranchRef"]["target"]["history"]["edges"][0]["node"]["oid"]

    use_max_tag = conf.get('use_max_tag', False)
    if use_max_tag:
        refs = repo_data['refs']['edges']
        tags: List[Union[str, RichResult]] = [
            create_rich_result(
                conf=conf,
                commits=commits,
                sha=sha,
                version=ref['node']['name'],
                gitref=f"refs/tags/{ref['node']['name']}",
                revision=ref['node']['target']['oid'],
                url=f'https://github.com/{repo}/releases/tag/{ref["node"]["name"]}',
            ) for ref in refs
        ]
        if not tags:
            raise GetVersionError('No tag found in upstream repository.')
        return tags
    use_latest_release = conf.get('use_latest_release', False)
    use_newest_release = conf.get('use_newest_release', False)
    include_prereleases = conf.get('use_prereleases', False)
    if use_latest_release or use_newest_release:
        if use_latest_release:
            releases = repo_data['releases']['edges']
            if not releases:
                raise GetVersionError('No release found in upstream repository.')
            if include_prereleases:
                latest_release = next(
                    (release['node'] for release in releases if release['node']['isLatest'] or release['node']['isPrerelease]']),
                    None
                )        
            else:
                latest_release = next(
                    (release['node'] for release in releases if release['node']['isLatest'] and not release['node']['isPrerelease']),
                    None
                )        

        elif use_newest_release:
            releases = repo_data['releases']['edges']
            latest_release = next(
                (release['node'] for release in releases),
                None
            )        


        use_release_name = conf.get('use_release_name', False)
        version = latest_release['name'] if use_release_name else latest_release['tagName']

        return create_rich_result(
            conf=conf,
            commits=commits,
            sha=sha,
            version=version,
            gitref=f"refs/tags/{latest_release['tagName']}",
            url=latest_release['url'],
        )
    else:
        commit = repo_data['defaultBranchRef']['target']['history']['edges'][0]['node']
        return create_rich_result(
            conf=conf,
            commits=commits,
            sha=sha,
            version=commit['committedDate'].rstrip('Z').replace('-', '').replace(':', '').replace('T', '.'),
            revision=commit['oid'],
            url=f'https://github.com/{repo}/commit/{commit["oid"]}',
        )

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
                 name = name,
                 reset = reset)
    return None

  raise exc
