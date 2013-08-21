import logging

from .lib import nicelogger

from . import __version__

def add_common_arguments(parser):
  parser.add_argument('-i', '--oldver',
                      help='read an existing version record file')
  parser.add_argument('-o', '--newver',
                      help='write a new version record file')
  # parser.add_argument('-r', '--rc', default=os.path.expanduser('~/.nvcheckerrc'),
  #                     help='specify the nvcheckerrc file to use')
  parser.add_argument('-l', '--logging',
                      choices=('debug', 'info', 'warning', 'error'), default='info',
                      help='logging level (default: info)')
  parser.add_argument('-V', '--version', action='store_true',
                      help='show version and exit')

def process_common_arguments(args):
  '''return True if should stop'''
  nicelogger.enable_pretty_logging(getattr(logging, args.logging.upper()))

  if args.version:
    print('nvchecker v' + __version__)
    return True
