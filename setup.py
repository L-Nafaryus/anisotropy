#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

import os
from setuptools import setup

import anisotropy

def read(filename, split = False):
    content = ""

    with open(os.path.join(os.path.dirname(__file__), filename), "r") as io:
        content = io.read()

    return content.strip().split("\n") if split else content

def findall(directory):
    return [
        os.path.join(directory, f) for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f))
    ]

def main():
    setup(
        name = "anisotropy",
        description = "Anisotropy",
        long_description = read("README.rst"),
        long_description_content_type = "text/x-rst",
        version = anisotropy.__version__,
        author = anisotropy.__author__,
        author_email = anisotropy.__email__,
        license = anisotropy.__license__,

        url = "https://github.com/L-Nafaryus/anisotropy",
        project_urls = {
            "Source": "https://github.com/L-Nafaryus/anisotropy"
        },

        keywords = "anisotropy console CFD",
        classifiers = [
            "Environment :: Console",
            "Operating System :: POSIX",
            "Operating System :: Unix",
            "Intended Audience :: Developers",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Programming Language :: Python :: 3.9"
        ],

        data_files = [
            ("share/doc/anisotropy", findall("docs")),
            ("share/doc/anisotropy/source", findall("docs/source")),
            ("share/doc/anisotropy/source/static", findall("docs/source/static")),
            ("share/doc/anisotropy/source/notes", findall("docs/source/notes"))
        ],

        package_data = {
            "anisotropy": [
                "config/default.toml",
                "config/bashrc"
            ]
        },
        packages = (
            "anisotropy",
            "anisotropy.config",
            "anisotropy.core",
            "anisotropy.openfoam",
            "anisotropy.salomepl",
            "anisotropy.samples"
        ),

        python_requires = ">=3.6",
        install_requires = read("requirements.txt", True),
        extras_require = {
            "documentation": ["Sphinx", "sphinx-rtd-theme", "pydeps", "peewee-erd" ],
            "extra": ["jupyterlab", "seaborn", "sklearn"]
        },
        entry_points = {
            "console_scripts": [
                "anisotropy=anisotropy.core.cli:anisotropy"
            ]
        }
    )


if __name__ == "__main__":
    main()
