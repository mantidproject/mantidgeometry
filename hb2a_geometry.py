################################################################################
#
# A script to generate (HFIR) HB2A geometry
#
################################################################################
#!/usr/bin/python

import sys

import helper as helper


# definition of important parameters of HB2A
HB2AParam = {
    "moderator_distance": 2.0,
    "sample_position": [0., 0., 0.],
    }
            


def importGapFile(gapfilename):
    """
    """
    
    return {}


def main(argv):
    """ Main
    """
    if len(argv) < 3:
        print "Create HB2A IDF.  Run as: %s [IDF file name] [Gap file name]" % (
            argv[0])
        exit(2)
    
    outidfname = argv[1]
    gapfilename = argv[2]
    
    # import detector gap (delta-2theta) file
    gapdict = importGapFile(gapfilename)
    
    # initialize MantidGeom object
    instname = "HB2A"
    comment = "Created by Wenduo Zhou"
    valid_from = "2015-01-22 00:00:00"
    
    hb2a = helper.MantidGeom(instname, comment, valid_from)
    
    hb2a.addComment("SOURCE AND SAMPLE POSITION")
    # add source/moderator
    hb2a.addModerator(HB2AParam["moderator_distance"])
    # add sample
    hb2a.addSamplePosition(location=HB2AParam["sample_position"])
    
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
    
    for i in xrange(1, 45):
        twotheta = 0.0 + float(i)*2.6
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