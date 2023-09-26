#!/usr/bin/env python
import sys
from distutils.core import Command
import subprocess

from setuptools import setup

import defusedxml


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        errno = subprocess.call([sys.executable, "tests.py"])
        raise SystemExit(errno)


long_description = []
with open("README.txt") as f:
    long_description.append(f.read())
with open("CHANGES.txt") as f:
    long_description.append(f.read())


setup(
    name="defusedxml",
    version=defusedxml.__version__,
    cmdclass={"test": PyTest},
    packages=["defusedxml"],
    author="Christian Heimes",
    author_email="christian@python.org",
    maintainer="Christian Heimes",
    maintainer_email="christian@python.org",
    url="https://github.com/tiran/defusedxml",
    download_url="https://pypi.python.org/pypi/defusedxml",
    keywords="xml bomb DoS",
    platforms="all",
    license="PSFL",
    description="XML bomb protection for Python stdlib modules",
    long_description="\n".join(long_description),
    long_description_content_type="text/x-rst",
    classifiers=[
        "Development Status :: 6 - Mature",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Python Software Foundation License",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Text Processing :: Markup :: XML",
    ],
    python_requires=">=3.6",
)
