import sys 
import salome

salome.salome_init()

import GEOM
from salome.geom import geomBuilder
import math
import SALOMEDS

geompy = geomBuilder.New()

def faceCenteredCubic(alpha):
    O = geompy.MakeVertex(0, 0, 0)
    OX = geompy.MakeVectorDXDYDZ(1, 0, 0)
    OY = geompy.MakeVectorDXDYDZ(0, 1, 0)
    OZ = geompy.MakeVectorDXDYDZ(0, 0, 1)
    V = geompy.MakeVectorDXDYDZ(1, 1, 1)
    V_1 = geompy.MakeVectorDXDYDZ(1, 1, 0)
    V_2 = geompy.MakeVectorDXDYDZ(1, -1, 0)

    L = 1.0
    r0 = L*math.sqrt(2)/4
    a=2*r0
    b=L/2
    #c=b/2
    h=L/math.sqrt(3)
    Pi_4 = 45*math.pi/180.0

    Vertex_1 = geompy.MakeVertex(-a, -a, -b)
    Vertex_2 = geompy.MakeVertex(a, a, b)
    Vertex_3 = geompy.MakeVertex(-1, 0, -b)                             # Center of Sphere_1
    Vertex_4 = geompy.MakeVertex(-b, 0, -0)
    Vertex_5 = geompy.MakeVertex(0, 0, -b)

    sk = geompy.Sketcher3D()                                            #            Rombus
    sk.addPointsAbsolute(-b, -b, b)                                     #Vertex_1 of Rombus
    sk.addPointsAbsolute(0, -b, 0)                                      #Vertex_2 of Rombus
    sk.addPointsAbsolute(0, 0, -b)                                      #Vertex_3 of Rombus
    sk.addPointsAbsolute(-b, 0, 0)                                      #Vertex_4 of Rombus
    sk.addPointsAbsolute(-b, -b, b)                                     #Vertex_1 of Rombus
    a3D_Sketcher_1 = sk.wire()
    Face_1 = geompy.MakeFaceWires([a3D_Sketcher_1], 1)
    Face_1_Up = geompy.MakeTranslation(Face_1, b, b, 0)
    Rhombohedron = geompy.MakeHexa2Faces(Face_1, Face_1_Up)

    sk_2 = geompy.Sketcher3D()                                          #            Triangle
    sk_2.addPointsAbsolute(-2*b/3, -2*b/3, b/3)                         #Vertex_1 of Triangle
    sk_2.addPointsAbsolute(0, -b, 0)                                    #Vertex_2 of Triangle
    sk_2.addPointsAbsolute(-b/3, -b/3, -b/3)                            #Vertex_3 of Triangle
    sk_2.addPointsAbsolute(-2*b/3, -2*b/3, b/3)                         #Vertex_1 of Triangle
    a3D_Sketcher_2 = sk_2.wire() 
    Face_2 = geompy.MakeFaceWires([a3D_Sketcher_2], 1)
    Extrusion_2 = geompy.MakePrismVecH(Face_2, V, h)

    sk_3 = geompy.Sketcher3D()                                          #            Hexagon
    sk_3.addPointsAbsolute(-2*b/3, -2*b/3, b/3)                         #Vertex_1 of Hexagon
    sk_3.addPointsAbsolute(0, -b, 0)                                    #Vertex_2 of Hexagon
    sk_3.addPointsAbsolute(b/3, -2*b/3, -2*b/3)                         #Vertex_3 of Hexagon
    sk_3.addPointsAbsolute(0, 0, -b)                                    #Vertex_4 of Hexagon
    sk_3.addPointsAbsolute(-2*b/3, b/3, -2*b/3)                         #Vertex_5 of Hexagon
    sk_3.addPointsAbsolute(-b, 0, 0)                                    #Vertex_6 of Hexagon
    sk_3.addPointsAbsolute(-2*b/3, -2*b/3, b/3)                         #Vertex_1 of Hexagon
    a3D_Sketcher_3 = sk_3.wire() 
    Face_3 = geompy.MakeFaceWires([a3D_Sketcher_3], 1)
    Extrusion_3 = geompy.MakePrismVecH(Face_3, V, h)

    Box_1 = geompy.MakeBoxTwoPnt(Vertex_1, Vertex_2)
    Rotation_1 = geompy.MakeRotation(Box_1, OZ, Pi_4)
    Box_2 = geompy.MakeBoxTwoPnt(Vertex_5, Vertex_2)
    Rotation_2 = geompy.MakeRotation(Box_2, OZ, Pi_4)

    geompy.addToStudy( O, 'O' )
    geompy.addToStudy( OX, 'OX' )
    geompy.addToStudy( OY, 'OY' )
    geompy.addToStudy( OZ, 'OZ' )
    geompy.addToStudy( V_1, 'V_1' )
    geompy.addToStudy( V_2, 'V_2' )
    geompy.addToStudy( Box_1, 'Box_1' )
    geompy.addToStudy( Rotation_1, 'Rotation_1' )
    geompy.addToStudy( Box_2, 'Box_2' )
    geompy.addToStudy( Rotation_2, 'Rotation_2_' )

    geompy.addToStudy( a3D_Sketcher_1, 'a3D_Sketcher_1' )
    geompy.addToStudy( Face_1, 'Face_1' )
    geompy.addToStudy( Face_1_Up, 'Face_1_Up' )
    geompy.addToStudy( Rhombohedron, 'Rhombohedron' )
    geompy.addToStudy( a3D_Sketcher_2, 'a3D_Sketcher_2' )
    geompy.addToStudy( Face_2, 'Face_2' )
    geompy.addToStudy( Extrusion_2, 'Extrusion_2' )
    geompy.addToStudy( a3D_Sketcher_3, 'a3D_Sketcher_3' )
    geompy.addToStudy( Face_3, 'Face_3' )
    geompy.addToStudy( Extrusion_3, 'Extrusion_3' )
     

    Radius = r0/(1-alpha)
    Sphere_1 = geompy.MakeSpherePntR(Vertex_3, Radius)
    Down = geompy.MakeMultiTranslation2D(Sphere_1, V_1, a, 3, V_2, a, 3)
    Up_Down = geompy.MakeMultiTranslation1D(Down, OZ, 1, 2)
    Cut_1 = geompy.MakeCutList(Rotation_1, [Up_Down], True)

    Sphere_2 = geompy.MakeSpherePntR(Vertex_4, Radius)
    Middle = geompy.MakeMultiTranslation2D(Sphere_2, V_1, a, 2, V_2, a, 2)
    Cut_2 = geompy.MakeCutList(Cut_1, [Middle], True)

    Common = geompy.MakeCommonList([Cut_2, Rotation_2], True)
    Pore_3 = geompy.MakeCommonList([Rhombohedron, Cut_2], True)

    Cut_3 = geompy.MakeCutList(Extrusion_2, [Up_Down], True)
    Cut_4 = geompy.MakeCutList(Cut_3, [Middle], True)
    
    Cut_5 = geompy.MakeCutList(Extrusion_3, [Up_Down], True)
    Cut_6 = geompy.MakeCutList(Cut_5, [Middle], True)

    #geompy.addToStudy( Sphere_1, 'Sphere_' )
    geompy.addToStudy( Down, 'Down_' )
    geompy.addToStudy( Up_Down, 'Up_Down_' )
    geompy.addToStudy( Cut_1, 'Cut_1_' )
    geompy.addToStudy( Middle, 'Middle_' )
    geompy.addToStudy( Cut_2, 'Pore_' )
    geompy.addToStudy( Common, 'Pore_2_' )
    geompy.addToStudy( Pore_3, 'Pore_3_' )
    geompy.addToStudy( Cut_4, 'Pore_3a_' )
    geompy.addToStudy( Cut_6, 'Pore_3b_' )

    if salome.sg.hasDesktop():
        salome.sg.updateObjBrowser()
    
    # Preparation
    grains = geompy.ExtractShapes(Up_Down, geompy.ShapeType["SOLID"], True)
    grains += geompy.ExtractShapes(Middle, geompy.ShapeType["SOLID"], True)

    grains = geompy.MakeFuseList(grains, False, False)

    return grains, Common, Pore_3
