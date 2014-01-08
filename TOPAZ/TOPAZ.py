#!/usr/bin/env python

from sns_geometry import Geometry, Component, Maths, Recipe, Vector, \
     extractValueFromFile, generateGeom, getEuler

from math import cos, sin, acos, atan2
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
def addBank(instrument, banknum, local_name, azimuth, elevation, rotation, distance):
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

    # Now we need to convert from our azimuth/elevation coordinates
    #   to azimuth/polar.
    
    #Assuming azimuth of zero points to z positive = same direction as incident radiation.
    r2 = cos(elevation)
    z=cos(azimuth) * r2
    x=sin(azimuth) * r2
    #Assuming polar angle is 0 when horizontal, positive to y positive
    y=sin(elevation)
    #So (x,y,z) is the direction; length is 1

    #We calculate the polar (theta) and azimuth (phi) angles
    theta = acos(z)
    phi = atan2(y,x)

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
    
    #Now we set the detector orientation. If we set any of the detector orientation
    # values, this overrides the orientation that would come from cenPolar and cenAzimuthal

    #We will use the getEuler() method to find the phi, chi, omega angles.

    #But first we need the u,v vectors describing the face of the detector.
    #u = the horizontal vector; v = the vertical vector
    u = np.array([1.,0.,0.]).reshape(3,1)
    v = np.array([0.,1.,0.]).reshape(3,1)

    #Ok, first rotate the detector around its center by angle.
    #Since this is rotation around z axis, it is a chi angle
    rot = rotation_matrix(0, rotation, 0)

    u_rotated = Vector(np.dot(rot, u))
    v_rotated = Vector(np.dot(rot, v))

    #Now do the elevation rotation, by rotating around the x axis.
    rot = np.dot(x_rotation_matrix(-elevation), rot)

    #Finally add an azimuthal rotation (around the y axis, or phi)
    rot = np.dot(rotation_matrix(azimuth, 0, 0), rot)

    #Now we rotate the base vectors, save them as vectors
    u_rotated = Vector(np.dot(rot, u))
    v_rotated = Vector(np.dot(rot, v))

    #Use getEuler to get the equivalent phi,chi,omega (in that order) rotation angles.
    (phi, chi, omega) = getEuler(u_rotated, v_rotated) #getEuler input units defaults to radians

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

    #  Have to flip U because it is the opposite of what we expect
    u_rotated = Vector(np.dot(rot, u)*-1.0)
    (phi, chi, omega) = getEuler(u_rotated, v_rotated) #getEuler input units defaults to radians
    #print "<!--- Rotated we have u ", u_rotated, ", v", v_rotated, "giving angles ", (phi, chi, omega), " ... for bank", banknum, " --->"
    print makeMantidGeometryCode(local_name, idstart, distance, theta_center, phi_center, phi, chi, omega)

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




from datetime import datetime
print "<!-- XML Code automatically generated on %s for the Mantid instrument definition file -->" % datetime.now()

# Detectors
import csv
#f = open("TOPAZ_geom_all_2011.csv") # For TS, removing/adding as needed
f = open("TOPAZ_geom_all_2012.csv") # All detectors, for Mantid
# f = open("TOPAZ_geom_all_2010.csv") # For 2010 and before  TOPAZ
cr = csv.reader(f)
#Ignore the header row
header = cr.next()

#Collect the rows
rows = [];
for row in cr:
    rows.append(row)
    
#Now sort by bank number so the output looks better
# rows.sort(cmp_row)

all_names = []

for row in rows:
    #Parse each row
    det_name = row[0]
    #Detector number. 
    if len(row[8]) > 0: #Is it in use?
        # Bank number; as of Jan 2011, starts at 10 and goes up to 59.
        det_num = int(row[0])
        local_name = "bank%d" % det_num
        
        # Is the detector in use?
        in_use = 0
        if len(row[8]) > 0:
            in_use = int(row[8])
            
        #Angles in rad
        azimuth = float(row[2]) 
        elevation = float(row[3]) # As of Feb 14, 2011: File contains the elevation
        rotation = float(row[4])
        
        #Distance, kept in cm
        distance = float(row[5])

        addBank(instrument, det_num, local_name, azimuth, elevation, rotation, distance)
        all_names.append(local_name)

print "<!-- List of all the bank names:"
print ",".join(all_names)
print "-->"

f.close()

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
geometry.writeToFile()
