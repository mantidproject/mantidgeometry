#! /usr/bin/python

from helper import MantidGeom
import h5py
import math

#nexusfile = "/Users/scu/data/BSS_15600_event.nxs"
nexusfile = "/home/scu/Desktop/BSS_23741_event.nxs"
banks = 4


TUBE_PRESSURE = ("tube_pressure", 0.0, "atm")
TUBE_THICKNESS = ("tube_thickness", 0.0008, "metre")
TUBE_TEMPERATURE = ("tube_temperature", 290.0, "K")

__author__="Stuart Campbell"
__date__ ="$Dec 14, 2010 3:13:15 PM$"

if __name__ == "__main__":

    inst_name = "BASIS"
    short_name = "BSS"

    xml_outfile = inst_name+"_Definition_new.xml"

    file = h5py.File(nexusfile, 'r')

    det = MantidGeom(inst_name, comment=" Created by Stuart Campbell ")
    det.addSnsDefaults()
    det.addComment("SOURCE AND SAMPLE POSITION")
    det.addModerator(-84.0)
    det.addSamplePosition()
    det.addComment("MONITORS")
    det.addMonitors(names=["monitor1"], distance=["-0.23368"])


    for i in range(banks):
        pixel_id = file["/entry/instrument/bank%d/pixel_id" % (i+1)].value
        distance = file["/entry/instrument/bank%d/distance" % (i+1)].value
        polar_angle = file["/entry/instrument/bank%d/polar_angle" % (i+1)].value
        polar_angle *= (180.0/math.pi)
        azimuthal_angle = file["/entry/instrument/bank%d/azimuthal_angle" % (i+1)].value
        azimuthal_angle *= (180.0/math.pi)
        
        analyser_wavelength = file["/entry/instrument/analyzer%d/wavelength" % (i+1)].value
        analyser_energy = 81.8042051/analyser_wavelength**2

        bank_id = "bank%d" % (i+1)
        det.addComponent(bank_id, bank_id)
        #doc_handle = det.makeTypeElement(bank_id)

        det.addDetectorPixels(bank_id, r=distance, theta=polar_angle,
                              phi=azimuthal_angle, names=pixel_id, energy=analyser_energy)

        det.addDetectorPixelsIdList(bank_id, r=distance, names=pixel_id)

    # Pixel Height
    y_pixel_offset = file["/entry/instrument/bank1/y_pixel_offset"].value
    pixel_ysize = y_pixel_offset[1] - y_pixel_offset[0]

    # Pixel Width
    x_pixel_offset = file["/entry/instrument/bank1/x_pixel_offset"].value
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

    det.addComment("PIXEL")
    det.addCuboidPixel("pixel", left_front_bottom, left_front_top, left_back_bottom, right_front_bottom, "detector")

    det.addComment("MONITOR SHAPE")
    det.addComment("FIXME: Do something real here.")
    det.addDummyMonitor(0.01, 0.03)

    det.addComment("MONITOR IDs")
    det.addMonitorIds(["-1"])

    det.showGeom()
    det.writeGeom(xml_outfile)
