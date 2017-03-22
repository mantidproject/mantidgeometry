# Much of this code was not so casually ported from
#
# https://flathead.ornl.gov/repos/TranslationService/trunk/sns-translation-client/sns-translation-core/src/main/java/gov/ornl/sns/translation/geometry/calc/helpers/RectCorners.java
#

import math
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

    def __init__(self, x=None, y=None, z=None):
        # set the data
        if y is None and z is None:
            if x is None:
                self.__data = [0.]*Vector.LENGTH
            else:
                try:
                    self.__data = x.__data[:]
                except AttributeError, e:
                    if len(x) != Vector.LENGTH:
                        msg = "Expected 3 values, found %d" % len(x)
                        raise RuntimeError(msg)
                    self.__data = x[:Vector.LENGTH]
        else:
            self.__data = [x, y, z]

        # convert the values to floats
        self.__data = [float(num) for num in self.__data]

        # sanity check the numbers
        for num in self.__data:
            if math.isnan(num):
                raise RuntimeError("Encountered NaN")

    x = property(lambda self: self.__data[0])
    y = property(lambda self: self.__data[1])
    z = property(lambda self: self.__data[2])

    def cross(self, other):
        """
        Calculate the cross product of this with another vector.
        """
        result = [0.]*Vector.LENGTH
        result[0] = self.y*other.z - self.z*other.y
        result[1] = self.z*other.x - self.x*other.z
        result[2] = self.x*other.y - self.y*other.x

        return Vector(result)

    def dot(self, other):
        """
        Calculate the dot product of this with another vector.
        """
        result = 0.
        for (a, b) in zip (self.__data, other.__data):
            result += a*b
        return result

    def normalize(self):
        """
        Set the unit length to one
        """
        if self.isCardinal(True):
            return self

        length = self.length # cache value
        if abs(length) < TOLERANCE:
            raise RuntimeError("Zero vector of zero length")
        if abs(length -1.) > TOLERANCE:
            self.__data = [it/length for it in self.__data]

        # set near zeros to zero
        for i in range(len(self.__data)):
            if abs(self.__data[i]) < TOLERANCE:
                self.__data[i] = 0.

        return self

    def isCardinal(self, resetValues=False):
        """
        Returns true iff the vector is (1,0,0), (0,1,0) or (0,0,1).
        """
        if abs(self.length-1.) > TOLERANCE:
            return False
        x_is_zero = abs(self.__data[0]) <TOLERANCE
        y_is_zero = abs(self.__data[1]) <TOLERANCE
        z_is_zero = abs(self.__data[2]) <TOLERANCE

        def sign(number):
            """
            Specialized version of sign intended to be used with +/-1 only
            """
            return number/abs(number)

        # x = +/-1
        if abs(abs(self.__data[0])-1.) <TOLERANCE:
            if y_is_zero and z_is_zero:
                if resetValues:
                    self.__data[0] = sign(self.__data[0])
                    self.__data[1] = 0.
                    self.__data[2] = 0.
                return True
        # y = +/-1
        if abs(abs(self.__data[1])-1.) <TOLERANCE:
            if x_is_zero and z_is_zero:
                if resetValues:
                    self.__data[0] = 0.
                    self.__data[1] = sign(self.__data[1])
                    self.__data[2] = 0.
                return True
        # z = +/-1
        if abs(abs(self.__data[2])-1.) <TOLERANCE:
            if x_is_zero and y_is_zero:
                if resetValues:
                    self.__data[0] = 0.
                    self.__data[1] = 0.
                    self.__data[2] = sign(self.__data[2])
                return True

        # otherwise no
        return False

    def __getitem__(self, key):
        return self.__data[key]

    def __eq__(self, other):
        other = Vector(other)
        if not self.x == other.x:
            return False
        if not self.y == other.y:
            return False
        if not self.z == other.z:
            return False
        return True

    def __add__(self, other):
        temp = Vector()
        for i in range(Vector.LENGTH):
            temp.__data[i] = self.__data[i] + other.__data[i]
        return temp

    def __sub__(self, other):
        temp = Vector()
        for i in range(Vector.LENGTH):
            temp.__data[i] = self.__data[i] - other.__data[i]
        return temp

    def __div__(self, other):
        other = float(other) # only allow divide by a scalar
        temp = Vector(self)
        for i in range(Vector.LENGTH):
            temp.__data[i] /= float(other)
        return temp

    def __mul__(self, other):
        other = float(other) # only allow multiply by a scalar
        temp = Vector(self)
        for i in range(Vector.LENGTH):
            temp.__data[i] *= float(other)
        return temp

    def __rmul__(self, other):
        return self * other

    def __repr__(self):
        temp = [str(it) for it in self.__data]
        return "(%s)" % (", ".join(temp))

    def __len__(self):
        return Vector.LENGTH

    length = property(lambda self: math.sqrt(self.dot(self)))

UNIT_X = Vector(1.,0.,0.)
UNIT_Y = Vector(0.,1.,0.)
UNIT_Z = Vector(0.,0.,1.)

def getAngle(y, x, debug=False, onlyPositive=True):
    """
    Returns the angle in radians using atan2.
    """
    if debug:
        print "getAngle(%f, %f)=" % (y, x),
    angle = math.atan2(y, x)
    if onlyPositive and angle < 0:
        angle += 2*math.pi
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
        self.__orient = []
        self.__orient.append(xvec)
        self.__orient.append(yvec)
        self.__orient.append(zvec)

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
