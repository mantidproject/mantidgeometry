import numpy as np

def histEventList(evlist):
    bins = np.histogram(evlist[:, 1], 500)
    binnedData=np.zeros([500,4*16*48])
    for i in range(4*16*48):
        ind = evlist[:, 0] == i
        tmp=evlist[ind,1]
       
        binnedEvents = np.histogram(tmp, bins[1])
        
        binnedData[:,i]=binnedEvents[0]

    return bins, binnedData

evlst=np.load('Eventlist.dat.npy')

bins,binneddata=histEventList(evlst)
test=CreateWorkspace(bins[1],np.transpose(binneddata),NSpec=4*16*48,UnitX='tof')
LoadInstrument("test", True, Filename="c:/multigrid/cncs_multigrid1.xml") 
data = test.extractY()
data = np.sum(data, axis=1)

with open("MultigridData.csv", "w") as f:
    f.write("x,y,z,signal,detectorID\n")
    for i, signal in enumerate(data):
        det = test.getDetector(i)
        detPos = det.getPos()
        detID = det.getID()
        detShape = det.shape()
        detBB = detShape.getBoundingBox()
        xoff = detPos[0]
        yoff = detPos[1]
        zoff = detPos[2]
        x = detBB.minPoint()[0]
        y = detBB.minPoint()[1]
        z = detBB.minPoint()[2]
        dx = detBB.maxPoint()[0] - detBB.minPoint()[0]
        dy = detBB.maxPoint()[1] - detBB.minPoint()[1]
        dz = detBB.maxPoint()[2] - detBB.minPoint()[2]
        f.write(str(xoff+x)+","+str(yoff+y)+","+str(zoff+z)+","+str(signal)+","+str(detID)+"\n")
        f.write(str(xoff+x+dx)+","+str(yoff+y)+","+str(zoff+z)+","+str(signal)+","+str(detID)+"\n")
        f.write(str(xoff+x)+","+str(yoff+y+dy)+","+str(zoff+z)+","+str(signal)+","+str(detID)+"\n")
        f.write(str(xoff+x+dx)+","+str(yoff+y+dy)+","+str(zoff+z)+","+str(signal)+","+str(detID)+"\n")
        f.write(str(xoff+x)+","+str(yoff+y)+","+str(zoff+z+dz)+","+str(signal)+","+str(detID)+"\n")
        f.write(str(xoff+x+dx)+","+str(yoff+y)+","+str(zoff+z+dz)+","+str(signal)+","+str(detID)+"\n")
        f.write(str(xoff+x)+","+str(yoff+y+dy)+","+str(zoff+z+dz)+","+str(signal)+","+str(detID)+"\n")
        f.write(str(xoff+x+dx)+","+str(yoff+y+dy)+","+str(zoff+z+dz)+","+str(signal)+","+str(detID)+"\n")
        
print "done"
    
