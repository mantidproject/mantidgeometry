#!/usr/bin/python
import numpy as np

NUM_PIXELS_PER_TUBE = 512
NUM_TUBES_PER_BANK = 16
TUBE_SIZE = 0.6546 #meter
TUBE_WIDTH = 0.0127 #meter
AIR_GAP_WIDTH = 0.0147 #meter
NUM_DETS = 7
DISTANCE_TO_SAMPLE = 1.467 #meter
ANGLES = np.arange(7) * 21.594 + 12.797 #degrees
Y_OFFSET = 0.0137 #meter
PIXELS_PER_BANK = NUM_TUBES_PER_BANK * NUM_PIXELS_PER_TUBE
BANKFMT = "bank%d"
ROTX = None # no X rotation
ROTZ = 90 # no z rotation
FLIPY = 180.0 # flip y orientation
# Detector Parameters
TUBE_PRESSURE = ("tube_pressure", 6.0, "atm")
TUBE_THICKNESS = ("tube_thickness", 0.0008, "metre")
TUBE_TEMPERATURE = ("tube_temperature", 290.0, "K")


if __name__ == "__main__":
    import sys
    from helper import MantidGeom
    from sns_ncolumn import readFile

    # Set header information
    comment = "Created by Andrei Savici"
    # Time needs to be in UTC?
    valid_from = "2025-08-07 10:00:00"

    # Get geometry information file
    inst_name = "MIDAS"
    
    xml_outfile = inst_name+"_Definition.xml"
 
    det = MantidGeom(inst_name, comment=comment, valid_from=valid_from)
    det.addSnsDefaults()
    det.addComment("SOURCE AND SAMPLE POSITION")
    det.addModerator(-3.0)
    det.addSamplePosition()
    det.addComment("MONITORS")
    det.addMonitors(names=["monitor1"],
                    distance=["-0.3"])

    label = "detectors"
    det.addComponent(label, label, blank_location=False)
    doc_handle = det.makeTypeElement(label)
    for i in range(NUM_DETS):
        detname = BANKFMT % (i)
        roty = ANGLES[i]
        xpos = np.sin(np.radians(ANGLES[i])) * DISTANCE_TO_SAMPLE
        ypos = -Y_OFFSET*(i%2)
        zpos = np.cos(np.radians(ANGLES[i])) * DISTANCE_TO_SAMPLE
        det.addComponent(detname, root=doc_handle, blank_location=False)
        det.addDetector(xpos, ypos, zpos, ROTX, roty, ROTZ, detname, "sixteenpack")

    det.addComment("STANDARD 16-PACK")
    det.addNPack("sixteenpack", NUM_TUBES_PER_BANK, TUBE_WIDTH, AIR_GAP_WIDTH)

    det.addComment("STANDARD 512 PIXEL TUBE")
    det.addPixelatedTube("tube", NUM_PIXELS_PER_TUBE, TUBE_SIZE)

    det.addComment("PIXEL FOR STANDARD 512 PIXEL TUBE")
    det.addCylinderPixel("pixel", (0.0, 0.0, 0.0), (0.0, 1.0, 0.0),
                         (TUBE_WIDTH/2.0),
                         (TUBE_SIZE/NUM_PIXELS_PER_TUBE))

    det.addComment("MONITOR SHAPE")
    det.addComment("FIXME: Do something real here.")
    det.addDummyMonitor(0.01, 0.03)

    det.addComment("DETECTOR IDs")
    det.addDetectorIds(label, [0, (NUM_DETS * PIXELS_PER_BANK) - 1 , None])

    det.addComment("MONITOR IDs")
    det.addMonitorIds(["-1"])

    det.addComment("DETECTOR PARAMETERS")
    det.addDetectorParameters(label, TUBE_PRESSURE, TUBE_THICKNESS,
                              TUBE_TEMPERATURE)    
    
    #det.showGeom()
    det.writeGeom(xml_outfile)

