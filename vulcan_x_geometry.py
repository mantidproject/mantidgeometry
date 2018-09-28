# This is the geometry/IDF generator for VULCAN-X
from vulcan_geometry import VulcanGeomIDF
import math


# Define pixel ID gap between 2 adjacent 8 packs in a same group
GAP = 10
VULCAN_L1 = 43.

PIXEL_WIDTH = 0.004145
PIXEL_HEIGHT = 0.00301625


class VulcanXIDFGenerator(object):
    """
    main generator for VULCAN IDF
    """
    # value-tuple: 2theta, detector type, number of eight packs, starting PID, gap PID, pixels in a tube
    DetectorInfoDict = {'Phase 1': {'bank1': (-90., 'eightpack', 20, GAP, 512),
                                    'bank2': (90., 'eightpack', 20, GAP, 512),
                                    'bank3': (150., 'eightpack',  0, 256)},
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
                                       num_tube_pixels=512)

        # single tube
        self._vulcan.add_tube_type(self._geom_root, num_pixels=512, pixel_height=0.0063578125)

        # 9 x 8 packs
        self._vulcan.addComment('9 x standard 8 packs')
        self._vulcan.add_n_8packs_type(self._geom_root, name='pack_72tubes', num_tubes=72, tube_x=0.01,
                                       num_tube_pixels=256)

        # single tube
        self._vulcan.add_tube_type(self._geom_root, num_pixels=256, pixel_height=0.0063578125)

        # single pixel
        self._vulcan.addComment('Cylinder Pixel In Tube')
        self._vulcan.add_cylinder_pixel(self._geom_root, axis=(0, 1, 0), radius=0.0047, height=0.0063578125)

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

    def build_complete_vulcan_x(self):
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
        self._vulcan.add_banks_type(root=self._geom_root, name='detectors', components=['bank1'])  #, 'bank4'])

        # west bank: bank 1
        self._vulcan.addComment('Define Bank 1/West Bank')
        self._vulcan.add_bank(root=self._geom_root, name='bank1', component_name='pack_160tubes',
                              x=2.0, y=0., z=0., rot=90)

        # east bank: bank 2
        self._vulcan.addComment('Define Bank 2/East Bank')
        self._vulcan.add_bank(root=self._geom_root, name='bank2', component_name='pack_160tubes',
                              x=-2.0, y=0., z=0., rot=-90)

        # bank 3 @ 135
        bank_angle = 120.
        self._vulcan.addComment('Define Bank 3')
        self._vulcan.add_bank(root=self._geom_root, name='bank3', component_name='pack_160tubes',
                              x=2.0*math.sin(bank_angle*math.pi/180.), y=0., z=2.*math.cos(bank_angle*math.pi/180.),
                              rot=bank_angle)

        # bank 4 @ 155
        bank_angle = 150.
        self._vulcan.addComment('Define Bank 4')
        self._vulcan.add_bank(root=self._geom_root, name='bank4', component_name='pack_160tubes',
                              x=2.0*math.sin(bank_angle*math.pi/180.), y=0., z=2.*math.cos(bank_angle*math.pi/180.),
                              rot=bank_angle)

        # bank 5 (old) high angle bank @ -150
        bank5_angle = -155.
        self._vulcan.addComment('Define High Angle Bank at {}'.format(bank5_angle))
        self._vulcan.add_bank(root=self._geom_root, name='bank5', component_name='pack_72tubes',
                              x=2.*math.sin(bank5_angle*math.pi/180.), y=0., z=2.*math.cos(bank5_angle*math.pi/180.),
                              rot=bank5_angle)

        # bank 6:
        bank6_angle = -65.
        self._vulcan.addComment('Define Bank 6 at {}'.format(bank6_angle))
        self._vulcan.add_bank(root=self._geom_root, name='bank6', component_name='pack_88tubes',
                              x=2.*math.sin(bank6_angle*math.pi/180.), y=0., z=2.*math.cos(bank6_angle*math.pi/180.),
                              rot=bank6_angle)

        # 20 x 8 packs
        self._vulcan.addComment('20 x standard 8 packs')
        self._vulcan.add_n_8packs_type(self._geom_root, name='pack_160tubes', num_tubes=160, tube_x=0.01,
                                       num_tube_pixels=512)

        # single tube
        self._vulcan.add_tube_type(self._geom_root, num_pixels=512, pixel_height=0.0063578125)

        # 9 x 8 packs
        self._vulcan.addComment('9 x standard 8 packs')
        self._vulcan.add_n_8packs_type(self._geom_root, name='pack_72tubes', num_tubes=72, tube_x=0.01,
                                       num_tube_pixels=256)

        # 11 x 8 packs
        self._vulcan.addComment('11 x standard 8 packs')
        self._vulcan.add_n_8packs_type(self._geom_root, name='pack_88tubes', num_tubes=88, tube_x=0.01,
                                       num_tube_pixels=512)

        # single tube
        self._vulcan.add_tube_type(self._geom_root, num_pixels=256, pixel_height=0.0063578125)

        # single pixel
        self._vulcan.addComment('Cylinder Pixel In Tube')
        self._vulcan.add_cylinder_pixel(self._geom_root, axis=(0, 1, 0), radius=0.0047, height=0.0063578125)

        # monitor shape
        self._vulcan.addComment('MONITOR SHAPE')
        self._vulcan.add_cylinder_pixel(self._geom_root, axis=(0, 0, 1), radius=0.0047, height=0.008, is_monitor=True)

        # define detector IDs
        self._vulcan.addComment('DETECTOR IDs')
        num_pixels = 4 * 20 * 8 * 512 + + 1 * 11 * 8 * 512 + 9 * 8 * 256
        self._vulcan.define_id_list(self._geom_root, id_name='detectors', start_id=0, end_id=num_pixels - 1)

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

    elif True:
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
        vulcan_simulator.build_complete_vulcan_x()
        vulcan_simulator.export_idf('vulcan_x_complete_sim.xml')

    # END-IF-ELSE


if __name__ == '__main__':
    main()
