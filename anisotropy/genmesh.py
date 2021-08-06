###
#   This file executes inside salome environment
#
#   salome starts at user home directory
##
import os, sys
import math
import logging
import salome
import click

@click.command()
@click.argument("root")
@click.argument("name")
@click.argument("direction")
@click.argument("theta", type = click.FLOAT)
def genmesh(root, name, direction, theta):
    print(root)
    print(name)
    print(direction)
    print(theta)
    ###
    #   Args
    ##
    direction = list(map(lambda num: float(num), direction[1:-1].split(",")))


    ###
    #   Modules
    ##
    sys.path.extend([
        root,
        os.path.join(root, "env/lib/python3.9/site-packages")
    ])

    from anisotropy import (
        Anisotropy,
        logger,
        Simple,
        BodyCentered,
        FaceCentered
    )

    import salomepl

    ###
    #   Model
    ##
    model = Anisotropy()
    model.setupDB()
    model.loadDB(name, direction, theta)
    model.evalParams()

    p = model.params


    ###
    #   Entry
    ##
    logger.info("\n".join([
        "genmesh:",
        f"structure type:\t{ p['structure']['type'] }",
        f"coefficient:\t{ p['structure']['theta'] }",
        f"fillet:\t{ p['structure']['fillets'] }",
        f"flow direction:\t{ p['structure']['direction'] }"
    ]))

    salome.salome_init()


    ###
    #   Shape
    ##
    geompy = salomepl.geometry.getGeom()
    structure = dict(
        simple = Simple,
        bodyCentered = BodyCentered,
        faceCentered = FaceCentered
    )[p["structure"]["type"]]
    shape, groups = structure(**p["structure"]).build()

    [length, surfaceArea, volume] = geompy.BasicProperties(shape, theTolerance = 1e-06)

    logger.info("\n".join([
        "shape:",
        f"edges length:\t{ length }",
        f"surface area:\t{ surfaceArea }",
        f"volume:\t{ volume }"
    ]))


    ###
    #   Mesh
    ##
    mp = p["mesh"]

    lengths = [
        geompy.BasicProperties(edge)[0] for edge in geompy.SubShapeAll(shape, geompy.ShapeType["EDGE"]) 
    ]
    meanSize = sum(lengths) / len(lengths)
    mp["maxSize"] = meanSize
    mp["minSize"] = meanSize * 1e-1
    mp["chordalError"] = mp["maxSize"] / 2

    faces = []
    for group in groups:
        if group.GetName() in mp["facesToIgnore"]:
            faces.append(group)


    mesh = salomepl.mesh.Mesh(shape)
    mesh.Tetrahedron(**mp)

    if mp["viscousLayers"]:
        mesh.ViscousLayers(**mp, faces = faces)

    smp = p["submesh"]

    for submesh in smp:
        for group in groups:
            if submesh["name"] == group.GetName():
                subshape = group

                submesh["maxSize"] = meanSize * 1e-1
                submesh["minSize"] = meanSize * 1e-3
                submesh["chordalError"] = submesh["minSize"] * 1e+1

                mesh.Triangle(subshape, **submesh)


    model.updateDB()
    returncode, errors = mesh.compute()

    if not returncode:
        # TODO: MeshResult
        pass

    else:
        logger.error(errors)


    mesh.removePyramids()
    mesh.assignGroups()

    casePath = model.getCasePath()
    os.makedirs(casePath, exist_ok = True)
    mesh.exportUNV(os.path.join(casePath, "mesh.unv"))

    meshStats = mesh.stats()
    p["meshresults"] = dict(
        #mesh_id = p["mesh"]["mesh_id"],
        surfaceArea = surfaceArea,
        volume = volume,
        **meshStats
    )
    model.updateDB()

    logger.info("mesh stats:\n{}".format(
        "\n".join(map(lambda v: f"{ v[0] }:\t{ v[1] }", meshStats.items()))
    ))

    salome.salome_close()

genmesh()
