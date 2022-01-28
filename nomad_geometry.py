#!/usr/bin/env python

# liberally ported from
# https://flathead.ornl.gov/trac/TranslationService/browser/calibration/geometry/NOM.py
from helper import INCH_TO_METRE, DEG_TO_RAD, MantidGeom
from rectangle import Rectangle, Vector
from lxml import etree as le # python-lxml on rpm based systems
from math import cos, sin, radians, pi
import numpy as np
from sns_ncolumn import readFile

# All of the tubes are 40" long with a 2mm gap between tubes
TUBE_LENGTH = 40. * INCH_TO_METRE # 1m long matches better in bank4
AIR_GAP = .002
TUBE_LENGTH_END = 1.0 # 1m
TUBE_LENGTH_SHORT = 0.461 # sausages
AIR_GAP_END = 0.0005

# Indices for the four corners of an eight-pack
LL = 0*128+0   # LOWER LEFT CORNER
UL = 0*128+127 # UPPER LEFT CORNER
LR = 7*128+0   # LOWER RIGHT CORNER
UR = 7*128+127 # UPPER RIGHT CORNER

def makeIds(numBanks, offset, size):
    ids = []
    for i in range(numBanks):
        ids.extend((i*size+offset, (i+1)*size+offset-1, None))
    return ids

# eight tubes in each bank, starting from 0
def getCorners(bank, pixels_high=128, pixels_wide=8):
    tube0 = (bank - 1) * 8 * 128 # most of the instrument is that size
    tube7 = tube0 + pixels_high*(pixels_wide-1)
    corners = [tube0 + 0, tube0 + (pixels_high-1), tube7 + (pixels_high-1), tube7 + 0]
    return corners

def getCornersSpecial(banknum):
    if banknum in [72, 90]:
        tube0 = getCorners(banknum)[0]
    elif banknum in [73,91]:
        tube0 = getCorners(banknum-1)[0] + 69
    tube15 = tube0 + 15*128
    corners = [tube0 + 0, tube0 + 58, tube15 + 58, tube15 + 0]
    return corners

def getRectangle(bank_num, positions, corners, tolerance_len=0.006):
    # TODO for some reason tolerance is bigger than the default
    try:
        one = positions[corners[0]]
        two = positions[corners[1]]
        three = positions[corners[2]]
        four = positions[corners[3]]
        if bank_num in (90,91):
            if bank_num == 90: # .046875 -> 0.148
                y_offset = 0.10113
            elif bank_num == 91: # -.0390625 -> -0.148
                y_offset = -0.1089375
            one = Vector(one.x, one.y+y_offset, one.z)
            two = Vector(two.x, two.y+y_offset, two.z)
            three = Vector(three.x, three.y+y_offset, three.z)
            four = Vector(four.x, four.y+y_offset, four.z)
        return Rectangle(one, two, three, four, tolerance_len=tolerance_len)
    except RuntimeError as e:
        print('bank', bank_num, corners)
        raise e

def readEngineeringPositions(filename):
    positions = readFile(filename, hasLabels=False)

    tube = np.fromiter(map(int, positions[0]), dtype=int)
    pixel = np.fromiter(map(int, positions[1]), dtype=int)
    id = tube*128+pixel

    x = -1. * np.fromiter(map(float, positions[6]), dtype=float)
    x[x == -0.] = 0.
    y = np.fromiter(map(float, positions[5]), dtype=float)
    z = np.fromiter(map(float, positions[7]), dtype=float)

    positions = {}
    for i, x_i,y_i,z_i in zip(id, x,y,z):
        positions[i] = Vector(x_i, y_i, z_i)

    return positions

def readSurveyPositions(filename):
    # label1, label2, z, x, y
    positions = readFile(filename, hasLabels=False, headerLines=1)

    labels = positions[0]
    #id = np.array(map(float, positions[0]))
    #id = np.array(map(int, id))
    # NOTE: label2 column is empty on latest survey, so these indices are shifted back one
    x = np.fromiter(map(float, positions[2]), dtype=float)
    y = np.fromiter(map(float, positions[3]), dtype=float)
    z = np.fromiter(map(float, positions[1]), dtype=float)

    # this is an intentional truncation of the information in the file
    # the values of the front and back planes do not make sense together
    # arbitrarily pick one of the sets
    '''
    id = []
    id.extend(getCornersSpecial(90))
    id.extend(getCornersSpecial(91))
    id.extend(getCorners(92))
    id.extend(getCorners(93))
    id.extend(getCorners(94))
    '''

    # skip reading measurements for these banks
    # NOTE: including these causes errors when Rectangles are created
    bad_banks = [58, 59, 60, 61, 62, 63]

    ids = []

    # mapping between survey points to getCorner indices
    # this allows survey measurements to be in any ordering in the file
    # getCorners returns in order: LL, UL, UR, LR
    mapping = {"1U": 3, "2U": 0, "2D": 1, "1D": 2}
    for i in range(0, len(labels), 4):
        det = labels[i]

        # this assumes the label column is in the format "Det#_[1U,2U,1D,2D]"
        [bank, _] = det.split("_")
        bank = int(bank.lstrip("Det"))

        if bank in bad_banks:
            print("Skipping bank {}!".format(bank))
            continue

        # loop over each measurement for this bank and find the correct
        # detector id it corresponds to
        corners = getCorners(bank)
        for j in range(0, 4):
            [b, pos] = labels[i + j].split("_")
            b = int(b.lstrip("Det"))
            # print("bank {} - {} --> {} ({})".format(b, pos, mapping[pos], corners[mapping[pos]]))
            # verify that this bank is the one we are working on
            assert (b == bank)
            ids.append(corners[mapping[pos]])

    positions = {}
    for i, x_i, y_i, z_i in zip(ids, x, y, z):
        if x_i == 0. and y_i == 0. and z_i == 0:
            continue
        # subtract off distance to source from z values
        positions[i] = Vector(x_i, y_i, z_i - 19.5)
    return positions

if __name__ == "__main__":
    inst_name = "NOMAD"
    xml_outfile = inst_name+"_Definition.xml"

    # boiler plate stuff
    instr = MantidGeom(inst_name,
                       comment=" Created by Peter Peterson",
                       valid_from="2017-06-05 00:00:01")
    instr.addComment("DEFAULTS")
    instr.addSnsDefaults(theta_sign_axis="x")
    instr.addComment("SOURCE")
    instr.addModerator(-19.5)
    instr.addComment("SAMPLE")
    instr.addSamplePosition()

    # monitors
    instr.addComment("MONITORS")
    instr.addMonitorIds([-1,-2])
    instr.addMonitors([-0.879475,5.748782], ["monitor1", "monitor2"])
    instr.addComment("Shape for monitors")
    instr.addComment("TODO: Update to real shape")
    instr.addDummyMonitor(0.01, .03)


    # TODO choppers and slits could go here


    ####################
    # read the positions of the pixels that was provided
    positions = readEngineeringPositions('SNS/NOMAD/NOM_detpos.txt')

    # update engineering postions with values from survey - survey values are worse
    #positionsSurvey = readSurveyPositions('SNS/NOMAD/NOMAD_survey_20180530_group6.csv')
    positionsSurvey = readSurveyPositions('SNS/NOMAD/NOMAD_survey_20210121.csv')
    for i, key in enumerate(positionsSurvey.keys()):
        positions[key] = positionsSurvey[key]

    num_banks = [14, 23, 14,12, 18, 18]

    ####################
    # add the id lists for groups - [start, stop, step]
    start, stop = -1, -1
    for i, num_banks_in_pack in enumerate(num_banks):
        start = stop+1
        stop = start + num_banks_in_pack*8*128-1
        info = instr.addDetectorIds('Group%d' % (i+1), [start, stop, None])

    for i, _ in enumerate(num_banks):
        group = 'Group%d' % (i+1)
        # set blank_location=False to add <location/> tag to component
        group = instr.addComponent(group, idlist=group, blank_location=False)

    ####################
    # group 1 is banks 1-14 (inclusive)
    bank_offset = 0
    group = instr.makeTypeElement('Group1')
    for i in range(num_banks[0]):
        bank_num = bank_offset + i + 1
        bank = "bank%d" % bank_num
        corners = getCorners(bank_num)
        rect = getRectangle(bank_num, positions, corners)
       	det = instr.makeDetectorElement('pack', root=group)
       	rect.makeLocation(instr, det, bank)

    # group 2 is banks 15-37 (inclusive)
    bank_offset += num_banks[0]
    group = instr.makeTypeElement('Group2')
    for i in range(num_banks[1]):
        bank_num = bank_offset+i+1
        bank = "bank%d" % bank_num
        corners = getCorners(bank_num)
        # appears to be backwards!!!!!!!!!!!!!!!!
        corners = [corners[1], corners[0], corners[3], corners[2]]
        rect = getRectangle(bank_num, positions, corners)
       	det = instr.makeDetectorElement('pack', root=group)
       	rect.makeLocation(instr, det, bank)

    # group 3 is banks 38-51 (inclusive)
    bank_offset += num_banks[1]
    group = instr.makeTypeElement('Group3')
    for i in range(num_banks[2]):
        bank_num = bank_offset+i+1
        bank = "bank%d" % bank_num
        corners = getCorners(bank_num)
        rect = getRectangle(bank_num, positions, corners)
       	det = instr.makeDetectorElement('pack', root=group)
       	rect.makeLocation(instr, det, bank)

    # group 4 is banks 52-63 (inclusive)
    bank_offset += num_banks[2]
    group = instr.makeTypeElement('Group4')
    for i in range(num_banks[3]):
        bank_num = bank_offset+i+1
        bank = "bank%d" % bank_num
        corners = getCorners(bank_num)

        rect = getRectangle(bank_num, positions, corners)

       	det = instr.makeDetectorElement('pack', root=group)
       	rect.makeLocation(instr, det, bank)

    # group 5 is banks 64-81 (inclusive) - 72 and 73 are special
    bank_offset += num_banks[3]
    group = instr.makeTypeElement('Group5')
    special = [72, 73]
    for i in range(num_banks[4]):
        bank_num = bank_offset+i+1
        bank = "bank%d" % bank_num
        if bank_num in special:
            corners = getCornersSpecial(bank_num)
        else:
            corners = getCorners(bank_num)

        # flipy
        corners = [corners[2], corners[3], corners[0], corners[1]]
        rect = getRectangle(bank_num, positions, corners)

        if bank_num in special:
       	    det = instr.makeDetectorElement('packhalfshort', root=group)
        else:
       	    det = instr.makeDetectorElement('packhalf', root=group)
       	rect.makeLocation(instr, det, bank)


    # group 6 is banks 81-99 (inclusive) - 90 and 91 are special
    bank_offset += num_banks[4]
    group = instr.makeTypeElement('Group6')
    special = [90,91]
    # Panels 92,93 were moved into backscattering (pixel numbers reassigned),
    # then 94,95,96 were slid over without reassigning pixles. This dictionary
    # handles shuffling those around and should be removed for the next run
    # cycle
    shuffled = {94:92, 95:93, 96:94, 92:95, 93:96}
    for i in range(num_banks[5]):
        bank_num = bank_offset+i+1
        bank = "bank%d" % bank_num
        if bank_num in special:
            corners = getCornersSpecial(bank_num)
        else:
            corners = getCorners(shuffled.get(bank_num, bank_num))

        # corners are mixed up
        if bank_num == 91:
            # flipx
            corners = [corners[3], corners[2], corners[1], corners[0]]
        elif bank_num == 90:
            # flipy
            corners = [corners[2], corners[3], corners[0], corners[1]]
        else:
            corners = [corners[2], corners[3], corners[0], corners[1]]

        rect = getRectangle(bank_num, positions, corners)

        if bank_num in special:
       	    det = instr.makeDetectorElement('packhalfshort', root=group)
        else:
       	    det = instr.makeDetectorElement('packhalf', root=group)
       	rect.makeLocation(instr, det, bank)

    ####################
    # define various "packs" of detectors
    # 1m x 1" 8-pack
    instr.addComment('banks 1 - 4 - 128x8 panel (128x8) - one inch')
    instr.addNPack(name='pack', type_name='tube', num_tubes=8,
                   tube_width=INCH_TO_METRE, air_gap=AIR_GAP)
    instr.addPixelatedTube(name='tube', type_name='onepixel', num_pixels=128,
                           tube_height=TUBE_LENGTH)
    instr.addCylinderPixel("onepixel", (0.0, 0.0, 0.0), (0.0, 1.0, 0.0),
                           (.5*INCH_TO_METRE), (TUBE_LENGTH/128.))


    # 1m x .5" 8-pack
    instr.addComment('banks 5 and 6 - 128x8 panel - half inch by 1m')
    instr.addNPack(name='packhalf', type_name='halftube', num_tubes=8,
                   tube_width=0.25*INCH_TO_METRE, air_gap=AIR_GAP_END)
    instr.addPixelatedTube(name='halftube', type_name='halfonepixel', num_pixels=128,
                           tube_height=TUBE_LENGTH_END)
    instr.addCylinderPixel('halfonepixel', (0.0, 0.0, 0.0), (0.0, 1.0, 0.0),
                           (.25*INCH_TO_METRE), (TUBE_LENGTH_END/128.))


    # sausage .5m x .5" 6-pack
    instr.addComment('banks 5 and 6 - 64x8 panel - half inch by .5m')
    instr.addNPack(name='packhalfshort', type_name='halfshorttube', num_tubes=16,
                   tube_width=0.25*INCH_TO_METRE, air_gap=AIR_GAP_END)
    instr.addPixelatedTube(name='halfshorttube', type_name='shortonepixel', num_pixels=64,
                           tube_height=TUBE_LENGTH_SHORT)
    instr.addCylinderPixel('shortonepixel', (0.0, 0.0, 0.0), (0.0, 1.0, 0.0),
                           (.25*INCH_TO_METRE), TUBE_LENGTH_SHORT/64.)

    # write out the file
    instr.writeGeom(xml_outfile)
    #instr.showGeom()
