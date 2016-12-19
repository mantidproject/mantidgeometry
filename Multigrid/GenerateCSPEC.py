import math
import numpy as np

class GenerateCSPECIDF:
	_grid_x_width = 0.02 #metres
	_grid_z_depth = 0.01 #metres
	_columns = 100
	
	def __init__(self, Filename, FlightPath = 3.0, ThetaMin=5.0, ThetaMax=140.0, NumCols=100, ColHeight = 4.0, GridsPerCol=128, VoxelsX=4, VoxelsZ=16):
		self.filename = Filename
		self.fileHandle = None
		self.flightPath = float(FlightPath) #metres
		self.thetamin = float(ThetaMin) #degrees
		self.thetamax = float(ThetaMax) #degrees
		self.numCols = int(NumCols)
		self.colheight = float(ColHeight) #metres
		self.gridsPerCol = int(GridsPerCol)
		self.voxelsx = int(VoxelsX)
		self.voxelsz = int(VoxelsZ)
		
	def _open_file(self):
		self.fileHandle = open(self.filename, "w")
		
	def _close_file(self):
		self.fileHandle.close()
		
	def _write_header_and_defaults(self):
		self.fileHandle.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
		self.fileHandle.write("<instrument xmlns=\"http://www.mantidproject.org/IDF/1.0\"\n" 
						"xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n"
						"xsi:schemaLocation=\"http://www.mantidproject.org/IDF/1.0/IDFSchema.xsd\"\n"
						"name=\"VoxelDetector\" valid-from   =\"2015-11-01 00:00:01\"\n"
						"valid-to     =\"2100-12-31 23:59:59\"\n"
						"last-modified=\"2015-11-05 12:00:00\">\n\n")

		self.fileHandle.write("<defaults>\n")
		self.fileHandle.write("<length unit=\"meter\"/>\n")
		self.fileHandle.write("<angle unit=\"degree\"/>\n")
		self.fileHandle.write("<location r=\"0.0\" t=\"0.0\" p=\"0.0\" ang=\"0.0\" axis-x=\"0.0\" axis-y=\"0.0\" axis-z=\"1.0\"/>\n")
		self.fileHandle.write("<reference-frame>\n")
		self.fileHandle.write("<!-- The z-axis is set parallel to and in the direction of the beam. the"
						"y-axis points up and the coordinate system is right handed. -->\n")
		self.fileHandle.write("<along-beam axis=\"z\"/>\n")
		self.fileHandle.write("<pointing-up axis=\"y\"/>\n")
		self.fileHandle.write("<handedness val=\"right\"/>\n")
		self.fileHandle.write("<origin val=\"beam\" />\n") 
		self.fileHandle.write("</reference-frame>\n")
		self.fileHandle.write("<default-view view=\"cylindrical_y\"/>\n")
		self.fileHandle.write("</defaults>\n\n")
		
	def _write_footer(self):
		self.fileHandle.write("\n</instrument>")
		
	def _write_source(self):
		self.fileHandle.write("<!-- ***** SOURCE ***** -->\n")
		self.fileHandle.write("<component type=\"cold_source\">\n")
		self.fileHandle.write("\t<location z=\"-36.2\">") 
		self.fileHandle.write("<facing val=\"none\"/>") 
		self.fileHandle.write("</location>\n")
		self.fileHandle.write("</component>\n\n")

		self.fileHandle.write("<type name=\"cold_source\" is=\"Source\">\n")
		self.fileHandle.write("\t<properties />\n")
		self.fileHandle.write("\t<cylinder id=\"some-shape\">\n")
		self.fileHandle.write("\t\t<centre-of-bottom-base r=\"0.0\" t=\"0.0\" p=\"0.0\" />\n")
		self.fileHandle.write("\t\t<axis x=\"0.0\" y=\"0.0\" z=\"1.0\" />\n") 
		self.fileHandle.write("\t\t<radius val=\"0.01\" />\n")
		self.fileHandle.write("\t\t<height val=\"0.03\" />\n")
		self.fileHandle.write("\t</cylinder>\n") 
		self.fileHandle.write("\t<algebra val=\"some-shape\" />\n")
		self.fileHandle.write("</type>\n\n")
		
	def _write_sample(self):
		self.fileHandle.write("<!-- ***** SAMPLE POSITION ***** -->\n")
		self.fileHandle.write("<component type=\"sample_position\">\n")
		self.fileHandle.write("\t<location>") 
		self.fileHandle.write("<facing val=\"none\"/>") 
		self.fileHandle.write("</location>\n")
		self.fileHandle.write("</component>\n\n")

		self.fileHandle.write("<type name=\"sample_position\" is=\"SamplePos\">\n")
		self.fileHandle.write("\t<properties />\n")
		self.fileHandle.write("\t<sphere id=\"some-shape\">\n")
		self.fileHandle.write("\t\t<centre x=\"0.0\"  y=\"0.0\" z=\"0.0\" />\n")
		self.fileHandle.write("\t\t<radius val=\"0.03\" />\n")
		self.fileHandle.write("\t</sphere>\n")
		self.fileHandle.write("\t<algebra val=\"some-shape\" />\n")
		self.fileHandle.write("</type>\n\n")
	
	def _write_grid_module(self):
		self.fileHandle.write("<type name=\"Grid_module\">\n")
		self.fileHandle.write("\t<component type=\"Grid_layer\" outline=\"yes\">\n")
		
		xmin = 0
		xmax = self._grid_x_width * self.voxelsx
		
		for i, x in enumerate(np.arange(xmin, xmax, self._grid_x_width, dtype=float)):
			self.fileHandle.write("\t\t<location  x=\""+str(x)+"\" y=\"0\" name=\"Segment"+str(i+1)+"\" />\n")

		self.fileHandle.write("\t</component>\n")
		self.fileHandle.write("</type>\n\n")
		
	def _write_grid_layer(self):
		self.fileHandle.write("<type name=\"Grid_layer\" outline=\"yes\">\n")
		self.fileHandle.write("\t<component type=\"Voxel\" >\n")
		self.fileHandle.write("\t\t<locations z=\"0\" z-end=\""+str(self._grid_z_depth * self.voxelsz)+"\" name=\"Voxel_\" n-elements=\"16\" />\n")
		self.fileHandle.write("\t</component>\n")
		self.fileHandle.write("</type>\n\n")
		
	def _write_voxel(self):
		xmin = 0
		ymin = 0
		zmin = 0
		width = self._grid_x_width
		height = self.colheight/self.gridsPerCol
		depth = self._grid_z_depth
		
		self.fileHandle.write("<type name=\"Voxel\" is=\"detector\">\n")
		self.fileHandle.write("\t<cuboid id=\"shape\">\n")
		self.fileHandle.write("\t\t<left-front-bottom-point x=\""+str(xmin)+"\" y=\""+str(ymin)+"\" z=\""+str(zmin)+"\"  />\n")
		self.fileHandle.write("\t\t<left-front-top-point  x=\""+str(xmin)+"\" y=\""+str(ymin+height)+"\" z=\""+str(zmin)+"\"  />\n")
		self.fileHandle.write("\t\t<left-back-bottom-point  x=\""+str(xmin+width)+"\" y=\""+str(ymin)+"\" z=\""+str(zmin)+"\"  />\n")
		self.fileHandle.write("\t\t<right-front-bottom-point  x=\""+str(xmin)+"\" y=\""+str(ymin)+"\" z=\""+str(zmin+depth)+"\"  />\n")
		self.fileHandle.write("\t</cuboid>\n")
		self.fileHandle.write("<algebra val=\"shape\" />\n")
		self.fileHandle.write("</type>\n\n")
		
	def _write_id_list(self, idname, start, end):
		self.fileHandle.write("<idlist idname=\""+idname+"\">\n")
		self.fileHandle.write("<id start=\""+str(start)+"\" end=\""+str(end)+"\" />\n")
		self.fileHandle.write("</idlist>\n")
		
	def _write_all_components(self):
		thetaStep = (self.thetamax - self.thetamin)/ self._columns
		
		theta = self.thetamin
		for i in xrange(self.numCols):
			name = "module_"+str(i+1)
			posX = self.flightPath * math.sin(theta * math.pi/180.0)
			posZ = self.flightPath * math.cos(theta * math.pi/180.0)
			
			self.fileHandle.write("<component type=\"bank\" idlist=\""+name+"\" name=\""+name+"\">\n")
			self.fileHandle.write("\t<location x=\""+str(posX)+"\" y=\"0\" z=\""+str(posZ)+"\"><facing x=\"0.0\"  y=\"0.0\" z=\"0.0\"/></location>\n")
			self.fileHandle.write("</component>\n")
			theta += thetaStep
		self.fileHandle.write("\n")
		
		#need to write components and types separatel
		self._write_module_type()

	def _write_module_type(self):
		self.fileHandle.write("<type name=\"bank\">\n")
		self.fileHandle.write("<component type=\"Grid_module\"  name=\"_Grid_Module\">\n")
		
		hmin = 0;
		hmax = self.colheight
		hstep = self.colheight/self.gridsPerCol
		for h in np.arange(hmin, hmax, hstep, dtype=float):
			self.fileHandle.write("\t<location x=\"0\" y=\""+str(h)+"\" z=\"0\"/>\n")
		self.fileHandle.write("</component>\n")
		self.fileHandle.write("</type>\n\n")
	
	def _write_all_ids(self):
		idSpan = self.voxelsx * self.voxelsz * self.gridsPerCol

		for i in xrange(self.numCols):
			start = (i*idSpan)
			end = start + idSpan-1
			self._write_id_list("module_"+str(i+1), start, end);
			
	def generate(self):
		self._open_file()
		self._write_header_and_defaults()
		self._write_source()
		self._write_sample()
		self._write_all_components()
		self._write_grid_module()
		self._write_grid_layer()
		self._write_voxel()
		self._write_all_ids()
		self._write_footer()
		self._close_file()
		
gen = GenerateCSPECIDF("cspec.xml")
gen.generate()