__author__ = 'Stuart Campbell'

import lxml

# Some static information
INSTRUMENT_NAME = "VISION"
INSTRUMENT_SHORT_NAME = "VIS"

def main():

	# Setup some defaults
	xml_filename = INSTRUMENT_NAME+"_Definition.xml"

	print "Generating IDF for %s with name %s" % (INSTRUMENT_NAME,xml_filename)

if __name__ == '__main__':
	main()
