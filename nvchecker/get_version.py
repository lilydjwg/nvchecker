import logging
from importlib import import_module

logger = logging.getLogger(__name__)
handler_precedence = (
  'github', 'aur', 'pypi', 'archpkg', 'gems', 'pacman',
  'cmd', 'gcode_hg', 'regex', 'manual',
)

def get_version(name, conf, callback):
  for key in handler_precedence:
    if key in conf:
      func = import_module('.source.' + key, __package__).get_version
      func(name, conf, callback)
      break
  else:
    logger.error('%s: no idea to get version info.', name)
    callback(name, None)
