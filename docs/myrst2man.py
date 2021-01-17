#!/usr/bin/python3

import time
import locale
import os
import sys
try:
  locale.setlocale(locale.LC_ALL, '')
except:
  pass

sys.path.insert(0, '..')
import nvchecker

from docutils.core import publish_cmdline, default_description
from docutils import nodes
from docutils.writers import manpage
from docutils.parsers.rst import roles

def ref_role(
  role, rawtext, text, lineno, inliner,
  options={}, content=[],
):
  node = nodes.reference(rawtext, text.title(), **options)
  return [node], []

def doc_role(
  role, rawtext, text, lineno, inliner,
  options={}, content=[],
):
  node = nodes.reference(rawtext, text, **options)
  return [node], []

roles.register_local_role('ref', ref_role)
roles.register_local_role('doc', doc_role)

class MyTranslator(manpage.Translator):
  def visit_image(self, node):
    raise nodes.SkipNode

  def visit_topic(self, node):
    self.body.append('\n')
    raise nodes.SkipNode

  def visit_title(self, node):
    try:
      super().visit_title(node)
    except nodes.SkipNode:
      if self.section_level == 0:
        self._docinfo['title'] = 'nvchecker'
        self._docinfo['subtitle'] = 'New version checker for software releases'
        self._docinfo['title_upper'] = 'nvchecker'.upper()
        self._docinfo['manual_section'] = '1'
        # Make the generated man page reproducible. Based on the patch from
        # https://sourceforge.net/p/docutils/patches/132/#5333
        source_date_epoch = os.environ.get('SOURCE_DATE_EPOCH')
        if source_date_epoch:
            self._docinfo['date'] = time.strftime('%Y-%m-%d', time.gmtime(int(source_date_epoch)))
        else:
            self._docinfo['date'] = time.strftime('%Y-%m-%d')
        self._docinfo['version'] = nvchecker.__version__
      raise

class MyWriter(manpage.Writer):
  def __init__(self):
    super().__init__()
    self.translator_class = MyTranslator

def main():
  description = ("Generates plain unix manual documents.  " + default_description)
  publish_cmdline(writer=MyWriter(), description=description)

if __name__ == '__main__':
  main()
