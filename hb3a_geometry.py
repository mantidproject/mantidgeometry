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
    "detector_distance": 0.3518,
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


    # Calculate some dimension parameters for HB3A
    detsize_x = HB3AParam["detector_size"][0]
    numpixel_x = HB3AParam["pixel_number"][0]
    pixelsize_x = detsize_x/numpixel_x

    detsize_y = HB3AParam["detector_size"][1]
    numpixel_y = HB3AParam["pixel_number"][1]
    pixelsize_y = detsize_y/numpixel_y

    xrightpixel = (numpixel_x-1)*0.5*pixelsize_x
    ytoppixel = (numpixel_y-1)*0.5*pixelsize_y

    #print "Pixel size : %.6f X %.6f" % (pixelsize_x, pixelsize_y)
    #print "Right-most pixel position = %.6f, Top pixel position = %.6f" % (xrightpixel, ytoppixel)

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
    if False: 
        panel = hb3a.addComponent2(type_name='panel', idstart=1, idfillbyfirst='y', idstepbyrow=256, blank_location=False)
    else: 
        panel = hb3a.addComponent2(type_name='panel', idstart=1, idfillbyfirst='x', idstepbyrow=256, blank_location=False)
    hb3a.addLocationRTP2(root=panel, name='bank1', 
            r = HB3AParam["detector_distance"], 
            t = '2theta -1.0*2theta+0.0', 
            p = '0.0',
            rot_x = None,
            rot_y = '2theta -1.0*2theta+0.0',
            rot_z = None)

    #if False:
    #    xpixels="256" 
    #    xstart="-0.078795" 
    #    xstep="+0.000618"
    #    ypixels="256" 
    #    ystart="-0.078795" 
    #    ystep="+0.000618"
    #else:
    #    xpixels="256" 
    #    xstart="0.078795" 
    #    xstep="-0.000618"
    #    ypixels="256" 
    #    ystart="-0.078795" 
    #    ystep="+0.000618"

    # Define pixel positions in a rectangular detector and add detector
    xpixels = str(numpixel_x)
    xstart  = str(xrightpixel)
    xstep   = str(-1.*pixelsize_x)

    ypixels = str(numpixel_y)
    ystart  = str(ytoppixel)
    ystep   = str(-1.*pixelsize_y)

    hb3a.addRectangularDetector(None, xpixels, xstart, xstep, ypixels, ystart, ystep)

    # Add pixel information
    lfb_pt = [-1.*pixelsize_x*0.5, -1.*pixelsize_y*0.5, 0.0]      # left-front-bottom
    lft_pt = [-1.*pixelsize_x*0.5,     pixelsize_y*0.5, 0.0]      # left-front-top
    lbb_pt = [-1.*pixelsize_x*0.5, -1.*pixelsize_y*0.5, -0.0001]  # left-back-bottom
    rfb_pt = [    pixelsize_x*0.5, -1.*pixelsize_y*0.5, 0.0]      # right-front-bottom

    hb3a.addCuboidPixel(name="pixel", 
                        lfb_pt = lfb_pt,
                        lft_pt = lft_pt,
                        lbb_pt = lbb_pt,
                        rfb_pt = rfb_pt,
                        is_type="detector", 
                        shape_id="pixel-shape")


    # write geometry
    hb3a.showGeom()
    hb3a.writeGeom(outidfname)
    
    return    
    
    
if __name__ == "__main__":
    main(sys.argv)
