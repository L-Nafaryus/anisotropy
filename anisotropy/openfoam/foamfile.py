# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

from anisotropy.openfoam.utils import version
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from PyFoam.Basics.FoamFileGenerator import FoamFileGenerator
import os

class FoamFile(object):
    def __init__(self, 
            filename,
            _version = 2.0,
            _format = "ascii",
            _class = "dictionary",
            _location = None,
            _object = None
        ):

        self.filename = filename
        self.header = { 
            "version": _version,
            "format": _format,
            "class": _class,
            "object": _object or os.path.split(self.filename)[1]
        }
        self.content = {}

        if _location:
            self.header["location"] = f'"{ _location }"'

    def __getitem__(self, key):
        return self.content[key]

    def __setitem__(self, key, value):
        self.content[key] = value

    def __delitem__(self, key):
        del self.content[key]

    def update(self, **kwargs):
        self.content.update(**kwargs)

    def __len__(self):
        return len(self.content)

    def __iter__(self):
        for key in self.content:
            yield key

    def read(self):
        ppf = ParsedParameterFile(os.path.abspath(self.filename))

        self.header = ppf.header
        self.content = ppf.content

    def _template(self, header, content):
        limit = 78
        desc = [
            "/*--------------------------------*- C++ -*----------------------------------*\\",
            "| =========                 |                                                 |",
            "| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |",
            "|  \\\\    /   O peration     |",
            "|   \\\\  /    A nd           |                                                 |",
            "|    \\\\/     M anipulation  |                                                 |",
            "\*---------------------------------------------------------------------------*/"
        ]
        desc[3] += " Version: {}".format(version() or "missed")
        desc[3] += " " * (limit - len(desc[3])) + "|"
        afterheader = "// " + 37 * "* " + "//"
        endfile = "// " + 73 * "*" + " //"

        return "\n".join([*desc, header, afterheader, content, endfile])


    def write(self, casepath: str = None):
        header = FoamFileGenerator({}, header = self.header)
        header = header.makeString()[ :-2]
        header = header.replace("\n ", "\n" + 4 * " ")

        content = FoamFileGenerator(self.content)
        content = content.makeString()[ :-1]
        content = content.replace("\n  ", "\n" + 4 * " ").replace(" \t// " + 73 * "*" + " //", "")
        content = content.replace(" /* empty */ ", "")

        prepared = self._template(header, content)

        if casepath:
            path = os.path.join(casepath, self.filename)

        else:
            path = os.path.abspath(self.filename)

        os.makedirs(os.path.split(path)[0], exist_ok = True)

        with open(path, "w") as io:
            _ = io.write(prepared)



