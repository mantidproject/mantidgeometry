#!/bin/env python
from rectangle import Rectangle, calcEuler, checkRotation, generateRotation, \
    getAngle, getYZY, getZYZ
from rectangle import Vector, UNIT_X, UNIT_Y, UNIT_Z
import math
import numpy as np
import unittest

def assertAllClose(obs, exp, atol):
    if atol == 0.:
        if np.all(obs == exp):
            return
    else:
        if np.allclose(obs,exp, atol=atol):
            return

    # getting here means something didn't match
    raise AssertionError(str(obs) + ' != ' + str(exp))

class TestRectangle(unittest.TestCase):
    def checkCenter(self, rectangle, center):
        assertAllClose(rectangle.center, center, 0.)

    def checkOrientation(self, rectangle, orientation):
        assertAllClose(rectangle.orientation, orientation, 0.)

    def checkRotation(self, rectangle, alpha, beta, gamma):
        rot = rectangle.euler_rot
        rot = [item[0] for item in rot]
        assertAllClose(rot, [alpha, beta, gamma], 0.)

    def test_rect1(self):
        rect = Rectangle((0,0,0), (1,0,0), (1,1,0), (0,1,0))
        self.checkCenter(rect, [.5,.5,0.])
        self.checkOrientation(rect, ((0.0, 1.0, 0.0),
                                     (1.0, 0.0, 0.0),
                                     (0.0, 0.0, -1.0)))
        self.checkRotation(rect, 90., 180., 180.) # zyz - was 90,180,0

    def test_rect2(self):
        rect = Rectangle((0,1,0), (1,1,0), (1,0,0), (0,0,0))
        self.checkCenter(rect, [.5,.5,0.])
        self.checkOrientation(rect, ((0.0, -1.0, 0.0),
                                     (1.0,  0.0, 0.0),
                                     (-0.0, 0.0, 1.0)))
        self.checkRotation(rect, 0., 0., 90.)

    def test_rect3(self):
        rect = Rectangle((1,1,0), (0,1,0), (0,0,0), (1,0,0))

        self.checkCenter(rect, [.5,.5,0.])
        #self.checkOrientation(rect, ((0.0, 1.0, 0.0),
        #                             (1.0, 0.0, 0.0),
        #                             (0.0, 0.0, -1.0)))
        #self.checkRotation(rect, 90., 180., 0.)

    def test_rect4(self):
        rect = Rectangle((1,0,0), (0,0,0), (0,1,0), (1,1,0))

        self.checkCenter(rect, [.5,.5,0.])
        #self.checkOrientation(rect, ((0.0, 1.0, 0.0),
        #                             (1.0, 0.0, 0.0),
        #                             (0.0, 0.0, -1.0)))
        #self.checkRotation(rect, 90., 180., 0.)

class TestGetAngle(unittest.TestCase):
    def check(self, y, x, angle):
        self.assertEqual(math.degrees(getAngle(y,x)), angle)

    def testAll(self):
        self.check(0.,  0., 0.)
        self.check(1.,  0., 90.)
        self.check(0., -1., 180.)
        self.check(-1., 0., 270.)

IDENTITY = np.array([[1,0,0],[0,1,0],[0,0,1]], dtype=np.float)
ATOL_ROTATION = 1.e-15

class TestOrientation(unittest.TestCase):
    def checkOrientation(self, rotation):
        try:
            checkRotation(rotation)
        except RuntimeError, e:
            raise AssertionError(e)

    def checkRotation(self, axis, angle, exp):
        obs = generateRotation(axis, angle)
        assertAllClose(obs,exp, atol=ATOL_ROTATION)
        return obs

    def testRotationIdentity(self):
        for axis in UNIT_X, UNIT_Y, UNIT_Z:
            self.checkRotation(axis, 0., IDENTITY)

        assertAllClose(np.degrees(getYZY(IDENTITY)), [0., 0., 0.], 0.)
        assertAllClose(np.degrees(getZYZ(IDENTITY)), [0., 0., 0.], 0.)

    def testRotationX(self):
        exp = np.array([[1,0,0],[0,0,-1],[0,1,0]], dtype=np.float)
        obs = self.checkRotation(UNIT_X, .5*np.pi, exp)
        assertAllClose(np.degrees(getYZY(obs)), np.degrees(calcEuler(obs, 'YZY')), 0.)
        assertAllClose(np.degrees(getYZY(obs)), [90., 90., 270.], 0.) # TODO verify

        assertAllClose(np.degrees(getZYZ(obs)), np.degrees(calcEuler(obs, 'ZYZ')), 0.)
        assertAllClose(np.degrees(getZYZ(obs)), [270., 90., 90.], 0.) # TODO verify

        exp = np.array([[1,0,0],[0,-1,0],[0,0,-1]], dtype=np.float)
        obs = self.checkRotation(UNIT_X, np.pi, exp)
        assertAllClose(np.degrees(getYZY(obs)), [180., 180., 0.], 0.) # TODO verify
        assertAllClose(np.degrees(getZYZ(obs)), [0., 180., 180.], 0.) # TODO verify

    def testRotationY(self):
        exp = np.array([[0,0,1],[0,1,0],[-1,0,0]], dtype=np.float)
        obs = self.checkRotation(UNIT_Y, .5*np.pi, exp)

        exp = np.array([[-1,0,0],[0,1,0],[0,0,-1]], dtype=np.float)
        obs = self.checkRotation(UNIT_Y, np.pi, exp)

    def testRotationZ(self):
        exp = np.array([[0,-1,0],[1,0,0],[0,0,1]], dtype=np.float)
        obs = self.checkRotation(UNIT_Z, .5*np.pi, exp)

        exp = np.array([[-1,0,0],[0,-1,0],[0,0,1]], dtype=np.float)
        obs = self.checkRotation(UNIT_Z, np.pi, exp)

        # https://en.wikipedia.org/wiki/Rotation_matrix

class TestVector(unittest.TestCase):
    def testCross(self):
        self.assertEqual(UNIT_X.cross(UNIT_Y), UNIT_Z)
        self.assertEqual(UNIT_Y.cross(UNIT_Z), UNIT_X)
        self.assertEqual(UNIT_Z.cross(UNIT_X), UNIT_Y)

        self.assertEqual(UNIT_X.cross((0,1,0)), UNIT_Z)
        self.assertEqual(UNIT_X.cross(np.array((0,1,0), dtype=np.float)), UNIT_Z)


    def testDot(self):
        self.assertEqual(UNIT_X.dot(UNIT_X), 1.)
        self.assertEqual(UNIT_X.dot(UNIT_Y), 0.)
        self.assertEqual(UNIT_X.dot(UNIT_Z), 0.)
        self.assertEqual(UNIT_Y.dot(UNIT_Y), 1.)
        self.assertEqual(UNIT_Y.dot(UNIT_Z), 0.)
        self.assertEqual(UNIT_Z.dot(UNIT_Z), 1.)

        self.assertEqual(UNIT_X.dot((1,0,0)), 1.)
        self.assertEqual(UNIT_X.dot(np.array((1,0,0), dtype=np.float)), 1.)

    def testVector(self):
        temp = Vector(100., 200., 300.)

        self.assertEqual(len(temp), 3)

        self.assertEqual(temp, Vector(100., 200., 300.))
        self.assertEqual(temp, (100., 200., 300.))
        self.assertEqual(temp, [100., 200., 300.])
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
