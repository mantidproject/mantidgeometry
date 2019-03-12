from __future__ import (absolute_import, division, print_function)

from helper import MantidGeom
from lxml import etree as le
import numpy as np


# All distances are in meter, angles in degrees
instrumentName = 'PANTHER'
numberOfBoxes = 9
numberOfTubesPerBox = 32
numberOfTubes = numberOfBoxes * numberOfTubesPerBox
numberOfPixelsPerTube = 256
firstDetectorId = 1
l1 = 0.8
l2 = 2.5
tubeHeight = 2.2
pixelRadius = 0.022 / 2. - 0.0004
pixelHeight = tubeHeight / numberOfPixelsPerTube
tubeVerticalShift = tubeHeight / 2 - 0.5925
monitorZ = -0.4955

boxGapAngle = 1.03
boxAngleWidth = 16.06
tubeAngleStep = boxAngleWidth / (numberOfTubesPerBox - 1)

boxAngles = list()
firstBoxCenterAngle = -0.5 * (boxAngleWidth + boxGapAngle)
for i in range(numberOfBoxes):
    boxAngles.append(firstBoxCenterAngle + i * (boxAngleWidth + boxGapAngle))

comment = """ This is the instrument definition file of the PANTHER spectrometer at the ILL.
       This file was automatically generated by mantidgeometry/ILL/IDF/panther_generateIDF.py
       """
validFrom = '1900-01-31 23:59:59'
geometry = MantidGeom(instrumentName, comment=comment, valid_from=validFrom)
geometry.addSnsDefaults(theta_sign_axis='x')
geometry.addComponentILL('fermi_chopper', 0.0, 0.0, -l1, 'Source')
geometry.addComponentILL('sample-position', 0.0, 0.0, 0.0, 'SamplePos')
geometry.addMonitors(names=['monitor'], distance=[monitorZ])
geometry.addDummyMonitor(0.01, 0.03)
geometry.addMonitorIds(['100000'])
geometry.addCylinderPixelAdvanced(
    'pixel', center_bottom_base={'x': 0., 'y': 0., 'z': -pixelHeight / 2.},
    axis={'x': 0., 'y': 1., 'z': 0.}, pixel_radius=pixelRadius,
    pixel_height=pixelHeight,
    algebra='pixel_shape')
root = geometry.getRoot()
bank = le.SubElement(root, 'type', name='bank')
tubes = le.SubElement(bank, 'component', type='tube')
for boxIndex, boxAngle in enumerate(boxAngles):
    for tubeIndex in range(numberOfTubesPerBox):
        tubeAngle = boxAngle - boxAngleWidth / 2. + tubeIndex * tubeAngleStep
        x = l2 * np.sin(np.deg2rad(tubeAngle))
        y = tubeVerticalShift
        z = l2 * np.cos(np.deg2rad(tubeAngle))
        attributes = {
            'x': str(x),
            'y': str(y),
            'z': str(z),
            'rot': str(tubeAngle),
            'axis-x': str(0.),
            'axis-y': str(1.),
            'axis-z': str(0.),
            'name': 'tube_{}'.format(boxIndex * numberOfTubesPerBox + tubeIndex + 1)
        }
        le.SubElement(tubes, 'location', **attributes)
tubeType = le.SubElement(root, 'type', name='tube', outline='yes')
tube = le.SubElement(tubeType, 'component', type='pixel')
pixelPositions = np.linspace(-tubeHeight/2., tubeHeight/2., numberOfPixelsPerTube)
for pos in pixelPositions:
    le.SubElement(tube, 'location', y=str(pos))
geometry.addComponent('detectors', idlist='detectors')
detectorType = le.SubElement(root, 'type', name='detectors')
bankComponent = le.SubElement(detectorType, 'component', type='bank')
le.SubElement(bankComponent, 'location')
geometry.addDetectorIds('detectors', [1, 73728, None])
geometry.writeGeom("./ILL/IDF/" + instrumentName + "_Definition.xml")
