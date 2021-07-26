from peewee import *

class ListField(Field):
    field_type = "list"

    def db_value(self, value):
        return str(value)

    def python_value(self, value):
        pval = []

        for ch in value[1 : -1].split(","):
            try:
                pval.append(float(ch))

            except:
                pass

            finally:
                pval.append(ch.strip().replace("'", ""))

        return pval

db = SqliteDatabase(
    None,
    pragmas = { "foreign_keys": 1 },
    field_types = { "list": "text" }
)

class BaseModel(Model):
    class Meta:
        database = db


class Structure(BaseModel):
    name = TextField()
    direction = ListField()
    theta = FloatField()

    r0 = FloatField()
    L = FloatField()
    radius = FloatField()

    filletsEnabled = BooleanField()
    fillets = FloatField()
    path = TextField()


class Mesh(BaseModel):
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


class SubMesh(Mesh):
    mesh_id = ForeignKeyField(Mesh, backref = "submeshes")


class MeshResult(BaseModel):
    mesh_id = ForeignKeyField(Mesh, backref = "meshresults")

    calculationTime = TimeField(null = True)

