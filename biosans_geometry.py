#!/usr/bin/python3
import math
from helper import MantidGeom
from SNS.SANS.utilities import (kw, ag, make_filename, add_basic_types,
                                add_double_flat_panel_type,
                                add_double_flat_panel_component,
                                add_double_curved_panel_type,
                                add_double_curved_panel_component,
                                add_double_panel_idlist)

"""
Instrument requirements from meeting at HFIR on May 07, 2019
- One component for the front panel and one component for the back panel
- divide each bank into fourpacks
- Pixel ID's start at tube1 of bank1 and finish at last tube of the last bank
"""

"""
Explanation of some entries in iinfo dictionary
 tube_separation      distance between consecutive tube axis
 fourpack_separation  distance between front and back fourpacks
 fourpack_slip        slip vector between the two fourpacks along X-axis
 number_eightpacks    number of eight-packs in the detector array
"""
iinfo = dict(valid_from='2019-01-01 00:00:00',
             valid_to='2100-12-31 23:59:59',
             comment='Created by Jose Borregero, borreguerojm@ornl.gov',
             instrument_name='BIOSANS',
             source_sample_distance=1.0,
             flat_array='detector1',  # name of the detector array
             flat_panel_types=dict(front='front-panel', back='back-panel'),
             bank_name='bank',
             tube_length=1.046,
             tube_diameter=0.00805,
             pixels_per_tube=256,
             tube_separation=0.0112522,
             fourpack_separation=0.008205216,
             fourpack_slip=0.0055103014,
             number_eightpacks=24)

# Instrument handle
det = MantidGeom(iinfo['instrument_name'],
                 **kw(iinfo, 'comment', 'valid_from', 'valid_to'))
det.addSnsDefaults(default_view="3D", axis_view_3d="Z-")
fn = make_filename(*ag(iinfo, 'instrument_name', 'valid_from', 'valid_to'))
add_basic_types(det, iinfo)  # source, sample, pixel, tube, and fourpack
#
# Insert the flat panel
#
double_panel = add_double_flat_panel_type(det, iinfo)
pixel_idlist = 'flat_panel_ids'
add_double_flat_panel_component(double_panel, 'flat_panel_ids', det,
                                iinfo['flat_array'])
add_double_panel_idlist(det, iinfo, pixel_idlist)
last_pixel_id = 8 * iinfo['number_eightpacks'] * iinfo['pixels_per_tube'] - 1

#
# Insert the curved panel
#
"""
Explanation of some entries in jinfo dictionary
 bank_radius      distance between focal-point and anchor point
 anchor_offset    add this to bank_radius for distance between focal-point
                  and eightpack midline
 eightpack_angle  effective angle subtended by each eightpack, in degrees
"""
jinfo = dict(curved_array='wing_detector_arm',  # name of the wing detector
             curved_panel_types=dict(front='front-wing-panel',
                                     back='back-wing-panel'),
             bank_name='wing-bank',
             number_eightpacks=20,
             bank_radius=1.129538,
             anchor_offset=0.0,
             eightpack_angle=2.232094)

iinfo.update(jinfo)
double_panel = add_double_curved_panel_type(det, iinfo)
pixel_idlist = 'curved_panel_ids'
double_panel = add_double_curved_panel_component(double_panel,
                                                 pixel_idlist,
                                                 det, iinfo['curved_array'])
# Rotate the double panel away from the path of the Z-axis
rot_y = - iinfo['eightpack_angle'] * iinfo['number_eightpacks'] / 2
rot_y += 0.5 * iinfo['fourpack_slip'] / jinfo['bank_radius'] * 180. / math.pi
det.addLocation(double_panel, 0., 0., 0, rot_y=rot_y)
add_double_panel_idlist(det, iinfo, pixel_idlist, start=1 + last_pixel_id)

#
# Write to file
#
det.writeGeom(fn)
