#!/usr/bin/python

'''
Created on August 2012

@author: ricardo.leal@ill.fr

'''

import nxs, os, sys
import numpy as np

'''



'''

def _show(f, indent=0):
    prefix = ' ' * indent
    link = f.link()
    # link
    if link:
        print "%(prefix)s-> %(link)s" % locals()
        return
    # Atributes
    for attr, value in f.attrs():
        # HDF attributes like: NeXus_version
        # at the beggining of the file
        print "%(prefix)s@%(attr)s = %(value)s" % locals()
    #Class
    for name, nxclass in f.entries():
        if nxclass == "SDS": # Dataset
            shape, dtype = f.getinfo()
            dims = "x".join([str(x) for x in shape])
            print "%(prefix)s%(name)s : %(dtype)s [%(dims)s] " % locals()
            link = f.link()
            if link:
                print "  %(prefix)s-> %(link)s" % locals()
            else:
                for attr, value in f.attrs():
                    print "  %(prefix)s@%(attr)s = %(value)s" % locals()
                #if np.prod(shape) < 8:
                if np.prod(shape) < 128: # Prints strings up to len 128 
                    value = f.getdata()
                    print "  %s< %s >" % (prefix, str(value))
        else:
            print "%(prefix)s%(name)s : %(nxclass)s" % locals()
            _show(f, indent + 2)

def show_structure(filename):
    f = nxs.open(filename)
    print "Showing contents for: ", f.inquirefile()
    _show(f)
    
 

if __name__ == '__main__':
    if len(sys.argv) >= 2: 
        show_structure(sys.argv[1])
    else:
        print 'Use: %s <nexusfile>' % sys.argv[0]

