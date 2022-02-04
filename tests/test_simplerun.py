# MIT licensed
# Copyright (c) 2022 lilydjwg <lilydjwg@gmail.com>, et al.

import sys
import tempfile
import subprocess

def test_simple_run():
  '''make sure the tool as a whole can run the simplest check'''
  with tempfile.NamedTemporaryFile(mode='w') as f:
    f.write('''\
[t]
source = "cmd"
cmd = "echo 1"
''')
    f.flush()
    subprocess.check_call([
      sys.executable, '-m', 'nvchecker',
      '-c', f.name,
    ])

