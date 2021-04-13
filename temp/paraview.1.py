# state file generated using paraview version 5.8.1

# ----------------------------------------------------------------
# setup views used in the visualization
# ----------------------------------------------------------------

# trace generated using paraview version 5.8.1
#
# To ensure correct image size when batch processing, please search 
# for and uncomment the line `# renderView*.ViewSize = [*,*]`

#### import the simple module from the paraview
from paraview.simple import *
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

# Create a new 'Render View'
renderView1 = CreateView('RenderView')
renderView1.ViewSize = [1518, 833]
renderView1.AxesGrid = 'GridAxes3DActor'
renderView1.CenterOfRotation = [1.9999999835818016e-05, 2.0000001541120582e-05, 9.999999747378752e-06]
renderView1.StereoType = 'Crystal Eyes'
renderView1.CameraPosition = [1.9999999835818016e-05, 2.0000001541120582e-05, 0.0001558028029300748]
renderView1.CameraFocalPoint = [1.9999999835818016e-05, 2.0000001541120582e-05, 9.999999747378752e-06]
renderView1.CameraFocalDisk = 1.0
renderView1.CameraParallelScale = 3.773654229301616e-05
renderView1.CameraParallelProjection = 1

# init the 'GridAxes3DActor' selected for 'AxesGrid'
renderView1.AxesGrid.Visibility = 1

SetActiveView(None)

# ----------------------------------------------------------------
# setup view layouts
# ----------------------------------------------------------------

# create new layout object 'Layout #1'
layout1 = CreateLayout(name='Layout #1')
layout1.AssignView(0, renderView1)

# ----------------------------------------------------------------
# restore active view
SetActiveView(renderView1)
# ----------------------------------------------------------------

# ----------------------------------------------------------------
# setup the data processing pipelines
# ----------------------------------------------------------------

# create a new 'OpenFOAMReader'
simplefoam = OpenFOAMReader(FileName='/home/nafaryus/projects/anisotrope-cube/build/simple/coeff-0.01/direction-100/simple.foam')
simplefoam.CaseType = 'Decomposed Case'
simplefoam.MeshRegions = ['internalMesh']
simplefoam.CellArrays = ['U', 'p']

# create a new 'Clip'
clip1 = Clip(Input=simplefoam)
clip1.ClipType = 'Plane'
clip1.HyperTreeGridClipper = 'Plane'
clip1.Scalars = ['POINTS', 'p']
clip1.Value = 0.000504692076901847

# init the 'Plane' selected for 'ClipType'
clip1.ClipType.Origin = [1.999999909685357e-05, 2.0000001029529813e-05, 9.999999747378752e-06]
clip1.ClipType.Normal = [0.0, 0.0, 1.0]

# init the 'Plane' selected for 'HyperTreeGridClipper'
clip1.HyperTreeGridClipper.Origin = [1.999999909685357e-05, 2.0000001029529813e-05, 9.999999747378752e-06]

# ----------------------------------------------------------------
# setup the visualization in view 'renderView1'
# ----------------------------------------------------------------

# show data from simplefoam
simplefoamDisplay = Show(simplefoam, renderView1, 'UnstructuredGridRepresentation')

# get color transfer function/color map for 'p'
pLUT = GetColorTransferFunction('p')
pLUT.RGBPoints = [-2.29675952141406e-05, 0.231373, 0.298039, 0.752941, 0.000504692076901847, 0.865003, 0.865003, 0.865003, 0.0010323517490178347, 0.705882, 0.0156863, 0.14902]
pLUT.ScalarRangeInitialized = 1.0

# get opacity transfer function/opacity map for 'p'
pPWF = GetOpacityTransferFunction('p')
pPWF.Points = [-2.29675952141406e-05, 0.0, 0.5, 0.0, 0.0010323517490178347, 1.0, 0.5, 0.0]
pPWF.ScalarRangeInitialized = 1

# trace defaults for the display properties.
simplefoamDisplay.Representation = 'Surface'
simplefoamDisplay.ColorArrayName = ['POINTS', 'p']
simplefoamDisplay.LookupTable = pLUT
simplefoamDisplay.OSPRayScaleArray = 'p'
simplefoamDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
simplefoamDisplay.SelectOrientationVectors = 'U'
simplefoamDisplay.ScaleFactor = 3.740525119155791e-06
simplefoamDisplay.SelectScaleArray = 'p'
simplefoamDisplay.GlyphType = 'Arrow'
simplefoamDisplay.GlyphTableIndexArray = 'p'
simplefoamDisplay.GaussianRadius = 1.8702625595778954e-07
simplefoamDisplay.SetScaleArray = ['POINTS', 'p']
simplefoamDisplay.ScaleTransferFunction = 'PiecewiseFunction'
simplefoamDisplay.OpacityArray = ['POINTS', 'p']
simplefoamDisplay.OpacityTransferFunction = 'PiecewiseFunction'
simplefoamDisplay.DataAxesGrid = 'GridAxesRepresentation'
simplefoamDisplay.PolarAxes = 'PolarAxesRepresentation'
simplefoamDisplay.ScalarOpacityFunction = pPWF
simplefoamDisplay.ScalarOpacityUnitDistance = 9.756969141785036e-07
simplefoamDisplay.ExtractedBlockIndex = 1

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
simplefoamDisplay.ScaleTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 0.0010000000474974513, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
simplefoamDisplay.OpacityTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 0.0010000000474974513, 1.0, 0.5, 0.0]

# show data from clip1
clip1Display = Show(clip1, renderView1, 'UnstructuredGridRepresentation')

# get color transfer function/color map for 'U'
uLUT = GetColorTransferFunction('U')
uLUT.RGBPoints = [0.0, 0.231373, 0.298039, 0.752941, 0.00010124565929526629, 0.865003, 0.865003, 0.865003, 0.00020249131859053257, 0.705882, 0.0156863, 0.14902]
uLUT.ScalarRangeInitialized = 1.0

# get opacity transfer function/opacity map for 'U'
uPWF = GetOpacityTransferFunction('U')
uPWF.Points = [0.0, 0.0, 0.5, 0.0, 0.00020249131859053257, 1.0, 0.5, 0.0]
uPWF.ScalarRangeInitialized = 1

# trace defaults for the display properties.
clip1Display.Representation = 'Surface'
clip1Display.ColorArrayName = ['POINTS', 'U']
clip1Display.LookupTable = uLUT
clip1Display.OSPRayScaleArray = 'p'
clip1Display.OSPRayScaleFunction = 'PiecewiseFunction'
clip1Display.SelectOrientationVectors = 'U'
clip1Display.ScaleFactor = 3.740524778095278e-06
clip1Display.SelectScaleArray = 'p'
clip1Display.GlyphType = 'Arrow'
clip1Display.GlyphTableIndexArray = 'p'
clip1Display.GaussianRadius = 1.870262389047639e-07
clip1Display.SetScaleArray = ['POINTS', 'p']
clip1Display.ScaleTransferFunction = 'PiecewiseFunction'
clip1Display.OpacityArray = ['POINTS', 'p']
clip1Display.OpacityTransferFunction = 'PiecewiseFunction'
clip1Display.DataAxesGrid = 'GridAxesRepresentation'
clip1Display.PolarAxes = 'PolarAxesRepresentation'
clip1Display.ScalarOpacityFunction = uPWF
clip1Display.ScalarOpacityUnitDistance = 1.1332065866368908e-06
clip1Display.ExtractedBlockIndex = 1

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
clip1Display.ScaleTransferFunction.Points = [-2.29675952141406e-05, 0.0, 0.5, 0.0, 0.0010323517490178347, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
clip1Display.OpacityTransferFunction.Points = [-2.29675952141406e-05, 0.0, 0.5, 0.0, 0.0010323517490178347, 1.0, 0.5, 0.0]

# setup the color legend parameters for each legend in this view

# get color legend/bar for pLUT in view renderView1
pLUTColorBar = GetScalarBar(pLUT, renderView1)
pLUTColorBar.Title = 'p'
pLUTColorBar.ComponentTitle = ''

# set color bar visibility
pLUTColorBar.Visibility = 0

# get color legend/bar for uLUT in view renderView1
uLUTColorBar = GetScalarBar(uLUT, renderView1)
uLUTColorBar.Title = 'U'
uLUTColorBar.ComponentTitle = 'Magnitude'

# set color bar visibility
uLUTColorBar.Visibility = 1

# hide data in view
Hide(simplefoam, renderView1)

# show color legend
clip1Display.SetScalarBarVisibility(renderView1, True)

# ----------------------------------------------------------------
# setup color maps and opacity mapes used in the visualization
# note: the Get..() functions create a new object, if needed
# ----------------------------------------------------------------

# ----------------------------------------------------------------
# finally, restore active source
SetActiveSource(clip1Display)
# ----------------------------------------------------------------
SaveScreenshot("test.png", renderView1)
