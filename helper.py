from lxml import etree as le
from string import split,join
class MantidGeom:

    def __init__(self, instname, comment=None):
        from datetime import datetime
        the_future = datetime(2100, 1, 31, 23, 59, 59)
        self.__root = le.Element("instrument", **{"name": instname,
                                 "valid-from": str(datetime.now()),
                                 "valid-to": str(the_future)})
        if comment is not None:
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
        print le.tostring(self.__root, pretty_print=True,
                             xml_declaration=True)

    def addSnsDefaults(self, indirect=False):
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
        le.SubElement(reference_element, "handedness", axis="right")


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
                    


    def addDetectorPixelsIdList(self, name, r=[], names=[]):

        component = le.SubElement(self.__root, "idlist",
                                  idname=name)
        for i in range(len(r)):
            for j in range(len(r[i])):
                if (str(r[i][j]) != "nan"):
                    le.SubElement(component, "id", val=str(names[i][j]))


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
                                      **{"type":"monitor",
                                         "mark-as":"monitor"})
        
        for i in range(len(distance)):
            #check if float
            try:
                zi=float(distance[i])
                location = le.SubElement(basecomponent, "location", z=distance[i],name=names[i])
                le.SubElement(location, "neutronic", z=distance[i])
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
        comp = None
        if idlist is not None:
            comp = le.SubElement(root, "component", type=type_name,
                                 idlist=idlist)
        else:
            comp = le.SubElement(root, "component", type=type_name)
        l=comp
        if blank_location:
          l=le.SubElement(comp, "location")
        return l        

    def makeTypeElement(self, name):
        """
        Return a simple type element.
        """
        return le.SubElement(self.__root, "type", name=name)
            
    def makeDetectorElement(self, name, idlist_type=None, root=None):
        """
        Return a component element.
        """
        if root is not None:
            root_element = root
        else:
            root_element = self.__root

        if idlist_type is not None:
            return le.SubElement(root_element, "component", type=name,
                                 idlist=idlist_type)
        else:
            return le.SubElement(root_element, "component", type=name)

    def makeIdListElement(self, name):
        return le.SubElement(self.__root, "idlist", idname=name)

    def addDetector(self, x, y, z, rot_x, rot_y, rot_z, name, comp_type, usepolar=None, facingSample=False):
        """
        Add a detector in a type element for the XML definition.
        """
        type_element = le.SubElement(self.__root, "type", name=name)
        comp_element = le.SubElement(type_element, "component", type=comp_type)
        
        if usepolar is not None:
            self.addLocationPolar(comp_element, x, y, z, facingSample=facingSample)
        else:
           self.addLocation(comp_element, x, y, z, rot_x, rot_y, rot_z, facingSample=facingSample)

    def addSingleDetector(self, root, x, y, z, rot_x, rot_y, rot_z, name=None,
                          id=None, usepolar=None):
        """
        Add a single detector by explicit declaration. The rotation order is
        performed as follows: y, x, z.
        """
        if name is None:
            name = "bank"

        if usepolar is not None:
            self.addLocationPolar(root, x, y, z, name)
        else:
            self.addLocation(root, x, y, z, rot_x, rot_y, rot_z, name)

    def addLocation(self, root, x, y, z, rot_x, rot_y, rot_z, name=None, facingSample=False):
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
            le.SubElement(r2, "rot", **{"val":str(rot_z), "axis-x":"0",
                                        "axis-y":"0", "axis-z":"1"})

        if facingSample:
            le.SubElement(pos_loc, "facing", x="0.0", y="0.0", z="0.0")

    def addLocationPolar(self, root, r, theta, phi, name=None):
        if name is not None:
            pos_loc = le.SubElement(root, "location", r=r, t=theta, p=phi, name=name)
        else:
            pos_loc = le.SubElement(root, "location", r=r, t=theta, p=phi)

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
            except:  
              processed=split(str(r))
              if len(processed)==1:
                le.SubElement(log, "logfile", **{"id":r})
              else:
                equation=join(processed[1:]).replace(processed[0],"value")
                le.SubElement(log, "logfile", **{"id":processed[0],"eq":equation})  
            log=le.SubElement(pos_loc,"parameter",**{"name":"t-position"})
            try:
              tf=float(t)               
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
              pf=float(p)               
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
              rotxf=float(rot_x)               
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
              rotyf=float(rot_y)               
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
              rotzf=float(rot_z)               
              le.SubElement(log, "value", **{"val":rot_z})    
            except:  
              processed=split(str(rot_z))
              if len(processed)==1:
                le.SubElement(log, "logfile", **{"id":rot_z})
              else:
                equation=join(processed[1:]).replace(processed[0],"value")
                le.SubElement(log, "logfile", **{"id":processed[0],"eq":equation})  

    def addNPack(self, name, num_tubes, tube_width, air_gap, type_name="tube"):
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

    def addPixelatedTube(self, name, num_pixels, tube_height,
                         type_name="pixel"):
        """
        Add a tube of N pixels. If there are going to be more than one pixel
        type specified later, an optional type name can be given. The default
        pixel type name will be pixel.
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
            le.SubElement(component, "location", name=pixel_name, y=str(y))

    def addCylinderPixel(self, name, center_bottom_base, axis, pixel_radius,
                         pixel_height, is_type="detector"):
        """
        Add a cylindrical pixel. The center_bottom_base is a 3-tuple of radius,
        theta, phi. The axis is a 3-tuple of x, y, z.
        """
        type_element = le.SubElement(self.__root, "type",
                                     **{"name":name, "is":is_type})
        cylinder = le.SubElement(type_element, "cylinder", id="cyl-approx")
        le.SubElement(cylinder, "centre-of-bottom-base",
                      r=str(center_bottom_base[0]),
                      t=str(center_bottom_base[1]),
                      p=str(center_bottom_base[2]))
        le.SubElement(cylinder, "axis", x=str(axis[0]), y=str(axis[1]),
                      z=str(axis[2]))
        le.SubElement(cylinder, "radius", val=str(pixel_radius))
        le.SubElement(cylinder, "height", val=str(pixel_height))
        le.SubElement(type_element, "algebra", val="cyl-approx")

    def addCuboidPixel(self, name, lfb_pt, lft_pt, lbb_pt, rfb_pt,
                      is_type="detector"):
        """
        Add a cuboid pixel. The origin of the cuboid is assumed to be the
        center of the front face of the cuboid. The parameters lfb_pt, lft_pt,
        lbb_pt, rfb_pt are 3-tuple of x, y, z.
        """
        type_element = le.SubElement(self.__root, "type",
                                     **{"name":name, "is":is_type})
        cuboid = le.SubElement(type_element, "cuboid", id="shape")
        le.SubElement(cuboid, "left-front-bottom-point", x=str(lfb_pt[0]),
                      y=str(lfb_pt[1]), z=str(lfb_pt[2]))
        le.SubElement(cuboid, "left-front-top-point", x=str(lft_pt[0]),
                      y=str(lft_pt[1]), z=str(lft_pt[2]))
        le.SubElement(cuboid, "left-back-bottom-point", x=str(lbb_pt[0]),
                      y=str(lbb_pt[1]), z=str(lbb_pt[2]))
        le.SubElement(cuboid, "right-front-bottom-point", x=str(rfb_pt[0]),
                      y=str(rfb_pt[1]), z=str(rfb_pt[2]))
        le.SubElement(type_element, "algebra", val="shape")

    def addDummyMonitor(self, radius, height):
        """
        Add a dummy monitor with some-shape.
        """
        type_element = le.SubElement(self.__root, "type", **{"name":"monitor",
                                                             "is":"detector"})
        cylinder = le.SubElement(type_element, "cylinder", id="cyl-approx")
        le.SubElement(cylinder, "centre-of-bottom-base", x="0.0", y="0.0",
                      z="0.0")
        le.SubElement(cylinder, "axis", x="0.0", y="0.0", z="1.0")
        le.SubElement(cylinder, "radius", radius=str(radius))
        le.SubElement(cylinder, "height", height=str(height))
        
        le.SubElement(type_element, "algebra", val="cyl-approx")
    
    def addCuboidMonitor(self,width,height,depth):
        """
        Add a cuboid monitor
        """
        type_element = le.SubElement(self.__root, "type", **{"name":"monitor",
                                                             "is":"detector"})
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
            le.SubElement(idElt, "id", val=ids[i])

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
