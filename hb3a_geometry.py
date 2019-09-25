import sys
import datetime
import helper

# Definition of constants
HB3A_L1 = 2.

# TODO - Need to separate FourCircle_256_SETUP and FourCircle_512_SETUP
# TODO - Unify the dictioanry layout!
FourCircle_256_SETUP = {'L1': 2.0,
                        'L2': 0.3750,  # arm length
                        'PixelNumber': {1: (256, 256)},  # bank: (row, col)
                        'PixelSize': {1: 0.0001984375},  # bank: pixel size
                        'Panel Center': {1: (0, 0)}
                        }

FourCircle_512_SETUP = {'L1': 2.0,
                        'L2': 0.3750,  # arm length
                        'PixelNumber': {1: (512, 512)},  # bank: (row, col)
                        'PixelSize': {1: 0.0002265625},
                        'Panel Center': {1: (0, 0)}
                        }

ZEBRA_SETUP = {'L1': 2.0,
               'L2': 0.3750,  # arm length
               'PixelNumber': {1: (256, 256)},
               'PixelSize': {1: 0.01234567}}

Y = 0.1234567
DEMAND_SETUP = {'L1': 2.0,
                'L2': 0.3750,
                'Panel Center': {1: (0, -Y), 2: (0, 0), 3: (0, Y)},
                'PixelNumber': {1: (512, 512), 2: (512, 512), 3: (512, 512)},
                'PixelSize': {1: 0.0002265625, 2: 0.0002265625, 3: 0.0002265625}
                }


class DemandGeometry(helper.MantidGeom):
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
        super(DemandGeometry, self).__init__(instname, comment, valid_from, valid_to)

        return

    def add_panel(self, bank_id, geom_setup_dict, cal_shift_x='diffx', cal_shift_y='diffy',
                  cal_rotx='cal::flip', cal_roty='cal::roty',
                  cal_rotz='cal::spin'):
        """ Add 1 2D detector panel
        Code is somehow shared with hb2b_geometry.generate_1bank_2d_idf
        For Mantid IDF, the logic of applying shift to a detector is from bottom to top as
        - shift X and Y
        - shift Z, rotX, rotY, rotZ
        - shift 2theta
        In the same level, rotation shift is applied in a higher priority than linear shift
        Args:
            bank_id:
            geom_setup_dict:
            cal_shift_x: String, name of calibration shift along X-axis
            cal_shift_y:
            cal_rotx:
            cal_roty:
            cal_rotz:

        Returns:
        None
        """
        # Define arm component - component with roty as 2theta
        pixel_row_count, pixel_column_count = geom_setup_dict['PixelNumber'][bank_id]
        arm_loc_dict = dict()
        arm_loc_dict['r-position'] = {'value': 0.0}
        arm_loc_dict['t-position'] = {'value': 0.0}
        arm_loc_dict['p-position'] = {'value': 0.0}
        arm_loc_dict['roty'] = {'logfile': 'value+0.0', 'id': '2theta'}  # roty works as 2theta with experiment
        arm_node = self.add_component(type_name='arm', idfillbyfirst='x', idstart=1,
                                      idstepbyrow=pixel_column_count)
        self.add_location('bank{}'.format(bank_id), arm_node, arm_loc_dict)

        # Define arm node type: arm
        arm_type_node = self.add_component_type(type_name='arm')

        # Define component panel installed on the arm
        # rotation along x-, y- and z- axis and shift along arm will be defined from log
        arm_loc_dict = {'z': {'logfile': 'value+{}'.format(geom_setup_dict['L2']), 'id': 'cal::arm'},
                        'rotx': {'logfile': 'value+0.0', 'id': cal_rotx},
                        'roty': {'logfile': 'value+0.0', 'id': cal_roty},
                        'rotz': {'logfile': 'value+0.0', 'id': cal_rotz},
                        }
        # Add component-panel to arm-type-node
        panel_node = self.add_component(type_name='panel', idfillbyfirst=None, idstart=None,
                                        idstepbyrow=None, root=arm_type_node)
        # Add location to panel node
        self.add_location(None, panel_node, arm_loc_dict)

        # Add another layer: shift-panel on to panel for shift in X- and Y- direction
        center_y = geom_setup_dict['Panel Center'][bank_id]
        panel_loc_dict = {'x': {'logfile': 'value', 'id': cal_shift_x},
                          'y': {'logfile': '{}+value'.format(center_y), 'id': cal_shift_y}}
        panel_type_node = self.add_component_type('panel')
        shift_panel_node = self.add_component(type_name='shiftpanel', idfillbyfirst=None, idstart=None,
                                              idstepbyrow=None, root=panel_type_node)
        self.add_location(None, shift_panel_node, panel_loc_dict)

        return

# END-DEF-HB3A


def generate_1_panel_idf(is_zebra, idf_name, config_name, linear_pixel_size):
    """ Generate the 1 panel (256 X 256) IDF valid to October 2018
    :param is_zebra:
    :param idf_name:
    :param config_name:
    :param linear_pixel_size:
    :return:
    """
    if is_zebra:
        instrument_name = 'ZEBRA'
        geom_setup_dict = ZEBRA_SETUP
    else:
        instrument_name = 'HB3A'
        if linear_pixel_size == 256:
            geom_setup_dict = FourCircle_256_SETUP
        elif linear_pixel_size == 512:
            geom_setup_dict = FourCircle_512_SETUP
        else:
            raise RuntimeError('HB3A-1-Panel with {0} x {0} does not exist'.format(linear_pixel_size))

    # generate instrument geometry object
    authors = ["Wenduo Zhou"]
    begin_date = '2018-12-01 00:00:01'
    end_date = '2100-10-20 23:59:59'

    # boiler plate stuff
    scx_instrument = DemandGeometry(instrument_name,
                                    comment="Created by " + ", ".join(authors),
                                    valid_from=begin_date,
                                    valid_to=end_date)

    # source
    scx_instrument.addComment("SOURCE")
    scx_instrument.addModerator(geom_setup_dict['L1'])
    # sample
    scx_instrument.addComment("SAMPLE")
    scx_instrument.addSamplePosition()

    # Build 'arm'/panel/shiftpanel
    scx_instrument.addComment("PANEL")
    scx_instrument.add_panel(bank_id=1, geom_setup_dict=geom_setup_dict,
                             cal_shift_x='diffx', cal_shift_y='diffy')

    # Generate rectangular detector based on 'shiftpanel'
    # TODO - refactor this to a method (not ASAP)
    pixel_size_x = pixel_size_y = geom_setup_dict['PixelSize'][1]
    pixel_row_count, pixel_column_count = geom_setup_dict['PixelNumber'][1]
    x_start = (float(pixel_column_count)*0.5 - 0.5) * pixel_size_x
    x_step = - pixel_size_x
    y_start = -(float(pixel_row_count)*0.5 - 0.5) * pixel_size_y
    y_step = pixel_size_y
    scx_instrument.add_rectangular_detector(x_start=x_start, x_step=x_step, x_pixels=pixel_column_count,
                                            y_start=y_start, y_step=y_step, y_pixels=pixel_row_count,
                                            pixel_size_x=pixel_size_x, pixel_size_y=pixel_size_y,
                                            pixel_size_z=0.0001)  # pixel size Z is not concerned

    scx_instrument.write_terminal()
    scx_instrument.writeGeom(idf_name)

    return


def generate_3_panel_idf(out_file_name):
    """
    generate 3 panel (3 x 4 x 256 x 256) instrument definition for 2018 October
    upgrade
    :return:
    """
    # generate instrument geometry object
    instrument_name = 'HB3A'
    authors = ["Wenduo Zhou"]
    begin_date = '2018-10-20 23:59:59'
    end_date = '3018-10-20 23:59:59'

    # boiler plate stuff
    hb3a = DemandGeometry(instrument_name,
                          comment="Created by " + ", ".join(authors),
                          valid_from=begin_date,
                          valid_to=end_date)

    # source
    hb3a.addComment("SOURCE")
    hb3a.addModerator(HB3A_L1)
    # sample
    hb3a.addComment("SAMPLE")
    hb3a.addSamplePosition()
    # monitor: No monitor
    # hb3a.addComment("MONITORS")
    # hb3a.add_monitor_type()
    # self._vulcan.addMonitors(distance=[-1.5077], names=["monitor1"])

    # Build 'arm'/panel/shiftpanel
    # TODO FIXME - shall be: 1 arm, 3 panel
    hb3a.addComment("PANEL Lower")
    hb3a.add_panel(bank_id=1, geom_setup_dict=DEMAND_SETUP,
                   cal_shift_x='diffx1', cal_shift_y='diffy1')

    hb3a.addComment("PANEL Middle")
    hb3a.add_panel(bank_id=2, geom_setup_dict=DEMAND_SETUP,
                   cal_shift_x='diffx2', cal_shift_y='diffy2')

    hb3a.addComment("PANEL Upper")
    hb3a.add_panel(bank_id=3, geom_setup_dict=DEMAND_SETUP,
                   cal_shift_x='diffx3', cal_shift_y='diffy3')

    # Generate rectangular detector based on 'shiftpanel'
    # TODO - refactor this to a method (not ASAP)
    pixel_size_x = pixel_size_y = DEMAND_SETUP['PixelSize'][1]
    pixel_row_count, pixel_column_count = DEMAND_SETUP['PixelNumber'][1]
    x_start = (float(pixel_column_count)*0.5 - 0.5) * pixel_size_x
    x_step = - pixel_size_x
    y_start = -(float(pixel_row_count)*0.5 - 0.5) * pixel_size_y
    y_step = pixel_size_y
    hb3a.add_rectangular_detector(x_start=x_start, x_step=x_step, x_pixels=pixel_column_count,
                                  y_start=y_start, y_step=y_step, y_pixels=pixel_row_count,
                                  pixel_size_x=pixel_size_x, pixel_size_y=pixel_size_y,
                                  pixel_size_z=0.0001)  # pixel size Z is not concerned

    # Write out HB3A
    hb3a.write_terminal()
    hb3a.writeGeom(out_file_name)

    return


def main(argv):
    """ Main
    :param argv:
    :return:
    """
    if len(argv) < 2:
        print ('Generate HB3A IDF: {} [number of panel [1, 3, zebra] [pixel size (default)]'.format(argv[0]))
        sys.exit(0)
    else:
        is_zebra = argv[1].lower() == 'zebra'
        if is_zebra:
            instrument_name = 'ZEBRA'
        else:
            instrument_name = 'HB3A'

    # about output file
    now = datetime.datetime.now()
    output_idf_name = '{}_Definition_{:04}{:02}{:02}_{:02}{:02}.xml' \
                      ''.format(instrument_name, now.year, now.month, now.day,
                                now.hour, now.minute)
    instrument_config_name = '{}_Definition_{:04}{:02}{:02}_{:02}{:02}.txt' \
                             ''.format(instrument_name, now.year, now.month, now.day, now.hour, now.minute)

    if is_zebra:
        generate_1_panel_idf(is_zebra, output_idf_name, instrument_config_name, None)
    else:
        num_panel = int(argv[1])

        if num_panel == 1:
            # 1 panel case: need to find out if it is 256 x 256
            if len(argv) == 3:
                linear_pixel_number = int(argv[2])
                if linear_pixel_number not in [256, 512]:
                    print ('[ERROR] HB3A 1-panel only supports 256(x256) and 512(x512) but not {}(x{})'
                           ''.format(linear_pixel_number, linear_pixel_number))

            generate_1_panel_idf(is_zebra, output_idf_name, instrument_config_name, linear_pixel_number)
        elif num_panel == 3:
            # 3 panels: DEMAND
            generate_3_panel_idf(output_idf_name)
        else:
            # Non-support
            print ('Panel configuration {} is not supported'.format(argv[1]))
            sys.exit(-1)
    # END-IF-ELSE

    print ('[REPORT] {} and {} are generated for {}'.format(output_idf_name, instrument_config_name, instrument_name))

    return


if __name__ == '__main__':
    main(sys.argv)


