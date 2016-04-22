#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

BIOSANS new Wing detector

I'm using DJANGO templates to generate this

This is just a test, note that this does not procuce the full IDF file
accepted by mantid

"""
from django.template import Template, Context
from django.conf import settings
from django import setup

import numpy as np

# INIT
settings.configure()
setup()

# Variables
radius = 1.13
n_tubes = 20*8
n_pixels_tube = 256
n_total_pixels = n_tubes * n_pixels_tube

biosans_tube_step_meters = 0.0055
tube_step_angle_radians = np.arcsin(biosans_tube_step_meters/2.0/radius)
tube_step_angle_degrees = np.degrees(tube_step_angle_radians)

# copied from biosans
pixel_positions = np.linspace(-0.54825, 0.54825, 256)

# Values to replace in the template
values = {
 "first_id" : 2000000,
 "last_id" : 2000000 + n_total_pixels,
 "radius" : radius,
 "tube_pos_angle" : [ -tube_step_angle_degrees * x for x in range(n_tubes) ] ,
 "pixel_positions" : pixel_positions,
}


# Template
template = """
<component type="detectors" idlist="detectors">
    <location />
</component>

<idlist idname="detectors">
    <id start="{{ first_id }}" end="{{ last_id }}" />
</idlist>

<type name="detectors">
    <component type="wing_detector"><location/></component>
</type>

<type name="wing_detector">
    <component type="wing_tube">
        {% for angle in tube_pos_angle %}
        <location r="{{ radius }}" t="{{ angle }}" name="wing_tube_{{ forloop.counter0 }}" />{% endfor %}
    </component>
</type>

<type name="wing_tube" outline="yes">
    <component type="wing_pixel">
        {% for pos_y in pixel_positions %}
        <location y="{{pos_y}}" name="wing_pixel_{{ forloop.counter0 }}" />{% endfor %}
    </component>
</type>

<type name="wing_pixel" is="detector">
    <cylinder id="cyl-approx">
        <centre-of-bottom-base p="0.0" r="0.0" t="0.0"/>
        <axis y="1.0" x="0.0" z="0.0"/>
        <radius val="0.00275"/>
        <height val="0.0043"/>
    </cylinder>
    <algebra val="cyl-approx"/>
</type>


"""

def to_string():
    """
    Render the template
    """
    t = Template(template)
    c = Context(values)
    return t.render(c)


if __name__ == '__main__':
    print to_string()
