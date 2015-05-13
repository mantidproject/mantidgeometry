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
    hb3a.addModerator(HB2AParam["source_distance"])
    # add sample
    hb3a.addComment("SAMPLE")
    hb3a.addSamplePosition(location=HB2AParam["sample_position"])

    # add panel
    hb3a.addComment("PANEL")


    


    
    # add detector idlist
    hb2a.addComment("Detector list def")
    hb2a.addDetectorIds(idname="detectors", idlist=[1,44,1]) 
    
    hb2a.addComponent(type_name="detectors", idlist="detectors")
    
    # detector banks
    hb2a.addComment("Detector Banks")
   
    locationdict = {
        "r_position": 0,
        "p_position": 0
        }
    
    typeattrib = {
        "component": "bank_uniq"
        }
    el = hb2a.makeTypeElement(name="detectors") #, extra_attrs=typeattrib)
    el_bank = hb2a.makeDetectorElement(name="bank_uniq", root=el)
    
    hb2a.addLocationRTP(root=el_bank, r='0.', t='rotangle rotangle+0.0', p='0.', rot_x='0.', rot_y='rotangle rotangle+0.0', rot_z='0.') 
    
    # add detectors
    hb2a.addComment("Definition of the unique existent bank (made of tubes)")
    
    bankattrib = {
        "component": "standard_tube"
        }
    
    el_dets = hb2a.makeTypeElement(name="bank_uniq") #, extra_attrs=bankattrib)
    el_tube = hb2a.makeDetectorElement(name="standard_tube", root=el_dets)
   
    twotheta = 0.0
    for i in xrange(1, 45):
        pixel_id = "anode%d" % (i)
        twotheta += gapdict[pixel_id]
        hb2a.addLocationPolar(el_tube, r='2.00', theta=str(twotheta), phi='0.0', name='tube_%d'%(i))
        
    # add single detector/pixel information
    hb2a.addComment("Definition of standard_tube")

    tubedict = {"outline": "yes"}
    el_tube = hb2a.makeTypeElement(name='standard_tube', extra_attrs=tubedict)
    el_pixel = hb2a.makeDetectorElement(name='standard_pixel', root=el_tube)
    hb2a.addLocation(el_pixel, x=0, y=0, z=0)
    
    # add standard_pixel
    hb2a.addCylinderPixel(name="standard_pixel", center_bottom_base=[0.0,0.0,0.0], axis=[0.,1.,0.],
        pixel_radius=0.00127, pixel_height=0.0114341328125, algebra='shape')
    
    """
    pixdict = {"is": "detector"}
    el_pixel = hb2a.makeTypeElement(name="standard_pixel", extra_attrs=pixdict)
    hb2a.makeCylinderPixel(root=el_pixel, center_bottom_base=[0.0,0.0,0.0], axis=[0.,0.,0.],
        pixel_radius=0.00127, pixel_height=0.0114341328125, algebra='shape')
    """
    
    # write geometry
    hb2a.showGeom()
    hb2a.writeGeom(outidfname)
    
    
    return    
    
    
if __name__ == "__main__":
    main(sys.argv)
