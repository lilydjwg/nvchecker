import logging
from functools import partial

import tornado.process
from tornado.ioloop import IOLoop

import os.path as _path

logger = logging.getLogger(__name__)
_self_path = _path.dirname(_path.abspath(__file__))
_cmd_prefix = ['/bin/bash', _path.join(_self_path, 'vcs.sh')]

PROT_VER = 1

def _parse_oldver(oldver):
    if oldver is None:
        return PROT_VER, 0, ''
    try:
        prot_ver, count, ver = oldver.split('.', maxsplit=2)
        prot_ver = int(prot_ver)
        count = int(count)
    except:
        return PROT_VER, 0, ''
    if prot_ver != PROT_VER:
        return PROT_VER, 0, ver
    return PROT_VER, count, ver

def get_version(name, conf, callback):
  vcs = conf['vcs']
  oldver = conf['oldver']
  cmd = _cmd_prefix + [name, vcs]
  p = tornado.process.Subprocess(cmd, io_loop=IOLoop.instance(),
                                 stdout=tornado.process.Subprocess.STREAM)
  p.set_exit_callback(partial(_command_done, name, oldver, callback, p))

def _command_done(name, oldver, callback, process, status):
  if status != 0:
    logger.error('%s: command exited with %d.', name, status)
    callback(name, None)
  else:
    process.stdout.read_until_close(partial(_got_version_from_cmd,
                                            callback, name, oldver))

def _got_version_from_cmd(callback, name, oldver_str, output):
  output = output.strip().decode('latin1')
  oldver = _parse_oldver(oldver_str)
  if output == oldver[2]:
      callback(name, None)
  else:
      callback(name, "%d.%d.%s" % (oldver[0], oldver[1] + 1, output))
