import os
path = os.path.abspath("")
import sys
sys.path.insert(0, path)
from helper import MantidGeom

from lxml import etree as le
# using metre as unit
instrumentName = 'D7'
validFrom = "1900-01-31 23:59:59"
validTo="2100-01-31 23:59:59"

# Monochromator position
source = -3.6

# Fermi chopper
zChopper = -0.48

# 2 Monitors
zMon1 = -1.3
zMon2 = 1.5

# distance between the sample and detectors:
rSampleDetectors = 1.5177 # distance from the sample of even detectors
minTwoTheta = 0
maxTwoTheta = 136

# definition of a detector bank
numberBanks = 3 # banks 2, 3 and 4; bank 1 is a monitor
numberDetectors = 44

# definition of a pixel
tubeRadius = 0.0125
tubeHeight = 0.25

# definitions of intersection positions for detectors in the same casette
externalIntersectonDistance = 11.0
intersectionAngle = 0.4189 # externalIntersectonDistance / (rSampleDetectors - tubeRadius) = 0.4189 degrees
detectorOffset = 1.114 # degree


comment = """ This is the instrument definition file of the D7 diffuse scattering spectrometer at the ILL.
       Generated file, PLEASE DO NOT EDIT THIS FILE!
       This file was automatically generated by mantidgeometry/ILL/IDF/d7_generateIDF.py
       z axis defines the direction of the beam
       y axis will be the axis used for rotation
       coordinate system is right-handed
       x axis rotation defined by phi 
       y axis rotation defined by theta 
       height y direction
       The instrument operates in two modes
       - Diffraction:
          - wavelength 3.1 A, qmin = 0.4, qmax = 4.0
          - wavelength 4.8 A, qmin = 0.3, qmax = 2.5
          - wavelength 5.7 A, qmin = 0.2, qmax = 2.1
       - Spectroscopy time-of-flight 
          - using Fermi chopper, with the same possible wavelengths

       Source-to-sample distances is 3.6 m 
       Three detector banks with 44 position-insensitive He3 detectors each
       Each detector located 1.5 m from the sample
       covering 2 Theta range from about 10 to 155 degrees
       Detector tubes have 25 mm in diameter and are 250 mm in height
       For more information, please visit 
       https://www.ill.eu/instruments-support/instruments-groups/instruments/d7/characteristics/
       """
d7 = MantidGeom(instrumentName, comment=comment, valid_from=validFrom)
d7.addSnsDefaults(default_view='3D',axis_view_3d='z-')
d7.addComment("SOURCE")
d7.addComponentILL("Monochromator", 0., 0., source, "Source")
d7.addComment("Sample position")
d7.addComponentILL("sample_position", 0., 0., 0., "SamplePos")
d7.addComment("Fermi chopper")
d7.addComponentILL('fermi_chopper', 0.0, 0.0, zChopper, 'ChopperPos')
d7.addComment("MONITORS")
d7.addMonitors(names=["monitor1", "monitor2"], distance=[zMon1, zMon2])
d7.addComment("MONITOR SHAPE")
d7.addComment("FIXME: Do something real here.")
d7.addDummyMonitor(0.01, 0.03)
d7.addComment("MONITOR IDs")
d7.addMonitorIds([repr(1000), repr(1001)])
d7.addComment("DETECTORS")
d7.addComponentILL("detector", 0., 0., 0.)
detector = d7.makeTypeElement("detector")

# define detector banks
d7.addDetectorIds("bank2_ids", [1,44,1]) 
d7.addDetectorIds("bank3_ids", [45,88,1]) 
d7.addDetectorIds("bank4_ids", [89,132,1]) 
bank = d7.makeTypeElement("bank")
bank2 = d7.addComponent("bank", idlist = "bank2_ids", root=detector)
bank3 = d7.addComponent("bank", idlist = "bank3_ids", root=detector)
bank4 = d7.addComponent("bank", idlist = "bank4_ids", root=detector)

# define detector banks initial positions
d7.addLocation(root=bank2, x = 0, y = 0, z = 0, rot_y = repr(-(minTwoTheta + 0.5 * numberDetectors)), name="bank2")
d7.addLocation(root=bank3, x = 0, y = 0, z = 0, rot_y = repr(-(minTwoTheta + 1.5 * numberDetectors + 2 )), name="bank3")
d7.addLocation(root=bank4, x = 0, y = 0, z = 0, rot_y = repr(-(maxTwoTheta - 0.5 * numberDetectors)), name="bank4")

bankComponent = d7.addComponent(root=bank, type_name="pixel")

# define detectors and their relative position inside the bank:
for j in range(numberDetectors):
    tubeTheta = 0.5*numberDetectors - j - detectorOffset
    detectorName = "pixel_%d" % (j+1)
    rDetectors = rSampleDetectors
    if j % 2 != 0: # odd detectors are closer to the sample 
        rDetectors -= tubeRadius
    else:
        tubeTheta -= intersectionAngle
    d7.addLocationPolar(root=bankComponent, r=repr(rDetectors), theta=repr(tubeTheta), phi=repr(0), name=detectorName)

# define pixel type
d7.addCylinderPixelAdvanced(
    'pixel', center_bottom_base={'x': 0., 'y': -tubeHeight / 2., 'z': 0},
    axis={'x': 0., 'y': 1., 'z': 0.}, pixel_radius=tubeRadius,
    pixel_height=tubeHeight,
    algebra='cyl_approx')
        
d7.writeGeom(instrumentName + "_Definition.xml")
