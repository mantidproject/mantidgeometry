# This is the geometry/IDF generator for VULCAN-X
from vulcan_geometry import VulcanGeomIDF
import math


# Define pixel ID gap between 2 adjacent 8 packs in a same group
GAP = 10
VULCAN_L1 = 43.

VULCAN_X_L2 = {'bank1': 2.3,
               'bank2': 2.3,
               'bank3': 2.07,
               'bank4': 2.07,
               'bank5': 2.07,
               'bank6': 2.53}

VULCAN_X_Phase1_Setup = {'bank1': (-90., 20, 512),
                         'bank2': (90., 20, 512),
                         'bank5': (150, 9, 256)}

VULCAN_X_Phase2_Setup = {'bank1': (-90., 20, 512),
                         'bank2': (90., 20, 512),
                         'bank3': (120., 18, 512),
                         'bank4': (150., 18, 512),
                         'bank5': (-155., 9, 256),
                         'bank6': (-65., 11, 256)}

PIXEL_WIDTH = 0.004145
PIXEL_HEIGHT = 0.00301625

PIXEL_FLAT_256_WIDTH = 0.004145
PIXEL_FLAT_256_HEIGHT = 0.00301625
PIXEL_FLAT_256_RADIUS = 0.004145 * 0.5

PIXEL_FLAT_512_WIDTH = 1.09982 * 0.01 * 0.5  # 2 front tube distance is 0.433 inch (1.09982 cm)
PIXEL_FLAT_512_HEIGHT = 1./512.
PIXEL_FLAT_512_RADIUS = 1.09982 * 0.01 * 0.5 / 2.


class VulcanXIDFGenerator(object):
    """
    main generator for VULCAN IDF
    """
    # value-tuple: 2theta, detector type, number of eight packs, starting PID, gap PID, pixels in a tube
    DetectorInfoDict = {'Phase 1': {'bank1': (-90., 'eightpack', 20, GAP, 512),
                                    'bank2': (90., 'eightpack', 20, GAP, 512),
                                    'bank5': (150., 'eightpack',  0, 256)},
                        'Phase Final': {'bank1':  (-90., 'eightpack', 20, GAP, 512),
                                        'bank2': (90., 'eightpack', 20, GAP, 512),
                                        'bank3': (150., 'eightpack',  GAP, 256)}
                        }

    def __init__(self, from_date, exp_date):
        """
        initialization to generate the VULCAN-X
        """

        return

    def generate_idf(self, idf_xml_name):
        """

        :param idf_xml_name:
        :return:
        """

        self._vulcan = VulcanGeomIDF('VULCAN', comment, self._from_date, self._exp_date)

        # add source, sample
        self._vulcan.addSamplePosition()
        self._vulcan.addModerator(-VULCAN_L1)



        return

    def export_idf(self, idf_xml_name):
        """

        Args:
            idf_xml_name:

        Returns:

        """

# END-DEF-CLASS: VulcanXIDFGenerator


class SimulationVulcanXIDFGenerator(object):
    """ IDF generator for VULCAN-X-Simulation
    """
    def __init__(self, from_date, to_date):
        """
        initialization
        :param from_date:
        :param to_date
        """
        self._instrument_name = 'VULCAN'

        authors = ["Wenduo Zhou"]

        # boiler plate stuff
        self._vulcan = VulcanGeomIDF(self._instrument_name,
                                     comment="Vulcan-X Simulator: Created by " + ", ".join(authors),
                                     valid_from=from_date,
                                     valid_to=to_date)

        self._vulcan.addComment("DEFAULTS")
        self._vulcan.addSnsDefaults()

        self._geom_root = self._vulcan.get_root()

        return

    def build_prototype_instrument(self):
        """ Build instrument
        Returns:
        """
        # source
        self._vulcan.addComment("SOURCE")
        self._vulcan.addModerator(VULCAN_L1)
        # sample
        self._vulcan.addComment("SAMPLE")
        self._vulcan.addSamplePosition()
        # monitor
        self._vulcan.addComment("MONITORS")
        self._vulcan.add_monitor_type(self._geom_root)
        # self._vulcan.addMonitors(distance=[-1.5077], names=["monitor1"])

        # add detectors
        self._vulcan.addComment('Define detector banks')
        self._vulcan.addComponent(type_name='detectors', idlist='detectors')
        # define detector type
        self._vulcan.add_banks_type(root=self._geom_root, name='detectors', components=['bank1'])  #, 'bank4'])

        # west bank
        self._vulcan.addComment('Define West Bank')
        self._vulcan.add_bank(root=self._geom_root, name='bank1', component_name='pack_160tubes',
                              x=2.0, y=0., z=0., rot=90)

        # 20 x 8 packs
        self._vulcan.addComment('20 x standard 8 packs')
        self._vulcan.add_n_8packs_type(self._geom_root, name='pack_160tubes', num_tubes=34, tube_x=0.01)

        # single tube
        self._vulcan.add_tube_type(self._geom_root, num_pixels=128, pixel_height=0.0063578125)

        # single pixel
        self._vulcan.addComment('Cylinder Pixel In Tube')
        self._vulcan.add_cylinder_pixel(self._geom_root, axis=(0, 1, 0), radius=0.0047, height=0.0063578125)

        # monitor shape
        self._vulcan.addComment('MONITOR SHAPE')
        self._vulcan.add_cylinder_pixel(self._geom_root, axis=(0, 0, 1), radius=0.0047, height=0.008, is_monitor=True)

        # define detector IDs
        self._vulcan.addComment('DETECTOR IDs')
        num_dets = 128 * 34
        self._vulcan.define_id_list(self._geom_root, id_name='detectors', start_id=0, end_id=num_dets-1)

        # define monitor IDs
        self._vulcan.addComment('MONITOR IDs')
        self._vulcan.define_id_list(self._geom_root, id_name='monitors', start_id=None, end_id=None)

        # define detector parameters
        self._vulcan.addComment('DETECTOR PARAMETERS')
        self._vulcan.define_detector_parameters(self._geom_root)

        return

    def build_vulcan_x_prototype(self):
        """
        for McVine debugging
        1. 128 pixel tube
        2.
        Returns:

        """
        # source
        self._vulcan.addComment("SOURCE")
        self._vulcan.addModerator(VULCAN_L1)
        # sample
        self._vulcan.addComment("SAMPLE")
        self._vulcan.addSamplePosition()
        # monitor
        self._vulcan.addComment("MONITORS")
        self._vulcan.add_monitor_type(self._geom_root)
        # self._vulcan.addMonitors(distance=[-1.5077], names=["monitor1"])

        # add detectors
        self._vulcan.addComment('Define detector banks')
        self._vulcan.addComponent(type_name='detectors', idlist='detectors')
        # define detector type
        self._vulcan.add_banks_type(root=self._geom_root, name='detectors', components=['bank1', 'bank2', 'bank5'])

        # west bank
        self._vulcan.addComment('Define West Bank')
        self._vulcan.add_bank(root=self._geom_root, name='bank1', component_name='pack_160tubes',
                              x=2.0, y=0., z=0., rot=90)

        # east bank
        self._vulcan.addComment('Define West Bank')
        self._vulcan.add_bank(root=self._geom_root, name='bank2', component_name='pack_160tubes',
                              x=-2.0, y=0., z=0., rot=-90)

        # high angle bank
        self._vulcan.addComment('Define High Angle Bank')
        self._vulcan.add_bank(root=self._geom_root, name='bank5', component_name='pack_72tubes',
                              x=2.*math.sin(150.*math.pi/180.), y=0., z=2.*math.cos(150.*math.pi/180.), rot=150.)

        # 20 x 8 packs
        self._vulcan.addComment('20 x standard 8 packs')
        self._vulcan.add_n_8packs_type(self._geom_root, name='pack_160tubes', num_tubes=160, tube_x=0.01,
                                       num_tube_pixels=128)

        # single tube
        self._vulcan.add_tube_type(self._geom_root, num_pixels=128, pixel_height=PIXEL_HEIGHT)

        # 9 x 8 packs
        self._vulcan.addComment('9 x standard 8 packs')
        self._vulcan.add_n_8packs_type(self._geom_root, name='pack_72tubes', num_tubes=72, tube_x=0.01,
                                       num_tube_pixels=128)

        # single tube
        # self._vulcan.add_tube_type(self._geom_root, num_pixels=128, pixel_height=PIXEL_WIDTH)

        # single pixel
        self._vulcan.addComment('Cylinder Pixel In Tube')
        self._vulcan.add_cylinder_pixel(self._geom_root, axis=(0, 1, 0), radius=PIXEL_WIDTH, height=PIXEL_HEIGHT)

        # monitor shape
        self._vulcan.addComment('MONITOR SHAPE')
        self._vulcan.add_cylinder_pixel(self._geom_root, axis=(0, 0, 1), radius=0.0047, height=0.008, is_monitor=True)

        # define detector IDs
        self._vulcan.addComment('DETECTOR IDs')
        num_pixels = 2 * 20 * 8 * 128 + 9 * 8 * 128
        self._vulcan.define_id_list(self._geom_root, id_name='detectors', start_id=0, end_id=num_pixels-1)

        # define monitor IDs
        self._vulcan.addComment('MONITOR IDs')
        self._vulcan.define_id_list(self._geom_root, id_name='monitors', start_id=None, end_id=None)

        # define detector parameters
        self._vulcan.addComment('DETECTOR PARAMETERS')
        self._vulcan.define_detector_parameters(self._geom_root)

    def build_vulcan_x_phase1(self):
        """
        build the IDF for VULCAN-X of phase 1 such that it will have 3 banks: west/east/high angle
        :return:
        """
        # source
        self._vulcan.addComment("SOURCE")
        self._vulcan.addModerator(VULCAN_L1)
        # sample
        self._vulcan.addComment("SAMPLE")
        self._vulcan.addSamplePosition()
        # monitor
        self._vulcan.addComment("MONITORS")
        self._vulcan.add_monitor_type(self._geom_root)
        # self._vulcan.addMonitors(distance=[-1.5077], names=["monitor1"])

        # add detectors
        self._vulcan.addComment('Define detector banks')
        self._vulcan.addComponent(type_name='detectors', idlist='detectors')
        # define detector type
        self._vulcan.add_banks_type(root=self._geom_root, name='detectors', components=['bank1', 'bank2', 'bank5'])

        # west bank
        self._vulcan.addComment('Define West Bank')
        bank_name = 'bank1'
        two_theta = VULCAN_X_Phase1_Setup[bank_name][0]*math.pi/180.
        x = VULCAN_X_L2[bank_name] * math.sin(two_theta)
        z = VULCAN_X_L2[bank_name] * math.cos(two_theta)
        self._vulcan.add_bank(root=self._geom_root, name='bank1', component_name='pack_160tubes',
                              x=x, y=0., z=z, rot=VULCAN_X_Phase1_Setup[bank_name][0])

        # east bank
        self._vulcan.addComment('Define West Bank')
        bank_name = 'bank2'
        two_theta = VULCAN_X_Phase1_Setup[bank_name][0]*math.pi/180.
        x = VULCAN_X_L2[bank_name] * math.sin(two_theta)
        z = VULCAN_X_L2[bank_name] * math.cos(two_theta)
        self._vulcan.add_bank(root=self._geom_root, name='bank2', component_name='pack_160tubes',
                              x=x, y=0., z=z, rot=VULCAN_X_Phase1_Setup[bank_name][0])

        # high angle bank
        self._vulcan.addComment('Define High Angle Bank')
        bank_name = 'bank5'
        two_theta = VULCAN_X_Phase1_Setup[bank_name][0]*math.pi/180.
        x = VULCAN_X_L2[bank_name] * math.sin(two_theta)
        z = VULCAN_X_L2[bank_name] * math.cos(two_theta)
        self._vulcan.add_bank(root=self._geom_root, name='bank5', component_name='pack_72tubes',
                              x=x, y=0., z=z, rot=VULCAN_X_Phase1_Setup[bank_name][0]*math.pi/180.)

        # 20 x 8 packs
        self._vulcan.addComment('20 x standard 8 packs')
        self._vulcan.add_n_8packs_type(self._geom_root, name='pack_160tubes', num_tubes=160,
                                       tube_x=PIXEL_FLAT_512_WIDTH,
                                       num_tube_pixels=512)

        # single tube
        self._vulcan.add_tube_type(self._geom_root, num_pixels=512, pixel_height=PIXEL_FLAT_512_HEIGHT)

        # 9 x 8 packs
        self._vulcan.addComment('9 x standard 8 packs')
        self._vulcan.add_n_8packs_type(self._geom_root, name='pack_72tubes', num_tubes=72,
                                       tube_x=PIXEL_FLAT_256_WIDTH,
                                       num_tube_pixels=256)

        # single tube
        self._vulcan.add_tube_type(self._geom_root, num_pixels=256, pixel_height=PIXEL_FLAG_256_HEIGHT)

        # single pixel
        self._vulcan.addComment('Cylinder Pixel In 512 Tube')
        self._vulcan.add_cylinder_pixel(self._geom_root, axis=(0, 1, 0), radius=PIXEL_FLAT_512_RADIUS,
                                        height=PIXEL_FLAT_512_HEIGHT,
                                        pixel_name='pixel{}tube'.format(512))

        self._vulcan.addComment('Cylinder Pixel in 256 Tube')
        self._vulcan.add_cylinder_pixel(self._geom_root, axis=(0, 1, 0), radius=PIXEL_FLAG_256_RADIUS,
                                        height=PIXEL_FLAG_256_HEIGHT,
                                        pixel_name='pixel{}tube'.format(256))

        # monitor shape
        self._vulcan.addComment('MONITOR SHAPE')
        self._vulcan.add_cylinder_pixel(self._geom_root, axis=(0, 0, 1), radius=0.0047, height=0.008, is_monitor=True)

        # define detector IDs
        self._vulcan.addComment('DETECTOR IDs')
        num_pixels = 2 * 20 * 8 * 512 + 9 * 8 * 256
        self._vulcan.define_id_list(self._geom_root, id_name='detectors', start_id=0, end_id=num_pixels-1)

        # define monitor IDs
        self._vulcan.addComment('MONITOR IDs')
        self._vulcan.define_id_list(self._geom_root, id_name='monitors', start_id=None, end_id=None)

        # define detector parameters
        self._vulcan.addComment('DETECTOR PARAMETERS')
        self._vulcan.define_detector_parameters(self._geom_root)

        return

    def build_vulcan_x_phase2(self):
        """
        build the IDF for VULCAN-X of phase 1 such that it will have 3 banks: west/east/high angle
        :return:
        """
        # source
        self._vulcan.addComment("SOURCE")
        self._vulcan.addModerator(VULCAN_L1)
        # sample
        self._vulcan.addComment("SAMPLE")
        self._vulcan.addSamplePosition()
        # monitor
        self._vulcan.addComment("MONITORS")
        self._vulcan.add_monitor_type(self._geom_root)
        # self._vulcan.addMonitors(distance=[-1.5077], names=["monitor1"])

        # add detectors
        self._vulcan.addComment('Define detector banks')
        self._vulcan.addComponent(type_name='detectors', idlist='detectors')
        # define detector type
        banks_name_list = sorted(VULCAN_X_Phase2_Setup.keys())
        self._vulcan.add_banks_type(root=self._geom_root, name='detectors', components=banks_name_list)

        tube_pixel_pack_dict = dict()
        for bank_name in banks_name_list:
            self._vulcan.addComment('Define {}'.format(bank_name.upper()))

            two_theta_degree, num_8packs, tube_pixel_number = VULCAN_X_Phase2_Setup[bank_name]
            two_theta = two_theta_degree * math.pi / 180.
            x = VULCAN_X_L2[bank_name] * math.sin(two_theta)
            z = VULCAN_X_L2[bank_name] * math.cos(two_theta)

            mcvine_pack_name = 'pack_{}tubes'.format(num_8packs*8)

            self._vulcan.add_bank(root=self._geom_root, name=bank_name, component_name=mcvine_pack_name,
                                  x=x, y=0., z=z, rot=two_theta_degree)

            if tube_pixel_number not in tube_pixel_pack_dict:
                tube_pixel_pack_dict[tube_pixel_number] = set()
            tube_pixel_pack_dict[tube_pixel_number].add(num_8packs)
        # END-FOR

        # define panels
        for tube_pixel in tube_pixel_pack_dict.keys():
            if tube_pixel == 256:
                pixel_width = PIXEL_FLAT_256_WIDTH
                pixel_height = PIXEL_FLAT_256_HEIGHT
                pixel_radius = PIXEL_FLAT_256_RADIUS
            elif tube_pixel == 512:
                pixel_width = PIXEL_FLAT_512_WIDTH
                pixel_height = PIXEL_FLAT_512_HEIGHT
                pixel_radius = PIXEL_FLAT_512_RADIUS
            else:
                raise RuntimeError('Not supported tube type')
            for pack_number in tube_pixel_pack_dict[tube_pixel]:
                self._vulcan.addComment('{} x standard 8 packs with {}-pixel tubes'.format(pack_number, tube_pixel))
                self._vulcan.add_n_8packs_type(self._geom_root, name='pack_{}tubes'.format(pack_number*8),
                                               num_tubes=pack_number*8,
                                               tube_x=pixel_width,
                                               num_tube_pixels=tube_pixel)
            # END-FOR

            # single tube
            self._vulcan.add_tube_type(self._geom_root, num_pixels=tube_pixel, pixel_height=pixel_height)

            # single pixel
            self._vulcan.addComment('Cylinder Pixel In {}-Pixel Tube'.format(tube_pixel))
            self._vulcan.add_cylinder_pixel(self._geom_root, axis=(0, 1, 0), radius=pixel_radius,
                                            height=pixel_height,
                                            pixel_name='pixel{}tube'.format(tube_pixel))
        # END-FOR

        # monitor shape
        self._vulcan.addComment('MONITOR SHAPE')
        self._vulcan.add_cylinder_pixel(self._geom_root, axis=(0, 0, 1), radius=0.0047, height=0.008, is_monitor=True)

        # define detector IDs
        self._vulcan.addComment('DETECTOR IDs')
        num_pixels = 0
        for bank_name in sorted(VULCAN_X_Phase2_Setup.keys()):
            two_theta_degree, num_8packs, num_tube_pixels = VULCAN_X_Phase2_Setup[bank_name]
            bank_pixel_number = num_8packs * 8 * num_tube_pixels
            num_pixels += bank_pixel_number
            print ('{}: {} x 8 x {} = {}'.format(bank_name, num_8packs, num_tube_pixels, bank_pixel_number))
        print ('Total pixel number = {}'.format(num_pixels))
        # num_pixels = 2 * 20 * 8 * 512 + 9 * 8 * 256

        self._vulcan.define_id_list(self._geom_root, id_name='detectors', start_id=0, end_id=num_pixels-1)

        # define monitor IDs
        self._vulcan.addComment('MONITOR IDs')
        self._vulcan.define_id_list(self._geom_root, id_name='monitors', start_id=None, end_id=None)

        # define detector parameters
        self._vulcan.addComment('DETECTOR PARAMETERS')
        self._vulcan.define_detector_parameters(self._geom_root)

        return

    def export_idf(self, out_file_name):
        """ Export the built instrument to a Mantid IDF file
        :param out_file_name:
        :return:
        """
        self._vulcan.writeGeom(out_file_name)

        return

# END-DEF-CLASS


def main():
    """
    :return:
    """
    if False:
        # prototype
        vulcan_simulator = SimulationVulcanXIDFGenerator('2017-03-01 00:00:01', '2020-12-31 00:00:01')
        vulcan_simulator.build_prototype_instrument()
        vulcan_simulator.export_idf('prototype_vulcan_x_sim.xml')

    elif False:
        # concept of proof for phase 1
        vulcan_simulator = SimulationVulcanXIDFGenerator('2017-03-01 00:00:01', '2020-12-31 00:00:01')
        vulcan_simulator.build_vulcan_x_prototype()
        vulcan_simulator.export_idf('vulcan_x_concept_proof_phase1_sim.xml')

    elif False:
        # phase 1
        vulcan_simulator = SimulationVulcanXIDFGenerator('2017-03-01 00:00:01', '2020-12-31 00:00:01')
        vulcan_simulator.build_vulcan_x_phase1()
        vulcan_simulator.export_idf('vulcan_x_phase1_sim.xml')

    else:
        # final phase
        vulcan_simulator = SimulationVulcanXIDFGenerator('2017-03-01 00:00:01', '2020-12-31 00:00:01')
        vulcan_simulator.build_vulcan_x_phase2()
        vulcan_simulator.export_idf('vulcan_x_phase2_sim.xml')

    # END-IF-ELSE


if __name__ == '__main__':
    main()
