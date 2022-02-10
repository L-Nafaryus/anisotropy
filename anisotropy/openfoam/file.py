# -*- coding: utf-8 -*-

import pathlib

from . import conversion


class FoamFile(object):
    def __init__(
        self, 
        filename: str = None,
        _version: float = 2.0,
        _format: str = "ascii",
        _class: str = "dictionary",
        _object: str = None,
        _location: str = None
    ):
        """A FoamFile object.

        :param filename:
            Can be used as shortcut to set _location and _object,
            _location and _object parameters will be ignored.
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

    @property
    def version(self) -> str:
        return self.header.get("version")

    @property
    def format(self) -> str:
        return self.header.get("format")

    @property
    def class_(self) -> str:
        return self.header.get("class")

    @property
    def object(self) -> str:
        return self.header.get("object")

    @property
    def location(self) -> str:
        return self.header.get("location").replace('"', "")

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

    def __add__(self, file):
        from . import FoamCase

        assert type(file) is FoamFile

        return FoamCase([ self, file ])

    def read(self, filename: str = None):
        """Read a FoamFile.

        :param filename:
            Path to the file. If None, use location and object from header with
            the current working directory.
        :return:
            Self.
        """
        filename = (
            filename or self.location + "/" + self.object 
            if self.location else self.object
        )
        path = pathlib.Path(filename).resolve()
        header, content = conversion.read_foamfile(path)

        self.header = header
        
        if not header.get("object"):
            self.header["object"] = path.parts[-1]

        self.content = content

        return self

    def write(self, filename: str = None):
        """Write a FoamFile to the file.

        :param filename:
            Path to the file. If None, use location and object from header with
            the current working directory.
        """  
        filename = (
            filename or self.location + "/" + self.object 
            if self.location else self.object
        )
        path = pathlib.Path(filename).resolve()
        path.parent.mkdir(parents = True, exist_ok = True)
        conversion.write_foamfile(self.header, self.content, path)

    def remove(self, filename: str = None):
        """Remove a FoamFile.

        :param filename:
            Path to the file. If None, use location and object from header with
            the current working directory.
        """  
        filename = (
            filename or self.location + "/" + self.object 
            if self.location else self.object
        )
        path = pathlib.Path(filename).resolve()

        if path.exists():
            pathlib.os.remove(filename)
