#!/usr/bin/env python

from helper import INCH_TO_METRE, MantidGeom
from lxml import etree as le # python-lxml on rpm based systems

def makeLoc(instr, det, name, x, y, z, rot, rot_inner=None, rot_innermost=None):
    sub = instr.addLocation(det, x=x, y=y, z=z, rot_y=rot, name=name)
    if rot_inner is not None:
        sub = le.SubElement(sub, "rot", **{"val":str(rot_inner)})
        if rot_innermost is not None:
            le.SubElement(sub, "rot", **{"val":str(rot_innermost), "axis-x":"0", "axis-y":"1", "axis-z":"0"})

def makeAttrs(idstart):
    """Return list of pixel ids appropriate for rectangular detectors."""
    return {"idstart":idstart, "idfillbyfirst":"y", "idstepbyrow":128}

if __name__ == "__main__":
    inst_name = "NOMAD"
    xml_outfile = inst_name+"_Definition.xml"

    # boiler plate stuff
    instr = MantidGeom(inst_name, comment=" Created by Peter Peterson ")
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
        instr.addComponent("Group%d" % i)

    # add in groups
    group1 = instr.makeTypeElement("Group1")
    det = instr.makeDetectorElement("one_inch", root=group1, extra_attrs=makeAttrs(0))
    makeLoc(instr, det, "bank1",
            x=-0.0900835, y=-0.50034125, z=1.940845, rot=-89.3663312,
            rot_inner=92.7740541972, rot_innermost=102.872503501)
    det = instr.makeDetectorElement("one_inch", root=group1, extra_attrs=makeAttrs(1024))
    makeLoc(instr, det, "bank2",
            x=-0.29825225, y=-0.41170625, z=1.940845, rot=-88.2250765278,
            rot_inner=92.2242357116, rot_innermost=128.605560457)
    det = instr.makeDetectorElement("one_inch", root=group1, extra_attrs=makeAttrs(2048))
    makeLoc(instr, det, "bank3",
            x=-0.44734875, y=-0.241528, z=1.940845, rot=-87.4360086541,
            rot_inner=91.2341549097, rot_innermost=154.31324826)
    det = instr.makeDetectorElement("one_inch", root=group1, extra_attrs=makeAttrs(3072))
    makeLoc(instr, det, "bank4",
            x=-0.507842, y=-0.023511625, z=1.940845, rot=-87.1545655812,
            rot_inner=90.0, rot_innermost=180.0)
    det = instr.makeDetectorElement("one_inch", root=group1, extra_attrs=makeAttrs(4096))
    makeLoc(instr, det, "bank5",
            x=-0.4677515, y=0.199161, z=1.940845, rot=-87.4360162435,
            rot_inner=88.7658487398, rot_innermost=-154.313248163)
    det = instr.makeDetectorElement("one_inch", root=group1, extra_attrs=makeAttrs(5120))
    makeLoc(instr, det, "bank6",
            x=-0.33501675, y=0.382388, z=1.940845, rot=-88.2250361723,
            rot_inner=87.7757484484, rot_innermost=-128.605997196)
    det = instr.makeDetectorElement("one_inch", root=group1, extra_attrs=makeAttrs(6144))
    makeLoc(instr, det, "bank7",
            x=-0.135927725, y=0.4898775, z=1.940845, rot=-89.3663380315,
            rot_inner=87.2259863472, rot_innermost=-102.872551406)
    det = instr.makeDetectorElement("one_inch", root=group1, extra_attrs=makeAttrs(7168))
    makeLoc(instr, det, "bank8",
            x=0.0900835227694, y=0.50034125, z=1.940845, rot=-90.6336689203,
            rot_inner=87.2259458689, rot_innermost=-77.1274935015)
    det = instr.makeDetectorElement("one_inch", root=group1, extra_attrs=makeAttrs(8192))
    makeLoc(instr, det, "bank9",
            x=0.29825225, y=0.41170625, z=1.940845, rot=-91.7749234722,
            rot_inner=87.7757642884, rot_innermost=-51.3944395427)
    det = instr.makeDetectorElement("one_inch", root=group1, extra_attrs=makeAttrs(9216))
    makeLoc(instr, det, "bank10",
            x=0.44734875, y=0.241528, z=1.940845, rot=-92.5639913459,
            rot_inner=88.7658450903, rot_innermost=-25.686751674)
    det = instr.makeDetectorElement("one_inch", root=group1, extra_attrs=makeAttrs(10240))
    makeLoc(instr, det, "bank11",
            x=0.507842, y=0.023511625, z=1.940845, rot=-92.8454344188,
            rot_inner=90.0)
    det = instr.makeDetectorElement("one_inch", root=group1, extra_attrs=makeAttrs(11264))
    makeLoc(instr, det, "bank12",
            x=0.46775125, y=-0.199161, z=1.940845, rot=-92.5639926177,
            rot_inner=91.2341401341, rot_innermost=25.6864726524)
    det = instr.makeDetectorElement("one_inch", root=group1, extra_attrs=makeAttrs(12288))
    makeLoc(instr, det, "bank13",
            x=0.33501675, y=-0.382388, z=1.940845, rot=-91.7749638277,
            rot_inner=92.2242515516, rot_innermost=51.3940028045)
    det = instr.makeDetectorElement("one_inch", root=group1, extra_attrs=makeAttrs(13312))
    makeLoc(instr, det, "bank14",
            x=0.1359277, y=-0.4898775, z=1.940845, rot=-90.6336619129,
            rot_inner=92.774014947, rot_innermost=77.1274554878)

    group2 = instr.makeTypeElement("Group2") # TODO
    group3 = instr.makeTypeElement("Group3") # TODO
    group4 = instr.makeTypeElement("Group4") # TODO
    group5 = instr.makeTypeElement("Group5") # TODO
    group6 = instr.makeTypeElement("Group6") # TODO

    instr.addComment("New Detector Panel (128x8) - one_inch")
    instr.addComment(" xsize=0.2112m  ysize=1.016m ")
    det = instr.makeTypeElement("one_inch",
                                {"is":"rectangular_detector", "type":"onepixel",
                                 "xpixels":8, "xstart":0.0924, "xstep":-0.0264,
                                 "ypixels":128, "ystart":0.508, "ystep":-0.0079375})
    le.SubElement(det, "properties")

    instr.addComment("New Detector Panel (128x8) - half_inch") # TODO
    instr.addComment("New Detector Panel (128x8) - half_inch_back") # TODO

    instr.addComment("Shape for monitors")
    instr.addComment("TODO: Update to real shape")
    instr.addDummyMonitor(0.01, .03)

    instr.addComment("Shape for half inch tube pixels")
    instr.addComment("TODO: should be cylinders")
    instr.addCuboidPixel("halfpixel",
                         (-0.003425, -0.00390625, 0.0),
                         (-0.003425, 0.00390625, 0.0),
                         (-0.003425, -0.00390625, -0.0001),
                         (0.003425, -0.00390625, 0.0),
                         shape_id="halfpixel-shape")

    instr.addComment("Shape for inch tube pixels")
    instr.addComment("TODO: should be cylinders")
    instr.addCuboidPixel("onepixel",
                         (-0.0132, -0.00396875, 0.0),
                         (-0.0132, 0.00396875, 0.0),
                         (-0.0132, -0.00396875, -0.0001),
                         (0.0132, -0.00396875, 0.0),
                         shape_id="onepixel-shape")

    # monitor ids
    instr.addComment("MONITOR IDS")
    instr.addMonitorIds([-1,-2])

    # write out the file
    instr.writeGeom(xml_outfile)
    instr.showGeom()
