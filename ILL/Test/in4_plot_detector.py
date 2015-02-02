"""
Plot IN4 detector
"""
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

import sys
from collections import Counter

"""
Copied from the in4_generate.py
"""
# last 96 angles are the opening of the beam (rho)
azimuthalAngle = [-15.925, -14.975, -14.025, -13.075, 13.075, 14.025, 14.975, 15.925, 19.075, 20.025, 20.975, 21.925, 24.975, 25.925, 26.875, 27.825, 28.775, 29.725, 30.675, 31.625, 34.575, 35.525, 36.475, 37.425, 38.375, 39.325, 40.275, 41.225, 44.075, 45.025, 45.975, 46.925, 47.875, 48.825, 49.775, 50.725, 50.675, 52.625, 53.775, 54.525, 57.275, 58.225, 59.175, 60.125, 61.075, 62.025, 62.975, 63.925, 64.875, 65.825, 66.775, 67.725, 70.475, 71.425, 72.375, 73.325, 74.275, 75.225, 76.175, 77.125, 78.075, 79.025, 79.975, 80.925, 83.575, 84.525, 85.475, 86.425, 87.375, 88.325, 89.275, 90.225, 91.175, 92.125, 93.075, 94.025, 96.675, 97.625, 98.575, 99.525, 100.475, 101.425, 102.375, 103.325, 104.275, 105.225, 106.175, 107.125, 109.875, 110.825, 111.775, 112.725, 113.675, 114.625, 115.575, 116.525, 117.475, 118.425, 119.375, 120.325, 13.275, 14.225, 15.175, 16.125, 17.075, 18.025, 18.975, 19.925, 20.875, 21.825, 22.775, 23.725, 26.275, 27.225, 28.175, 29.125, 30.075, 31.025, 31.975, 32.925, 33.875, 34.825, 35.775, 36.725, 39.275, 40.275, 41.175, 42.125, 43.075, 44.025, 44.975, 45.925, 46.875, 47.825, 48.775, 49.725, 52.275, 53.225, 54.175, 55.125, 56.075, 57.025, 57.975, 58.925, 59.875, 60.825, 61.775, 62.725, 64.325, 65.275, 66.225, 67.175, 68.125, 69.075, 70.025, 70.975, 71.925, 72.875, 73.825, 74.775, 78.275, 79.225, 80.175, 81.125, 82.075, 83.025, 83.975, 84.925, 85.875, 86.825, 87.775, 88.725, 91.275, 92.225, 93.175, 94.125, 95.075, 96.025, 96.975, 97.925, 98.875, 99.825, 100.775, 101.725, 104.275, 105.225, 106.175, 107.125, 108.075, 109.025, 109.975, 110.925, 111.875, 112.825, 113.775, 114.725, 117.275, 118.225, 119.175, 120.125, -15.925, -14.975, -14.025, -13.075, 13.075, 14.025, 14.975, 15.925, 19.075, 20.025, 20.975, 21.925, 24.975, 25.925, 26.875, 27.825, 28.775, 29.725, 30.675, 31.625, 34.575, 35.525, 36.475, 37.425, 38.375, 39.325, 40.275, 41.225, 44.075, 45.025, 45.975, 46.925, 47.875, 48.825, 49.775, 50.725, 50.675, 52.625, 53.775, 54.525, 57.275, 58.225, 59.175, 60.125, 61.075, 62.025, 62.975, 63.925, 64.875, 65.825, 66.775, 67.725, 70.475, 71.425, 72.375, 73.325, 74.275, 75.225, 76.175, 77.125, 78.075, 79.025, 79.975, 80.925, 83.575, 84.525, 85.475, 86.425, 87.375, 88.325, 89.275, 90.225, 91.175, 92.125, 93.075, 94.025, 96.675, 97.625, 98.575, 99.525, 100.475, 101.425, 102.375, 103.325, 104.275, 105.225, 106.175, 107.125, 109.875, 110.825, 111.775, 112.725, 113.675, 114.625, 115.575, 116.525, 117.475, 118.425, 119.375, 120.325, 2.435, 3.008, 3.581, 4.154, 4.727, 5.300, 5.873, 6.446, 7.019, 7.592, 8.165, 8.738, 2.435, 3.008, 3.581, 4.154, 4.727, 5.300, 5.873, 6.446, 7.019, 7.592, 8.165, 8.738, 2.435, 3.008, 3.581, 4.154, 4.727, 5.300, 5.873, 6.446, 7.019, 7.592, 8.165, 8.738, 2.435, 3.008, 3.581, 4.154, 4.727, 5.300, 5.873, 6.446, 7.019, 7.592, 8.165, 8.738, 2.435, 3.008, 3.581, 4.154, 4.727, 5.300, 5.873, 6.446, 7.019, 7.592, 8.165, 8.738, 2.435, 3.008, 3.581, 4.154, 4.727, 5.300, 5.873, 6.446, 7.019, 7.592, 8.165, 8.738, 2.435, 3.008, 3.581, 4.154, 4.727, 5.300, 5.873, 6.446, 7.019, 7.592, 8.165, 8.738, 2.435, 3.008, 3.581, 4.154, 4.727, 5.300, 5.873, 6.446, 7.019, 7.592, 8.165, 8.738]
# 398  ( SmalANGLE-Roscace=4  Bot=1 Medium=2 Top=3 Moni=0 )
detectorLocation = [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4]
# Roscace apperar to have 8 detectors (pie) of 12 tubes each.

numberOfSimpleDetectors=300
simpleDetAngle=azimuthalAngle[0:numberOfSimpleDetectors]
simpleDetLocation=detectorLocation[0:numberOfSimpleDetectors] #len=300

rosaceDetAngle=azimuthalAngle[numberOfSimpleDetectors:]
rosaceDetLocation=detectorLocation[numberOfSimpleDetectors:] #len=96
numberOfSlicesInRosace=8

# # Global variables
numberOfDetectors = len(azimuthalAngle)
numberOfSimpleDets = len(simpleDetAngle)
firstDetectorId = 1
radius = 2.0  # meters
angle = 12.6 #16  # degrees # vertical detection angle
# Don't touch!
uniqueDic = Counter(azimuthalAngle)
numberOfBanks = len(uniqueDic)
uniqueAngles = np.array([k for k, v in sorted(uniqueDic.iteritems())])
numberOfDetsPerBank = np.array([v for k, v in sorted(uniqueDic.iteritems())])
# Reverse sorted numpy arrays
uniqueAngles = uniqueAngles[ ::-1 ]
numberOfDetsPerBank = numberOfDetsPerBank[ ::-1 ] 

"""
Code starts here
"""
#plt.ion()
fig = plt.figure()
#ax = fig.add_subplot(111, projection='3d')
ax = Axes3D(fig)
ax.view_init(-80,90)


detId = firstDetectorId
for theta,loc in zip(simpleDetAngle,simpleDetLocation):
    #  Bot=1 Medium=2 Top=3
    if loc == 1:
        p = -angle
    elif  loc == 2:
        p = 0
    elif loc == 3 :
        p = angle
    else:
        sys.stderr.write("Invalid Loc: " + str(loc)) 
        sys.exit(0)
    
    thetaRadians = theta * np.pi / 180 - np.pi;
    angleRadians = p * np.pi / 180 - np.pi / 2;
    z = radius * np.sin(angleRadians) * np.cos(thetaRadians)
    x = radius * np.sin(angleRadians) * np.sin(thetaRadians)
    y = radius * np.cos(angleRadians)
    
    # just to plot a few
    if detId%3 == 0:
        ax.scatter(x, y, z, c='y', marker='.')
    
    detId+=1
    
# sphere

# We know the detector is a sphere
# 

uarr = [-angle,0,angle]
print simpleDetAngle
varr = simpleDetAngle
for v in varr:
    vrad = v * np.pi / 180.0

    for u in uarr:
        urad = u * np.pi / 180.0
        
        
        #plane equation
        z = np.cos(vrad) * radius
        
        y = np.sin(urad) * radius
        
        xsq =  - ((y**2) + (z**2)) + (radius**2)
        x = np.sqrt(xsq)
        
        if ((y**2) + (z**2)) > (radius**2) :
            print u,'\t',v,'\t',x,'\t',y,'\t',z,'\t',(y**2) + (z**2),'\t',(radius**2)
        
        
        if v > 0:
            ax.scatter(x, y, z, c='r', marker='x')
        else :
            ax.scatter(-x, y, z, c='r', marker='x')



# uarr = [-angle,0,angle]
# print simpleDetAngle
# varr = simpleDetAngle
# for u in uarr:
#     u = u * np.pi / 180.0
#     for v in varr:
#         v = v * np.pi / 180.0
#         
#         # spherical
#         r = radius
#         phi = v
#         # theta has 3 values arct(y,x)
#         theta = np.arctan2(np.sin(u) * r,np.sin(v) * r)
#         
#         x = r * np.cos(theta) * np.sin(phi)
#         y = r * np.sin(theta) * np.sin(phi)
#         z = r * np.cos(phi)
#         
#         ax.scatter(x, y, z, c='b', marker='.')
        
        
        
        
        
        
        
#         y = radius * np.sin(u)
#         z = radius * np.cos(v)
#         
#         if (np.square(y) + np.square(z)) > np.square(radius) :
#             print np.square(y) + np.square(z) , np.square(radius)
#         
#         x = np.sqrt( np.square(radius) - np.square(y) - np.square(z) )
#         
#         #ax.plot_wireframe(x, y, z, color="r")
#         if v > 0:
#             ax.scatter(x, y, z, c='b', marker='.')
#         else :
#             ax.scatter(-x, y, z, c='b', marker='.')



ax.set_xlabel('X Label')
ax.set_ylabel('Y Label')
ax.set_zlabel('Z Label')

plt.show()
# for angle in range(270, 360):
#     ax.view_init(30, angle)
#     plt.draw()


