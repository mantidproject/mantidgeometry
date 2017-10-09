from __future__ import (print_function)
from lxml import etree as le # python-lxml on rpm based systems
from string import split,join
import numpy as np
from itertools import groupby
from operator import itemgetter

INCH_TO_METRE = 0.0254
DEG_TO_RAD = 0.0174533 # degrees to radians according to idl
XMLNS = "http://www.mantidproject.org/IDF/1.0"
XSI = "http://www.w3.org/2001/XMLSchema-instance"
SCHEMA_LOC = "http://www.mantidproject.org/IDF/1.0 http://schema.mantidproject.org/IDF/1.0/IDFSchema.xsd"

class MantidGeom:

    def __init__(self, instname, comment=None, valid_from=None, valid_to=None):
        from datetime import datetime
        if valid_to is None:
            valid_to = str(datetime(2100, 1, 31, 23, 59, 59))
        last_modified = str(datetime.now())
        if valid_from is None:
            valid_from = last_modified
        self.__root = le.Element("instrument",
                                 attrib={"name": instname,
                                    "valid-from": valid_from,
                                    "valid-to": valid_to,
                                    "last-modified": last_modified
                                    },
                                 nsmap={None: XMLNS, "xsi": XSI}
                                 )
        self.__root.attrib['{{{pre}}}schemaLocation'.format(pre=XSI)] = SCHEMA_LOC 
        if comment is not None:
            if type(comment) == list or type(comment) == tuple:
                for bit in comment:
                    self.__root.append(le.Comment(bit))
            else:
                self.__root.append(le.Comment(comment))

    def writeGeom(self, filename):
        """
        Write the XML geometry to the given filename
        """
        fh = open(filename, "w")
        fh.write(le.tostring(self.__root, pretty_print=True,
                             xml_declaration=True))
        fh.close()

    def showGeom(self):
        """
        Print the XML geometry to the screeen
        """
        print(le.tostring(self.__root, pretty_print=True,
                             xml_declaration=True))

    def addSnsDefaults(self, indirect=False, default_view=None):
        """
        Set the default properties for SNS geometries
        """
        defaults_element = le.SubElement(self.__root, "defaults")
        le.SubElement(defaults_element, "length", unit="metre")
        le.SubElement(defaults_element, "angle", unit="degree")
        if (indirect):
          le.SubElement(defaults_element, "indirect-neutronic-positions")
        
        reference_element = le.SubElement(defaults_element, "reference-frame")
        le.SubElement(reference_element, "along-beam", axis="z")
        le.SubElement(reference_element, "pointing-up", axis="y")
        le.SubElement(reference_element, "handedness", val="right")
        if default_view is not None:
            le.SubElement(defaults_element, "default-view", view=default_view)

    def addComment(self, comment):
        """
        Add a global comment to the XML file
        """
        self.__root.append(le.Comment(comment))

    def addModerator(self, distance):
        """
        This adds the moderator position for the instrument
        """
        source = le.SubElement(self.__root, "component", type="moderator")
        try:
          distance = float(distance)
          if distance > 0:
            distance *= -1.0
          le.SubElement(source, "location", z=str(distance))
        except:
          pos_loc = le.SubElement(source, "location")
          processed=split(str(distance))
          if len(processed)==1:
            log=le.SubElement(pos_loc,"parameter",**{"name":"z"})
            le.SubElement(log, "logfile", **{"id":distance})
          else:
            equation=join(processed[1:]).replace(processed[0],"value")
            log=le.SubElement(pos_loc,"parameter",**{"name":"z"})
            le.SubElement(log, "logfile", **{"id":processed[0],"eq":equation})

        le.SubElement(self.__root, "type",
                      **{"name":"moderator", "is":"Source"})

    def addCuboidModerator(self, distance,width=0.12,height=0.12,depth=0.06):
        """
        This adds the moderator position for the instrument.
        Use this instead of addModerator for cuboid moderator.
        """
        source = le.SubElement(self.__root, "component", type="moderator")
        try:
          distance = float(distance)
          if distance > 0:
            distance *= -1.0
          le.SubElement(source, "location", z=str(distance))
        except:
          pos_loc = le.SubElement(source, "location")
          processed=split(str(distance))
          if len(processed)==1:
            log=le.SubElement(pos_loc,"parameter",**{"name":"z"})
            le.SubElement(log, "logfile", **{"id":distance})
          else:
            equation=join(processed[1:]).replace(processed[0],"value")
            log=le.SubElement(pos_loc,"parameter",**{"name":"z"})
            le.SubElement(log, "logfile", **{"id":processed[0],"eq":equation})

        type_element = le.SubElement(self.__root, "type",
                      **{"name":"moderator", "is":"Source"})
        cuboid = le.SubElement(type_element, "cuboid", id="shape")
        le.SubElement(cuboid, "left-front-bottom-point",
                      x=str(-width/2), y=str(-height/2),z=str(-depth/2))
        le.SubElement(cuboid, "left-front-top-point",
                      x=str(-width/2), y=str(height/2),z=str(-depth/2))
        le.SubElement(cuboid, "left-back-bottom-point",
                      x=str(-width/2), y=str(-height/2),z=str(depth/2))
        le.SubElement(cuboid, "right-front-bottom-point",
                      x=str(width/2), y=str(-height/2),z=str(-depth/2))
        le.SubElement(type_element, "algebra", val="shape")

    def addSamplePosition(self, location=None, coord_type="cartesian"):
        """
        Adds the sample position to the file. The coordinates should be passed
        as a tuple of (x, y, z) or (r, t, p). Default location is (0, 0, 0) in
        cartesian coordinates.
        """
        source = le.SubElement(self.__root, "component", type="sample-position")
        if location is None:
            le.SubElement(source, "location", x="0.0", y="0.0", z="0.0")
        else:
            if coord_type is "cartesian":
                le.SubElement(source, "location", x=str(location[0]),
                              y=str(location[1]), z=str(location[2]))
            if coord_type is "spherical":
                le.SubElement(source, "location", r=str(location[0]),
                              t=str(location[1]), p=str(location[2]))
                    
        le.SubElement(self.__root, "type",
                      **{"name":"sample-position", "is":"SamplePos"})

    def addDetectorPixels(self, name, r=[], theta=[], phi=[], names=[], energy=[]):

        #component = le.SubElement(self.__root, "component",
        #                          type=name, idlist=name)

        type_element = le.SubElement(self.__root, "type", name=name)
        #le.SubElement(type_element, "location")

        for i in range(len(r)):
            for j in range(len(r[i])):
                if (str(r[i][j]) != "nan"):
                    basecomponent = le.SubElement(type_element, "component", type="pixel")
                    location_element = le.SubElement(basecomponent, "location", r=str(r[i][j]),
                          t=str(theta[i][j]), p=str(phi[i][j]), name=str(names[i][j]))
                    le.SubElement(location_element, "facing", x="0.0", y="0.0", z="0.0")
                    #le.SubElement(basecomponent, "properties")
                    efixed_comp = le.SubElement(basecomponent, "parameter", name="Efixed")
                    le.SubElement(efixed_comp, "value", val=str(energy[i][j]))

    def addDetectorPixelsIdList(self, name, r=[], names=[], elg="single_list"):
        """
        Add the detector IDs
        :param name: name of the component owning the detector pixes
        :param r: (list of list) distances from sample
        :param names: (list of list) pixel ID's
        :param elg: element grouping, 'single_list' creates one element per pixel,
         'multiple_ranges' creates one element for every range of physical pixels
        """
        if elg=="single_list":
            component = le.SubElement(self.__root, "idlist",
                                      idname=name)
            for i in range(len(r)):
                for j in range(len(r[i])):
                    # nan indicates unphysical pixel
                    if (str(r[i][j]) != "nan"):
                        le.SubElement(component, "id", val=str(names[i][j]))
        elif elg=="multiple_ranges":
            # find ID's of pixels with physical distances
            pxids = names.flatten()[np.where(~np.isnan(r.flatten()))[0]]
            # Split pxids into continous chunks of pixel ID's
            idlist = list()
            for k, g in groupby(enumerate(pxids), lambda (i, x): i-x):
                chunk = map(itemgetter(1), g)
                idlist += [chunk[0], chunk[-1], None]
            # Create one element for every continous chunks
            self.addDetectorIds(name, idlist)
        else:
            raise NotImplementedError("invalid element grouping scheme")

    def addMonitors(self, distance=[], names=[], neutronic=False):
        """
        Add a list of monitors to the geometry. 
        """
        if len(distance) != len(names):
            raise IndexError("Distance and name list must be same size!")
        
        component = le.SubElement(self.__root, "component",
                                  type="monitors", idlist="monitors")
        le.SubElement(component, "location")
        
        type_element = le.SubElement(self.__root, "type", name="monitors")
        basecomponent = le.SubElement(type_element, "component",
                                      **{"type":"monitor"})
        
        for i in range(len(distance)):
            try:
                zi=float(distance[i]) # check if float
                zi=str(zi) # convert it to a string for lxml
                location = le.SubElement(basecomponent, "location", z=zi, name=names[i])
                if neutronic:
                    le.SubElement(location, "neutronic", z=zi)
            except:
                pos_loc=le.SubElement(basecomponent, "location",name=names[i])
                processed=split(str(distance[i]))
                if len(processed)==1:
                    log=le.SubElement(pos_loc,"parameter",**{"name":"z"})
                    le.SubElement(log, "logfile", **{"id":str(distance[i])})
                else:
                    equation=join(processed[1:]).replace(processed[0],"value")
                    log=le.SubElement(pos_loc,"parameter",**{"name":"z"})
                    le.SubElement(log, "logfile", **{"id":processed[0],"eq":equation})

    def addComponent(self, type_name, idlist=None, root=None, blank_location=True):
        """
        Add a component to the XML definition. A blank location is added.
        """
        if root is None:
            root = self.__root

        if idlist is not None:
            comp = le.SubElement(root, "component", type=type_name,
                                 idlist=idlist)
        else:
            comp = le.SubElement(root, "component", type=type_name)
        l=comp
        if blank_location:
            l = le.SubElement(comp, "location")
        return l

    def addComponentILL(self, type_name, x, y, z, isType=None, idlist=None, root=None):
        """
        Add a component with location to the XML definition.
        """
        if root is None:
            root = self.__root

        comp = le.SubElement(root, "component", type=type_name)

        self.addLocation(comp, x, y, z)

        if isType is "Source":
            le.SubElement(self.__root, "type",
                          **{"name": type_name, "is": "Source"})
        if isType is "SamplePos":
            le.SubElement(self.__root, "type",
                          **{"name": type_name, "is": "SamplePos"})

    def addComponentRectangularDetector(self, type_name, x, y, z, idstart, idfillbyfirst, idstepbyrow, rotx=None, roty=None,rotz=None, root=None):
        """

        Returns: a component argument -> rectangular detector

        """
        if root is None:
            root = self.__root

        comp = le.SubElement(root, "component", type=type_name, idstart=idstart, idfillbyfirst=idfillbyfirst,
                             idstepbyrow=idstepbyrow)
        self.addLocation(comp, x, y, z, rot_x=rotx, rot_y=roty, rot_z=rotz)

    def makeTypeElement(self, name, extra_attrs={}):
        """
        Return a simple type element.
        """
        for key in extra_attrs.keys():
            extra_attrs[key] = str(extra_attrs[key])  # convert everything to strings
        return le.SubElement(self.__root, "type", name=name, **extra_attrs)
            
    def makeDetectorElement(self, name, idlist_type=None, root=None, extra_attrs={}, location=[0.0, 0.0, 0.0]):
        """
        Return a component element.
        """
        if root is not None:
            root_element = root
        else:
            root_element = self.__root

        for key in extra_attrs.keys():
            extra_attrs[key] = str(extra_attrs[key]) # convert everything to strings

        if idlist_type is not None:
            comp = le.SubElement(root_element, "component", type=name,
                                     idlist=idlist_type, **extra_attrs)
        else:
            comp = le.SubElement(root_element, "component", type=name, **extra_attrs)

        if location[0] > 0.0 or location[1] > 0.0 or location[2] > 0.0:
            self.addLocation(comp, location[0], location[1], location[2])
        return comp

    def makeIdListElement(self, name):
        return le.SubElement(self.__root, "idlist", idname=name)

    def addDetector(self, x, y, z, rot_x, rot_y, rot_z, name, comp_type, usepolar=None, facingSample=False,
                    neutronic=False, nx=None,  ny=None, nz=None):
        """
        Add a detector in a type element for the XML definition.
        """
        type_element = le.SubElement(self.__root, "type", name=name)
        comp_element = le.SubElement(type_element, "component", type=comp_type)
        
        if usepolar is not None:
            self.addLocationPolar(comp_element, x, y, z, facingSample)
        else:
            self.addLocation(comp_element, x, y, z, rot_x, rot_y, rot_z, facingSample=facingSample,
                neutronic=neutronic, nx=nx, ny=ny, nz=nz)

    def addRectangularDetector(self, name, type, xstart, xstep, xpixels, ystart, ystep, ypixels):
        """
        Add a rectangular detector in a type element for the XML definition.
        """
        type_element = le.SubElement(self.__root, "type",
                                     xstart=xstart, xstep=xstep, xpixels=xpixels,
                                     ystart=ystart, ystep=ystep, ypixels=ypixels,
                                     **{"name": name, "is": "rectangular_detector", "type": type})

    def addSingleDetector(self, root, x, y, z, rot_x, rot_y, rot_z, name=None,
                          usepolar=None, facingSample=False):
        """
        Add a single detector by explicit declaration. The rotation order is
        performed as follows: y, x, z.
        """
        if name is None:
            name = "bank"

        if usepolar is not None:
            self.addLocationPolar(root, x, y, z, name)
        else:
            self.addLocation(root, x, y, z, rot_x, rot_y, rot_z, name, facingSample=facingSample)

    def addLocation(self, root, x, y, z, rot_x=None, rot_y=None, rot_z=None, name=None,
                    facingSample=False, neutronic=False, nx=None, ny=None, nz=None):
        """
        Add a location element to a specific parent node given by root.
        """
        if name is not None:
            pos_loc = le.SubElement(root, "location", x=str(x), y=str(y), z=str(z), name=name)
        else:
            pos_loc = le.SubElement(root, "location", x=str(x), y=str(y), z=str(z))
                        
        if rot_y is not None:
            r1 = le.SubElement(pos_loc, "rot", **{"val":str(rot_y), "axis-x":"0",
                                                  "axis-y":"1", "axis-z":"0"})
        else:
            r1 = pos_loc

        if rot_x is not None:
            r2 = le.SubElement(r1, "rot", **{"val":str(rot_x), "axis-x":"1",
                                             "axis-y":"0", "axis-z":"0"})
        else:
            r2 = r1

        if rot_z is not None:
            r3 = le.SubElement(r2, "rot", **{"val":str(rot_z), "axis-x":"0",
                                             "axis-y":"0", "axis-z":"1"})
        else:
            r3 = r2

        if facingSample:
            le.SubElement(pos_loc, "facing", x="0.0", y="0.0", z="0.0")

        if neutronic:
            le.SubElement(pos_loc, "neutronic", x=str(nx), y=str(ny), z=str(nz))

        return r3

    def addLocationPolar(self, root, r, theta, phi, name=None):
        if name is not None:
            pos_loc = le.SubElement(root, "location", r=r, t=theta, p=phi, name=name)
        else:
            pos_loc = le.SubElement(root, "location", r=r, t=theta, p=phi)
        return pos_loc

    def addLocationRTP(self, root, r, t, p, rot_x, rot_y, rot_z, name=None):
        """
        Add a location element to a specific parent node given by root, using r, theta, phi coordinates.
        """
        try:
          rf=float(r)
          tf=float(f)
          pf=float(p)
          if name is not None:
            pos_loc = le.SubElement(root, "location", r=r, t=t, p=p, name=name)
          else:
            pos_loc = le.SubElement(root, "location", r=r, t=t, p=p)
        except:
          if name is not None:
            pos_loc = le.SubElement(root, "location", name=name)
          else:
            pos_loc = le.SubElement(root, "location")
            log=le.SubElement(pos_loc,"parameter",**{"name":"r-position"})
            try:
              rf=float(r)               
              le.SubElement(log, "value", **{"val":r})    
            except Exception as e:
              print("Excpetion: {}".format(str(e)))
              processed=split(str(r))
              if len(processed)==1:
                le.SubElement(log, "logfile", **{"id":r})
              else:
                equation=join(processed[1:]).replace(processed[0],"value")
                le.SubElement(log, "logfile", **{"id":processed[0],"eq":equation})
            log=le.SubElement(pos_loc,"parameter",**{"name":"t-position"})
            try:
              le.SubElement(log, "value", **{"val":t})
            except:  
              processed=split(str(t))
              if len(processed)==1:
                le.SubElement(log, "logfile", **{"id":t})
              else:
                equation=join(processed[1:]).replace(processed[0],"value")
                le.SubElement(log, "logfile", **{"id":processed[0],"eq":equation})        
            log=le.SubElement(pos_loc,"parameter",**{"name":"p-position"})
            try:
              le.SubElement(log, "value", **{"val":p})    
            except:  
              processed=split(str(p))
              if len(processed)==1:
                le.SubElement(log, "logfile", **{"id":p})
              else:
                equation=join(processed[1:]).replace(processed[0],"value")
                le.SubElement(log, "logfile", **{"id":processed[0],"eq":equation})  
          #add rotx, roty, rotz
          #Regardless of what order rotx, roty and rotz is specified in the IDF,
          #the combined rotation is equals that obtained by applying rotx, then roty and finally rotz. 
          if rot_x is not None:
            log=le.SubElement(pos_loc,"parameter",**{"name":"rotx"})
            try:
              le.SubElement(log, "value", **{"val":rot_x})    
            except:  
              processed=split(str(rot_x))
              if len(processed)==1:
                le.SubElement(log, "logfile", **{"id":rot_x})
              else:
                equation=join(processed[1:]).replace(processed[0],"value")
                le.SubElement(log, "logfile", **{"id":processed[0],"eq":equation})  
          if rot_y is not None:
            log=le.SubElement(pos_loc,"parameter",**{"name":"roty"})
            try:
              le.SubElement(log, "value", **{"val":rot_y})    
            except:  
              processed=split(str(rot_y))
              if len(processed)==1:
                le.SubElement(log, "logfile", **{"id":rot_y})
              else:
                equation=join(processed[1:]).replace(processed[0],"value")
                le.SubElement(log, "logfile", **{"id":processed[0],"eq":equation})  
          if rot_z is not None:
            log=le.SubElement(pos_loc,"parameter",**{"name":"rotz"})
            try:
              le.SubElement(log, "value", **{"val":rot_z})    
            except:  
              processed=split(str(rot_z))
              if len(processed)==1:
                le.SubElement(log, "logfile", **{"id":rot_z})
              else:
                equation=join(processed[1:]).replace(processed[0],"value")
                le.SubElement(log, "logfile", **{"id":processed[0],"eq":equation})  

    def addNPack(self, name, num_tubes, tube_width, air_gap, type_name="tube",
                 neutronic=False, neutronicIsPhysical=False):
        """
        Add a block of N tubes in a pack. A name for the pack type needs
        to be specified as well as the number of tubes in the pack, the tube
        width and air gap. If there are going to be more than one type tube
        specified later, an optional type name can be given. The default tube
        type name will be tube.
        """
        type_element = le.SubElement(self.__root, "type", name=name)
        le.SubElement(type_element, "properties")

        component = le.SubElement(type_element, "component", type=type_name)

        effective_tube_width = tube_width + air_gap
        
        pack_start = (effective_tube_width / 2.0) * (1 - num_tubes)

        for i in range(num_tubes):
            tube_name = "tube%d" % (i + 1)
            x = pack_start + (i * effective_tube_width)
            location_element = le.SubElement(component, "location", name=tube_name, x=str(x))
            if (neutronic):
                if (neutronicIsPhysical):
                    le.SubElement(location_element, "neutronic", x=str(x))
                else:
                    le.SubElement(location_element, "neutronic", x="0.0")

    def addPixelatedTube(self, name, num_pixels, tube_height,
                         type_name="pixel", neutronic=False, neutronicIsPhysical=False):
        """
        Add a tube of N pixels. If there are going to be more than one pixel
        type specified later, an optional type name can be given. The default
        pixel type name will be pixel.
        The neutronic flag indicates that the neutronic position will also be
        included.  The neutronicIsPhysical will if True, set the neutronic position to
        be the same as the physical - otherwise the neutronic position will be 0.0.
        """
        type_element = le.SubElement(self.__root, "type", outline="yes",
                                     name=name)
                                     
        le.SubElement(type_element, "properties")
        
        component = le.SubElement(type_element, "component", type=type_name)

        pixel_width = tube_height / num_pixels
        tube_start = (pixel_width / 2.0) * (1 - num_pixels)

        for i in range(num_pixels):
            pixel_name = "pixel%d" % (i + 1)
            y = tube_start + (i * pixel_width)
            location_element = le.SubElement(component, "location", name=pixel_name, y=str(y))
            if (neutronic):
                if (neutronicIsPhysical):
                    le.SubElement(location_element, "neutronic", y=str(y))
                else:
                    le.SubElement(location_element, "neutronic", y="0.0")

    def addCylinderPixel(self, name, center_bottom_base, axis, pixel_radius,
                         pixel_height, is_type="detector", algebra="cyl-approx"):
        """
        Add a cylindrical pixel. The center_bottom_base is a 3-tuple of radius,
        theta, phi. The axis is a 3-tuple of x, y, z.
        """
        type_element = le.SubElement(self.__root, "type",
                                     **{"name":name, "is":is_type})
        #cylinder = le.SubElement(type_element, "cylinder", id="cyl-approx")
        cylinder = le.SubElement(type_element, "cylinder", id=algebra)
        le.SubElement(cylinder, "centre-of-bottom-base",
                      r=str(center_bottom_base[0]),
                      t=str(center_bottom_base[1]),
                      p=str(center_bottom_base[2]))
        le.SubElement(cylinder, "axis", x=str(axis[0]), y=str(axis[1]),
                      z=str(axis[2]))
        le.SubElement(cylinder, "radius", val=str(pixel_radius))
        le.SubElement(cylinder, "height", val=str(pixel_height))
        #le.SubElement(type_element, "algebra", val="cyl-approx")
        le.SubElement(type_element, "algebra", val=algebra)

        return

    def addCuboidPixel(self, name, lfb_pt, lft_pt, lbb_pt, rfb_pt,
                      is_type="detector", shape_id="shape"):
        """
        Add a cuboid pixel. The origin of the cuboid is assumed to be the
        center of the front face of the cuboid. The parameters lfb_pt, lft_pt,
        lbb_pt, rfb_pt are 3-tuple of x, y, z.
        """
        type_element = le.SubElement(self.__root, "type",
                                     **{"name":name, "is":is_type})
        cuboid = le.SubElement(type_element, "cuboid", id=shape_id)
        le.SubElement(cuboid, "left-front-bottom-point", x=str(lfb_pt[0]),
                      y=str(lfb_pt[1]), z=str(lfb_pt[2]))
        le.SubElement(cuboid, "left-front-top-point", x=str(lft_pt[0]),
                      y=str(lft_pt[1]), z=str(lft_pt[2]))
        le.SubElement(cuboid, "left-back-bottom-point", x=str(lbb_pt[0]),
                      y=str(lbb_pt[1]), z=str(lbb_pt[2]))
        le.SubElement(cuboid, "right-front-bottom-point", x=str(rfb_pt[0]),
                      y=str(rfb_pt[1]), z=str(rfb_pt[2]))
        le.SubElement(type_element, "algebra", val=shape_id)

    def addDummyMonitor(self, radius, height):
        """
        Add a dummy monitor with some-shape.
        """
        type_element = le.SubElement(self.__root, "type", **{"name":"monitor",
                                                             "is":"monitor"})
        cylinder = le.SubElement(type_element, "cylinder", id="cyl-approx")
        le.SubElement(cylinder, "centre-of-bottom-base", p="0.0", r="0.0",
                      t="0.0")
        le.SubElement(cylinder, "axis", x="0.0", y="0.0", z="1.0")
        le.SubElement(cylinder, "radius", val=str(radius))
        le.SubElement(cylinder, "height", val=str(height))
        
        le.SubElement(type_element, "algebra", val="cyl-approx")
    
    def addCuboidMonitor(self,width,height,depth):
        """
        Add a cuboid monitor
        """
        type_element = le.SubElement(self.__root, "type", **{"name":"monitor",
                                                             "is":"monitor"})
        cuboid = le.SubElement(type_element, "cuboid", id="shape")
        le.SubElement(cuboid, "left-front-bottom-point", x=str(-width/2), y=str(-height/2),z=str(-depth/2))
        le.SubElement(cuboid, "left-front-top-point", x=str(-width/2), y=str(height/2),z=str(-depth/2))
        le.SubElement(cuboid, "left-back-bottom-point", x=str(-width/2), y=str(-height/2),z=str(depth/2))
        le.SubElement(cuboid, "right-front-bottom-point", x=str(width/2), y=str(-height/2),z=str(-depth/2))
        le.SubElement(type_element, "algebra", val="shape")

    def addDetectorIds(self, idname, idlist):
        """
        Add the detector IDs. A list is provided that must be divisible by 3.
        The list should be specified as [start1, end1, step1, start2, end2,
        step2, ...]. If no step is required, use None.
        """
        if len(idlist) % 3 != 0:
            raise IndexError("Please specifiy list as [start1, end1, step1, "\
                             +"start2, end2, step2, ...]. If no step is"\
                             +"required, use None.")
        num_ids = len(idlist) / 3
        id_element = le.SubElement(self.__root, "idlist", idname=idname)
        for i in range(num_ids):
            if idlist[(i*3)+2] is None:
                le.SubElement(id_element, "id", start=str(idlist[(i*3)]),
                              end=str(idlist[(i*3)+1]))
            else:
                le.SubElement(id_element, "id", start=str(idlist[(i*3)]),
                              step=str(idlist[(i*3)+2]),
                              end=str(idlist[(i*3)+1]))
        
    def addMonitorIds(self, ids=[]):
        """
        Add the monitor IDs.
        """
        idElt = le.SubElement(self.__root, "idlist", idname="monitors")
        for i in range(len(ids)):
            le.SubElement(idElt, "id", val=str(ids[i]))

    def addDetectorParameters(self, component_name, *args):
        """
        Add detector parameters to a particular component name. Args is an
        arbitrary list of 3-tuples containing the following information:
        (parameter name, parameter value, parameter units).
        """
        complink = le.SubElement(self.__root, "component-link",
                                 name=component_name)
        for arg in args:
            if len(arg) != 3:
                raise IndexError("Will not be able to parse:", arg)
            
            par = le.SubElement(complink, "parameter", name=arg[0])
            le.SubElement(par, "value", val=str(arg[1]), units=str(arg[2]))

    def addDetectorStringParameters(self, component_name, *args):
        """
        Add detector parameters to a particular component name. Args is an
        arbitrary list of 2-tuples containing the following information:
        (string name, string value).
        """
        complink = le.SubElement(self.__root, "component-link",
                                 name=component_name)
        for arg in args:
            if len(arg) != 2:
                raise IndexError("Will not be able to parse:", arg)
            par = le.SubElement(complink, "parameter", name=arg[0], type="string")
            le.SubElement(par, "value", val=str(arg[1]))

    def addChopper(self, component_name, distance, *args):
        """
        Add chopper position.
        *args are for attaching logfile to the chopper component
              should contain list of parameter name, logfile string
              and optionally extractSingleValueAs (default mean)
        """
        component = le.SubElement(self.__root, "component", type = component_name)
        distance = float(distance)
        le.SubElement(component, "location", z=str(distance))
        for arg in args:
            log = le.SubElement(component, "parameter", name=arg[0])
            if len(arg) == 2:
                le.SubElement(log, "logfile", id=arg[1])
            elif len(arg) == 3:
                le.SubElement(log, "logfile", **{"id":arg[1], "extract-single-value-as":arg[2]})
            else:
                raise IndexError("Will not be able to parse:", arg)

    def addEmptyChopper(self,component_name, distance, is_type="chopper"):
        """
        Add an empty chopper position.
        """
        component = le.SubElement(self.__root, "component", type = component_name)
        distance = float(distance)
        le.SubElement(component, "location", z=str(distance))
        le.SubElement(self.__root, "type",
                      **{"name":component_name, "is":is_type})

    def addSingleDiskChopper(self, name, center=(-0.17, 0.0),
                             hole=(0.04,0.02), radius=0.2,
                             height=0.02, is_type="chopper"):
        """
        Add a single disk chopper. The chopper center and hole dimensions
        is x, y relative to beam center.
        """
        type_element = le.SubElement(self.__root, "type",
                                     **{"name":name, "is":is_type})
        cylinder = le.SubElement(type_element, "cylinder", id="body")
        le.SubElement(cylinder, "centre-of-bottom-base",x=str(center[0]),
                      y=str(center[1]),z="0.0")
        le.SubElement(cylinder, "axis", x="0.0", y="0.0", z="1.0")
        le.SubElement(cylinder, "radius", val=str(radius))
        le.SubElement(cylinder, "height", val=str(height))
        cuboid = le.SubElement(type_element, "cuboid", id="hole")
        le.SubElement(cuboid, "left-front-bottom-point",
                      x=str(hole[0]),y=str(-hole[1]),z="0.0")
        le.SubElement(cuboid, "left-front-top-point",
                      x=str(hole[0]),y=str(-hole[1]),z=str(height))
        le.SubElement(cuboid, "left-back-bottom-point",
                      x=str(-hole[0]),y=str(-hole[1]),z="0.0")
        le.SubElement(cuboid, "right-front-bottom-point",
                      x=str(hole[0]),y=str(hole[1]),z="0.0")
        le.SubElement(type_element, "algebra", val="body (# hole)")
        

    def addDoubleDiskChopper(self, name, center=(0.17, 0.0),
                             hole=(0.04,0.02), radius=0.2,
                             height=0.02, separation=0.015, is_type="chopper"):
        """
        Add a double disk chopper. The chopper center and hole dimensions
        is x, y relative to beam center.
        """
        type_element = le.SubElement(self.__root, "type",
                                     **{"name":name, "is":is_type})
        cylinder1 = le.SubElement(type_element, "cylinder", id="body1")
        le.SubElement(cylinder1, "centre-of-bottom-base",x=str(center[0]),
                      y=str(center[1]),z="0.0")
        le.SubElement(cylinder1, "axis", x="0.0", y="0.0", z="1.0")
        le.SubElement(cylinder1, "radius", val=str(radius))
        le.SubElement(cylinder1, "height", val=str(height))
        cuboid = le.SubElement(type_element, "cuboid", id="hole")
        le.SubElement(cuboid, "left-front-bottom-point",
                      x=str(hole[0]),y=str(-hole[1]),z="0.0")
        le.SubElement(cuboid, "left-front-top-point",
                      x=str(hole[0]),y=str(-hole[1]),z=str(height*2+separation))
        le.SubElement(cuboid, "left-back-bottom-point",
                      x=str(-hole[0]),y=str(-hole[1]),z="0.0")
        le.SubElement(cuboid, "right-front-bottom-point",
                      x=str(hole[0]),y=str(hole[1]),z="0.0")
        cylinder2 = le.SubElement(type_element, "cylinder", id="body2")
        le.SubElement(cylinder2, "centre-of-bottom-base",x=str(-center[0]),
                      y=str(-center[1]),z=str(height+separation))
        le.SubElement(cylinder2, "axis", x="0.0", y="0.0", z="1.0")
        le.SubElement(cylinder2, "radius", val=str(radius))
        le.SubElement(cylinder2, "height", val=str(height))
        le.SubElement(type_element, "algebra", val="(body1 : body2) (#hole)")

    def addFermiChopper(self, name, radius=0.05, height=0.065,width=0.061,is_type="chopper"):
        """
         Add a Fermi chopper 
        """
        y0=-height/2.0
        x0=-width/2.0
        type_element = le.SubElement(self.__root, "type",
                                     **{"name":name, "is":is_type})
        cylinder = le.SubElement(type_element, "cylinder", id="body")
        le.SubElement(cylinder, "centre-of-bottom-base",x="0.0",y=str(y0),z="0.0")
        le.SubElement(cylinder, "axis", x="0.0", y="1.0", z="0.0")
        le.SubElement(cylinder, "radius", val=str(radius))
        le.SubElement(cylinder, "height", val=str(height))
        cuboid = le.SubElement(type_element, "cuboid", id="hole")
        le.SubElement(cuboid, "left-front-bottom-point", x=str(x0),y=str(y0),z=str(-radius))
        le.SubElement(cuboid, "left-front-top-point", x=str(x0),y=str(-y0),z=str(-radius))
        le.SubElement(cuboid, "left-back-bottom-point", x=str(-x0),y=str(y0),z=str(-radius))
        le.SubElement(cuboid, "right-front-bottom-point",x=str(x0),y=str(y0),z=str(radius))
        le.SubElement(type_element, "algebra", val="body (# hole)")
        
    def addVerticalAxisT0Chopper(self, name, radius=0.175, height=0.090,width_out=0.095,width_in=0.085,is_type="chopper"):
        """
         Add a Vertical Axis T0 chopper 
        """
        y0=-height/2.0
        #x0=-width/2.0
        x0_o=-width_out/2.0
        x0_i=-width_in/2.0
        type_element = le.SubElement(self.__root, "type",
                                     **{"name":name, "is":is_type})
        cylinder = le.SubElement(type_element, "cylinder", id="body")
        le.SubElement(cylinder, "centre-of-bottom-base",x="0.0",y=str(y0),z="0.0")
        le.SubElement(cylinder, "axis", x="0.0", y="1.0", z="0.0")
        le.SubElement(cylinder, "radius", val=str(radius))
        le.SubElement(cylinder, "height", val=str(height))
        hex_1 = le.SubElement(type_element, "hexahedron", id="hole1")
        le.SubElement(hex_1, "left-front-bottom-point",
                      x=str(x0_o),y=str(y0),z=str(-radius))
        le.SubElement(hex_1, "left-front-top-point",
                     x=str(x0_o),y=str(-y0),z=str(-radius))
        le.SubElement(hex_1, "left-back-bottom-point",
                      x=str(-x0_o),y=str(y0),z=str(-radius))
        le.SubElement(hex_1, "left-back-top-point",
                      x=str(-x0_o),y=str(-y0),z=str(-radius))
        le.SubElement(hex_1, "right-front-bottom-point",
                      x=str(x0_i),y=str(y0),z=str(0))
        le.SubElement(hex_1, "right-front-top-point",
                      x=str(x0_i),y=str(-y0),z=str(0))
        le.SubElement(hex_1, "right-back-bottom-point",
                      x=str(-x0_i),y=str(y0),z=str(0))
        le.SubElement(hex_1, "right-back-top-point",
                      x=str(-x0_i),y=str(-y0),z=str(0))
        hex_2 = le.SubElement(type_element, "hexahedron", id="hole2")
        le.SubElement(hex_2, "right-front-bottom-point",
                     x=str(x0_o),y=str(y0),z=str(radius))
        le.SubElement(hex_2, "right-front-top-point",
                      x=str(x0_o),y=str(-y0),z=str(radius))
        le.SubElement(hex_2, "right-back-bottom-point",
                      x=str(-x0_o),y=str(y0),z=str(radius))
        le.SubElement(hex_2, "right-back-top-point",
                      x=str(-x0_o),y=str(-y0),z=str(radius))
        le.SubElement(hex_2, "left-front-bottom-point",
                      x=str(x0_i),y=str(y0),z=str(0))
        le.SubElement(hex_2, "left-front-top-point",
                      x=str(x0_i),y=str(-y0),z=str(0))
        le.SubElement(hex_2, "left-back-bottom-point",
                      x=str(-x0_i),y=str(y0),z=str(0))
        le.SubElement(hex_2, "left-back-top-point",
                      x=str(-x0_i),y=str(-y0),z=str(0))              
        le.SubElement(type_element, "algebra", val="body (# (hole1 : hole2))")

    def addCorrelationChopper(self, name, center=(-0.28, 0.0),
                              radius=0.3, height=0.02,
                              sequence=[3,4,4,3,3,1,7,1,1,4],
                              is_type="chopper"):
        """
        For CORELLI only. Look at corelli_geometry.py for usage example.
        """
        import math
        type_element = le.SubElement(self.__root, "type",
                                     **{"name":name, "is":is_type})
        cylinder = le.SubElement(type_element, "cylinder", id="body")
        le.SubElement(cylinder, "centre-of-bottom-base",x=str(center[0]),
                      y=str(center[1]),z="0.0")
        le.SubElement(cylinder, "axis", x="0.0", y="0.0", z="1.0")
        le.SubElement(cylinder, "radius", val=str(radius*0.85))
        le.SubElement(cylinder, "height", val=str(height))
        sequence=map(float,sequence.split())
        n=len(sequence)
        s=sum(sequence)
        hole_list=""
        hexahedrons=[0]*n
        for i in range(n/2):
            hexahedrons[i] = le.SubElement(type_element, "hexahedron", id="hole"+str(i))
            hole_list+="hole"+str(i)+" : "
            angle_start=sum(sequence[:i*2])*math.pi*2./s
            angle_end=sum(sequence[:i*2+1])*math.pi*2./s
            xx1=math.sin(angle_start)*radius
            xx2=math.sin(angle_end)*radius
            yy1=math.cos(angle_start)*radius
            yy2=math.cos(angle_end)*radius
            le.SubElement(hexahedrons[i], "left-back-bottom-point",
                          x=str(xx1+center[0]),
                          y=str(yy1+center[1]),
                          z="0.0")
            le.SubElement(hexahedrons[i], "left-front-bottom-point",
                          x=str(xx1+center[0]),
                          y=str(yy1+center[1]),
                          z=str(height))
            le.SubElement(hexahedrons[i], "right-front-bottom-point",
                          x=str(xx2+center[0]),
                          y=str(yy2+center[1]),
                          z=str(height))
            le.SubElement(hexahedrons[i], "right-back-bottom-point",
                          x=str(xx2+center[0]),
                          y=str(yy2+center[1]),
                          z="0.0")
            le.SubElement(hexahedrons[i], "left-back-top-point",
                          x=str(xx1*0.8+center[0]),
                          y=str(yy1*0.8+center[1]),
                          z="0.0")
            le.SubElement(hexahedrons[i], "left-front-top-point",
                          x=str(xx1*0.8+center[0]),
                          y=str(yy1*0.8+center[1]),
                          z=str(height))
            le.SubElement(hexahedrons[i], "right-front-top-point",
                          x=str(xx2*0.8+center[0]),
                          y=str(yy2*0.8+center[1]),
                          z=str(height))
            le.SubElement(hexahedrons[i], "right-back-top-point",
                          x=str(xx2*0.8+center[0]),
                          y=str(yy2*0.8+center[1]),
                          z="0.0")
        le.SubElement(type_element, "algebra", val="body : "+hole_list[:-3])
