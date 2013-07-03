#!/usr/bin/env python3
# vim:fileencoding=utf-8

from setuptools import setup, find_packages

setup(
  name = 'nvchecker',
  version = '0.1',
  packages = find_packages(),
  install_requires = ['tornado'],
  entry_points = {
    'console_scripts': [
      'nvchecker = nvchecker.main:main',
    ],
  },

  author = 'lilydjwg',
  author_email = 'lilydjwg@gmail.com',
  description = 'New version checker for software',
  license = 'MIT',
  keywords = 'new version build check',
  url = 'https://github.com/lilydjwg/nvchecker',
)
