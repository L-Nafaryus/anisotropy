#!/usr/bin/env python
# -*- coding: utf-8 -*-

from salome.smesh import smeshBuilder

smesh = smeshBuilder.New()

ALGOS = [
    smeshBuilder.NETGEN_1D2D3D,
    smeshBuilder.NETGEN_3D, smeshBuilder.NETGEN_1D2D,
    smeshBuilder.NETGEN_2D,
    smeshBuilder.MEFISTO, # only 2d
    smeshBuilder.REGULAR, smeshBuilder.COMPOSITE
]

mesh = smesh.Mesh(SHAPE)

algo = mesh.Tetrahedron(algo = ALGO)

