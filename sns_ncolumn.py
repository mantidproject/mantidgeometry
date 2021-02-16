#!/usr/bin/env python
import os


def readFile(filename, hasLabels=True, headerLines=0, delimiter=r'\s+'):
    """This loads in a n-column ascii file and converts it into a dictionary
    where the column headings are the keys, and the columns are as a list in
    the value. If the "hasLabels" variable is False then the keys are the
    column numbers."""

    if not os.path.exists(filename):
        raise RuntimeError("File '%s' does not exist" % filename)

    # load the file
    with open(filename, "r") as datafile:
        lines = []
        numcol = None
        import re
        splitter = re.compile(delimiter)
        for linenum, line in enumerate(datafile):
            if linenum < headerLines:
                continue
            line = line.strip()
            if len(line) > 0:
                line = splitter.split(line)
                if numcol is None:
                    numcol = len(line)
                else:
                    if numcol != len(line):
                        raise Exception("Number of columns varies at line %d in '%s'"
                                        % (linenum, filename))
                lines.append(line)

    # set up resulting data structure
    if (hasLabels):
        labels = lines[0]
        lines = lines[1:]
    else:
        labels = range(numcol)
    result = {}
    for label in labels:
        result[label] = []

    # convert it into a different form
    for line in lines:
        for (label, value) in zip(labels, line):
            result[label].append(value)

    # return the result
    return result


if __name__ == "__main__":
    info = readFile("SEQ_geom.txt")
    print("******************************")
    for key in info.keys():
        print(key, info[key][0])
