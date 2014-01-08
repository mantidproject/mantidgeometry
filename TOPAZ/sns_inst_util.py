#!/usr/bin/env python

from finders_version import version as __version__

XML_FILE = "./instrumentlist.xml"
INSTRUMENTS = []

def getNodeValue(node):
    for child in node.childNodes:
        if child.nodeValue is not None:
            return str(child.nodeValue)
    raise Exception("Failed to find value of node \"%s\"" % node.nodeName)

########## DEFINE THE INSTRUMENT CLASS
class Instrument:
    """This is a complex object for holding information about an instrument"""
    def __init__(self, facilityName, instrumentNode, **kwargs):
        # initialize things with default information
        self.facility = facilityName
        self.shortname = None
        self.longname = None
        self.beamline = None
        self.computers = []
        for child in instrumentNode.childNodes:
            name = child.nodeName
            if name == "shortname":
                self.shortname = getNodeValue(child)
            elif name == "longname":
                self.longname = getNodeValue(child)
            elif name == "beamline":
                self.beamline = getNodeValue(child)
            elif name == "computer":
                self.computers.append(getNodeValue(child))
    def __repr__(self):
        return self.shortname
    def validHost(self, name):
        for computer in self.computers:
            if computer.startswith(name):
                return True
        return False

########## DYNAMICALLY LOAD THE ENUMERATIONS
def __init__():
    from xml.dom.minidom import parse
    try:
        dom = parse(XML_FILE)
    except IOError, e:
        print "IOError: Failed to read configuration file:", e
        import sys
        sys.exit(-1)
    facilitiesNode = None
    for child in dom.childNodes:
        if child.nodeName == "facilities":
            facilitiesNode = child

    def processFacility(facilityNode):
        name = None
        # get the facility name
        for child in facilityNode.childNodes:
            if child.nodeName == "name":
                name = getNodeValue(child)

        # process the instruments
        for child in facilityNode.childNodes:
            if child.nodeName == "instrument":
                INSTRUMENTS.append(Instrument(name, child))

    for child in facilitiesNode.childNodes:
        if child.nodeName == "facility":
            processFacility(child)
__init__()

########## HERE IS THE LIBRARY
def getMachine():
    """Determine the name of the machine this process is running on."""
    from socket import gethostname
    return gethostname()

def getInstrument(inst=None, options=None):
    """Determine the default instrument name."""
    try:
        inst.shortname
        return inst
    except AttributeError:
        pass
    if inst is not None and len(inst) > 0:
        name = inst.upper()
        for instrument in INSTRUMENTS:
            if instrument.shortname == name:
                return instrument
    host = getMachine()
    # check each instrument
    for instrument in INSTRUMENTS:
        if instrument.validHost(host):
            return instrument
    return None

def getFacility(inst):
    """Determine the facility an instrument is at."""
    try:
        return inst.facility
    except:
        myInst = getInstrument(inst)
        if myInst is not None and len(str(myInst)) > 0:
            return myInst.facility
    raise KeyError("Could not find instrument \"%s\" in enumerations" % inst)

def getUserPath(info, user = None):
    import os
    if user is None:
        user = os.getenv("USER")
    path = os.path.join("/SNSlocal/users/", user)
    try:
        path = os.path.join(path, str(info.instrument))
        if info.proposal is not None:
            path = os.path.join(path, info.proposal)
    except AttributeError:
        path = os.path.join(path, str(info))

    return path

def getNeXusPaths(info, withUser = False):
    paths = []
    if withUser:
        paths.append(getUserPath(info.instrument))
    import os
    paths.append(os.path.join("/SNSlocal", str(info.instrument)))
    if not info.facility == "SNS":
        paths.append(os.path.join("/", "%slocal" % info.facility,
                                  str(info.instrument)))
    paths.append(os.path.join("/", info.facility, str(info.instrument)))
    if info.proposal is not None:
        paths = [os.path.join(item, info.proposal) for item in paths]
        if info.collection is not None:
            paths = [os.path.join(item, info.collection) for item in paths]
    return paths

def getSharedPaths(info):
    result=[]
    import os
    bases = [os.path.join("/", "SNSlocal", str(info.instrument)),
             os.path.join("/", info.facility, str(info.instrument))]
    if not info.facility == "SNS":
        bases.append(os.path.join("/%slocal" % info.facility,
                                  str(info.instrument)))

    if info.proposal is not None:
        for base in bases:
            if os.path.exists(base):
                result.append(os.path.join(base, info.proposal, "shared"))
    else:
        import dircache
        for base in bases:
            if os.path.exists(base):
                paths = dircache.listdir(base)
                for path in paths:
                    if path.endswith("shared"):
                        path = os.path.join(base, path)
                    else:
                        path = os.path.join(base, path, "shared")
                    if os.path.exists(path):
                        result.append(path)
    return result
    

def getDasRoot(inst, proposal=None):
    result = "/%s-DAS-FS" % inst
    if proposal is not None:
        import os
        result = os.path.join(result, proposal)
    return result

def splitArgs(optArgs, sysArgs, options=None):
    try:
        index = sysArgs.index("--")
        comArgs = sysArgs[index+1:]
    except ValueError:
        index = -1
        comArgs = []
        runArgs = optArgs

    if index > 0:
        runArgs = optArgs[:-1*len(comArgs)]
        temp = " "
        comArgs = temp.join(comArgs)
    else:
        comArgs = ""
    runs = generateList(runArgs, options)
    if options is not None:
        if options.verbose is True or int(options.verbose) > 0:
            print "RUNS:", runs
            print "COM :", comArgs
    return (runs,comArgs)

def getConcurrentIndices(runs, startIndex=0):
    """Compress a collection of consecutive integers into a single string
    with a dash in the middle"""
    start = startIndex
    stop = start
    for i in range(startIndex,len(runs)-1):
        if runs[i]+1 == runs[i+1]:
            stop = i+1
        else:
            return (start, stop)
    return (start,stop)

def condenseList(runs):
    """Turn a list of integers into a condensed string version of the list"""
    result = []
    (start, stop) = (0,0)
    length = len(runs)
    while stop < length:
        (start, stop) = getConcurrentIndices(runs, start)
        if stop >= length:
            break
        if start < stop:
            result.append("%s-%s" % (runs[start], runs[stop]))
        else:
            result.append(runs[start])
        start = stop+1

    # convert the remaining runs into strings
    result = map(lambda x: str(x), result)

    return ",".join(result)

def generateList(args, options=None):
    """Convert a string list into a list of integers
    
    args = single string or list of strings in the form
        '\d+(-\d+)?(,\d+(-\d+)?)*'
        For example: '12-15,30-33'
    options = If options.verbose exists and is True, then this function
              will send a warning message to stdout when it cannot
              understand a portion of args.

    Returns a list of all the integers indicated by args.  The example
    above would return the list [12, 13, 14, 15, 30, 31, 32, 33].
    Returned integers will be sorted least to greatest with no
    duplicates.
    """
    optargs = getattr(options, 'run', None)
    if args == None:
        args = []
    if optargs is not None:
        args.append(optargs)
    if len(args) <= 0:
        raise RuntimeError("Cannot generate list from empty")
    verbose = getattr(options, 'verbose', False);
    # normalize args to always be a list
    if (not isinstance(args, list)):
        args = [args]
    # args should be a list of strings like this:
    # ['1-5,10', '12,15-21'].
    # force all elements to be strings and split on commas
    args = [str(a).split(',') for a in args]
    # args should now be a list of lists like this:
    # [['1-5', '10'], ['12', '15-21']]
    # flatten the list back out again
    from operator import add # function equivalent of +
    args = reduce(add, args)
    # args should now be a list of strings again like this:
    # ['1-5', '10', '12', '15-21']
    # use a set instead of a list so overlapping ranges won't create
    # duplicate integers in the output
    result = set()
    for a in args:
        # watch for badly formatted input ranges
        # Mainly I expect the int() cast below to fail for bad input.
        try:
            ends = [int(x) for x in a.split('-')]
            if (len(ends) > 2):
                raise ValueError, "too many dashes"
            # reverse any backwards ranges
            ends.sort();
            result |= set(xrange(ends[0], ends[-1] + 1))
        except:
            if verbose:
                print "WARN: Skipping range \"%s\"" % a
    return sorted(result)

########## MAIN FUNCTION FOR TESTING
if __name__ == "__main__":
    print XML_FILE
    print "getMachine():", getMachine()
    print "getInstrument():", getInstrument()
    ref_m = getInstrument("ref_m")
    print "getInstrument(ref_m):", ref_m
    print "getFacility(Instrument):", getFacility(ref_m)
    print "getFacility('ref_m'):", getFacility("ref_m")
    print "condenseList([1,2,3,7])", condenseList([1,2,3,7])
    print "generateList('1-3,8')", generateList("1-3,8")
