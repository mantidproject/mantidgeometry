__author__ = 'Stuart Campbell'

inelastic_banklist = [1,2,4,5,7,8,10,11,13,14,16,17,19,20]

bank_mins=[0,1024,4096,5120,8192,9216,12288,13312,16384,17408,20480,21504,24576,25600]

l2 = (259.4 + 259.4) / 1000.0
ef = 12.478

index = 0

for i in inelastic_banklist:

    print "Writing file for Bank #%d" % i

    filename = "VISION_bank%d.dat" % i
    file = open(filename, "w")

    print >> file, "## Bank %s" % i
    print >> file, "# id\tl2\tef"

    for j in range(bank_mins[index],bank_mins[index]+1024):
        print >> file, j, l2, ef

    index += 1
