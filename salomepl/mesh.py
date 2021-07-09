import SMESH
from salome.smesh import smeshBuilder
smesh = smeshBuilder.New()

import enum

class Fineness(enum.Enum):
    VeryCoarse = 0
    Coarse = 1
    Moderate = 2
    Fine = 3
    VeryFine = 4
    Custom = 5

class ExtrusionMethod(object):
    SURF_OFFSET_SMOOTH = smeshBuilder.SURF_OFFSET_SMOOTH
    FACE_OFFSET = smeshBuilder.FACE_OFFSET
    NODE_OFFSET = smeshBuilder.NODE_OFFSET

def getSmesh():
    return smesh

def updateParams(old, new: dict):
    old.SetMaxSize(new.get("maxSize") if new.get("maxSize") else old.GetMaxSize())
    old.SetMinSize(new.get("minSize") if new.get("minSize") else old.GetMinSize())

    old.SetFineness(new.get("fineness") if new.get("fineness") else old.GetFineness())
    old.SetGrowthRate(new.get("growthRate") if new.get("growthRate") else old.GetGrowthRate())
    old.SetNbSegPerEdge(new.get("nbSegPerEdge") if new.get("nbSegPerEdge") else old.GetNbSegPerEdge())
    old.SetNbSegPerRadius(new.get("nbSegPerRadius") if new.get("nbSegPerRadius") else old.GetNbSegPerRadius())

    old.SetChordalErrorEnabled(new.get("chordalErrorEnabled") if new.get("chordalErrorEnabled") else old.GetChordalErrorEnabled())
    old.SetChordalError(new.get("chordalError") if new.get("chordalError") else old.GetChordalError())

    old.SetSecondOrder(new.get("secondOrder") if new.get("secondOrder") else old.GetSecondOrder())
    old.SetOptimize(new.get("optimize") if new.get("optimize") else old.GetOptimize())
    old.SetQuadAllowed(new.get("quadAllowed") if new.get("quadAllowed") else old.GetQuadAllowed())
    old.SetUseSurfaceCurvature(new.get("useSurfaceCurvature") if new.get("useSurfaceCurvature") else old.GetUseSurfaceCurvature())
    old.SetFuseEdges(new.get("fuseEdges") if new.get("fuseEdges") else old.GetFuseEdges())
    old.SetCheckChartBoundary(new.get("checkChartBoundary") if new.get("checkChartBoundary") else old.GetCheckChartBoundary())


class Mesh(object):
    def __init__(self, shape, name = ""):
        self.name = name if name else shape.GetName()
        self.mesh = smesh.Mesh(shape, self.name)
        self.geom = shape
        self.algo = None
        self.params = None
        self.viscousLayers = None

        self.submeshes = []
    
    def Tetrahedron(self, **kwargs):
        self.algo = self.mesh.Tetrahedron(algo = smeshBuilder.NETGEN_1D2D3D)
        self.params = self.algo.Parameters()

        self.params = updateParams(self.params, kwargs)

    def ViscousLayers(self,
            thickness = 1, 
            numberOfLayers = 1, 
            stretchFactor = 0,
            faces = [], 
            isFacesToIgnore = True, 
            extrMethod = ExtrusionMethod.SURF_OFFSET_SMOOTH, 
            **kwargs
        ):

        self.viscousLayers = self.algo.ViscousLayers(
            thickness,
            numberOfLayers,
            stretchFactor,
            faces,
            isFacesToIgnore,
            extrMethod
        )

    def Triangle(self, subshape, **kwargs):
        submesh = Submesh(self.mesh, subshape)
        submesh.algo = self.mesh.Triangle(algo = smeshBuilder.NETGEN_1D2D, geom = subshape)
        submesh.mesh = submesh.algo.subm
        submesh.params = submesh.algo.Parameters()

        submesh.params = updateParams(submesh.params, kwargs)

        self.submeshes.append(submesh)
    
    def assignGroups(self, withPrefix = True):
        prefix = "smesh_" if withPrefix else ""

        for group in self.mesh.geompyD.GetGroups(self.geom):
            if group.GetName():
                self.mesh.GroupOnGeom(group, f"{ prefix }{ group.GetName() }", SMESH.FACE)

    def compute(self):
        isDone = self.mesh.Compute()
        returncode = int(not isDone)
        errors = self.mesh.GetComputeErrors()

        return returncode, errors

    def stats(self):
        return {
            "elements":     self.mesh.NbElements(),
            "edges":        self.mesh.NbEdges(),
            "faces":        self.mesh.NbFaces(),
            "volumes":      self.mesh.NbVolumes(),
            "tetrahedrons": self.mesh.NbTetras(),
            "prisms":       self.mesh.NbPrisms(),
            "pyramids":     self.mesh.NbPyramids()
        }

    def exportUNV(self, path):
        returncode = 0
        error = ""

        try:
            self.mesh.ExportUNV(path)

        except Exception as e:
            error = e.details.text
            returncode = 1

        return returncode, error

    def removePyramids(self):
        if self.mesh.NbPyramids() > 0:
            pyramidCriterion = smesh.GetCriterion(
                SMESH.VOLUME,
                SMESH.FT_ElemGeomType,
                SMESH.FT_Undefined,
                SMESH.Geom_PYRAMID
            )
            pyramidGroup = self.mesh.MakeGroupByCriterion("pyramids", pyramidCriterion)
            pyramidVolumes = self.mesh.GetIDSource(pyramidGroup.GetIDs(), SMESH.VOLUME)

            self.mesh.SplitVolumesIntoTetra(pyramidVolumes, smesh.Hex_5Tet)
            
            self.mesh.RemoveGroup(pyramidGroup)
            self.mesh.RenumberElements()



class Submesh(object):
    def __init__(self, father, subshape, name = ""):
        self.name = name if name else subshape.GetName()
        self.mesh = None
        self.geom = subshape
        self.algo = None
        self.params = None

