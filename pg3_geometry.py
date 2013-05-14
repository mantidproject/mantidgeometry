#!/usr/bin/env python

from helper import INCH_TO_METRE, DEG_TO_RAD, MantidGeom
from rectangle import Rectangle, Vector
from lxml import etree as le # python-lxml on rpm based systems
from math import cos, sin, radians, pi
from sns_ncolumn import readFile

def toEasier(label):
    letter = "ABCDEFGHIJKL".index(label[0])
    number = int(label[1:])
    side = 0
    if number > 9:
        side  = 1
    return (side, letter, number)

def getBankNameAndOffset(label):
    (side, letter, number) = toEasier(label)
    offset = 25000*letter + number*1250
    return ("bank%d" % (offset/1250), offset)

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
            det = instr.makeDetectorElement("panel", root=col,
                                            extra_attrs={"idstart":offset, 'idfillbyfirst':'y', 'idstepbyrow':7})
            corners.rectangle(label, .006).makeLocation(instr, det, name, technique="uv")


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
    L1 = -60.0

    # boiler plate stuff
    instr = MantidGeom(inst_name,
                       comment="Created by " + ", ".join(authors),
                       valid_from="2013-06-01 00:00:01",
                       valid_to="2013-07-31 23:59:59")
    instr.addComment("DEFAULTS")
    instr.addSnsDefaults()
    instr.addComment("SOURCE")
    instr.addModerator(L1)
    instr.addComment("SAMPLE")
    instr.addSamplePosition()

    # monitors
    instr.addComment("MONITORS")
    instr.addMonitors([-1.], ["monitor1"])
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
    cols = {4:['B'], 3:['C', 'D'], 2:['E', 'F'], 1:['G', 'H', 'I', 'J', 'K']}

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
    corners = CornersFile("PG3_geom_2011_txt.csv", abs(L1))
    addGroup(corners, cols[4], ["B2", "B3", "B4", "B5"])
    addGroup(corners, cols[3], ['C2', 'C3',  'C4', 'C5', 'D2', 'D3', 'D4'])
    addGroup(corners, cols[2], ['E2', 'E3', 'E4', 'F2', 'F3', 'F4'])
    addGroup(corners, cols[1], ['G3', 'G4', 'H3', 'H4', 'I4', 'J4', 'K4'])

    # add the panel shape
    instr.addComment(" New Detector Panel (7x154)")
    det = instr.makeTypeElement("panel", extra_attrs={"is":"rectangular_detector", "type":"pixel",
                                                         "xpixels":154, "xstart":-0.3825, "xstep":0.005,
                                                         "ypixels":7, "ystart":-0.162857142857, "ystep":0.0542857142857
                                                         })
    le.SubElement(det, "properties")

    # shape for monitors
    instr.addComment(" Shape for Monitors")
    instr.addComment(" TODO: Update to real shape ")
    instr.addDummyMonitor(0.01, .03)

    # shape for detector pixels
    instr.addComment(" Pixel for New Detectors (7x154)")
    instr.addCuboidPixel("pixel", 
                         [-0.0025, -0.027143,  0.0],
                         [-0.0025,  0.027143,  0.0],
                         [-0.0025, -0.027143, -0.0001],
                         [ 0.0025, -0.027143,  0.0],
                         shape_id="pixel-shape")

    # monitor ids
    instr.addComment("MONITOR IDs")
    instr.addMonitorIds([-1]) # TODO [-1,-2,-3]

    # write out the file
    instr.writeGeom(xml_outfile)
    #instr.showGeom()
