# vim:fileencoding=utf-8

from tornado.options import parse_command_line, define, options

def take():
    raise NotImplementedError

define("notify", type=bool,
       help="show desktop notifications when a new version is available")
define("oldverfile", type=str, metavar="FILE",
       help="a text file listing current version info in format 'name: version'")
define("verfile", type=str, metavar="FILE",
       help="write a new version file")
