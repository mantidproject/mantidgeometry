# Much of this code was not so casually ported from
#
# https://flathead.ornl.gov/repos/TranslationService/trunk/sns-translation-client/sns-translation-core/src/main/java/gov/ornl/sns/translation/geometry/calc/helpers/RectCorners.java
#
from __future__ import print_function

import math
import numpy as np
try:
    from string import maketrans  # python2
except ImportError:
    maketrans = str.maketrans  # python3
HAS_LXML = True
try:
    from lxml import etree as le # python-lxml on rpm based systems
except ImportError:
    print("WARNING: Failed to load lxml. Xml output turned off for rectangle.py")
    HAS_LXML = False

TOLERANCE = .0001

class Vector:
    """
    This class encapsulates the concept of a vector in 3D space from
    geometry
    """

    LENGTH = 3

    def __init__(self, *values):
        self.data = np.array(values, dtype=np.float).flatten()

        # check the length
        if self.data.size != Vector.LENGTH:
            msg = "Expected %d values, found %d" % (Vector.LENGTH, self.__data.size)
            raise RuntimeError(msg)

        # sanity check the numbers
        if np.any(np.isnan(self.data)):
            raise RuntimeError("Encountered NaN")

    x = property(lambda self: self.data[0])
    y = property(lambda self: self.data[1])
    z = property(lambda self: self.data[2])
    length = property(lambda self: np.sqrt(self.dot(self)))


    def cross(self, other):
        """
        Calculate the cross product of this with another vector.
        """
        return Vector(np.cross(self.data, Vector(other).data))

    def dot(self, other):
        """
        Calculate the dot product of this with another vector.
        """
        return np.dot(self.data, Vector(other).data)

    def normalize(self):
        """
        Set the unit length to one
        """
        if self.isCardinal(True):
            return self

        length = self.length # cache value
        if abs(length) < TOLERANCE:
            raise RuntimeError("Zero vector of zero length")

        # divide the elements by the length
        self.data /= length

        # set near zeros to zero
        self.data[np.abs(self.data) < TOLERANCE] = 0.

        return self

    def isCardinal(self, resetValues=False):
        """
        Returns true iff the vector is (1,0,0), (0,1,0) or (0,0,1).
        """
        if abs(self.length-1.) > TOLERANCE:
            return False

        for unit_vec in (UNIT_X, UNIT_Y, UNIT_Z):
            if np.allclose(self.data, unit_vec, atol=TOLERANCE):
                if resetValues:
                    self.data = unit_vec
                return True

        return False

    def __getitem__(self, key):
        return self.data[key]

    def __eq__(self, other):
        try:
            return np.alltrue(self.data == other.data)
        except AttributeError:
            other = Vector(other)
            return self == other

    def __add__(self, other):
        return Vector(self.data + other.data)

    def __sub__(self, other):
        return Vector(self.data - other.data)

    def __div__(self, other):
        return Vector(self.data / other) # only allow divide by a scalar

    def __truediv__(self, other):
        return Vector(self.data / other) # only allow divide by a scalar

    def __mul__(self, other):
        return Vector(self.data * other) # only allow multiply by a scalar

    def __rmul__(self, other):
        return self * other

    def __repr__(self):
        return self.data.__repr__()

    def __len__(self):
        return self.data.size

    length = property(lambda self: math.sqrt(self.dot(self)))

UNIT_X = Vector(1.,0.,0.)
UNIT_Y = Vector(0.,1.,0.)
UNIT_Z = Vector(0.,0.,1.)

def getAngle(y, x, debug=False, onlyPositive=True):
    """
    Returns the angle in radians using atan2 (y=sin, x=cos)
    """
    if debug:
        print("getAngle(%f, %f)=" % (y, x),)
    angle = math.atan2(y, x)
    if onlyPositive and angle < 0.:
        angle += 2.*math.pi
    if debug:
        print(math.degrees(angle))
    return angle

def getEuler(uVec, vVec, **kwargs):
    """This is taken from the Goiniometer.getEulerAngles() function that is
    in the package gov.ornl.sns.translation.geometry.calc.jython"""

    degrees = kwargs.get("degrees", False)
    verbose = kwargs.get("verbose", 0)

    # normalize the u-vector
    uVec = uVec.normalize()

    # determine the perpendicular
    nVec = uVec.cross(vVec)
    nVec = nVec.normalize()
    # make sure that u,v are perpendicular
    vVec = nVec.cross(uVec)
    vVec = vVec.normalize()

    # make sure the new unit vectors are orthogonal
    if abs(uVec.dot(vVec)) > TOLERANCE:
        raise RuntimeError('u dot v is too large: {} > {}'.format(abs(uVec.dot(vVec)), TOLERANCE))
    if abs(uVec.dot(nVec)) > TOLERANCE:
        raise RuntimeError('u dot n is too large: {} > {}'.format(abs(uVec.dot(nVec)), TOLERANCE))
    if abs(vVec.dot(nVec)) > TOLERANCE:
        raise RuntimeError('v dot n is too large: {} > {}'.format(abs(vVec.dot(nVec)), TOLERANCE))

    if verbose:
        print("orthonormal:", uVec, vVec, nVec)

    # calculate the angles
    import math

    if vVec.y == 1.: # chi rotation is 0, just rotate about z-axis
        if verbose > 1:
            print("chi rotation is 0")
        phi = math.atan2(nVec.x, nVec.z)
        chi = 0.
        omega = 0.
    elif vVec.y == -1.:# chi rotation is 180 degrees
        if verbose > 1:
            print("chi rotation is 180 degrees")
        phi = -1. * math.atan2(nVec.x, nVec.z)
        if phi == -1.* math.pi:
            phi = math.pi
        chi = math.pi
        omega = 0.
    else:
        if verbose > 1:
            print("using generic version")
        phi = math.atan2(nVec.y, uVec.y)
        chi = math.acos(vVec.y)
        omega = math.atan2(vVec.z, -1. * vVec.x)

    # put together the result
    result = [phi, chi, omega]
    if degrees:
        result = [math.degrees(val) for val in result]
    for (i, val) in enumerate(result):
        if abs(val) == 0.:
            result[i] = 0.
    return tuple(result)

def __genRotationDict(rotation):
    """
    Generate the dict used for creating attributes.
    """
    (angle, axis) = rotation
    axis = [str(int(val)) for val in axis]

    result = {}
    result["val"]    = str(angle)
    if axis[0] != '0' or axis[1] != '0' or axis[2] != '1':
        result["axis-x"] = axis[0]
        result["axis-y"] = axis[1]
        result["axis-z"] = axis[2]
    return result

ATOL_ORIENTATION = 1.e-15
def checkRotation(rotation):
    '''Determine if the supplied matrix adheres to the rules of a rotation matrix'''
    # determinant mush be +/- 1
    determinant = np.abs(np.linalg.det(rotation))
    if np.abs(determinant) - 1. > 1.e-15:
        raise RuntimeError('Determinant must be +-1. Found %f' % determinant)

    # rotation matrix is orthogonal (inverse == transpose)
    inverse = np.linalg.inv(rotation)
    transpose = np.transpose(rotation)
    if not np.allclose(inverse, transpose, atol=ATOL_ORIENTATION):
        raise RuntimeError(str(inverse) + ' != ' + str(transpose))

def generateRotation(axis, angle, radians=True):
    if not radians:
        angle = np.radian(angle)

    sqr_a = axis.x*axis.x
    sqr_b = axis.y*axis.y
    sqr_c = axis.z*axis.z
    len2  = sqr_a+sqr_b+sqr_c

    k2    = math.cos(angle)
    k1    = (1.0-k2)/len2
    k3    = math.sin(angle)/math.sqrt(len2)
    k1ab  = k1*axis.x*axis.y
    k1ac  = k1*axis.x*axis.z
    k1bc  = k1*axis.y*axis.z
    k3a   = k3*axis.x
    k3b   = k3*axis.y
    k3c   = k3*axis.z

    rotation = np.matrix([[k1*sqr_a+k2, k1ab-k3c, k1ac+k3b],
                          [k1ab+k3c, k1*sqr_b+k2, k1bc-k3a],
                          [k1ac-k3b, k1bc+k3a, k1*sqr_c+k2]],
                         dtype=np.float)
    rotation[np.abs(rotation) < 1.e-15] = 0.

    checkRotation(rotation)
    return rotation

def calcEuler(rotation, convention):
    R=rotation
    angles = np.zeros(3, dtype=np.float)
    XYZ=np.array([[1,0,0],[0,1,0],[0,0,1]], dtype=np.float) # identity matrix
    #decode the convention: code X=0, Y=1, Z=2
    convention=convention.upper().translate(maketrans("XYZ","012"))
    first,second,last=int(convention[0]),int(convention[1]),int(convention[2])
    tb = 1 if (first+second+last==3) else 0
    par12 = 1 if ((last-second)%3 ==1) else -1
    par01 = 1 if ((second-first)%3 ==1) else -1
    s3=(1-tb-tb*par12)*R[(last+tb*par12)%3,(last-par12)%3]
    c3=(tb-(1-tb)*par12)*R[(last+tb*par12)%3,(last+par12)%3]
    angles[2]=getAngle(s3,c3)
    R1R2=np.dot(R, generateRotation(Vector(XYZ[last]),-1.*angles[2]))
    s1=par01*R1R2[(first-par01)%3,(first+par01)%3]
    c1=R1R2[second,second]
    s2=par01*R1R2[first,3-first-second]
    c2=R1R2[first,first]
    angles[1]=getAngle(s2,c2)
    angles[0]=getAngle(s1,c1)
    #note equivalent solution o1-180,-o2,o3-180 for ABA
    #note equivalent solution o1-180,180-o2,o3-180 for ABC
    angles[abs(angles) < 1.e-5] = 0.
    return angles

#https://en.wikipedia.org/wiki/Euler_angles
def getYZY(rotation):
    angles = calcEuler(rotation, 'YZY')

    # if the z-rotation is missing, just set
    # everything to the first y-rotation
    if angles[1] == 0.:
        angles = np.array([0., 0., angles[0]+angles[2]])

    # make sure that everything has angle <= 2pi
    angles = angles % (2. * np.pi)
    angles[np.abs(angles) < 1.e-15] = 0.

    return angles

def getZYZ(rotation):
    angles = calcEuler(rotation, 'ZYZ')

    # if the y-rotation is missing, just set
    # everything to the first z-rotation
    if angles[1] == 0.:
        angles = np.array([0., 0., angles[0]+angles[2]])

    # make sure that everything has angle <= 2pi
    angles = angles % (2. * np.pi)
    angles[np.abs(angles) < 1.e-15] = 0.

    return angles

def makeLocation(instr, det, name, center, rotations, tol_ang=TOLERANCE):
    """
    Make a location appropriate for an instrument component.
    """
    # set angles to zero if they aren' already
    for i, rot in enumerate(rotations):
        if abs(rot[0]) < 1.e-15:
            rotations[i] = [0., rot[1]]

    # location includes first rotation
    sub = instr.addLocation(det,
                            x=center[0], y=center[1], z=center[2],
                            name=name, rot_y=rotations[0][0])
    if abs(rotations[1][0]) > tol_ang: # second rotation
        sub = le.SubElement(sub, "rot",
                            __genRotationDict(rotations[1]))
        if abs(rotations[2][0]) > tol_ang: # third rotation angle
            le.SubElement(sub, "rot", __genRotationDict(rotations[2]))

class Rectangle:
    NPOINTS = 4
    BOTTOMLEFT = 1
    TOPLEFT = 2
    TOPRIGHT = 3
    BOTTOMRIGHT = 4

    def __init__(self, p1, p2, p3, p4, tolerance_len=TOLERANCE, tolerance_ang=TOLERANCE):
        """
        The points should be specified as lower-left (p1) in a clockwise order.
        """
        p1 = Vector(p1)
        p2 = Vector(p2)
        p3 = Vector(p3)
        p4 = Vector(p4)
        self._tol_len = tolerance_len
        self._tol_ang = tolerance_ang

        # Are they 4 edges of a 2D plane arrange so consecutive
        # points with wrap are edges
        d1 = self.__magnitudeSq(p1, p2)
        d2 = self.__magnitudeSq(p1, p3)
        d3 = self.__magnitudeSq(p1, p4)
        if d1 > d2 or d3 > d2:
            if d1 > d2:
                specific = " (d1=|p1-p2|=%f > d2=|p1-p3|=%f)" % (d1, d2)
            if d3 > d2:
                specific = " (d3=|p1-p4|=%f > d2=|p1-p3|=%f)" % (d3, d2)
            raise RuntimeError("The Points are in the incorrect order"+specific)


        # Parallelogram opposite side from p1 to p4 is parallel and
        # equal lengths.
        left = p2-p1
        right = p4-p3
        if abs(left.length - right.length) > self._tol_len:
            msg = "Left and right sides are not equal length: " \
                + "left=%f != right=%f (diff=%f)" \
                % (left.length, right.length, abs(left.length-right.length))
            raise RuntimeError(msg)

        top = p2-p3
        bottom = p4-p1
        if abs(top.length - bottom.length) > self._tol_len:
            msg = "Top and bottom sides are not equal length: "\
                + "top=%f != bottom=%f (diff=%f)" \
                % (top.length, bottom.length, abs(top.length-bottom.length))
            raise RuntimeError(msg)

        # opposite sides should add up to zero length vector
        for (i,num) in zip(('x', 'y', 'z'), left+right):
            if abs(num) > self._tol_len:
                msg = "Points not rectangle corners (num[%s]=%f > %f)" \
                                       % (i,num, self._tol_len)
                raise RuntimeError(msg)

        # Make sure the points are at right angles. Eliminates collinear
        # case too
        dotProd = left.dot(bottom)
        if abs(dotProd) > self._tol_len:
            msg = " This is not a rectangle (p2-p1)dot(p4-p1) = %f > %f" \
                % (dotProd, self._tol_len)
            raise RuntimeError(msg)

        self.__center = (p1 + p2 + p3 + p4) / float(Rectangle.NPOINTS)
        self.__calcOrientation(p1, p2, p3, p4)
        self.__points = (p1, p2, p3, p4)

    def __magnitudeSq(self, first, second):
        """
        Finds the square of the magnitude of the difference of two arrays
        with three elements.
        @param first  The first array
        @param second The second array
        @return  The magnitude squared of (first-second)
        """
        temp = first - second
        return temp.dot(temp)

    def __calcOrientation(self, p1, p2, p3, p4):
        """
        Calculates the orientation matrix for these points.
        @return  The 9 element orientation matrix for these points.
        """
        # calculate the direction vectors
        xvec =  .5*(p4 + p3) - self.__center
        yvec = -.5*(p1 + p4) + self.__center

        # normalize the vectors
        zvec = xvec.cross(yvec)
        xvec.normalize()
        yvec.normalize()
        zvec.normalize()

        #print("x =", xvec, "y =", yvec, "z =", zvec)
        #print("x dot y =", xvec.dot(yvec))
        #print("x dot z =", xvec.dot(zvec))
        #print("y dot z =", yvec.dot(zvec))

        # xvec should change most in x direction
        self.__orient = np.array([xvec.data,yvec.data,zvec.data],
                                 dtype=np.float)

    def __euler_rotations_zyz(self):
        angles = np.degrees(getZYZ(self.__orient))

        # output for each: rotation angle (in degrees), axis of rotation
        alpha_rot = [angles[0], (0., 0., 1.)]
        beta_rot  = [angles[1], (0., 1., 0.)]
        gamma_rot = [angles[2], (0., 0., 1.)]

        return (alpha_rot, beta_rot, gamma_rot)

    def __euler_rotations_yzy(self):
        angles = np.degrees(getYZY(self.__orient))

        alpha_rot = [-1.*angles[0], (0., 1., 0.)]
        beta_rot  = [-1.*angles[1], (0., 0., 1.)]
        gamma_rot = [-1.*angles[2], (0., 1., 0.)]

        return (alpha_rot, beta_rot, gamma_rot)

    def __width(self):
        width = self.__points[3] - self.__points[0]
        return width.length

    def __height(self):
        height = self.__points[1] - self.__points[0]
        return height.length

    width = property(__width, doc="Width of the rectangle")
    height = property(__height, doc="Height of the rectangle")
    center = property(lambda self: Vector(self.__center[:]),
                      doc="Center of the rectangle")
    orientation = property(lambda self: self.__orient[:],
                           doc="Orientation as a set of three basis vectors")
    euler_rot = property(__euler_rotations_zyz)
    euler_rot_yzy = property(__euler_rotations_yzy)
    points = property(lambda self: self.__points[:],
                      doc="The four corners originally supplied in the constructor")

    def makeLocation(self, instr, det, name, technique="orientation"):
        """
        @param instr The root instrument that does most of the work.
        @param det   The detector component.
        @param name  The name of the bank.
        """
        if not HAS_LXML:
            raise RuntimeError("lxml is not loaded")

        # cache within the function
        technique = technique.upper()
        if technique == "ORIENTATION":
            rotations = list(self.__euler_rotations_yzy())
        elif technique == "UV":
            # 'simple' euler rotation calculation
            u = self.__points[3]-self.__points[0] # lower right - lower left
            v = self.__points[1]-self.__points[0] #  upper left - lower left
            rotations = list(getEuler(u, v, degrees=True))
            rotations[0] = [rotations[0], (0., 1., 0.)]
            rotations[1] = [rotations[1], (0., 0., 1.)]
            rotations[2] = [rotations[2], (0., 1., 0.)]
        else:
            raise RuntimeError("Do not understand technique '%s'" % technique)

        rotations.reverse() # may need this

        makeLocation(instr, det, name, self.__center, rotations, self._tol_ang)
