import xml
from xml.etree import ElementTree as et
import numpy as np

class IDFParser:
	fileContents = []
	ns = '{http://www.mantidproject.org/IDF/1.0}'
	def __init__(self, IDFFilename, offFilename, instrFilename=None):
		self.idf = IDFFilename
		self.off = offFilename
		self.instr = instrFilename
		tree = et.parse(IDFFilename)
		self.root = tree.getroot()
		
	def outputOFF(self):
		vertices = {}
  
		with open(self.off, "w") as offfile:
			offfile.write("OFF\n")
			structDets = []
			
			for elem in self.root.findall(self.ns+"type"):
				isStr = elem.get("is")
				
				if isStr == "StructuredDetector":
					structDets.append(elem)
					
			for det in structDets:
				w = int(det.get("xpixels"))
				h = int(det.get("ypixels"))
				offfile.write("#<type name=\"StrDet\" is=\"StructuredDetector\" xpixels=\""+str(w)+"\" ypixels=\""+str(h)+"\" type=\"pixel\">\n")
				
				zarr = []
				xarr = []
				yarr = []
				
				for vert in det.findall(self.ns+"vertex"):
					z = 0
					x = vert.get("x")
					y = vert.get("y")
					
					offfile.write("#\t<vertex x=\""+str(x)+"\" y=\""+str(y)+"\" />\n")
					zarr.append(z)
					yarr.append(y)
					xarr.append(x)
				
				offfile.write(str((w+1)*(h+1))+" "+str(w*h)+" 0\n")
				for i, x in enumerate(xarr):
					offfile.write(str(x)+" "+str(yarr[i])+" "+str(zarr[i])+"\n")
				
				for i in xrange(h):
					for j in xrange(w):
						offfile.write("4 "+str((i*w)+j)+" "+str((i*w)+j+1)+" "+str((i*w)+j+w)+" "+str((i*w)+j+w+1)+"\n")
					
	def __write_instr_header(self, f):
		f.write(
		"/*******************************************************************************\n"
		"*\n"
		"* McStas, neutron ray-tracing package\n"
		"*         Copyright (C) 1997-2008, All rights reserved\n"
		"*         Risoe National Laboratory, Roskilde, Denmark\n"
		"*         Institut Laue Langevin, Grenoble, France\n"
		"*\n"
		"* Instrument: templateSANS\n"
		"*\n"
		"* %Identification\n"
		"* Written by: <a href=\"mailto:kim.lefmann@risoe.dk\">Kim Lefmann</a>\n"
		"* Date: 19th Dec 2003.\n"
		"* Origin: <a href=\"http://www.risoe.dk\">Risoe</a>\n"
		"* Release: McStas CVS_080624\n"
		"* Version: $Revision: 1.6 $\n"
		"* %INSTRUMENT_SITE: Templates\n"
		"*\n"
		"* Test instrument for the Sans_spheres component. No guide / velocity selector\n"
		"* etc. Will be developed further at later time.\n"
		"*\n"
		"* %Description\n"
		"* Very simple test instrument for the Sans_spheres component\n"
		"*\n"
		"* Modified to show a proof of concept method for storing a 'Mantid friendly' type of NeXus file.\n"
		"*\n"
		"* Needed steps:\n"
		"* 1) Compile your instrument with NeXus library support\n"
		"* 2) Generate an IDF using mcdisplay templateSANS_Mantid --format=Mantid -n0\n"
		"* 3) mcrun templateSANS_Mantid -n1e6 --format=NeXus\n"
		"*\n"
		"* %Example: lambda=6 Detector: detector_I=6.55e-17\n"
		"*\n"
		"* %Parameters\n"
		"* INPUT PARAMETERS:\n"
		"* lambda:    Mean wavelength of neutrons      [AA]\n"
		"* dlambda:   Wavelength spread of neutrons    [AA]\n"
		"* r:         Radius of scattering hard spheres [AA]\n"
		"* PHI:       Particle volume fraction [1]\n"
		"* Delta_Rho: Excess scattering length density (fm/AA^3)\n"
		"* sigma_abs: Absorption cross section at 2200 m/s [barns]\n"
		"* Qmax:      Maximum momentum transfer [AA^-1]\n"
		"*\n"
		"* %Link\n"
		"* *\n"
		"* %End\n"
		"*******************************************************************************/\n\n")
		
	def outputINSTR(self):
		isOffFile = True
		
		try:
			offfile = open(self.off, "r")
		except:
			isOffFile = False
			
		if self.instr is not None:
			with open(self.instr, "w") as instfile:
				self.__write_instr_header(instfile)
				instfile.write(
				"DEFINE INSTRUMENT templateSANS_Mantid"
					"(lambda=6, dlambda=0.05, r=100, PHI=1e-3, "
					"Delta_Rho=0.6, sigma_abs=0.0, string offfile=\""+self.off+"\",ROTz=0)\n"
					
				"DEPENDENCY \"-DUSE_NEXUS -lNeXus\"\n\n"
				
				"DECLARE %{\n%}\n\n"
				"INITIALIZE %{\n%}\n\n"

				"TRACE\n\n"

				"COMPONENT a1 = Progress_bar()\n\tAT (0,0,0) ABSOLUTE\n\n"

				"COMPONENT arm = Arm()\n\tAT (0, 0, 0) ABSOLUTE\n\n"

				"COMPONENT sourceMantid = Source_simple(\n"
					"\t\tradius = 0.02, dist = 3, focus_xw = 0.01, focus_yh = 0.01,\n"
					"\t\tlambda0 = lambda, dlambda = dlambda, flux = 1e8)\n"
				  "\tAT (0, 0, 0) RELATIVE arm\n\n"

				"COMPONENT coll1 = Slit(\n\t\tradius = 0.005)\n"
				  "\tAT (0, 0, 3) RELATIVE arm\n\n"

				"COMPONENT coll2 = Slit(\n\t\tradius = 0.005)\n"
				  "\tAT (0, 0, 6) RELATIVE arm\n\n"


				"COMPONENT LdetectorSample = L_monitor(\n"
					"\t\tnL = 1000, filename = \"EdetSample.dat\", xmin = -0.3,\n"
					"\t\txmax = 0.3, ymin = -0.3, ymax = 0.3, Lmin = 5.5,\n"
					"\t\tLmax = 6.5)\n"
				   "\tAT (0,0,0.01) RELATIVE coll2\n\n"
				
				"// SASVIEW scatterin kernel\n"
				"SPLIT 10 COMPONENT sampleMantid "
					"= SasView_model(model_index=10, model_scale=1, "
					"model_pars={ 4, 1, 200, 100, 60, 60 }, "
				 "\n\t\tmodel_abs=0.0, "
				  "\n\t\txwidth=0.01, yheight=0.01, zdepth=0.005, "
				  "focus_xw=1.5, focus_yh=1.5, target_index=1)\n"
					"\tAT (0,0,0.2) RELATIVE coll2\n" 
				 "EXTEND %{\n\tif (!SCATTERED) ABSORB;\n%}\n\n\n"


				"COMPONENT detector = PSD_monitor(\n"
					"\t\tnx = 128, ny = 128, filename = \"PSD.dat\", xmin = -0.9,\n"
					"\t\txmax = 0.9, ymin = -0.9, ymax = 0.9)\n"
				  "\t\tAT (0, 0, 3) RELATIVE sampleMantid\n\n" 

				"COMPONENT Ldetector = L_monitor(\n"
					"\t\tnL = 1000, filename = \"Edet.dat\", xmin = -0.3,\n"
					"\t\txmax = 0.3, ymin = -0.3, ymax = 0.3, Lmin = 5.5,\n"
					"\t\tLmax = 6.5)\n"
				  "\tAT (0, 0, 3.01) RELATIVE sampleMantid\n\n"
					 
				"COMPONENT PSDrad = PSD_monitor_rad(\n"
					"\t\tfilename = \"psd2.dat\", filename_av = \"psd2_av.dat\", rmax = 0.3)\n"
				  "\tAT (0, 0, 3.02) RELATIVE sampleMantid\n\n"

				"COMPONENT Det_Arm0 = Arm()\n"
				  "\tAT (0, 0, 3.03) RELATIVE sampleMantid\n\n")

				for i in xrange(7):
					instfile.write(
					"COMPONENT Det_Arm"+str(i+1)+" = Arm()\n"
					  "\tAT (0, 0, 0) RELATIVE PREVIOUS\n"
					  "\tROTATED (0,0,"+str((i+1)*45)+") RELATIVE sampleMantid\n\n")

				instfile.write(
				"COMPONENT nD_Mantid_0 = Monitor_nD(options "
				"=\"mantid x, y, neutron pixel min=1000 t list all neutrons\",\n"
				"\t\tgeometry=offfile,\n"
				"\t\trestore_neutron = 1,\n"
				"\t\t//xwidth=0.3,\n"
				"\t\tfilename = \"bank00_events.dat\")\n"
				"\tAT (0.0, 0, 0) RELATIVE Det_Arm0\n\n") 

				for i in xrange(7):
					id = i+1
					instfile.write(
					"COMPONENT nD_Mantid_"+str(id)+" = COPY(PREVIOUS)(options "
					"=\"mantid x, y, neutron pixel min="+str(id*10000)+" t list all neutrons\","
					"filename = \"bank01_events.dat\")\n"
					 "\tAT (0.0, 0, 0.0) RELATIVE Det_Arm"+str(id)+"\n\n")

				instfile.write("END")
		
if __name__ == "__main__":
	parser = IDFParser("LOKI_definition.xml", "LOKI_Definition.off", "templateSANS_Mantid.instr")
	parser.outputOFF()
	parser.outputINSTR()