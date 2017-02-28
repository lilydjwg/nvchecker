# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import queue
import logging
from functools import partial

import tornado.process
from tornado.ioloop import IOLoop

logger = logging.getLogger(__name__)
cmd_q = queue.Queue()
cmd_q.running = False

def get_version(name, conf, callback):
  cmd = conf['cmd']
  cmd_q.put((name, cmd, callback))
  if not cmd_q.running:
    _run_command()

def _run_command():
  cmd_q.running = True
  try:
    name, cmd, callback = cmd_q.get_nowait()
  except queue.Empty:
    cmd_q.running = False
    return

  p = tornado.process.Subprocess(cmd, shell=True,
                                 stdout=tornado.process.Subprocess.STREAM)
  p.set_exit_callback(partial(_command_done, name, callback, p))

def _command_done(name, callback, process, status):
  if status != 0:
    logger.error('%s: command exited with %d.', name, status)
    callback(name, None)
  else:
    process.stdout.read_until_close(partial(_got_version_from_cmd, callback, name))
  _run_command()

def _got_version_from_cmd(callback, name, output):
  output = output.strip().decode('latin1')
  callback(name, output)

