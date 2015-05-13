################################################################################
#
# A script to generate (HFIR) HB3A (four-circle)'s geometry file
#
################################################################################
#!/usr/bin/python

import sys
import datetime

import helper as helper


# definition of important parameters of HB2A
HB3AParam = {
    "source_distance": 2.0,
    "sample_position": [0., 0., 0.],
    "detector_distance": 1.0,
    "detector_size": [2.*0.0254, 2.*0.0254], # 2 inch x 2 inch
    "pixel_number": [256, 256],
    }

INST_NAME = 'HB3A'

def main(argv):
    """ Main
    """
    # Retrieve output file name
    if len(argv) < 2:
        outidfname = INST_NAME+"_Definition.xml"
    else: 
        outidfname = argv[1]
    
    # initialize MantidGeom object
    instname = INST_NAME    
    comment = "Created by Wenduo Zhou"
    today = datetime.datetime.today()
    valid_from = "%d-%02d-%02d %02d:%02d:%02d" % (today.year, today.month, today.day,
            today.hour, today.minute, today.second)
    print "valid_from: ", valid_from, " output to ", outidfname

    hb3a = helper.MantidGeom(instname, comment, valid_from)
    
    # add source/moderator
    hb3a.addComment("SOURCE")
    hb3a.addModerator(HB3AParam["source_distance"])
    # add sample
    hb3a.addComment("SAMPLE")
    hb3a.addSamplePosition(location=HB3AParam["sample_position"])

    # add panel
    hb3a.addComment("PANEL")
    panel = hb3a.addComponent2(type_name='panel', idstart=1, idfillbyfirst='y', idstepbyrow=256, blank_location=False)
    hb3a.addLocationRTP2(root=panel, name='bank1', 
            r = HB3AParam["detector_distance"], 
            t = '2theta -1.0*2theta+0.0', 
            p = '0.0',
            rot_x = None,
            rot_y = '2theta -1.0*2theta+0.0',
            rot_z = None)

    xpixels="256" 
    xstart="-0.078795" 
    xstep="+0.000618"
    ypixels="256" 
    ystart="-0.078795" 
    ystep="+0.000618"
    hb3a.addRectangularDetector(None, xpixels, xstart, xstep, ypixels, ystart, ystep)

    # add pixel information
    hb3a.addCuboidPixel(name="pixel", 
                        lfb_pt = [-0.000309, -0.000309, 0.0],
                        lft_pt = [-0.000309,  0.000309, 0.0],
                        lbb_pt = [-0.000309, -0.000309, -0.0001],
                        rfb_pt = [ 0.000309, -0.000309, 0.0],
                        is_type="detector", shape_id="pixel-shape")


    hb3a.showGeom()

    # write geometry
    hb2a.showGeom()
    hb2a.writeGeom(outidfname)
    
    return    
    
    
if __name__ == "__main__":
    main(sys.argv)
