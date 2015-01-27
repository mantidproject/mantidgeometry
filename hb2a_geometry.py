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

NUM_HB2A_DETS = 44
INST_NAME = 'HB2A'

def importGapFile(gapfilename):
    """ Import detector gap file from a file

    The gap file is a column file.  
    A new column is added as a new calibration is made on detectors' gaps.

    The right most column is always taken as the detectors' gaps to import. 
    """
    # import file
    try:
        gfile = open(gapfilename, "r")
        lines = gfile.readlines()
        gfile.close()
    except IOError as e:
        print "Unable to open or read file %s." % (gapfilename)
        raise e

    # parse file
    gapdict = {}
    idetgap = 1
    for line in lines:
        line = line.strip()
        if len(line) == 0:
            continue

        terms = line.split()
        try: 
            tmpgap = float(terms[-1])
            tmpdetname = 'anode%d' % (idetgap)
            gapdict[tmpdetname] = tmpgap
            idetgap += 1
        except ValueError as e:
            print e
    # ENDFOR (line)

    if len(gapdict.keys()) != NUM_HB2A_DETS:
        raise NotImplementedError("The number of gaps is %d. It is not correct for HB2A which has %d detectors."
                % (len(gapdict.keys()), NUM_HB2A_DETS))

    return gapdict


def main(argv):
    """ Main
    """
    if len(argv) != 1 and len(argv) != 3:
        print "Create HB2A IDF.  Run as: %s [IDF file name] [Gap file name]" % (
            argv[0])
        exit(2)

    if len(argv) == 3:
        outidfname = argv[1]
        gapfilename = argv[2]
    else:
        outidfname = INST_NAME+"_Definition.xml"
        gapfilename = 'HFIR/HB2A_exp0379__gaps.txt'
    
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
