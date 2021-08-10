#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

from setuptools import setup

import anisotropy

def read(filename, split = False):
    content = ""

    with open(os.path.join(os.path.dirname(__file__), filename), "r") as io:
        content = io.read()

    return content.strip().split("\n") if split else content


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
            "Intended Audience :: Science/Research",
            "Programming Language :: Python :: 3.9"
        ],

        package_data = {
            "anisotropy": [
                "config/default.toml"
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
        entry_points = {
            "console_scripts": [
                "anisotropy=anisotropy.core.cli:anisotropy"
            ]
        }
    )


if __name__ == "__main__":
    main()
