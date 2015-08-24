from . import cmd

def get_version(name, conf, callback):
  referree = conf['pacman']
  c = "LANG=C pacman -Si %s | grep -F Version | awk '{print $3}'" % referree
  conf['cmd'] = c

  def callback_wrapper(name, version):
    strip_release = conf.getboolean('strip-release', False)
    if strip_release and '-' in version:
      version = version.rsplit('-', 1)[0]
    callback(name, version)

  cmd.get_version(name, conf, callback_wrapper)
