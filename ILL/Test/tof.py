'''
Created on Jun 11, 2013

@author: leal
'''
def convertToEnergy(wavelength):
    '''
    Convert wavelength A to Energy meV
    '''
    wavelength = wavelength*1e-10 # A -> m
    m = 1.67e-27 # kg 
    h = 6.626e-34 
    mev = 1.6e-22
    e = ((h/wavelength)**2)/ (2*m) / mev
    return e

def tof(distance,wavelength):
    '''
    get tof from distance and wavelength
    '''
    wavelength = wavelength*1e-10 # A -> m
    m = 1.67e-27 # kg 
    h = 6.626e-34 
    speed = h / ( m * wavelength ) # m/s
    return distance / speed;

if __name__ == '__main__':
    print 'Start test'
    wavelength = 5;
    distance = 5;
    print 'convertToEnergy:', convertToEnergy(wavelength)
    print 'tof:', tof(distance,wavelength)
    print 'End test'
    
    print 'mibemol'
    print 'convertToEnergy:', convertToEnergy(wavelength=5.2)
    print 'tof:', tof(distance=0.49+3.58,wavelength=5.2)
    
    