import xlrd
from numpy import array,zeros, where,greater
from helper import MantidGeom


def read_xls(filename):
  wb=xlrd.open_workbook(filename) 
  sheet=wb.sheet_by_name('S2at0')
  di={}
  di["id"]=range(1,21)
  di["name"]=[]
  for i in di["id"]:
    di["name"].append('bank%d'%int(i))
  di["X"]=array(sheet.col_values(8)[7:28])
  di["Y"]=array(sheet.col_values(9)[7:28])
  di["Z"]=array(sheet.col_values(7)[7:28])
  di["RotX"]=zeros(20)
  psi1=array(sheet.col_values(10)[7:28])
  psi2=array(sheet.col_values(11)[7:28])
  di["RotY"]=180+where(greater(psi2,90),-psi1,psi1)
  di["RotZ"]=zeros(20)
  #individual eightpack info
  sheet=wb.sheet_by_name('8Packs')
  di["NUM_PIXELS_PER_TUBE"]=int(sheet.cell_value(10,5))
  di["NUM_TUBES_PER_BANK"]=int(sheet.cell_value(9,5))
  di["AIR_GAP_WIDTH"]=sheet.cell_value(7,4)*1e-3
  #individual tube info
  di["TUBE_SIZE"]=sheet.cell_value(4,8)*1e-3
  di["TUBE_WIDTH"]=sheet.cell_value(8,4)*1e-3
  di["TUBE_THICKNESS"]=("tube_thickness",sheet.cell_value(7,8)*1e-3,"meter")
  di["TUBE_PRESSURE"]=("tube_pressure",10.0,"atm")
  di["TUBE_TEMPERATURE"]=("tube_temperature",290.0,"K")
  return di
  
if __name__=="__main__":
  filename='SNS/HYSPEC/hyspec_MotorList4GG.xls'
  info=read_xls(filename)
  inst_name="HYSPEC"
  xml_outfile=inst_name+"_Definition.xml"
  det=MantidGeom(inst_name)
  det.addSnsDefaults()
  det.addComment("SOURCE AND SAMPLE POSITION")
  det.addModerator("msd -0.001*msd-38.980")# TODO: change moderator position to read from the excel sheet
  det.addSamplePosition()
  det.addComment("MONITORS")
  det.addMonitors(names=["monitor1", "monitor2", "monitor3"],distance=["msd -0.001*msd-3.340", "msd -0.001*msd-1.59643", "-0.200"])
  # TODO: change monitor positions to read from the excel sheet

  label = "Tank"
  tank=det.addComponent(label, label,blank_location=False)
  det.addLocationRTP(tank,"0","s2 0.0+s2","0","0","s2 0.0+s2","0")
  doc_handle = det.makeTypeElement(label)
  num_dets=len(info["name"])
  for i in range(num_dets):
    det.addComponent(info["name"][i], root=doc_handle)
    det.addDetector(info["X"][i], info["Y"][i], info["Z"][i], 
                    info["RotX"][i], info["RotY"][i], info["RotZ"][i],
                    info["name"][i], "eightpack")

  det.addComment("STANDARD 8-PACK")
  det.addNPack("eightpack", info["NUM_TUBES_PER_BANK"], info["TUBE_WIDTH"], info["AIR_GAP_WIDTH"])

  det.addComment("STANDARD 1.2m 128 PIXEL TUBE")
  det.addPixelatedTube("tube", info["NUM_PIXELS_PER_TUBE"], info["TUBE_SIZE"])
	
  det.addComment("PIXEL FOR STANDARD 1.2m 128 PIXEL TUBE")
  det.addCylinderPixel("pixel", (0.0, 0.0, 0.0), (0.0, 1.0, 0.0),
                       (info["TUBE_WIDTH"]/2.0),
                       (info["TUBE_SIZE"]/info["NUM_PIXELS_PER_TUBE"]))

  det.addComment("MONITOR SHAPE")
  det.addCuboidMonitor(0.0508,0.1651,0.0381)

  det.addComment("DETECTOR IDs")	
  PIXELS_PER_BANK = info["NUM_TUBES_PER_BANK"] * info["NUM_PIXELS_PER_TUBE"]
  det.addDetectorIds(label, [0, (num_dets * PIXELS_PER_BANK) - 1 , None])

  det.addComment("MONITOR IDs")
  det.addMonitorIds(["-1", "-2", "-3"])

  det.addComment("DETECTOR PARAMETERS")
  det.addDetectorParameters(label, info["TUBE_PRESSURE"], info["TUBE_THICKNESS"],
                             info["TUBE_TEMPERATURE"])    
  det.writeGeom(xml_outfile)



