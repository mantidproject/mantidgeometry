#!/usr/bin/env python

# Much of the information for this is taken from ~zjn/idl/detpos.pro
from helper import INCH_TO_METRE, DEG_TO_RAD, MantidGeom
from rectangle import Rectangle, Vector
from lxml import etree as le # python-lxml on rpm based systems
from math import cos, sin, radians, pi

# All of the tubes are 40" long with a 2mm gap between tubes
TUBE_LENGTH = 40.*.0254 # 1m long matches better in bank4
AIR_GAP = .002

# Indices for the four corners of an eight-pack
LL = 0*128+0   # LOWER LEFT CORNER
UL = 0*128+127 # UPPER LEFT CORNER
LR = 7*128+0   # LOWER RIGHT CORNER
UR = 7*128+127 # UPPER RIGHT CORNER

def makeLoc(instr, det, name, x, y, z, rot, rot_inner=None, rot_innermost=None):
    sub = instr.addLocation(det, x=x, y=y, z=z, rot_y=rot, name=name)
    if rot_inner is not None:
        sub = le.SubElement(sub, "rot", **{"val":str(rot_inner)})
        if rot_innermost is not None:
            le.SubElement(sub, "rot",
                          **{"val":str(rot_innermost),
                             "axis-x":"0", "axis-y":"1", "axis-z":"0"})

def makeRectLoc(instr, det, name, rect):
    center = rect.center
    rotations = rect.euler_rot
    sub = instr.addLocation(det, x=center[0], y=center[1], z=center[2],
                            name=name, rot_z=rotations[0][0])
    if rotations[1][0] != 0.: # second rotation angle about y-axis
        sub = le.SubElement(sub, "rot", genRotationDict(rotations[1]))
        if rotations[2][0] != 0.: # third rotation angle about z-axis
            le.SubElement(sub, "rot", genRotationDict(rotations[2]))

def makeAttrs(idstart):
    """Return list of pixel ids appropriate for rectangular detectors."""
    return {"idstart":idstart, "idfillbyfirst":"y", "idstepbyrow":128}

def makeIds(numBanks, offset, size):
    ids = []
    for i in range(numBanks):
        ids.extend((i*size+offset, (i+1)*size+offset-1, None))
    return ids

class DetPack:
    def __init__(self, tuberadius=0., ysize=0., airgap=0., xsize=0.,
                 xnum=8, ynum=128,
                 xstart=None, xstartdiff=0., ystart=None, ystartdiff=0.,
                 debug=False):
        """
        Create a n-pack of detector tubes where y is along the tube and x 
        is between tubes.

        @param tuberadius : The radius if the detector tube
        @param airgap : Gap between tubes
        @param xsize  : The extent of the pack (tube centers)
        @param ysize  : The length of the tube
        @param xnum   : Number of tubes (default=8)
        @param ynum   : Number of pixels along a tube (default=128)
        @param xstart : Used to calculate tube position. Default is 
        to put tubes centered at zero.
        @param xstartdiff : Offset (in metres) to add to the xstart 
        calculation. This is ignored if xstart is specified.
        @param ystart : Used to calculate pixel position. Default is
        to center the tube at zero.
        @param xstartdiff : Offset (in metres) to add to the ystart 
        calculation. This is ignored if ystart is specified.
        @param debug  : enable debug printing (default=False)
        """
        self.__debug = bool(debug)

        self.radius = abs(float(tuberadius))
        if (self.radius) <= 0.:
            raise RuntimeError("Need to specify a tube radius")

        if xnum <= 0:
            raise ValueError("Cannot have xnum = %d (<= 0)" % xnum)
        if xsize != 0.:
            xsize  = float(xsize)
            self.xstep = xsize/float(xnum-1) # 1 is for centers
        else:
            self.xstep = 2.*tuberadius + airgap
            xsize = float(xnum) * self.xstep
        self.xnum   = int(xnum)
        if xstart is not None:
            self.xstart = float(xstart)
        else:
            self.xstart = -1. * (.5*float(self.xnum) - .5) * self.xstep \
                + xstartdiff

        if self.__debug:
            print "XSIZE: [%f,%f]" % (self.xstart, self.xstep), \
                xsize, self.xstep*self.xnum, \
                (xsize-self.xstep*self.xnum)

        # default values
        self.__z = [0.]*self.xnum
        self.__tubes = [i+1 for i in range(self.xnum)]

        if ynum <= 0:
            raise ValueError("Cannot have ynum = %d (<= 0)" % ynum)
        self.ysize  = float(ysize)
        self.ystep = ysize/float(ynum)
        self.ynum   = int(ynum)
        if ystart is not None:
            self.ystart = float(ystart)
        else:
            self.ystart = -1. * (.5*float(self.ynum) - .5) * self.ystep \
                + ystartdiff

        if self.__debug:
            print "YSIZE:", ysize, self.ystep*self.ynum, \
                (ysize-self.ystep*self.ynum)

        self.namepixel = "pixel"
        self.nametube  = "tube"
        self.namepack  = "pack"

    def setNames(self, pixel=None, tube=None, pack=None):
        if pixel is not None:
            self.namepixel = pixel
        if tube is not None:
            self.nametube = tube
        if pack is not None:
            self.namepack = pack

    def setPosZ(self, z):
        if len(z) != self.xnum:
            msg = "Must set the same number of z-values (%d) as x-values (%d)" % (len(z), self.xnum)
            raise ValueError(msg)
        self.__z = list(z)

    def setTubeNumbers(self, numbers):
        if len(numbers) != self.xnum:
            msg = "Must set the same number of tubes (%d) as x-values (%d)" % (len(numbers), self.xnum)
            raise ValueError(msg)
        self.__tubes = list(numbers)


    def writePack(self, instr, comment=""):
        if len(comment) > 0:
            instr.addComment(comment)
        det = instr.makeTypeElement(self.namepack)
        le.SubElement(det, "properties")
        det = instr.addComponent(self.nametube, root=det, blank_location=False)
        debug_ids = [0, self.xnum-1]
        for (j, z, tube) in zip(range(self.xnum), self.__z, self.__tubes):
            name="tube%d"  % tube
            x = float(j)*self.xstep + self.xstart
            if self.__debug and (j in debug_ids):
                print "x[%d] = %f" % (j, x)
            instr.addLocation(det, x, 0., z, name=name)

    def writeTube(self, instr, comment=""):
        if len(comment) > 0:
            instr.addComment(comment)
        tube = instr.makeTypeElement(self.nametube, {"outline":"yes"})
        le.SubElement(tube, "properties")
        tube = instr.addComponent(self.namepixel, root=tube, blank_location=False)
        debug_ids = [0, self.ynum-1]
        for i in range(self.ynum):
            name = "pixel%d" % (i+1)
            y = float(i)*self.ystep + self.ystart
            if self.__debug and (i in debug_ids):
                print "y[%d] = %f" % (i, y)
            instr.addLocation(tube, 0., y, 0., name=name)

    def writePixel(self, instr, comment=""):
        if len(comment) > 0:
            instr.addComment(comment)
        instr.addCylinderPixel(self.namepixel,
                               (0.,0.,0.), # base (radius, theta, phi)
                               (0.,1.,0.), # axis
                               self.radius,   # pixel radius
                               abs(self.ystep))    # pixel height

    def __eq__(self, other):
        """Compare this to another object for equality. This does not compare names or debug."""
        def innerEq(debug, label, left, right):
            if left != right:
                if debug:
                    print label, "does not match", left, "!=", right
                return False
            return True

        try:
            debug = (self.__debug or other.__debug)
            if not innerEq(debug, "radius", self.radius, other.radius):
                return False
            if not innerEq(debug, "xstep", self.xstep, other.xstep):
                return False
            if not innerEq(debug, "xnum", self.xnum, other.xnum):
                return False
            if not innerEq(debug, "xstart", self.xstart, other.xstart):
                return False
            if not innerEq(debug, "ystep", self.ystep, other.ystep):
                return False
            if not innerEq(debug, "ynum", self.ynum, other.ynum):
                return False
            if not innerEq(debug, "ystart", self.ystart, other.ystart):
                return False
        except:
            return False # any exception means it is not a DetPack

        # getting this far means all tests passed
        return True

    def __ne__(self, other):
        """Compare this to another object for inequality"""
        return not self.__eq__(other)

if __name__ == "__main__":
    inst_name = "NOMAD"
    xml_outfile = inst_name+"_Definition.xml"

    # boiler plate stuff
    instr = MantidGeom(inst_name,
                       comment=" Created by Peter Peterson and Vickie Lynch",
                       valid_from="2012-07-01 00:00:01",
                       valid_to="2012-07-31 23:59:59")
    instr.addComment("DEFAULTS")
    instr.addSnsDefaults()
    instr.addComment("SOURCE")
    instr.addModerator(-19.5)
    instr.addComment("SAMPLE")
    instr.addSamplePosition()

    # monitors
    instr.addComment("MONITORS")
    instr.addMonitors([-0.879475,5.748782], ["monitor1", "monitor2"])

    # add the empty components
    for i in range(1,7):
        name = "Group%d" % i
        instr.addComponent(name, idlist=name)

    # add the id lists for groups
    info = instr.addDetectorIds("Group1", makeIds(14,     0, 8*128))
    info = instr.addDetectorIds("Group2", makeIds(23, 14336, 8*128))
    info = instr.addDetectorIds("Group3", makeIds(14, 37888, 8*128))
    info = instr.addDetectorIds("Group4", makeIds(12, 52224, 8*128))
    info = instr.addDetectorIds("Group5", makeIds(18, 64512, 8*128))
    ids = makeIds(18, 82944, 8*128)
    #print ids
    ids_len = len(ids)
    for i in range(3):
        ids.insert(0, ids[ids_len-1])
    del ids[ids_len:]
    #print ids
    info = instr.addDetectorIds("Group6", ids)
    #info = instr.addDetectorIds("Group6", makeIds(18, 82944, 8*128))

    # ---------- add in group1
    """
;;;source idl code
N_first=14
z0_first=6.41/8.45*3.2
x0_first=1.31/8.45*3.2
z1_first=3.86/8.45*3.2
x1_first=1.44/8.45*3.2
dx_first=x1_first-x0_first
dz_first=z1_first-z0_first
section=360/float(n_first)

onehundredtwentyeight=findgen(128) ; 0->127

for i=0,n_first-1 do begin
angle=(360*(i+.5)/float(N_first))*!dtor
x0=-x0_first*cos(section*i*!dtor)
y0=x0_first*sin(section*i*!dtor)
x1=-x1_first*cos(section*i*!dtor)
y1=x1_first*sin(section*i*!dtor)

for j=0,7 do begin
x0j=x0+j*(.0254+0.001)*sin(section*(i+.5)*!dtor)
y0j=y0+j*(.0254+0.001)*cos(section*(i+.5)*!dtor)
x1j=x1+j*(.0254+0.001)*sin(section*(i+.5)*!dtor)
y1j=y1+j*(.0254+0.001)*cos(section*(i+.5)*!dtor)
x(i*8+j,*)=x0j+(x1j-x0j)*(1-onehundredtwentyeight/128.)
y(i*8+j,*)=y0j+(y1j-y0j)*(1-onehundredtwentyeight/128.)
z(i*8+j,*)=z0_first+dz_first*(1-onehundredtwentyeight/128.)
end
end
    """
    n_first=14

    z0_first=6.41/8.45*3.2
    x0_first=1.31/8.45*3.2
    z1_first=3.86/8.45*3.2
    x1_first=1.44/8.45*3.2

    dx_first=x1_first-x0_first
    dz_first=z1_first-z0_first

    section=(2.*pi)/float(n_first)

    x=[]
    y=[]
    z=[]
    for i in range(n_first):
        angle = section*i
        x0=-x0_first*cos(angle)
        y0=x0_first*sin(angle)
        x1=-x1_first*cos(angle)
        y1=x1_first*sin(angle)

        for j in range(8):
            angle2 = section*(i+.5)
            x0j=x0+j*(.0254+0.001)*sin(angle2)
            y0j=y0+j*(.0254+0.001)*cos(angle2)

            xextent = -1. * dx_first * cos(angle2)
            yextent =       dx_first * sin(angle2)

            for k in range(128):
                k = float(k)
                x.append(x0j      + xextent *(1.-k/128.))
                y.append(y0j      + yextent *(1.-k/128.))
                z.append(z0_first + dz_first*(1.-k/128.))

    pack1 = DetPack(tuberadius = .5*.0254,
                    airgap     = AIR_GAP,
                    xstartdiff = (.0254+AIR_GAP),
                    ysize      = -1.*TUBE_LENGTH,
                    ystartdiff = -1.*TUBE_LENGTH/128.,
                    debug=False)
    pack1.setNames(pixel="onepixel", tube="tubedecreasing", pack="packdecreasing")

    group1 = instr.makeTypeElement("Group1")
    for i in range(n_first):
        offset = i*8*128
        bank = "bank%d" % (i+1)
        rect = Rectangle(
                         (-y[offset+UL], x[offset+UL], z[offset+UL]),
                         (-y[offset+LL], x[offset+LL], z[offset+LL]),
                         (-y[offset+LR], x[offset+LR], z[offset+LR]),
                         (-y[offset+UR], x[offset+UR], z[offset+UR])
                         )
       	det = instr.makeDetectorElement(pack1.namepack, root=group1)
       	rect.makeLocation(instr, det, bank)

    # ---------- add in group2
    """
;;; source idl code
N_second=23
;z0_second=5.05/8.45*3.2
;x0_second=2.24/8.45*3.2
;z1_second=2.54/8.45*3.2
;x1_second=2.24/8.45*3.2
z0_second=5.09/7.06*2.7-0.0095
x0_second=2.22/7.06*2.7
z1_second=2.45/7.06*2.7+0.0095
x1_second=2.22/7.06*2.7
dx_second=x1_second-x0_second
dz_second=z1_second-z0_second
section=360/float(n_second)

for i=0,n_second-1 do begin
  angle=(360*(i+.5)/float(N_second))*!dtor
  x0=-x0_second*cos(section*i*!dtor)
  y0=x0_second*sin(section*i*!dtor)
  x1=-x1_second*cos(section*i*!dtor)
  y1=x1_second*sin(section*i*!dtor)

  for j=0,7 do begin
    x0j=x0+j*(.0254+0.001)*sin(section*(i+.5)*!dtor)
    y0j=y0+j*(.0254+0.001)*cos(section*(i+.5)*!dtor)
    x1j=x1+j*(.0254+0.001)*sin(section*(i+.5)*!dtor)
    y1j=y1+j*(.0254+0.001)*cos(section*(i+.5)*!dtor)
    x((i+n_first)*8+j,*)=x0j+(x1j-x0j)*onehundredtwentyeight/128.
    y((i+n_first)*8+j,*)=y0j+(y1j-y0j)*onehundredtwentyeight/128.
    z((i+n_first)*8+j,*)=z0_second+dz_second*onehundredtwentyeight/128.
  end
end
    """
    n_second=23

    z0_second=5.09/7.06*2.7-0.0095
    x0_second=2.22/7.06*2.7
    z1_second=2.45/7.06*2.7+0.0095
    x1_second=2.22/7.06*2.7

    dx_second=x1_second-x0_second
    dz_second=z1_second-z0_second

    section=(2.*pi)/float(n_second)

    x=[]
    y=[]
    z=[]
    for i in range(n_second):
        angle = section*i
        x0=-x0_second*cos(angle)
        y0=x0_second*sin(angle)
        x1=-x1_second*cos(angle)
        y1=x1_second*sin(angle)

        for j in range(8):
            angle2 = section*(i+.5)
            x0j=x0+j*(.0254+0.001)*sin(angle2)
            y0j=y0+j*(.0254+0.001)*cos(angle2)
            x1j=x1+j*(.0254+0.001)*sin(angle2)
            y1j=y1+j*(.0254+0.001)*cos(angle2)

            for k in range(128):
                k = float(k)
                x.append(x0j       + (x1j-x0j)*k/128.)
                y.append(y0j       + (y1j-y0j)*k/128.)
                z.append(z0_second + dz_second*k/128.)

    pack2 = DetPack(tuberadius = .5*.0254,
                    airgap     = AIR_GAP,
                    #xstartdiff = (.0254+AIR_GAP),
                    ysize      = TUBE_LENGTH,
                    ystartdiff = TUBE_LENGTH/128.,
                    debug=False)
    pack2.setNames(pixel=pack1.namepixel, tube="tubeincreasing", pack="packincreasing")

    group2 = instr.makeTypeElement("Group2")
    for i in range(n_second):
        offset = i*8*128
        bank = "bank%d" % (i+15)
        rect = Rectangle(
                         (-y[offset+UL], x[offset+UL], z[offset+UL]),
                         (-y[offset+LL], x[offset+LL], z[offset+LL]),
                         (-y[offset+LR], x[offset+LR], z[offset+LR]),
                         (-y[offset+UR], x[offset+UR], z[offset+UR])
                         )
        det = instr.makeDetectorElement(pack2.namepack, root=group2)
        rect.makeLocation(instr, det, bank)

    # ---------- add in group3
    """
;;; source idl code
N_third=14
ii=[3,4,5,6,7,8,9,18,19,20,21,22,23,24]+.5
;z0_third=2.60/8.45*3.2
;x0_third=2.56/8.45*3.2
;z1_third=0/8.45*3.2
;x1_third=2.56/8.45*3.2
z0_third=2.59/7.06*2.7-0.0076
;x0_third=2.61/7.06*2.7
x0_third=1.00
z1_third=-0.04/7.06*2.7+.0076
;x1_third=2.61/7.06*2.7
x1_third=1.00
dx_third=x1_third-x0_third
dz_third=z1_third-z0_third
section=360/float(29)

for i=0,n_third-1 do begin
angle=(360*(ii(i)+.5)/float(N_third))*!dtor
x0=-x0_third*cos(section*ii(i)*!dtor)
y0=x0_third*sin(section*ii(i)*!dtor)
x1=-x1_third*cos(section*ii(i)*!dtor)
y1=x1_third*sin(section*ii(i)*!dtor)

for j=0,7 do begin
x0j=x0+j*(.0254+0.001)*sin(section*(ii(i)+.5)*!dtor)
y0j=y0+j*(.0254+0.001)*cos(section*(ii(i)+.5)*!dtor)
x1j=x1+j*(.0254+0.001)*sin(section*(ii(i)+.5)*!dtor)
y1j=y1+j*(.0254+0.001)*cos(section*(ii(i)+.5)*!dtor)
x((i+n_first+n_second)*8+j,*)=x0j+(x1j-x0j)*(1-onehundredtwentyeight/128.)
y((i+n_first+n_second)*8+j,*)=y0j+(y1j-y0j)*(1-onehundredtwentyeight/128.)
z((i+n_first+n_second)*8+j,*)=z0_third+dz_third*(1-onehundredtwentyeight/128.)
end
end
    """
    n_third=14

    z0_third=2.59/7.06*2.7-0.0076
    x0_third=1.00
    z1_third=-0.04/7.06*2.7+.0076
    x1_third=1.00

    dx_third=x1_third-x0_third
    dz_third=z1_third-z0_third
    section=(2.*pi)/float(29)
    
    x=[]
    y=[]
    z=[]
    ii=[3,4,5,6,7,8,9,18,19,20,21,22,23,24]
    for i in range(n_third):
        angle=section*(ii[i]+0.5)
        x0=-x0_third*cos(angle)
        y0=x0_third*sin(angle)
        x1=-x1_third*cos(angle)
        y1=x1_third*sin(angle)
    
        for j in range(8):
            angle2 = section*(ii[i]+1)
            x0j=x0+j*(.0254+0.001)*sin(angle2)
            y0j=y0+j*(.0254+0.001)*cos(angle2)
            x1j=x1+j*(.0254+0.001)*sin(angle2)
            y1j=y1+j*(.0254+0.001)*cos(angle2)
            for k in range(128):
                k = float(k)
                x.append(x0j       + (x1j-x0j)*k/128.)
                y.append(y0j       + (y1j-y0j)*k/128.)
                z.append(z0_third + dz_third*k/128.)

    pack3 = DetPack(tuberadius = .5*.0254,
                    airgap     = AIR_GAP,
                    #xstartdiff = (.0254+AIR_GAP),
                    ysize      = TUBE_LENGTH,
                    ystartdiff = TUBE_LENGTH/128.,
                    debug=False)
    pack3.setNames(pixel=pack2.namepixel, tube=pack2.nametube, pack=pack2.namepack)

    group3 = instr.makeTypeElement("Group3")
    for i in range(n_third):
        offset = i*8*128
        bank = "bank%d" % (i+15+23)
        rect = Rectangle(
                         (-y[offset+UL], x[offset+UL], z[offset+UL]),
                         (-y[offset+LL], x[offset+LL], z[offset+LL]),
                         (-y[offset+LR], x[offset+LR], z[offset+LR]),
                         (-y[offset+UR], x[offset+UR], z[offset+UR])
                         )
        det = instr.makeDetectorElement(pack3.namepack, root=group3)
        rect.makeLocation(instr, det, bank)

    # ---------- add in group4
    """
;;; source idl code
N_forth=12
ii=[2,3,4,5,6,7,13,14,15,16,17,18]+1
;z0_forth=-.2/8.45*3.2
;x0_forth=2.67/8.45*3.2
;z1_forth=-2.8/8.45*3.2
;x1_forth=2.08/8.45*3.2
z0_forth=-.28/7.06*2.7+.0016
x0_forth=2.66/7.06*2.7
z1_forth=-2.79/7.06*2.7-.0016
x1_forth=2.09/7.06*2.7
dx_forth=x1_forth-x0_forth
dz_forth=z1_forth-z0_forth
section=360/float(23)

for i=0,n_forth-1 do begin
  angle=(360*(ii(i)+.5)/float(N_forth))*!dtor
  x0=-x0_forth*cos(section*ii(i)*!dtor)
  y0= x0_forth*sin(section*ii(i)*!dtor)
  x1=-x1_forth*cos(section*ii(i)*!dtor)
  y1= x1_forth*sin(section*ii(i)*!dtor)

  for j=0,7 do begin
    x0j=x0+j*(.0254+0.001)*sin(section*(ii(i)+.5)*!dtor)
    y0j=y0+j*(.0254+0.001)*cos(section*(ii(i)+.5)*!dtor)
    x1j=x1+j*(.0254+0.001)*sin(section*(ii(i)+.5)*!dtor)
    y1j=y1+j*(.0254+0.001)*cos(section*(ii(i)+.5)*!dtor)
    x((i+n_first+n_second+n_third)*8+j,*)=x0j+(x1j-x0j)*(1-onehundredtwentyeight/128.)
    y((i+n_first+n_second+n_third)*8+j,*)=y0j+(y1j-y0j)*(1-onehundredtwentyeight/128.)
    z((i+n_first+n_second+n_third)*8+j,*)=z0_forth+dz_forth*(1-onehundredtwentyeight/128.)
  end
end
    """
    ii=[float(i+1) for i in (2,3,4,5,6,7,13,14,15,16,17,18)]
    n_forth=len(ii)

    z0_forth=-0.28/7.06*2.7+.0016
    x0_forth= 2.66/7.06*2.7
    z1_forth=-2.79/7.06*2.7-.0016
    x1_forth= 2.09/7.06*2.7

    dx_forth=x1_forth-x0_forth
    dz_forth=z1_forth-z0_forth

    section=(2.*pi)/23.
    x=[]
    y=[]
    z=[]
    for i in ii:
        angle = section*i
        x0=-x0_forth*cos(angle)
        y0= x0_forth*sin(angle)
        x1=-x1_forth*cos(angle)
        y1= x1_forth*sin(angle)

        for j in range(8):
            x0j=x0+j*(.0254+0.001)*sin(angle)
            y0j=y0+j*(.0254+0.001)*cos(angle)

            xextent = -1. * dx_forth * cos(angle)
            yextent =       dx_forth * sin(angle)

            for k in range(128):
                k = float(k)
                x.append(x0j      + xextent *(1.-k/128.))
                y.append(y0j      + yextent *(1.-k/128.))
                z.append(z0_forth + dz_forth*(1.-k/128.))

    pack4 = DetPack(tuberadius = .5*.0254,
                    airgap     = AIR_GAP,
                    xstartdiff = (.0254+AIR_GAP),
                    ysize      = -1.*TUBE_LENGTH,
                    ystartdiff = -1.*TUBE_LENGTH/128.,
                    debug=False)
    pack4.setNames(pixel=pack1.namepixel, tube=pack1.nametube, pack=pack1.namepack)

    group4 = instr.makeTypeElement("Group4")
    for i in range(n_forth):
        offset = i*8*128
        bank = "bank%d" % (i+52)
        #print bank, "i =", i, "offset=", offset
        #if i == 6:
        #    for point in rect.points:
        #        print point
        rect = Rectangle((-y[offset+UR], x[offset+UR], z[offset+UR]),
                         (-y[offset+LR], x[offset+LR], z[offset+LR]),
                         (-y[offset+LL], x[offset+LL], z[offset+LL]),
                         (-y[offset+UL], x[offset+UL], z[offset+UL]))
        det = instr.makeDetectorElement(pack4.namepack, root=group4)
        rect.makeLocation(instr, det, bank)

    # ---------- add in group5
    """
;;; source idl code
N_back=19
z0_back=-1.78/8.45*3.2
y0_back=1.32/8.45*3.2
for i=0,n_back-1 do begin

for j=0,7 do begin
ntube=i*8+j
x((i+n_first+n_second+n_third+n_fourth)*8+j,*)=(1-onehundredtwentyeight/128.)-0.5
y((i+n_first+n_second+n_third+n_fourth)*8+j,*)=y0_back-(.0254/2+.001)/2*ntube
z((i+n_first+n_second+n_third+n_fourth)*8+j,*)=z0_back-((i/2)*2 eq i)*(.0254/2+.001)
end
end
    """
    pack5 = DetPack(tuberadius = -.25*.0254,
                    airgap = .00585, # tubes are overlapping if you ignore z-offset
                    xstart = 0.023975, # empirical
                    ysize  =  .9, 
                    ystart = -0.44296875,
                    debug = True)
    pack5tubes = [2,1,4,3,6,5,8,7] # wacky empiracle numbering
    pack5.setTubeNumbers(pack5tubes)
    pack5z = [-1.* float((tube+1)% 2) * (.0254/2+.001) for tube in pack5tubes]
    pack5.setPosZ(pack5z)
    pack5.setNames(pixel="halfpixel", tube="halftube", pack="half_inch_back")

    group5 = instr.makeTypeElement("Group5")
    y = 0.0078125/0.9
    z = -1.78/8.45*3.2
    rot = 0.
    names = ["bank%d" % i for i in range(64,82)]
    def tube5X(ntube):
        return 1.34/8.45*3.2 - (.0254/2+.001)/2*(ntube)  
    x2 = []
    for i in range(len(names)):
        x2.append((tube5X(i*8+0) + tube5X(i*8+7))*.5)
    x2.reverse()
    #print x2
    for name, x in zip(names, x2):
        det = instr.makeDetectorElement(pack5.namepack, root=group5)
        makeLoc(instr, det, name,
                x=x, y=y, z=z, rot=rot)

    # ---------- add in group6 - results match
    """
;;; source idl code

N_forward=19
z0_forward=6.69/8.45*3.2
y0_forward=1.34/8.45*3.2
for i=0,n_forward-1 do begin

for j=0,7 do begin
ntube=i*8+j
x((i+n_first+n_second+n_third+n_fourth+n_back)*8+j,*)=(1-onehundredtwentyeight/128.)*.9-0.9/2
;;; hack: shift the forward panel by some
y((i+n_first+n_second+n_third+n_fourth+n_back)*8+j,*)=y0_forward-(.0254/2+.001)/2*(ntube+32)+.062
z((i+n_first+n_second+n_third+n_fourth+n_back)*8+j,*)=z0_forward-((j/2)*2 eq j)*(.0254/2+.001)
end
end
    """
    pack6 = DetPack(tuberadius = -.25*.0254,
                    airgap = .00585, # tubes are overlapping if you ignore z-offset
                    xstart = -0.023975, # empirical
                    ysize  =  .9, 
                    ystart = -0.44296875,
                    debug = True)
    pack6tubes = [2,1,4,3,6,5,8,7] # wacky empiracle numbering
    pack6.setTubeNumbers(pack6tubes)
    pack6z = [-1.* float(tube% 2) * (.0254/2+.001) for tube in pack6tubes]
    pack6.setPosZ(pack6z)
    pack6.setNames(pixel=pack5.namepixel, tube=pack5.nametube, pack="half_inch")

    group6 = instr.makeTypeElement("Group6")
    y = 0.0078125 # 0. # 0.003906
    z = 6.69/8.45*3.2# 2.51979
    rot = 0.
    names = ["bank%d" % i for i in range(82,100)]
    def tubeX(ntube):
        return 1.34/8.45*3.2 - (.0254/2+.001)/2*(ntube+32) + .062 + .217444
    x2 = []
    for i in range(len(names)):
        x2.append((tubeX(i*8+0) + tubeX(i*8+7))*.5)
    x2.reverse()
    #print x2
    for name, x in zip(names, x2):
        det = instr.makeDetectorElement(pack6.namepack, root=group6)
        makeLoc(instr, det, name,
                x=x, y=y, z=z, rot=rot)

    # ---------- detector panels
    pack1.writePack(instr, " bank 1 and 4 - New Detector Panel (128x8) - one inch - decreasing y ")
    pack2.writePack(instr, " bank 2 and 3 - New Detector Panel (128x8) - one inch - increasing y ")
    pack6.writePack(instr, "New Detector Panel (128x8) - half_inch - bank 6")
    pack5.writePack(instr, "New Detector Panel (128x8) - half_inch_back - bank 5")

    # ---------- monitors

    instr.addComment("Shape for monitors")
    instr.addComment("TODO: Update to real shape")
    instr.addDummyMonitor(0.01, .03)

    # ---------- detector tubes

    # this shape is used for 5 and 6 
    pack5.writeTube(instr, " bank 5 and 6 - 1m 128 pixel half inch tube ")

    # this shape is used for 1 and 4 
    pack1.writeTube(instr, " bank 1 and 4 - 1m 128 pixel inch tube decreasing y")

    # this shape is used for 2 and 3
    pack2.writeTube(instr, " bank 2 and 3 - 1m 128 pixel inch tube increasing y")

    # this shape is used for 5 and 6
    pack5.writePixel(instr, "Shape for half inch tube pixels")

    # this shape is used for pack/group 1-4
    pack1.writePixel(instr, "Shape for one inch tube pixels")

    # monitor ids
    instr.addComment("MONITOR IDS")
    instr.addMonitorIds([-1,-2])

    # debug information to help reduce definition size
    """
    print "pack1 == pack2", pack1 == pack2
    print "pack1 == pack3", pack1 == pack3
    print "pack1 == pack4", pack1 == pack4
    print "pack2 == pack3", pack2 == pack3
    print "pack2 == pack4", pack2 == pack4
    print "pack3 == pack4", pack3 == pack4
    """

    # write out the file
    instr.writeGeom(xml_outfile)
    #instr.showGeom()
