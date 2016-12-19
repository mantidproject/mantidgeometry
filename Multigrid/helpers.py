import numpy as np

def find(data,lolim,hilim):
    return np.where(np.logical_and(data>lolim,data<hilim))


def centerBins(dataIn):
    newVals = (dataIn + np.roll(dataIn, -1)) / 2  # calculate the bin center
    return np.delete(newVals, -1)

def lstSearch(lst,val1,val2,delta):
    return [item for item in lst if np.logical_and(np.logical_and(item[0] >= val1-delta, item[0] <= val1+delta), np.logical_and(item[1] >= val2-delta, item[1] <= val2+delta))]


def histEventList(evlist):
    bins = np.histogram(evlist[:, 1], 500)
    binnedData=np.zeros([500,8*16*48])
    for i in range(8*16*48):
        ind = evlist[:, 0] == i
        tmp=evlist[ind,1]
        print('Number of counts in channel ' ,i,' ', len(tmp))
        binnedEvents = np.histogram(tmp, bins[1])
        binnedData[:,i]=binnedEvents[0]

    return bins, binnedData




