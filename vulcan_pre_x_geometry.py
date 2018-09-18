#!/usr/bin/env python
# Note: This class shall be designed to be used in IPython notebook friendly
from helper import INCH_TO_METRE, DEG_TO_RAD, MantidGeom
from rectangle import Rectangle, Vector, getEuler, makeLocation
from sns_ncolumn import readFile
from math import cos, sin, radians, pi
import numpy as np

# size of the panels from original pixel sizes
x_extent = 154*.005
y_extent = 7*.0543

# number of pixels in each direction - v2
x_num2 = 154
y_num2 = 7

# primary flight path - negative b/c it is upstream
L1 = -60.0

def readPositions(filename):
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
            banks[bank] = (column, Rectangle(four, one, two, three, tolerance_len=0.006))

    return banks


def generate_tube_pixels():
    """ generate pixel XML in IDF tube in 8-pack

    Example:
      <location y="-0.59526090625" name="pixel1"/>
      ... ...  
      <location y="0.59526090625" name="pixel128"/>
    """
    delta_y = 0.77216 / 256.
    y_start = -0.77216 * 0.5 + 0.5 * delta_y

    tube_def = ''
    for index in range(256):
        tube_def += '<location y="{0:.10f}" name="pixel{1}"/>\n'.format((y_start + delta_y * index), index+1)

    print tube_def
    print delta_y

    return


class WestEastGroup(object):
    """
    """
    def __init__(self):
        """
        """
        return

    def _setup_banks(self):
        """
        """
        return

    def export_idf_str(self):
        """
        """
        return ''


class EightPacksGroup(object):
    """
    """
    pixel_size['x'] = 1.  # meter
    pixel_size['y'] = 1.2 # meter
    def __init__(self, num_8packs, start_pid, position, twotheta):
        """
        """

        return

    def _setup_8packs(self):
        """
        """

        return

    def export_idf_str(self):
        """
        """

        return ''


class EightPack(object):
    """
    """
    def __init__(self, start_pid, position, twotheta):
        """
        """
        return

    def info(self):
        """
        """
        return

    def form_string(self):
        """
        """
        return


class GenerateIDFPreVulcanX(object):
    """
    """
    def __init__(self, begin_date, end_date):
        """
        """
        return

    def create_idf(self, user_name=None):
        """
        """

        return

    def help(self):
        """
        """
        print ('What do you want to do?')

        return

    def print_info(self):
        """
        """
        print ('whatever')

        return




if __name__ == "__main__":

    generate_tube_pixels()

    exit(1) 

    inst_name = "VULCAN"
    xml_outfile = inst_name+"_Definition.xml"
    authors = ["Peter Peterson",
               "Stuart Campbell",
               "Vickie Lynch",
               "Janik Zikovsky"]

    # boiler plate stuff
    instr = MantidGeom(inst_name,
                       comment="Created by " + ", ".join(authors),
                       valid_from="2017-05-01 00:00:01")
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
    banks = readPositions("SNS/POWGEN/PG3_geom_2017.csv")

    # create columns
    columns = set()
    for name in banks.keys():
        column, _ =  banks[name]
        columns.add(column)
    columns = list(columns)
    columns.sort()
    for name in columns:
        group = instr.addComponent(str(name))

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

    '''
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
    '''

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
