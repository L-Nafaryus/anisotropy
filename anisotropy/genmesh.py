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
        simple,
        bodyCentered,
        faceCentered
    )

    import salomepl

    ###
    #   Model
    ##
    model = Anisotropy()
    model.updateFromDB()

    p = model.getParams(name, direction, theta)


    ###
    #   Entry
    ##
    logger.info("\n".join([
        "genmesh:",
        f"structure type:\t{ p['name'] }",
        f"coefficient:\t{ p['geometry']['theta'] }",
        f"fillet:\t{ p['geometry']['fillets'] }",
        f"flow direction:\t{ p['geometry']['direction'] }"
    ]))

    salome.salome_init()


    ###
    #   Shape
    ##
    geompy = salomepl.geometry.getGeom()
    structure = locals().get(p["name"])
    shape, groups = structure(**p["geometry"])

    [length, surfaceArea, volume] = geompy.BasicProperties(shape, theTolerance = 1e-06)

    logger.info("\n".join([
        "shape:"
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
        if group.GetName() in mconfig["facesToIgnore"]:
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

    mesh.exportUNV(os.path.join(p["path"], "mesh.unv"))

    meshStats = mesh.stats()
    p["meshResult"] = dict(
        mesh_id = p["mesh"]["id"],
        surfaceArea = surfaceArea,
        volume = volume,
        **meshStats
    )
    model.updateDB()

    statstr = "\n".join(map(lambda k, v: f"{ k }:\t{ v }", meshStats))
    logger.info(f"mesh stats:\n{ statsstr }")

    salome.salome_close()

genmesh()
