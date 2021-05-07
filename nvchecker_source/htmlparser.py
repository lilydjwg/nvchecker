# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

from lxml import html, etree

from nvchecker.api import (
    VersionResult, Entry, KeyManager,
    TemporaryError, session
)

async def get_version(name, conf, **kwargs):
    try:
        return await get_version_real(name, conf, **kwargs)
    except TemporaryError as e:
        check_ratelimit(e, name)

async def get_version_real(
    name: str, conf: Entry, *, keymanager: KeyManager,
    **kwargs,
) -> VersionResult:

    encoding = conf.get('encoding', 'latin1')                                                      
    
    # Load token from config
    token = conf.get('token')
    # Load token from keyman
    if token is None:
        key_name = 'htmlparser_' + name
        token = keymanager.get_key(key_name)

    # Set private token if token exists.
    headers = {}
    if token:
        headers["Authorization"] = token

    data = await session.get(conf.get('url'), headers = headers)
    body = html.fromstring(data.body.decode(encoding))
    try:
        checkxpath = body.xpath(conf.get('xpath'))
    except etree.XPathEvalError as e:
        raise GetVersionError('bad xpath', exc_info=e)

    try:
        version = body.xpath(conf.get('xpath'))
    except ValueError:
        if not conf.get('missing_ok', False):
            raise GetVersionError('version string not found.')
    return version