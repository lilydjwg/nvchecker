# MIT licensed
# Copyright (c) 2020 lilydjwg <lilydjwg@gmail.com>, et al.

from contextvars import ContextVar

from . import __version__

DEFAULT_USER_AGENT = 'lilydjwg/nvchecker %s' % __version__

tries = ContextVar('tries', default=1)
proxy = ContextVar('proxy', default=None)
user_agent = ContextVar('user_agent', default=DEFAULT_USER_AGENT)
