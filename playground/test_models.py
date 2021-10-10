#!/usr/bin/env python
# -*- coding: utf-8 -*-

from peewee import (
    SqliteDatabase, JOIN, 
    Model, Field, 
    AutoField, ForeignKeyField, 
    TextField, FloatField, 
    IntegerField, BooleanField, 
    TimeField
)

db = SqliteDatabase("test_db.db", pragmas = { "foreign_keys" : 1, "journal_mode": "wal" })

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

class Structure(Model):
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
    
    class Meta:
        database = db
        db_table = "structures"


class Mesh(Model):
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

    class Meta:
        database = db
        db_table = "meshes"
        depends_on = Structure
