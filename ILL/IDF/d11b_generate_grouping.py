#!/usr/bin/python

header = '<?xml version="1.0" encoding="utf-8"?>\n<detector-grouping instrument="D11B">\n'
footer = '</detector-grouping>'
template = '\t<group name="tube_{0}"> \n\t\t <detids val="{1}-{2}"/> \n\t </group>\n'
template_2 = '\t<group name="tube_{0}"> \n\t\t <detids val="{1}"/> \n\t </group>\n'
pixels_per_tube = 256
n_tubes_panels = 32
n_tubes_center = 128
center_start = 0
left_start = n_tubes_center*pixels_per_tube
right_start = (n_tubes_center+n_tubes_panels)*pixels_per_tube

out = header

# center
for i in range(n_tubes_center):
    ids = center_start + i
    id_str = str(ids)
    for p in range(1, pixels_per_tube):
        next = ids + p * n_tubes_center
        id_str += ',' + str(next)
    out += template_2.format('center_'+str(i), id_str)

# left
for i in range(n_tubes_panels):
    start = left_start + i * pixels_per_tube
    end = start + pixels_per_tube - 1
    out += template.format('left_'+str(i), start, end)

# right
for i in range(n_tubes_panels):
    start = right_start + i * pixels_per_tube
    end = start + pixels_per_tube - 1
    out += template.format('right_'+str(i), start, end)

out += footer

print(out)
