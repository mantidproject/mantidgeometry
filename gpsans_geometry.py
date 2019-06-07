#!/usr/bin/python3
from helper import MantidGeom
from SNS.SANS.utilities import (kw, ag, make_filename, add_basic_types,
                                add_double_flat_panel_type,
                                add_double_flat_panel_component,
                                add_double_panel_idlist)

"""
Instrument requirements from meeting at HFIR on May 07, 2019
- One component for the front panel and one component for the back panel
- divide each bank into fourpacks
- Pixel ID's start at tube1 of bank1 and finish at last tube of the last bank
"""

iinfo = dict(valid_from='2019-01-01 00:00:00',
             valid_to='2100-12-31 23:59:59',
             comment='Created by Jose Borregero, borreguerojm@ornl.gov',
             instrument_name='GPSANS',
             source_sample_distance=1.0,
             bank_name='bank',
             flat_panel_types=dict(front='front-panel', back='back-panel'),
             flat_array='detector1',  # name of the detector array
             tube_length=1.046,
             tube_diameter=0.00805,
             pixels_per_tube=256,
             tube_separation=0.0110,  # distance between consecutive tube axis
             fourpack_separation=0.0082,  # distance between front and back fourpacks
             fourpack_slip=0.0055,  # slip vector between the two fourpacks along X-axis
             number_eightpacks=24)  # number of eight-packs in the detector array


det = MantidGeom(iinfo['instrument_name'],
                 **kw(iinfo, 'comment', 'valid_from', 'valid_to'))
det.addSnsDefaults(default_view="3D", axis_view_3d="Z-")
fn = make_filename(*ag(iinfo, 'instrument_name', 'valid_from','valid_to'))
#
# Insert the flat panel
#
add_basic_types(det, iinfo)  # source, sample, pixel, tube, and fourpack
double_panel = add_double_flat_panel_type(det, iinfo)
pixel_idlist = 'pixel_ids'
add_double_flat_panel_component(double_panel, pixel_idlist, det,
                                iinfo['flat_array'])
add_double_panel_idlist(det, iinfo, pixel_idlist)
det.writeGeom(fn)