from .simple_json import simple_json

# Using metacpan
CPAN_URL = 'https://api.metacpan.org/release/%s'

def _version_from_json(data):
  return str(data['version'])

get_version = simple_json(
  CPAN_URL,
  'cpan',
  _version_from_json,
)
