#!/usr/bin/env python

from helper import INCH_TO_METRE, MantidGeom

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
    #det.addDummyMonitor(0.01, 0.03)
    #det.addComment("MONITOR IDs")
    #det.addMonitorIds(["-1"])

    # add the empty components
    for i in range(1,7):
        instr.addComponent("Group%d" % i)

    # add in groups
    group1 = instr.makeTypeElement("Group1")
    det = instr.makeDetectorElement("one_inch", root=group1, extra_attrs={"idstart":0, "idfillbyfirst":"y", "idstepbyrow":128})
    group2 = instr.makeTypeElement("Group2")
    group3 = instr.makeTypeElement("Group3")
    group4 = instr.makeTypeElement("Group4")
    group5 = instr.makeTypeElement("Group5")
    group6 = instr.makeTypeElement("Group6")

    # TODO
    instr.addComment("New Detector Panel (128x8) - one_inch")
    instr.addComment("New Detector Panel (128x8) - half_inch")
    instr.addComment("New Detector Panel (128x8) - half_inch_back")
    instr.addComment("Shape for monitors")
    instr.addComment("Shape for inch tube pixels")
    instr.addComment("Shape for half inch tube pixels")

    # monitor ids
    instr.addComment("MONITOR IDS")
    instr.addMonitorIds([-1,-2])

    # write out the file
    instr.writeGeom(xml_outfile)
    instr.showGeom()
