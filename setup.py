#!/usr/bin/env python3

from setuptools import setup, find_packages
import nvchecker

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
  platforms = 'any',
  zip_safe = False,

  packages = find_packages(exclude=["tests"]),
  install_requires = ['setuptools', 'structlog', 'tornado', 'pycurl'],
  extras_require = {
    'vercmp': ['pyalpm'],
  },
  tests_require = [
    'pytest',
    'pytest-asyncio',
    'pytest-xdist',
    'flaky',
  ],
  entry_points = {
    'console_scripts': [
      'nvchecker = nvchecker.main:main',
      'nvtake = nvchecker.tools:take',
      'nvcmp = nvchecker.tools:cmp',
    ],
  },
  package_data = {'nvchecker': ['source/vcs.sh']},

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
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Topic :: Internet",
    "Topic :: Internet :: WWW/HTTP",
    "Topic :: Software Development",
    "Topic :: System :: Archiving :: Packaging",
    "Topic :: System :: Software Distribution",
    "Topic :: Utilities",
  ],
)
