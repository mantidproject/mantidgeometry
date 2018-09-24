# This is the geometry/IDF generator for VULCAN-X
from vulcan_geometry import VulcanGeomIDF

# Define pixel ID gap between 2 adjacent 8 packs in a same group
GAP
VULCAN_L1 = 43.

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

    def generatae_idf(self, idf_xml_name):
        """

        :param idf_xml_name:
        :return:
        """

        self._vulcan = VulcanGeomIDF('VULCAN', comment, self._from_date, self._exp_date)

        # add source, sample
        self._vulcan.addSamplePosition()
        self._vulcan.addModerator(-VULCAN_L1)



        return