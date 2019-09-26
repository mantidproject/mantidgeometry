#!/usr/bin/python3
from helper import MantidGeom
from SNS.SANS.utilities import (kw, ag, make_filename, add_basic_types,
                                add_double_flat_panel_type,
                                add_double_flat_panel_component,
                                add_double_panel_idlist,
                                add_comment_section, add_sample_aperture,
                                insert_location_from_logs)

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
             source_sample_distance=13.601,
             monitors=(dict(name='monitor1', z=-10.5),
                       dict(name='timer', z=-10.5)),
             sample_aperture=dict(z=0.0, diameter=14.0),
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

add_sample_aperture(det, **iinfo['sample_aperture'])

#
# Insert the flat panel
#
double_panel = add_double_flat_panel_type(det, iinfo)
pixel_idlist = 'pixel_ids'
double_panel = add_double_flat_panel_component(double_panel, pixel_idlist, det, iinfo['flat_array'])
insert_location_from_logs(double_panel, log_key=['detector-translation', 'sdd'], coord_name=['x', 'z'],
                          equation=['-0.001*value', '0.001*value'])
add_double_panel_idlist(det, iinfo, pixel_idlist)
det.writeGeom(fn)
