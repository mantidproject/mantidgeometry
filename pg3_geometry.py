#!/usr/bin/env python

from helper import INCH_TO_METRE, DEG_TO_RAD, MantidGeom
from rectangle import Rectangle, Vector, getEuler, makeLocation
from lxml import etree as le # python-lxml on rpm based systems
from math import cos, sin, radians, pi
import numpy as np
from sns_ncolumn import readFile

# size of the panels from original pixel sizes
x_extent = 154*.005
y_extent = 7*.0543

# number of pixels in each direction - v2
x_num2 = 154
y_num2 = 7

# primary flight path - negative b/c it is upstream
L1 = -60.0

def readPositionsRight(filename):
    positions = readFile(filename)
    del positions['Position']
    del positions['DetectorNum']

    x = np.array(map(float, positions['X']))
    y = np.array(map(float, positions['Elevation']))
    z = np.array(map(float, positions['Z'])) - 60.
    positions['bank'] = np.array(map(int, positions['bank']))

    positions['position'] = []
    for x_i,y_i,z_i in zip(x,y,z):
        positions['position'].append(Vector(x_i, y_i, z_i))

    del positions['X']
    del positions['Elevation']
    del positions['Z']

    banks = {}
    for i, (column, row, bank, position) in enumerate(zip(positions['column'], positions['row'], positions['bank'], positions['position'])):
        i = i%4
        if i == 0:
            one = position
        elif i == 1:
            two = position
        elif i == 2:
            three = position
        elif i == 3:
            four = position
        else:
            raise ValueError("Inconceivable! i = %d" % i)

        if i == 3:
            banks[int(bank)] = (column, Rectangle(four, one, two, three, tolerance_len=0.006))

    return banks

def readPositionsLeft(filename):
    positions = readFile(filename)
    x = np.array(map(float, positions['X']))
    y = np.array(map(float, positions['Elevation']))
    z = np.array(map(float, positions['Z']))
    positions['position'] = []
    for x_i,y_i,z_i in zip(x,y,z):
        positions['position'].append(Vector(x_i, y_i, z_i))

    del positions['X']
    del positions['Elevation']
    del positions['Z']

    names = {'D596':79,
             'D579':76,
             'D261':73,
             'D585':70,
             'D586':67,
             'D573':64,
             'D571':61,
             'D574':58,
             'D225':55,
             'D565':52,
             'D551':48,
             'D594':43}
    columns = {43:'NA', 48:'NB', 52:'NC', 55:'ND', 58:'NE', 61:'NF', 64:'NG', 67:'NH', 70:'NI', 73:'NJ', 76:'NK', 79:'NL'}
    banks = {}
    for i, (det, position) in enumerate(zip(positions['Detector'], positions['position'])):
        bank = names[det[:4]]
        i = i%4
        if i == 0:
            three = position
        elif i == 1:
            four = position
        elif i == 2:
            one = position
        elif i == 3:
            two = position
        else:
            raise ValueError("Inconceivable! i = %d" % i)

        if i == 3:
            banks[bank] = (columns[bank], Rectangle(four, one, two, three, tolerance_len=0.006))

    return banks

if __name__ == "__main__":
    inst_name = "PG3"
    xml_outfile = inst_name+"_Definition.xml"
    authors = ["Peter Peterson",
               "Stuart Campbell",
               "Vickie Lynch",
               "Janik Zikovsky"]

    # boiler plate stuff
    instr = MantidGeom(inst_name,
                       comment="Created by " + ", ".join(authors),
                       valid_from="2018-05-05 00:00:01")
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

    # read in detectors
    banks = readPositionsRight("SNS/POWGEN/PG3_geom_2017.csv")
    banksL = readPositionsLeft("SNS/POWGEN/PG3_geom_left_2018.csv")
    for bank in banksL.keys():
        banks[bank] = banksL[bank]
    del banksL

    # delete the banks that are no longer installed
    for bank in [1,5,6,10,32,35,38,28,31,34,37,40]:
        del banks[bank]

    # create north and south sides
    sides = {'North':['NA','NB', 'NC', 'ND', 'NE', 'NF', 'NG', 'NH', 'NI', 'NJ', 'NK', 'NL'],
             'South':['SA','SB', 'SC', 'SD', 'SE', 'SF', 'SG', 'SH', 'SI', 'SJ', 'SK', 'SL']}
    # add the empty components
    for name in sides.keys():
        group = instr.addComponent(name)
    # add the columns to the groups
    for side in sides.keys():
        group = instr.makeTypeElement(side)

        for column in sides[side]:
            instr.addComponent(column, root=group)

    # create an ordered list of all columns
    columns = set()
    for name in banks.keys():
        column, _ =  banks[name]
        columns.add(column)
    columns = list(columns)
    columns.sort()

    createdcolumns = dict()
    for name in banks.keys():
        offset = (int(name)-1) * 15000
        column, rect =  banks[name]
        name = 'bank'+str(name)

        # create the column if it doesn't already exist
        if column in createdcolumns:
            col = createdcolumns[column]
        else:
            col = instr.makeTypeElement(str(column))
            createdcolumns[column] = col

        extra_attrs={"idstart":offset, 'idfillbyfirst':'y', 'idstepbyrow':y_num2}
        det = instr.makeDetectorElement('panel_v2', root=col, extra_attrs=extra_attrs)
        rect.makeLocation(instr, det, name)

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

    # monitor ids
    instr.addComment("MONITOR IDs")
    instr.addMonitorIds([-1]) # TODO [-1,-2,-3]

    # write out the file
    instr.writeGeom(xml_outfile)
    #instr.showGeom()
