#!/usr/bin/env python

from helper import INCH_TO_METRE, MantidGeom
from lxml import etree as le # python-lxml on rpm based systems

def makeLoc(instr, det, name, x, y, z, rot, rot_inner=None, rot_innermost=None):
    sub = instr.addLocation(det, x=x, y=y, z=z, rot_y=rot, name=name)
    if rot_inner is not None:
        sub = le.SubElement(sub, "rot", **{"val":str(rot_inner)})
        if rot_innermost is not None:
            le.SubElement(sub, "rot", **{"val":str(rot_innermost), "axis-x":"0", "axis-y":"1", "axis-z":"0"})

def makeAttrs(idstart):
    """Return list of pixel ids appropriate for rectangular detectors."""
    return {"idstart":idstart, "idfillbyfirst":"y", "idstepbyrow":128}

def makeIds(numBanks, offset, size):
    ids = []
    for i in range(numBanks):
        ids.extend((i*size+offset, (i+1)*size+offset-1, None))
    return ids

if __name__ == "__main__":
    inst_name = "NOMAD"
    xml_outfile = inst_name+"_Definition.xml"

    # boiler plate stuff
    instr = MantidGeom(inst_name, comment=" Created by Peter Peterson ", valid_from="2012-08-01 00:00:01")
    instr.addComment("DEFAULTS")
    instr.addSnsDefaults()
    instr.addComment("SOURCE")
    instr.addModerator(-19.49958)
    instr.addComment("SAMPLE")
    instr.addSamplePosition()

    # monitors
    instr.addComment("MONITORS")
    instr.addMonitors([-0.879475,5.748782], ["monitor1", "monitor2"])

    # add the empty components
    for i in range(1,7):
        name = "Group%d" % i
        instr.addComponent(name, idlist=name)

    # add the id lists for groups
    info = instr.addDetectorIds("Group1", makeIds(14,     0, 8*128))
    info = instr.addDetectorIds("Group2", makeIds(23, 14336, 8*128))
    info = instr.addDetectorIds("Group3", makeIds(14, 37888, 8*128))
    info = instr.addDetectorIds("Group4", makeIds(12, 52224, 8*128))
    info = instr.addDetectorIds("Group5", makeIds(18, 64512, 8*128))
    info = instr.addDetectorIds("Group6", makeIds(18, 82944, 8*128))

    # ---------- add in group1
    group1 = instr.makeTypeElement("Group1")
    z = .5*((6.41/8.45*3.2) + (3.86/8.45*3.2))# 1.940845
    det = instr.makeDetectorElement("one_inch", root=group1)
    makeLoc(instr, det, "bank1",
            x=-0.0900835, y=-0.50034125, z=z, rot=-89.3663312,
            rot_inner=92.7740541972, rot_innermost=102.872503501)
    det = instr.makeDetectorElement("one_inch", root=group1)
    makeLoc(instr, det, "bank2",
            x=-0.29825225, y=-0.41170625, z=z, rot=-88.2250765278,
            rot_inner=92.2242357116, rot_innermost=128.605560457)
    det = instr.makeDetectorElement("one_inch", root=group1)
    makeLoc(instr, det, "bank3",
            x=-0.44734875, y=-0.241528, z=z, rot=-87.4360086541,
            rot_inner=91.2341549097, rot_innermost=154.31324826)
    det = instr.makeDetectorElement("one_inch", root=group1)
    makeLoc(instr, det, "bank4",
            x=-0.507842, y=-0.023511625, z=z, rot=-87.1545655812,
            rot_inner=90.0, rot_innermost=180.0)
    det = instr.makeDetectorElement("one_inch", root=group1)
    makeLoc(instr, det, "bank5",
            x=-0.4677515, y=0.199161, z=z, rot=-87.4360162435,
            rot_inner=88.7658487398, rot_innermost=-154.313248163)
    det = instr.makeDetectorElement("one_inch", root=group1)
    makeLoc(instr, det, "bank6",
            x=-0.33501675, y=0.382388, z=z, rot=-88.2250361723,
            rot_inner=87.7757484484, rot_innermost=-128.605997196)
    det = instr.makeDetectorElement("one_inch", root=group1)
    makeLoc(instr, det, "bank7",
            x=-0.135927725, y=0.4898775, z=z, rot=-89.3663380315,
            rot_inner=87.2259863472, rot_innermost=-102.872551406)
    det = instr.makeDetectorElement("one_inch", root=group1)
    makeLoc(instr, det, "bank8",
            x=0.0900835227694, y=0.50034125, z=z, rot=-90.6336689203,
            rot_inner=87.2259458689, rot_innermost=-77.1274935015)
    det = instr.makeDetectorElement("one_inch", root=group1)
    makeLoc(instr, det, "bank9",
            x=0.29825225, y=0.41170625, z=z, rot=-91.7749234722,
            rot_inner=87.7757642884, rot_innermost=-51.3944395427)
    det = instr.makeDetectorElement("one_inch", root=group1)
    makeLoc(instr, det, "bank10",
            x=0.44734875, y=0.241528, z=z, rot=-92.5639913459,
            rot_inner=88.7658450903, rot_innermost=-25.686751674)
    det = instr.makeDetectorElement("one_inch", root=group1)
    makeLoc(instr, det, "bank11",
            x=0.507842, y=0.023511625, z=z, rot=-92.8454344188,
            rot_inner=90.0)
    det = instr.makeDetectorElement("one_inch", root=group1)
    makeLoc(instr, det, "bank12",
            x=0.46775125, y=-0.199161, z=z, rot=-92.5639926177,
            rot_inner=91.2341401341, rot_innermost=25.6864726524)
    det = instr.makeDetectorElement("one_inch", root=group1)
    makeLoc(instr, det, "bank13",
            x=0.33501675, y=-0.382388, z=z, rot=-91.7749638277,
            rot_inner=92.2242515516, rot_innermost=51.3940028045)
    det = instr.makeDetectorElement("one_inch", root=group1)
    makeLoc(instr, det, "bank14",
            x=0.1359277, y=-0.4898775, z=z, rot=-90.6336619129,
            rot_inner=92.774014947, rot_innermost=77.1274554878)

    # ---------- add in group2
    group2 = instr.makeTypeElement("Group2")
    z = .5*((5.09/7.06*2.7-0.0095) + (2.45/7.06*2.7+0.0095)) # 1.445654
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank15",
            x=-0.0915395, y=-0.836427, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=97.8262008026)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank16",
            x=-0.31381, y=-0.780713, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=113.478192701)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank17",
            x=-0.512807, y=-0.6670965, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=129.130313954)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank18",
            x=-0.6737715, y=-0.504005, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=144.78248153)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank19",
            x=-0.784765, y=-0.303534, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=160.434729108)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank20",
            x=-0.8375565, y=-0.08055513, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=176.087022238)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank21",
            x=-0.82823, y=0.14840565, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=-168.261070831)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank22",
            x=-0.757478, y=0.3663565, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=-152.608674007)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank23",
            x=-0.6305465, y=0.557136, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=-136.95660485)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank24",
            x=-0.4568505, y=0.7065955, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=-121.304270268)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank25",
            x=-0.2492725, y=0.8036495, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=-105.652349705)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank26",
            x=-0.0232068, y=0.841101, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=-90.0)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank27",
            x=0.20458, y=0.8161715, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=-74.3477339442)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank28",
            x=0.4171945, y=0.7307105, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=-58.695729732)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank29",
            x=0.598867, y=0.5910565, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=-43.0434101201)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank30",
            x=0.736125, y=0.4075655, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=-27.3913259927)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank31",
            x=0.818787, y=0.1938458, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=-11.7389102452)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank32",
            x=0.8407235, y=-0.0342456, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=3.91299045695)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank33",
            x=0.800308, y=-0.259801, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=19.5652708918)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank34",
            x=0.700537, y=-0.466087, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=35.2172651748)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank35",
            x=0.54881, y=-0.6378065, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=50.8696860457)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank36",
            x=0.356381, y=-0.7622215, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=66.5215229238)
    det = instr.makeDetectorElement("one_inch", root=group2)
    makeLoc(instr, det, "bank37",
            x=0.1375204, y=-0.830107, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=82.173807641)

    # ---------- add in group3
    group3 = instr.makeTypeElement("Group3")
    z = .5*((2.59/7.06*2.7-0.0076) + (-0.04/7.06*2.7+.0076)) # 0.48373677
    det = instr.makeDetectorElement("one_inch", root=group3)
    makeLoc(instr, det, "bank38",
            x=-0.7475175, y=-0.6555715, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=139.65505902)
    det = instr.makeDetectorElement("one_inch", root=group3)
    makeLoc(instr, det, "bank39",
            x=-0.87097, y=-0.4795505, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=152.068928854)
    det = instr.makeDetectorElement("one_inch", root=group3)
    makeLoc(instr, det, "bank40",
            x=-0.9536965, y=-0.281106, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=164.482826207)
    det = instr.makeDetectorElement("one_inch", root=group3)
    makeLoc(instr, det, "bank41",
            x=-0.991829, y=-0.0695175, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=176.896821582)
    det = instr.makeDetectorElement("one_inch", root=group3)
    makeLoc(instr, det, "bank42",
            x=-0.9835845, y=0.145322, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=-170.68977393)
    det = instr.makeDetectorElement("one_inch", root=group3)
    makeLoc(instr, det, "bank43",
            x=-0.929359, y=0.3533655, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=-158.275738743)
    det = instr.makeDetectorElement("one_inch", root=group3)
    makeLoc(instr, det, "bank44",
            x=-0.8316585, y=0.544887, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=-145.862002566)
    det = instr.makeDetectorElement("one_inch", root=group3)
    makeLoc(instr, det, "bank45",
            x=0.814016, y=0.570975, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=-34.1380800603)
    det = instr.makeDetectorElement("one_inch", root=group3)
    makeLoc(instr, det, "bank46",
            x=0.917713, y=0.3825705, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=-21.7242612566)
    det = instr.makeDetectorElement("one_inch", root=group3)
    makeLoc(instr, det, "bank47",
            x=0.9784985, y=0.17634535, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=-9.31026118073)
    det = instr.makeDetectorElement("one_inch", root=group3)
    makeLoc(instr, det, "bank48",
            x=0.993531, y=-0.0381263, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=3.10317170469)
    det = instr.makeDetectorElement("one_inch", root=group3)
    makeLoc(instr, det, "bank49",
            x=0.9621065, y=-0.250814, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=15.5171737927)
    det = instr.makeDetectorElement("one_inch", root=group3)
    makeLoc(instr, det, "bank50",
            x=0.885696, y=-0.451775, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=27.9309259204)
    det = instr.makeDetectorElement("one_inch", root=group3)
    makeLoc(instr, det, "bank51",
            x=0.7678705, y=-0.631611, z=z, rot=-90.0,
            rot_inner=90.0, rot_innermost=40.3447402631)

    # ---------- add in group4
    group4 = instr.makeTypeElement("Group4")
    z = .5*((-.28/7.06*2.7+.0016) + (-2.79/7.06*2.7-.0016)) # -0.590803
    det = instr.makeDetectorElement("one_inch", root=group4)
    makeLoc(instr, det, "bank52",
            x=-0.71647125, y=-0.5438845, z=z, rot=-100.380800509,
            rot_inner=82.7514091291, rot_innermost=145.442056102)
    det = instr.makeDetectorElement("one_inch", root=group4)
    makeLoc(instr, det, "bank53",
            x=-0.8366405, y=-0.330414, z=z, rot=-101.93010022,
            rot_inner=85.7981490801, rot_innermost=160.873964923)
    det = instr.makeDetectorElement("one_inch", root=group4)
    makeLoc(instr, det, "bank54",
            x=-0.89476125, y=-0.0924384, z=z, rot=-102.609961197,
            rot_inner=89.1442736336, rot_innermost=176.180633801)
    det = instr.makeDetectorElement("one_inch", root=group4)
    makeLoc(instr, det, "bank55",
            x=-0.88651975, y=0.152392725, z=z, rot=-102.382153342,
            rot_inner=92.5513960694, rot_innermost=-168.537574441)
    det = instr.makeDetectorElement("one_inch", root=group4)
    makeLoc(instr, det, "bank56",
            x=-0.81253, y=0.38592175, z=z, rot=-101.259734987,
            rot_inner=95.7771900875, rot_innermost=-153.178651419)
    det = instr.makeDetectorElement("one_inch", root=group4)
    makeLoc(instr, det, "bank57",
            x=-0.6782785, y=0.590829, z=z, rot=-99.3065608131,
            rot_inner=98.5886817118, rot_innermost=-137.656749509)
    det = instr.makeDetectorElement("one_inch", root=group4)
    makeLoc(instr, det, "bank58",
            x=0.63573875, y=0.636378, z=z, rot=-80.693405525,
            rot_inner=98.5885823254, rot_innermost=-42.3428178708)
    det = instr.makeDetectorElement("one_inch", root=group4)
    makeLoc(instr, det, "bank59",
            x=0.7838565, y=0.44125875, z=z, rot=-78.7402567115,
            rot_inner=95.7771942637, rot_innermost=-26.8213477452)
    det = instr.makeDetectorElement("one_inch", root=group4)
    makeLoc(instr, det, "bank60",
            x=0.8738395, y=0.213413675, z=z, rot=-77.6177951612,
            rot_inner=92.5514008681, rot_innermost=-11.4623986459)
    det = instr.makeDetectorElement("one_inch", root=group4)
    makeLoc(instr, det, "bank61",
            x=0.89901375, y=-0.030258525, z=z, rot=-77.3901270893,
            rot_inner=89.1445508423, rot_innermost=3.81816021827)
    det = instr.makeDetectorElement("one_inch", root=group4)
    makeLoc(instr, det, "bank62",
            x=0.857512, y=-0.271688, z=z, rot=-78.0699239299,
            rot_inner=85.7981574327, rot_innermost=19.1260368466)
    det = instr.makeDetectorElement("one_inch", root=group4)
    makeLoc(instr, det, "bank63",
            x=0.7524125, y=-0.492967, z=z, rot=-79.6191744094,
            rot_inner=82.7513919919, rot_innermost=34.5579407336)

    # ---------- add in group5
    group5 = instr.makeTypeElement("Group5")
    y = 0. # 0.003906
    z = -1.78/8.45*3.2 # -0.687783
    det = instr.makeDetectorElement("half_inch_back", root=group5)
    makeLoc(instr, det, "bank64",
            x=-0.503307, y=y, z=z, rot=180.0)
    det = instr.makeDetectorElement("half_inch_back", root=group5)
    makeLoc(instr, det, "bank65",
            x=-0.448507, y=y, z=z, rot=180.0)
    det = instr.makeDetectorElement("half_inch_back", root=group5)
    makeLoc(instr, det, "bank66",
            x=-0.393707, y=y, z=z, rot=180.0)
    det = instr.makeDetectorElement("half_inch_back", root=group5)
    makeLoc(instr, det, "bank67",
            x=-0.338907, y=y, z=z, rot=180.0)
    det = instr.makeDetectorElement("half_inch_back", root=group5)
    makeLoc(instr, det, "bank68",
            x=-0.284107, y=y, z=z, rot=180.0)
    det = instr.makeDetectorElement("half_inch_back", root=group5)
    makeLoc(instr, det, "bank69",
            x=-0.229307, y=y, z=z, rot=180.0)
    det = instr.makeDetectorElement("half_inch_back", root=group5)
    makeLoc(instr, det, "bank70",
            x=-0.174507, y=y, z=z, rot=180.0)
    det = instr.makeDetectorElement("half_inch_back", root=group5)
    makeLoc(instr, det, "bank71",
            x=-0.11970685, y=y, z=z, rot=180.0)
    det = instr.makeDetectorElement("half_inch_back", root=group5)
    makeLoc(instr, det, "bank72",
            x=-0.0649067, y=y, z=z, rot=180.0)
    det = instr.makeDetectorElement("half_inch_back", root=group5)
    makeLoc(instr, det, "bank73",
            x=0.044693295, y=y, z=z, rot=180.0)
    det = instr.makeDetectorElement("half_inch_back", root=group5)
    makeLoc(instr, det, "bank74",
            x=0.0994933, y=y, z=z, rot=180.0)
    det = instr.makeDetectorElement("half_inch_back", root=group5)
    makeLoc(instr, det, "bank75",
            x=0.154293, y=y, z=z, rot=180.0)
    det = instr.makeDetectorElement("half_inch_back", root=group5)
    makeLoc(instr, det, "bank76",
            x=0.209093, y=y, z=z, rot=180.0)
    det = instr.makeDetectorElement("half_inch_back", root=group5)
    makeLoc(instr, det, "bank77",
            x=0.263893, y=y, z=z, rot=180.0)
    det = instr.makeDetectorElement("half_inch_back", root=group5)
    makeLoc(instr, det, "bank78",
            x=0.318693, y=y, z=z, rot=180.0)
    det = instr.makeDetectorElement("half_inch_back", root=group5)
    makeLoc(instr, det, "bank79",
            x=0.373493, y=y, z=z, rot=180.0)
    det = instr.makeDetectorElement("half_inch_back", root=group5)
    makeLoc(instr, det, "bank80",
            x=0.428293, y=y, z=z, rot=180.0)
    det = instr.makeDetectorElement("half_inch_back", root=group5)
    makeLoc(instr, det, "bank81",
            x=0.483093, y=y, z=z, rot=180.0)

    # ---------- add in group6
    group6 = instr.makeTypeElement("Group6")
    y = 0.0078125 # 0. # 0.003906
    z = 6.69/8.45*3.2 # 2.51979
    rot = 180.0
    names = ["bank%d" % i for i in range(82,100)]
    x = [-0.5457338, -0.4909338, -0.4361338, -0.381338, -0.3265338, -0.2717338,
         -0.2169338, -0.16213365, -0.1073334, 0.07197215, 0.12677215, 0.1815723,
         0.2363718, 0.2911718, 0.3459718, 0.4007718, 0.4555718, 0.5103718]
    def tubeX(ntube):
        return 1.34/8.45*3.2 - (.0254/2+.001)/2*(ntube+32) + .062 +0.13951937869822478 # +.06
    x2 = []
    for i in range(len(names)):
        x2.append((tubeX(i*8+0) + tubeX(i*8+7))*.5)
    x2.reverse()
    print x2
    for name, x in zip(names, x2):
        det = instr.makeDetectorElement("half_inch", root=group6)
        makeLoc(instr, det, name,
                x=x, y=y, z=z, rot=rot)

    # ---------- detector panels

    instr.addComment("New Detector Panel (128x8) - one_inch")
    det = instr.makeTypeElement("one_inch")
    le.SubElement(det, "properties")
    det = instr.addComponent("tube", root=det, blank_location=False)
    xstep = (-0.0254*5.5/5.) # tubes are at 5.5inches for 6 tubes on centre OLD=-0.0264
    xstart = -8.*.5*xstep + .5*xstep # OLD=0.0924
    for j in range(8):
        name="tube%d"  % (j+1)
        x = float(j)*xstep + xstart
        #if j == 0 or j == 7:
        #    print j, x
        instr.addLocation(det, x, 0., 0., name=name)

    instr.addComment("New Detector Panel (128x8) - half_inch")
    det = instr.makeTypeElement("half_inch")
    le.SubElement(det, "properties")
    det = instr.addComponent("halftube", root=det, blank_location=False)
    xstep = 0.00685
    xstart = -.5*8.*xstep + .5*xstep # OLD=-0.0924
    for j in range(8):
        name="halftube%d"  % (j+1)
        x = float(j)*xstep + xstart
        #if j == 0 or j == 7:
        #    print j, x
        z = -1.* float((j + 1)% 2) * (.0254/2+.001) 
        instr.addLocation(det, x, 0., z, name=name)

    instr.addComment("New Detector Panel (128x8) - half_inch_back")
    det = instr.makeTypeElement("half_inch_back")
    le.SubElement(det, "properties")
    det = instr.addComponent("halftube", root=det, blank_location=False)
    xstep = -0.00685
    xstart = -.5*8.*xstep + .5*xstep # OLD=0.023975
    for j in range(8):
        name="halftube_back%d"  % (j+1)
        x = float(j)*xstep + xstart
        #if j == 0 or j == 7:
        #    print j, x
        z = -1.* float(j % 2) * (.0254/2+.001) 
        instr.addLocation(det, x, 0., z, name=name)

    # ---------- monitors

    instr.addComment("Shape for monitors")
    instr.addComment("TODO: Update to real shape")
    instr.addDummyMonitor(0.01, .03)

    # ---------- detector tubes
    ypixels = 128
    ystep = 1./128. # 1m tubes
    ystart = -.5-.5*ystep

    instr.addComment(" 1m 128 pixel half inch tube ")
    tube = instr.makeTypeElement("halftube", {"outline":"yes"})
    le.SubElement(tube, "properties")
    tube = instr.addComponent("halfpixel", root=tube, blank_location=False)
    for i in range(ypixels):
        name = "pixel%d" % (i+1)
        y = float(i)*ystep + ystart
        #if i == 0 or i == 127:
        #    print y
        instr.addLocation(tube, 0., y, 0., name=name)

    ystep = -1./128. # pixels go in the other direction
    ystart = .5+.5*ystep
    instr.addComment(" 1m 128 pixel inch tube ")
    tube = instr.makeTypeElement("tube", {"outline":"yes"})
    le.SubElement(tube, "properties")
    tube = instr.addComponent("onepixel", root=tube, blank_location=False)
    for i in range(ypixels):
        name = "pixel%d" % (i+1)
        y = float(i)*ystep + ystart
        #if i == 0 or i == 127:
        #    print y
        instr.addLocation(tube, 0., y, 0., name=name)

    instr.addComment("Shape for half inch tube pixels")
    instr.addCylinderPixel("halfpixel", # 1 metre long 1/2 inch tube
                           (0.,0.,0.), (0.,1.,0.), .25*.0254, 1./128.)

    instr.addComment("Shape for inch tube pixels")
    instr.addCylinderPixel("onepixel", # 1 metre long 1 inch tube
                           (0.,0.,0.), (0.,1.,0.), .5*.0254, 1./128.)

    # monitor ids
    instr.addComment("MONITOR IDS")
    instr.addMonitorIds([-1,-2])

    # write out the file
    instr.writeGeom(xml_outfile)
    #instr.showGeom()
