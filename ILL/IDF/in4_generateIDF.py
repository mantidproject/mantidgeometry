#!/usr/bin/python
# -*- coding: utf-8 -*-

"""This script generates an instrument definition for the IN4 instrument
   at ILL and writes it to stdout. The 'tidy' command available on some
   systems can be used to clean up the output:
   python in4_generateIDF.py | tidy -utf8 -xml -w 255 -i -c -q -asxml
"""

import common_IDF_functions
import numpy
import scipy.constants
import sys

class WideAngleProperties:
    """This is a placeholder for all the information regarding the
       wide-angle detectors.
    """
    box_sizes = {
        'top': [4, 4, 4, 8, 8, 12, 12, 12, 12, 12, 12],
        'middle': [12, 12, 12, 12, 12, 12, 12, 12, 4],
        'bottom': [4, 4, 4, 8, 8, 12, 12, 12, 12, 12, 12]
    }
    dPhis = {           # Latitudes for the banks
        'top': 12.6,
        'middle': 0.0,
        'bottom': -12.6
    }
    dTheta = 0.95       # Scattering angle delta
    R = 2.0             # Sample-detector distance
    thetas = {          # Box center scattering angles.
        'top': numpy.array([-14.5, 14.5, 20.5, 28.3, 37.9, 49.3, 62.5, 75.7, 88.8, 101.9, 115.1]),
        'middle': numpy.array([18.5, 31.5, 44.5, 57.5, 69.55, 83.5, 96.5, 109.5, 118.7]),
        'bottom': numpy.array([-14.5, 14.5, 20.5, 28.3, 37.9, 49.3, 62.5, 75.7, 88.8, 101.9, 115.1]),
    }
    tube_length = 0.3
    tube_radius = 0.0127

class RosaceProperties:
    """This class holds details of the rosace small-angle detector.
    """
    R = 2.0                # Distance from sample to *sector* center
    thetas = numpy.array([ # Pixel scattering angles
        2.435,
        3.008,
        3.581,
        4.154,
        4.727,
        5.300,
        5.873,
        6.446,
        7.019,
        7.592,
        8.165,
        8.738
    ])
    mean_theta = numpy.mean(thetas)
    thickness = 0.01       # A guess for pixel thickness

def write_in4_monitors(f, indent):
    """Writes monitor information to f.
    """
    f.write(indent + '<idlist idname="monitor_ids">\n')
    f.write(indent + '  <id val="0" />\n')
    f.write(indent + '</idlist>\n')
    f.write(indent + '<type name="monitor" is="Monitor">\n')
    f.write(indent + '  <!-- This may not be the real monitor shape. -->\n')
    f.write(indent + '  <cylinder id="monitor_shape">\n')
    f.write(indent + '    <centre-of-bottom-base x="0.0" y="0.0" z="0.0" />\n')
    f.write(indent + '    <axis x="0.0" y="0.0" z="1.0" />\n')
    f.write(indent + '    <radius val="0.02" />\n')
    f.write(indent + '    <height val="0.03" />\n')
    f.write(indent + '  </cylinder>\n')
    f.write(indent + '  <algebra val="monitor_shape" />\n')
    f.write(indent + '</type>\n')
    f.write(indent + '<component type="monitors" idlist="monitor_ids">\n')
    f.write(indent + '  <location />\n')
    f.write(indent + '</component>\n')
    f.write(indent + '<type name="monitors">\n')
    f.write(indent + '  <component type="monitor">\n')
    f.write(indent + '    <location x="0.0" y="0.0" z="-0.3039" name="monitor_1" />\n')
    f.write(indent + '  </component>\n')
    f.write(indent + '</type>\n')

def write_in4_idlist(f, indent):
    """Writes detector id list to f.
    """
    # 300 tubes and 96 pixels in rosace, 396 in total. 
    f.write(indent + '<idlist idname="detectors">\n')
    f.write(indent + '  <id start="{}" end="{}" />\n'.format(1, 396))
    f.write(indent + '</idlist>\n')

### Wide-angle detectors

def write_in4_tube_type(f, indent):
    """Writes the wide angle detector tube type to f.
    """
    f.write(indent + '<type name="tube" is="detector">\n')
    f.write(indent + '  <cylinder id="tube_shape">\n')
    f.write(indent + '    <centre-of-bottom-base x="0.0" y="-{}" z="0.0" />\n'.format(WideAngleProperties.tube_length / 2.0))
    f.write(indent + '    <axis x="0.0" y="1.0" z="0.0" />\n')
    f.write(indent + '    <radius val="{}" />\n'.format(WideAngleProperties.tube_radius))
    f.write(indent + '    <height val="{}" />\n'.format(WideAngleProperties.tube_length))
    f.write(indent + '  </cylinder>\n')
    f.write(indent + '  <algebra val="tube_shape" />\n')
    f.write(indent + '</type>\n')

def write_in4_box_type(f, size, indent):
    """Writes tube box types to f. The number of tubes in each box is
       specified by size.
    """
    theta_begin = WideAngleProperties.dTheta * float(size - 1) / 2.0
    f.write(indent + '<type name="{}_tube_box">\n'.format(size))
    for i in range(size):
        theta = theta_begin - i * WideAngleProperties.dTheta
        x = WideAngleProperties.R * numpy.sin(theta * scipy.constants.degree)
        z = WideAngleProperties.R * (1.0 - numpy.cos(theta * scipy.constants.degree))
        pos = (x, 0.0, z)
        f.write(indent + '  <component type="tube" name="tube_{}">\n'.format(i + 1))
        f.write(indent + '    <location x="{pos[0]}" y="{pos[1]}" z="{pos[2]}">\n'.format(pos = pos))
        f.write(indent + '      <rot val="{}" axis-x="0.0" axis-y="1.0" axis-z="0.0" />\n'.format(theta))
        f.write(indent + '    </location>\n')
        f.write(indent + '  </component>\n')
    f.write(indent + '</type>\n')

def write_in4_bank_types(f, indent):
    """Writes the top, middle and bottom wide-angle detector banks to f.
    """
    for bank_id in WideAngleProperties.thetas.keys():
        f.write(indent + '<type name="{}_bank">\n'.format(bank_id))
        orientations = numpy.copysign(numpy.ones(len(WideAngleProperties.thetas[bank_id])), WideAngleProperties.thetas[bank_id])
        (xs, y, zs) = common_IDF_functions.box_coordinates(WideAngleProperties.R, WideAngleProperties.thetas[bank_id], WideAngleProperties.dPhis[bank_id], orientations)
        tilting_angles = common_IDF_functions.tilting_angle(WideAngleProperties.thetas[bank_id], WideAngleProperties.dPhis[bank_id], 1)
        for i in range(len(WideAngleProperties.thetas[bank_id])):
            f.write(indent + '  <component type="{}_tube_box" name="box_{}">\n'.format(WideAngleProperties.box_sizes[bank_id][i], i + 1))
            f.write(indent + '    <location x="{}" y="{}" z="{}">\n'.format(xs[i], y, zs[i]))
            f.write(indent + '      <rot val="{}" axis-x="0.0" axis-y="1.0" axis-z="0.0">\n'.format(numpy.arctan2(xs[i], zs[i]) / scipy.constants.degree + 180.0))
            f.write(indent + '        <rot val="{}" axis-x="1.0" axis-y="0.0" axis-z="0.0">\n'.format(WideAngleProperties.dPhis[bank_id]))
            f.write(indent + '          <rot val="{}" axis-x="0.0" axis-y="0.0" axis-z="1.0" />\n'.format(tilting_angles[i]))
            f.write(indent + '        </rot>\n')
            f.write(indent + '      </rot>\n')
            f.write(indent + '    </location>\n')
            f.write(indent + '  </component>\n')
        f.write(indent + '</type>\n')

def write_in4_wide_angle_type(f, indent):
    """Writes the wide angle detector banks to f.
    """
    f.write(indent + '<type name="wide_angle">\n')
    f.write(indent + '  <component type="top_bank">\n')
    f.write(indent + '    <location />\n')
    f.write(indent + '  </component>\n')
    f.write(indent + '  <component type="middle_bank">\n')
    f.write(indent + '    <location />\n')
    f.write(indent + '  </component>\n')
    f.write(indent + '  <component type="bottom_bank">\n')
    f.write(indent + '    <location />\n')
    f.write(indent + '  </component>\n')
    f.write(indent + '</type>\n')

### Rosace small-angle detector

def rosace_pixel_r(theta):
    """Calculates a pixel's distance from detector center.
    """
    theta = theta * scipy.constants.degree
    return numpy.sin(theta) / numpy.cos(RosaceProperties.mean_theta * scipy.constants.degree - theta) * RosaceProperties.R

def rosace_pixel_half_xml(lb, lt, rt, rb, indent):
    """Returns an xml snipped describing the left half of a pixel.
    """
    def back_side(x, thickness):
        return (x[0], x[1], -thickness)
    xml  = indent + '<left-front-bottom-point x="{lfb[0]}" y="{lfb[1]}" z="{lfb[2]}" />'.format(lfb = lb) + '\n'
    xml += indent + '<left-front-top-point x="{lft[0]}" y="{lft[1]}" z="{lft[2]}" />'.format(lft = lt) + '\n'
    xml += indent + '<right-front-top-point x="{rft[0]}" y="{rft[1]}" z="{rft[2]}" />'.format(rft = rt) + '\n'
    xml += indent + '<right-front-bottom-point x="{rfb[0]}" y="{rfb[1]}" z="{rfb[2]}" />'.format(rfb = rb) + '\n'
    xml += indent + '<left-back-bottom-point x="{lbb[0]}" y="{lbb[1]}" z="{lbb[2]}" />'.format(lbb = back_side(lb, RosaceProperties.thickness)) + '\n'
    xml += indent + '<left-back-top-point x="{lbt[0]}" y="{lbt[1]}" z="{lbt[2]}" />'.format(lbt = back_side(lt, RosaceProperties.thickness)) + '\n'
    xml += indent + '<right-back-top-point x="{rbt[0]}" y="{rbt[1]}" z="{rbt[2]}" />'.format(rbt = back_side(rt, RosaceProperties.thickness)) + '\n'
    xml += indent + '<right-back-bottom-point x="{rbb[0]}" y="{rbb[1]}" z="{rbb[2]}" />'.format(rbb = back_side(rb, RosaceProperties.thickness)) + '\n'
    return xml

def write_in4_rosace_pixel_type(f, indent):
    """Writes rosace's pixel type to f.
    """
    alpha = 45.0 / 2 # Half of sector angle.
    rs = numpy.array([rosace_pixel_r(theta) for theta in RosaceProperties.thetas])
    h = numpy.amin(numpy.ediff1d(rs)) # Pixel height along the sector's y axis
    # In the following: r = right, l = left, t = top, b = bottom.
    rt = (0.0,  0.5 * h, 0.0)
    rb = (0.0, -0.5 * h, 0.0)
    for i in range(len(RosaceProperties.thetas)):
        d = rs[i] - 0.5 * h
        lb = (-d * numpy.sin(alpha * scipy.constants.degree), d * numpy.cos(alpha * scipy.constants.degree) - rs[i], 0.0)
        d = rs[i] + 0.5 * h
        lt = (-d * numpy.sin(alpha * scipy.constants.degree), d * numpy.cos(alpha * scipy.constants.degree) - rs[i], 0.0)
        f.write(indent + '<type name="rosace_pixel_{pixel_id}" is="detector">\n'.format(pixel_id = i))
        f.write(indent + '  <hexahedron id="left_half_shape">\n')
        f.write(rosace_pixel_half_xml(lb, lt, rt, rb, indent + 2 * "  "))
        f.write(indent + '  </hexahedron>\n')
        f.write(indent + '  <hexahedron id="right_half_shape">\n')
        def mirror_yz(x):
            return (-x[0], x[1], x[2])
        f.write(rosace_pixel_half_xml(mirror_yz(lb), mirror_yz(lt), mirror_yz(rt), mirror_yz(rb), indent + 2 * "  "))
        f.write(indent + '  </hexahedron>\n')
        f.write(indent + '  <algebra val="left_half_shape : right_half_shape" />\n')
        f.write(indent + '</type>\n')

def write_in4_rosace_sector_type(f, indent):
    """Writes rosace's sector type to f.
    """
    f.write(indent + '<type name="rosace_sector">\n')
    # Sample to detector center distance along z-axis.
    R_z = RosaceProperties.R / numpy.cos(RosaceProperties.mean_theta * scipy.constants.degree)
    for i in range(12):
        y = R_z * numpy.sin(RosaceProperties.thetas[i] * scipy.constants.degree) / numpy.cos((RosaceProperties.mean_theta - RosaceProperties.thetas[i]) * scipy.constants.degree)
        f.write(indent + '  <component type="rosace_pixel_{}" name="pixel_{}">\n'.format(i, i + 1))
        f.write(indent + '    <location x="0.0" y="{}" z="0.0" />\n'.format(y))
        f.write(indent + '  </component>\n')
    f.write(indent + '</type>\n')

def write_in4_rosace_type(f, indent):
    """Writes the rosace detector type to f.
    """
    f.write(indent + '<type name="rosace">\n')
    tilting = 90.0 - RosaceProperties.mean_theta
    for i in range(8):
        f.write(indent + '  <component type="rosace_sector" name="sector_{}">\n'.format(i))
        f.write(indent + '    <location x="0.0" y="0.0" z="0">\n')
        f.write(indent + '      <rot val="{}" axis-x="0.0" axis-y="0.0" axis-z="1.0">\n'.format(i * 45.0))
        f.write(indent + '        <rot val="{}" axis-x="1.0" axis-y="0.0" axis-z="0.0" />\n'.format(90.0 - tilting))
        f.write(indent + '      </rot>\n')
        f.write(indent + '    </location>\n')
        f.write(indent + '  </component>\n')
    f.write(indent + '</type>\n')

# Entire detector set

def write_in4_detectors_type(f, indent):
    """Writes the detectors type to f.
    """
    f.write(indent + '<type name="detectors">\n')
    f.write(indent + '  <component type="wide_angle">\n')
    f.write(indent + '    <location />\n')
    f.write(indent + '  </component>\n')
    f.write(indent + '  <component type="rosace">\n')
    f.write(indent + '    <location z="{}">\n'.format(2.0 / numpy.cos(RosaceProperties.mean_theta * scipy.constants.degree)))
    f.write(indent + '      <rot val="180.0" axis-x="0.0" axis-y="1.0" axis-z="0.0" />\n')
    f.write(indent + '    </location>\n')
    f.write(indent + '  </component>\n')
    f.write(indent + '</type>\n')

def write_in4_root_component(f, indent):
    """Writes the detectors root component to f.
    """
    f.write(indent + '<component type="detectors" idlist="detectors">\n')
    f.write(indent + '  <location />\n')
    f.write(indent + '</component>\n')

if __name__ == '__main__':
    f = sys.stdout
    common_IDF_functions.write_header(f, "IN4", "Riccardo Leal and Antti Soininen")
    common_IDF_functions.write_sample_position(f)
    common_IDF_functions.write_moderator(f)
    f.write('\n')
    indent = "  "
    f.write(indent + '<!-- Monitors -->\n')
    write_in4_monitors(f, indent)
    f.write(indent + '<!-- Detector ids -->\n')
    write_in4_idlist(f, indent)
    f.write(indent + '<!-- Wide-angle detectors -->\n')
    write_in4_tube_type(f, indent)
    write_in4_box_type(f, 4, indent)
    write_in4_box_type(f, 8, indent)
    write_in4_box_type(f, 12, indent)
    write_in4_bank_types(f, indent)
    write_in4_wide_angle_type(f, indent)
    f.write(indent + '<!-- Small angle rosace detector -->\n')
    write_in4_rosace_pixel_type(f, indent)
    write_in4_rosace_sector_type(f, indent)
    write_in4_rosace_type(f, indent)
    f.write(indent + '<!-- Entire detector set -->\n')
    write_in4_detectors_type(f, indent)
    write_in4_root_component(f, indent)
    common_IDF_functions.write_end(f)
