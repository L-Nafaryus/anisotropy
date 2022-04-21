# -*- coding: utf-8 -*-

import peewee as pw

from . import utils


#   proxy, assign database later
database_proxy = pw.Proxy()


class Execution(pw.Model):
    exec_id = pw.AutoField()

    date = pw.DateTimeField()
    executionTime = pw.TimeField(null = True)

    class Meta:
        database = database_proxy
        table_name = "executions"


class Shape(pw.Model):
    shape_id = pw.AutoField()
    exec_id = pw.ForeignKeyField(Execution, backref = "executions", on_delete = "CASCADE")

    shapeStatus = pw.TextField(null = True, default = "idle")
    shapeExecutionTime = pw.TimeField(null = True)   
    
    label = pw.TextField(null = True)
    direction = utils.JSONField(null = True)
    alpha = pw.FloatField(null = True)

    r0 = pw.FloatField(null = True)
    L = pw.FloatField(null = True)
    radius = pw.FloatField(null = True)

    filletsEnabled = pw.BooleanField(null = True)
    fillets = pw.FloatField(null = True)

    volumeCell = pw.FloatField(null = True)
    volume = pw.FloatField(null = True)
    porosity = pw.FloatField(null = True)

    areaOutlet = pw.FloatField(null = True)
    length = pw.FloatField(null = True)
    areaCellOutlet = pw.FloatField(null = True)

    class Meta:
        database = database_proxy
        table_name = "shapes"
        # depends_on = Execution


class Mesh(pw.Model):
    mesh_id = pw.AutoField()
    shape_id = pw.ForeignKeyField(Shape, backref = "shapes", on_delete = "CASCADE")
 
    meshStatus = pw.TextField(null = True, default = "idle")
    meshExecutionTime = pw.TimeField(null = True)   
    
    elements = pw.IntegerField(null = True)
    edges = pw.IntegerField(null = True)
    faces = pw.IntegerField(null = True)
    volumes = pw.IntegerField(null = True)
    tetrahedrons = pw.IntegerField(null = True)
    prisms = pw.IntegerField(null = True)
    pyramids = pw.IntegerField(null = True)

    class Meta:
        database = database_proxy
        table_name = "meshes"
        # depends_on = Execution


class FlowOnephase(pw.Model):
    flow_id = pw.AutoField()
    mesh_id = pw.ForeignKeyField(Mesh, backref = "meshes", on_delete = "CASCADE")

    flowStatus = pw.TextField(null = True, default = "idle")
    flowExecutionTime = pw.TimeField(null = True)

    pressureInlet = pw.FloatField(null = True)
    pressureOutlet = pw.FloatField(null = True)
    pressureInternal = pw.FloatField(null = True)
    velocityInlet = utils.JSONField(null = True)
    velocityOutlet = utils.JSONField(null = True)
    velocityInternal = utils.JSONField(null = True)
    viscosity = pw.FloatField(null = True)
    viscosityKinematic = pw.FloatField(null = True)
    density = pw.FloatField(null = True)
    flowRate = pw.FloatField(null = True)
    permeability = pw.FloatField(null = True)

    class Meta:
        database = database_proxy
        table_name = "flows"
        # depends_on = Execution


__all__ = [
    "Execution",
    "Shape",
    "Mesh",
    "FlowOnephase"
]
