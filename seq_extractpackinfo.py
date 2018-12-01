#!/usr/bin/env python

"""extract pack geometry info from a SEQ definition file and prints them
The output can be saved to a file that can be the input for sequoia_geometry.py
"""

import os, sys
from lxml import etree
f = sys.argv[1]
tree = etree.parse(open(f))

def travel(e):
    if str(e.tag).endswith('type'):
        name = e.attrib.get('name')
        if name[0] in ['B', 'C', 'D'] and 'row' not in name:
            extract(e)
            return
    for e1 in e: travel(e1)
    return

def extract(e):
    name = e.attrib['name']
    c = e[0]
    assert c.tag.endswith('component')
    assert str(c.attrib['type']).startswith('eightpack'), c.attrib
    l = c[0]
    assert l.tag.endswith('location')
    _ = lambda k: float(l.attrib[k])
    xyz = map(_, 'xyz')
    r = l[0]
    r = float(r.attrib['val'])
    x,y,z = xyz
    toinch = 100/2.54
    print "%s\t%.8f\t%.8f\t%.8f\t%.8f" % (name, x*toinch,y*toinch,z*toinch,r-180.)
    return

print "Location	X	Y	Z	Angle"
travel(tree.getroot())
