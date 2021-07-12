from peewee import *

class BaseModel(Model):
    class Meta:
        database = db

class Structure(BaseModel):
    name = TextField()
    direction = TextField()
    theta = FloatField()

class Mesh(BaseModel):
    maxSize = FloatField()
    minSize = FloatField()
    chordalErrorEnabled = BooleanField()
    chordalError = FloatField()
    calculationTime = TimeField()
    structure = ForeignKeyField(Structure, backref = "mesh")

