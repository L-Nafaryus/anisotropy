# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

import os
from peewee import SqliteDatabase

class Database(SqliteDatabase):
    def __init__(self, *args, **kwargs):
        self.filepath = None
        self.pragmas_ = kwargs.get("pragmas", { "foreign_keys": 1 })
        self.field_types_ = kwargs.get("field_types", { "list": "text" })
        self.autoconnect_ = kwargs.get("autoconnect", False)
        
        SqliteDatabase.__init__(
            self,
            None,
            pragmas = kwargs.get("pragmas", { "foreign_keys": 1 }),
            field_types = kwargs.get("field_types", { "list": "text" }),
            autoconnect = kwargs.get("autoconnect", False)
        )

    @property
    def tables(self):
        return models.__models__
    
    def setup(self, filename: str):
        if not self.filepath:
            self.filepath = os.path.abspath(filename) if filename else None
            self.init(
                self.filepath,
                pragmas = self.pragmas_,
                #field_types = self.field_types_,
                #autoconnect = self.autoconnect_
            )
            
        print(self.tables)
        self.connect()
        self.create_tables(self.tables)
        self.close()


# NOTE: avoid circular or partial import
from . import models