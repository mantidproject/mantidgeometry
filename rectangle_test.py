#!/bin/env python
from rectangle import Rectangle, getAngle
from rectangle import Vector, UNIT_X, UNIT_Y, UNIT_Z
import math
import unittest

class TestRectangle(unittest.TestCase):
    def checkCenter(self, rectangle, center):
        self.assertEqual(rectangle.center, center)

    def checkOrientation(self, rectangle, orientation):
        obs = rectangle.orientation
        row = 0
        for (obs_row, exp_row) in zip(obs, orientation):
            col = 0
            for (obs_val, exp_val) in zip(obs_row, exp_row):
                msg = "Mismatch of element [%d, %d] obs=%f != exp=%f" \
                    % (row, col, obs_val, exp_val)
                self.assertEqual(obs_val, exp_val, msg)
                col += 1
            row += 1

    def checkRotation(self, rectangle, alpha, beta, gamma):
        rot = rectangle.euler_rot
        self.assertEqual(rot[0][0], alpha,
                         "Error in alpha: %f != %f" % (rot[0][0], alpha))
        self.assertEqual(rot[1][0], beta,
                         "Error in beta: %f != %f" % (rot[1][0], beta))
        self.assertEqual(rot[2][0], gamma,
                         "Error in gamma: %f != %f" % (rot[2][0], gamma))

    def test_rect1(self):
        rect = Rectangle((0,0,0), (1,0,0), (1,1,0), (0,1,0))
        self.checkCenter(rect, [.5,.5,0.])
        self.checkOrientation(rect, ((0.0, 1.0, 0.0),
                                     (1.0, 0.0, 0.0),
                                     (0.0, 0.0, -1.0)))
        self.checkRotation(rect, 90., 180., 0.)

    def test_rect2(self):
        rect = Rectangle((0,1,0), (1,1,0), (1,0,0), (0,0,0))
        self.checkCenter(rect, [.5,.5,0.])
        self.checkOrientation(rect, ((0.0, -1.0, 0.0),
                                     (1.0,  0.0, 0.0),
                                     (-0.0, 0.0, 1.0)))
        self.checkRotation(rect, 90., 0., 0.)

class TestGetAngle(unittest.TestCase):
    def check(self, y, x, angle):
        self.assertEqual(math.degrees(getAngle(y,x)), angle)

    def testAll(self):
        self.check(0.,  0., 0.)
        self.check(1.,  0., 90.)
        self.check(0., -1., 180.)
        self.check(-1., 0., 270.)

class TestVector(unittest.TestCase):
    def testCross(self):
        self.assertEqual(UNIT_X.cross(UNIT_Y), UNIT_Z)
        self.assertEqual(UNIT_Y.cross(UNIT_Z), UNIT_X)
        self.assertEqual(UNIT_Z.cross(UNIT_X), UNIT_Y)

    def testDot(self):
        self.assertEqual(UNIT_X.dot(UNIT_X), 1.)
        self.assertEqual(UNIT_X.dot(UNIT_Y), 0.)
        self.assertEqual(UNIT_X.dot(UNIT_Z), 0.)
        self.assertEqual(UNIT_Y.dot(UNIT_Y), 1.)
        self.assertEqual(UNIT_Y.dot(UNIT_Z), 0.)
        self.assertEqual(UNIT_Z.dot(UNIT_Z), 1.)

    def testVector(self):
        temp = Vector(100., 200., 300.)

        self.assertEqual(len(temp), 3)

        self.assertEqual(temp, (100., 200., 300.))
        self.assertEqual(temp.x, 100.)
        self.assertEqual(temp.y, 200.)
        self.assertEqual(temp.z, 300.)
        self.assertEqual(temp.x, temp[0])
        self.assertEqual(temp.y, temp[1])
        self.assertEqual(temp.z, temp[2])

        self.assertAlmostEqual(temp.length, 374.16573867739413)
        self.assertEqual(temp.normalize().length, 1.)

    def testVectorMath(self):
        a = Vector(UNIT_X)
        b = Vector(UNIT_Y)
        a = a+b
        self.assertEqual(a.x, 1.)
        self.assertEqual(a.y, 1.)
        self.assertEqual(a.z, 0.)

        a = Vector(UNIT_X)
        b = Vector(UNIT_Y)
        a = a-b
        self.assertEqual(a.x,  1.)
        self.assertEqual(a.y, -1.)
        self.assertEqual(a.z,  0.)

        a = Vector(UNIT_X)
        a = a/2.
        self.assertEqual(a.x,  .5)
        self.assertEqual(a.y,  0.)
        self.assertEqual(a.z,  0.)

        a = Vector(UNIT_X)
        a = a*2.
        self.assertEqual(a.x,  2.)
        self.assertEqual(a.y,  0.)
        self.assertEqual(a.z,  0.)

        a = Vector(UNIT_X)
        a = 2.*a
        self.assertEqual(a.x,  2.)
        self.assertEqual(a.y,  0.)
        self.assertEqual(a.z,  0.)

def suite():
    suite_rect  = unittest.TestLoader().loadTestsFromTestCase(TestRectangle)
    suite_angle = unittest.TestLoader().loadTestsFromTestCase(TestGetAngle)

    return unittest.TestSuite([suite_rect, suite_angle])

if __name__ == "__main__":
    unittest.main(module="rectangle_test", verbosity=2)
