import sys
from pathlib import Path

if __name__ == '__main__' and __package__ is None:
    file = Path(__file__).resolve()
    parent = file.parents[1]
    sys.path.append(str(parent))
    from helper import MantidGeom

    INST_NAME = "HRC"
    NUM_PIXELS_PER_TUBE = 1024
    NUM_TUBES_PER_BANK_WIDE = 64
    NUM_TUBES_PER_BANK_SMALL = 34
    DISTANCE_WIDE = 4.0
    DISTANCE_SMALL= 5.2
    TUBE_LENGTH_WIDE = 2.8
    TUBE_LENGTH_SMALL = 0.8
    CENTER_SMALL = 0.
    CENTER_WIDE = 0.4
    BANKFMT = 'Bank_%s'
    BANK_NAMES_SMALL = ['B1', 'B2']
    BANK_WIDE_NAMES = ['A', 'C', 'D', 'E']
    
    
    TUBE_WIDTH_WIDE = 0.019 #meter
    TUBE_WIDTH_SMALL = 0.0127 #meter
    
    AIR_GAP_WIDTH = 0.002032 #meter
    PIXELS_PER_BANK_WIDE= NUM_TUBES_PER_BANK_WIDE * NUM_PIXELS_PER_TUBE
    PIXELS_PER_BANK_SMALL= NUM_TUBES_PER_BANK_SMALL * NUM_PIXELS_PER_TUBE

    CONVERT_TO_METERS = 1000.0 #x,y,z in millimeters
    # Detector Parameters
    TUBE_PRESSURE = ("tube_pressure", 10.0, "atm")
    TUBE_THICKNESS = ("tube_thickness", 0.0008, "metre")
    TUBE_TEMPERATURE = ("tube_temperature", 290.0, "K")



    # Set header information
    comment = "Created by Andrei Savici"
    # Time needs to be in UTC?
    valid_from = "2025-10-10 10:00:00"

    # Get geometry information file
    xml_outfile = INST_NAME + "_Definition.xml"
 
    det = MantidGeom(INST_NAME, comment=comment, valid_from=valid_from)
    det.addSnsDefaults()
    
    det.addComment("SOURCE AND SAMPLE POSITION")
    det.addModerator(-15.0)
    det.addSamplePosition()
    
    det.addComment("CHOPPERS")
    det.addChopper("t0-chopper",-6.0)
    det.addVerticalAxisT0Chopper("t0-chopper")
    det.addChopper("fermi-chopper",-1.0)
    det.addFermiChopper("fermi-chopper")

    label = "detectors"
    det.addComponent(label,blank_location=False)
    doc_handle = det.makeTypeElement(label)
    detinfo = dict()
    detinfo["BankAngle"] = [-1.75, -7.25, -21, 13, 33, 53]
    detinfo["Distance"] = [DISTANCE_SMALL, DISTANCE_SMALL, DISTANCE_WIDE, DISTANCE_WIDE, DISTANCE_WIDE, DISTANCE_WIDE]
    detinfo["Bank_xpos"] = detinfo["Distance"] * np.sin(np.radians(detinfo["BankAngle"]))
    detinfo["Bank_ypos"] = [CENTER_SMALL, CENTER_SMALL, CENTER_WIDE, CENTER_WIDE, CENTER_WIDE, CENTER_WIDE]
    detinfo["Bank_zpos"] = detinfo["Distance"] * np.cos(np.radians(detinfo["BankAngle"]))
    detinfo["Names"] = BANK_NAMES_SMALL + BANK_WIDE_NAMES
    # Small angle
    for i in range(6):
        detname = BANKFMT % detinfo["Names"][i]
        roty = float(detinfo["BankAngle"][i]) 
        xpos = detinfo["Bank_xpos"][i]
        ypos = detinfo["Bank_ypos"][i]
        zpos = detinfo["Bank_zpos"][i]
        det.addComponent(detname, detname, root=doc_handle, blank_location=False)
        label="small"
        if i>=2:
            label="wide"
        det.addDetector(xpos, ypos, zpos, 0, roty, 0, detname, label)

    det.addComment("STANDARD SMALL ANGLE PACK")
    det.addNPack("small", NUM_TUBES_PER_BANK_SMALL, TUBE_WIDTH_SMALL, AIR_GAP_WIDTH, type_name="tube_small")

    det.addComment("STANDARD SMALL ANGLE 1024 PIXEL TUBE")
    det.addPixelatedTube("tube_small", NUM_PIXELS_PER_TUBE, TUBE_LENGTH_SMALL)

    det.addComment("PIXEL FOR SMALL ANGLE TUBE")
    det.addCylinderPixel("pixel", (0.0, 0.0, 0.0), (0.0, 1.0, 0.0),
                         (TUBE_WIDTH_SMALL/2.0),
                         (TUBE_LENGTH_SMALL/NUM_PIXELS_PER_TUBE))


    det.addComment("STANDARD WIDE ANGLE PACK")
    det.addNPack("wide", NUM_TUBES_PER_BANK_WIDE, TUBE_WIDTH_WIDE, AIR_GAP_WIDTH, type_name="tube_wide")
    det.addComment("STANDARD WIDE ANGLE 1024 PIXEL TUBE")
    det.addPixelatedTube("tube_wide", NUM_PIXELS_PER_TUBE, TUBE_LENGTH_WIDE)
    det.addComment("PIXEL FOR WIDE ANGLE TUBE")
    det.addCylinderPixel("pixel_wide", (0.0, 0.0, 0.0), (0.0, 1.0, 0.0),
                         (TUBE_WIDTH_WIDE/2.0),
                         (TUBE_LENGTH_WIDE/NUM_PIXELS_PER_TUBE))
    
    det.addComment("DETECTOR IDs")
    for i in range(6):
        bank_name = BANKFMT % detinfo["Names"][i]
        if i < 2:
            det.addDetectorIds(bank_name, [i * PIXELS_PER_BANK_SMALL, (i + 1) * PIXELS_PER_BANK_SMALL - 1, None])
        else:
            det.addDetectorIds(bank_name, [2 * PIXELS_PER_BANK_SMALL + (i - 2) * PIXELS_PER_BANK_WIDE,
                                           2 * PIXELS_PER_BANK_SMALL + (i - 1) * PIXELS_PER_BANK_WIDE - 1, None])   


    det.addComment("DETECTOR PARAMETERS")
    det.addDetectorParameters(label, TUBE_PRESSURE, TUBE_THICKNESS,
                              TUBE_TEMPERATURE)    
    
    #det.showGeom()
    det.writeGeom(xml_outfile)
