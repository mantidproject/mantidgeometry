import math
import numpy as np


class LOKIGenerator(object):
    ''' Generates an Instrument Definition File (IDF) for the LOKI intrument '''
   
    def __init__(self, sectors, innerRadius, outerRadius, phiSlice, yStep, thetaTilt, outputFile):
        ''' Initialises the LOKIGenerator object
        Args:
            sectors: Number of sectors per detector bank
            innerRadius: Sector inner radius in metres
            outerRadius: Sector outer radius in metres 
            phiSlice: Number of phi slices per sector
            yStep: Step length in y in metres
            thetaTilt: Tilt angle which may not necessarily be on xy plane
            outputFile: File name where XML IDF will be stored
        '''
        # Define the segmentation of the
        # detector surface
        self.xSeg=phiSlice
        self.ySeg= (outerRadius - innerRadius)/yStep

        self.ySeg = int(math.ceil(self.ySeg))
       
        #metres
        self.ymin = innerRadius
        self.ymax = outerRadius

        self.pi = 3.14159265359
        self.piDiv = self.pi/180.0
        self.printArr = None
        self.outputFile = outputFile

        # Number of fan pieces in LOKI instrument
        self.numPieces = sectors

    def _calcVerts(self):
        '''
        Calculates the vertices for a single detector bank. This will be used in the IDF to produce all
        other detector banks.
        '''
        # Rotation of fan segments wrt to each other
        angleInc = 44.9999999999/self.xSeg
        theta = 0.0;
        x_ = 0.0
        y_ = 0.0

        arr_ = []
        xsort = None
        nparr = None

        h = self.ymax - self.ymin;
        h_seg = h/(self.ySeg + 1);
        y_val = self.ymin

        z=0;

        for y in xrange(self.ySeg+1):
            theta = -angleInc*(self.xSeg/2)
            for x in xrange(self.xSeg+1):
                if theta == 0:
                    x_ = 0
                else:
                    x_ = y_val/math.tan(self.piDiv * (90-theta))
                
                y_ = y_val
                arr_.append([x_, y_, z*0.001])
                theta += angleInc
            
            y_val += h_seg
            
            xsort = np.asarray(arr_).reshape(len(arr_), 3)
            xsort = xsort[np.argsort(xsort[:,0])]
            
            del arr_[:]
            
            if y == 0:
                nparr = xsort
            else:
                nparr = np.append(nparr, xsort)

        nparr = nparr.reshape((nparr.size/3,3))
                
        self.printArr = nparr
            
        self.printArr = self.printArr.reshape((self.printArr.size/3, 3))

    def _writeIDFHeader(self, f):
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

    def _writeIDFDefaults(self, f):
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

    def _writeIDFSamplesAndSources(self, f):
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

        ### write sources #############################################################################
        xyval = 0.0
        zval = 0.0
        val = [-1, 1] # used for alternating sign
        c1 = 0; # index into val for alternating sign
        c2 = 0; # index into val for alternating sign

        for i in xrange(numSources):
            f.write("<type name=\"line-sourceMantid-"+str(i)+"\" >\n")
            f.write("\t<cylinder id=\"dummy\" >\n")
            f.write("\t\t<centre-of-bottom-base x=\""+str(xyval * val[c1])+"\" y=\""+str(xyval * val[c2])+"\" z=\""+str(zval)+"\" />\n")
            f.write("\t\t<axis x=\""+str(0.000555556 * val[c1])+"\" y=\""+str(0.000555556 * val[c2])+"\" z=\"0.333333\" />\n")
            f.write("\t\t<radius val=\"0.005\" />\n")
            f.write("<height val=\"0.333333925927047\" />\n")
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
            f.write("\t\t<centre-of-bottom-base x=\""+str(0.005 * c1)+"\" y=\""+str(0.005 * c2)+"\" z=\""+str(0.0025 * c3)+"\" />\n")

            if i < 8:
                f.write("\t\t<axis x=\""+str(ax[(i+3)%4])+"\" y=\""+str(ax[(i+2)%4])+"\" z=\"0\" />\n")
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

    def _writeIDFDetectorBanks(self, f):
        ''' Writes each detector bank and handles rotation and offsets.
        Each bank is fan shaped and rotated 45 degrees with respect to the
        previous bank starting at 0 degrees. There is an additional offset
        added to each panel of 0.01m.
        Args:
            f: File handle
        '''

        f.write("<!--\n")
        f.write("Define detector panels so that each panel is rotated 45 degrees w.r.t the previous\n")
        f.write("in the Z direction. It produces the following arrangement of detectors: \n\n")
        f.write("\t\t 2  1  8\n")
        f.write("\t\t  \ | / \n")
        f.write("\t\t3-     -7 \n")
        f.write("\t\t  / | \ \n")
        f.write("\t\t 4  5  6 \n")
        f.write("\-->\n\n")

        f.write( "<component name =\"MonNDtype-0\" type=\"fan\" idstart=\"0\" idfillbyfirst=\"x\" idstepbyrow=\"1\" idstep=\"100\">\n")
        f.write("<!-- Detector panel 1 with offset x=0.01*sin(0) y=0.01*cos(0) -->\n")
        f.write( "\t<location x=\"0\" y=\"0.01\" z=\" 9.23\"/>\n")
        f.write( "</component>\n\n")

        angle = 45.0;
        id = 1000;

        #write components to file.
        for i in xrange(self.numPieces-1):
            f.write( "<component name =\"MonNDtype-"+str(i+1)+"\" type=\"fan\" idstart=\""+str(id)+"\" idfillbyfirst=\"x\" idstepbyrow=\"1\" idstep=\"100\">\n")
            f.write("<!--\n")
            f.write("Detector Panel "+str(i+2)+" with offset x=0.01*sin("+str(-angle)+") y=0.01*cos("+str(angle)+")\n ")
            f.write("the negative angle in x produces the correct sign for the x offset-->\n")
            if angle <= 180:
                f.write( "\t<location x=\""+str(0.01 * math.sin(self.piDiv * -angle))+"\" y=\""+str(0.01 * math.cos(self.piDiv * angle))+"\" z=\"9.23\" rot=\""+str(angle)+"\" axis-x=\"0.0\" axis-y=\"0.0\" axis-z=\"1.0\" />\n")
            else:
                f.write( "\t<location x=\""+str(0.01 * math.sin(self.piDiv * -angle))+"\" y=\""+str(0.01 * math.cos(self.piDiv * angle))+"\" z=\"9.23\" rot=\""+str(360-angle)+"\" axis-x=\"0.0\" axis-y=\"0.0\" axis-z=\"-1.0\" />\n")
            angle += 45.0
            f.write( "</component>\n\n")
            id+=1000

    def _writeIDFVertices(self, f):
        ''' Writes StructuredDetector type and all vertices which make up the first
        panel using the structured detector winding order (x increases, then y).
        Args:
            f: File handle
        '''
        f.write( "<type name=\"fan\" is=\"StructuredDetector\" xpixels=\""+str(self.xSeg)+"\" ypixels=\""+str(self.ySeg)+"\" type=\"pixel\">\n")
        f.write("<!--\n")
        f.write("Define every vertex for the StructuredDetector in X and Y, \n")
        f.write("assuming the detector is flat with the normal in the Z direction.\n")
        f.write("-->\n")

        #write individual vertices to file.
        for i in xrange(self.printArr.size/3):
            f.write( "\t <vertex x=\""+str(self.printArr[i][0])+"\" y=\""+str(self.printArr[i][1])+"\" />\n")
        f.write( "</type>\n"   )

        f.write( "<type is=\"detector\" name=\"pixel\"/>\n" )
        f.write("</instrument>")

    def _writeXMLIDF(self):
        '''
        Writes the IDF file using vertices and information about the detector
        '''
        with open(self.outputFile, "w") as f:
            #write xml header
            self._writeIDFHeader(f)

            #write defaults
            self._writeIDFDefaults(f)
            
            #write samples and sources
            self._writeIDFSamplesAndSources(f)

            #write components
            self._writeIDFDetectorBanks(f)

            #write Detector type and vertices
            self._writeIDFVertices(f)

    def generateLOKI(self):
        '''Generates Loki IDF'''
        self._calcVerts()
        self._writeXMLIDF()
        
if __name__ == "__main__"   :         
    lokiGen = LOKIGenerator(8, 0.03, 0.43, 10, 0.004, 0, "LOKI_Definition.xml")
    lokiGen.generateLOKI()