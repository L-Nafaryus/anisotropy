from peewee import *

class BaseModel(Model):
    class Meta:
        database = db

class Structure(BaseModel):
    name = TextField()
    direction = TextField()
    theta = FloatField()
    
    r0 = FloatField()
    L = FloatField()
    radius = FloatField()
    length = FloatField()
    width = FloatField()
    height = FloatField()
    
    fillets = FloatField()
    path = TextField()

class Mesh(BaseModel):
    structure = ForeignKeyField(Structure, backref = "meshes")

    maxSize = FloatField() 
    minSize = FloatField() 

    fineness = IntegerField() 
    growthRate = FloatField()
    nbSegPerEdge = FloatField()
    nbSegPerRadius = FloatField()
    
    chordalErrorEnabled = BooleanField()
    chordalError = FloatField()
    
    secondOrder = BooleanField()
    optimize = BooleanField()
    quadAllowed = BooleanField()
    useSurfaceCurvature = BooleanField()
    fuseEdges = BooleanField()
    checkChartBoundary = BooleanField()

    viscousLayers = BooleanField()
    thickness = FloatField()
    numberOfLayers = IntegerField()
    stretchFactor = FloatField()
    isFacesToIgnore = BooleanField()
    #facesToIgnore = ["inlet", "outlet"]
    #faces = []
    #extrusionMethod = ExtrusionMethod.SURF_OFFSET_SMOOTH
    calculationTime = TimeField()


