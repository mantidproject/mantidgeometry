import sys
import datetime
import helper

# Definition of constants
HB3A_L1 = 2.

# TODO - Need to separate FourCircle_256_SETUP and FourCircle_512_SETUP
# TODO - Unify the dictioanry layout!
FourCircle_SETUP = {'L1': 2.0,
                    'L2': 0.3750,  # arm length
                    'PixelNumber': {1: (256, 256)},
                    'PixelSize': {256: xx, 512: 0.0002265625},
                    'Panel Center': {1: (0, -Y), 2: (0, 0), 3: (0, Y)},
                    }

ZEBRA_SETUP = {'L1': 2.0,
               'L2': 0.3750,  # arm length
               'PixelNumber': {256: (256, 256)},
               'PixelSize': {256: xx}}

DEMAND_SETUP = {'L1': 2.0,
                'L2': 0.3750,
                'Panel Center': {1: (0, -Y), 2: (0, 0), 3: (0, Y)},
                'PixelNumber': {1: (512, 512), 2: (512, 512), 3: (512, 512)}
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
        # define arm - component
        pixel_row_count, pixel_column_count = geom_setup_dict['PixelNumber'][linear_pixel_size]
        arm_loc_dict = dict()
        arm_loc_dict['r-position'] = {'value': 0.0}
        arm_loc_dict['t-position'] = {'value': 0.0}
        arm_loc_dict['p-position'] = {'value': 0.0}
        arm_loc_dict['roty'] = {'logfile': 'value+0.0', 'id': '2theta'}  # roty works as 2theta with experiment
        arm_node = self.add_component(type_name='arm', idfillbyfirst='x', idstart=1,
                                      idstepbyrow=pixel_column_count)
        arm_loc_node = self.add_location(bank_id, arm_node, arm_loc_dict)

        # define type: arm
        arm_type_node = self.add_component_type(type_name='arm')

        # define component panel under type arm
        arm_loc_dict = {'z': {'logfile': 'value+{}'.format(geom_setup_dict['L2']), 'id': 'cal::arm'},
                        'rotx': {'logfile': 'value+0.0', 'id': cal_rotx},
                        'roty': {'logfile': 'value+0.0', 'id': cal_roty},
                        'rotz': {'logfile': 'value+0.0', 'id': cal_rotz},
                        }
        arm_node = self.add_component(type_name='panel', idfillbyfirst=None, idstart=None,
                                      idstepbyrow=None, root=arm_type_node)
        self.add_location(None, arm_node, arm_loc_dict)

        # add panel
        center_y = geom_setup_dict['Panel Center'][]
        panel_loc_dict = {'x': {'logfile': 'value', 'id': cal_shift_x},
                          'y': {'logfile': '{}+value'.format(center_y), 'id': cal_shift_y}}
        panel_type_node = self.add_component_type('panel')
        panel_node = self.add_component(type_name='shiftpanel', idfillbyfirst=None, idstart=None,
                                        idstepbyrow=None, root=panel_type_node)
        scx_instrument.add_location(None, panel_node, panel_loc_dict)

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
        geom_setup_dict = FourCircle_SETUP

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

    scx_instrument.add_panel()

    # generate rectangular detector based on 'shiftpanel'
    pixel_size_x = pixel_size_y = geom_setup_dict['PixelSize'][linear_pixel_size]
    x_start = (float(pixel_column_count)*0.5 - 0.5) * pixel_size_x
    x_step = - pixel_size_x
    y_start = -(float(pixel_row_count)*0.5 - 0.5) * pixel_size_y
    y_step = pixel_size_y
    scx_instrument.add_rectangular_detector(x_start=x_start, x_step=x_step, x_pixels=pixel_column_count,
                                            y_start=y_start, y_step=y_step, y_pixels=pixel_row_count,
                                            pixel_size_x=pixel_size_x, pixel_size_y=pixel_size_y,
                                            pixel_size_z=0.0001)

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
    hb3a = HB3AGeometry(instrument_name,
                        comment="Created by " + ", ".join(authors),
                        valid_from=begin_date,
                        valid_to=end_date)

    hb3a.addComment('DEFAULTS')
    hb3a.addHfirDefaults()

    # source
    hb3a.addComment("SOURCE")
    hb3a.addModerator(HB3A_L1)
    # sample
    hb3a.addComment("SAMPLE")
    hb3a.addSamplePosition()
    # monitor
    hb3a.addComment("MONITORS")
    hb3a.add_monitor_type()
    # self._vulcan.addMonitors(distance=[-1.5077], names=["monitor1"])

    # add detectors
    hb3a.addComment('Define detector banks')
    hb3a.addComponent(type_name='detectors', idlist='detectors')
    # define detector type
    hb3a.add_banks_type(name='detectors',
                        components=['bank1', 'bank2', 'bank3'])

    # define center bank
    hb3a.addComment('Define Centre Bank')
    hb3a.add_bank(name='bank3', component_name='square256detector',
                  x=2.0, y=0., z=0., rot=90)

    # define upper bank
    hb3a.addComment('Define Upper Bank')
    hb3a.add_bank(name='bank3', component_name='square256detector',
                  x=2.0, y=1., z=0., rot=90)

    # define lower bank
    hb3a.addComment('Define Lower Bank')
    hb3a.add_bank(name='bank1', component_name='square256detector',
                  x=2.0, y=-1., z=0., rot=90)

    # 512 x 512 pack
    hb3a.addComment('512 x 512 pack')
    hb3a.angler_detector(name='square256detector', num_linear_pixel=512, tube_x=0.01)

    #
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
        elif num_panel:
            generate_3_panel_idf(output_idf_name, instrument_config_name)
        else:
            print ('Panel configuration {} is not supported'.format(argv[1]))
            sys.exit(-1)
    # END-IF-ELSE

    print ('[REPORT] {} and {} are generated for {}'.format(output_idf_name, instrument_config_name, instrument_name))

    return


if __name__ == '__main__':
    main(sys.argv)


