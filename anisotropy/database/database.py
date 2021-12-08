# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

import os
from .models import (
    sqliteDB,
    Execution, 
    Shape, 
    Mesh, 
    FlowOnephase
)


class Database(object):
    def __init__(self, filename: str):
        self.filename = filename
        self.database = sqliteDB

    def setup(self):
        path = os.path.abspath(self.filename)
        #os.makedirs(path, exist_ok = True)
        
        self.database.init(
            path,
            pragmas = { "foreign_keys": 1 },
            field_types = { "list": "text" },
            autoconnect = False
        )
        
        if not os.path.exists(path):
            with self.database:
                self.database.create_tables([Execution])
                self.database.create_tables([
                    Shape,
                    Mesh,
                    FlowOnephase
                ])


