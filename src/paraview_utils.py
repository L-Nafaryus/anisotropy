from paraview.simple import *

def plotMagnitude():

    rv = CreateRenderView()
    rv.ViewSize = [1920, 1080]
    rv.CameraPosition = [1e-05, 2e-05, 1e-05]
    rv.CameraFocalPoint = [1e-05, 2e-05, 1e-05]


    layout1 = CreateLayout(name='Layout #1')
    layout1.AssignView(0, rv)

    SetActiveView(rv)

    foam = OpenFOAMReader(FileName = "simple.foam")
    foam.CaseType = "Decomposed Case"
    foam.MeshRegions = ["internalMesh"]
    foam.CellArrays = ["U", "p"]

    SetActiveSource(foam)
    display = Show(foam, rv, "UnstructuredGridRepresentation")
    r = Render()
    
    SaveScreenshot("test.png", r)

if __name__ == "__main__":
    plotMagnitude()
