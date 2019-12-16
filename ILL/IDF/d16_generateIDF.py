import os
path = os.path.abspath("")
import sys
sys.path.insert(0, path)
from helper import MantidGeom


# unit is metre
instrumentName = 'D16'
validFrom = "2019-12-16 00:00:00"  # TODO : ask for the real value


monochromator_source = 2.8  # TODO : check if correct

# 2 monitors
zMon1 = 0  # TODO: ask value
zMon2 = 0

# definition of the quadratic detector
numberPixelsVertical = 320
numberPixelsHorizontal = 320

# definition of a quadratic pixel
pixelName = "pixel"
pixelWidth = 0.001
pixelHeight = 0.001
x = pixelWidth / 2.
y = pixelHeight / 2.
z = 0.
thickness = 0.0001  # TODO : find value

# detector
zPosDetector = 1  # somewhere inbetween 0.3 and 1 -> TODO: ask how to determine how to set this

# identification numbers
id0 = repr(0)

# rectangular detector
xstart = repr(-pixelWidth * (numberPixelsHorizontal - 1) / 2)
xstep = repr(pixelWidth)
xpixels = repr(numberPixelsHorizontal)
ystart = repr(-pixelHeight * (numberPixelsVertical - 1) / 2)
ystep = repr(pixelHeight)
ypixels = repr(numberPixelsVertical)

# TODO : ask what is this used for
FF = "y"  # idfillbyfirst
SR = repr(numberPixelsVertical)  # idstepbyrow

# detector name
detector0 = "main_detector"

# introductory comment
comment = "To write"


# Instrument creation
d33 = MantidGeom(instrumentName, comment=comment, valid_from=validFrom)
d33.addSnsDefaults(default_view='3D', axis_view_3d='z-')

d33.addComment("SOURCE")
d33.addComponentILL("monochromator", 0., 0., monochromator_source, "Source")

# Sample is set as the origin
d33.addComment("Sample position")
d33.addComponentILL("sample_position", 0., 0., 0., "SamplePos")

d33.addComment("MONITORS")
d33.addMonitors(names=["monitor1", "monitor2"], distance=[zMon1, zMon2])
d33.addComment("MONITOR SHAPE")
d33.addComment("FIXME: Do something real here.")
d33.addDummyMonitor(0.01, 0.03)  # TODO : ask for monitors shape
d33.addComment("MONITOR IDs")
d33.addMonitorIds([repr(500000), repr(500001)])

d33.addComment("DETECTORS")
d33.addComponentILL("detector", 0., 0., 0.)
detector = d33.makeTypeElement("detector")
d33.addComponentRectangularDetector(detector0, 0., 0., zPosDetector, idstart=id0, idfillbyfirst=FF, idstepbyrow=SR, root=detector)
d33.addComment("REAR DETECTOR")
d33.addRectangularDetector(detector0, pixelName, xstart, xstep, xpixels, ystart, ystep, ypixels)

# TODO : check if this should be kept, and if so, ask for thickness
d33.addComment("PIXEL, EACH PIXEL IS A DETECTOR")
d33.addCuboidPixel(pixelName, [-x, -y, thickness/2.], [-x, y, thickness/2.], [-x, -y, -thickness/2.], [x, -y, -thickness/2.], shape_id="pixel-shape")

d33.writeGeom("./ILL/IDF/" + instrumentName + "_Definition.xml")
