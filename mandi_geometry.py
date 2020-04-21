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
        if self.det_num == 42:
            print('base', base_vector)
            print('up  ', up_vector)
        # all of these angles are in radians
        phi, chi, omega = [item for item in getEuler(base_vector, up_vector, degrees=True,verbose=(self.det_num==42))]
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
        extra_attrs={"idstart":self.first_pixel, 'idfillbyfirst':'y', 'idstepbyrow':self.ncols}
        det = instr.makeDetectorElement(type_name, extra_attrs=extra_attrs)
        makeLocation(instr, det, 'bank{}'.format(self.det_num), self.center, self.rotations)


class DetCal():
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

if __name__ == '__main__':
    # read in the detector calibration
    detcal = DetCal('MANDI/MANDI_April2020.DetCal')

    # write the instrument geometry
    instr = MantidGeom('MANDI',
                       valid_from='2020-04-01 00:00:00')
    instr.addComment('DEFAULTS')
    instr.addSnsDefaults(default_view='spherical_y')

    instr.addComment("SOURCE")
    instr.addModerator(detcal.l1)
    instr.addComment("SAMPLE")
    instr.addSamplePosition()

    instr.addComment("MONITORS")
    instr.addMonitors(distance=[-2.935, -0.898, 1.042], names=["monitor1", 'monitor2', 'monitor3'])

    # TODO add banks here
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
    instr.addMonitorIds([-1,-2,-3])

    instr.writeGeom()


    # TODO write out parameter file with T0
