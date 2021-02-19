import os, sys

import salome
salome.salome_init()

import geometry, mesh

#alpha = [ 0.1, 0.15, 0.2 ]
build_path = str(sys.argv[1])
coef = float(sys.argv[2])

#for coef in alpha:
print("alpha = {}".format(coef))
print("Building geometry ...")

Pore, bc = geometry.create(coef)
#geometry.geompy.addToStudy(Pore, 'Pore {}'.format(coef))
#geometry.geompy.addToStudyInFather(Pore, bc[0], "INLET")
print("Building mesh ...")

PoreMesh = mesh.create(Pore, bc)
isDone = PoreMesh.Compute()

status = "Succesfully" if isDone else "Mesh is not computed"
print(status)

try:
    filename = os.path.join(build_path, "mesh.unv")
    PoreMesh.ExportUNV(filename)
    pass
except:
    print('ExportUNV() failed. Invalid file name?')

if salome.sg.hasDesktop():
    salome.sg.updateObjBrowser()
