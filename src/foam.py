#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, shutil


if __name__ == "__main__":
    src = os.getcwd()
    build = os.path.join(src, "../build")

    if not os.path.exists(build):
        os.makedirs(build)

    foamCase = [ "0", "constant", "system" ]

    for d in foamCase:
        shutil.copytree("{}/foam/{}".format(src, d), 
            "{}/simple-cubic/0.1/{}".format(build, d))
