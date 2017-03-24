# Much of this code was not so casually ported from
#
# https://flathead.ornl.gov/repos/TranslationService/trunk/sns-translation-client/sns-translation-core/src/main/java/gov/ornl/sns/translation/geometry/calc/helpers/RectCorners.java
#

import math
import numpy as np
HAS_LXML = True
try:
    from lxml import etree as le # python-lxml on rpm based systems
except ImportError, e:
    print "WARNING: Failed to load lxml. Xml output turned off for rectangle.py"
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
        if abs(length - 1.) > TOLERANCE:
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
        print "getAngle(%f, %f)=" % (y, x),
    angle = math.atan2(y, x)
    if onlyPositive and angle < 0.:
        angle += 2.*math.pi
    if debug:
        print math.degrees(angle)
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

    if verbose:
        print "orthonormal:", uVec, vVec, nVec

    # calculate the angles
    import math

    if vVec.y == 1.: # chi rotation is 0, just rotate about z-axis
        if verbose > 1:
            print "chi rotation is 0"
        phi = math.atan2(nVec.x, nVec.z)
        chi = 0.
        omega = 0.
    elif vVec.y == -1.:# chi rotation is 180 degrees
        if verbose > 1:
            print "chi rotation is 180 degrees"
        phi = -1. * math.atan2(nVec.x, nVec.z)
        if phi == -1.* math.pi:
            phi = math.pi
        chi = math.pi
        omega = 0.
    else:
        if verbose > 1:
            print "using generic version"
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

def generateRotation(axis, angle, radians=True):
    if not radians:
        angle = np.radian(angle)
    c,s = np.cos(angle), np.sin(angle)

    rotation = None
    if axis == UNIT_X:
        rotation = np.matrix('1 0 0; 0 {} {}; 0 {} {}'.format(c,-s,s,c))
    elif axis == UNIT_Y:
        rotation = np.matrix('{} 0 {}; 0 1 0; {} 0 {}'.format(c,s,-s,c))
    elif axis == UNIT_Z:
        rotation = np.matrix('{} {} 0; {} {} 0; 0 0 1'.format(c,-s,s,c))
    else:
        raise ValueError('Unsupported rotation axis: %s' % str(axis))

    rotation[np.abs(rotation) == 0.] = 0.
    return rotation

#https://en.wikipedia.org/wiki/Euler_angles
def getYZY(orientation):
    return np.array((0., 0., 0.), dtype=np.float)

def getZYZ(orientation):
    return np.array((0., 0., 0.), dtype=np.float)

def makeLocation(instr, det, name, center, rotations, tol_ang=TOLERANCE):
    """
    Make a location appropriate for an instrument component.
    """
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

        #print "x =", xvec, "y =", yvec, "z =", zvec
        #print "x dot y =", xvec.dot(yvec)
        #print "x dot z =", xvec.dot(zvec)
        #print "y dot z =", yvec.dot(zvec)

        # xvec should change most in x direction
        self.__orient = np.array([xvec.data,yvec.data,zvec.data],
                                 dtype=np.float)

    def __euler_rotations_zyz(self):
        """
        The Euler angles are about the z (alpha), then unrotated y (beta),
        then unrotated z (gamma). This is described in equations and pretty
        pictures in Arfken pages 199-200.

        George Arfken, Mathematical methods for physicists, 3rd edition
        Academic Press, 1985
        """
        # calculate beta
        beta = getAngle(UNIT_Z.cross(self.__orient[2]).length,
                        UNIT_Z.dot(self.__orient[2]))

        if abs(math.sin(beta)) < self._tol_ang: # special case for numerics
            # since alpha and gamma are coincident, just force gamma to be zero
            gamma = 0.

            # calculate alpha
            cos_beta = UNIT_Z.dot(self.__orient[2])
            if cos_beta == 1. or cos_beta == -1.:
                alpha = getAngle(UNIT_X.dot(self.__orient[1]),
                                 UNIT_Y.dot(self.__orient[1]))
            else:
                msg = "Equations aren't worked out for cos(beta)=%f" % cos_beta
                raise RuntimeError(msg)

        else: # go with the traditional route
            # calculate alpha
            alpha = getAngle(UNIT_Z.dot(self.__orient[1]),
                             UNIT_Z.dot(self.__orient[0]))

            # calculate gamma
            gamma = getAngle(UNIT_Y.dot(self.__orient[2]),
                             -1.*UNIT_X.dot(self.__orient[2]))

        # output for each: rotation angle (in degrees), axis of rotation
        alpha_rot = [math.degrees(alpha), (0., 0., 1.)]
        beta_rot  = [math.degrees(beta),  (0., 1., 0.)]
        gamma_rot = [math.degrees(gamma), (0., 0., 1.)]
        return (alpha_rot, beta_rot, gamma_rot)

    def __euler_rotations_yzy(self):
        print(self.__orient) # wikipedia says zyz

        gamma = getAngle(-1.*self.__orient[2][0], self.__orient[2][1])
        if abs(gamma) == 0.: gamma = 0.

        cg = math.cos(gamma) # c3
        sg = math.sin(gamma) # s3

        if abs(cg) > abs(sg):
            beta = getAngle(self.__orient[2][2], -1.*self.__orient[2][0]/cg)
        else:
            beta = getAngle(self.__orient[2][2], self.__orient[2][1]/sg)
        print cg, sg

        alpha = getAngle(self.__orient[1][2], self.__orient[2][0])

        return 0.,beta,gamma

    def __euler_rotations_yzym(self):
        """
        Taken from mantid's Quat::getEulerAngles('YZY') with the
        conditionals calculated out.
        """
        #// Cannot be XXY, XYY, or similar. Only first and last may be the same: YXY
        #if ((conv[0] == conv[1]) || (conv[2] == conv[1]))
        #  throw std::invalid_argument("Wrong convention name (repeated indices)");

        #boost::replace_all(conv, "X", "0");
        #boost::replace_all(conv, "Y", "1");
        #boost::replace_all(conv, "Z", "2");

        #std::stringstream s;
        #s << conv[0] << " " << conv[1] << " " << conv[2];

        #int first, second, last;
        #s >> first >> second >> last;
        first, second, last = 1,2,1

        #// Do we want Tait-Bryan angles, as opposed to 'classic' Euler angles?
        #const int TB =
        #    (first * second * last == 0 && first + second + last == 3) ? 1 : 0;
        TB = 0

        #const int par01 = ((second - first + 9) % 3 == 1) ? 1 : -1;
        par01 = 1
        #const int par12 = ((last - second + 9) % 3 == 1) ? 1 : -1;
        par12 = -1

        #std::vector<double> angles(3);

        #const DblMatrix R = DblMatrix(this->getRotation());
        R = self.__orient

        #const int i = (last + TB * par12 + 9) % 3;
        i = 1
        #const int j1 = (last - par12 + 9) % 3;
        j1 = 2
        #const int j2 = (last + par12 + 9) % 3;
        j2 = 0

        #const double s3 = (1.0 - TB - TB * par12) * R[i][j1];
        s3 = R[i,j1] # 1,2
        #const double c3 = (TB - (1.0 - TB) * par12) * R[i][j2];
        c3 = R[i,j2] # 1,0

        #V3D axis3(0, 0, 0);
        #axis3[last] = 1.0;
        axis3 = Vector(0,0,1)

        #angles[2] = atan2(s3, c3) * rad2deg;
        gamma = atan2(s3, c3)


        '''
        DblMatrix Rm3(Quat(-angles[2], axis3).getRotation());
        DblMatrix Rp = R * Rm3;

        const double s1 =
             par01 * Rp[(first - par01 + 9) % 3][(first + par01 + 9) % 3];
        const double c1 = Rp[second][second];
        const double s2 = par01 * Rp[first][3 - first - second];
        const double c2 = Rp[first][first];

        angles[0] = atan2(s1, c1) * rad2deg;
        angles[1] = atan2(s2, c2) * rad2deg;

        return angles;'''
        return 0,0,0


    def __euler_rotations_yzyold(self):
        """
        This is very similar to __euler_roatations_zyz except the rotations
        are about the y (alpha), then unrotated z (beta), then unrotated
        y (gamma).
        """
        rotated_x = self.__orient[0]
        rotated_y = self.__orient[1]
        rotated_z = self.__orient[2]

        # calculate beta
        beta = getAngle(UNIT_Y.cross(rotated_y).length,
                        UNIT_Y.dot(rotated_y))

        if abs(math.sin(beta)) < self._tol_ang: # special case for numerics
            print "small beta:", beta, math.sin(beta)
            # since alpha and gamma are coincident, just force gamma to be zero
            gamma = 0.

            # calculate alpha
            alpha = getAngle(UNIT_Z.dot(rotated_x),
                             UNIT_Z.dot(rotated_z))
        else:
            # calculate alpha
            alpha = getAngle(UNIT_Y.dot(rotated_z),
                             -1.*UNIT_Y.dot(rotated_x))

            # calculate gamma
            gamma = getAngle(UNIT_Z.dot(rotated_y),
                             UNIT_X.dot(rotated_y))

        # output for each: rotation angle (in degrees), axis of rotation
        alpha_rot = [-1.*math.degrees(alpha), (0., 1., 0.)]
        beta_rot  = [-1.*math.degrees(beta),  (0., 0., 1.)]
        gamma_rot = [-1.*math.degrees(gamma), (0., 1., 0.)]
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
