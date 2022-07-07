import os
import sys
from lxml import etree as le
import numpy as np
import argparse
sys.path.insert(0, os.path.normpath(os.path.dirname(__file__)) + "/../../")
from helper import MantidGeom

parser = argparse.ArgumentParser()
parser.add_argument('--TubeHeight', help='Tube height in meters', default=2.)
parser.add_argument('--EquatorialPixel', help='The index of the pixel (counting from 1) which is in xz plane', default=128.5)
parser.add_argument('--GlobalOffset', help='The global offset angle in degrees', default = 0.)
args = parser.parse_args()

valid_from = "1901-01-01 00:00:00"
# All distances are in meter, angles in degrees
instrumentName = 'SHARP'
numberOfTubes = 240
numberOfPixelsPerTube = 256
firstDetectorId = 1
l1 = 0.551
l2 = 2.5
pixelRadius = 0.0127
tubeHeight = float(args.TubeHeight)
equator = float(args.EquatorialPixel)
pixelHeight = tubeHeight / numberOfPixelsPerTube
tubeVerticalShift = (numberOfPixelsPerTube / 2 - equator) * pixelHeight
monitorZ = -0.362

pixelSpacingDegrees = 0.605
tubeAngles = np.linspace(0., (numberOfTubes-1)*pixelSpacingDegrees, numberOfTubes)

comment = """ This is the instrument definition file of the SHARP spectrometer at the ILL.
       Generated file, PLEASE DO NOT EDIT THIS FILE!
       This file was automatically generated by mantidgeometry/ILL/IDF/sharp_generateIDF.py
       """
geometry = MantidGeom(instrumentName, comment=comment, valid_from=valid_from)
geometry.addSnsDefaults(theta_sign_axis='x')
geometry.addComponentILL('fermi_chopper', 0.0, 0.0, -l1, 'Source')
geometry.addComponentILL('sample-position', 0.0, 0.0, 0.0, 'SamplePos')
geometry.addMonitors(names=['monitor'], distance=[monitorZ])
geometry.addDummyMonitor(0.009, 0.036) # the real radius is 0.09
geometry.addMonitorIds(['100000'])
geometry.addCylinderPixelAdvanced(
    'pixel', center_bottom_base={'x': 0., 'y': -pixelHeight / 2., 'z': 0.},
    axis={'x': 0., 'y': 1., 'z': 0.}, pixel_radius=pixelRadius,
    pixel_height=pixelHeight,
    algebra='pixel_shape')
root = geometry.getRoot()
detectorType = le.SubElement(root, 'type', name='detector')
tubes = le.SubElement(detectorType, 'component', type='tube')
for tubeIndex, tubeAngle in enumerate(tubeAngles):
    x = l2 * np.sin(-np.deg2rad(tubeAngle))
    z = l2 * np.cos(np.deg2rad(tubeAngle))
    attributes = {
        'x': str(x),
        'y': str(0.),
        'z': str(z),
        'name': 'tube_{}'.format(tubeIndex + 1)
    }
    le.SubElement(tubes, 'location', **attributes)
tubeType = le.SubElement(root, 'type', name='tube', outline='yes')
tube = le.SubElement(tubeType, 'component', type='pixel')
tube_bottom_pos = -(equator - 1) * pixelHeight
tube_top_pos = (numberOfPixelsPerTube - equator) * pixelHeight
pixelPositions = np.linspace(tube_bottom_pos, tube_top_pos, numberOfPixelsPerTube)
for i, pos in enumerate(pixelPositions):
    le.SubElement(tube, 'location', y=str(pos), name='pixel_{}'.format(i + 1))
detector = geometry.addComponent('detector', idlist='detectors')
le.SubElement(detector, 'location')
geometry.addDetectorIds('detectors', [1, numberOfTubes*numberOfPixelsPerTube, None])
geometry.writeGeom("./ILL/IDF/" + instrumentName + "_Definition.xml")
