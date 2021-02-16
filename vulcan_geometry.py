#!/usr/bin/env python
from helper import INCH_TO_METRE, DEG_TO_RAD, MantidGeom
from lxml import etree as le  # python-lxml on rpm based systems
import numpy as np
from sns_ncolumn import readFile


L1: float = -43.754  # meter
TUBE_LENGTH: float = 1.0  # meter
TUBE_LENGTH_SHORT: float = 0.7  # meters
TUBE_RADIUS: float = 0.317 * INCH_TO_METRE * 0.5  # given as diameter
TUBE_PIXELS: int = 512
PIXELS_PER_EIGHTPACK: int = 8*TUBE_PIXELS  # number of actual pixels
PIXELS_PER_PANEL: int = 5000  # reserve extra pixels after the end of the 8-pack
PIXELS_PER_BANK: int = PIXELS_PER_PANEL * 20  # maximum number of 8-pack in a bank
SEPARATION: float = 0.323 * INCH_TO_METRE  # distance between front and back
SLIP: float = 0.434 * INCH_TO_METRE  # distance between 2 and 4
SLIP_PANEL: float = 3 * SLIP + 0.460 * INCH_TO_METRE  # bonus spacing between panel centers

CSV_FILE: str = 'SNS/VULCAN/VULCAN_geom_20210210.csv'


def readPositions(filename: str = CSV_FILE):
    # read in and delete unneccessary columns
    positions = readFile(filename, delimiter=',')
    del positions['L']
    del positions['C']

    # set up a dict to split the data into
    banks = {'bank1': {},
             'bank2': {},
             'bank5': {}}
    for bank_label in banks.keys():
        for column in positions.keys():
            banks[bank_label][column] = []

    # split the data into banks
    for i, point_label in enumerate(positions['Point']):
        bank_label = ''
        if point_label.startswith('HA_'):
            bank_label = 'bank5'
        elif point_label.startswith('BR_'):
            bank_label = 'bank2'
        elif point_label.startswith('BL_'):
            bank_label = 'bank1'
        if bank_label:
            banks[bank_label]['Point'].append(point_label.split('_')[-1])
            banks[bank_label]['X'].append(positions['X'][i])
            banks[bank_label]['Y'].append(positions['Y'][i])
            banks[bank_label]['Z'].append(positions['Z'][i])

    # convert the positions to ndarray of float
    for bank_label in banks.keys():
        for column in ['X', 'Y', 'Z']:
            banks[bank_label][column] = np.array(banks[bank_label][column], dtype=float)

    return banks


def addEightPack(instr, name: str, tube_type: str):
    '''Add an interleaved 8-pack where pixel 1 is in the lower-left
    corner in the back then increases along the tube upward. The bottom
    of tube two is in the front.

    back     1 3 5 7
    front     2 4 6 8

    This is similar to the incomplete function MantidGeometry.add_double_pack.
    '''
    type_element = le.SubElement(instr.root, 'type', name=name)
    le.SubElement(type_element, 'properties')
    component = le.SubElement(type_element, 'component', type=tube_type)
    # z plane is centered in middle of detectors
    tube_z = (-0.5 * SEPARATION, 0.5 * SEPARATION)  # 2 rows back, front
    # x plane is centered between the leftmost and rightmost tubes
    x_offset = (-1.75 * SLIP, -1.25 * SLIP)
    tube_x = np.arange(4, dtype=float) * SLIP   # 4 tube in a row
    for i, x in enumerate(tube_x):
        for j, (z, slip) in enumerate(zip(tube_z, x_offset)):
            le.SubElement(component, 'location', name=f'{name}_{i}_{j}',
                          x=f'{x + slip:.5f}', z=f'{z:.5f}')


def addEmptyComponent(instr, type_name: str):
    '''type_name is reused as idlist name'''
    component = instr.addComponent(type_name=type_name, idlist=type_name)
    le.SubElement(component, "location")  # empty location tag


def addBankPosition(instr, bankname: str, componentname: str,
                    num_panels: int,
                    x_center: float, z_center: float, rot_y: float, rot_y_bank=None):
    '''
    for <location> the rotations happen before the translation

    x_center: center of the bank as a whole
    z_center: center of the bank as a whole
    rot_y: rotation of the bank around the positive y-axis
    '''
    bank = instr.makeTypeElement(bankname)

    if rot_y_bank is None:
        rot_y_bank = rot_y
    sine = np.sin(DEG_TO_RAD * rot_y_bank)
    cosine = np.cos(DEG_TO_RAD * rot_y_bank)
    # print('========================================')
    # print(bankname, 'sin={:.5f}'.format(sine), 'cos={:.5f}'.format(cosine))

    for i in range(num_panels):
        position_index = i - 0.5*(num_panels-1)
        x_panel = -1. * cosine * SLIP_PANEL * position_index + x_center
        z_panel = -1. * sine * SLIP_PANEL * position_index + z_center
        # print('x={:10.7f} z={:10.7f}'.format(x_panel, z_panel))
        panel = instr.addComponent(type_name=componentname, root=bank)
        # also has rot_x, rot_y, rot_z
        instr.addLocation(x=x_panel, y=0., z=z_panel, rot_y=rot_y, root=panel)


def addBankIds(instr, bankname: str, bank_offset: int, num_panels: int):
    ids = []
    for i in range(num_panels):
        panel_offset = bank_offset + PIXELS_PER_PANEL * i
        ids.extend([panel_offset, panel_offset + PIXELS_PER_EIGHTPACK - 1, None])
    instr.addDetectorIds(bankname, ids)


if __name__ == "__main__":
    inst_name = "VULCAN"
    xml_outfile = inst_name+"_Definition.xml"
    authors = ["Peter Peterson"]

    # boiler plate stuff
    instr = MantidGeom(inst_name,
                       comment="Created by " + ", ".join(authors),
                       valid_from="2020-01-01 00:00:01")
    instr.addComment("DEFAULTS")
    instr.addSnsDefaults()
    instr.addComment("SOURCE")
    instr.addModerator(L1)
    instr.addComment("SAMPLE")
    instr.addSamplePosition()

    # monitors
    instr.addComment("MONITORS")
    instr.addMonitors(distance=[4.83, 1.50], names=["monitor2", "monitor3"])

    # add empty components to hang everything off of
    addEmptyComponent(instr, type_name='bank1')  # left  (when facing downstream)
    addEmptyComponent(instr, type_name='bank2')  # right (when facing downstream)
    #addEmptyComponent(instr, type_name='bank3')
    #addEmptyComponent(instr, type_name='bank4')
    addEmptyComponent(instr, type_name='bank5')  # high angle
    #addEmptyComponent(instr, type_name='bank6')

    # #### DETECTORS GO HERE! ######################################
    positions = readPositions()  # TODO these are not used yet

    # all tubes (all banks) are same diameter with 512 pixels
    # bank1 is old bank 1-3 - has 20 8packs that are 1m long
    addBankPosition(instr, bankname='bank1', componentname='eightpack', num_panels=20,
                    x_center=90.39 * INCH_TO_METRE, z_center=0., rot_y=-90.)

    # bank2 is old bank 4-6 - has 20 8packs that are 1m long
    addBankPosition(instr, bankname='bank2', componentname='eightpack', num_panels=20,
                    x_center=-90.39 * INCH_TO_METRE, z_center=0., rot_y=90.)

    # bank3 (not installed) will have 18 8packs at 120deg
    #addBankPosition(instr, bankname='bank3', componentname='eightpack', num_panels=18,
    #                x_center=2*np.sin(np.deg2rad(120)), z_center=2*np.cos(np.deg2rad(120)),
    #                rot_y=180+120., rot_y_bank=-120)
    # bank4 (not installed) will have 18 8packs at 150deg
    #addBankPosition(instr, bankname='bank4', componentname='eightpack', num_panels=18,
    #                x_center=2.*np.sin(np.deg2rad(150.)), z_center=2.*np.cos(np.deg2rad(150.)),
    #                rot_y=180+150., rot_y_bank=-150)
    # bank5 is old bank 7 - has 9 8packs that are 0.7m long
    addBankPosition(instr, bankname='bank5', componentname='eightpackshort', num_panels=9,
                    x_center=2.*np.sin(np.deg2rad(-150.)), z_center=2.*np.cos(np.deg2rad(-150.)),
                    rot_y=180-150., rot_y_bank=150)
    # bank6 (not installed) will have 11 8packs at 60deg
    #addBankPosition(instr, bankname='bank6', componentname='eightpack', num_panels=11,
    #                x_center=2.*np.sin(np.deg2rad(-60.)), z_center=2.*np.cos(np.deg2rad(-60.)),
    #                rot_y=180-60., rot_y_bank=60)
    # bank9 (future plan and not part of the upgrade) at 210/-150deg

    # 8-pack is being called a "eightpack"
    # single tube

    # 1m x
    # old geometry had
    #  <radius val="0.012192"/>
    #  <height val="0.0093741875"/>
    # ppt cad diagram has 0.434in in plane
    #    and 0.323in front plane to back plane
    #    and from one module to the next is 0.460in

    # build up 8-pack with 1m tubes
    addEightPack(instr, 'eightpack', 'tube')
    instr.addComment('most banks are 512 pixels across {}m'.format(TUBE_LENGTH))
    instr.addPixelatedTube(name='tube', type_name='onepixel', num_pixels=TUBE_PIXELS,
                           tube_height=TUBE_LENGTH)
    instr.addCylinderPixel("onepixel", (0.0, 0.0, 0.0), (0.0, 1.0, 0.0),
                           TUBE_RADIUS, (TUBE_LENGTH/TUBE_PIXELS))

    # build up 8-pack with .7m "short"  tubes
    addEightPack(instr, 'eightpackshort', 'tubeshort')
    instr.addComment('bank 5 is 512 pixels across {}m'.format(TUBE_LENGTH_SHORT))
    instr.addPixelatedTube(name='tubeshort', type_name='onepixelshort', num_pixels=TUBE_PIXELS,
                           tube_height=TUBE_LENGTH_SHORT)
    instr.addCylinderPixel("onepixelshort", (0.0, 0.0, 0.0), (0.0, 1.0, 0.0),
                           TUBE_RADIUS, (TUBE_LENGTH_SHORT/TUBE_PIXELS))

    # detector ids
    instr.addComment("DETECTOR IDs - panel is an 8-pack")
    addBankIds(instr, 'bank1', bank_offset=0, num_panels=20)
    addBankIds(instr, 'bank2', bank_offset=PIXELS_PER_BANK, num_panels=20)
    #addBankIds(instr, 'bank3', bank_offset=2*PIXELS_PER_BANK, num_panels=18)
    #addBankIds(instr, 'bank4', bank_offset=3*PIXELS_PER_BANK, num_panels=18)
    addBankIds(instr, 'bank5', bank_offset=4*PIXELS_PER_BANK, num_panels=9)
    #addBankIds(instr, 'bank6', bank_offset=5*PIXELS_PER_BANK, num_panels=11)

    # shape for monitors
    instr.addComment(" Shape for Monitors")
    instr.addComment(" TODO: Update to real shape ")
    instr.addDummyMonitor(0.01, 0.03)

    # monitor ids
    instr.addComment("MONITOR IDs")
    instr.addMonitorIds([-2, -3])

    # write out the file
    instr.writeGeom(xml_outfile)
    # instr.showGeom()
