# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

from peewee import (
    SqliteDatabase, JOIN, 
    Model, Field, 
    AutoField, ForeignKeyField, 
    TextField, FloatField, 
    IntegerField, BooleanField, 
    TimeField, DateTimeField, Proxy
)
from .utils import JSONField

__database_proxy__ = Proxy()

class Execution(Model):
    exec_id = AutoField()

    date = DateTimeField()
    executionTime = TimeField(null = True)

    class Meta:
        database = __database_proxy__
        table_name = "executions"


class Shape(Model):
    shape_id = AutoField()
    exec_id = ForeignKeyField(Execution, backref = "executions", on_delete = "CASCADE")

    shapeStatus = TextField(null = True, default = "idle")
    shapeExecutionTime = TimeField(null = True)   
    
    label = TextField(null = True)
    direction = JSONField(null = True)
    alpha = FloatField(null = True)

    r0 = FloatField(null = True)
    L = FloatField(null = True)
    radius = FloatField(null = True)

    filletsEnabled = BooleanField(null = True)
    fillets = FloatField(null = True)

    volumeCell = FloatField(null = True)
    volume = FloatField(null = True)
    porosity = FloatField(null = True)

    class Meta:
        database = __database_proxy__
        table_name = "shapes"
        #depends_on = Execution


class Mesh(Model):
    mesh_id = AutoField()
    shape_id = ForeignKeyField(Shape, backref = "shapes", on_delete = "CASCADE")
 
    meshStatus = TextField(null = True, default = "idle")
    meshExecutionTime = TimeField(null = True)   
    
    elements = IntegerField(null = True)
    edges = IntegerField(null = True)
    faces = IntegerField(null = True)
    volumes = IntegerField(null = True)
    tetrahedrons = IntegerField(null = True)
    prisms = IntegerField(null = True)
    pyramids = IntegerField(null = True)


    class Meta:
        database = __database_proxy__
        table_name = "meshes"
        #depends_on = Execution


class FlowOnephase(Model):
    flow_id = AutoField()
    mesh_id = ForeignKeyField(Mesh, backref = "meshes", on_delete = "CASCADE")

    flowStatus = TextField(null = True, default = "idle")
    flowExecutionTime = TimeField(null = True)

    pressureInlet = FloatField(null = True)
    pressureOutlet = FloatField(null = True)
    pressureInternal = FloatField(null = True)
    velocityInlet = JSONField(null = True)
    velocityOutlet = JSONField(null = True)
    velocityInternal = JSONField(null = True)
    viscosity = FloatField(null = True)
    viscosityKinematic = FloatField(null = True)
    density = FloatField(null = True)
    flowRate = FloatField(null = True)
    permeability = FloatField(null = True)

    class Meta:
        database = __database_proxy__
        table_name = "flows"
        #depends_on = Execution


__models__ = [
    Execution,
    Shape,
    Mesh,
    FlowOnephase
]