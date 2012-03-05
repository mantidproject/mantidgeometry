#! /usr/bin/python

from helper import MantidGeom
import math


def main():

    inst_name = "VISION"
    short_name = "VIS"

    xml_outfile = inst_name+"_Definition.xml"
    
    det = MantidGeom(inst_name, comment=" Created by Stuart Campbell ")
    det.addSnsDefaults(indirect=True)
    det.addComment("SOURCE AND SAMPLE POSITION")
    det.addModerator(-16.0)
    det.addSamplePosition()
    det.addComment("MONITORS")
    det.addMonitors(names=["monitor1"], distance=["-6.71625"], neutronic=True)

    # Backscattering diffraction detectors
    
    
    
    # 90' diffraction detectors
    
    # inelastic detectors
    


    det.addComment("MONITOR SHAPE")
    det.addComment("FIXME: Do something real here.")
    det.addDummyMonitor(0.01, 0.03)

    det.addComment("MONITOR IDs")
    det.addMonitorIds(["-1"])

    det.showGeom()
    det.writeGeom(xml_outfile)


if __name__ == '__main__':
	main()