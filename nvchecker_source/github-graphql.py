import os
import time
import aiohttp
from typing import List, Tuple, Union, Optional
from nvchecker.api import RichResult, Entry, KeyManager, GetVersionError, AsyncCache

async def get_github_token(conf: Entry, host: str, keymanager: KeyManager) -> Optional[str]:
    token = conf.get('token')
    if token is None:
        token = keymanager.get_key(host.lower(), 'github')
    if token is None:
        token = os.environ.get('GITHUB_TOKEN')
    return token

def create_rich_result(conf, commits, sha, **kwargs) -> RichResult:
    if conf.get('use_commit_number', False):
        kwargs['version'] += f"+r{str(commits)}"
    if conf.get('use_commit_hash', False):
        kwargs['version'] += f"+g{sha[:9]}"
    return RichResult(**kwargs)

async def get_version(
    name: str, conf: Entry, *,
    cache: AsyncCache, keymanager: KeyManager,
    **kwargs,
) -> RichResult:
    repo = conf['github']
    owner, reponame = repo.split('/')
    host = conf.get('host', "github.com")
    token = await get_github_token(conf, host, keymanager)

    if not token:
        raise GetVersionError('token not given but it is required')

    GITHUB_GRAPHQL_URL = 'https://api.github.com/graphql'
    query = """
    query {
      repository(owner: "$owner", name: "$name") {
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
        refs(refPrefix: "refs/tags/", first: 100, orderBy: {field: TAG_COMMIT_DATE, direction: DESC}) {
          edges {
            node {
              name          
              target {
                oid
              }
            }
          }
        }
        releases(first: 100, orderBy: { field: CREATED_AT, direction: DESC }) {
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
        }
      }
    }
    """

    query_vars = query.replace("$owner", owner).replace("$name", reponame)
    
    async with aiohttp.ClientSession() as session:
        headers = {
            'Authorization': f'bearer {token}',
            'Content-Type': 'application/json',
        }

        try:
            async with session.post(
                GITHUB_GRAPHQL_URL,
                headers=headers,
                json={'query': query_vars}
            ) as response:
                data = await response.json()
                
                if 'errors' in data:
                    raise GetVersionError(f"GitHub API error: {data['errors']}")
                
                repo_data = data['data']['repository']
                commits = repo_data["defaultBranchRef"]["target"]["history"]["totalCount"]
                sha = repo_data["defaultBranchRef"]["target"]["history"]["edges"][0]["node"]["oid"]

                # Latest Tag Strategy
                if conf.get('use_latest_tag', False):
                    refs = repo_data['refs']['edges']
                    if not refs:
                        raise GetVersionError('No tag found in upstream repository.')
                    latest_tag = refs[0]['node']
                    return create_rich_result(
                        conf=conf,
                        commits=commits,
                        sha=sha,
                        version=latest_tag['name'],
                        gitref=f"refs/tags/{latest_tag['name']}",
                        revision=latest_tag['target']['oid'],
                        url=f'https://github.com/{repo}/releases/tag/{latest_tag["name"]}'
                    )

                # Maximum Tag Strategy - Return first tag
                if conf.get('use_max_tag', False):
                    refs = repo_data['refs']['edges']
                    if not refs:
                        raise GetVersionError('No tag found in upstream repository.')
                    first_tag = refs[0]['node']
                    return create_rich_result(
                        conf=conf,
                        commits=commits,
                        sha=sha,
                        version=first_tag['name'],
                        gitref=f"refs/tags/{first_tag['name']}",
                        revision=first_tag['target']['oid'],
                        url=f'https://github.com/{repo}/releases/tag/{first_tag["name"]}'
                    )

                # Release Strategies
                if conf.get('use_latest_release', False) or conf.get('use_newest_release', False):
                    releases = repo_data['releases']['edges']
                    if not releases:
                        raise GetVersionError('No release found in upstream repository.')

                    include_prereleases = conf.get('use_prereleases', False)
                    
                    if conf.get('use_latest_release', False):
                        latest_release = next(
                            (release['node'] for release in releases 
                             if release['node']['isLatest'] or (include_prereleases and release['node']['isPrerelease'])),
                            None
                        )
                    else:
                        latest_release = releases[0]['node']

                    if not latest_release:
                        raise GetVersionError('No suitable release found')

                    use_release_name = conf.get('use_release_name', False)
                    version = latest_release['name'] if use_release_name else latest_release['tagName']

                    return create_rich_result(
                        conf=conf,
                        commits=commits,
                        sha=sha,
                        version=version,
                        gitref=f"refs/tags/{latest_release['tagName']}",
                        url=latest_release['url']
                    )

                # Default: Use commit date
                commit = repo_data['defaultBranchRef']['target']['history']['edges'][0]['node']
                return create_rich_result(
                    conf=conf,
                    commits=commits,
                    sha=sha,
                    version=commit['committedDate'].rstrip('Z').replace('-', '').replace(':', '').replace('T', '.'),
                    revision=commit['oid'],
                    url=f'https://github.com/{repo}/commit/{commit["oid"]}'
                )

        except aiohttp.ClientError as e:
            raise GetVersionError(f"GitHub API request failed: {e}")
