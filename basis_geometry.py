#! /usr/bin/python

from helper import MantidGeom
import h5py
import math

nexusfile = "/SNS/BSS/shared/NeXusFiles/BSS/IPTS-8135/0/23741/NeXus/BSS_23741_event.nxs"
banks = 4

INCH_TO_METRE = 0.0254

TUBE_PRESSURE = ("tube_pressure", 0.0, "atm")
TUBE_THICKNESS = ("tube_thickness", 0.0008, "metre")
TUBE_TEMPERATURE = ("tube_temperature", 290.0, "K")

# DIFFRACTION
ELASTIC_BANK_START = 5
ELASTIC_BANK_END = 13
ELASTIC_DETECTORID_START = 16384
ELASTIC_TUBES_PER_BANK = 1
ELASTIC_TUBE_NPIXELS = 128
ELASTIC_TUBE_LENGTH = 25.24 * INCH_TO_METRE
ELASTIC_TUBE_WIDTH = 0.5 * INCH_TO_METRE   # 0.5" diameter tubes
ELASTIC_TUBE_PRESSURE = ("tube_pressure", 30.0, "atm")
ELASTIC_TUBE_THICKNESS = ("tube_thickness",  (0.01 * INCH_TO_METRE), "metre")
ELASTIC_TUBE_TEMPERATURE = ("tube_temperature", 290.0, "K")

if __name__ == "__main__":

    inst_name = "BASIS"
    short_name = "BSS"

    # Set header information
    comment = "Created by Michael Reuter"
    # Time needs to be in UTC?
    valid_from = "2013-01-20 00:00:00"

    xml_outfile = inst_name+"_Definition.xml"

    nfile = h5py.File(nexusfile, 'r')

    det = MantidGeom(inst_name, comment=comment, valid_from=valid_from)
    det.addSnsDefaults(indirect=True)
    det.addComment("SOURCE AND SAMPLE POSITION")
    det.addModerator(-84.0)
    det.addSamplePosition()
    det.addComment("MONITORS")
    det.addMonitors(names=["monitor1"], distance=["-0.23368"])

    # Create the inelastic banks information
    for i in range(banks):
        pixel_id = nfile["/entry/instrument/bank%d/pixel_id" % (i+1)].value
        distance = nfile["/entry/instrument/bank%d/distance" % (i+1)].value
        polar_angle = nfile["/entry/instrument/bank%d/polar_angle" % (i+1)].value
        polar_angle *= (180.0/math.pi)
        azimuthal_angle = nfile["/entry/instrument/bank%d/azimuthal_angle" % (i+1)].value
        azimuthal_angle *= (180.0/math.pi)
        
        analyser_wavelength = nfile["/entry/instrument/analyzer%d/wavelength" % (i+1)].value
        analyser_energy = 81.8042051/analyser_wavelength**2

        bank_id = "bank%d" % (i+1)
        det.addComponent(bank_id, bank_id)
        #doc_handle = det.makeTypeElement(bank_id)

        det.addDetectorPixels(bank_id, r=distance, theta=polar_angle,
                              phi=azimuthal_angle, names=pixel_id, 
                              energy=analyser_energy)

        det.addDetectorPixelsIdList(bank_id, r=distance, names=pixel_id)

    # Create the diffraction bank information
    det.addComponent("elastic", "elastic")
    handle = det.makeTypeElement("elastic")

    idlist = []

    detector_z = [-2.1474825,-1.704594,-1.108373,-0.4135165,0.3181,1.0218315,1.6330115,2.0993535,2.376999]
    detector_x = [1.1649855,1.7484015,2.175541,2.408594,2.422933,2.216378,1.8142005,1.247867,0.5687435]
    detector_y = [-0.001807,-0.001801,-0.0011845,-0.0006885,-0.0013145,-0.001626,-0.001397,0.0003465,-0.0001125]

    for i in range(ELASTIC_BANK_START, ELASTIC_BANK_END+1):
        bank_name = "bank%d" % i
        det.addComponent(bank_name, root=handle)
	
        k = i - ELASTIC_BANK_START

        x_coord = detector_x[k]
        y_coord = detector_y[k]
        z_coord = detector_z[k]
		
        det.addDetector(x_coord, y_coord, z_coord, 0.0, 0., 90., 
                        bank_name, "tube-elastic", facingSample=True)

        idlist.append(ELASTIC_DETECTORID_START + ELASTIC_TUBE_NPIXELS*(i-ELASTIC_BANK_START))
        idlist.append(ELASTIC_DETECTORID_START + ELASTIC_TUBE_NPIXELS*(i-ELASTIC_BANK_START) 
        + ELASTIC_TUBE_NPIXELS-1)
        idlist.append(None)

    # Diffraction tube information
    det.addComment("ELASTIC TUBE (90 degrees)")
    det.addPixelatedTube("tube-elastic", ELASTIC_TUBE_NPIXELS, 
                         ELASTIC_TUBE_LENGTH, "pixel-elastic-tube", 
                         neutronic=True, neutronicIsPhysical=True)
                         
    # Set the diffraction pixel Ids
    det.addDetectorIds("elastic", idlist)

    # Creating diffraction pixel
    det.addComment("PIXEL FOR DIFFRACTION TUBES")
    det.addCylinderPixel("pixel-elastic-tube", (0.0, 0.0, 0.0), (0.0, 1.0, 0.0),
                         (ELASTIC_TUBE_WIDTH/2.0), 
                         (ELASTIC_TUBE_LENGTH/ELASTIC_TUBE_NPIXELS))
    
    # Creating inelastic pixel
    # Pixel Height
    y_pixel_offset = nfile["/entry/instrument/bank1/y_pixel_offset"].value
    pixel_ysize = y_pixel_offset[1] - y_pixel_offset[0]

    # Pixel Width
    x_pixel_offset = nfile["/entry/instrument/bank1/x_pixel_offset"].value
    pixel_xsize = x_pixel_offset[1] - x_pixel_offset[0]

    # Lets just make them bigger for a moment so we can see them
    pixel_xsize *= 5.0
    pixel_ysize *= 2.0

    # arbitary value plucked from thin air!
    detector_depth = 0.01

    left_front_bottom = ((-pixel_xsize/2.0), (-pixel_ysize/2.0), 0.0)
    left_front_top = ((-pixel_xsize/2.0), (pixel_ysize/2.0), 0.0)
    left_back_bottom = ((-pixel_xsize/2.0), (-pixel_ysize/2.0), -detector_depth)
    right_front_bottom = ((pixel_xsize/2.0), (-pixel_ysize/2.0), 0.0)

    det.addComment("PIXEL FOR INELASTIC TUBES")
    det.addCuboidPixel("pixel", left_front_bottom, left_front_top, 
                       left_back_bottom, right_front_bottom, "detector")

    det.addComment("MONITOR SHAPE")
    det.addComment("FIXME: Do something real here.")
    det.addDummyMonitor(0.01, 0.03)

    det.addComment("MONITOR IDs")
    det.addMonitorIds(["-1"])

    det.showGeom()
    det.writeGeom(xml_outfile)
