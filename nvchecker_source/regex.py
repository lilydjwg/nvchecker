# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import re
import sre_constants
from nvchecker.api import (
    VersionResult, Entry, KeyManager,
    TemporaryError, session, GetVersionError
)

async def get_version(name, conf, **kwargs):
    return await get_version_real(name, conf, **kwargs)

async def get_version_real(
    name: str, conf: Entry, *, keymanager: KeyManager,
    **kwargs,
) -> VersionResult:

    # Load token from config
    token = conf.get('token')
    # Load token from keyman
    if token is None:
        key_name = 'regex_' + name
        token = keymanager.get_key(key_name)

    # Set private token if token exists.
    headers = {}
    if token:
        headers["Authorization"] = token

    try:
        regex = re.compile(conf['regex'])
    except sre_constants.error as e:
        raise GetVersionError('bad regex', exc_info=e)

    encoding = conf.get('encoding', 'latin1')

    res = await session.get(conf.get('url'), headers=headers)
    body = res.body.decode(encoding)
    try:
        version = regex.findall(body)
    except ValueError:
        if not conf.get('missing_ok', False):
            raise GetVersionError('version string not found.')
    return version