#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

from setuptools import setup

import anisotropy

def main():
    setup(
        name = "anisotropy",
        description = "Anisotropy",
        long_description = anisotropy.__doc__,
        version = anisotropy.__version__,
        author = anisotropy.__author__,
        author_email = anisotropy.__email__,
        license = anisotropy.__license__,
        url = "https://github.com/L-Nafaryus/anisotropy",
        keywords = "anisotropy console",
        classifiers = [
            "Environment :: Console",
            "Operating System :: POSIX",
            "Operating System :: Unix",
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
        )
    )


if __name__ == "__main__":
    main()
