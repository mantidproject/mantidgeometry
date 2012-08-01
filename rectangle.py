# Much of this code was not so casually ported from
#
# https://flathead.ornl.gov/repos/TranslationService/trunk/sns-translation-client/sns-translation-core/src/main/java/gov/ornl/sns/translation/geometry/calc/helpers/RectCorners.java
#

import math

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
                        raise RuntimeError("Expected 3 values, found %d" % len(x))
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
        length = self.length # cache value
        if abs(length) < TOLERANCE:
            raise RuntimeError("Zero vector of zero length")
        if abs(length -1.) < TOLERANCE:
            return # nothing to do
        self.__data = [it/length for it in self.__data]

        return self

    def __getitem__(self, key):
        return self.__data[key]

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

class Rectangle:
    NPOINTS = 4
    BOTTOMLEFT = 1
    TOPLEFT = 2
    TOPRIGHT = 3
    BOTTOMRIGHT = 4

    def __init__(self, p1, p2, p3, p4):
        p1 = Vector(p1)
        p2 = Vector(p2)
        p3 = Vector(p3)
        p4 = Vector(p4)

        # Are they 4 edges of a 2D plane arrange so consecutive
        # points with wrap are edges
        d1 = self.__magnitudeSq(p1, p2)
        d2 = self.__magnitudeSq(p1, p3)
        d3 = self.__magnitudeSq(p1, p4)
        if d1 > d2 or d3 > d2:
            raise RuntimeError("The Points are in the incorrect order")


        # Parallelogram opposite side from p1 to p4 is parallel and 
        # equal lengths.
        for num in p2+p4-p1-p3:
            if abs(num) > TOLERANCE:
                raise RuntimeError(" points not rectangle corners")

        # Make sure the points are at right angles. Eliminates collinear
        # case too
        dotProd = (p2 - p1).dot(p4 - p1)

        # will catch the collinear case here
        if abs(dotProd) > TOLERANCE:
            raise RuntimeError(" This is not a rectangle")

        self.__center = (p1 + p2 + p3 + p4) / float(Rectangle.NPOINTS)
        self.__calcOrientation(p1, p2, p3, p4)

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
        xvec.normalize()
        yvec.normalize()

        # xvec should change most in x direction
        self.__orient = []
        self.__orient.append(xvec)
        self.__orient.append(yvec)
        self.__orient.append(xvec.cross(yvec))

    def __rotations(self):
        """TODO this doesn't do anything yet"""
        # output for each: rotation angle (in degrees), axis of rotation
        phi_rot = [0., (1., 0., 0.)]
        chi_rot = [0., (0., 1., 0.)]
        omega_rot = [0., (1., 0., 0.)]
        return (omega_rot, chi_rot, phi_rot)

    center = property(lambda self: self.__center[:])
    orientation = property(lambda self: self.__orient[:])
    rotations = property(__rotations)


if __name__ == "__main__":
    rect = Rectangle((0,0,0), (1,0,0), (1,1,0), (0,1,0))
    print "center =", rect.center
    print "orientation =", rect.orientation
    print "rotations = ", rect.rotations
