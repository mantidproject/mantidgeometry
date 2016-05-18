import math
import numpy as np


class LOKIWriter(object):
    ''' Writes the Instrument Definition File (IDF) for the LOKI intrument '''
    #default setup for rear LOKI panel
    __defaultSampleDistance = 9.23
    __defaultSectors = 8
    __defaultPhiSlice = 10
    __defaultInnerRadius = 0.03
    __defaultOuterRadius = 0.43
    __defaultYStep = 0.004
    __defaultThetaTilt = 0.0
    __defaultBankName = "Bank_2"


    def __init__(self):
        ''' Initialises the LOKIGenerator object
        '''
        # Define the segmentation of the
        # detector surface
        #self.xSeg=self.__defaultPhiSlice
        #self.ySeg= (self.__defaultOuterRadius - self.__defaultInnerRadius)/self.__defaultYStep

        self.phiSlice = self.__defaultPhiSlice # number of phi slices per sector
        self.yStep = self.__defaultYStep # y pitch in metres

        self.innerRadiusY = self.__defaultInnerRadius # min y value in metres
        self.outerRadiusY = self.__defaultOuterRadius # max y value in metres

        # tilt of detector bank towards/away from sample
        self.thetaTilt = self.__defaultThetaTilt

        #pi values used for conversion from degrees to radians in sin/cos
        self.pi = 3.14159265359
        self.piDiv = self.pi/180.0

        self.vertexArray = None #stores calculated vertices for printing in IDF

        #Detector bank distance from sample
        self.sampleDistance = self.__defaultSampleDistance

        # Number of fan pieces in LOKI instrument
        self.numPieces = self.__defaultSectors
        self.angle = 360.0/float(self.numPieces) #divide 360 degrees

        self.bankName = self.__defaultBankName # unique bank id string

    def setSampleDistance(self, sampleDistance):
        ''' Sets the distance of a bank from the sample.
        :param sampleDistance: Distance of bank from sample
        '''
        self.sampleDistance = sampleDistance

    def setBankName(self, bankName):
        ''' Sets the unique identifier for each bank
        :param bankName: Unique identifier for detector ban
        '''
        self.bankName = bankName

    def setSectors(self, sectors):
        ''' Each detector bank is made of a set of panels. This describes the number
        of panels in each detector bank.

        :param sectors: The number of detector panel
        '''
        self.numPieces = sectors

    def setInnerRadius(self, innerRadius):
        ''' Inner bank radius
        :param innerRadius:
        '''
        self.innerRadiusY = innerRadius

    def setOuterRadius(self, outerRadius):
        ''' Outer bank radius
        :param outerRadius:
        '''
        self.outerRadiusY = outerRadius

    def setPhiSlice(self, phiSlice):
        ''' Number of detector segments in the x direction
        :param phiSlice:
        '''
        self.phiSlice = phiSlice

    def setYStep(self, yStep):
        ''' This sets the detector pitch in y
        :param yStep:
        '''
        if yStep == 0.0:
            raise Exception("yStep should be > 0.")

        self.yStep = yStep

    def setThetaTilt(self, thetaTilt):
        ''' The tilt angle (in degrees) towards (-ve) or away from (+ve) the sample.

        :param thetaTilt:
        '''
        self.thetaTilt = thetaTilt

    def calcVerts(self):
        '''
        Calculates the vertices for a single detector bank. This will be used in the IDF to produce all
        other detector banks.
        '''

        self.angle = 360.0/float(self.numPieces) # Rotation of fan segments wrt to each other
        angleInc = self.angle/self.phiSlice # Angle increments
        h = self.outerRadiusY - self.innerRadiusY; # total height of detector in meters
        y_val = self.innerRadiusY

        # calculate number of y segments to nearest integer
        ySeg = int(h / self.yStep)

        arr_ = [] # stores (x,y) values as array which will be sorted
        nparr = None # numpy array used to append sorted values to vertexArray.

        # Calculate and store vertices in winding order
        # required by StructuredDetector
        for y in xrange(int(ySeg+1)):
            theta = -angleInc*(self.phiSlice/2) # store current phi offset in degrees
            for x in xrange(self.phiSlice+1):
                # calculate x based on theta slice
                if theta == 0:
                    x_ = 0
                else:
                    x_ = y_val/math.tan(self.piDiv * (90-theta))

                #increment y value
                y_ = y_val
                arr_.append([x_, y_])
                theta += angleInc
            
            y_val += self.yStep

            #sort array by x
            xsort = np.asarray(arr_).reshape(len(arr_), 2)
            xsort = xsort[np.argsort(xsort[:,0])]
            
            del arr_[:]
            
            if y == 0:
                nparr = xsort
            else:
                nparr = np.append(nparr, xsort)

        #store vertices for printing
        nparr = nparr.reshape((nparr.size/2,2))
                
        self.vertexArray = nparr
            
        self.vertexArray = self.vertexArray.reshape((self.vertexArray.size/2, 2))

    def writeIDFHeader(self, f):
        ''' Writes XML header and instrument header information.
        Args:
            f: File handle
        '''
        f.write( "<?xml version='1.0' encoding='ASCII'?>\n")
        f.write( "<!-- For help on the notation used to specify an Instrument Definition File \n")
        f.write( "     see http://www.mantidproject.org/IDF -->\n")
        f.write( "<instrument xmlns=\"http://www.mantidproject.org/IDF/1.0\" \n")
        f.write( "            xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n")
        f.write( "            xsi:schemaLocation=\"http://www.mantidproject.org/IDF/1.0 http://schema.mantidproject.org/IDF/1.0/IDFSchema.xsd\"\n")
        f.write( " name=\"LOKI\" valid-from   =\"1900-01-31 23:59:59\"\n")
        f.write( "                         valid-to     =\"2100-01-31 23:59:59\"\n")
        f.write( "		          last-modified=\"2010-11-16 12:02:05\">\n")
        f.write( "<!---->\n")

    def writeIDFDefaults(self, f):
        ''' Writes Defaults information e.g length unit, angle unit,
        reference-frame etc.
        Args:
            f: File handle
        '''
        f.write( "<defaults>\n")
        f.write( "\t<length unit=\"metre\"/>\n")
        f.write( "\t<angle unit=\"degree\"/>\n")
        f.write( "\t<reference-frame>\n")
        f.write( "\t\t<along-beam axis=\"z\"/>\n")
        f.write( "\t\t<pointing-up axis=\"y\"/>\n")
        f.write( "\t\t<handedness val=\"right\"/>\n")
        f.write( "\t</reference-frame>\n")
        f.write("\t\t<default-view axis-view=\"z-\"/>")
        f.write( "</defaults>\n\n")

    def writeIDFSamplesAndSources(self, f):
        ''' Writes Instrument sources and samples.
        Args:
            f: File handle
        '''
        numSources = 20
        numSamples = 12

        f.write("<type name=\"Othercomp\"></type>\n\n")

        f.write("<component type=\"sourceMantid-type\" name=\"sourceMantid\">\n")
        f.write("<location x=\" 0\" y=\" 0\" z=\" 0\"  />\n")
        f.write("</component>\n\n")

        f.write("<component type=\"sampleMantid-type\" name=\"sampleMantid\">\n")
        f.write("<location x=\" 0\" y=\" 0\" z=\" 6.2\"  />\n")
        f.write("</component>\n\n")


        f.write("<type name=\"a1-type\"  >\n")
        f.write("</type>\n\n")

        ### write sources ##########################################################
        xyval = 0.0
        zval = 0.0
        val = [-1, 1] # used for alternating sign
        c1 = 0; # index into val for alternating sign
        c2 = 0; # index into val for alternating sign

        for i in xrange(numSources):
            f.write("<type name=\"line-sourceMantid-"+str(i)+"\" >\n")
            f.write("\t<cylinder id=\"dummy\" >\n")
            f.write("\t\t<centre-of-bottom-base x=\""+str(xyval * val[c1])+"\" " \
                    "y=\""+str(xyval * val[c2])+"\" z=\""+str(zval)+"\" />\n")
            f.write("\t\t<axis x=\""+str(0.000555556 * val[c1])+"\" " \
                    "y=\""+str(0.000555556 * val[c2])+"\" z=\"0.333333\" />\n")
            f.write("\t\t<radius val=\"0.005\" />\n")
            f.write("\t\t<height val=\"0.333333925927047\" />\n")
            f.write("\t</cylinder >\n")
            f.write("</type>\n\n")

            xyval += 0.00111111
            zval += 0.666667

            #switch indices every 5 elements
            if i == 4:
                c1 = 1
                c2 = 0
                xyval = zval = 0
            elif i == 9:
                c1 = c2 = 1
                xyval = zval = 0
            elif i == 14:
                c1 = 0
                c2 = 1
                xyval = zval = 0

        f.write("\n\n")

        f.write("<type name=\"sourceMantid-type\" is=\"Source\" >\n")
        for i in xrange(numSources):
            f.write("\t<component type=\"line-sourceMantid-"+str(i)+"\" >\n")
            f.write("\t\t<location x=\"0\" y=\"0\" z=\"0\" />\n")
            f.write("\t</component >\n\n")
        f.write("</type>\n\n\n")

        f.write("<type name=\"coll1-type\"  >\n")
        f.write("</type>\n\n")

        f.write("<type name=\"coll2-type\"  >\n")
        f.write("</type>\n\n\n")

        # write samples #############################################################
        c3 = -1
        c1 = -1
        c2 = -1
        ax = [0, -0.01, 0, 0.01]

        for i in xrange(numSamples):
            f.write("<type name=\"line-sampleMantid-"+str(i)+"\" >\n")
            f.write("\t<cylinder id=\"dummy\" >\n")
            f.write("\t\t<centre-of-bottom-base x=\""+str(0.005 * c1)+"\" " \
                    "y=\""+str(0.005 * c2)+"\" z=\""+str(0.0025 * c3)+"\" />\n")

            if i < 8:
                f.write("\t\t<axis x=\""+str(ax[(i+3)%4])+"\" " \
                        "y=\""+str(ax[(i+2)%4])+"\" z=\"0\" />\n")
            else:
                f.write("\t\t<axis x=\"0\" y=\"0\" z=\"0.005\" />\n")

            f.write("\t\t<radius val=\"0.005\" />\n")

            if i < 8:
                f.write("\t\t<height val=\"0.01\" />\n")
            else:
                f.write("\t\t<height val=\"0.005\" />\n")

            f.write("\t</cylinder >\n")
            f.write("</type>\n")

            if i % 2 == 0:
                c2 = c2 * -1
            if i % 4 == 0:
                c3 = c3 * -1

            c1 = c1 * -1
        f.write("\n\n")

        f.write("<type name=\"sampleMantid-type\" is=\"SamplePos\" >\n")

        for i in xrange(numSamples):
            f.write("\t<component type=\"line-sampleMantid-"+str(i)+"\" >\n")
            f.write("\t\t<location x=\"0\" y=\"0\" z=\"0\" />\n")
            f.write("\t</component >\n\n")
        f.write("</type>\n\n\n")

        f.write("<type name=\"STOP-type\"  >\n")
        f.write("</type>\n\n")

        f.write("<type name=\"PSDrad-type\"  >\n")
        f.write("</type>\n\n")

    def writeIDFDetectorBanks(self, f):
        ''' Writes each detector bank and handles rotation and offsets.
        Each bank is fan shaped and rotated 45 degrees with respect to the
        previous bank starting at 0 degrees. There is an additional offset
        added to each panel of 0.01m.
        Args:
            f: File handle
        '''

        f.write("<!--\n")
        f.write("Define detector panels so that each panel is " \
                "rotated "+str(self.angle)+" degrees w.r.t the previous\n")
        f.write("in the Z direction. For example, the following arrangement of detectors is produced: \n\n")
        f.write("\t\t 1  8  7\n")
        f.write("\t\t  \ | / \n")
        f.write("\t\t2-     -6 \n")
        f.write("\t\t  / | \ \n")
        f.write("\t\t 3  4  5 \n")
        f.write("\-->\n\n")

        id = 1000;
        ang = self.angle

        #write components to file.
        for i in xrange(self.numPieces):
            f.write( "<component name =\""+self.bankName+"_MonNDtype-"+str(i)+"\" " \
                    "type=\""+self.bankName+"\" idstart=\""+str(id)+"\" "\
                    "idfillfirst=\"y\" idstepbyrow=\"3\" idstep=\"30\">\n")
            if ang <= 180:
                f.write("\t<location x=\"" + str(0.01 * math.sin(self.piDiv * -ang)) + "\" " \
                        "y=\"" + str(0.01 * math.cos(self.piDiv * ang)) + "\" "\
                        "z=\"" + str(self.sampleDistance) + "\" " \
                        "rot=\"" + str(ang) + "\" axis-x=\"0.0\" axis-y=\"0.0\" axis-z=\"1.0\" >\n")
                f.write("\t\t<rot val=\"" + str(self.thetaTilt) + "\" " \
                        "axis-x=\"1\" axis-y=\"0\" axis-z=\"0\" />\n")
                f.write("\t</location>\n")
            else:
                f.write("\t<location x=\"" + str(0.01 * math.sin(self.piDiv * -ang)) + "\" " \
                        "y=\"" + str(0.01 * math.cos(self.piDiv * ang)) + "\" " \
                        "z=\"" + str(self.sampleDistance) + "\" " \
                        "rot=\"" + str(360 - ang) + "\" axis-x=\"0.0\" axis-y=\"0.0\" axis-z=\"-1.0\" >\n")
                f.write("\t\t<rot val=\"" + str(self.thetaTilt) + "\" " \
                        "axis-x=\"1\" axis-y=\"0\" axis-z=\"0\" />\n")
                f.write("\t</location>\n")

            ang += self.angle
            f.write( "</component>\n\n")
            id+=4000

    def writeIDFVertices(self, f):
        ''' Writes StructuredDetector type and all vertices which make up the first
        panel using the structured detector winding order (x increases, then y).
        Args:
            f: File handle
        '''

        # write structured detector type tag
        f.write("<type name=\""+self.bankName+"\" is=\"StructuredDetector\" " \
                "xpixels=\""+str(int(self.phiSlice))+"\" " \
                "ypixels=\""+str(int((self.outerRadiusY - self.innerRadiusY)/self.yStep))+"\" type=\"pixel\">\n")
        f.write("<!--\n")
        f.write("Define every vertex for the StructuredDetector in X and Y, \n")
        f.write("assuming the detector is flat with the normal in the Z direction.\n")
        f.write("-->\n")

        #write individual vertices to file.
        for i in xrange(self.vertexArray.size/2):
            f.write( "\t <vertex x=\""+str(self.vertexArray[i][0])+"\" y=\""+str(self.vertexArray[i][1])+"\" />\n")
        f.write( "</type>\n"   )

    def writeIDFFooter(self, f):
        '''
        Writes the ending footer of the IDF
        :param f: input file
        '''
        f.write("\n<type is=\"detector\" name=\"pixel\"/>\n")
        f.write("</instrument>")


class LOKIGenerator(object):
    '''Builder class which manages writing of LOKI files once provided with bank information'''
    def __init__(self):
        self._lokiWriter = LOKIWriter()
        self.idf = None

    def openIDF(self, fname):
        ''' Opens an new IDF file and writes header and default information. Samples
        and source information is also automatically written to file.

        :param fname: IDF file name
        :return:
        '''
        self.idf = open(fname, 'w')
        self._lokiWriter.writeIDFHeader(self.idf)
        self._lokiWriter.writeIDFDefaults(self.idf)
        self._lokiWriter.writeIDFSamplesAndSources(self.idf)

    def addBank(self, bankName, distFromSample, sectors, innerRadius, outerRadius, phislice, yStep, thetaTilt):
        '''Adds a new detector bank to the loki instrument
        which must then be written to file.

        :param bankName: Unique bank identifier
        :param distFromSample: Distance from sample position
        :param sectors: Number of sectors per detector bank
        :param innerRadius: Sector inner radius in metres
        :param outerRadius: Sector inner radius in metres
        :param phislice: Number of phi slices per sector
        :param yStep: Step length in y in metres
        :param thetaTilt: Tilt angle which may not necessarily be on xy plane
        :return:
        '''
        if self.idf.closed:
            raise Exception("IDF has already been generated.")

        self._lokiWriter.setBankName(bankName)
        self._lokiWriter.setSampleDistance(distFromSample)
        self._lokiWriter.setSectors(sectors)
        self._lokiWriter.setInnerRadius(innerRadius)
        self._lokiWriter.setOuterRadius(outerRadius)
        self._lokiWriter.setPhiSlice(phislice)
        self._lokiWriter.setYStep(yStep)
        self._lokiWriter.setThetaTilt(thetaTilt)

    def writeBank(self):
        ''' Writes a newly created detector bank to file.
        '''
        self._lokiWriter.calcVerts()
        self._lokiWriter.writeIDFDetectorBanks(self.idf)
        self._lokiWriter.writeIDFVertices(self.idf)

    def addAndWriteBank(self, bankName, distFromSample, sectors, innerRadius, outerRadius, phislice, yStep, thetaTilt):
        ''' Convenience method which adds a new detector bank and automatically writes it to file.

        :param bankName: Unique bank identifier
        :param distFromSample: Distance from sample position
        :param sectors: Number of sectors per detector bank
        :param innerRadius: Sector inner radius in metres
        :param outerRadius: Sector inner radius in metres
        :param phislice: Number of phi slices per sector
        :param yStep: Step length in y in metres
        :param thetaTilt: Tilt angle which may not necessarily be on xy plane
        :return:
        '''
        self.addBank(bankName, distFromSample, sectors, innerRadius, outerRadius, phislice, yStep, thetaTilt)
        self.writeBank()

    def closeIDF(self):
        if self.idf.closed:
            raise Exception("IDF has already been closed.")
        self._lokiWriter.writeIDFFooter(self.idf)
        self.idf.close()

if __name__ == "__main__"   :         
    #lokiGen = LOKIGenerator(8, 0.03, 0.43, 10, 0.004, 0, "LOKI_Definition.xml")
    #lokiGen.generateLOKI()

    loki = LOKIGenerator()
    loki.openIDF("LOKI_Definition.xml")
    loki.addAndWriteBank("Bank_2", 10, 8, 0.03, 0.5, 10, 0.004, 0)
    loki.addAndWriteBank("Bank_1", 5.00, 11, 0.23, 1.00, 10, 0.008, 0)
    loki.addAndWriteBank("Bank_0", 1.4, 14, 0.27, 1.30, 10, 0.012, 0)
    loki.closeIDF()
