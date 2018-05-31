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
        print 'bank', bank_num, corners
        raise e

def readEngineeringPositions(filename):
    positions = readFile(filename, hasLabels=False)

    tube = np.array(map(int, positions[0]))
    pixel = np.array(map(int, positions[1]))
    id = tube*128+pixel

    x = -1. * np.array(map(float, positions[6]))
    x[x == -0.] = 0.
    y = np.array(map(float, positions[5]))
    z = np.array(map(float, positions[7]))

    positions = {}
    for i, x_i,y_i,z_i in zip(id, x,y,z):
        positions[i] = Vector(x_i, y_i, z_i)

    return positions

def readSurveyPositions(filename):
    # pixelid, x, y, z
    positions = readFile(filename, hasLabels=False, headerLines=4)
    id = np.array(map(float, positions[0]))
    id = np.array(map(int, id))
    x = np.array(map(float, positions[1]))
    y = np.array(map(float, positions[2]))
    z = np.array(map(float, positions[3]))

    positions = {}
    for i, x_i,y_i,z_i in zip(id, x,y,z):
        if x_i == 0. and y_i == 0. and z_i == 0:
            continue
        positions[i] = Vector(x_i, y_i, z_i)
    return positions

if __name__ == "__main__":
    inst_name = "NOMAD"
    xml_outfile = inst_name+"_Definition.xml"

    # boiler plate stuff
    instr = MantidGeom(inst_name,
                       comment=" Created by Peter Peterson",
                       valid_from="2017-02-01 00:00:01")
    instr.addComment("DEFAULTS")
    instr.addSnsDefaults()
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
    '''
    positionsSurvey = readSurveyPositions('SNS/NOMAD/pixelpos.dat')
    # update the engineering positons with ones derived from survey
    special = [74752, 74879, 75775, 75648, # bank 74
               95232, 95359, 96255, 96128, # bank 94
               96256, 96383, 97279, 97152] # bank 95
    for i in special:
        if i not in positionsSurvey:
            continue
        print '*****', i
        print positions[i], 'eng'
        print positionsSurvey[i], 'survey'
    updated_pos = np.zeros(len(positions.keys())).astype(bool)
    for i in positions.keys():
        if i in positionsSurvey and i not in special:
            distance = (positions[i]-positionsSurvey[i]).length
            if abs(distance) > 0.01:
                print 'move', i, 'by', distance
            positions[i] = positionsSurvey[i]
            updated_pos[i] = True
    print 'updated', updated_pos

    #print positions[3071], 'eng 3071'
    #print positions[3072], 'eng 3072'
    #print positions[3073], 'eng 3073'
    #print positions2[3072], 'survey'
    #print '********************'
    #print '3071', positions2.get(3071, positions[3071]), 'meld'
    #print '3072', positions2.get(3072, positions[3072]), 'meld'
    '''

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
        group = instr.addComponent(group, idlist=group)

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
