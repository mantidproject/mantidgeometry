from bitstruct import *
import numpy
import matplotlib.pyplot as plt
from helpers import find, centerBins,lstSearch



wiredata = numpy.load('Ch3.dat.npy')


indiwire=find(wiredata,150,1300)
wireHist=numpy.histogram(wiredata[indiwire],8*16)

wireLUVals=centerBins(wireHist[1])


griddata = numpy.load('Ch7.dat.npy')

indigrid=find(griddata,150,1000)
gridHist=numpy.histogram(griddata[indigrid],2*48)

gridLUVals=centerBins(gridHist[1])

#print(gridLUVals,wireLUVals)

LUT=dict()

#NOTE THE DATA SEEM TO INDICATE THAT THE GRID NUMBERING IS MISREPRESENTED IN THE MULTIGRID.PDF FILE. IT LOOKS LIKE WIRES 1-64 GO WITH GRIDS 49-96
pixID=0
for j in range(48,96):
    for k in range(0,64):
        LUT.update({(int(wireLUVals[k]),int(gridLUVals[j])):pixID})
        pixID += 1

for j in range(0,48):
    for k in range(64,128):
        LUT.update({(int(wireLUVals[k]),int(gridLUVals[j])):pixID})
        pixID += 1


LUTlst=list(LUT.keys())

#key = lstSearch(LUTlst, 768, 247, 70)
#print(key)
#LUT.get(key[0])

fname='2016_07_13_beamOn_4p96A_050.bin'


headerStruct = 'u2u6u8u1u3u12'
datastruct = 'u2u9u5u1u1u14'
footerStruct = 'u2u30'

dataCh1=numpy.array(0)
dataCh2=numpy.array(0)
dataCh3=numpy.array(0)
dataCh4=numpy.array(0)
dataCh5=numpy.array(0)
dataCh6=numpy.array(0)
dataCh7=numpy.array(0)
dataCh8=numpy.array(0)

timeStamp=numpy.array(0)
numberOfEvents=0
numberOfEventsWithPosition=0
numberOfEventsWithoutPosition=0
badwords=0
badheaders=0
EventList=[]
PixHistogram=numpy.zeros(8*16*48)
with open(fname,'rb') as fin:

    while True:
        try:
            header = unpack(headerStruct, byteswap('4',fin.read(4)))
            #print(header)
        except:
            print('EOF1')
            break
        if header[0] != 1:
            print ('Skipping, bad header')
            badheaders=badheaders+1

        if header[0]==1:
            try:
                eventData=[]
                for i in range(8):
                    tmpEvent=unpack(datastruct, byteswap('4', fin.read(4)))
                    #print(tmpEvent)
                    if tmpEvent[2]== i:
                        eventData.append(tmpEvent[5])
                        #print(eventData)
                    else:
                        print('Dataword missing')
                        badwords=badwords+1

                if len(eventData)==8:
                    numberOfEvents += 1
                    #print(eventData)

                    #dataCh3 = numpy.asarray(eventData[2])
                    #dataCh7 = numpy.asarray(eventData[6])
                    #print (eventData[2],eventData[6])
                    key = lstSearch(LUTlst, eventData[2], eventData[6], 4)
                    #print(len(key),key)
                    if len(key)==1:
                        #print ('pixID',LUT.get(key[0]))
                        PixID=LUT.get(key[0])
                        PixHistogram[PixID] += 1
                        numberOfEventsWithPosition += 1

                    elif len(key)>1:
                        print('neutron can be assigned to multiple voxels or no matching ID found')
                        numberOfEventsWithoutPosition += 1

            except:
                print('EOF2')
                break
            try:
                timeStamp=(unpack(footerStruct, byteswap('4',fin.read(4)))[1])
                #print(timeStamp)
                if len(key)==1:
                    EventList.append((PixID,timeStamp*0.0625))

                #print(timeStamp)
            except:
                print('EOF3')
                break

print(numberOfEvents, numberOfEventsWithPosition ,numberOfEventsWithoutPosition)
numpy.save('Eventlist.dat',EventList)
numpy.save('Histogram.dat',PixHistogram)

