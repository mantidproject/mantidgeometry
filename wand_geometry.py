#!/usr/bin/python
INST_NAME = "WAND"
NUM_PIXELS_PER_TUBE = 512
NUM_TUBES_PER_BANK = 480
TUBE_SIZE = 0.2  # meter
TUBE_WIDTH = 0.000397  # meter
AIR_GAP_WIDTH = 0.0  # meter
PIXELS_PER_BANK = NUM_TUBES_PER_BANK * NUM_PIXELS_PER_TUBE
CONVERT_TO_METERS = 1000.0  # x,y,z in millimeters
NUM_DETS = 8
RADIUS = 0.728


def convert(value):
    return float(value) / CONVERT_TO_METERS


if __name__ == "__main__":
    from lxml import etree as le
    from helper import MantidGeom
    import numpy as np
    try:
        np.set_printoptions(legacy='1.13')
    except TypeError:
        pass

    # Set header information
    comment = "Created by Ross Whitfield"
    # Time needs to be in UTC?
    valid_from = "2017-12-01 00:00:00"

    # Get geometry information file
    xml_outfile = INST_NAME+"_Definition.xml"

    det = MantidGeom(INST_NAME, comment=comment, valid_from=valid_from)
    det.addSnsDefaults(default_view="cylindrical_y")
    det.addComment("SOURCE AND SAMPLE POSITION")
    det.addModerator(-3.289, "monochromator")
    det.addSamplePosition()

    doc_handle = None
    for i in range(NUM_DETS):
        bank = det.addComponent("bank"+str(i+1),
                                idlist="bank"+str(i+1),
                                root=doc_handle)
        log = le.SubElement(bank, "parameter", **{"name": "y"})
        le.SubElement(log, "logfile",
                      **{"id": "HB2C:Mot:detz.RBV", # detz is in cm
                         "eq": "rint(value*1000)/100000", # Round to 0.01mm and convert to metres
                         "extract-single-value-as": "mean"})

        det_type = "panel"
        angle = (NUM_DETS-i-1)*15+7.5  # Mantid
        angle = i*15+7.5  # Flipped

        type_element = le.SubElement(det.getRoot(), "type",
                                     name="bank"+str(i+1))
        comp_element = le.SubElement(type_element, "component",
                                     type=det_type)
        location = le.SubElement(comp_element, "location")

        log = le.SubElement(location, "parameter", **{"name": "r-position"})
        le.SubElement(log, "value", **{"val": str(RADIUS)})
        log = le.SubElement(location, "parameter", **{"name": "t-position"})
        le.SubElement(log, "logfile",
                      **{"id": "HB2C:Mot:s2.RBV",
                         "eq": str(angle)+"+rint(value*1000)/1000", # Round to 1/1000 of a degree
                         "extract-single-value-as": "mean"})
        log = le.SubElement(location, "parameter", **{"name": "roty"})
        le.SubElement(log, "logfile",
                      **{"id": "HB2C:Mot:s2.RBV",
                         "eq": str(angle)+"+value",
                         "extract-single-value-as": "mean"})

    det.addComment("DET PACK")
    det.addWANDDetector("panel",
                        NUM_TUBES_PER_BANK,
                        TUBE_WIDTH,
                        AIR_GAP_WIDTH,
                        RADIUS,
                        type_name="wire")

    det.addComment("20CM WIRE 512 PIXELS")
    det.addPixelatedTube("wire", NUM_PIXELS_PER_TUBE, TUBE_SIZE)

    det.addComment("PIXEL FOR WIRE")
    det.addCylinderPixel("pixel", (0.0, 0.0, 0.0), (0.0, 1.0, 0.0),
                         (TUBE_WIDTH/2.0),
                         (TUBE_SIZE/NUM_PIXELS_PER_TUBE))

    det.addComment("DETECTOR IDs")
    offset = 0
    for i in range(NUM_DETS):
        id_list = []
        id_list.append(i * PIXELS_PER_BANK)
        id_list.append((i+1) * PIXELS_PER_BANK - 1)
        id_list.append(None)
        det.addDetectorIds('bank'+str(i+1), id_list)

    det.addComment("MONITOR IDs")
    det.addMonitorIds(["-1"])

    det.writeGeom(xml_outfile)
