from . import cmd

def get_version(name, conf, callback):
  referree = conf['pacman']
  c = "LANG=C pacman -Si %s | grep -F Version | awk '{print $3}'" % referree
  conf['cmd'] = c
  cmd.get_version(name, conf, callback)
