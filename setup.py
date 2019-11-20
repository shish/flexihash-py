#!/usr/bin/env python

import setuptools
from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="Flexihash",
    version="1.3",
    description="Python port of PHP Flexihash",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Shish",
    author_email="webmaster@shishnet.org",
    url="http://github.com/shish/python-flexihash",
    packages=["flexihash"],
)
