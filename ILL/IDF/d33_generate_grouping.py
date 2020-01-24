#!/usr/bin/python

header = '<?xml version="1.0" encoding="utf-8"?>\n<detector-grouping instrument="D33">\n'
footer = '</detector-grouping>'
template = '\t<group name="tube_{0}"> \n\t\t <detids val="{1}-{2}"/> \n\t </group>\n'
template_2 = '\t<group name="tube_{0}"> \n\t\t <detids val="{1}"/> \n\t </group>\n'
pixels_per_tube = 256
front_right_start = 100000
front_left_start = 200000
front_bottom_start = 300000
front_top_start = 400000
back_start = 0
n_tubes_panels = 32
n_tubes_back = 128

out = header

# front-right
for i in range(n_tubes_panels):
    start = front_right_start + i * pixels_per_tube
    end = start + pixels_per_tube - 1
    out += template.format('front_right_'+str(i), start, end)

# front-left
for i in range(n_tubes_panels):
    start = front_left_start + i * pixels_per_tube
    end = start + pixels_per_tube - 1
    out += template.format('front_left_'+str(i), start, end)

# front-bottom
for i in range(n_tubes_panels):
    ids = front_bottom_start + i
    id_str = str(ids)
    for p in range(1, pixels_per_tube):
        next = ids + p * n_tubes_panels
        id_str += ',' + str(next)
    out += template_2.format('front_bottom_'+str(i), id_str)

# front-top
for i in range(n_tubes_panels):
    ids = front_top_start + i
    id_str = str(ids)
    for p in range(1, pixels_per_tube):
        next = ids + p * n_tubes_panels
        id_str += ',' + str(next)
    out += template_2.format('front_top_'+str(i), id_str)

# back
for i in range(n_tubes_back):
    ids = back_start + i
    id_str = str(ids)
    for p in range(1, pixels_per_tube):
        next = ids + p * n_tubes_back
        id_str += ',' + str(next)
    out += template_2.format('back_'+str(i), id_str)

out += footer

print(out)
