import numpy as np

def histEventList(evlist):
    bins = np.histogram(evlist[:, 1], 500)
    binnedData=np.zeros([500,4*16*48])
    for i in range(4*16*48):
        ind = evlist[:, 0] == i
        tmp=evlist[ind,1]
        
        print('Number of counts in channel ' ,i,' ', len(tmp))
        binnedEvents = np.histogram(tmp, bins[1])
        
        binnedData[:,i]=binnedEvents[0]

    return bins, binnedData

evlst=np.load('Eventlist.dat.npy')

bins,binneddata=histEventList(evlst)
print binneddata
test=CreateWorkspace(bins[1],np.transpose(binneddata),NSpec=4*16*48,UnitX='tof')
