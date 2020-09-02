# MIT licensed
# Copyright (c) 2020 lilydjwg <lilydjwg@gmail.com>, et al.

from __future__ import annotations

from contextvars import ContextVar
from typing import Optional

from . import __version__

DEFAULT_USER_AGENT = f'lilydjwg/nvchecker {__version__}'

tries = ContextVar('tries', default=1)
proxy: ContextVar[Optional[str]] = ContextVar('proxy', default=None)
user_agent = ContextVar('user_agent', default=DEFAULT_USER_AGENT)
