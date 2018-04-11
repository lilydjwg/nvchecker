# vim: se sw=2:
# MIT licensed
# Copyright (c) 2018 lilydjwg <lilydjwg@gmail.com>, et al.

import logging
import os
import io
import traceback

import structlog

def _console_msg(event):
  evt = event['event']
  if evt == 'up-to-date':
    msg = 'up-to-date, version %s' % event['version']
  elif evt == 'updated':
    if event.get('old_version'):
      msg = 'updated from %(old_version)s to %(version)s' % event
    else:
      msg = 'updated to %(version)s' % event
  else:
    msg = evt

  if 'name' in event:
    msg = '%s: %s' % (event['name'], msg)
    del event['name']

  event['msg'] = msg

  return event

def exc_info(logger, level, event):
  if level == 'exception':
    event['exc_info'] = True
  return event

def stdlib_renderer(logger, level, event):
  event = _console_msg(event)
  logger = logging.getLogger(event.get('logger_name'))
  msg = event.pop('msg', event['event'])
  exc_info = event.pop('exc_info', None)
  getattr(logger, level)(
    msg, exc_info = exc_info, extra=event,
  )
  return ''

_renderer = structlog.processors.JSONRenderer(ensure_ascii=False)
def json_renderer(logger, level, event):
  return _renderer(logger, level, event)

class _Logger(logging.Logger):
  _my_srcfile = os.path.normcase(
    stdlib_renderer.__code__.co_filename)

  def findCaller(self, stack_info=False):
    """
    Find the stack frame of the caller so that we can note the source
    file name, line number and function name.
    """
    f = logging.currentframe()
    #On some versions of IronPython, currentframe() returns None if
    #IronPython isn't run with -X:Frames.
    if f is not None:
      f = f.f_back
    rv = "(unknown file)", 0, "(unknown function)", None
    while hasattr(f, "f_code"):
      co = f.f_code
      filename = os.path.normcase(co.co_filename)
      if filename in [logging._srcfile, self._my_srcfile]:
        f = f.f_back
        continue
      sinfo = None
      if stack_info:
        sio = io.StringIO()
        sio.write('Stack (most recent call last):\n')
        traceback.print_stack(f, file=sio)
        sinfo = sio.getvalue()
        if sinfo[-1] == '\n':
          sinfo = sinfo[:-1]
        sio.close()
      rv = (co.co_filename, f.f_lineno, co.co_name, sinfo)
      break
    return rv

def fix_logging():
  logging.setLoggerClass(_Logger)

