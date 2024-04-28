# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

'''
A Tornado-inspired logging formatter, with displayed time with millisecond accuracy

FYI: pyftpdlib also has a Tornado-style logger.
'''

import sys
import time
import logging

class Colors:
  def __init__(self, color=None):
    if color is None:
      color = support_color()
    if color:
      import curses
      curses.setupterm()
      if sys.hexversion < 0x30203f0:
        fg_color = str(curses.tigetstr("setaf") or
                   curses.tigetstr("setf") or "", "ascii")
      else:
        fg_color = curses.tigetstr("setaf") or curses.tigetstr("setf") or b""

      self.blue = str(curses.tparm(fg_color, 4), "ascii")
      self.yellow = str(curses.tparm(fg_color, 3), "ascii")
      self.green = str(curses.tparm(fg_color, 2), "ascii")
      self.red = str(curses.tparm(fg_color, 1), "ascii")
      self.bright_red = str(curses.tparm(fg_color, 9), "ascii")
      self.normal = str(curses.tigetstr("sgr0"), "ascii")

    else:
      self.blue = self.yellow = self.green = self.red = self.bright_red = self.normal = ""


class TornadoLogFormatter(logging.Formatter):
  def __init__(self, color, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self._color = color
    if color:
      colors = Colors(color=color)
      self._colors = {
        logging.DEBUG: colors.blue,
        logging.INFO: colors.green,
        logging.WARNING: colors.yellow,
        logging.ERROR: colors.red,
        logging.CRITICAL: colors.bright_red,
      }
      self._normal = colors.normal

  def format(self, record):
    try:
      record.message = record.getMessage()
    except Exception as e:
      record.message = "Bad message (%r): %r" % (e, record.__dict__)
    record.asctime = time.strftime(
      "%m-%d %H:%M:%S", self.converter(record.created))
    prefix = '[%(levelname)1.1s %(asctime)s.%(msecs)03d %(module)s:%(lineno)d]' % \
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

def support_color(stream=sys.stderr):
  if stream.isatty():
    try:
      import curses
      curses.setupterm()
      if curses.tigetnum("colors") > 0:
        return True
    except:
      import traceback
      traceback.print_exc()
  return False

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
  if color is None and handler is None:
    color = support_color()
  formatter = TornadoLogFormatter(color=color)
  h.setLevel(level)
  h.setFormatter(formatter)
  logger.setLevel(level)
  logger.addHandler(h)
