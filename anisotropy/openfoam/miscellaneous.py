# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

from .application import application

def foamDictionary(filepath: str, entry: str, value: str = None, case: str = None):
    args = [filepath, "-entry", entry]

    if value:
        args.extend(["-set", value])

    application("foamDictionary", *args, case = case, stderr = False)

