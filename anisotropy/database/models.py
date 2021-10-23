# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

from peewee import (
    SqliteDatabase, JOIN, 
    Model, Field, 
    AutoField, ForeignKeyField, 
    TextField, FloatField, 
    IntegerField, BooleanField, 
    TimeField, DateTimeField
)
from anisotropy.database.utils import ListField, JSONField

sqliteDB = SqliteDatabase(
    None,
    pragmas = { "foreign_keys": 1 },
    field_types = { "list": "text" }
)

class Execution(Model):
    exec_id = AutoField()

    date = DateTimeField()
    executionTime = TimeField(null = True)

    class Meta:
        database = sqliteDB 
        db_table = "executions"


class Physics(Model):
    physics_id = AutoField()
    exec_id = ForeignKeyField(Execution, backref = "physics")

    volumeCell = FloatField(null = True)
    volume = FloatField(null = True)
    volumeRounded = FloatField(null = True)
    porosity = FloatField(null = True)
    porosityRounded = FloatField(null = True)
    flowRate = FloatField(null = True)
    permeability = FloatField(null = True)

    class Meta:
        database = sqliteDB 
        db_table = "physics"
        depends_on = Execution


class Shape(Model):
    structure_id = AutoField()
    exec_id = ForeignKeyField(Execution, backref = "physics")

    type = TextField()
    direction = ListField()
    theta = FloatField()

    r0 = FloatField(null = True)
    L = FloatField(null = True)
    radius = FloatField(null = True)

    filletsEnabled = BooleanField(null = True)
    fillets = FloatField(null = True)

    class Meta:
        database = sqliteDB 
        db_table = "shapes"
        depends_on = Execution


class Mesh(Model):
    mesh_id = AutoField()
    exec_id = ForeignKeyField(Execution, backref = "meshes")
    
    elements = IntegerField(null = True)
    edges = IntegerField(null = True)
    faces = IntegerField(null = True)
    volumes = IntegerField(null = True)
    tetrahedrons = IntegerField(null = True)
    prisms = IntegerField(null = True)
    pyramids = IntegerField(null = True)

    meshStatus = TextField(null = True, default = "Idle")
    meshCalculationTime = TimeField(null = True)

    class Meta:
        database = sqliteDB 
        db_table = "meshes"
        depends_on = Execution


class Flow(Model):
    flow_id = AutoField()
    exec_id = ForeignKeyField(Execution, backref = "flows")

    flowStatus = TextField(null = True, default = "Idle")
    flowCalculationTime = TimeField(null = True)

    class Meta:
        database = sqliteDB 
        db_table = "flows"
        depends_on = Execution


