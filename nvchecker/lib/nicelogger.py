# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

'''
A Tornado-inspired logging formatter, with displayed time with millisecond accuracy

FYI: pyftpdlib also has a Tornado-style logger.
'''

import sys
import time
import logging

class TornadoLogFormatter(logging.Formatter):
  def __init__(self, color, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self._color = color
    if color:
      import curses
      curses.setupterm()
      if sys.hexversion < 0x30203f0:
        fg_color = str(curses.tigetstr("setaf") or
                   curses.tigetstr("setf") or "", "ascii")
      else:
        fg_color = curses.tigetstr("setaf") or curses.tigetstr("setf") or b""
      self._colors = {
        logging.DEBUG: str(curses.tparm(fg_color, 4), # Blue
                     "ascii"),
        logging.INFO: str(curses.tparm(fg_color, 2), # Green
                    "ascii"),
        logging.WARNING: str(curses.tparm(fg_color, 3), # Yellow
                     "ascii"),
        logging.ERROR: str(curses.tparm(fg_color, 1), # Red
                     "ascii"),
        logging.CRITICAL: str(curses.tparm(fg_color, 9), # Bright Red
                     "ascii"),
      }
      self._normal = str(curses.tigetstr("sgr0"), "ascii")

  def format(self, record):
    try:
      record.message = record.getMessage()
    except Exception as e:
      record.message = "Bad message (%r): %r" % (e, record.__dict__)
    record.asctime = time.strftime(
      "%m-%d %H:%M:%S", self.converter(record.created))
    record.asctime += '.%03d' % ((record.created % 1) * 1000)
    prefix = '[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d]' % \
      record.__dict__
    if self._color:
      prefix = (self._colors.get(record.levelno, self._normal) +
            prefix + self._normal)
    formatted = prefix + " " + record.message

    formatted += ''.join(
      ' %s=%s' % (k, v) for k, v in record.__dict__.items()
      if k not in {
        'levelname', 'asctime', 'module', 'lineno', 'args', 'message',
        'filename', 'exc_info', 'exc_text', 'created', 'funcName',
        'processName', 'process', 'msecs', 'relativeCreated', 'thread',
        'threadName', 'name', 'levelno', 'msg', 'pathname', 'stack_info',
      })

    if record.exc_info:
      if not record.exc_text:
        record.exc_text = self.formatException(record.exc_info)
    if record.exc_text:
      formatted = formatted.rstrip() + "\n" + record.exc_text
    return formatted.replace("\n", "\n    ")

def enable_pretty_logging(level=logging.DEBUG, handler=None, color=None):
  '''
  handler: specify a handler instead of default StreamHandler
  color:   boolean, force color to be on / off. Default to be on only when
           ``handler`` isn't specified and the term supports color
  '''
  logger = logging.getLogger()
  if handler is None:
    h = logging.StreamHandler()
  else:
    h = handler
  if color is None:
    color = False
    if handler is None and sys.stderr.isatty():
      try:
        import curses
        curses.setupterm()
        if curses.tigetnum("colors") > 0:
          color = True
      except:
        import traceback
        traceback.print_exc()
  formatter = TornadoLogFormatter(color=color)
  h.setLevel(level)
  h.setFormatter(formatter)
  logger.setLevel(level)
  logger.addHandler(h)
