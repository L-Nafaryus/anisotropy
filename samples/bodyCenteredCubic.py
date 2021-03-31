import sys 
import salome

salome.salome_init()

import GEOM
from salome.geom import geomBuilder
import math
import SALOMEDS

geompy = geomBuilder.New()

def bodyCenteredCubic(alpha):
    O = geompy.MakeVertex(0, 0, 0)
    OX = geompy.MakeVectorDXDYDZ(1, 0, 0)
    OY = geompy.MakeVectorDXDYDZ(0, 1, 0)
    OZ = geompy.MakeVectorDXDYDZ(0, 0, 1)
    V_1 = geompy.MakeVectorDXDYDZ(1, 1, 0)
    V_2 = geompy.MakeVectorDXDYDZ(1, -1, 0)

    L = 1.0
    r0 = L*math.sqrt(3)/4
    d1 = L*math.sqrt(2)
    Pi_4 = 45*math.pi/180.0
    n = 3

    sk = geompy.Sketcher3D()
    sk.addPointsAbsolute(0, 0, 2*L)                                                 # Vertex_1 of Rombus
    sk.addPointsAbsolute(L, 0, L)                                                   # Vertex_2 of Rombus
    sk.addPointsAbsolute(L, L, 0)                                                   # Vertex_3 of Rombus
    sk.addPointsAbsolute(0, L, L)                                                   # Vertex_4 of Rombus
    sk.addPointsAbsolute(0, 0, 2*L)                                                 # Vertex_1 of Rombus
    a3D_Sketcher_1 = sk.wire()
    Face_1 = geompy.MakeFaceWires([a3D_Sketcher_1], 1)
    Extrusion_1 = geompy.MakePrismDXDYDZ(Face_1, L/2, L/2, L/2)

    sk2 = geompy.Sketcher3D()
    sk2.addPointsAbsolute(L/3, L/3, 4*L/3)                                          # Vertex_1 of Triangle
    sk2.addPointsAbsolute(L, 0, L)                                                  # Vertex_2 of Triangle
    sk2.addPointsAbsolute(2*L/3, 2*L/3, 2*L/3)                                      # Vertex_3 of Triangle
    sk2.addPointsAbsolute(L/3, L/3, 4*L/3)                                          # Vertex_1 of Triangle
    a3D_Sketcher_2 = sk2.wire()
    Face_2 = geompy.MakeFaceWires([a3D_Sketcher_2], 1)
    Extrusion_2 = geompy.MakePrismDXDYDZ(Face_2, L/2, L/2, L/2)

    sk3 = geompy.Sketcher3D()
    sk3.addPointsAbsolute(L/3, L/3, 4*L/3)                                          # Vertex_1 of Hexagon
    sk3.addPointsAbsolute(L, 0, L)                                                  # Vertex_2 of Hexagon
    sk3.addPointsAbsolute(4*L/3, L/3, L/3)                                          # Vertex_3 of Hexagon
    #sk3.addPointsAbsolute(2*L/3, 2*L/3, 2*L/3)                                     # Vertex_3 of Hexagon
    sk3.addPointsAbsolute(L, L, 0)                                                  # Vertex_4 of Hexagon
    sk3.addPointsAbsolute(L/3, 4*L/3, L/3)                                          # Vertex_5 of Hexagon
    sk3.addPointsAbsolute(0, L, L)                                                  # Vertex_6 of Hexagon
    sk3.addPointsAbsolute(L/3, L/3, 4*L/3)                                          # Vertex_1 of Hexagon
    a3D_Sketcher_3 = sk3.wire()
    Face_3 = geompy.MakeFaceWires([a3D_Sketcher_3], 1)
    Extrusion_3 = geompy.MakePrismDXDYDZ(Face_3, L/2, L/2, L/2)

    a3D_Sketcher_4 = geompy.MakeTranslation(a3D_Sketcher_3, -L/4, -L/4, -L/4)
    Face_4 = geompy.MakeFaceWires([a3D_Sketcher_4], 1)
    #Extrusion_4 = geompy.MakePrismDXDYDZ(Face_4, (n-1.5)*L, (n-1.5)*L, (n-1.5)*L)   # Extrusion_3Direction
    Vector_1 = geompy.MakeVectorDXDYDZ(1, 1, 1)
    #Extrusion_4 = geompy.MakePrismVecH(Face_4, Vector_1, 4*(n-1.5)*r0)              # Extrusion_3Direction
    Extrusion_4 = geompy.MakePrismVecH(Face_4, Vector_1, 4*(n-2.0)*r0)              # Extrusion_3Direction

    Box_1 = geompy.MakeBoxDXDYDZ(d1, d1, L)
    Rotation_1 = geompy.MakeRotation(Box_1, OZ, Pi_4)
    Translation_1 = geompy.MakeTranslation(Rotation_1, L, 0, 0)
    Translation_2 = geompy.MakeTranslation(Translation_1, 0, 0, L/4)

    Box_2 = geompy.MakeBoxDXDYDZ(d1/2, d1/2, L)
    Rotation_2 = geompy.MakeRotation(Box_2, OZ, Pi_4)
    Translation_3 = geompy.MakeTranslation(Rotation_2, L, 0, L/4)

    Box_3 = geompy.MakeBoxDXDYDZ(d1/2, d1/2, L/2)
    Rotation_3 = geompy.MakeRotation(Box_3, OZ, Pi_4)
    Translation_4 = geompy.MakeTranslation(Rotation_3, L, 0, L/4)

    geompy.addToStudy( O, 'O' )
    geompy.addToStudy( OX, 'OX' )
    geompy.addToStudy( OY, 'OY' )
    geompy.addToStudy( OZ, 'OZ' )
    geompy.addToStudy( V_1, 'V_1' )
    geompy.addToStudy( V_2, 'V_2' )
    geompy.addToStudy( Box_1, 'Box_1' )
    geompy.addToStudy( Rotation_1, 'Rotation_1' )
    geompy.addToStudy( Translation_1, 'Translation_1' )
    geompy.addToStudy( Translation_2, 'Translation_2' )
    geompy.addToStudy( Box_2, 'Box_2' )
    geompy.addToStudy( Rotation_2, 'Rotation_2' )
    geompy.addToStudy( Translation_3, 'Translation_3' )
    geompy.addToStudy( Rotation_3, 'Rotation_3' )
    geompy.addToStudy( Translation_4, 'Translation_4' )

    #geompy.addToStudy( a3D_Sketcher_1, 'a3D_Sketcher_1' )
    #geompy.addToStudy( Face_1, 'Face_1' )
    geompy.addToStudy( Extrusion_1, 'Extrusion_1' )
    geompy.addToStudy( a3D_Sketcher_2, 'a3D_Sketcher_2' )
    #geompy.addToStudy( Face_2, 'Face_2' )
    geompy.addToStudy( Extrusion_2, 'Extrusion_2' )
    geompy.addToStudy( a3D_Sketcher_3, 'a3D_Sketcher_3' )
    #geompy.addToStudy( Face_3, 'Face_3' )
    #geompy.addToStudy( Extrusion_3, 'Extrusion_3' )
    geompy.addToStudy( a3D_Sketcher_4, 'a3D_Sketcher_4' )
    #geompy.addToStudy( Face_4, 'Face_4' )
    geompy.addToStudy( Extrusion_4, 'Extrusion_4' )
     

    Radius = r0/(1-alpha)
    Sphere_1 = geompy.MakeSphereR(Radius)
    Down = geompy.MakeMultiTranslation2D(Sphere_1, OX, L, n, OY, L, n)
    Up = geompy.MakeTranslation(Down, 0, 0, (n-1)*L)
    Up_Down = geompy.MakeMultiTranslation1D(Down, OZ, L, n)
    Cut_1a = geompy.MakeCutList(Translation_1, [Up_Down])
    Cut_1b = geompy.MakeCutList(Translation_2, [Up_Down])
    Cut_2a = geompy.MakeCutList(Translation_3, [Up_Down])
    Cut_2b = geompy.MakeCutList(Translation_4, [Up_Down])
    Cut_3a = geompy.MakeCutList(Extrusion_1, [Up_Down])
    Cut_3b = geompy.MakeCutList(Extrusion_2, [Up_Down])
    Cut_3c = geompy.MakeCutList(Extrusion_4, [Up_Down])
    Middle = geompy.MakeTranslation(Up_Down, L/2, L/2, L/2)
    Pore_1a = geompy.MakeCutList(Cut_1a, [Middle])
    Pore_1b = geompy.MakeCutList(Cut_1b, [Middle])
    Pore_2a = geompy.MakeCutList(Cut_2a, [Middle])
    Pore_2b = geompy.MakeCutList(Cut_2b, [Middle])
    Pore_3a = geompy.MakeCutList(Cut_3a, [Middle])
    Pore_3b = geompy.MakeCutList(Cut_3b, [Middle])
    Pore_3c = geompy.MakeCutList(Cut_3c, [Middle])

    geompy.addToStudy( Sphere_1, 'Sphere_' )
    geompy.addToStudy( Down, 'Down_' )
    geompy.addToStudy( Up, 'Up_' )
    geompy.addToStudy( Up_Down, 'Up_Down_' )
    geompy.addToStudy( Cut_1a, 'Cut_1a_' )
    geompy.addToStudy( Cut_1b, 'Cut_1b_' )
    geompy.addToStudy( Middle, 'Middle_' )
    geompy.addToStudy( Pore_1a, 'Pore_1a_' )
    geompy.addToStudy( Pore_1b, 'Pore_1b_' )
    geompy.addToStudy( Pore_2a, 'Pore_2a_' )
    geompy.addToStudy( Pore_2b, 'Pore_2b_' )
    geompy.addToStudy( Pore_3a, 'Pore_3a_' )
    geompy.addToStudy( Pore_3b, 'Pore_3b_' )
    geompy.addToStudy( Pore_3c, 'Pore_3c_' )

    if salome.sg.hasDesktop():
        salome.sg.updateObjBrowser()

    # Preparation
    grains = geompy.ExtractShapes(Up_Down, geompy.ShapeType["SOLID"], True)
    grains += geompy.ExtractShapes(Middle, geompy.ShapeType["SOLID"], True)
    grains = geompy.MakeFuseList(grains, False, False)

    R = r0 / (1 - alpha)
    C1 = 0.8
    C2 = 0.4
    alpha1 = 0.01
    alpha2 = 0.13
    
    Cf = C1 + (C2 - C1) / (alpha2 - alpha1) * (alpha - alpha1)
    R_fillet = Cf * (r0 * math.sqrt(2) - R)
    
    grains = geompy.MakeFilletAll(grains, R_fillet)
    geometry1 = geompy.MakeCutList(Pore_1a, [grains], True)
    geometry2 = geompy.MakeCutList(Pore_3c, [grains], True)

    return grains, Pore_1a, Pore_3c
