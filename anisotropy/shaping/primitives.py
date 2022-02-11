# -*- coding: utf-8 -*-

from __future__ import annotations
from numpy import ndarray

import numpy as np
import netgen.occ as ng_occ

from . import Periodic
from . import utils


def simple(alpha: float, direction: list | ndarray, **kwargs) -> Periodic:
    """Simple periodic structure.

    :param alpha:
        Spheres overlap parameter.
    :param direction:
        Flow direction vector. This parameter affects the geometry type
        and boundary (faces) names.
    :return:
        Periodic object.
    """
    #   base object
    pc = Periodic(
        alpha = alpha,
        gamma = np.pi - 2 * (0.5 * 0.5 * np.pi)
    )
    
    #   additional parameters
    pc.__dict__.update(kwargs)
    pc.L = 2 * pc.r0
    pc.direction = np.asarray(direction)

    #   additional attributes
    pc.cell: ng_occ.Solid = None
    pc.lattice: ng_occ.Solid = None

    #   constants
    zero = ng_occ.Pnt(0, 0, 0)

    #   Lattice
    spheres = [] 

    for zn in range(3):
        z = zn * pc.L

        for yn in range(3):
            y = yn * pc.L

            for xn in range(3):
                x = xn * pc.L

                spheres.append(ng_occ.Sphere(ng_occ.Pnt(x, y, z), pc.radius))

    pc.lattice = np.sum(spheres)

    if pc.filletsEnabled:
        pc.lattice = pc.lattice.Scale(zero, pc.maximize)
        pc.lattice = (
            pc.lattice
            .MakeFillet(pc.lattice.edges, pc.fillets * pc.maximize)
            .Scale(zero, pc.minimize)
        )
    
    #   Inlet face
    if np.all(pc.direction == [1., 0., 0.]):
        length = pc.L * np.sqrt(2)
        width = pc.L * np.sqrt(2)
        height = pc.L

        xl = np.sqrt(length ** 2 * 0.5)
        yw = xl
        zh = height

        vertices = np.array([
            (xl, 0, 0),
            (0, yw, 0),
            (0, yw, zh),
            (xl, 0, zh)
        ])
        extr = width

    elif np.all(pc.direction == [0., 0., 1.]):
        length = pc.L * np.sqrt(2)
        width = pc.L * np.sqrt(2)
        height = pc.L

        xl = np.sqrt(length ** 2 * 0.5)
        yw = xl
        zh = height

        vertices = np.array([
            (0, yw, 0),
            (xl, 0, 0),
            (2 * xl, yw, 0),
            (xl, 2 * yw, 0)
        ])
        extr = height

    elif np.all(pc.direction == [1., 1., 1.]):
        length = pc.L * np.sqrt(2)
        width = pc.L * np.sqrt(2)
        height = pc.L

        xl = -pc.L - pc.L / 6 
        yw = -pc.L - pc.L / 6
        zh = -pc.L / 6

        vertices = np.array([
            (pc.L + xl, pc.L + yw, pc.L + zh),
            (5 * pc.L / 3 + xl, 2 * pc.L / 3 + yw, 2 * pc.L / 3 + zh),
            (2 * pc.L + xl, pc.L + yw, 0 + zh),
            (5 * pc.L / 3 + xl, 5 * pc.L / 3 + yw, -pc.L / 3 + zh),
            (pc.L + xl, 2 * pc.L + yw, 0 + zh),
            (2 * pc.L / 3 + xl, 5 * pc.L / 3 + yw, 2 * pc.L / 3 + zh)
        ])
        extr = pc.L * np.sqrt(3) 

    else:
        raise Exception(f"Direction { pc.direction } is not implemented")
    
    #   Cell
    circuit = ng_occ.Wire([ 
        ng_occ.Segment(ng_occ.Pnt(*v1), ng_occ.Pnt(*v2))
        for v1, v2 in zip(vertices, np.roll(vertices, -1, axis = 0)) 
    ])
    inletface = ng_occ.Face(circuit)
    inletface.name = "inlet"

    vecFlow = utils.normal(inletface)
    pc.cell = inletface.Extrude(extr, ng_occ.Vec(*vecFlow))
    
    #   Boundary faces
    symetryId = 0

    for face in pc.cell.faces:
        fNorm = utils.normal(face)
        fAngle = utils.angle(vecFlow, fNorm)
        
        if fAngle == 0 or fAngle == np.pi:
            if np.all(utils.pos(face.center) == utils.pos(inletface.center)):
                face.name = "inlet"
                
            else:
                face.name = "outlet"

        else:
            face.name = f"symetry{ symetryId }"
            symetryId += 1

    #   Main shape
    pc.shape = pc.cell - pc.lattice

    assert len(pc.shape.solids) == 1, "Expected single solid shape"

    pc.shape = pc.shape.solids[0]

    #   Boundary faces (walls)
    for face in pc.shape.faces:
        if face.name not in ["inlet", "outlet", *[ f"symetry{ n }" for n in range(6) ]]:
            face.name = "wall"

    return pc


def body_centered(alpha: float, direction: list | ndarray, **kwargs) -> Periodic:
    """Body centered periodic structure.

    :param alpha:
        Spheres overlap parameter.
    :param direction:
        Flow direction vector. This parameter affects the geometry type
        and boundary (faces) names.
    :return:
        Periodic object.
    """
    #   base object 
    pc = Periodic(
        alpha = alpha,
        gamma = np.pi - 2 * np.arccos(np.sqrt(2 / 3))
    )

    #   additional parameters
    pc.__dict__.update(kwargs)
    pc.L = 4 / np.sqrt(3) * pc.r0
    pc.direction = np.asarray(direction)

    #   additional attributes
    pc.cell: ng_occ.Solid = None
    pc.lattice: ng_occ.Solid = None

    #   constants   
    zero = ng_occ.Pnt(0, 0, 0)

    #   Lattice
    spheres = [] 

    for zn in range(3):
        z = zn * pc.L
        z2 = z - 0.5 * pc.L

        for yn in range(3):
            y = yn * pc.L
            y2 = y - 0.5 * pc.L

            for xn in range(3):
                x = xn * pc.L
                x2 = x - 0.5 * pc.L

                spheres.append(ng_occ.Sphere(ng_occ.Pnt(x, y, z), pc.radius))
                # shifted
                spheres.append(ng_occ.Sphere(ng_occ.Pnt(x2, y2, z2), pc.radius))

    pc.lattice = np.sum(spheres)

    if pc.filletsEnabled:
        pc.lattice = pc.lattice.Scale(zero, pc.maximize)
        pc.lattice = (
            pc.lattice
            .MakeFillet(pc.lattice.edges, pc.fillets * pc.maximize)
            .Scale(zero, pc.minimize)
        )
    
    #   Inlet face
    if np.all(pc.direction == [1., 0., 0.]):
        # length = 2 * pc.r0
        # width = pc.L / 2
        diag = pc.L * np.sqrt(2)
        height = pc.L

        xl = np.sqrt(diag ** 2 + diag ** 2) * 0.5
        yw = xl
        zh = height

        vertices = np.array([
            (xl, 0, 0),
            (0, yw, 0),
            (0, yw, zh),
            (xl, 0, zh)
        ])
        extr = diag

    elif np.all(pc.direction == [0., 0., 1.]):
        # length = 2 * pc.r0
        # width = pc.L / 2
        diag = pc.L * np.sqrt(2)
        height = pc.L

        xl = np.sqrt(diag ** 2 + diag ** 2) * 0.5
        yw = xl
        zh = height

        vertices = np.array([
            (0, yw, 0),
            (xl, 0, 0),
            (2 * xl, yw, 0),
            (xl, 2 * yw, 0)
        ])
        extr = height

    elif np.all(pc.direction == [1., 1., 1.]):
        # length = 2 * pc.r0
        # width = pc.L / 2
        diag = pc.L * np.sqrt(2)
        height = diag / 3

        xl = -pc.L / 4
        yw = -pc.L / 4
        zh = -pc.L / 4

        vertices = np.array([
            (pc.L / 3 + xl, pc.L / 3 + yw, 4 * pc.L / 3 + zh),
            (pc.L + xl, 0 + yw, pc.L + zh),
            (4 * pc.L / 3 + xl, pc.L / 3 + yw, pc.L / 3 + zh),
            (pc.L + xl, pc.L + yw, 0 + zh),
            (pc.L / 3 + xl, 4 * pc.L / 3 + yw, pc.L / 3 + zh),
            (0 + xl, pc.L + yw, pc.L + zh)
        ])
        extr = pc.L * np.sqrt(3) 

    else:
        raise Exception(f"Direction { pc.direction } is not implemented")

    #   Cell
    circuit = ng_occ.Wire([ 
        ng_occ.Segment(ng_occ.Pnt(*v1), ng_occ.Pnt(*v2)) 
        for v1, v2 in zip(vertices, np.roll(vertices, -1, axis = 0)) 
    ])
    inletface = ng_occ.Face(circuit)
    inletface.name = "inlet"

    vecFlow = utils.normal(inletface)
    pc.cell = inletface.Extrude(extr, ng_occ.Vec(*vecFlow))
    
    #   Boundary faces
    symetryId = 0

    for face in pc.cell.faces:
        fNorm = utils.normal(face)
        fAngle = utils.angle(vecFlow, fNorm)
        
        if fAngle == 0 or fAngle == np.pi:
            if np.all(utils.pos(face.center) == utils.pos(inletface.center)):
                face.name = "inlet"

            else:
                face.name = "outlet"

        else:
            face.name = f"symetry{ symetryId }"
            symetryId += 1

    #   Main shape
    pc.shape = pc.cell - pc.lattice

    assert len(pc.shape.solids) == 1, "Expected single solid shape"

    pc.shape = pc.shape.solids[0]

    #   Boundary faces (walls)
    for face in pc.shape.faces:
        if face.name not in ["inlet", "outlet", *[ f"symetry{ n }" for n in range(6) ]]:
            face.name = "wall"

    return pc


def face_centered(alpha: float, direction: list | ndarray, **kwargs) -> Periodic:
    """Face centered periodic structure.

    :param alpha:
        Spheres overlap parameter.
    :param direction:
        Flow direction vector. This parameter affects the geometry type
        and boundary (faces) names.
    :return:
        Periodic object.
    """
    #   base class
    pc = Periodic(
        alpha = alpha,
        gamma = 2 / 3 * np.pi 
    )

    #   additional parameters
    pc.__dict__.update(kwargs)
    pc.L = pc.r0 * 4 / np.sqrt(2)
    pc.direction = np.asarray(direction)

    #   additional attributes
    pc.cell: ng_occ.Solid = None
    pc.lattice: ng_occ.Solid = None

    #   constants   
    zero = ng_occ.Pnt(0, 0, 0)

    #   Lattice
    spheres = [] 
    x0 = 0  
    x20 = 0  
    z0 = -0.5 * pc.L * (3 - 2)
    z20 = -0.5 * pc.L * (3 - 1)

    for zn in range(3):
        z = z0 + zn * pc.L 
        z2 = z20 + zn * pc.L 

        for yn in range(3):
            y = yn * 2 * pc.r0
            y2 = yn * 2 * pc.r0 + pc.r0

            for xn in range(3):
                x = x0 + xn * 2 * pc.r0
                x2 = x20 + xn * 2 * pc.r0 + pc.r0

                # TODO: fix rotations (arcs intersection -> incorrect boolean operations
                spheres.append(
                    ng_occ.Sphere(ng_occ.Pnt(x, y, z), pc.radius)
                    .Rotate(ng_occ.Axis(ng_occ.Pnt(x, y, z), ng_occ.X), 45)
                    .Rotate(ng_occ.Axis(ng_occ.Pnt(x, y, z), ng_occ.Z), 45)
                )
                # shifted
                spheres.append(
                    ng_occ.Sphere(ng_occ.Pnt(x2, y2, z2), pc.radius)
                    .Rotate(ng_occ.Axis(ng_occ.Pnt(x2, y2, z2), ng_occ.X), 45)
                    .Rotate(ng_occ.Axis(ng_occ.Pnt(x2, y2, z2), ng_occ.Z), 45)
                )

    pc.lattice = (
        np.sum(spheres)
        .Move(ng_occ.Vec(-pc.r0 * 2, -pc.r0 * 2, 0))
        .Rotate(ng_occ.Axis(zero, ng_occ.Z), 45)
    )

    if pc.filletsEnabled:
        pc.lattice = pc.lattice.Scale(zero, pc.maximize)
        pc.lattice = (
            pc.lattice
            .MakeFillet(pc.lattice.edges, pc.fillets * pc.maximize)
            .Scale(zero, pc.minimize)
        )

    #   Inlet face
    if np.all(pc.direction == [1., 0., 0.]):
        length = 2 * pc.r0
        width = pc.L / 2
        # diag = pc.L * np.sqrt(3)
        # height = diag / 3

        xl = np.sqrt(length ** 2 + length ** 2) * 0.5
        yw = xl
        zh = width

        vertices = np.array([
            (0, 0, -zh),
            (-xl, yw, -zh),
            (-xl, yw, zh),
            (0, 0, zh)
        ])
        extr = length

    elif np.all(pc.direction == [0., 0., 1.]):
        length = 2 * pc.r0
        width = pc.L / 2
        # diag = pc.L * np.sqrt(3)
        # height = diag / 3

        xl = np.sqrt(length ** 2 + length ** 2) * 0.5
        yw = xl
        zh = width

        vertices = np.array([
            (0, 0, -zh),
            (xl, yw, -zh),
            (0, 2 * yw, -zh),
            (-xl, yw, -zh)
        ])
        extr = 2 * width

    elif np.all(pc.direction == [1., 1., 1.]):
        length = 2 * pc.r0
        width = pc.L / 2
        # diag = pc.L * np.sqrt(3)
        # height = diag / 3

        xl = -(3 - 2) * pc.L / 3
        yw = -(3 - 2) * pc.L / 3
        zh = -(3 - 2) * pc.L / 3

        vertices = np.array([
            (-2 * width / 3 + xl, -2 * width / 3 + yw, width / 3 + zh),
            (0 + xl, -width + yw, 0 + zh),
            (width / 3 + xl, -2 * width / 3 + yw, -2 * width / 3 + zh),
            (0 + xl, 0 + yw, -width + zh),
            (-2 * width / 3 + xl, width / 3 + yw, -2 * width / 3 + zh),
            (-width + xl, 0 + yw, 0 + zh)
        ])
        extr = np.sqrt(3) * pc.L
        
    else:
        raise Exception(f"Direction { pc.direction } is not implemented")
    
    #   Cell
    circuit = ng_occ.Wire([ 
        ng_occ.Segment(ng_occ.Pnt(*v1), ng_occ.Pnt(*v2)) 
        for v1, v2 in zip(vertices, np.roll(vertices, -1, axis = 0)) 
    ])
    inletface = ng_occ.Face(circuit)
    inletface.name = "inlet"

    vecFlow = utils.normal(inletface)
    pc.cell = inletface.Extrude(extr, ng_occ.Vec(*vecFlow))
    
    #   Boundary faces
    symetryId = 0

    for face in pc.cell.faces:
        fNorm = utils.normal(face)
        fAngle = utils.angle(vecFlow, fNorm)
        
        if fAngle == 0 or fAngle == np.pi:
            if np.all(utils.pos(face.center) == utils.pos(inletface.center)):
                face.name = "inlet"

            else:
                face.name = "outlet"

        else:
            face.name = f"symetry{ symetryId }"
            symetryId += 1

    #   Main shape
    pc.shape = pc.cell - pc.lattice

    assert len(pc.shape.solids) == 1, "Expected single solid shape"

    pc.shape = pc.shape.solids[0]

    #   Boundary faces (walls)
    for face in pc.shape.faces:
        if face.name not in ["inlet", "outlet", *[ f"symetry{ n }" for n in range(6) ]]:
            face.name = "wall"

    return pc
