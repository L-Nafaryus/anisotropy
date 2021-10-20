# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

import logging
    
SMESH_IMPORTED = False

try:
    import SMESH
    from salome.smesh import smeshBuilder

    SMESH_IMPORTED = True

except:
    pass

class Mesh(object):
    def __init__(self, geom):
        
        #   Mesh module
        if not SMESH_IMPORTED:
            raise ImportError("Cannot find the salome mesh modules.")

        else:
            self.smesh = smeshBuilder.New()
            self.smeshBuilder = smeshBuilder

        #   General attributes
        self.geom = geom
        self.mesh = self.smesh.Mesh(self.geom.shape, self.geom.name)
    
    def algo3d(self, algo, type = "tetrahedron"):
        smeshAlgo = self.mesh.__dict__.get(type.capitalize())
        self.meshAlgorithm3d = algo()
        self.meshAlgorithm3d.initialize(smeshAlgo(algo = self.meshAlgorithm3d.key))
        self.mesh.AddHypothesis(self.meshAlgorithm3d.hypo)
        
        return self.meshAlgorithm3d
    
    def algo2d(self, algo, type = "triangle"):
        smeshAlgo = self.mesh.__dict__.get(type.capitalize())
        self.meshAlgorithm2d = algo()
        self.meshAlgorithm2d.initialize(smeshAlgo(algo = self.meshAlgorithm2d.key))
        self.mesh.AddHypothesis(self.meshAlgorithm2d.hypo)
        
        return self.meshAlgorithm2d
    
    def algo1d(self, algo, type = "segment"):
        smeshAlgo = self.mesh.__dict__.get(type.capitalize())
        self.meshAlgorithm1d = algo()
        self.meshAlgorithm1d.initialize(smeshAlgo(algo = self.meshAlgorithm1d.key))
        self.mesh.AddHypothesis(self.meshAlgorithm1d.hypo)
        
        return self.meshAlgorithm1d
    
    def createGroups(self, prefix = None):
        prefix = prefix or ""
        
        for group in self.shape.groups:
            name = group.GetName()
            
            if name:
                name = prefix + name
                self.mesh.GroupOnGeom(group, name, SMESH.FACE)
    
    def compute(self):
        """Compute mesh.
        """
        isDone = self.mesh.Compute()
        out = ""
        err = self.mesh.GetComputeErrors()
        returncode = int(not isDone)
        
        return out, err, returncode
    
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

    def export(
        filename: str
    ):
        """Export a mesh.
        
        Supported formats: unv.
        
        :param filename:
            Name of the file to store the given mesh in.
        
        :return:
            Output, error messages and returncode
        """
        out, err, returncode = "", "", 0
        ext = os.path.splitext(filename)[1][1: ]
        
        try:
            if ext == "unv":
                self.mesh.ExportUNV(self.mesh, filename)
            
            else:
                raise NotImplementedError(f"{ ext } is not supported")
            
        except NotImplementedError as e:
            err = e
            returncode = 1
        
        except Exception as e:
            err = e.details.text
            returncode = 1
        
        return out, err, returncode
        

class MeshAlgorithm(object):
    pass

class AlgorithmHypothesis(object):
    pass

class Netgen3D(MeshAlgorithm):
    """
    MaxElementVolume
    Parameters
    ViscousLayers
    """
    def __init__(self, **kwargs):
        self.key = smeshBuilder.NETGEN_3D
    
    def initialize(self, algo, hypo): #thesises: list):
        self.algo = algo
        #self.hypo = self.algo.Parameters()

        #for hypo in hypothesises:

        self.hypo = self.__dict__[hypo.__name__]()
    
    class ViscousLayers(AlgorithmHypothesis):
        def __init__(self,
            algo,
            thickness = 1, 
            numberOfLayers = 1, 
            stretchFactor = 0,
            faces = [], 
            isFacesToIgnore = True, 
            extrMethod = "SURF_OFFSET_SMOOTH",
            **kwargs
        ):
            extrusionMethod = dict(
                SURF_OFFSET_SMOOTH = smeshBuilder.SURF_OFFSET_SMOOTH,
                FACE_OFFSET = smeshBuilder.FACE_OFFSET,
                NODE_OFFSET = smeshBuilder.NODE_OFFSET,
            ).get(extrMethod, smeshBuilder.SURF_OFFSET_SMOOTH)

            self.hypo = self.algo.ViscousLayers(
                thickness,
                numberOfLayers,
                stretchFactor,
                faces,
                isFacesToIgnore,
                extrusionMethod
            )   

    class Parameters(AlgorithmHypothesis):
        def __init__(self, algo):
            self.hypo = self.algo.Parameters()

        @property
        def minSize(self):
            return self.hypo.GetMinSize()
        
        @minSize.setter
        def minSize(self, value):
            self.hypo.SetMinSize(value)

        @property
        def maxSize(self):
            return self.hypo.GetMaxSize()

        @maxSize.setter
        def maxSize(self, value):
            self.hypo.SetMaxSize(value)

        @property
        def fineness(self):
            return self.hypo.GetFineness()

        @fineness.setter
        def fineness(self, value):
            self.hypo.SetFineness(value)

        @property
        def growthRate(self):
            return self.hypo.GetGrowthRate()

        @growthRate.setter
        def growthRate(self, value):
            self.hypo.SetGrowthRate(value)

        @property
        def nbSegPerEdge(self):
            return self.hypo.GetNbSegPerEdge()

        @nbSegPerEdge.setter
        def nbSegPerEdge(self, value):
            self.hypo.SetNbSegPerEdge(value)

        @property
        def nbSegPerRadius(self):
            return self.hypo.GetNbSegPerRadius()

        @nbSegPerRadius.setter
        def nbSegPerRadius(self, value):
            self.hypo.SetNbSegPerRadius(value)

        @property
        def chordalErrorEnabled(self):
            return self.hypo.GetChordalErrorEnabled()

        @chordalErrorEnabled.setter
        def chordalErrorEnabled(self, value):
            self.hypo.SetChordalErrorEnabled(value)

        @property
        def chordalError(self):
            return self.hypo.GetChordalError()

        @chordalError.setter
        def chordalError(self, value):
            self.hypo.SetChordalError(value)

        @property
        def secondOrder(self):
            return self.hypo.GetSecondOrder()

        @secondOrder.setter
        def secondOrder(self, value):
            self.hypo.SetSecondOrder(value)

        @property
        def optimize(self):
            return self.hypo.GetOptimize()

        @optimize.setter
        def optimize(self, value):
            self.hypo.SetOptimize(value)

        @property
        def quadAllowed(self):
            return self.hypo.GetQuadAllowed()

        @quadAllowed.setter
        def quadAllowed(self, value):
            self.hypo.SetQuadAllowed(value)

        @property
        def useSurfaceCurvature(self):
            return self.hypo.GetUseSurfaceCurvature()

        @useSurfaceCurvature.setter
        def useSurfaceCurvature(self, value):
            self.hypo.SetUseSurfaceCurvature(value)

        @property
        def fuseEdges(self):
            return self.hypo.GetFuseEdges()

        @fuseEdges.setter
        def fuseEdges(self, value):
            self.hypo.SetFuseEdges(value)

        @property
        def checkChartBoundary(self):
            return self.hypo.GetCheckChartBoundary()

        @checkChartBoundary.setter
        def GetCheckChartBoundary(self, value):
            self.hypo.SetCheckChartBoundary(value)

class MEFISTO(MeshAlgorithm):
    pass 
