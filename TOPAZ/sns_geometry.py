#!/usr/bin/env python

# imports...
import xml.dom.minidom
from datetime import date

def extractValueByNumber(filename, bankNumber, columnNumber):
    datafile = open(filename, "r")
    i=0
    for line in datafile:
        if (i==bankNumber):
            elements = line.split()
            return elements[columnNumber]
        i=i+1    

def extractValueByName(filename, bankNumber, columnName):
    datafile = open(filename, "r")
    headers = datafile.readline().split()
    columnNumber=headers.index(columnName)
    return extractValueByNumber(filename, bankNumber, columnNumber)

def extractValueByNames(filename, bankName, columnName):
    datafile=open(filename, "r")
    i=0
    for line in datafile:
        elements=line.split()
        if (elements[0] == bankName):
            return extractValueByName(filename, i, columnName)
        i=i+1

def extractValueFromFile(filename, bankName=None, bankNumber=None, columnName=None, columnNumber=None):
    if (bankName is None) and (bankNumber is None):
        return "ERROR: You must specify which bank you want (either by name or number)"
    if (columnName is None) and (columnNumber is None):
        return "ERROR: You must specify which bank you want (either by name or number)"

    if (bankNumber is not None) and (columnNumber is not None):
        return extractValueByNumber(filename, bankNumber, columnNumber)
    
    if (bankNumber is not None) and (columnName is not None):
        #print "Calling extractValueByName"
        return extractValueByName(filename, bankNumber, columnName)
    
    if (bankName is not None) and (columnName is not None):
        #print "Looking for BankName=%s. ColumnName=%s" % (bankName, columnName)
        return extractValueByNames(filename, bankName, columnName)


class MathsEquation():
    """Utility class for equations"""
    def __init__(self, equation, comment):
        self._equation=equation
        self._comment=comment

class Variable():
    def __init__(self, param, var):
        self._param = param
        self._var = var
        
    def _getname(self):
        return self._param

    name = property(_getname, doc="Variable name (read only)")
            
    def __repr__(self):
        return "V-%s" % self._name

    def writeXML(self, document, parent):
        variable = document.createElement("variable")
        paramName = document.createElement("paramName")
        paramName.appendChild(document.createTextNode(self._param))
        variable.appendChild(paramName)
        varName = document.createElement("varName")
        varName.appendChild(document.createTextNode(self._var))
        variable.appendChild(varName)
        parent.appendChild(variable)

class Parameter():
    """Utility class for Parameters"""
    def __init__(self, name, value, type=None, units=None):
        self._name = name
        self._value = str(value)
        self._type = type
        self._units = units
        self._datatype = None

    def _getname(self):
        return self._name

    name = property(_getname, doc="Parameter name (read only)")
            
    def __repr__(self):
        return "P-%s" % self._name

    def writeXML(self, document, parent):
        parameter=document.createElement("parameter")
       
        if self._name is not None:
            parameter.setAttribute("name",self._name)
       
        if self._type is not None:
            parameter.setAttribute("type",self._type)
       
        if self._units is not None:
            parameter_units=document.createElement("units")
            parameter_units.appendChild(document.createTextNode(self._units))
            parameter.appendChild(parameter_units)
                
        # TODO: make this next line workout the datatype..
        if '.' in self._value:
            datatype = "floatvalue"
        else:
            datatype="intvalue"
            
        parameter_value=document.createElement(datatype)
        parameter_value.appendChild(document.createTextNode(self._value))
        parameter.appendChild(parameter_value)
        
        parent.appendChild(parameter)
    
class MathParameter():
    def __init__(self, name, type):
        self._name = name
        self._type = type
    
    def writeXML(self, document, parent):
        mathpar=document.createElement("parameter")
        mathpar.setAttribute("name", self._name)
        mathpar.setAttribute("type", self._type)
        parent.appendChild(mathpar) 
    
class Recipe():
    """Recipe class"""
    def __init__(self, name):
        self._name = name
        self._recipe = None
        self._helper = None
        self._parameters = []
        self._variables = []
        self._comment = None
    
    def setRecipe(self, recipe):
        """set a recipe"""
        self._recipe = recipe
        
    def setHelper(self, helper):
        """set a helper"""
        self._helper = helper
    
    def addParameter(self, parameter, value, type=None, units=None):
        self._parameters = self._parameters + [Parameter(parameter, value, type, units)]
        
    def addVariable(self, param, var):
        self._variables = self._variables + [Variable(param, var)]
    
    def setComment(self, comment):
        self._comment = comment

    def writeXML(self, document, parent):
        # put the comment above the element
        if not (self._comment == None):
            parent.appendChild(document.createComment(self._comment))
        
        recipe=document.createElement("recipe")
        parent.appendChild(recipe)
        
        name = document.createElement("name")
        name.appendChild(document.createTextNode(self._name))
        recipe.appendChild(name)
      
        #  Write the parameterList
        parameterList=document.createElement("parameterList")
        recipe.appendChild(parameterList)
        
        # Recipe
        if self._recipe is not None:
            recipe_member=document.createElement("recipe")
            recipe_member.appendChild(document.createTextNode(self._recipe))
            parameterList.appendChild(recipe_member)
        
        # Helper
        if self._helper is not None:
            helper=document.createElement("helper")
            helper.appendChild(document.createTextNode(self._helper))
            parameterList.appendChild(helper)
        
        #  Write the parameters
        for i in range(len(self._parameters)):
            self._parameters[i].writeXML(document, parameterList)
            
        #  Write the variables
        for i in range(len(self._variables)):
            self._variables[i].writeXML(document, parameterList)
      
        
class Maths():
    """Maths Geometry Class"""
    def __init__(self):
        self._inputs = []
        self._equations = []
        self._outputs = []
        self._definitions = []
    
    def addEquation(self, equation, comment=None):
        "Adds a new equation to the instrument geometry"
        self._equations = self._equations + [MathsEquation(equation,comment)]

    def addInput(self, name, type):
        self._inputs = self._inputs + [MathParameter(name, type)]
    
    def addOutput(self, name, type):
        self._outputs = self._outputs + [MathParameter(name, type)]
        
    def addDefinition(self, name, value=None, type=None, units=None):
        if value is None:
            self._definitions = self._definitions + [MathParameter(name,type)]
        else:
            self._definitions = self._definitions + [Parameter(name, value, type, units)]
        
    def writeXML(self, document, parent):
        # Add a comment
        parent.appendChild(document.createComment(" MATH "))
        
        maths=document.createElement("math")
        parent.appendChild(maths)

        # Definitions
        if (len(self._definitions) > 0):
            definitions = document.createElement("definitions")
            maths.appendChild(definitions)
            for i in range(len(self._definitions)):
                self._definitions[i].writeXML(document, definitions)

        # Inputs
        if (len(self._inputs) > 0):
            inputs = document.createElement("inputs")
            maths.appendChild(inputs)
            for i in range(len(self._inputs)):
                input=document.createElement("parameter")
                input.setAttribute("name", self._inputs[i]._name)
                input.setAttribute("type", self._inputs[i]._type)
                inputs.appendChild(input)
              
        # Equations
        if (len(self._equations) > 0):
            equations=document.createElement("equations")
            maths.appendChild(equations)
            for i in range(len(self._equations)):
                if not (self._equations[i]._comment == None):
                    equations.appendChild(document.createComment(self._equations[i]._comment))
                equation=document.createElement("equation")
                equation.appendChild(document.createTextNode(self._equations[i]._equation))
                equations.appendChild(equation)
        
        # Outputs
        if (len(self._outputs) > 0):
            outputs = document.createElement("outputs")
            maths.appendChild(outputs)
            for i in range(len(self._outputs)):
                output=document.createElement("parameter")
                output.setAttribute("name", self._outputs[i]._name)
                output.setAttribute("type", self._outputs[i]._type)
                outputs.appendChild(output)        

class Instrument():
    """NXinstrument class"""
    def __init__(self, name="instrument"):
        self._name = name
        self._components =[] 
        self._comment = None
        
    def getName(self):
        return self._name

    def addComponent(self, component):
        """Adds a new component to the instrument geometry"""
        self._components = self._components + [component] 

    def getComponent(self, name=None):
        """Return the requested component."""
        if name is None and len(self._components) == 1:
            return self._components[0]
        for component in self._components:
            if component.getName() == name:
                return component
        return None

    def setComment(self, comment):
        self._comment = comment

    def writeXML(self, document, parent):
        if self._comment is None:
            parent.appendChild(document.createComment(" INSTRUMENT "))
        else:
            parent.appendChild(document.createComment(self._comment))
        
        instrument=document.createElement("instrument")
        instrument.setAttribute("name", self._name)
        parent.appendChild(instrument)
        
        #  Components
        for i in range(len(self._components)):
            self._components[i].writeXML(document, instrument)

#### COMPONENTS ####      
class Component():
    """An instrument component"""
    def __init__(self, name, type, localname=None):
        self._name = name
        self._type = type
        self._helper = None # Can only have 1 helper per component
        self._parameters = []
        self._variables = []
        self._annotation = None
        self._comment = None
        self._recipe = None   # Can only have 1 recipe per component
        if localname is not None:
            self.setAnnotation("<local_name>%s</local_name>" % localname)

    def getName(self):
        return self._name
    
    def writeXML(self, document, element):
        if not (self._comment == None):
            element.appendChild(document.createComment(self._comment))

        component=document.createElement("component")
        component.setAttribute("type", self._type)
        component.setAttribute("name", self._name)
        element.appendChild(component)
        
        #  Write the annotation          
        if not (self._annotation == None):
            annotation=document.createElement("annotation")
            component.appendChild(annotation)
            annotation_cdata=document.createCDATASection(self._annotation)
            annotation.appendChild(annotation_cdata)
        
        if ((self._recipe is None) and (self._helper is None) and
           (len(self._parameters) == 0) and (len(self._variables) == 0)):
            return
        
        #  Write the parameterList
        parameterList=document.createElement("parameterList")
        component.appendChild(parameterList)
        
        # Recipe
        if self._recipe is not None:
            recipe=document.createElement("recipe")
            recipe.appendChild(document.createTextNode(self._recipe))
            parameterList.appendChild(recipe)
        
        # Helper
        if self._helper is not None:
            helper=document.createElement("helper")
            helper.appendChild(document.createTextNode(self._helper))
            parameterList.appendChild(helper)
        
        #  Write the parameters
        for i in range(len(self._parameters)):
            self._parameters[i].writeXML(document, parameterList)
            
        #  Write the variables
        for i in range(len(self._variables)):
            self._variables[i].writeXML(document, parameterList)

    def setRecipe(self, recipe):
        self._recipe = recipe
        
    def setHelper(self, helper):
        self._helper = helper
    
    def addParameter(self, parameter, value, type=None, units=None):
        newguy = Parameter(parameter, value, type, units)

        # see if there is already a parameter with this name
        index = -1
        for (i, item) in enumerate(self._parameters):
            if item.name == newguy.name:
                index = i
        if index >= 0:
            self._parameters[index] = newguy
            return

        # see if there is already a variable with this name
        index = -1
        for (i, item) in enumerate(self._variables):
            if item.name == newguy.name:
                index = i
        if index >= 0:
            del self._variables[index]

        self._parameters.append(newguy)
        
    def addVariable(self, param, var):
        newguy = Variable(param, var)

        # see if there is already a varialbe with this name
        index = -1
        for (i, item) in enumerate(self._variables):
            if item.name == newguy.name:
                index = i
        if index >= 0:
            self._variables[index] = newguy
            return

        # see if there is already a parameter with this name
        index = -1
        for (i, item) in enumerate(self._parameters):
            if item.name == newguy.name:
                index = i
        if index >= 0:
            del self._parameters[index]

        self._variables.append(newguy)
    
    def setComment(self, comment):
        self._comment = comment
        
    def setAnnotation(self, annotation):
        self._annotation = annotation

class Entry():
    """Instrument Entry Class"""
    def __init__(self, name):
        self._name=name
        if self._name is not None:
            self._name = str(self._name)
        self._monitors = []
        self._samples = []
        self._instruments = []
        self._maths = None
        self._recipes = None

    def getName(self):
        return self._name

    def addMonitor(self, monitor):
        """Adds a new monitor(component) to the current entry"""
        self._monitors = self._monitors + [monitor]

    def addSample(self, sample):
        """Adds a new sample (component) to the current entry"""
        self._samples = self._samples + [sample]

#    def addComponent(self, component):
#        """Adds a new component to the current entry"""
#        self._components = self._components + [component] 
        
    def addInstrument(self, instrument):
        """Adds a new instrument to the current entry"""
        self._instruments = self._instruments + [instrument]
    
    def getComponent(self, name):
        """Look throughout this entry for a component with the requested
        name. This goes through the monitors, sample, then instrument."""
        for monitor in self._monitors:
            if monitor.getName() == name:
                return monitor
        for sample in self._samples:
            if sample.getName() == name:
                return sample
        for instrument in self._instruments:
            component = instrument.getComponent(name)
            if component is not None:
                return component
        return None

    def getInstrument(self, name=None):
        """Return the requested instrument"""
        if name is None and len(self._instruments) == 1:
            return self._instruments[0]
        for instrument in self._instruments:
            if instrument.getName() == name:
                return instrument
        return None

    def writeXML(self, doc, parent):
        """generates the xml for the entry"""
        entry=doc.createElement("entry")
        entry.setAttribute("name", self._name)
        parent.appendChild(entry)
        
        # Monitors
        for i in range(len(self._monitors)):
            self._monitors[i].writeXML(doc,entry)
         
        # Samples
        for i in range(len(self._samples)):
            self._samples[i].writeXML(doc,entry) 
        
        # Instruments
        for i in range(len(self._instruments)):
            self._instruments[i].writeXML(doc, entry)
        

class Geometry():
    """Instrument Geometry Class"""
    def __init__(self, name=None):
        self._name = name
        if self._name is not None:
            self.name = str(self._name)
        self._entries = []
        self._equations = []
        self._recipies = []
        self._math = None
    
    def addEntry(self, entry):
        """Adds a entry into the instrument geometry"""
        self._entries = self._entries + [entry]
    
    def getEntry(self, name=None):
        """Return the requested entry"""
        if name is None and len(self._entries) == 1:
            return self._entries[0]
        for entry in self._entries:
            if entry.getName() == name:
                return entry
        return None

    def getInstrument(self, name=None):
        if len(self._entries) == 1:
            return self._entries[0].getInstrument(name)
        for entry in self._entries:
            instrument = entry.getInstrument(name)
            if instrument is not None:
                return instrument
        return None

    def addRecipe(self, recipe):
        """Adds a recipe into the instrument geometry"""
        self._recipies = self._recipies + [recipe]
    
    def addMath(self, math):
        """Adds a maths section to the instrument geometry"""
        self._math = math
    
    def generateXML(self):
        doc=xml.dom.minidom.Document()
        instrumentgeometry=doc.createElementNS("http://neutrons.ornl.gov/SNS/ASG/GeometryInput", "instrumentgeometry")
        doc.appendChild(instrumentgeometry)

        version=doc.createElement("version")        
        today = date.today()
        version.appendChild(doc.createTextNode("%04i-%02i-%02i" % (today.year,today.month,today.day)))
        instrumentgeometry.appendChild(version)

        # Generate the XML for all entry(s)
        for i in range(len(self._entries)):
            self._entries[i].writeXML(doc, instrumentgeometry)
    
        # Recipes 
        if (len(self._recipies) > 0):
            instrumentgeometry.appendChild(doc.createComment(" RECIPES "))
            recipes = doc.createElement("recipes")
            instrumentgeometry.appendChild(recipes)
            for i in range(len(self._recipies)):
                self._recipies[i].writeXML(doc, recipes)
            
        # Math Section
        if self._math is not None:
            self._math.writeXML(doc, instrumentgeometry)
                
        return doc
    
    def validateXML(self):
        """validates the xml against the geometry input schema"""
    
    def writeToScreen(self):
        """Prints the generated XML to the screen"""
        self.generateXML().toprettyxml()
        
    def writeToFile(self):
        """Writes the XML to a file with the prescriptive name"""
        today = date.today()
        filename = "%s_geom_%4i_%02i_%02i.xml" % (self._name,today.year,today.month,today.day)
        self.generateXML().toprettyxml()

def generateGeom(instrument):
    """Returns a geometry is an instrument containing a source and
    moderator."""
    from sns_inst_util import getInstrument
    instrumentEnum = getInstrument(instrument)

    # geometry
    geometry = Geometry(instrumentEnum)
    entry = Entry(instrumentEnum)
    geometry.addEntry(entry)

    # instrument
    instrumentObj = Instrument()
    entry.addInstrument(instrumentObj)
    
    # source
    source = Component(instrumentEnum.facility, "NXsource")
    source.setHelper("%sfacility" % instrumentEnum.facility)
    source.setComment(" SOURCE ")
    instrumentObj.addComponent(source)

    # moderator
    moderator = Component("moderator", "NXmoderator")
    moderator.setComment("MODERATOR")
    moderator.setHelper("%smoderator" % instrumentEnum.facility)
    if str(instrumentEnum.facility) == "SNS":
        moderator.addParameter("beamline", value=str(instrumentEnum.beamline))
    instrumentObj.addComponent(moderator)

    return geometry

class Vector:
    """Immutable object for a vector. All functions that do math
    return a new object with the correct information."""
    def __init__(self, x, y=0., z=0., w=1.0, **kwargs):
        verbose = kwargs.get("verbose", 0)
        if verbose:
            print "__init__(%s, %s, %s, %s, %s)" % (x, y, z, w, kwargs)
        try:
            self._x = x.x
            self._y = x.y
            self._z = x.z
            self._w = x.w
        except AttributeError:
            try:
                self._init_from_num(x[0], x[1], x[2], x[3])
            except IndexError:
                self._init_from_num(x[0], x[1], x[2], w)
            except TypeError:
                self._init_from_num(x, y, z, w)
            except ValueError:
                self._init_from_num(x, y, z, w)
        self._iter_index = 0
    def _init_from_num(self, x, y, z, w):
        self._x = float(x)
        self._y = float(y)
        self._z = float(z)
        self._w = float(w)

    def __repr__(self):
        prefix = "{%f, %f, %f" % (self.x, self.y, self.z)
        if self.w != 1.0:
            prefix += " | %f" % self.w
        return "%s}" % prefix

    def __eq__(self, other):
        myval = [self.x, self.y, self.z, self.w]
        try:
            otval = [other.x, other.y, other.z, other.w]
        except AttributeError:
            length = len(other)
            if length == 3 or length == 4:
                otval = [float(val) for val in other]
                if length == 3:
                    otval.append(1.)
            else:
                return False
        return myval == otval

    def _getX(self):
        return self._x
    x = property(_getX, doc="x-component of the vector")

    def _getY(self):
        return self._y
    y = property(_getY, doc="y-component of the vector")

    def _getZ(self):
        return self._z
    z = property(_getZ, doc="z-component of the vector")

    def _getW(self):
        return self._w
    w = property(_getW, doc="scale of the vector")

    def _getLength(self):
        import math
        number = self.x * self.x + self.y * self.y + self.z * self.z
        return math.sqrt(number)
    length = property(_getLength, doc="The length of the vector")

    def __add__(self, other):
        if self.w != 1. and other.w != 1.:
            raise Error("Cannot add with weights!=1 (found %s and %s)" % \
                        (self.w, other.w))
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        if self.w != 1. and other.w != 1.:
            raise Error("Cannot subtract with weights!=1 (found %s and %s)" % \
                        (self.w, other.w))
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __iter__(self):
        self._iter_index = 0
        return self

    def next(self):
        if self._iter_index == 0:
            result = self.x
        elif self._iter_index == 1:
            result = self.y
        elif self._iter_index == 2:
            result = self.z
        else:
            raise StopIteration
        self._iter_index += 1
        return result

    def normalize(self):
        """Return a vector that is a normalized version of this one."""
        length = self.length
        return Vector(self.x / length, self.y / length, self.z / length)

    def dot(self, other):
        """Return the dot product of this with the other vector"""
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        """Return a new vector that is the cross product of this vector with
        another"""
        x = self.y * other.z - self.z * other.y
        y = -1. * self.x * other.z + self.z * other.x
        z = self.x * other.y - self.y * other.x
        return Vector(x, y, z)

def getEulerCorners(one, two, three, four, **kwargs):
    u = Vector(four - one)
    v = Vector(two - one)
    return getEuler(u, v, **kwargs)

def getNormal(one, two, three, four, **kwargs):
    """Find normal to plan given 4 corner points. This returns (nx, ny, nz)
    The original code was provided by Jason Hodges"""
    import math

    # constants to understand indices
    (X, Y, Z) = (0, 1, 2)
    
    # calculate components of normal vector
    x = (two[Y]-one[Y])*(((three[Z]+four[Z])/2)-one[Z]) \
        - (((two[Y]+four[Y])/2)-one[Y])*(two[Z]-one[Z])
    y = (two[X]-one[X])*(((three[Z]+four[Z])/2)-one[Z]) \
        - (((three[X]+four[X])/2)-one[X])*(two[Z]-one[Z])
    z = (two[X]-one[X])*(((three[Y]+four[Y])/2)-one[Y]) \
        - (((three[X]+four[X])/2)-one[X])*(two[Y]-one[Y])
    magnitude = math.sqrt(x*x + y*y + z*z)

    # normalize it
    x = x/magnitude
    y = y/magnitude
    z = z/magnitude

    # verify the result is orthonormal
    if math.sqrt(x*x + y*y + z*z) != 1.0:
        raise Error("Final vector is not normal")

    return (x, y, z)

def getCenter(one, two, three, four, **kwargs):
    answer = [sum(item)/4. for item in zip(one, two, three, four)]
    return Vector(answer)

def getEuler(uVec, vVec, **kwargs):
    """This is taken from the Goiniometer.getEulerAngles() function that is
    in the package gov.ornl.sns.translation.geometry.calc.jython"""

    degrees = kwargs.get("degrees", False)
    verbose = kwargs.get("verbose", 0)

    # normalize the u-vector
    uVec = uVec.normalize()
    # determine the perpendicular
    nVec = uVec.cross(vVec)
    nVec = nVec.normalize()
    # make sure that u,v are perpendicular
    vVec = nVec.cross(uVec)
    vVec = vVec.normalize()

    if verbose:
        print "orthonormal:", uVec, vVec, nVec

    # calculate the angles
    import math

    if vVec.y == 1.: # chi rotation is 0, just rotate about z-axis
        if verbose > 1:
            print "chi rotation is 0"
        phi = math.atan2(nVec.x, nVec.z)
        chi = 0.
        omega = 0.
    elif vVec.y == -1.:# chi rotation is 180 degrees
        if verbose > 1:
            print "chi rotation is 180 degrees"
        phi = -1. * math.atan2(nVec.x, nVec.z)
        if phi == -1.* math.pi:
            phi = math.pi
        chi = math.pi
        omega = 0.
    else:
        if verbose > 1:
            print "using generic version"
        phi = math.atan2(nVec.y, uVec.y)
        chi = math.acos(vVec.y)
        omega = math.atan2(vVec.z, -1. * vVec.x)

    # put together the result
    result = [phi, chi, omega]
    if degrees:
        result = [val*180./math.pi for val in result]
    for (i, val) in enumerate(result):
        if abs(val) == 0.:
            result[i] = 0.
    return tuple(result)

############################## TEST SUITE
def printTestResult(found, expected):
    print found == expected,
    if found != expected:
        print "found", found,
    print

def testVector():
    vecx = Vector(1,0,0)
    vecy = Vector(0,1,0)
    cross = vecx.cross(vecy)
    print "(1,0,0) cross (0,1,0) == (0,0,1)",cross == (0,0,1)
    dot = vecx.dot(vecy)
    print "(1,0,0) dot (0,1,0) == 0", dot == 0.
    vec = Vector(3,3,3)
    print "(3,3,3).normalize().length == 1", vec.normalize().length == 1.

def testGetOrientation(u, v, expected):
    result = getEuler(Vector(u), Vector(v), degrees=True)
    print "getEuler(%s, %s) == %s" % (u, v, expected),
    printTestResult(result, expected)

def testGetNormal(one, two, three, four, expected):
    result = getNormal(one, two, three, four)
    print "getNormal(%s, %s, %s,%s) == %s" % (one, two, three, four, expected),
    printTestResult(result, expected)

def testGetCenter(one, two, three, four, expected):
    result = getCenter(one, two, three, four)
    print "getCenter(%s, %s, %s, %s) == %s" % (one, two, three, four, expected),
    printTestResult(result, expected)

def testOrientation():
    print "identity"
    testGetOrientation((1,0,0),  (0,1,0),           (0,0,0))
    print "just phi"
    testGetOrientation((0,0,-1), (0,1,0),     (90., 0., 0.))
    testGetOrientation((-1,0,0), (0,1,0),    (180., 0., 0.))
    print "chi=180"
    testGetOrientation((-1,0,0), (0,-1,0),    (0, 180., 0.))
    testGetOrientation((0,0,-1), (0,-1,0),  (90., 180., 0.))
    testGetOrientation((1,0,0),  (0,-1,0), (180., 180., 0.))
    print "others"
    testGetOrientation((0,1,0),  (-1,0,0),    (0., 90., 0.))
    testGetOrientation((0,0,-1), (-1,0,0),   (90., 90., 0.))
    testGetOrientation((-1,0,0),  (0,0,1),  (90., 90., 90.))

def testNormal():
    testGetNormal((1,0,0), (1,1,0), (-1,1,0), (-1,0,0), (0,0,1))
    testGetNormal((-1,0,0), (-1,1,0), (1,1,0), (1,0,0), (0,0,-1))

def testCenter():
    testGetCenter((-1,-1,0), (-1,1,0), (1,1,0), (1,-1,0), (0,0,0))

if __name__ == "__main__":
    print "******************** Testing Vector ********************"
    testVector()
    print "**************** Testing getOrientation ****************"
    testOrientation()
    print "******************* Testing getNormal ******************"
    testNormal()
    print "******************* Testing getCenter ******************"
    testCenter()
