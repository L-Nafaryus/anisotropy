import os, sys
#print(os.getcwd())
#sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import salome
salome.salome_init()

import geometry, mesh

#alpha = [ 0.1, 0.15, 0.2 ]
coef = float(sys.argv[1])

#for coef in alpha:
print("alpha = {}".format(coef))
print("Building geometry ...")

Pore, bc = geometry.create(coef)
geometry.geompy.addToStudy(Pore, 'Pore {}'.format(coef))
        
print("Building mesh ...")

PoreMesh = mesh.create(Pore, bc)
isDone = PoreMesh.Compute()

status = "Succesfully" if isDone else "Mesh is not computed"
print(status)

#try:
#    dirname = os.path.dirname(__file__)
#    filename = os.path.join(dirname, '../build/mesh.unv')
#    PoreMesh.ExportUNV( filename )
#    pass
#except:
#    print('ExportUNV() failed. Invalid file name?')

if salome.sg.hasDesktop():
    salome.sg.updateObjBrowser()
