#!/usr/bin/python3
# local imports
from helper import MantidGeom
from SNS.SANS.utilities import (kw, ag, make_filename, add_basic_types, add_double_flat_panel_type,
                                add_double_flat_panel_component, add_double_curved_panel_type,
                                add_double_curved_panel_component, add_double_panel_idlist, add_comment_section,
                                insert_location_from_logs)
# third party imports

# standard imports
from copy import deepcopy
import math

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
iinfo = dict(valid_from='2023-10-01 00:00:00',
             valid_to='2100-12-31 23:59:59',
             comment='Created by Jose Borregero, borreguerojm@ornl.gov',
             instrument_name='BIOSANS',
             source_sample_distance=1.0,
             monitors=(dict(name='monitor1', z=-10.5),
                       dict(name='timer', z=-10.5)),
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
det = MantidGeom(iinfo['instrument_name'], **kw(iinfo, 'comment', 'valid_from', 'valid_to'))
det.addSnsDefaults(default_view="3D", axis_view_3d="Z-")
fn = make_filename(*ag(iinfo, 'instrument_name', 'valid_from', 'valid_to'))
add_basic_types(det, iinfo)  # source, sample, pixel, tube, and fourpack
#
# Monitor Section
#
add_comment_section(det, 'COMPONENT, TYPE, and IDLIST: MONITORS')
det.addMonitors(distance=[m['z'] for m in iinfo['monitors']],
                names=[m['name'] for m in iinfo['monitors']])
det.addMonitorIds(ids=[-1, -2])
det.addDummyMonitor(0.01, 0.1)
#
# Insert the flat panel
#
double_panel = add_double_flat_panel_type(det, iinfo)
pixel_idlist = 'flat_panel_ids'
double_panel = add_double_flat_panel_component(double_panel, 'flat_panel_ids', det, iinfo['flat_array'])
insert_location_from_logs(double_panel, log_key=['detector_trans_Readback', 'sample_detector_distance'],
                          coord_name=['x', 'z'], equation=['-0.001*value', 'value'])
add_double_panel_idlist(det, iinfo, pixel_idlist)
last_pixel_id = 8 * iinfo['number_eightpacks'] * iinfo['pixels_per_tube'] - 1
last_bank_number = 2 * iinfo['number_eightpacks']
#
# Insert the curved panel for the wing detector
#
"""
Explanation of some entries in the below jinfo dictionary
 bank_radius      distance between focal-point and anchor point
 anchor_offset    add this to bank_radius for distance between focal-point
                  and eightpack midline
 eightpack_angle  effective angle subtended by each eightpack, in degrees
"""
jinfo = dict(curved_array='wing_detector',  # name of the wing detector
             curved_panel_types=dict(front='front-wing-panel',
                                     back='back-wing-panel',
                                     double='double-wing-panel'),
             number_eightpacks=20,
             bank_radius=1.129538,
             anchor_offset=0.0,
             eightpack_angle=2.232094,
             panel_translation_log_key='detectorZ')
panel_info = deepcopy(iinfo)
panel_info.update(jinfo)
r_eightpack = panel_info['bank_radius'] + panel_info['anchor_offset']
comment = f'Panel is positioned {r_eightpack} meters downstream'
kwargs = dict(comment=comment, to_origin=False, first_bank_number=1 + last_bank_number)
double_panel = add_double_curved_panel_type(det, panel_info, **kwargs)
pixel_idlist = 'curved_panel_ids'
double_panel = add_double_curved_panel_component(double_panel, pixel_idlist, det, panel_info['curved_array'])
# Rotate the double panel away from the path of the Z-axis
rot_y = - panel_info['eightpack_angle'] * panel_info['number_eightpacks'] / 2
rot_y += 0.5 * panel_info['fourpack_slip'] / panel_info['bank_radius'] * 180. / math.pi
det.addLocation(double_panel, 0., 0., 0, rot_y=f'{rot_y:.2f}')
insert_location_from_logs(double_panel, log_key=['ww_rot_Readback', 'ww_rot_Readback'],
                          coord_name=['t-position', 'roty'], equation=[f'{rot_y:.2f}-value', f'{rot_y:.2f}-value'])
add_double_panel_idlist(det, panel_info, pixel_idlist, start=1 + last_pixel_id)
last_pixel_id += 8 * panel_info['number_eightpacks'] * panel_info['pixels_per_tube']
last_bank_number += 2 * panel_info['number_eightpacks']
#
# Insert the curved panel for the midrange detector
#
"""
Explanation of some entries in the below kinfo dictionary
 bank_radius      distance between focal-point and anchor point
 anchor_offset    add this to bank_radius for distance between focal-point
                  and eightpack midline
 eightpack_angle  effective angle subtended by each eightpack, in degrees
"""
kinfo = dict(curved_array='midrange_detector',  # name of the midrange detector
             curved_panel_types=dict(front='front-midrange-panel',
                                     back='back-midrange-panel',
                                     double='double-midrange-panel'),
             number_eightpacks=8,
             bank_radius=3.9662,  # shift so that the arc between the front and back panels is 4m away
             anchor_offset=0.0,
             eightpack_angle=0.629663,
             panel_translation_log_key='midrange_rot_Readback')
panel_info = deepcopy(iinfo)
panel_info.update(kinfo)
r_eightpack = panel_info['bank_radius'] + panel_info['anchor_offset']
comment = f'Panel is positioned {r_eightpack} meters downstream'
kwargs = dict(comment=comment, to_origin=False, first_bank_number=1 + last_bank_number)
double_panel = add_double_curved_panel_type(det, panel_info, **kwargs)
pixel_idlist = 'midrange_panel_ids'
double_panel = add_double_curved_panel_component(double_panel, pixel_idlist, det, panel_info['curved_array'])
# Rotate the double panel away from the path of the Z-axis to the nominal angle
rot_y = panel_info['eightpack_angle'] * panel_info['number_eightpacks'] / 2
rot_y += - 0.5 * panel_info['fourpack_slip'] / panel_info['bank_radius'] * 180. / math.pi
det.addLocation(double_panel, 0., 0., 0, rot_y=f'{rot_y:.2f}')
insert_location_from_logs(double_panel,
                          log_key=[panel_info['panel_translation_log_key'], panel_info['panel_translation_log_key']],
                          coord_name=['t-position', 'roty'],
                          equation=[f'{rot_y:.2f}-value', f'{rot_y:.2f}-value'])
add_double_panel_idlist(det, panel_info, pixel_idlist, start=1 + last_pixel_id)
#
# Write to file
#
det.writeGeom(fn)
