# MIT licensed
# Copyright (c) 2021 lilydjwg <lilydjwg@gmail.com>, et al.

import re
import sre_constants
from nvchecker.api import (
    VersionResult, Entry, KeyManager,
    TemporaryError,session, GetVersionError
)

async def get_version(name, conf, **kwargs):
    return await get_version_real(name, conf, **kwargs)

async def get_version_real(
    name: str, conf: Entry, *, keymanager: KeyManager,
    **kwargs,
) -> VersionResult:

    url = conf.get('url')
    header = conf.get('header', 'Location')
    follow_redirects = conf.get('follow_redirects', False)
    method = conf.get('method', 'HEAD')

    # Load token from config
    token = conf.get('token')
    # Load token from keyman
    if token is None:
        key_name = 'httpheader_' + name
        token = keymanager.get_key(key_name)

    # Set private token if token exists.
    headers = {}
    if token:
        headers["Authorization"] = token

    try:
        regex = re.compile(conf['regex'])
    except sre_constants.error as e:
        raise GetVersionError('bad regex', exc_info=e)

    res = await session.request(
        url,
        method=method,
        headers=headers,
        follow_redirects=follow_redirects,
    )

    header_value = res.headers.get(header)
    if not header_value:
        raise GetVersionError('header %s not found or is empty' % header)
    try:
        version = regex.findall(header_value)
    except ValueError:
        raise GetVersionError('version string not found.')
    return version
