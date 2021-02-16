import os, sys
print(os.getcwd())
#sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import salome
salome.salome_init()

import geometry, mesh

alpha = [ 0.1, 0.15, 0.2 ]
pore = []

for coef in alpha:
    # TODO: Manage bc, not used
    Pore, bc = geometry.create(coef)
    geometry.geompy.addToStudy(Pore, 'Pore {}'.format(coef))
    
    pore.append(Pore)
    
    print("Geometry for alpha = {}".format(coef))

###

for Pore in pore:
    print("Building mesh for {}".format(Pore.GetName()))

    mesh_ = mesh.create(Pore, bc)
    #isDone = mesh_.Compute()
    
    #status = "Succesfully" if isDone else "Mesh is not computed"
    #print(status)

#try:
#    dirname = os.path.dirname(__file__)
#    filename = os.path.join(dirname, '../build/mesh.unv')
#    mesh.ExportUNV( filename )
#    pass
#except:
#    print('ExportUNV() failed. Invalid file name?')

if salome.sg.hasDesktop():
    salome.sg.updateObjBrowser()
