import csv
import numpy as np
from vtk import *
from paraview.simple import *


uGrid = vtkUnstructuredGrid()
numFiles = 3072
numHexahedra = numFiles
numPoints = 8

signal = vtkFloatArray()
signal.SetName("Signal")
signal.SetNumberOfComponents(1)
signal.SetNumberOfTuples(numHexahedra)
detectorIDs = vtkFloatArray()
detectorIDs.SetName("DetectorID")
detectorIDs.SetNumberOfComponents(1)
detectorIDs.SetNumberOfTuples(numHexahedra)

points = vtkPoints()

with open("MultigridData.csv", "r") as csvFile:
	reader = csv.reader(csvFile, delimiter=',')
	
	r = 0
	for row in reader:
		try:
			data = np.array(row, dtype=float)
			if len(data) > 3:
				points.InsertNextPoint(data[0], data[1], data[2])
				signal.SetValue(r/8, data[3])
				detectorIDs.SetValue(r/8, data[4])
				r = r+1
		except ValueError:
			pass

uGrid.SetPoints(points)

for i in xrange(numHexahedra):
	hex = vtkHexahedron()
	
	ids = np.array((0, 1, 3, 2, 4, 5, 7, 6))
	for j in xrange(numPoints):
		id = (i*numPoints)+ids[j]
		hex.GetPointIds().SetId(j, id)

	uGrid.InsertNextCell(hex.GetCellType(), hex.GetPointIds())

uGrid.GetCellData().AddArray(detectorIDs)
uGrid.GetCellData().SetScalars(signal)

print "Printing UnstructuredGrid File"

gw = vtkXMLUnstructuredGridWriter()
gw.SetFileName("MutliGrid.vtu")
gw.SetInputData(uGrid)
gw.Write()
		
### LOAD FILE INTO PARAVIEW ######################################################################
# create a new 'XML Unstructured Grid Reader'
mutliGridvtu = XMLUnstructuredGridReader(FileName=['C:\\Users\\bpe14858\\Desktop\\MutliGrid.vtu'])
mutliGridvtu.CellArrayStatus = ['Signal']

# get active view
renderView1 = GetActiveViewOrCreate('RenderView')
# uncomment following to set a specific view size
# renderView1.ViewSize = [3469, 2145]

# get color transfer function/color map for 'Signal'
signalLUT = GetColorTransferFunction('Signal')
# Apply a preset using its name. Note this may not work as expected when presets have duplicate names.
signalLUT.ApplyPreset('ColdFire', True)

# show data in view
mutliGridvtuDisplay = Show(mutliGridvtu, renderView1)
# trace defaults for the display properties.
mutliGridvtuDisplay.ColorArrayName = ['CELLS', 'Signal']
mutliGridvtuDisplay.LookupTable = signalLUT
mutliGridvtuDisplay.OSPRayScaleArray = 'Signal'
mutliGridvtuDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
mutliGridvtuDisplay.SelectOrientationVectors = 'None'
mutliGridvtuDisplay.ScaleFactor = 0.10015012025833131
mutliGridvtuDisplay.SelectScaleArray = 'Signal'
mutliGridvtuDisplay.GlyphType = 'Arrow'
mutliGridvtuDisplay.ScalarOpacityUnitDistance = 0.06993683163897997
mutliGridvtuDisplay.GaussianRadius = 0.050075060129165655
mutliGridvtuDisplay.SetScaleArray = [None, '']
mutliGridvtuDisplay.ScaleTransferFunction = 'PiecewiseFunction'
mutliGridvtuDisplay.OpacityArray = [None, '']
mutliGridvtuDisplay.OpacityTransferFunction = 'PiecewiseFunction'

# reset view to fit data
renderView1.ResetCamera()

# show color bar/color legend
mutliGridvtuDisplay.SetScalarBarVisibility(renderView1, True)

# get opacity transfer function/opacity map for 'Signal'
signalPWF = GetOpacityTransferFunction('Signal')