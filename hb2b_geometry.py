import sys
import datetime
import helper

# Definition of constants
HB3A_L1 = 2.


HB2B_SETUP = {'L1': 2.678898,
              'L2': 0.95,  # arm length
              'PixelNumber': {'1K': (1024, 1024), '2K': (2048, 2048)},
              'PixelSize': {'1K': 0.00029296875, '2K': 0.00029296875*0.5}
              }


HZB_SETUP = {'L1': 2.678898,
             'L2': 1.13268,  # arm length
             'PixelNumber': {'1K': (1024, 1024), '2K': (2048, 2048), '256': (256, 256)},
             'PixelSize': {'1K': 0.00029296875, '2K': 0.00029296875*0.5, '256': 0.00029296875*4}
             }

XRAY_SETUP = {'L1': 2.678898,
              'L2': 0.416,  # arm length
              'PixelNumber': {'1K': (1024, 1024), '2K': (2048, 2048)},
              'PixelSize': {'1K': 0.0004000, '2K': 0.0004000*0.5}
              }


class ResidualStressGeometry(helper.MantidGeom):
    """
    HB3A geometry extended from MantidGeom
    """
    def __init__(self, instname, comment=None, valid_from=None, valid_to=None):
        """
        initialization
        :param instname: name of instrument
        :param comment: comment
        :param valid_from: beginning date
        :param valid_to: end date
        """
        super(ResidualStressGeometry, self).__init__(instname, comment, valid_from, valid_to)

        return

    def add_rectangular_detector(self, x_start, x_step, x_pixels,
                                 y_start, y_step, y_pixels,
                                 pixel_size_x, pixel_size_y, pixel_size_z):
        """ Add a rectangular detector
        """
        # add detector panel
        self.addRectangularDetector(name='shiftpanel', type='pixel',
                                    xstart='{}'.format(x_start), xstep='{}'.format(x_step),
                                    xpixels='{}'.format(x_pixels),
                                    ystart='{}'.format(y_start), ystep='{}'.format(y_step),
                                    ypixels='{}'.format(y_pixels))

        # add pixels
        self.addCuboidPixel(name='pixel', shape_id='pixel-shape',
                            lfb_pt=(pixel_size_x*0.5, -pixel_size_y*0.5, 0),  # left-front-bottom
                            lft_pt=(pixel_size_x*0.5, pixel_size_y*0.5, 0),  # left-front-top
                            lbb_pt=(pixel_size_x*0.5, -pixel_size_y*0.5, -pixel_size_z),  # left-back-bottom
                            rfb_pt=(-pixel_size_x*0.5, -pixel_size_y*0.5, 0)  # right-front-bottom
                            )

        return

# END-DEF-HB3A


def generate_1bank_2d_idf(instrument_name, geom_setup_dict, pixel_setup, output_idf_name):
    """ Generate the general HB2B (or similar X-Ray) IDF file from 2018.12.01
    :param instrument_name:
    :param geom_setup_dict:
    :param pixel_setup:
    :param output_idf_name:
    :return:
    """
    # generate instrument geometry object
    authors = ["Wenduo Zhou"]
    begin_date = '2018-12-01 00:00:01'
    end_date = '2100-10-20 23:59:59'

    # boiler plate stuff
    hb2b = ResidualStressGeometry(instrument_name,
                                  comment="Created by " + ", ".join(authors),
                                  valid_from=begin_date,
                                  valid_to=end_date)

    # TODO/FIXME - NO HFIR Default
    # hb2b.addComment('DEFAULTS')
    # hb2b.addHfirDefaults()

    # source
    hb2b.addComment("SOURCE")
    hb2b.addModerator(geom_setup_dict['L1'])
    # sample
    hb2b.addComment("SAMPLE")
    hb2b.addSamplePosition()

    # TODO/FIXME - NO Default
    # monitor
    # hb2b.addComment("MONITORS")
    # hb2b.add_monitor_type()

    # Build 'arm'/panel/shiftpanel
    hb2b.addComment("PANEL")

    # define arm - component
    pixel_row_count, pixel_column_count = geom_setup_dict['PixelNumber'][pixel_setup]
    arm_loc_dict = dict()
    arm_loc_dict['r-position'] = {'value': 0.0}
    arm_loc_dict['t-position'] = {'value': 0.0}
    arm_loc_dict['p-position'] = {'value': 0.0}
    arm_loc_dict['roty'] = {'logfile': 'value+0.0', 'id': '2theta'}  # roty works as 2theta with experiment
    arm_node = hb2b.add_component(type_name='arm', idfillbyfirst='x', idstart=1, idstepbyrow=pixel_column_count)
    arm_loc_node = hb2b.add_location('bank1', arm_node, arm_loc_dict)

    # define type: arm
    arm_type_node = hb2b.add_component_type(type_name='arm')

    # define component panel under type arm
    arm_loc_dict = {'z': {'logfile': 'value+{}'.format(geom_setup_dict['L2']), 'id': 'cal::arm'},
                    'rotx': {'logfile': 'value+0.0', 'id': 'cal::flip'},
                    'roty': {'logfile': 'value+0.0', 'id': 'cal::roty'},
                    'rotz': {'logfile': 'value+0.0', 'id': 'cal::spin'},
                    }
    arm_node = hb2b.add_component(type_name='panel', idfillbyfirst=None, idstart=None,
                                  idstepbyrow=None, root=arm_type_node)
    hb2b.add_location(None, arm_node, arm_loc_dict)

    # add panel
    panel_loc_dict = {'x': {'logfile': 'value', 'id': 'cal::deltax'},
                      'y': {'logfile': 'value', 'id': 'cal::deltay'}}
    panel_type_node = hb2b.add_component_type('panel')
    panel_node = hb2b.add_component(type_name='shiftpanel', idfillbyfirst=None, idstart=None,
                                    idstepbyrow=None, root=panel_type_node)
    hb2b.add_location(None, panel_node, panel_loc_dict)

    # generate rectangular detector based on 'shiftpanel'
    pixel_size_x = pixel_size_y = geom_setup_dict['PixelSize'][pixel_setup]
    x_start = (float(pixel_column_count)*0.5 - 0.5) * pixel_size_x
    x_step = - pixel_size_x
    y_start = -(float(pixel_row_count)*0.5 - 0.5) * pixel_size_y
    y_step = pixel_size_y
    hb2b.add_rectangular_detector(x_start=x_start, x_step=x_step, x_pixels=pixel_column_count,
                                  y_start=y_start, y_step=y_step, y_pixels=pixel_row_count,
                                  pixel_size_x=pixel_size_x, pixel_size_y=pixel_size_y,
                                  pixel_size_z=0.0001)

    hb2b.write_terminal()
    hb2b.writeGeom(output_idf_name)

    return


def generate_2d_configure(instrument_name, geom_setup_dict, pixel_setup, output_pyrs_name):
    """
    # ASCII instrument configuration file for 2K detector (2048 x 2048)

    arm = 0.416
    rows = 2048
    columns = 2048
    pixel_size_x = 0.0002
    pixel_size_y = 0.0002
    """
    # TODO - TONIGHT 0 - Also output ...

    return


def main(argv):
    """ Main
    :param argv:
    :return:
    """
    if len(argv) < 3:
        print ('Generate HB2B IDF: {} [hb2b [xray, hzb]] [1k [2k]]'.format(argv[0]))
        sys.exit(0)

    instrument = argv[1]
    if instrument == 'hb2b':
        geom_setup_dict = HB2B_SETUP
        instrument_name = 'HB2B'
    elif instrument == 'xray':
        geom_setup_dict = XRAY_SETUP
        instrument_name = 'XRAY'
    elif instrument == 'hzb':
        geom_setup_dict = HZB_SETUP
        instrument_name = 'HZB'
    else:
        print ('[ERROR] Instrument {} is not supported.'.format(instrument))
        sys.exit(-1)

    # about the number of pixels setup
    pixel_setup = argv[2]
    if pixel_setup == '1k':
        pixel_setup = '1K'
    elif pixel_setup == '2k':
        pixel_setup = '2K'
    else:
        print ('[ERROR] Pixel setup {} is not supported.'.format(pixel_setup))

    # create instrument
    now = datetime.datetime.now()

    output_idf_name = '{}_Definition_{:04}{:02}{:02}_{:02}{:02}.xml' \
                      ''.format(instrument_name, now.year, now.month, now.day,
                                now.hour, now.minute)
    generate_1bank_2d_idf(instrument_name, geom_setup_dict, pixel_setup, output_idf_name)
    generate_2d_configure(instrument_name, geom_setup_dict, pixel_setup, output_config_name)

    return


if __name__ == '__main__':
    main(sys.argv)
