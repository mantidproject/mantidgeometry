#!/usr/bin/env python

from sns_geometry import Geometry, Component, Maths, Recipe, Vector, \
     extractValueFromFile, generateGeom, getEuler

from math import cos, sin, acos,  atan2, pi, sqrt
from datetime import datetime, date
import numpy as np

geometry = generateGeom("TOPAZ")
entry = geometry.getEntry()
instrument = entry.getInstrument()

# Monitors
monitor1 = Component("monitor1", "NXmonitor")
monitor1.setComment("MONITORS")
monitor1.setHelper("ParameterCopy")
monitor1.addVariable("distance", "mon1dis")
entry.addMonitor(monitor1)
monitor2 = Component("monitor2", "NXmonitor")
monitor2.setHelper("ParameterCopy")
monitor2.addVariable("distance", "mon2dis")
entry.addMonitor(monitor2)

# Sample
sample=Component("sample", "NXsample")
sample.setComment(" SAMPLE ")
sample.setHelper("Goiniometer")
#real_phi, etc. are the real sample orientations (sanitized names, taken from phi,chi,omega MOTOR values)
#phi, chi, etc. are the sample orientations
sample.addVariable("phi", "real_phi")
sample.addVariable("chi", "real_chi")
sample.addVariable("omega", "real_omega")
entry.addSample(sample)

# Moderator
moderator = entry.getComponent("moderator")
moderator.addParameter("beamline", value="11")
moderator.addVariable("distance", "L1")


# Choppers
chopper1 = Component("chopper1", "NXchopper")
chopper1.setComment("CHOPPERS")
chopper1.setHelper("ParameterCopy")
chopper1.addVariable("distance", "chop1dis")
instrument.addComponent(chopper1)
chopper2 = Component("chopper2", "NXchopper")
chopper2.setHelper("ParameterCopy")
chopper2.addVariable("distance", "chop2dis")
instrument.addComponent(chopper2)
chopper3 = Component("chopper3", "NXchopper")
chopper3.setHelper("ParameterCopy")
chopper3.addVariable("distance", "chop3dis")
instrument.addComponent(chopper3)

# Slits
aperture1 = Component("aperture1", "NXaperture")
aperture1.setComment("APERTURES")
aperture1.setHelper("CenteredRectangle")
aperture1.addVariable("cenDistance", "s1sam")
aperture1.addVariable("xExtent", "s1width")
aperture1.addVariable("yExtent", "s1height")
instrument.addComponent(aperture1)
aperture2 = Component("aperture2", "NXaperture")
aperture2.setComment("APERTURES")
aperture2.setHelper("CenteredRectangle")
aperture2.addVariable("cenDistance", "s2sam")
aperture2.addVariable("xExtent", "s2width")
aperture2.addVariable("yExtent", "s2height")
instrument.addComponent(aperture2)



#===============================================================================================
def writeToFile(xmlOut,append):
    """Writes the XML to a file with the prescriptive name"""
    today = date.today()
    filename = "%s_geom_%4i_%02i_%02i.xml" % ("TOPAZ",today.year,today.month,today.day)
    f1=open(filename, append)
    f1.write(xmlOut)
    f1.write("\n")

#===============================================================================================
def x_rotation_matrix(polar=0):
    """Generate a rotation matrix for a polar rotation,
    i.e. a rotation about the x axis."""

    #s and c are temp. variables for sin(x) and cos(x)
    c = cos(polar)
    s = sin(polar)
    M = np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    return M;


#===============================================================================================
def rotation_matrix(phi=0, chi=0, omega=0):
    """Generate a rotation matrix M for 3 rotation angles:
       Uses convention of IPNS and ISAW for angles.
       PHI = first rotation, around the y axis
       CHI = second rotation, around the z axis
       OMEGA = third rotation, around the y axis again.

       Angles in radians.
       Use rotated_vector = matrix * initial_vector"""

    #s and c are temp. variables for sin(x) and cos(x)
    c = cos(phi)
    s = sin(phi)
    M_phi = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])

    c = cos(chi)
    s = sin(chi)
    M_chi = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])

    c = cos(omega)
    s = sin(omega)
    M_omega = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])

    #rotated =  M_omega * (M_chi * (M_phi * vector));
    M = np.dot(M_omega, np.dot(M_chi, M_phi))

    return M;


def makeMantidGeometryIntro():
    """ Generate XML code to make a bit of XML for use in the
    Mantid XML geometry.


    """
    st = datetime.now()

    sxml = """<?xml version='1.0' encoding='UTF-8'?>
<!-- For help on the notation used to specify an Instrument Definition File 
     see http://www.mantidproject.org/IDF -->
<instrument xmlns="http://www.mantidproject.org/IDF/1.0" 
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://www.mantidproject.org/IDF/1.0 http://schema.mantidproject.org/IDF/1.0/IDFSchema.xsd"
 name="TOPAZ" valid-from   ="%s"
              valid-to     ="2100-12-31 23:59:59"
                      last-modified="%s">
  <!--DEFAULTS-->
  <defaults>
    <length unit="metre"/>
    <angle unit="degree"/>
    <reference-frame>
      <along-beam axis="z"/>
      <pointing-up axis="y"/>
      <handedness val="right"/>
    </reference-frame>
    <default-view view="spherical_y"/>
  </defaults>

  <!--SOURCE-->
  <component type="moderator">
    <location z="-18.0"/>
  </component>
  <type name="moderator" is="Source"/>

  <!--SAMPLE-->
  <component type="sample-position">
    <location y="0.0" x="0.0" z="0.0"/>
  </component>
  <type name="sample-position" is="SamplePos"/>

  <!--MONITORS-->
  <component type="monitors" idlist="monitors">
    <location/>
  </component>
  <type name="monitors">
    <component type="monitor">
      <location z="-2.488" name="monitor1"/>
    </component>
    <component type="monitor">
      <location z="1.049" name="monitor2"/>
    </component>
  </type>""" %(st, st)


    return sxml

def makeMantidGeometryEnd(widX, widY):
    """ Generate XML code to make a bit of XML for use in the
    Mantid XML geometry.


    """

    widX /= 100
    deltaX = widX/256
    startX = (deltaX-widX)/2
    widY /= 100
    deltaY = widY/256
    startY = (deltaY-widY)/2
    sxml = """

<!-- NOTE: This detector is the same as the SNAP detector -->
<!-- Rectangular Detector Panel -->
<type name="panel" is="rectangular_detector" type="pixel"
    xpixels="256" xstart="%f" xstep="%f"
    ypixels="256" ystart="%f" ystep="%f" >
  <properties/>
</type>

  <!-- Pixel for Detectors-->
  <type is="detector" name="pixel">
    <cuboid id="pixel-shape">
      <left-front-bottom-point y="-0.000309" x="-0.000309" z="0.0"/>
      <left-front-top-point y="0.000309" x="-0.000309" z="0.0"/>
      <left-back-bottom-point y="-0.000309" x="-0.000309" z="-0.0001"/>
      <right-front-bottom-point y="-0.000309" x="0.000309" z="0.0"/>
    </cuboid>
    <algebra val="pixel-shape"/>
  </type>

  <!-- Shape for Monitors-->
  <!-- TODO: Update to real shape -->
  <type is="monitor" name="monitor">
    <cylinder id="some-shape">
      <centre-of-bottom-base p="0.0" r="0.0" t="0.0"/>
      <axis y="0.0" x="0.0" z="1.0"/>
      <radius val="0.01"/>
      <height val="0.03"/>
    </cylinder>
    <algebra val="some-shape"/>
  </type>

  <!--MONITOR IDs-->
  <idlist idname="monitors">
    <id val="-1"/>
    <id val="-2"/>
  </idlist>
</instrument>""" %(startX, deltaX, startY, deltaY)


    return sxml

def makeMantidGeometryCode(name, idstart, radius, theta_center_rad, phi_center_rad, phi_rad, chi_rad, omega_rad):
    """ Generate XML code to make a bit of XML for use in the
    Mantid XML geometry.

    name: name of the bank
    idstart: where the pixel ID's start

    radius: in cm, radius of center of detector
    theta_center_rad, phi_center_rad: radians, position of center of detector
    phi_rad, chi_rad, omega_rad: radians, tilt and rotation of the detector.

    Angles will be converted to degrees and radius to meters.
    """
    r = radius/100
    theta_center = np.rad2deg(theta_center_rad)
    phi_center = np.rad2deg(phi_center_rad)
    phi = np.rad2deg(phi_rad)
    chi = np.rad2deg(chi_rad)
    omega = np.rad2deg(omega_rad)
    phi = np.rad2deg(phi_rad)

    # Added an extra 90 degree rotation about the axis of the panel on May 2, 2011.

    sxml = """<component type="panel" idstart="%d" idfillbyfirst="y" idstepbyrow="256">
<location r="%f" t="%f" p="%f" name="%s" rot="%f" axis-x="0" axis-y="1" axis-z="0">
  <rot val="%f">
    <rot val="%f" axis-x="0" axis-y="1" axis-z="0" />
  </rot>
</location>
</component> """ % (idstart, r, theta_center, phi_center, name, omega, chi, phi)

    return sxml

    


#===============================================================================================
def addBank(instrument, banknum, local_name, distance, cenX, cenY, cenZ, base, up):
    """Add a bank (detector) with given angles.

    Parameters:
        banknum: Number of the detector.
        local_name: local_name of the detector (a string)
        azimuth: azimuthal angle in radians. 0 = pointing downstream
        elevation: elevation angle in radians. Positive = going up (towards +Y)
        rotation: rotation of the detector face, in rad, around the positive +Z axis.
            For topaz this is -45 degrees.
        distance: in cm, from sample to center of detector face.
    """
    CM = "centimetre"
    RAD = "radian"

    bank = Component( "bank%d" % banknum, "NXdetector")
    bank.setRecipe("topaz_detector")
    theta = acos(cenZ/distance)
    phi = atan2(cenY, cenX)

    # Distance between sample and center of detector
    bank.addParameter("cenDistance", distance, units=CM)

    # cenPolar is "The angle of the rectangle center from the positive z-axis."
    # So this corresponds to our "theta" angle.
    bank.addParameter("cenPolar", theta, units=RAD)
    #Azimuthal = the angle of the rectangle center from the positive x-axis constrained in the xy-plane.
    # so this corresponds to the "phi" angle.
    bank.addParameter("cenAzimuthal", phi, units=RAD)
    
    #For later
    phi_center = phi
    theta_center = theta
    
    #Use getEuler to get the equivalent phi,chi,omega (in that order) rotation angles.
    (phi, chi, omega) = getEuler(base, up) #getEuler input units defaults to radians

    # Now we save these 3 orientation angles
    bank.addParameter("phi", phi, units=RAD)
    bank.addParameter("chi", chi, units=RAD)
    bank.addParameter("omega", omega, units=RAD)

    #Congrats! We have now tricked the program into making the correct detector orientation
    # (we hope!)
    

    # Now we set a local_name for the bank	
    bank.setAnnotation("<local_name>%s</local_name>" % local_name)
    
    instrument.addComponent(bank)


    #! Now mantid
    idstart = banknum * 65536

    print makeMantidGeometryCode(local_name, idstart, distance, theta_center, phi_center, phi, chi, omega)
    writeToFile(makeMantidGeometryCode(local_name, idstart, distance, theta_center, phi_center, phi, chi, omega), 'a')

##    
##    
##    # ZtowardsX: The local coordinates are rotated with the z-axis moving towards the x-axis.
##    #   i.e.: the detector tilt, which is the same as the elevation angle
##    bank.addParameter("ZtowardsX", elevation, units=RAD)
##    
##    # XtowardsY: The local coordinates are rotated with the x-axis moving towards the y-axis.
##    #   i.e.: the detector rotation, which is -45 degrees for TOPAZ
##    bank.addParameter("XtowardsY", rotation, units=RAD)
##    
##    # ZtowardsY: The local coordinates are rotated with the z-axis moving towards the y-axis.
##    #   i.e.: the detector azimuth facing rotation, which is equal to the center position azimuth
##    bank.addParameter("ZtowardsY", azimuth, units=RAD)

##    nx = sin(theta)*cos(phi)
##    ny = sin(theta)*sin(phi)
##    nz = cos(theta)
##    print "Old x,y,z are %.3f, %.3f, %3.f; and now\n              %.3f, %.3f, %3.f" % (x,y,z,nx,ny,nz)


def cmp_row(x,y):
    """Comparator for two rows in the CSV file """
    xi = -1
    yi = -1
    if len(x[5]) > 0:
        xi = int(x[5])
    if len(y[5]) > 0:
        yi = int(y[5])
    return cmp(xi, yi)




detCalFile = (raw_input("Please enter the name of the DetCal file: "))
print "<!-- XML Code automatically generated on %s for the Mantid instrument definition file from %s -->" % (datetime.now(), detCalFile)
writeToFile(makeMantidGeometryIntro(), "w")
writeToFile( "<!-- XML Code automatically generated on %s for the Mantid instrument definition file from %s -->" % (datetime.now(), detCalFile), "a")

#Now sort by bank number so the output looks better
# rows.sort(cmp_row)

all_names = []

for row in range(len(open(detCalFile).readlines())):
    #Parse each row
    flag = extractValueFromFile(detCalFile,None,row,None,0)
    #Detector number. 
    if flag == "5": #Is it in use?
        # Bank number; as of Jan 2011, starts at 10 and goes up to 59.
        det_num = int(extractValueFromFile(detCalFile,None,row,None,1))
        local_name = "bank%d" % det_num
        
        #Distance, kept in cm
        distance = float(extractValueFromFile(detCalFile,None,row,None,7))
        cenX = float(extractValueFromFile(detCalFile,None,row,None,8))
        cenY = float(extractValueFromFile(detCalFile,None,row,None,9))
        cenZ = float(extractValueFromFile(detCalFile,None,row,None,10))
        baseX = float(extractValueFromFile(detCalFile,None,row,None,11))
        baseY = float(extractValueFromFile(detCalFile,None,row,None,12))
        baseZ = float(extractValueFromFile(detCalFile,None,row,None,13))
        upX = float(extractValueFromFile(detCalFile,None,row,None,14))
        upY = float(extractValueFromFile(detCalFile,None,row,None,15))
        upZ = float(extractValueFromFile(detCalFile,None,row,None,16))
        widX = float(extractValueFromFile(detCalFile,None,row,None,4))
        widY = float(extractValueFromFile(detCalFile,None,row,None,5))
        center = Vector([cenX,cenY,cenZ])
        base = Vector([baseX,baseY,baseZ])
        up = Vector([upX,upY,upZ])

        addBank(instrument, det_num, local_name, distance, cenX, cenY, cenZ, base, up)
        all_names.append(local_name)

print "<!-- List of all the bank names:"
print ",".join(all_names)
print "-->"
writeToFile( "<!-- List of all the bank names:", "a")
writeToFile( ",".join(all_names), "a")
writeToFile( "-->", "a")
writeToFile(makeMantidGeometryEnd(widX, widY), "a")


### RECIPES ###
recipe = Recipe("topaz_detector")
recipe.setHelper("Rectangle") #Use the general Rectangle
recipe.addParameter("xNumPixel", "256")
recipe.addParameter("yNumPixel", "256")
recipe.addParameter("flip", "1")
recipe.addVariable("xExtent", "extent") #width and height of detector
recipe.addVariable("yExtent", "extent")
recipe.addVariable("xOffset", "0") 
recipe.addVariable("yOffset", "0") 
geometry.addRecipe(recipe)

### MATHS ###
maths = Maths()

# Definitions
maths.addDefinition("extent", "158.19", units="millimetre") # the size (width and height) of each detector

maths.addDefinition("L1", "18.0", units="metre")
maths.addDefinition("chop1mod_distance", "6.4029", units="metre")
maths.addDefinition("chop2mod_distance", "8.90157", units="metre")
maths.addDefinition("chop3mod_distance", "11.45713", units="metre")
maths.addDefinition("mon1mod_distance", "15.45", units="metre")
maths.addDefinition("mon2mod_distance", "19.049", units="metre") #calibrated as of 8/21/2012
maths.addDefinition("s1mod_distance", "15.40", units="metre")
maths.addDefinition("s2mod_distance", "17.45", units="metre")

# Inputs
maths.addInput("s1l", "length")
maths.addInput("s1r", "length")
maths.addInput("S1HWidth", "length")
maths.addInput("s1t", "length")
maths.addInput("s1b", "length")
maths.addInput("S1VHeight", "length")
maths.addInput("s2l", "length")
maths.addInput("s2r", "length")
maths.addInput("S2HWidth", "length")
maths.addInput("s2t", "length")
maths.addInput("s2b", "length")
maths.addInput("S2VHeight", "length")
# Ambient goniometer inputs
# THESE ARE THE MOTOR NAMES
maths.addInput("phi", "angle")
maths.addInput("chi", "angle")
maths.addInput("omega", "angle")


# Equations
maths.addEquation("a=L1") # this is required by the schema
maths.addEquation("chop1dis = chop1mod_distance - L1")
maths.addEquation("chop2dis = chop2mod_distance - L1")
maths.addEquation("chop3dis = chop3mod_distance - L1")
maths.addEquation("mon1dis = mon1mod_distance - L1")
maths.addEquation("mon2dis = mon2mod_distance - L1")
maths.addEquation("s1sam = s1mod_distance - L1")
maths.addEquation("s2sam = s2mod_distance - L1")

maths.addEquation("""try:
  s1width = S1HWidth
except:
  s1width = abs(s1l - s1r)""", comment="slit sizes")
maths.addEquation("""try:
  s1height = S1VHeight
except:
  s1height = abs(s1t - s1b)""")
maths.addEquation("""try:
  s2width = S2HWidth
except:
  s2width = abs(s2l - s2r)""")
maths.addEquation("""try:
  s2height = S2VHeight
except:
  s2height = abs(s2t - s2b)""")

#Convert GONIOMETER MOTOR POSITIONS to sanitized REAL sample orientation names
maths.addEquation("real_phi = phi", comment="TOPAZ Ambient Goniometer - taken from CV info file.")
maths.addEquation("real_omega = omega")
#Starting Oct 26, 2010, we grab Chi from the DAS logs (CV info file)
maths.addEquation("real_chi = chi")

maths.addOutput("L1", "length")
maths.addOutput("extent", "length")
maths.addOutput("chop1dis", "length")
maths.addOutput("chop2dis", "length")
maths.addOutput("chop3dis", "length")
maths.addOutput("mon1dis", "length")
maths.addOutput("mon2dis", "length")
maths.addOutput("s1sam", "length")
maths.addOutput("s2sam", "length")
maths.addOutput("s1width", "length")
maths.addOutput("s1height", "length")
maths.addOutput("s2width", "length")
maths.addOutput("s2height", "length")

#Real sample orientation angles output
maths.addOutput("real_phi", "angle")
maths.addOutput("real_chi", "angle")
maths.addOutput("real_omega", "angle")


geometry.addMath(maths)

#geometry.writeToScreen()
#geometry.writeToFile()
