import sys
import datetime
import helper

# Definition of constants
HB3A_L1 = 2.

FourCircle_SETUP = {'L1': 2.0,
                    'L2': 0.3750,  # arm length
                    'PixelNumber': {256: (256, 256), 512: (512, 512)},
                    'PixelSize': {256: xx, 512: 0.0002265625},
                    }

ZEBRA_SETUP = {}

DEMAND_SETUP = {'L1': 2.0,
                'L2': 0.3750,
                'Panel Center': {1: (0, -Y), 2: (0, 0), 3: (0, Y)},
                'PixelNumber': {1: (512, 512), 2: (512, 512), 3: (512, 512)}
                }



class HB3AGeometry(helper.MantidGeom):
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
        super(HB3AGeometry, self).__init__(instname, comment, valid_from, valid_to)

        return

# END-DEF-HB3A


def generate_1_panel_idf(out_file_name):
    """ Generate the 1 panel (256 X 256) IDF valid to October 2018
    :return:
    """
    # rot-y --> 2theta
    # diffx --> deltax
    # diffy --> deltay

    # generate instrument geometry object
    instrument_name = 'HB3A'
    authors = ["Wenduo Zhou"]
    begin_date = '2015-01-01 00:00:01'
    end_date = '2018-10-20 23:59:59'

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
                        components=['bank1'])

    # define center bank
    hb3a.addComment('Define Centre Bank')
    hb3a.add_bank(name='bank1', component_name='square256detector',
                  x=2.0, y=0., z=0., rot=90)

    # 20 x 8 packs
    hb3a.addComment('256 x 256 pack')
    hb3a.angler_detector(name='square256detector', num_linear_pixel=256, tube_x=0.01)

    # write file
    hb3a.writeGeom(out_file_name)

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
        print ('Generate HB3A IDF: {} [number of panel [1, 3, zebra]'.format(argv[0]))
        sys.exit(0)

    is_zebra = argv[1].lower() == 'zebra'
    if is_zebra:
        generate_1_panel_idf(is_zebra)
    else:
        num_panel = int(argv[1])
        now = datetime.datetime.now()
        output_idf_name = 'HB3A_Definition_{:04}{:02}{:02}_{:02}{:02}.xml' \
                          ''.format(now.year, now.month, now.day,
                                    now.hour, now.minute)
        if num_panel == 1:
            generate_1_panel_idf(output_idf_name)
        elif num_panel:
            generate_3_panel_idf(output_idf_name)
        else:
            print ('Panel configuration {} is not supported'.format(argv[1]))
            sys.exit(-1)

    return


if __name__ == '__main__':
    main(sys.argv)


