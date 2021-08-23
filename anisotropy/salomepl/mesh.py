# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

import logging

logger = logging.getLogger("anisotropy")

try:
    import SMESH
    from salome.smesh import smeshBuilder

except ImportError:
    logger.debug("Trying to get SALOME mesh modules outside SALOME environment. Modules won't be imported.")

if globals().get("smeshBuilder"):
    smesh = smeshBuilder.New()

else:
    smesh = None

import enum

class Fineness(enum.Enum):
    VeryCoarse = 0
    Coarse = 1
    Moderate = 2
    Fine = 3
    VeryFine = 4
    Custom = 5


def getSmesh():
    return smesh


def updateParams(old, new: dict):
    old.SetMaxSize(new.get("maxSize", old.GetMaxSize()))
    old.SetMinSize(new.get("minSize", old.GetMinSize()))

    old.SetFineness(new.get("fineness", old.GetFineness()))
    old.SetGrowthRate(new.get("growthRate", old.GetGrowthRate()))
    old.SetNbSegPerEdge(new.get("nbSegPerEdge", old.GetNbSegPerEdge()))
    old.SetNbSegPerRadius(new.get("nbSegPerRadius", old.GetNbSegPerRadius()))

    old.SetChordalErrorEnabled(new.get("chordalErrorEnabled", old.GetChordalErrorEnabled()))
    old.SetChordalError(new.get("chordalError", old.GetChordalError()))

    old.SetSecondOrder(new.get("secondOrder", old.GetSecondOrder()))
    old.SetOptimize(new.get("optimize", old.GetOptimize()))
    old.SetQuadAllowed(new.get("quadAllowed", old.GetQuadAllowed()))
    old.SetUseSurfaceCurvature(new.get("useSurfaceCurvature", old.GetUseSurfaceCurvature()))
    old.SetFuseEdges(new.get("fuseEdges", old.GetFuseEdges()))
    old.SetCheckChartBoundary(new.get("checkChartBoundary", old.GetCheckChartBoundary()))


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

    def _extrusionMethod(self, key: str):
        return dict(
            SURF_OFFSET_SMOOTH = smeshBuilder.SURF_OFFSET_SMOOTH,
            FACE_OFFSET = smeshBuilder.FACE_OFFSET,
            NODE_OFFSET = smeshBuilder.NODE_OFFSET,
        ).get(key, smeshBuilder.SURF_OFFSET_SMOOTH)

    def ViscousLayers(self,
            thickness = 1, 
            numberOfLayers = 1, 
            stretchFactor = 0,
            faces = [], 
            isFacesToIgnore = True, 
            extrMethod = "SURF_OFFSET_SMOOTH",
            **kwargs
        ):

        self.viscousLayers = self.algo.ViscousLayers(
            thickness,
            numberOfLayers,
            stretchFactor,
            faces,
            isFacesToIgnore,
            self._extrusionMethod(extrMethod)
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
        err = self.mesh.GetComputeErrors()

        return "", err, returncode

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

