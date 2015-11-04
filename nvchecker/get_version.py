import logging
from importlib import import_module

logger = logging.getLogger(__name__)
handler_precedence = (
  'github', 'gitcafe', 'aur', 'pypi', 'archpkg', 'gems', 'pacman',
  'cmd', 'bitbucket', 'gcode_hg', 'gcode_svn', 'regex', 'manual', 'vcs',
  'npm',
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
