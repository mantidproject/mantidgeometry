#!/usr/bin/env python

import difflib
import logging
import os
import subprocess
import sys

__version__ = "0.1.1"
LOGLEVELS = ["INFO", "WARNING", "DEBUG"]
# mapping of instrument names here into what is in mantid
INSTR_MAP = {"PG3": "POWGEN"}

__original_idf = '_Definition_master.xml'
__idf = '_Definition.xml'

__key_last_modified = 'last-modified='
__key_valid_to = 'valid-to'


def findGeoms():
    logging.debug('Found following IDF generator Python files: ')
    names = []
    for root, dirs, files in os.walk('./'):
        files = [f for f in files if f.endswith('_geometry.py') or f.endswith('_generateIDF.py')]
        for name in files:
            name = os.path.join(root, name)
            names.append(name)
            logging.debug(name)
    return names


def toOutputNames(filename):
    direc, filename = os.path.split(filename)

    instr = filename.split("_")[0]
    instr = instr.upper()

    golden = os.path.join(direc, instr + __original_idf)
    result = os.path.join(direc, instr + __idf)

    # fix up the instrument name to match what is in mantid
    if instr in INSTR_MAP.keys():
        instr = INSTR_MAP[instr]

    return golden, result, instr


def findMantidInstrFile(mantiddir, instr):
    # get all files in the directory
    all_files = os.listdir(mantiddir)
    if len(all_files) <= 0:
        raise RuntimeError("Failed to find any files in " + mantiddir)

    # reduce to just the ones that are IDFs for this instrument
    candidates = []
    for filename in all_files:
        if filename.startswith(instr) and filename.endswith(".xml") and \
                "Definition" in filename:
            candidates.append(os.path.join(mantiddir, filename))

    # pop them open and look for the valid-to information
    datemap={}
    for filename in candidates:
        handle = open(filename)
        for line in handle:
            if __key_valid_to in line:
                break
            if not __key_valid_to in line:
                raise RuntimeError("Failed to find 'valid-to' tag in " + filename)
            line = line[line.index(__key_valid_to)+len(__key_valid_to):].strip()
            line = line[line.index('=') + 1:].strip()
            line = line[1:].strip()
            line = line.split()[0]
            datemap[line] = filename

    # return the one that has the latest valid-to date
    dates = datemap.keys()
    dates.sort()
    return datemap[dates[-1]]


def copyFromMantid(mantiddir, instr, goldenfile):
    mantidfile = findMantidInstrFile(mantiddir, instr)
    shutil.copy(mantidfile, goldenfile)


def runGeom(pyscript, goldenfile, outfile, generateGolden):
    logging.info("*****"+pyscript+"*****")
    cmd = "python %s" % pyscript
    try:
        proc = subprocess.Popen(cmd, shell=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        retcode = proc.wait()
        if retcode:
            if len(out) > 0:
                logging.warning("----output----")
                logging.warning(out)
            if len(err) > 0:
                logging.warning("----error-----")
                logging.warning(err)
            if retcode == 2:
                logging.info(' Skip creating ' + outfile)
                return
            else:
                logging.error(cmd + " returned " + str(retcode))
        else:
            if len(out) > 0:
                logging.debug("----output----")
                logging.debug(out)
            if len(err) > 0:
                logging.debug("----error-----")
                logging.debug(err)
    except ValueError:
        logging.error(" Cannot run " + pyscript)

    if generateGolden:
        if os.path.exists(goldenfile):
            logging.debug(" Removing golden file " + goldenfile)
            os.remove(goldenfile)
        if os.path.exists(outfile):
            os.rename(outfile, goldenfile)
            logging.info(" Created " + goldenfile)


def getModified(instrTag):
    if __key_last_modified in instrTag:
        start = instrTag.index(__key_last_modified) + len(__key_last_modified)
        end = instrTag.index('"', start + 1)
        modified = __key_last_modified+instrTag[start:end+1]
        newline = instrTag.replace(modified, "")
    else:
        raise RuntimeError("Failed to find " + __key_last_modified + " in " + instrTag)
    return modified, newline[1:]


def compareGeom(golden, outfile):
    if not os.path.exists(golden):
        logging.warning(" Failed to find the original geometry " + golden + " - not comparing")
        return
    if not os.path.exists(outfile):
        logging.warning(" Failed to find the new geometry " + outfile)
        return

    oldData = open(golden).readlines()
    newData = open(outfile).readlines()

    # do the "quick" check to see if anything has been changed
    diff = difflib.unified_diff(oldData, newData, golden, outfile, n=0)

    leftDiff = 0
    rightDiff = 0
    oldModified = None
    oldDate = None
    newDate = None

    for line in diff:
        if line.startswith('-<instrument'):
            oldDate, oldModified = getModified(line)
        elif line.startswith('+<instrument'):
            newDate, newModified = getModified(line)
            if oldModified != newModified:
                leftDiff += 1
                rightDiff += 1
        else:
            if line.startswith('-') and not line.startswith('---'):
                leftDiff += 1
            if line.startswith('+') and not line.startswith('+++'):
                rightDiff += 1

    if oldDate is not None:
        logging.info(" Compare " + golden + " " + oldDate)
    else:
        logging.info(golden+" oldDate is None")
    if newDate is not None:
        logging.info(" With " + outfile + " " + newDate)
    else:
        logging.info(outfile+" newDate is None")

    # only print diff if there is a meaningful one
    if (leftDiff+rightDiff) > 0:
        logging.info(" ========================================")
        logging.info(" " + str(leftDiff) + " line(s) removed and " + str(rightDiff) + " line(s) added")
        # rerun and write out
        diff = difflib.unified_diff(oldData, newData, golden, outfile)
        sys.stdout.writelines(diff)
    else:
        logging.info(" " + os.path.split(golden)[1] + " and " + os.path.split(outfile)[1] + " match")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Verify that definition files haven't changed")
    parser.add_argument("-l", "--loglevel", default="WARNING",
                        help="Specify the log level (" + ", ".join(LOGLEVELS) + "), default is WARNING")
    parser.add_argument("-v", "--version", action="store_true",
                        help="Print the version information and exit")
    parser.add_argument("--copy-from-mantid", dest="mantidloc", default=None,
                        help="Copy the most recent geometry files from mantid instrument directory")
    parser.add_argument("--setup", action="store_true",
                        help="Run all of the geometries from the unchanged repository")
    parser.add_argument("--diffonly", action="store_true",
                        help="Don't run the geometries, only calculate the differences")
    parser.add_argument("--script", help="Script file to run")

    # parse the command line
    options = parser.parse_args()

    # setup logging
    logging.basicConfig(format='%(levelname)s:%(message)s',
                        level=options.loglevel)

    # log the options and arguments
    logging.debug('Options: ' + str(options))

    # if they want the version just give it back and exit
    if options.version:
        print(sys.argv[0] + " version " + __version__)
        sys.exit(0)

    # where is the actual test script
    directory = os.path.dirname(os.path.realpath(__file__))

    # determine what geometries are available
    if options.script is None:
        geometries = findGeoms()
    else:
        if not os.path.isabs(options.script):
            options.script = os.path.join(directory, options.script)
            options.script = os.path.abspath(options.script)
        geometries = [options.script]

    # generate the expected geometry file names
    outfiles = {}
    for geometry in geometries:
        outfiles[geometry] = toOutputNames(geometry)

    # copy the files from a mantid source tree if specified
    if options.mantidloc is not None:
        mantidloc = os.path.abspath(options.mantidloc)
        if not os.path.exists(mantidloc):
            raise RuntimeError("Specified non-existent instrument directory " + mantidloc)
        if not os.path.isdir(mantidloc):
            raise RuntimeError(mantidloc + " is not a directory")
        import shutil
        for key in outfiles.keys():
            copyFromMantid(mantidloc, outfiles[key][2], outfiles[key][0])
        sys.exit(0)

    # run each one
    if not options.diffonly:
        for key in outfiles.keys():
            master, output, instrument = outfiles[key]
            runGeom(key, master, output, options.setup)

    # exit early if we are in setup
    if options.setup:
        sys.exit(0)

    # calculate and display the differences
    for key in outfiles.keys():
        master, output, instrument = outfiles[key]
        compareGeom(master, output)
