# MultiGrid

Please beware, you may need to change the hard-coded file paths for the following files:
* MultiGridCSV_RunInMantid.py
* MultiGridVTUGenerator_RunInParaview.py


### Instructions for Loading CSPEC Demo in Mantid/Paraview (7 - 9 optional): 
1. Run cncs_CreateLUT.py
2. Run cncs_Histogram.py
3. Launch MantidPlot and open the script editor.
4. Open MultiGridCSV_RunInMantid.py. This should output MultiGridData.csv needed for the next step
5. Launch Paraview and go to Tools->Python Shell to launch the python shell
6. In the python shell window select Run Script and open the MultiGridVTUGenerator_RunInParaview.py.
7. The ColdFire.xml file is a paraview colormap file which is the same as the default map in Mantid. 
8. In Paraview got to View->ColorMapEditor and then click choose preset icon to the right of color graph.
9. Click import in the popup box and select ColdFire.xml.


### Instructions for Loading full CSPEC Geometry.
1. Run GenerateCSPEC.py. This should output cspec.xml
2. Launch MantidPlot.
3. In the Algorithm widget, type LoadEmptyInstrument
4. Select the cspec.xml file. Get a cup of coffee.
5. When the file is loaded right-click the output workspace and select ShowInstrument.
6. You can leave that running overnight.