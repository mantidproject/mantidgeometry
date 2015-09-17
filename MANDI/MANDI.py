#!/usr/bin/env python

# Based on TOPAZ.py wrote by Janik

from sns_geometry import Geometry, Component, Maths, Recipe, Vector, \
     extractValueFromFile, generateGeom, getEuler

from math import cos, sin, acos, atan2
import numpy as np

geometry = generateGeom("MANDI")
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
monitor3 = Component("monitor3", "NXmonitor")
monitor3.setHelper("ParameterCopy")
monitor3.addVariable("distance", "mon3dis")
entry.addMonitor(monitor3)

# Sample
sample=Component("sample", "NXsample")
sample.setComment(" SAMPLE ")
sample.setHelper("Goiniometer")
#real_phi, and real_omega are the real sample orientations (sanitized names, taken from phi and omega MOTOR values)
#chi: default value
#phi, chi, and omega are the sample orientations
sample.addVariable("phi", "real_phi")
sample.addVariable("chi", "default_chi")
sample.addVariable("omega", "real_omega")
entry.addSample(sample)

# Moderator
moderator = entry.getComponent("moderator")
moderator.addParameter("beamline", value="11")
moderator.addVariable("distance", "mod_dis")


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
aperture1 = Component("slitu", "NXaperture")
aperture1.setComment("APERTURES")
aperture1.setHelper("CenteredRectangle")
aperture1.addVariable("cenDistance", "s1sam")
aperture1.addVariable("xExtent", "s1width")
aperture1.addVariable("yExtent", "s1height")
instrument.addComponent(aperture1)
aperture2 = Component("slitud", "NXaperture")
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
            For MANDI this is -45 degrees (if the same to TOPAZ).
        distance: in cm, from sample to center of detector face.
    """
    CM = "centimetre"
    RAD = "radian"

    bank_name = "bank" + str(banknum)
    bank = Component( bank_name, "NXdetector")
    bank.setRecipe("detector")

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
    print makeMantidGeometryCode(bank_name, idstart, distance, theta_center, phi_center, phi, chi, omega)

from datetime import datetime
print "<!-- XML Code automatically generated on %s for the Mantid instrument definition file -->" % datetime.now()

# Detectors
import csv
f = open("MANDI_geom_2015_2.csv") # added bank1, 2, 3, 7, 8, 12, 53 and 57 at 2015_2 start-up

cr = csv.reader(f)
#Ignore the header row
header = cr.next()

#Collect the rows
rows = [];
for row in cr:
    rows.append(row)
    
all_names = []

for row in rows:
    #Parse each row
    det_name = row[0]

    in_use = 0
    #Detector number. 
    if len(row[8]) > 0: #In use
        det_num = int(row[0])
        local_name = row[1]
        in_use = int(row[8])
                     
        #Angles in rad
        azimuth = float(row[2]) 
        elevation = float(row[3])
        rotation = float(row[4])
        
        #Distance, kept in cm
        distance = float(row[5])

        addBank(instrument, det_num, local_name, azimuth, elevation, rotation, distance)
        all_names.append(str(det_num))

print "<!-- List of all the banks:"
print ",".join(all_names)
print "-->"

f.close()

### RECIPES ###
recipe = Recipe("detector")
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

maths.addDefinition("L1", "30.0", units="metre")
maths.addDefinition("chop1mod_distance", "7.2", units="metre")
maths.addDefinition("chop2mod_distance", "8.27", units="metre")
maths.addDefinition("chop3mod_distance", "10.5", units="metre")
maths.addDefinition("mon1mod_distance", "27.065", units="metre") # refined on 12-07-2012
maths.addDefinition("mon2mod_distance", "29.102", units="metre") # refined on 12-07-2012 
maths.addDefinition("mon3mod_distance", "31.042", units="metre") # refined on 02-01-2013 
maths.addDefinition("s1mod_distance", "27.04", units="metre")
maths.addDefinition("s2mod_distance", "29.53", units="metre")
maths.addDefinition("default_chi", "-45.0", units="degree")

# Inputs

maths.addInput("SUHWidth", "length")
maths.addInput("SUVHeight", "length")
maths.addInput("sdHxGap", "length")
maths.addInput("sdVertGap", "length")
# Ambient goniometer inputs
# THESE ARE THE MOTOR NAMES
maths.addInput("phi", "angle")
maths.addInput("omega", "angle")


# Equations
maths.addEquation("mod_dis = -1 * L1")
maths.addEquation("chop1dis = chop1mod_distance - L1")
maths.addEquation("chop2dis = chop2mod_distance - L1")
maths.addEquation("chop3dis = chop3mod_distance - L1")
maths.addEquation("mon1dis = mon1mod_distance - L1")
maths.addEquation("mon2dis = mon2mod_distance - L1")
maths.addEquation("mon3dis = mon3mod_distance - L1")
maths.addEquation("s1sam = s1mod_distance - L1")
maths.addEquation("s2sam = s2mod_distance - L1")


maths.addEquation("""try:
  s1width = SUHWidth
except:
  pass""") # slit may be missing in NeXus files if missing virtual motors
maths.addEquation("""try:
  s1height = SUVHeight
except:
  pass""") # slit may be missing in NeXus files if missing virtual motors
maths.addEquation("""try:
  s2width = sdHxGap
except:
  pass""") # slit may be missing in NeXus files if missing virtual motors
maths.addEquation("""try:
  s2height = sdVertGap
except:
  pass""") # slit may be missing in NeXus files if missing virtual motors

#Convert GONIOMETER MOTOR POSITIONS to sanitized REAL sample orientation names
maths.addEquation("real_phi = phi")
maths.addEquation("real_omega = omega")

maths.addOutput("extent", "length")
maths.addOutput("mod_dis", "length")
maths.addOutput("chop1dis", "length")
maths.addOutput("chop2dis", "length")
maths.addOutput("chop3dis", "length")
maths.addOutput("mon1dis", "length")
maths.addOutput("mon2dis", "length")
maths.addOutput("mon3dis", "length")
maths.addOutput("s1sam", "length")
maths.addOutput("s2sam", "length")
maths.addOutput("s1width", "length")
maths.addOutput("s1height", "length")
maths.addOutput("s2width", "length")
maths.addOutput("s2height", "length")

#Real sample orientation angles output
maths.addOutput("real_phi", "angle")
maths.addOutput("real_omega", "angle")
maths.addOutput("default_chi", "angle")

geometry.addMath(maths)

#geometry.writeToScreen()
geometry.writeToFile()
