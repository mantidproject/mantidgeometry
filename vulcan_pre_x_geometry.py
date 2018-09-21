#!/usr/bin/env python
"""
TODO LIST:

1. test whether idlist and idstart can be put to eight packs (manually manipulate)
2. test create group with 8 packs


"""


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
# x_num2 = 154
# y_num2 = 7

# primary flight path - negative b/c it is upstream



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


class WestEastBank(object):
    """ Single module for pre-VULCAN-X west/east bank with 154 x 7 pixels
    """
    NUM_ROWS = 7
    NUM_COLUMNS = 154



class WestEastPixel(object):
    """
    Pixel information (old) west/east bank
    """
    size_x = 0.005  # meter
    size_y = 0.543  # meter

    def __init__(self):
        """
        initialization
        """
        return

    @property
    def dimension(self):
        """
        dimension of the pixels
        :return:  dimension in x and y respectively
        """
        return WestEastPixel.size_x, WestEastPixel.size_y


class EightPacksGroup(object):
    """
    """
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


class EightPackTube(object):
    """
    Class to describe a tube that consists of an 8-packs
    :param object:
    :return:
    """
    def __init__(self, num_pixels):
        """ Initialization
        :param num_pixels:
        :param self:
        :return:
        """
        self._num_pixels = num_pixels

        self._pixels_dict = self._create_pixels()

        return

    def _create_pixels(self):
        """
        create pixels with location
        :return:
        """
        # y_start = -0.77216 * 0.5 + 0.5 * pixel_y_length
        # tube_def += '<location y="{0:.10f}" name="pixel{1}"/>\n'.format((y_start + pixel_y_length * index), index + 1)

        pixel_x_length, pixel_y_length = EightPackPixel.dimension
        if self._num_pixels % 2 == 0:
            # event number: start from the first pixel's center
            y_start = - self._num_pixels / 2 * pixel_y_length + 0.5 * pixel_y_length
        else:
            # odd number: from center of middle pixel to first pixel's center
            y_start = - self._num_pixels / 2 * pixel_y_length
        # END-IF

        # set up the pixels
        tube_pixel_dict = dict()
        for pixel_id in range(1, self._num_pixels + 1):
            pixel_pos_i = y_start + (pixel_id - 1) * pixel_y_length
            pixel_i = EightPackPixel(pixel_id, pixel_pos_i)
            tube_pixel_dict[pixel_id] = pixel_i
        # END-FOR

        return tube_pixel_dict

    def generate_idf(self):
        """ generate pixel XML in IDF tube in 8-pack

        Example:
          <location y="-0.59526090625" name="pixel1"/>
          ... ...
          <location y="0.59526090625" name="pixel128"/>
        """
        tube_def = ''
        for pixel_id in sorted(self._pixels_dict.keys()):
            tube_def += '<location y="{0:.10f}" name="pixel{1}"/>\n'.format(self._pixels_dict[pixel_id].pos_y, pixel_id)
        # END-FOR

        return tube_def


class EightPackPixel(object):
    """
    class to describe a pixel in a detector of 8 packs
    """
    size_x = 0.77216 / 256.  # meter
    size_y = 0.77216 / 256.  # meter

    def __init__(self, pixel_id, loc_y):
        """ initialization
        :param pixel_id: in-tube pixel ID
        :param loc_y: in-tube pixel location (Y)
        """
        self._pixel_id = pixel_id
        self._location_y = loc_y

        return

    @property
    def dimension(self):
        """
        dimension of the pixels (size x and size y)
        :return:
        """
        return EightPackPixel.size_x, EightPackPixel.size_y

    @property
    def pixel_id(self):
        """
        In-tube pixel ID
        :return:
        """
        return self.pixel_id

    @property
    def pos_y(self):
        """
        In-tube pixel position Y
        :return:
        """
        return self._location_y

# END-CLASS(EightPackPixel)


class GenerateIDFPreVulcanX(object):
    """
    """
    VULCAN_L1 = 43.0   # meter

    def __init__(self, begin_date, end_date):
        """ Initialization
        :param begin_date: beginning date of this instrument: "2017-05-01 00:00:01"
        :param end_date:
        """
        self._instrument_name = 'VULCAN'

        authors = ["Wenduo Zhou"]

        # boiler plate stuff
        self._vulcan = MantidGeom(inst_name,
                                  comment="Created by " + ", ".join(authors),
                                  valid_from=begin_date)

        self._vulcan.addComment("DEFAULTS")
        self._vulcan.addSnsDefaults()

        return

    def create_instrument(self):
        """
        create the instrument
        :return:
        """
        # source
        self._vulcan.addComment("SOURCE")
        self._vulcan.addModerator(GenerateIDFPreVulcanX.VULCAN_L1)
        # sample
        self._vulcan.addComment("SAMPLE")
        self._vulcan.addSamplePosition()
        # monitor
        self._vulcan.addComment("MONITORS")
        self._vulcan.addMonitors(distance=[-1.5077], names=["monitor1"])


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
    # authors = ["Peter Peterson",
    #            "Stuart Campbell",
    #            "Vickie Lynch",
    #            "Janik Zikovsky"]
    #
    # # boiler plate stuff
    # instr = MantidGeom(inst_name,
    #                    comment="Created by " + ", ".join(authors),
    #                    valid_from="2017-05-01 00:00:01")
    # instr.addComment("DEFAULTS")
    # instr.addSnsDefaults()
    # instr.addComment("SOURCE")
    # instr.addModerator(L1)
    # instr.addComment("SAMPLE")
    # instr.addSamplePosition()

    # monitors

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
