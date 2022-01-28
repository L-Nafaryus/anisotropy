# -*- coding: utf-8 -*-

import pathlib

from . import conversion


class FoamFile(object):
    def __init__(
        self, 
        _version: float = 2.0,
        _format: str = "ascii",
        _class: str = "dictionary",
        _object: str = None,
        _location: str = None,
        filename: str = None
    ):
        """A FoamFile object.

        :param _version:
            Version of the file format, current is 2.0.
        :param _format:
            ASCII or binary representation, currently ascii only
            supported.
        :param _class:
            Class of the file.
        :param _object:
            Usually contains name of the file.
        :param _location:
            Path to the parent directory of the file according 
            to the case root.
        :param filename:
            Can be used as shortcut to set _location and _object,
            _location and _object parameters will be ignored.
        """

        if filename:
            splitted = filename.split("/")
            _object = splitted[-1]
            _location = "/".join(splitted[ :-1])

        self.header = { 
            "version": _version,
            "format": _format,
            "class": _class,
            "object": _object
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

    def __repr__(self) -> str:
        return "<FoamFile: {}>".format(self.header["object"] or None)

    def read(self, filename: str = None):
        """Read a FoamFile.

        :param filename:
            Path to the file. If None, use location from header with
            current working directory.
        :return:
            Self.
        """
        path = pathlib.Path(filename or self.header["location"]).resolve()
        header, content = conversion.read_foamfile(path)

        self.header = header
        
        if not header.get("object"):
            self.header["object"] = path.parts[-1]

        self.content = content

        return self

    def write(self, filename: str = None):
        """Write a FoamFile to the file.

        :param filename:
            Path to the file. If None, use location from header with
            current working directory..
        """  
        filename = pathlib.Path(filename or self.header["location"]).resolve()
        conversion.write_foamfile(self.header, self.content, filename)
