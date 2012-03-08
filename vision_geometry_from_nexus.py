__author__ = 'scu'

import nxs
import math

nexusfile = "/SNS/VIS/shared/NeXusFiles/VIS/2012_1_16B_SCI/1/224/NeXus/VIS_224_event.nxs"
banks = 100


if __name__ == "__main__":
    file = nxs.open(nexusfile)



    file.close()

