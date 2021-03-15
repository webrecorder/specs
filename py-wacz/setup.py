#!/usr/bin/env python3
# vim: set sw=4 et:
from setuptools import setup, find_packages

__version__ = "0.2.2"


def load_requirements(filename):
    with open(filename, "rt") as fh:
        return fh.read().rstrip().split("\n")


setup(
    name="wacz",
    version=__version__,
    author="Ilya Kreymer, Emma Dickson",
    author_email="info@webrecorder.net",
    license="Apache 2.0",
    packages=find_packages(exclude=["test"]),
    url="https://github.com/webrecorder/wacz-format",
    description="WACZ Format Tools",
    long_description="",
    install_requires=load_requirements("requirements.txt"),
    zip_safe=True,
    entry_points="""
        [console_scripts]
        wacz = wacz.main:main
    """,
)
