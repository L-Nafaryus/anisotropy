# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

import logging

GEOM_IMPORTED = False

try:
    import GEOM
    from salome.geom import geomBuilder

    GEOM_IMPORTED = True

except:
    pass


class StructureGeometry(object):
    def __init__(
        self,
        direction: list = None,
        theta: float = None,
        r0: float = 1,
        #L: float = None,
        #radius: float = None,
        filletsEnabled: bool = False,
        #fillets: float = None,
        **kwargs
    ):
        """Constructor method.
        
        :param direction:
            Flow vector that characterizes geometry.
        
        :param theta:
            Spheres overlap parameter.
        
        :param r0:
            Initial spheres radius.
        
        :param filletsEnabled:
            Enable fillets beetween spheres.
        """
        #   Geometry parameters
        self.direction = direction
        self.theta = theta
        self.r0 = r0
        self.filletsEnabled = filletsEnabled
        #self.fillets = fillets
        self.filletScale = 0.8
        
        #   General attributes
        self.shape = None
        self.groups = []
        self.shapeCell = None
        self.shapeLattice = None

        #   Geometry module
        if not GEOM_IMPORTED:
            raise ImportError("Cannot find the salome modules.")

        else:
            self.geo = geomBuilder.New() 
    
    @property
    def name(self):
        """(Override) Shape name.
        """
        pass
    
    @property
    def L(self):
        """(Override) Parameter depending on the ``r0``.
        """
        pass
    
    @property
    def radius(self):
        """Spheres radius
        """
        return self.r0 / (1 - self.theta)
    
    @property
    def volumeCell(self):
        """General volume of the cell.
        """
        return self.geo.BasicProperties(self.shapeCell, theTolerance = 1e-06)[2]
    
    @property
    def volume(self):
        """Volume of the structure.
        """
        return self.geo.BasicProperties(self.shape, theTolerance = 1e-06)[2]
    
    @property
    def porosity(self):
        """Porosity of the structure.
        """
        return self.volume / self.volumeCell
    
    def build(self):
        """(Override) Construct shape and physical groups.
        """
        pass
    
    def isValid(self) -> (bool, str):
        """Check a topology of the given shape.
        
        :return:
            True, if the shape "seems to be valid" else False and description.
        """
        return self.geo.CheckShape(self.shape, theIsCheckGeom = True, theReturnStatus = 1)
    
    def heal(self):
        """Try to heal the shape.
        """
        self.shape = self.geo.RemoveExtraEdges(self.shape, doUnionFaces = False)
    
    def createGroupAll(self, mainShape):
        """Create group from all the shape faces.
        
        :param mainShape:
            Input shape.
        
        :return:
            Created group.
        """
        group = self.geo.CreateGroup(mainShape, self.geo.ShapeType["FACE"])
        
        self.geo.UnionIDs(
            group,
            self.geo.SubShapeAllIDs(mainShape, self.geo.ShapeType["FACE"])
        )
        
        return group
        
    def createGroup(self, mainShape, subShape, name: str, cutShapes: list = None, scaleTransform: float = None):
        """Create group from the sub shape.
        
        :param mainShape:
            Input shape.
        
        :param subShape:
            Input sub shape.
        
        :param name:
            Name of the new group.
        
        :param cutShapes:
            List of shapes for cut from the sub shape.
            
        :param scaleTransform:
            Value of the scale transform regarding to the zero point.
        
        :return:
            Created group.
        """
        group = self.geo.CreateGroup(mainShape, self.geo.ShapeType["FACE"], theName = name)
        
        if cutShapes:
            subShape = self.geo.MakeCutList(subShape, cutShapes)
        
        if scaleTransform:
            subShape = self.geo.MakeScaleTransform(subShape, self.geo.MakeVertex(0, 0, 0), scaleTransform)
        
        self.geo.UnionList(
            group, 
            self.geo.SubShapeAll(
                self.geo.GetInPlace(mainShape, subShape, True), 
                self.geo.ShapeType["FACE"]
            )
        )
        
        return group
    
    def export(
        filename: str,
        deflection: float = 0.001
    ):
        """Export a shape.
        
        Supported formats: step, vtk.
        
        :param filename:
            Name of the file to store the given shape in.
        
        :param deflection:
            vtk: Deflection of the given shape.
        
        :return:
            Output, error messages and returncode
        """
        out, err, returncode = "", "", 0
        ext = os.path.splitext(filename)[1][1: ]
        
        try:
            if ext == "step":
                self.geo.ExportSTEP(self.shape, filename) # theUnit = GEOM.LU_METER)
            
            elif ext == "vtk":
                self.geo.ExportVTK(self.shape, filename, theDeflection = deflection)
            
            else:
                raise NotImplementedError(f"{ ext } is not supported")
            
        except NotImplementedError as e:
            err = e
            returncode = 1
        
        except Exception as e:
            err = e.details.text
            returncode = 1
        
        return out, err, returncode
 
