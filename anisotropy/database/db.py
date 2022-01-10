# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

import os
from peewee import SqliteDatabase, JOIN, OperationalError
from . import models

class Database(SqliteDatabase):
    def __init__(self, *args, **kwargs):
        self.filepath = kwargs.get("path", None)
        self.pragmas_ = kwargs.get("pragmas", { "foreign_keys": 1, "journal_mode": "wal" })
        self.field_types_ = kwargs.get("field_types", { "list": "text" })
        self.autoconnect_ = kwargs.get("autoconnect", False)
        
        SqliteDatabase.__init__(
            self,
            None,
            pragmas = self.pragmas_,
            field_types = self.field_types_,
            autoconnect = self.autoconnect_
        )

        if self.filepath:
            self.setup()

    @property
    def tables(self):
        return models.__models__
    
    def setup(self, filename: str = None):
        #if not self.filepath:
        self.filepath = os.path.abspath(filename or self.filepath)
        self.init(
            self.filepath,
            pragmas = self.pragmas_,
            #field_types = self.field_types_,
            #autoconnect = self.autoconnect_
        )
        models.__database_proxy__.initialize(self)

        with self:
            self.create_tables(self.tables)

    def csave(self, table, tries: int = 100):
        while tries >= 0:
            if self.is_closed():
                self.connect()
            
            try:
                table.save()
            
            except OperationalError as e:
                logger.debug(e)
                tries -= 1
                time.sleep(1)
            
            else:
                self.close()
                break

    def getExecution(self, idn):
        query = models.Execution.select().where(models.Execution.exec_id == idn)

        with self:
            table = query.get() if query.exists() else None

        return table

    def getLatest(self):
        query = models.Execution.select()

        with self:
            table = query[-1] if query.exists() else None

        return table

    def getShape(self, label = None, direction = None, alpha = None, execution = None, **kwargs):
        execution = execution or self.getLatest()
        query = (
            models.Shape
            .select()
            .join(models.Execution, JOIN.LEFT_OUTER)
            .where(
                models.Execution.exec_id == execution,
                models.Shape.label == label,
                models.Shape.direction == direction,
                models.Shape.alpha == alpha
            )
        )

        with self:
            table = query.get() if query.exists() else None

        return table

    def getMesh(self, label = None, direction = None, alpha = None, execution = None, **kwargs):
        execution = execution or self.getLatest()
        query = (
            models.Mesh
            .select()
            .join(models.Shape, JOIN.LEFT_OUTER)
            .join(models.Execution, JOIN.LEFT_OUTER)
            .where(
                models.Execution.exec_id == execution,
                models.Shape.label == label,
                models.Shape.direction == direction,
                models.Shape.alpha == alpha
            )
        )

        with self:
            table = query.get() if query.exists() else None

        return table

    def getFlowOnephase(self, label = None, direction = None, alpha = None, execution = None, to_dict = False, **kwargs):
        execution = execution or self.getLatest()
        query = (
            models.FlowOnephase
            .select()
            .join(models.Mesh, JOIN.LEFT_OUTER)
            .join(models.Shape, JOIN.LEFT_OUTER)
            .join(models.Execution, JOIN.LEFT_OUTER)
            .where(
                models.Execution.exec_id == execution,
                models.Shape.label == label,
                models.Shape.direction == direction,
                models.Shape.alpha == alpha
            )
        )

        with self:
            if to_dict:
                table = query.dicts().get() if query.exists() else None
            
            else:
                table = query.get() if query.exists() else None

        return table
