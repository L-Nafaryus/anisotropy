# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

from peewee import (
    SqliteDatabase, JOIN, 
    Model, Field, 
    AutoField, ForeignKeyField, 
    TextField, FloatField, 
    IntegerField, BooleanField, 
    TimeField
)
import json

db = SqliteDatabase(
    None,
    pragmas = { "foreign_keys": 1 },
    field_types = { "list": "text" }
)


class BaseModel(Model):
    class Meta:
        database = db


class ListField(Field):
    field_type = "list"

    def db_value(self, value):
        return str(value)

    def python_value(self, value):
        pval = []

        for entry in value[1 : -1].split(","):
            try:
                pval.append(float(entry))

            except:
                pval.append(entry.strip().replace("'", ""))

        return pval


class JSONField(TextField):
    def db_value(self, value):
        return json.dumps(value)

    def python_value(self, value):
        if value is not None:
            return json.loads(value)


class Structure(BaseModel):
    structure_id = AutoField()

    type = TextField()
    direction = ListField()
    theta = FloatField()

    r0 = FloatField(null = True)
    L = FloatField(null = True)
    radius = FloatField(null = True)

    filletsEnabled = BooleanField(null = True)
    fillets = FloatField(null = True)
    #path = TextField()


class Mesh(BaseModel):
    mesh_id = AutoField()
    structure_id = ForeignKeyField(Structure, backref = "meshes")

    maxSize = FloatField(null = True) 
    minSize = FloatField(null = True) 

    fineness = IntegerField(null = True) 
    growthRate = FloatField(null = True)
    nbSegPerEdge = FloatField(null = True)
    nbSegPerRadius = FloatField(null = True)
    
    chordalErrorEnabled = BooleanField(null = True)
    chordalError = FloatField(null = True)
    
    secondOrder = BooleanField(null = True)
    optimize = BooleanField(null = True)
    quadAllowed = BooleanField(null = True)
    useSurfaceCurvature = BooleanField(null = True)
    fuseEdges = BooleanField(null = True)
    checkChartBoundary = BooleanField(null = True)

    viscousLayers = BooleanField(null = True)
    thickness = FloatField(null = True)
    numberOfLayers = IntegerField(null = True)
    stretchFactor = FloatField(null = True)
    isFacesToIgnore = BooleanField(null = True)
    facesToIgnore = ListField(null = True)
    #faces = []
    extrusionMethod = TextField(null = True)


class SubMesh(BaseModel):
    submesh_id = AutoField()
    mesh_id = ForeignKeyField(Mesh, backref = "submeshes")
    name = TextField()

    maxSize = FloatField(null = True) 
    minSize = FloatField(null = True) 

    fineness = IntegerField(null = True) 
    growthRate = FloatField(null = True)
    nbSegPerEdge = FloatField(null = True)
    nbSegPerRadius = FloatField(null = True)
    
    chordalErrorEnabled = BooleanField(null = True)
    chordalError = FloatField(null = True)
    
    secondOrder = BooleanField(null = True)
    optimize = BooleanField(null = True)
    quadAllowed = BooleanField(null = True)
    useSurfaceCurvature = BooleanField(null = True)
    fuseEdges = BooleanField(null = True)
    checkChartBoundary = BooleanField(null = True)


class MeshResult(BaseModel):
    meshresult_id = AutoField()
    mesh_id = ForeignKeyField(Mesh, backref = "meshresults")
    
    surfaceArea = FloatField(null = True)
    volume = FloatField(null = True)
    
    elements = IntegerField(null = True)
    edges = IntegerField(null = True)
    faces = IntegerField(null = True)
    volumes = IntegerField(null = True)
    tetrahedrons = IntegerField(null = True)
    prisms = IntegerField(null = True)
    pyramids = IntegerField(null = True)

    status = TextField(null = True, default = "Idle")
    calculationTime = TimeField(null = True)

class Flow(BaseModel):
    flow_id = AutoField()
    structure_id = ForeignKeyField(Structure, backref = "flows")

    scale = ListField(null = True)
    pressure = JSONField(null = True)
    velocity = JSONField(null = True)
    transportProperties = JSONField(null = True)

   
class FlowApproximation(BaseModel):
    flow_approximation_id = AutoField()
    flow_id = ForeignKeyField(Flow, backref = "flowapprox")

    pressure = JSONField(null = True)
    velocity = JSONField(null = True)
    transportProperties = JSONField(null = True)

class FlowResult(BaseModel):
    flowresult_id = AutoField()
    flow_id = ForeignKeyField(Flow, backref = "flowresults")

    flowRate = FloatField(null = True)

    status = TextField(null = True, default = "Idle")
    calculationTime = TimeField(null = True)
