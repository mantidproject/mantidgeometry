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
        if xsize > 0.:
            xsize  = float(xsize)
            self.xstep = xsize/float(xnum)
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

    def writePack(self, instr, comment=""):
        if len(comment) > 0:
            instr.addComment(comment)
        instr.addComment("New Detector Panel (128x8) - one_inch")
        det = instr.makeTypeElement(self.namepack)
        le.SubElement(det, "properties")
        det = instr.addComponent(self.nametube, root=det, blank_location=False)
        debug_ids = [0, self.xnum-1]
        for j in range(self.xnum):
            name="tube%d"  % (j+1)
            x = float(j)*self.xstep + self.xstart
            if self.__debug and (j in debug_ids):
                print "x[%d] = %f" % (j, x)
            instr.addLocation(det, x, 0., 0., name=name)

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
if __name__ == "__main__":
    inst_name = "NOMAD"
    xml_outfile = inst_name+"_Definition.xml"

    # boiler plate stuff
    instr = MantidGeom(inst_name, comment=" Created by Peter Peterson ",
                       valid_from="2012-07-01 00:00:01",
                       valid_to="2012-07-31 23:59:59")
    instr.addComment("DEFAULTS")
    instr.addSnsDefaults()
    instr.addComment("SOURCE")
    instr.addModerator(-19.49958)
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
    group1 = instr.makeTypeElement("Group1")
    z = .5*((6.41/8.45*3.2) + (3.86/8.45*3.2))# 1.940845
    det = instr.makeDetectorElement("one_inch", root=group1)
    makeLoc(instr, det, "bank1",
            x=-0.0900835, y=-0.50034125, z=z, rot=-89.3663312,
            rot_inner=92.7740541972, rot_innermost=102.872503501)
    det = instr.makeDetectorElement("one_inch", root=group1)
    makeLoc(instr, det, "bank2",
            x=-0.29825225, y=-0.41170625, z=z, rot=-88.2250765278,
            rot_inner=92.2242357116, rot_innermost=128.605560457)
    det = instr.makeDetectorElement("one_inch", root=group1)
    makeLoc(instr, det, "bank3",
            x=-0.44734875, y=-0.241528, z=z, rot=-87.4360086541,
            rot_inner=91.2341549097, rot_innermost=154.31324826)
    det = instr.makeDetectorElement("one_inch", root=group1)
    makeLoc(instr, det, "bank4",
            x=-0.507842, y=-0.023511625, z=z, rot=-87.1545655812,
            rot_inner=90.0, rot_innermost=180.0)
    det = instr.makeDetectorElement("one_inch", root=group1)
    makeLoc(instr, det, "bank5",
            x=-0.4677515, y=0.199161, z=z, rot=-87.4360162435,
            rot_inner=88.7658487398, rot_innermost=-154.313248163)
    det = instr.makeDetectorElement("one_inch", root=group1)
    makeLoc(instr, det, "bank6",
            x=-0.33501675, y=0.382388, z=z, rot=-88.2250361723,
            rot_inner=87.7757484484, rot_innermost=-128.605997196)
    det = instr.makeDetectorElement("one_inch", root=group1)
    makeLoc(instr, det, "bank7",
            x=-0.135927725, y=0.4898775, z=z, rot=-89.3663380315,
            rot_inner=87.2259863472, rot_innermost=-102.872551406)
    det = instr.makeDetectorElement("one_inch", root=group1)
    makeLoc(instr, det, "bank8",
            x=0.0900835227694, y=0.50034125, z=z, rot=-90.6336689203,
            rot_inner=87.2259458689, rot_innermost=-77.1274935015)
    det = instr.makeDetectorElement("one_inch", root=group1)
    makeLoc(instr, det, "bank9",
            x=0.29825225, y=0.41170625, z=z, rot=-91.7749234722,
            rot_inner=87.7757642884, rot_innermost=-51.3944395427)
    det = instr.makeDetectorElement("one_inch", root=group1)
    makeLoc(instr, det, "bank10",
            x=0.44734875, y=0.241528, z=z, rot=-92.5639913459,
            rot_inner=88.7658450903, rot_innermost=-25.686751674)
    det = instr.makeDetectorElement("one_inch", root=group1)
    makeLoc(instr, det, "bank11",
            x=0.507842, y=0.023511625, z=z, rot=-92.8454344188,
            rot_inner=90.0)
    det = instr.makeDetectorElement("one_inch", root=group1)
    makeLoc(instr, det, "bank12",
            x=0.46775125, y=-0.199161, z=z, rot=-92.5639926177,
            rot_inner=91.2341401341, rot_innermost=25.6864726524)
    det = instr.makeDetectorElement("one_inch", root=group1)
    makeLoc(instr, det, "bank13",
            x=0.33501675, y=-0.382388, z=z, rot=-91.7749638277,
            rot_inner=92.2242515516, rot_innermost=51.3940028045)
    det = instr.makeDetectorElement("one_inch", root=group1)
    makeLoc(instr, det, "bank14",
            x=0.1359277, y=-0.4898775, z=z, rot=-90.6336619129,
            rot_inner=92.774014947, rot_innermost=77.1274554878)

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
            x0j=x0+j*(.0254+0.001)*sin(angle)
            y0j=y0+j*(.0254+0.001)*cos(angle)
            x1j=x1+j*(.0254+0.001)*sin(angle)
            y1j=y1+j*(.0254+0.001)*cos(angle)

            for k in range(128):
                k = float(k)
                x.append(x0j       + (x1j-x0j)*k/128.)
                y.append(y0j       + (y1j-y0j)*k/128.)
                z.append(z0_second + dz_second*k/128.)

    #pack2 = DetPack(tuberadius=.5*.0254,
    #                airgap=AIR_GAP,
    #                #xsize      = -8.*(.0254+AIR_GAP),
    #                #xstartdiff = -1.*(.0254+AIR_GAP),
    #                ysize      = TUBE_LENGTH,
    #                #ystartdiff = TUBE_LENGTH/128.,
    #                debug=True)
    pack2 = DetPack(tuberadius = .5*.0254,
                    airgap     = AIR_GAP,
                    #xstartdiff = (.0254+AIR_GAP),
                    ysize      = TUBE_LENGTH,
                    ystartdiff = TUBE_LENGTH/128.,
                    debug=True)
    pack2.setNames(pixel="bank2pixel", tube="bank2tube", pack="bank2pack")

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


    """
    z = .5*((5.09/7.06*2.7-0.0095) + (2.45/7.06*2.7+0.0095)) # 1.445654
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank15",
            x=-0.0915395, y=-0.836427, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=97.8262008026)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank16",
            x=-0.31381, y=-0.780713, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=113.478192701)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank17",
            x=-0.512807, y=-0.6670965, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=129.130313954)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank18",
            x=-0.6737715, y=-0.504005, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=144.78248153)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank19",
            x=-0.784765, y=-0.303534, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=160.434729108)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank20",
            x=-0.8375565, y=-0.08055513, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=176.087022238)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank21",
            x=-0.82823, y=0.14840565, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=-168.261070831)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank22",
            x=-0.757478, y=0.3663565, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=-152.608674007)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank23",
            x=-0.6305465, y=0.557136, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=-136.95660485)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank24",
            x=-0.4568505, y=0.7065955, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=-121.304270268)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank25",
            x=-0.2492725, y=0.8036495, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=-105.652349705)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank26",
            x=-0.0232068, y=0.841101, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=-90.0)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank27",
            x=0.20458, y=0.8161715, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=-74.3477339442)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank28",
            x=0.4171945, y=0.7307105, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=-58.695729732)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank29",
            x=0.598867, y=0.5910565, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=-43.0434101201)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank30",
            x=0.736125, y=0.4075655, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=-27.3913259927)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank31",
            x=0.818787, y=0.1938458, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=-11.7389102452)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank32",
            x=0.8407235, y=-0.0342456, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=3.91299045695)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank33",
            x=0.800308, y=-0.259801, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=19.5652708918)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank34",
            x=0.700537, y=-0.466087, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=35.2172651748)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank35",
            x=0.54881, y=-0.6378065, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=50.8696860457)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank36",
            x=0.356381, y=-0.7622215, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=66.5215229238)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank37",
            x=0.1375204, y=-0.830107, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=82.173807641)
    """

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
    group3 = instr.makeTypeElement("Group3")
    z = .5*((2.59/7.06*2.7-0.0076) + (-0.04/7.06*2.7+.0076)) # 0.48373677
    det = instr.makeDetectorElement("one_inch", root=group3)
    makeLoc(instr, det, "bank38",
            x=-0.7475175, y=-0.6555715, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=139.65505902)
    det = instr.makeDetectorElement("one_inch", root=group3)
    makeLoc(instr, det, "bank39",
            x=-0.87097, y=-0.4795505, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=152.068928854)
    det = instr.makeDetectorElement("one_inch", root=group3)
    makeLoc(instr, det, "bank40",
            x=-0.9536965, y=-0.281106, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=164.482826207)
    det = instr.makeDetectorElement("one_inch", root=group3)
    makeLoc(instr, det, "bank41",
            x=-0.991829, y=-0.0695175, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=176.896821582)
    det = instr.makeDetectorElement("one_inch", root=group3)
    makeLoc(instr, det, "bank42",
            x=-0.9835845, y=0.145322, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=-170.68977393)
    det = instr.makeDetectorElement("one_inch", root=group3)
    makeLoc(instr, det, "bank43",
            x=-0.929359, y=0.3533655, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=-158.275738743)
    det = instr.makeDetectorElement("one_inch", root=group3)
    makeLoc(instr, det, "bank44",
            x=-0.8316585, y=0.544887, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=-145.862002566)
    det = instr.makeDetectorElement("one_inch", root=group3)
    makeLoc(instr, det, "bank45",
            x=0.814016, y=0.570975, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=-34.1380800603)
    det = instr.makeDetectorElement("one_inch", root=group3)
    makeLoc(instr, det, "bank46",
            x=0.917713, y=0.3825705, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=-21.7242612566)
    det = instr.makeDetectorElement("one_inch", root=group3)
    makeLoc(instr, det, "bank47",
            x=0.9784985, y=0.17634535, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=-9.31026118073)
    det = instr.makeDetectorElement("one_inch", root=group3)
    makeLoc(instr, det, "bank48",
            x=0.993531, y=-0.0381263, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=3.10317170469)
    det = instr.makeDetectorElement("one_inch", root=group3)
    makeLoc(instr, det, "bank49",
            x=0.9621065, y=-0.250814, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=15.5171737927)
    det = instr.makeDetectorElement("one_inch", root=group3)
    makeLoc(instr, det, "bank50",
            x=0.885696, y=-0.451775, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=27.9309259204)
    det = instr.makeDetectorElement("one_inch", root=group3)
    makeLoc(instr, det, "bank51",
            x=0.7678705, y=-0.631611, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=40.3447402631)

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

    #print "dx =", dx_forth, (dx_forth/8.)
    #print "dz =", dz_forth, (dz_forth/128.)
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
    #print len(x), len(y), len(z)
    #print x[0:8*128]
    #print y[0:8*128]
    #print z[0:8*128]
    #####

    pack4 = DetPack(tuberadius = .5*.0254,
                    airgap     = AIR_GAP,
                    xstartdiff = (.0254+AIR_GAP),
                    ysize      = -1.*TUBE_LENGTH,
                    ystartdiff = -1.*TUBE_LENGTH/128.,
                    debug=False)
    pack4.setNames(pixel="bank4pixel", tube="bank4tube", pack="bank4pack")

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
    group5 = instr.makeTypeElement("Group5")
    y = 0. # 0.003906
    z = -1.78/8.45*3.2 # -0.687783
    det = instr.makeDetectorElement("half_inch_back", root=group5)
    makeLoc(instr, det, "bank64",
            x=-0.503307, y=y, z=z, rot=180.0)
    det = instr.makeDetectorElement("half_inch_back", root=group5)
    makeLoc(instr, det, "bank65",
            x=-0.448507, y=y, z=z, rot=180.0)
    det = instr.makeDetectorElement("half_inch_back", root=group5)
    makeLoc(instr, det, "bank66",
            x=-0.393707, y=y, z=z, rot=180.0)
    det = instr.makeDetectorElement("half_inch_back", root=group5)
    makeLoc(instr, det, "bank67",
            x=-0.338907, y=y, z=z, rot=180.0)
    det = instr.makeDetectorElement("half_inch_back", root=group5)
    makeLoc(instr, det, "bank68",
            x=-0.284107, y=y, z=z, rot=180.0)
    det = instr.makeDetectorElement("half_inch_back", root=group5)
    makeLoc(instr, det, "bank69",
            x=-0.229307, y=y, z=z, rot=180.0)
    det = instr.makeDetectorElement("half_inch_back", root=group5)
    makeLoc(instr, det, "bank70",
            x=-0.174507, y=y, z=z, rot=180.0)
    det = instr.makeDetectorElement("half_inch_back", root=group5)
    makeLoc(instr, det, "bank71",
            x=-0.11970685, y=y, z=z, rot=180.0)
    det = instr.makeDetectorElement("half_inch_back", root=group5)
    makeLoc(instr, det, "bank72",
            x=-0.0649067, y=y, z=z, rot=180.0)
    det = instr.makeDetectorElement("half_inch_back", root=group5)
    makeLoc(instr, det, "bank73",
            x=0.044693295, y=y, z=z, rot=180.0)
    det = instr.makeDetectorElement("half_inch_back", root=group5)
    makeLoc(instr, det, "bank74",
            x=0.0994933, y=y, z=z, rot=180.0)
    det = instr.makeDetectorElement("half_inch_back", root=group5)
    makeLoc(instr, det, "bank75",
            x=0.154293, y=y, z=z, rot=180.0)
    det = instr.makeDetectorElement("half_inch_back", root=group5)
    makeLoc(instr, det, "bank76",
            x=0.209093, y=y, z=z, rot=180.0)
    det = instr.makeDetectorElement("half_inch_back", root=group5)
    makeLoc(instr, det, "bank77",
            x=0.263893, y=y, z=z, rot=180.0)
    det = instr.makeDetectorElement("half_inch_back", root=group5)
    makeLoc(instr, det, "bank78",
            x=0.318693, y=y, z=z, rot=180.0)
    det = instr.makeDetectorElement("half_inch_back", root=group5)
    makeLoc(instr, det, "bank79",
            x=0.373493, y=y, z=z, rot=180.0)
    det = instr.makeDetectorElement("half_inch_back", root=group5)
    makeLoc(instr, det, "bank80",
            x=0.428293, y=y, z=z, rot=180.0)
    det = instr.makeDetectorElement("half_inch_back", root=group5)
    makeLoc(instr, det, "bank81",
            x=0.483093, y=y, z=z, rot=180.0)

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
        det = instr.makeDetectorElement("half_inch", root=group6)
        makeLoc(instr, det, name,
                x=x, y=y, z=z, rot=rot)

    # ---------- detector panels

    instr.addComment("New Detector Panel (128x8) - one_inch")
    det = instr.makeTypeElement("one_inch")
    le.SubElement(det, "properties")
    det = instr.addComponent("tube", root=det, blank_location=False)
    xstep = (-0.0254*5.5/5.) # tubes are at 5.5inches for 6 tubes on centre OLD=-0.0264
    xstart = -8.*.5*xstep + .5*xstep # OLD=0.0924
    for j in range(8):
        name="tube%d"  % (j+1)
        x = float(j)*xstep + xstart
        #if j == 0 or j == 7:
        #    print j, x
        instr.addLocation(det, x, 0., 0., name=name)

    pack2.writePack(instr, " bank 2 - New Detector Panel (128x8) - one inch ")
    pack4.writePack(instr, " bank 4 - New Detector Panel (128x8) - one inch ")

    instr.addComment("New Detector Panel (128x8) - half_inch")
    det = instr.makeTypeElement("half_inch")
    le.SubElement(det, "properties")
    det = instr.addComponent("halftube", root=det, blank_location=False)
    xstep = -0.00685
    xstart = -1*(-.5*8.*xstep + .5*xstep) # OLD=-0.0924
    tubenumbers = [1,0,3,2,5,4,7,6]
    for (tube,j) in zip(range(8),tubenumbers):
        name="halftube%d"  % (j+1)
        x = float(tube)*xstep + xstart
        #if j == 0 or j == 7:
        #    print j, x
        z = -1.* float((j + 1)% 2) * (.0254/2+.001) 
        instr.addLocation(det, x, 0., z, name=name)

    instr.addComment("New Detector Panel (128x8) - half_inch_back")
    det = instr.makeTypeElement("half_inch_back")
    le.SubElement(det, "properties")
    det = instr.addComponent("halftube", root=det, blank_location=False)
    xstep = -0.00685
    xstart = -.5*8.*xstep + .5*xstep # OLD=0.023975
    for j in range(8):
        name="halftube_back%d"  % (j+1)
        x = float(j)*xstep + xstart
        #if j == 0 or j == 7:
        #    print j, x
        z = -1.* float(j % 2) * (.0254/2+.001) 
        instr.addLocation(det, x, 0., z, name=name)

    # ---------- monitors

    instr.addComment("Shape for monitors")
    instr.addComment("TODO: Update to real shape")
    instr.addDummyMonitor(0.01, .03)

    # ---------- detector tubes
    ypixels = 128
    ystep = .9/float(ypixels) # 1m tubes
    ystart = -.5*float(ypixels)*ystep+ystep#-.446484#-.5-.5*ystep
    instr.addComment(" 1m 128 pixel half inch tube ")
    tube = instr.makeTypeElement("halftube", {"outline":"yes"})
    le.SubElement(tube, "properties")
    tube = instr.addComponent("halfpixel", root=tube, blank_location=False)
    for i in range(ypixels):
        name = "pixel%d" % (i+1)
        y = float(i)*ystep + ystart
        #if i == 0 or i == 127:
        #    print y
        instr.addLocation(tube, 0., y, 0., name=name)

    ystep = -1./float(ypixels) # pixels go in the other direction
    ystart = .5+.5*ystep
    instr.addComment(" 1m 128 pixel inch tube ")
    tube = instr.makeTypeElement("tube", {"outline":"yes"})
    le.SubElement(tube, "properties")
    tube = instr.addComponent("onepixel", root=tube, blank_location=False)
    for i in range(ypixels):
        name = "pixel%d" % (i+1)
        y = float(i)*ystep + ystart
        #if i == 0 or i == 127:
        #    print y
        instr.addLocation(tube, 0., y, 0., name=name)

    pack2.writeTube(instr, " bank 2 - 1m 128 pixel inch tube ")
    pack4.writeTube(instr, " bank 4 - 1m 128 pixel inch tube ")

    instr.addComment("Shape for half inch tube pixels")
    instr.addCylinderPixel("halfpixel", # 1 metre long 1/2 inch tube
                           (0.,0.,0.), (0.,1.,0.), .25*.0254, .9/128.)

    instr.addComment("Shape for inch tube pixels")
    instr.addCylinderPixel("onepixel", # 1 metre long 1 inch tube
                           (0.,0.,0.), (0.,1.,0.), .5*.0254, 1./128.)

    pack2.writePixel(instr, "Shape for bank 2 pixels")
    pack4.writePixel(instr, "Shape for bank 4 pixels")

    # monitor ids
    instr.addComment("MONITOR IDS")
    instr.addMonitorIds([-1,-2])

    # write out the file
    instr.writeGeom(xml_outfile)
    #instr.showGeom()
