#!/usr/bin/env python
from helper import MantidGeom
import numpy as np
import os
from rectangle import Vector, getEuler, makeLocation


class DetCalBank():
    '''Class that holds the information for a single panel/line of the detcal file'''
    def __init__(self, *args):
        if len(args) != 16:
            raise RuntimeError('Expeceted 16 args found {}'.format(len(args)))

        self.det_num = int(args[0])
        self.first_pixel = 256 * 256 * self.det_num

        self.nrows = int(args[1])
        self.ncols = int(args[2])

        # must get values before the rest ar converted to meters
        base_vector = Vector(args[10:13])  # 10, 11, 12
        up_vector = Vector(args[13:16])    # 13, 14, 15

        # convert everything else to floats in meeters
        args = np.array(args, dtype=np.float) / 100.

        self._calc_panel_size(width=args[3], height=args[4])

        # skip args[5] which is the depth and not apparently used
        # skip args[6] with is the length of the center vector
        self.center = Vector(args[7:10])        # 7, 8, 9
        self._calc_panel_pos_and_orient(base_vector, up_vector)

    def _calc_panel_size(self, width, height):
        self.deltaX = width / self.nrows
        self.startX = 0.5 * (self.deltaX - width)

        self.deltaY = height / self.ncols
        self.startY = 0.5 * (self.deltaY - height)

    def _calc_panel_pos_and_orient(self, base_vector, up_vector):
        # all of these angles are in radians
        phi, chi, omega = [item for item in getEuler(base_vector, up_vector, degrees=True)]
        # need the angle and what it is rotated around
        self.rotations = [(omega, [0, 1, 0]),
                          (chi, [0, 0, 1]),
                          (phi, [0, 1, 0])]

    def addToXml(self, instr):
        type_name = 'panel{}'.format(self.det_num)
        instr.addComment(type_name)  # make it easier to read the xml

        # write out the component/shape of the overall detector
        instr.addRectangularDetector(name=type_name, type='pixel',
                                     xpixels=self.nrows, xstart=self.startX, xstep=self.deltaX,
                                     ypixels=self.ncols, ystart=self.startY, ystep=self.deltaY)

        # write out the detector position
        extra_attrs = {"idstart": self.first_pixel, 'idfillbyfirst': 'y', 'idstepbyrow': self.ncols}
        det = instr.makeDetectorElement(type_name, extra_attrs=extra_attrs)
        makeLocation(instr, det, 'bank{}'.format(self.det_num), self.center, self.rotations)


class DetCal():
    '''Class holding information for a whole ISAW detcal file'''
    def __init__(self, filename):
        if not os.path.exists(filename):
            raise RuntimeError("File '%s' does not exist" % filename)

        self.banks = []  # list of banks

        with open(filename) as handle:
            for line in handle:
                if line.startswith('#'):
                    continue  # comment line

                flag = int(line[0])  # each line has a flag
                line = line[1:].strip().split()

                if flag == 4 or flag == 6:
                    pass  # label banks, label on l1/t0_shift
                elif flag == 5:
                    self.banks.append(DetCalBank(*line))
                elif flag == 7:
                    self.l1, self.t0 = [float(value) for value in line]
                    self.l1 /= 100.  # from cm to meters
                else:
                    raise RuntimeError(f'Do not know how to deal with flag {flag}')


parameters_template = '''<?xml version='1.0' encoding='UTF-8'?>
<parameter-file instrument = "MANDI" valid-from   ="{validfrom}" valid-to     ="2100-12-31 23:59:59">

<component-link name = "MANDI">
<!-- Specify that any banks not in NeXus file are to be removed -->
<parameter name="T0">
 <value val="{T0}"/>
</parameter>

<!-- Need to fill in gaps for peak profile fitting -->
<parameter name="fitConvolvedPeak" type="bool">
 <value val="false"/>
</parameter>

<!-- Multiplier for profile fitting for BVG polar angle -->
<parameter name="sigX0Scale">
 <value val="1." />
</parameter>

<!-- Multiplier for profile fitting for BVG azimuthal angle -->
<parameter name="sigY0Scale">
 <value val="1." />
</parameter>

<!-- Number of rows between detector gaps for profile fitting -->
<parameter name="numDetRows" type="int">
 <value val="255" />
</parameter>

<!-- Number of cols between detector gaps for profile fitting -->
<parameter name="numDetCols" type="int">
 <value val="255" />
</parameter>

<!-- Number of polar bins for BVG histogramming when profile fitting -->
<parameter name="numBinsTheta" type="int">
 <value val="50" />
</parameter>

<!-- Number of azimuthal bins for BVG histogramming when profile fitting -->
<parameter name="numBinsPhi" type="int">
 <value val="50" />
</parameter>

<!-- Fraction along (h,k,l) to use for profile fitting. 0.5 is the next peak. -->
<parameter name="fracHKL">
 <value val="0.25" />
</parameter>

<!-- Side length of each voxel for fitting in units of angstrom^-1 -->
<parameter name="dQPixel">
 <value val="0.003" />
</parameter>

<!-- Minimum spacing for profile fitting the TOF profile. Units of microseconds -->
<parameter name="mindtBinWidth">
 <value val="15" />
</parameter>

<!-- Maximum spacing for profile fitting the TOF profile. Units of microseconds -->
<parameter name="maxdtBinWidth">
 <value val="50" />
</parameter>

<!-- Size of peak mask for background calculation in units of dQPixel -->
<parameter name="peakMaskSize" type="int">
 <value val="5" />
</parameter>

<!-- Initial guess parameters for coshPeakWidthModel -->
<parameter name="sigSC0Params" type="string">
 <value val="0.00413132 1.54103839 1.0 -0.00266634" />
</parameter>

<!-- Initial guess for sigma along the azimuthal direction (rad) -->
<parameter name="sigAZ0">
 <value val="0.0025" />
</parameter>

<!-- Initial guess parameters for fsigP (BVG covariance) -->
<parameter name="sigP0Params" type="string">
 <value val="0.1460775 1.85816592 0.26850086 -0.00725352" />
</parameter>

</component-link>
</parameter-file>
'''

if __name__ == '__main__':
    valid_from = '2021-02-01 00:00:00'
    filename = 'MANDI_Definition_{}.xml'.format(valid_from.split()[0])

    # read in the detector calibration
    detcal = DetCal('SNS/MANDI/MaNDi-February2021.DetCal')

    # write the instrument geometry
    instr = MantidGeom('MANDI', valid_from=valid_from)
    instr.addComment('DEFAULTS')
    instr.addSnsDefaults(default_view='spherical_y')

    instr.addComment("SOURCE")
    instr.addModerator(detcal.l1)
    instr.addComment("SAMPLE")
    instr.addSamplePosition()

    instr.addComment("MONITORS")
    instr.addMonitors(distance=[-2.935, -0.898, 1.042], names=["monitor1", 'monitor2', 'monitor3'])

    # add banks here
    for bank in detcal.banks:
        bank.addToXml(instr)

    # shape for detector pixels - ignored by required
    instr.addComment(' Pixel for Detectors')
    delta = 0.000309
    instr.addCuboidPixel("pixel",
                         [-delta, -delta,  0.0],
                         [-delta, delta,  0.0],
                         [-delta, -delta, -0.0001],
                         [delta, -delta,  0.0],
                         shape_id="pixel-shape")

    instr.addComment(" Shape for Monitors")
    instr.addComment(" TODO: Update to real shape ")
    instr.addDummyMonitor(0.01, .03)

    instr.addComment("MONITOR IDs")
    instr.addMonitorIds([-1, -2, -3])

    instr.writeGeom(filename)

    # write the parameter file
    filename = filename.replace('Definition', 'Parameters')
    param_contents = parameters_template.format(validfrom=valid_from, T0=detcal.t0)
    print('writing', filename)
    with open(filename, mode='w') as handle:
        handle.write(param_contents)
