
from bitstruct import *
import numpy
import matplotlib.pyplot as plt
#from pypeaks import Data, Intervals

from peakdet import peakdet
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
badwords=0
badheaders=0
with open(fname,'rb') as fin:

    while True:
        try:
            header = unpack(headerStruct, byteswap('4',fin.read(4)))
            #print(header)
        except:
            print('EOF')
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
                    numberOfEvents=numberOfEvents+1
                    #print(eventData)
                    dataCh1 = numpy.append(dataCh1, numpy.asarray(eventData[0]))
                    dataCh2 = numpy.append(dataCh2, numpy.asarray(eventData[1]))
                    dataCh3 = numpy.append(dataCh3, numpy.asarray(eventData[2]))
                    dataCh4 = numpy.append(dataCh4, numpy.asarray(eventData[3]))
                    dataCh5 = numpy.append(dataCh5, numpy.asarray(eventData[4]))
                    dataCh6 = numpy.append(dataCh6, numpy.asarray(eventData[5]))
                    dataCh7 = numpy.append(dataCh7, numpy.asarray(eventData[6]))
                    dataCh8 = numpy.append(dataCh8, numpy.asarray(eventData[7]))



            except:
                print('EOF')
                break
            try:
                timeStamp=numpy.append(timeStamp,(unpack(footerStruct, byteswap('4',fin.read(4)))[1]))
                #print(timeStamp)
            except:
                print('EOF')
                break

#time stamp convertion = 1 tick 16MHz clock - 0.0625 microsec per tick


print('number of events= ',numberOfEvents)
#print(timeStamp.shape)
#print(timeStamp[0])
print('#BadHeaders=', badheaders,' #badwords=',badwords)
timeStamp=timeStamp[1:]

#data=data.reshape(8,numberOfEvents)
#print(data)

def plotFigure(data,title):
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111)
    histoData = ax1.hist(data, 1000)
    fig1.suptitle(title)

    #peaks=peakdet(histoData[0],60)


    plt.show()

    #return peaks

def find_peaks(a):
  x = numpy.array(a)
  max = numpy.max(x)
  lenght = len(a)
  ret = []
  for i in range(lenght):
      ispeak = True
      if i-1 > 0:
          ispeak &= (x[i] > 1.8 * x[i-1])
      if i+1 < lenght:
          ispeak &= (x[i] > 1.8 * x[i+1])

      ispeak &= (x[i] > 0.05 * max)
      if ispeak:
          ret.append(i)
  return ret


numpy.save('Ch3.dat', dataCh3)
numpy.save('Ch7.dat', dataCh7)
plotFigure(dataCh3,'Ch3 Wire0 position ')


plotFigure(dataCh7,'Ch7 Grid0 position')

plotFigure(dataCh4,'Ch4 Wire1 position')
plotFigure(dataCh8,'Ch8 Grid1 position')


plotFigure(dataCh1,'Ch1 Wire0 events energy')
plotFigure(dataCh5,'Ch5 Grid0 events energy')

plotFigure(dataCh2,'Ch2 Wire1 events energy')
plotFigure(dataCh6,'Ch6 Grid1 events energy')



plotFigure(timeStamp,'timestamp')



