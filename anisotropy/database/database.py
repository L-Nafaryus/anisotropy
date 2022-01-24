# -*- coding: utf-8 -*-

from __future__ import annotations
from numpy import ndarray

import peewee as pw
import pathlib
import time

from . import tables 


class Database(pw.SqliteDatabase):
    def __init__(self, *args, **kwargs):
        """A Database object contains SQLite database with convient
        properties and methods
        """
        self.filepath = kwargs.get("path", None)
        self.pragmas_ = kwargs.get("pragmas", { "foreign_keys": 1, "journal_mode": "wal" })
        self.field_types_ = kwargs.get("field_types", { "list": "text" })
        self.autoconnect_ = kwargs.get("autoconnect", False)
        
        pw.SqliteDatabase.__init__(
            self,
            None,
            pragmas = self.pragmas_,
            field_types = self.field_types_,
            autoconnect = self.autoconnect_
        )

        if self.filepath:
            self.setup()

    @property
    def tables(self) -> list:
        """Return all tables as list.
        """
        return [ tables.__dict__[table] for table in tables.__all__ ]
    
    def setup(self, filename: str = None):
        """Initialize database and create tables.

        :param filename:
            Path to the file.
        :return:
            Self.
        """        
        self.filepath = pathlib.Path(filename or self.filepath).resolve()
        self.init(
            self.filepath,
            pragmas = self.pragmas_
        )
        tables.database_proxy.initialize(self)

        with self:
            self.create_tables(self.tables)

        return self

    def csave(self, table: pw.Model, tries: int = 100):
        """Try to save data from model to the database ignoring
        peewee.OperationalError. Usefull for concurrent processes.

        :param table:
            Table to save.
        :param tries:
            Number of tries. Falling to sleep for 1 second if database 
            is locked.
        """
        while tries >= 0:
            if self.is_closed():
                self.connect()
            
            try:
                table.save()
            
            except pw.OperationalError:
                tries -= 1
                time.sleep(1)
            
            else:
                self.close()
                break

    def getExecution(self, idn: int) -> tables.Execution | None:
        """Get execution entry from database.

        :param idn:
            Index of the execution.
        :return:
            If entry is found returns Model instance else None.
        """
        query = tables.Execution.select().where(tables.Execution.exec_id == idn)

        with self:
            table = query.get() if query.exists() else None

        return table

    def getLatest(self) -> tables.Execution | None:
        """Get latest execution entry from database.

        :return:
            If entry is found returns Model instance else None.
        """
        query = tables.Execution.select()

        with self:
            table = query[-1] if query.exists() else None

        return table

    def getShape(
        self, 
        label: str = None, 
        direction: list[float] | ndarray = None, 
        alpha: float = None, 
        execution: int = None, 
        **kwargs
    ) -> tables.Shape | None:
        """Get shape entry from database.

        :param label:
            Label of the shape.
        :param direction:
            Array of floats represents direction vector.
        :param alpha:
            Spheres overlap parameter.
        :param execution:
            Index of the execution. If None, use latest.
        :return:
            If entry is found returns Model instance else None.
        """
        execution = execution or self.getLatest()
        query = (
            tables.Shape
            .select()
            .join(tables.Execution, pw.JOIN.LEFT_OUTER)
            .where(
                tables.Execution.exec_id == execution,
                tables.Shape.label == label,
                tables.Shape.direction == direction,
                tables.Shape.alpha == alpha
            )
        )

        with self:
            table = query.get() if query.exists() else None

        return table

    def getMesh(
        self, 
        label: str = None, 
        direction: list[float] | ndarray = None, 
        alpha: float = None, 
        execution: int = None, 
        **kwargs
    ) -> tables.Mesh | None:
        """Get mesh entry from database.

        :param label:
            Label of the shape.
        :param direction:
            Array of floats represents direction vector.
        :param alpha:
            Spheres overlap parameter.
        :param execution:
            Index of the execution. If None, use latest.
        :return:
            If entry is found returns Model instance else None.
        """
        execution = execution or self.getLatest()
        query = (
            tables.Mesh
            .select()
            .join(tables.Shape, pw.JOIN.LEFT_OUTER)
            .join(tables.Execution, pw.JOIN.LEFT_OUTER)
            .where(
                tables.Execution.exec_id == execution,
                tables.Shape.label == label,
                tables.Shape.direction == direction,
                tables.Shape.alpha == alpha
            )
        )

        with self:
            table = query.get() if query.exists() else None

        return table

    def getFlowOnephase(
        self, 
        label: str = None, 
        direction: list[float] | ndarray = None, 
        alpha: float = None, 
        execution: int = None, 
        to_dict: bool = False,
        **kwargs
    ) -> tables.Mesh | dict | None:
        """Get one phase flow entry from database.

        :param label:
            Label of the shape.
        :param direction:
            Array of floats represents direction vector.
        :param alpha:
            Spheres overlap parameter.
        :param execution:
            Index of the execution. If None, use latest.
        :param to_dict:
            If True, convert result to dict.
        :return:
            If entry is found returns Model instance or dict else None.
        """
        execution = execution or self.getLatest()
        query = (
            tables.FlowOnephase
            .select()
            .join(tables.Mesh, pw.JOIN.LEFT_OUTER)
            .join(tables.Shape, pw.JOIN.LEFT_OUTER)
            .join(tables.Execution, pw.JOIN.LEFT_OUTER)
            .where(
                tables.Execution.exec_id == execution,
                tables.Shape.label == label,
                tables.Shape.direction == direction,
                tables.Shape.alpha == alpha
            )
        )

        with self:
            if to_dict:
                table = query.dicts().get() if query.exists() else None
            
            else:
                table = query.get() if query.exists() else None

        return table
