#!/usr/bin/env python

import os, sys
from lxml import etree
if len(sys.argv)>1:
    here, inmantid = sys.argv[1:3]
    here = etree.parse(open(here))
    inmantid = etree.parse(open(inmantid))
else:
    here = etree.parse(open('SEQUOIA_Definition.xml'))
    inmantid = etree.parse(open(os.path.expanduser('~/.mantid/instrument/SEQUOIA_Definition_20120404_20180513.xml')))

def diff(a, b):
    if a is None and b is None: return
    if a is None or b is None: return True
    # is string
    return a.strip() != b.strip()

def elements_equal(e1, e2):
    diffs = []
    if e1.tag != e2.tag:
        diffs.append( ('tag', e1.tag, e2.tag) )
    if diff(e1.text, e2.text):
        diffs.append( ("text", e1.text, e2.text))
    if diff(e1.tail, e2.tail):
        diffs.append( ("tail", e1.tail, e2.tail))
    if e1.attrib != e2.attrib:
        diffs.append( ("attrib", e1.attrib, e2.attrib))
    if len(e1) != len(e2):
        diffs.append( ("len", len(e1), len(e2)))
    if diffs:
        attr_str = ' '.join('%s=%s' % (k,v) for k,v in e1.attrib.items())
        print '* <%s %s>' % (e1.tag, attr_str)
        for d in diffs:
            kind, v1, v2 = d
            print "  %s" % kind
            print '\t-%s' % v1
            print '\t-%s' % v2
    return all(elements_equal(c1, c2) for c1, c2 in zip(e1, e2))

elements_equal(here.getroot(), inmantid.getroot())
