# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

import os
from .models import (
    sqliteDB,
    Execution, 
    Physics, 
    Shape, 
    Mesh, 
    Flow
)


class Database(object):
    def __init__(self, filename: str):
        self.filename = filename
        self.database = sqliteDB

    def setup(self):
        path = os.path.abspath(self.filename)
        os.makedirs(path, exist_ok = True)

        self.database.init(path)
        
        if not os.path.exists(path):
            self.database.create_tables([
                Execution,
                Physics,
                Shape,
                Mesh,
                Flow
            ])


