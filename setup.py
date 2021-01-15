#!/usr/bin/env python3

from setuptools import setup, find_namespace_packages
import nvchecker

# The complex upload command:
# rm -rf dist && python setup.py sdist && twine check dist/* && twine upload -s dist/*

setup(
  name = 'nvchecker',
  version = nvchecker.__version__,
  author = 'lilydjwg',
  author_email = 'lilydjwg@gmail.com',
  description = 'New version checker for software',
  license = 'MIT',
  keywords = 'new version build check',
  url = 'https://github.com/lilydjwg/nvchecker',
  long_description = open('README.rst', encoding='utf-8').read(),
  long_description_content_type = 'text/x-rst',
  platforms = 'any',
  zip_safe = True,

  packages = find_namespace_packages(exclude=['tests', 'build*', 'docs']),
  install_requires = ['setuptools', 'packaging', 'toml', 'structlog', 'appdirs', 'tornado>=6', 'pycurl'],
  extras_require = {
    'vercmp': ['pyalpm'],
  },
  tests_require = [
    'pytest',
    'pytest-asyncio',
    'pytest-httpbin',
    'flaky',
  ],
  entry_points = {
    'console_scripts': [
      'nvchecker = nvchecker.__main__:main',
      'nvtake = nvchecker.tools:take',
      'nvcmp = nvchecker.tools:cmp',
    ],
  },
  scripts = [
    'scripts/nvchecker-ini2toml',
    'scripts/nvchecker-notify',
  ],

  classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Topic :: Internet",
    "Topic :: Internet :: WWW/HTTP",
    "Topic :: Software Development",
    "Topic :: System :: Archiving :: Packaging",
    "Topic :: System :: Software Distribution",
    "Topic :: Utilities",
  ],
)
