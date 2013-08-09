import sys
import time
import logging

class TornadoLogFormatter(logging.Formatter):
  def __init__(self, color, *args, **kwargs):
    super().__init__(self, *args, **kwargs)
    self._color = color
    if color:
      import curses
      curses.setupterm()
      if sys.hexversion < 50463728:
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
    if record.exc_info:
      if not record.exc_text:
        record.exc_text = self.formatException(record.exc_info)
    if record.exc_text:
      formatted = formatted.rstrip() + "\n" + record.exc_text
    return formatted.replace("\n", "\n    ")

def enable_pretty_logging(level=logging.DEBUG):
  logger = logging.getLogger()
  h = logging.StreamHandler()
  formatter = logging.Formatter('%(asctime)s:%(levelname)-7s:%(name)-12s:%(message)s')
  try:
    import curses
    color = False
    curses.setupterm()
    if curses.tigetnum("colors") > 0:
      color = True
    formatter = TornadoLogFormatter(color=color)
  except:
    import traceback
    traceback.print_exc()
  finally:
    h.setLevel(level)
    h.setFormatter(formatter)
    logger.setLevel(level)
    logger.addHandler(h)

