#!/usr/bin/python3
from helper import MantidGeom
from SNS.SANS.utilities import (kw, ag, make_filename, add_basic_types,
                                add_double_curved_panel_type,
                                add_double_curved_panel_component,
                                add_double_panel_idlist,
                                insert_location_from_logs)

"""
Instrument requirements from meeting at HFIR on May 07, 2019
- One component for the front panel and one component for the back panel
- divide each bank into fourpacks
- Pixel ID's start at tube1 of bank1 and finish at last tube of the last bank
"""

"""
Instrument hierarchy in Nexus file:
- 48 banks, 4 tubes per bank, 256 pixels per tube. The first eigthpack
  is made of banks 1 and 25, although the eightpack construct is not
  used.
- front panel (close to the sample) contains banks 1 through 24.
- bank number increases with decreasing X-coordinate values.
- tube number increases with decreasing X-coordinate values.
- pixel number increases with increasing Y-coordinate values.
- pixel number increases with decreasing X-coordinate values
- pixel number increases from bank1 to bank4, then from bank25 to bank28,
  then from bank5 to bank8, then from bank29 to bank32, and so on

Instrument hierarchy in current IDF:
- 48 banks, 4 tubes per bank, 256 pixels per tube.
- front panel (close to the sample) contains banks 1 through 24.
- bank number increases with decreasing X-coordinate values
- tube number increases with decreasing X-coordinate values
- pixel number increases with increasing Y-coordinate values
- pixel number increases with decreasing X-coordinate values
- pixel number increases with increasing bank number
"""

"""
Explanation of some entries in iinfo dictionary
 tube_separation      distance between consecutive tube axis
 fourpack_separation  distance between front and back fourpacks
 fourpack_slip        slip vector between the two fourpacks along X-axis
 bank_radius          distance between focal-point and anchor point
 anchor_offset        add this to bank_radius for distance between focal-point
                      and eightpack midline
 eightpack_angle      angle subtended by each eightpack, in degrees
 number_eightpacks    number of eight-packs in the detector array
 panel_translation_log_key  log entry specifying the position of the detector
"""
iinfo = dict(valid_from='2019-01-01 00:00:00',
             valid_to='2100-12-31 23:59:59',
             comment='Created by Jose Borregero, borreguerojm@ornl.gov',
             instrument_name='EQ-SANS',
             source_sample_distance=14.122,
             bank_name='bank',
             curved_array='detector1',
             curved_panel_types=dict(front='front-panel', back='back-panel'),
             tube_length=1.046,
             tube_diameter=0.00805,
             pixels_per_tube=256,
             tube_separation=0.0110,
             fourpack_separation=0.0082,
             fourpack_slip=0.0055,
             bank_radius=5.0,
             anchor_offset=0.0041,
             eightpack_angle=0.5041,
             number_eightpacks=24,
             panel_translation_log_key='detectorZ')


if __name__ == '__main__':
    det = MantidGeom(iinfo['instrument_name'],
                     **kw(iinfo, 'comment', 'valid_from', 'valid_to'))
    det.addSnsDefaults(default_view="3D", axis_view_3d="Z-")
    fn = make_filename(*ag(iinfo, 'instrument_name', 'valid_from', 'valid_to'))
    add_basic_types(det, iinfo)  # source, sample, pixel, tube, and fourpack
    #
    # Insert the curved panel
    #
    r_eightpack = iinfo['bank_radius'] + iinfo['anchor_offset']
    comment = f'Panel is positioned {r_eightpack} meters downstream'
    double_panel = add_double_curved_panel_type(det, iinfo, comment=comment)
    pixel_idlist = 'pixel_ids'
    comment = f'Panel is translated to the origin, ' \
              f'then shifted by an amount specified in the logs'
    double_panel = add_double_curved_panel_component(double_panel,
                                                     pixel_idlist,
                                                     det,
                                                     iinfo['curved_array'],
                                                     comment=comment)
    insert_location_from_logs(double_panel,
                              log_key=iinfo['panel_translation_log_key'],
                              coord_name='z',
                              equation=f'{-r_eightpack}+0.001*value')
    add_double_panel_idlist(det, iinfo, pixel_idlist)
    #
    # Write to file
    #
    det.writeGeom(fn)
