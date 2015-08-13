#!/usr/bin/env python

from helper import INCH_TO_METRE, DEG_TO_RAD, MantidGeom
from rectangle import Rectangle, Vector, getEuler, makeLocation
from lxml import etree as le # python-lxml on rpm based systems
from math import cos, sin, radians, pi
from sns_ncolumn import readFile

# size of the panels from original pixel sizes
x_extent = 154*.005
y_extent = 7*.0543

# number of pixels in each direction
x_num2 = 154
y_num2 = 7
x_num3 = 308
y_num3 = 16

# primary flight path - negative b/c it is upstream
L1 = -60.0

def toEasier(label):
    letter = "ABCDEFGHIJKL".index(label[0])
    number = int(label[1:])
    side = 0
    if number > 12:
        side  = 1
    return (side, letter, number)

def getBankNameAndOffset(label):
    (side, letter, number) = toEasier(label)
    offset = 100000*letter + number*5000
    return ("bank%d" % (offset/5000), offset)

def addCenterRectangle(instr, det, name, detinfo, index):
    # get the center
    center = ['x', 'y', 'z']
    center = [float(detinfo[item][index])/1000. for item in center]

    # create the two unit vectors
    u = Vector(detinfo["PUx"][index], detinfo["PUy"][index],
               detinfo["PUz"][index])
    v = Vector(detinfo["PVx"][index], detinfo["PVy"][index],
               detinfo["PVz"][index])

    # turn them into rotations
    (phi, chi, omega) = getEuler(u, v, degrees=True)
    rotations = [[phi,   (0., 1., 0.)],
                 [chi,   (0., 0., 1.)],
                 [omega, (0., 1., 0.)]]

    print name, center
    print "     ", u.normalize(), v.normalize()
    print "     ", rotations
    makeLocation(instr, det, name, center, rotations)

def addGroup(corners, columns, labels):
    # setup the relation between labels and columns
    labels_in_col = {}
    for column in columns:
        labels_in_col[column] = []
    for label in labels:
        column = label[0]
        labels_in_col[column].append(label)

    # add the panels
    for column in columns:
        letter = "ABCDEFGHIJKL".index(column) + 1
        col = instr.makeTypeElement("Column%d" % letter)
        for label in labels_in_col[column]:
            (name, offset) = getBankNameAndOffset(label)
            panel_name="panel_v2"
            idstepbyrow=y_num2
            if label in v3_panels:
                panel_name="panel_v3"
                idstepbyrow=y_num3
            extra_attrs={"idstart":offset, 'idfillbyfirst':'y', 'idstepbyrow':idstepbyrow}
            det = instr.makeDetectorElement(panel_name, root=col, extra_attrs=extra_attrs)
            try:
              corners.rectangle(label, .014).makeLocation(instr, det, name, technique="uv")
            except ValueError, e:
              print "Failed to generate '" + label \
                  + "' from corners. Trying from engineered centers."
              detinfo = readFile("SNS/POWGEN/PG3_geom.txt")
              addCenterRectangle(instr, det, name, detinfo, detinfo["label"].index(label))

# for the next cycle they will all be low resolution
v3_panels = []#'B2', 'B3', 'B4', 'B5', 'B6', 'K4', 'L4']

class CornersFile:
    def __init__(self, filename, L1=0.):
        self._detinfo = readFile(filename)
        self._L1 = L1
        #print self._detinfo.keys()
        #print self._detinfo['Point_ID']

    def _point(self, index):
        result = []
        for key in ('X', 'Y', 'Z'):
            result.append(self._detinfo[key][index])
        return result

    def points(self, label):
        indices = [label + "_" + str(item) for item in (1,2,3,4)]
        indices = [self._detinfo["Point_ID"].index(item) for item in indices]

        result = []
        for index in indices:
            result.append(self._point(index))
        return result

    def rectangle(self, label, tolerance_len):
        corners = self.points(label)
        for corner in corners:
            corner[2] = float(corner[2]) - self._L1
        (one, two, three, four) = corners
        # funny ordering copied from TS
        return Rectangle(three, four, one, two, tolerance_len=tolerance_len)

if __name__ == "__main__":
    inst_name = "PG3"
    xml_outfile = inst_name+"_Definition.xml"
    authors = ["Stuart Campbell",
               "Vickie Lynch",
               "Peter Peterson",
               "Janik Zikovsky"]

    # boiler plate stuff
    instr = MantidGeom(inst_name,
                       comment="Created by " + ", ".join(authors),
                       valid_from="2015-08-01 00:00:01")
    instr.addComment("DEFAULTS")
    instr.addSnsDefaults()
    instr.addComment("SOURCE")
    instr.addModerator(L1)
    instr.addComment("SAMPLE")
    instr.addSamplePosition()

    # monitors
    instr.addComment("MONITORS")
    instr.addMonitors(distance=[-1.5077], names=["monitor1"])
    #instr.addMonitors([L1+59., L1+62.5, L1+64], ["monitor1", "monitor2", "monitor3"])

    # choppers - copied verbatium from TS-geometry
    """
    chopper1 = Component("chopper1", "NXchopper")
    chopper1.setComment("CHOPPERS")
    chopper1.setHelper("ParameterCopy")
    chopper1.addParameter("distance", "6.647418", units="metre")
    instrument.addComponent(chopper1)
    chopper2 = Component("chopper2", "NXchopper")
    chopper2.setHelper("ParameterCopy")
    chopper2.addParameter("distance", "7.899603", units="metre")
    instrument.addComponent(chopper2)
    chopper3 = Component("chopper3", "NXchopper")
    chopper3.setHelper("ParameterCopy")
    chopper3.addParameter("distance", "49.975666", units="metre")
    instrument.addComponent(chopper3)
    """

    # apertures - copied verbatium from TS-geometry
    """
    aperture1=Component("aperture1", "NXaperture")
    aperture1.setComment(" APERTURES ")
    aperture1.setHelper("CenteredRectangle")
    aperture1.addVariable("cenDistance", "slit1Sam")
    aperture1.addVariable("xExtent", "s1width")
    aperture1.addVariable("yExtent", "s1height")
    instrument.addComponent(aperture1)
    """

    # guides - not even copying the text

    # mapping of groups to column names
    cols = {4:['B'], 3:['C', 'D'], 2:['E', 'F'], 1:['G', 'H', 'I', 'J', 'K', 'L']}

    # add the empty components
    for i in cols.keys():
        name = "Group%d" % i
        group = instr.addComponent(name)#, idlist=name)

    # add the columns to the group
    for groupNum in cols.keys():
        name = "Group%d" % groupNum
        group = instr.makeTypeElement(name)

        for column in cols[groupNum]:
            name = "Column%d" % ("ABCDEFGHIJKL".index(column) + 1)
            instr.addComponent(name, root=group)

    # the actual work of adding the detectors
    corners = CornersFile("SNS/POWGEN/PG3_geom_2014_txt.csv", abs(L1))
    addGroup(corners, cols[4], ["B2", "B3", "B4", "B5", "B6"])
    addGroup(corners, cols[3], ['C2', 'C3',  'C4', 'C5', 'C6', 'D2', 'D3', 'D4', 'D5', 'D6'])
    addGroup(corners, cols[2], ['E2', 'E3', 'E4', 'E5', 'E6', 'F2', 'F3', 'F4', 'F5'])
    addGroup(corners, cols[1], ['G3', 'G4', 'H3', 'H4', 'I4', 'J4', 'K4'])

    # add the panel shape
    instr.addComment(" Version 2 Detector Panel (7x154)")
    x_delta2 = x_extent/float(x_num2)
    x_offset2 = x_delta2*(1.-float(x_num2))/2.
    y_delta2 = y_extent/float(y_num2)
    y_offset2 = y_delta2*(1.-float(y_num2))/2.
    det = instr.makeTypeElement("panel_v2",
                                extra_attrs={"is":"rectangular_detector", "type":"pixel_v2",
                                             "xpixels":x_num2, "xstart":x_offset2, "xstep":x_delta2,
                                             "ypixels":y_num2, "ystart":y_offset2, "ystep":y_delta2
                                             })
    le.SubElement(det, "properties")
    if len(v3_panels) > 0:
        instr.addComment(" Version 3 Detector Panel (16x308)")
        x_delta3 = x_extent/float(x_num3)
        x_offset3 = x_delta3*(1.-float(x_num3))/2.
        y_delta3 = y_extent/float(y_num3)
        y_offset3 = y_delta3*(1.-float(y_num3))/2.
        det = instr.makeTypeElement("panel_v3",
                                    extra_attrs={"is":"rectangular_detector", "type":"pixel_v3",
                                                 "xpixels":x_num3, "xstart":x_offset3, "xstep":x_delta3,
                                                 "ypixels":y_num3, "ystart":y_offset3, "ystep":y_delta3
                                                 })
        le.SubElement(det, "properties")

    # shape for monitors
    instr.addComment(" Shape for Monitors")
    instr.addComment(" TODO: Update to real shape ")
    instr.addDummyMonitor(0.01, .03)

    # shape for detector pixels
    instr.addComment(" Pixel for Version 2 Detectors (7x154)")
    instr.addCuboidPixel("pixel_v2",
                         [-.5*x_delta2, -.5*y_delta2,  0.0],
                         [-.5*x_delta2,  .5*y_delta2,  0.0],
                         [-.5*x_delta2, -.5*y_delta2, -0.0001],
                         [ .5*x_delta2, -.5*y_delta2,  0.0],
                         shape_id="pixel-shape")
    if len(v3_panels) > 0:
        instr.addComment(" Pixel for Version 3 Detectors (16x308)")
        instr.addCuboidPixel("pixel_v3",
                             [-.5*x_delta3, -.5*y_delta3,  0.0],
                             [-.5*x_delta3,  .5*y_delta3,  0.0],
                             [-.5*x_delta3, -.5*y_delta3, -0.0001],
                             [ .5*x_delta3, -.5*y_delta3,  0.0],
                             shape_id="pixel-shape")

    # monitor ids
    instr.addComment("MONITOR IDs")
    instr.addMonitorIds([-1]) # TODO [-1,-2,-3]

    # write out the file
    instr.writeGeom(xml_outfile)
    #instr.showGeom()
