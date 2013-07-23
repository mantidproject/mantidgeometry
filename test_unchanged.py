#!/usr/bin/env python

import difflib
import logging
import os
import subprocess
import sys

__version__ = "0.1.0"
LOGLEVELS = ["DEBUG", "INFO", "WARNING"]

def findGeoms(direc):
    logging.info("Searching for files in " + direc)
    choices = os.listdir(direc)
    logging.debug("choices: " + str(choices))
    filenames = []
    for choice in choices:
        filename = os.path.join(direc, choice)
        if os.path.isdir(filename):
            continue
        if filename.endswith("_geometry.py"):
            filenames.append(filename)
    logging.debug("filenames: " + str(filenames))
    return filenames

def toOutputNames(filename):
    (direc, filename) = os.path.split(filename)

    instr = filename.split("_")[0]
    instr = instr.upper()

    golden = "%s_Definition_master.xml" % instr
    result = "%s_Definition.xml" % instr

    golden = os.path.join(direc, golden)
    result = os.path.join(direc, result)

    return (golden, result)
    

def findSourceDirec():
    direc = sys.argv[0]
    logging.debug("findSourceDirec 0:" + direc)
    direc = os.path.split(direc)[0]
    logging.debug("findSourceDirec 1:" + direc)
    direc = os.path.abspath(direc)
    logging.debug("findSourceDirec 2:" + direc)
    return direc

def runGeom(pyscript, outfile, goldenfile, generateGolden):
    logging.info("*****"+pyscript+"*****")
    if os.path.exists(outfile):
        logging.debug("Removing output file '%s'" % outfile)
        os.unlink(outfile)
    if generateGolden and os.path.exists(goldenfile):
        logging.debug("Removing golden file '%s'" % goldenfile)
        os.unlink(goldenfile)
    cmd = "python %s" % pyscript
    proc = subprocess.Popen(cmd, shell=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out, err) = proc.communicate() # waits for process to finish
    retcode = proc.wait()
    logging.debug("----output----")
    logging.debug(out)
    logging.debug("----error-----")
    logging.debug(err)

    if retcode:
        raise RuntimeError("'%s' returned %d" % (cmd, retcode))

    finalfile = outfile
    if generateGolden:
        logging.info("Renaming '%s' to '%s'" % (outfile, goldenfile))
        os.rename(outfile, goldenfile)
        finalfile=goldenfile

    print "Created '%s'" % finalfile

def getModified(instrTag):
    LAST_MOD='last-modified="'

    if not LAST_MOD in instrTag:
        raise RuntimeError("Failed to find '%s' in '%s'" % (LAST_MOD, instrTag))

    start = instrTag.index(LAST_MOD) + len(LAST_MOD)
    end = instrTag.index('"', start)
    return LAST_MOD+instrTag[start:end+1]

def compareGeom(golden, outfile, headerDecoration):
    if not os.path.exists(golden):
        raise RuntimeError("Failed to find the orignal geometry '%s'" % golden)
    if not os.path.exists(outfile):
        raise RuntimeError("Failed to find the new geometry '%s'" % outfile)

    oldData = open(golden, 'r').readlines()
    newData = open(outfile, 'r').readlines()

    # do the "quick" check to see if anything has been changed
    diff = difflib.unified_diff(oldData, newData, golden, outfile, n=0)
    leftDiff = 0
    rightDiff = 0
    oldModified=None
    newModified=None
    for line in diff:
        if line.startswith('-') or line.startswith('+'):
            if not (line.startswith('---') or line.startswith('+++')):
                if "<instrument " in line:
                    modified = getModified(line)
                    newline = line.replace(modified, "")
                    if line.startswith('-'):
                        oldModified = (modified, newline[1:])
                    else:
                        newModified = (modified, newline[1:])
                        if oldModified[1] != newModified[1]:
                            leftDiff += 1
                            rightDiff += 1
                else:
                    if line.startswith('-'):
                        leftDiff += 1
                    if line.startswith('+'):
                        rightDiff += 1

    # log the modified dates according to the file
    logging.info(golden+" "+oldModified[0])
    logging.info(outfile+" "+newModified[0])

    # only print diff if there is a meaningful one
    if (leftDiff+rightDiff) > 0:
        if headerDecoration:
            print "========================================"
        print "%d lines removed and %d lines added" % (leftDiff, rightDiff)
        # rerun and write out
        diff = difflib.unified_diff(oldData, newData, golden, outfile)
        sys.stdout.writelines(diff)
    else:
        print "%s and %s match" % (os.path.split(golden)[1], \
                                   os.path.split(outfile)[1])


if __name__ == "__main__":
    # set up optparse
    import optparse # deprecated since v2.7 and should switch to argparse
    parser = optparse.OptionParser(description="Verify that definition files haven't changed",
                                   usage="%prog [options]")
    parser.add_option("-l", "--loglevel", dest="loglevel", default="WARNING",
                    help="Specify the log level (" + ", ".join(LOGLEVELS)+ ")")
    parser.add_option("-v", "--version", dest="version", action="store_true",
                      help="Print the version information and exit")
    parser.add_option("", "--setup", dest="setup", action="store_true",
                      help="Run all of the geometries from the unchanged repository")
    parser.add_option("", "--diffonly", dest="diffonly", action="store_true",
                      help="Don't run the geometries, only calculate the differences")
    parser.add_option("", "--script", dest="script",
                      help="Script file to run")

    # parse the command line
    (options, args) = parser.parse_args()

    # setup logging
    options.loglevel = options.loglevel.upper()
    options.loglevel = getattr(logging, options.loglevel.upper(),
                               logging.WARNING)
    logging.basicConfig(format='%(levelname)s:%(message)s',
                        level=options.loglevel)

    # log the options and arguments
    logging.debug('opts ' + str(options))
    logging.debug('args ' + str(args))

    # if they want the version just give it back and exit
    if options.version:
        print sys.argv[0], "version", __version__
        sys.exit(0)

    # where is the actual test script
    direc = findSourceDirec()

    # determine what geometries are available
    if options.script is None:
        filenames = findGeoms(direc)
    else:
        if not os.path.isabs(options.script):
            options.script = os.path.join(direc, options.script)
            options.script = os.path.abspath(options.script)
        filenames = [options.script]

    # generate the expected geometry file names
    outfiles = {}
    for filename in filenames:
        outfiles[filename] = toOutputNames(filename)

    # run each one
    if not options.diffonly:
        for key in outfiles.keys():
            runGeom(key, outfiles[key][1], outfiles[key][0], options.setup)

    for key in outfiles.keys():
        (golden, output) = outfiles[key]
        compareGeom(golden, output, len(filenames)>1)
#    key = outfiles.keys()[1]
#    (golden, output) = outfiles[key]
#    compareGeom(golden, output)
