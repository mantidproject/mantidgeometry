#!/usr/bin/python

INST_NAME = "SEQUOIA"
NUM_PIXELS_PER_TUBE = 128
NUM_TUBES_PER_BANK = 8
SMALL_TOP_TUBE_SIZE = 0.25908 #meter
SMALL_BOTTOM_TUBE_SIZE = 0.333502 #meter
LARGE_TUBE_SIZE = 1.2 #meter
TUBE_WIDTH = 0.0254 #meter
AIR_GAP_WIDTH = 0.002032 #meter
PIXELS_PER_BANK = NUM_TUBES_PER_BANK * NUM_PIXELS_PER_TUBE
CONVERT_TO_METERS = 1.0/0.0254 #x,y,z are in inches
# Detector Parameters
TUBE_PRESSURE = ("tube_pressure", 10.0, "atm")
TUBE_THICKNESS = ("tube_thickness", 0.0008, "metre")
TUBE_TEMPERATURE = ("tube_temperature", 290.0, "K")

def read_file(filename):
    fh = open(filename)
    lines = fh.readlines()
    fh.close()
    di = {}
    di["name"] = []
    di["id"] = []
    di["X"] = []
    di["Y"] = []
    di["Z"] = []
    di["RotX"] = []
    di["RotY"] = []
    di["RotZ"] = []
    counter = 0
    for line in lines[1:]:
        values = line.split()
        counter += 1

        di["name"].append(values[0])
        di["id"].append(counter)
        di["X"].append(str(float(values[1])/CONVERT_TO_METERS))
        di["Y"].append(str(float(values[2])/CONVERT_TO_METERS))
        di["Z"].append(str(float(values[3])/CONVERT_TO_METERS))
        di["RotX"].append(None)
        di["RotY"].append(str(float(values[4])+180.0))
        di["RotZ"].append(None)
        
    return di

if __name__ == "__main__":
    import sys
    from helper import MantidGeom

    try:
        geom_input_file = sys.argv[1]
    except KeyError:
        geom_input_file = INST_NAME+"_geom.txt"
        
    # Set header information
    comment = "Created by Michael Reuter"
    # Time needs to be in UTC?
    valid_from = "2012-04-04 14:15:46"

    # Get geometry information file

    detinfo = read_file(geom_input_file)
    num_dets = len(detinfo.values()[0])
    xml_outfile = INST_NAME+"_Definition.xml"
    
    det = MantidGeom(INST_NAME, comment=comment, valid_from=valid_from)
    det.addSnsDefaults()
    det.addComment("SOURCE AND SAMPLE POSITION")
    det.addModerator(-20.0114)
    det.addSamplePosition()
    det.addComment("MONITORS")
    det.addMonitors(names=["monitor1", "monitor2"],
                    distance=["-1.77808", "8.99184"])

    row_id = ""
    row_id_list = []
    doc_handle = None
    for i in range(num_dets):
        # REMOVE ME: when A and E rows are filled
        if detinfo["name"][i].startswith("A") or \
               detinfo["name"][i].startswith("E"):
            continue
        
        if row_id != detinfo["name"][i][0]:
            row_id = detinfo["name"][i][0]
            row_id_list.append(row_id)
            row_id_str = row_id + " row"
            det.addComponent(row_id_str, row_id_str)
            doc_handle = det.makeTypeElement(row_id_str)

        det.addComponent(detinfo["name"][i], root=doc_handle)
        
        if detinfo["name"][i].startswith("C"):
            if detinfo["name"][i].endswith("T"):
                det.addDetector(detinfo["X"][i], detinfo["Y"][i],
                                detinfo["Z"][i], detinfo["RotX"][i],
                                detinfo["RotY"][i], detinfo["RotZ"][i],
                                detinfo["name"][i], "eightpack-top")
            elif detinfo["name"][i].endswith("B"):
                det.addDetector(detinfo["X"][i], detinfo["Y"][i],
                                detinfo["Z"][i], detinfo["RotX"][i],
                                detinfo["RotY"][i], detinfo["RotZ"][i],
                                detinfo["name"][i], "eightpack-bottom")
            else:
                det.addDetector(detinfo["X"][i], detinfo["Y"][i],
                                detinfo["Z"][i], detinfo["RotX"][i],
                                detinfo["RotY"][i], detinfo["RotZ"][i],
                                detinfo["name"][i], "eightpack")
        else:
            det.addDetector(detinfo["X"][i], detinfo["Y"][i],
                            detinfo["Z"][i], detinfo["RotX"][i],
                            detinfo["RotY"][i], detinfo["RotZ"][i],
                            detinfo["name"][i], "eightpack")

    det.addComment("STANDARD 8-PACK")
    det.addNPack("eightpack", NUM_TUBES_PER_BANK, TUBE_WIDTH, AIR_GAP_WIDTH)
    det.addComment("8-PACK ABOVE BEAMSTOP")
    det.addNPack("eightpack-top", NUM_TUBES_PER_BANK, TUBE_WIDTH,
                 AIR_GAP_WIDTH, type_name="tube-top")
    det.addComment("8-PACK BELOW BEAMSTOP")
    det.addNPack("eightpack-bottom", NUM_TUBES_PER_BANK, TUBE_WIDTH,
                 AIR_GAP_WIDTH, type_name="tube-bottom")

    det.addComment("STANDARD 128 PIXEL TUBE")
    det.addPixelatedTube("tube", NUM_PIXELS_PER_TUBE, LARGE_TUBE_SIZE)
    det.addComment("SMALL TOP 128 PIXEL TUBE")
    det.addPixelatedTube("tube-top", NUM_PIXELS_PER_TUBE, SMALL_TOP_TUBE_SIZE,
                         type_name="pixel-top")
    det.addComment("SMALL BOTTOM 128 PIXEL TUBE")
    det.addPixelatedTube("tube-bottom", NUM_PIXELS_PER_TUBE,
                         SMALL_BOTTOM_TUBE_SIZE, type_name="pixel-bottom")

    det.addComment("PIXEL FOR STANDARD 128 PIXEL TUBE")
    det.addCylinderPixel("pixel", (0.0, 0.0, 0.0), (0.0, 1.0, 0.0),
                         (TUBE_WIDTH/2.0),
                         (LARGE_TUBE_SIZE/NUM_PIXELS_PER_TUBE))
    det.addComment("PIXEL FOR SMALL TOP 128 PIXEL TUBE")
    det.addCylinderPixel("pixel-top", (0.0, 0.0, 0.0), (0.0, 1.0, 0.0),
                         (TUBE_WIDTH/2.0),
                         (SMALL_TOP_TUBE_SIZE/NUM_PIXELS_PER_TUBE))
    det.addComment("PIXEL FOR SMALL BOTTOM 128 PIXEL TUBE")
    det.addCylinderPixel("pixel-bottom", (0.0, 0.0, 0.0), (0.0, 1.0, 0.0),
                         (TUBE_WIDTH/2.0),
                         (SMALL_BOTTOM_TUBE_SIZE/NUM_PIXELS_PER_TUBE))

    det.addComment("MONITOR SHAPE")
    det.addComment("FIXME: Do something real here.")
    det.addDummyMonitor(0.01, 0.03)

    det.addComment("DETECTOR IDs")
    # FIXME: Set to zero when A and E rows are filled
    offset = 37888
    for i in range(len(row_id_list)):
        row_id_str = row_id_list[i] + " row"
        det_names = [x for x in detinfo["name"] if x.startswith(row_id_list[i])]
        id_list = []
        for j in range(len(det_names)):
            id_list.append(j * PIXELS_PER_BANK + offset)
            id_list.append((j+1) * PIXELS_PER_BANK - 1 + offset)
            id_list.append(None)

        offset += (PIXELS_PER_BANK * (j + 1))

        det.addDetectorIds(row_id_str, id_list)

    det.addComment("MONITOR IDs")
    det.addMonitorIds(["-1", "-2"])

    det.addComment("DETECTOR PARAMETERS")
    for row_id in row_id_list:
        row_id_str = row_id + " row"
        det.addDetectorParameters(row_id_str, TUBE_PRESSURE, TUBE_THICKNESS,
                                  TUBE_TEMPERATURE)

    #det.showGeom()
    det.writeGeom(xml_outfile)
