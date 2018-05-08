# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import atexit
import aiohttp
connector = aiohttp.TCPConnector(limit=20)

__all__ = ['session', 'HTTPError']

class HTTPError(Exception):
    def __init__(self, code, message, response):
        self.code = code
        self.message = message
        self.response = response

class BetterClientSession(aiohttp.ClientSession):
    async def _request(self, *args, **kwargs):
        if hasattr(self, "nv_config") and self.nv_config.get("proxy"):
            kwargs.setdefault("proxy", self.nv_config.get("proxy"))

        res = await super(BetterClientSession, self)._request(
            *args, **kwargs)
        if res.status >= 400:
            raise HTTPError(res.status, res.reason, res)
        return res

session = BetterClientSession(connector=connector, read_timeout=10, conn_timeout=5)
atexit.register(session.close)
