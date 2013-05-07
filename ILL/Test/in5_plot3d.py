#!/usr/bin/python

'''
Created on 24 Nov 2012

@author: leal
'''
import nxs
import numpy as np
import mayavi.mlab as mlab
import argparse

# http://docs.enthought.com/mayavi/mayavi/mlab_case_studies.html#mlab-case-studies

def readData(filePath='/home/leal/Documents/Mantid/IN5/094460.nxs'):
    f = nxs.open(filePath)
    f.opengroup('entry0')
    f.opengroup('data')
    f.opendata('data')
    a = f.getdata()
    f.closedata()
    f.closegroup()
    f.closegroup()
    f.close()
    # a.shape
    # Out[15]: (384, 256, 512)
    return a

def plotData2D(a):
    """
    Reduce one dimension of the 3D array
    """
    n = np.empty((a.shape[0], a.shape[1]), dtype=a.dtype)
    for i in range(a.shape[0]): 
        for j in range(a.shape[1]): 
            s = np.sum(a[i, j, :])
            n[i, j] = np.round(s/20)
    
    mlab.surf(n)
    mlab.show()

def plotData3DContour(a):
    mlab.contour3d(a,contours=4, transparent=True, vmin=0.2, vmax=0.8)
    
def plotData3D(a):
    #mlab.pipeline.volume(mlab.pipeline.scalar_field(a))
    mlab.pipeline.volume(mlab.pipeline.scalar_field(a), vmin=0.2, vmax=0.8)

def plotCutPlanes(s):
    mlab.pipeline.image_plane_widget(mlab.pipeline.scalar_field(s),
                            plane_orientation='x_axes',
                            slice_index=100,
                        )
    mlab.pipeline.image_plane_widget(mlab.pipeline.scalar_field(s),
                            plane_orientation='y_axes',
                            slice_index=100,
                        )
    mlab.outline()

def plotFancy(a):
    src = mlab.pipeline.scalar_field(a)
    mlab.pipeline.iso_surface(src, contours=[a.min() + 0.1 * a.ptp(), ], opacity=0.1)
    mlab.pipeline.iso_surface(src, contours=[a.max() - 0.1 * a.ptp(), ],)
    mlab.pipeline.image_plane_widget(src,
                            plane_orientation='z_axes',
                            slice_index=len(a[0,0,:])/2,
                        )    
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Debug IN5 tof')
    parser.add_argument('-f', '--file', help='Nexus file to parse', required=True)
    args = vars(parser.parse_args())
    
    a = readData(args['file'])
    #plotData2D(a)
    #plotData3D(a)
    #plotData3DContour(a)
    plotFancy(a)
    #plotCutPlanes(a)
    mlab.show()
    
