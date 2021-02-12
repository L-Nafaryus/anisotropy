import salome
salome.salome_init()

import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _geometry, _mesh

alpha = [ 0.1, 0.15, 0.2 ]
pore = []

for coef in alpha:
    [geompy, Pore, Segment1_4, Segment1_8] = _geometry.create(coef)
    geompy.addToStudy(Pore, 'Pore {}'.format(coef))
    pore.append(Pore)
    
    print("Geometry for alpha = {}".format(coef))

###

for Pore in pore:
    print("Building mesh for {}".format(Pore.GetName()))

    [smesh, mesh] = _mesh.create(Pore)
    isDone = mesh.Compute()
    
    status = "Succesfully" if isDone else "Mesh is not computed"
    print(status)

#try:
#    dirname = os.path.dirname(__file__)
#    filename = os.path.join(dirname, '../build/mesh.unv')
#    mesh.ExportUNV( filename )
#    pass
#except:
#    print('ExportUNV() failed. Invalid file name?')

if salome.sg.hasDesktop():
    salome.sg.updateObjBrowser()
