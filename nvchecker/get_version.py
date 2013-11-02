import re
import sre_constants
import logging
from functools import partial
import queue
import json
import urllib.parse
import time

from pkg_resources import parse_version
from tornado.httpclient import AsyncHTTPClient
import tornado.process
from tornado.ioloop import IOLoop

logger = logging.getLogger(__name__)
handler_precedence = ('github', 'aur', 'pypi', 'pacman',
                      'cmd', 'gcode_hg', 'regex')

try:
  import pycurl
  AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
except ImportError:
  pycurl = None

def get_version(name, conf, callback):
  g = globals()
  for key in handler_precedence:
    if key in conf:
      funcname = 'get_version_by_' + key
      g[funcname](name, conf, callback)
      break
  else:
    logger.error('%s: no idea to get version info.', name)
    callback(name, None)

def get_version_by_regex(name, conf, callback):
  try:
    r = re.compile(conf['regex'])
  except sre_constants.error:
    logger.warn('%s: bad regex, skipped.', name, exc_info=True)
    callback(name, None)
    return

  encoding = conf.get('encoding', 'latin1')
  httpclient = AsyncHTTPClient()

  kwargs = {}
  if conf.get('proxy'):
    if pycurl:
      host, port = urllib.parse.splitport(conf['proxy'])
      kwargs['proxy_host'] = host
      kwargs['proxy_port'] = int(port)
    else:
      logger.warn('%s: proxy set but not used because pycurl is unavailable.', name)

  httpclient.fetch(conf['url'], partial(
    _get_version_by_regex, name, r, encoding, callback
  ), **kwargs)

def _get_version_by_regex(name, regex, encoding, callback, res):
  body = res.body.decode(encoding)
  try:
    version = max(regex.findall(body), key=parse_version)
  except ValueError:
    logger.error('%s: version string not found.', name)
    callback(name, None)
  else:
    callback(name, version)

AUR_URL = 'https://aur.archlinux.org/rpc.php?type=info&arg='

def get_version_by_aur(name, conf, callback):
  aurname = conf.get('aur') or name
  url = AUR_URL + aurname
  AsyncHTTPClient().fetch(url, partial(_aur_done, name, callback))

def _aur_done(name, callback, res):
  data = json.loads(res.body.decode('utf-8'))
  version = data['results']['Version']
  callback(name, version)

GITHUB_URL = 'https://api.github.com/repos/%s/commits'

def get_version_by_github(name, conf, callback):
  repo = conf.get('github')
  url = GITHUB_URL % repo
  AsyncHTTPClient().fetch(url, user_agent='lilydjwg/nvchecker',
                          callback=partial(_github_done, name, callback))

def _github_done(name, callback, res):
  data = json.loads(res.body.decode('utf-8'))
  version = data[0]['commit']['committer']['date'].split('T', 1)[0].replace('-', '')
  callback(name, version)

cmd_q = queue.Queue()
cmd_q.running = False

def get_version_by_cmd(name, conf, callback):
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

  p = tornado.process.Subprocess(cmd, shell=True, io_loop=IOLoop.instance(),
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

PYPI_URL = 'https://pypi.python.org/pypi/%s/json'

def get_version_by_pypi(name, conf, callback):
  repo = conf.get('pypi') or name
  url = PYPI_URL % repo
  AsyncHTTPClient().fetch(url, user_agent='lilydjwg/nvchecker',
                          callback=partial(_pypi_done, name, callback))

def _pypi_done(name, callback, res):
  data = json.loads(res.body.decode('utf-8'))
  version = data['info']['version']
  callback(name, version)

GCODE_URL = 'https://code.google.com/p/%s/source/list'
GCODE_HG_RE = re.compile(
  r'<a onclick="cancelBubble=true" href="detail\?r=[0-9a-f]+">([^<]+)</a>')

def get_version_by_gcode_hg(name, conf, callback):
  repo = conf.get('gcode_hg') or name
  url = GCODE_URL % repo
  AsyncHTTPClient().fetch(url, user_agent='lilydjwg/nvchecker',
                          callback=partial(_gcodehg_done, name, callback))

def _gcodehg_done(name, callback, res):
  data = res.body.decode('utf-8')
  m = GCODE_HG_RE.search(data)
  if m:
    t = time.strptime('Aug 15, 2013', '%b %d, %Y')
    version = time.strftime('%Y%m%d', t)
  else:
    logger.error('%s: version not found.', name)
    version = None
  callback(name, version)


def get_version_by_pacman(name, conf, callback):
  referree = conf['pacman']
  cmd = "LANG=C pacman -Si %s | grep -F Version | awk '{print $3}'" % referree
  conf['cmd'] = cmd
  get_version_by_cmd(name, conf, callback)
