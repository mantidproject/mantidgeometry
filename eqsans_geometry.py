#!/usr/bin/python3
import math
from lxml import etree as le # python-lxml on rpm based systems
import sys
from helper import MantidGeom
from dateutil.parser import parse as parse_date
from collections import OrderedDict

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

iinfo = dict(valid_from='2019-01-01 00:00:00',
             valid_to='2100-12-31 23:59:59',
             comment='Created by Jose Borregero, borreguerojm@ornl.gov',
             instrument_name='EQSANS',
             source_sample_distance=14.122,
             array_name='detector1',
             tube_length=1.046,
             tube_diameter=0.00805,
             pixels_per_tube=256,
             tube_separation=0.0110,  # distance between consecutive tube axis
             fourpack_separation=0.0082,  # distance between front and back fourpacks
             fourpack_slip=0.0055,  # slip vector between the two fourpacks along X-axis
             bank_radius=5.0,  # distance between focal-point and anchor point
             anchor_offset=0.0041,  # add this to bank_radius for distance between focal-point and eightpack midline
             eightpack_angle=0.5041,  # angle subtended by each eightpack, in degrees
             number_eightpacks=24)   # number of eight-packs in the detector array


def filter_dict(d, *keys):
    r"""Filter a dictionary by passed keys

    Parameters
    ----------
    d: dict
        Dictionary to be filtered
    keys: list
        List of keys to be kept in the filtered dictionary

    Returns
    -------
    OrderedDict
        Dictionary that keeps the order in which the keys were passed.
    """
    return OrderedDict([(k, d[k]) for k in keys])


def kw(d, *keys):
    r"""Dictionary with only desired keys"""
    return dict(filter_dict(d, *keys))


def ag(d, *keys):
    r"""Values of a dictionary for only desired keys. Values are returned in
    same order as elements of list `keys`"""
    return list(filter_dict(d, *keys).values())


def make_filename(instrument_name, valid_from, valid_to):
    r"""
    Create XML file using the date ranges

    Parameters
    ----------
    instrument_name: str
        Instrument name
    valid_from: str
        Beginning time for the validity of this IDF
    valid_to: str
        Ending time for the validity of this IDF
    Returns
    -------
    str
        EQSANS_Definition_X_Y.xml where X and Y are derived from valid_from
        and valid_to, respectively
    """
    vfp, vtp = '', ''
    for period in ('year', 'month', 'day'):
        vfp += str(getattr(parse_date(valid_from), period)) + '-'
        vtp += str(getattr(parse_date(valid_to), period)) + '-'
        if vfp != vtp:
            break
    return f'{instrument_name}_Definition_{vfp[:-1]}_{vtp[:-1]}.xml'


def add_comment_section(instrument, comment):
    instrument.addComment("")
    instrument.addComment(comment)
    instrument.addComment("")


if __name__ == '__main__':
    det = MantidGeom(iinfo['instrument_name'],
                     **kw(iinfo, 'comment', 'valid_from', 'valid_to'))
    det.addSnsDefaults(default_view="3D", axis_view_3d="Z-")
    fn = make_filename(*ag(iinfo, 'instrument_name', 'valid_from','valid_to'))

    add_comment_section(det, 'COMPONENT and TYPE: SOURCE AND SAMPLE POSITION')
    det.addModerator(-iinfo['source_sample_distance'])
    det.addSamplePosition()

    add_comment_section(det, 'TYPE: PIXEL FOR STANDARD 256 PIXEL TUBE')
    center_bottom_base = (0.0, 0.0, 0.0)
    pixel_axis = (0.0, 1.0, 0.0)
    pixel_radius = iinfo['tube_diameter'] / 2.0
    pixel_height = iinfo['tube_length'] / iinfo['pixels_per_tube']
    det.addCylinderPixel("pixel", center_bottom_base, pixel_axis,
                         pixel_radius, pixel_height)

    add_comment_section(det, 'TYPE: STANDARD 256 PIXEL TUBE')
    tube_type_name = 'tube'
    det.addPixelatedTube(tube_type_name, iinfo['pixels_per_tube'],
                         iinfo['tube_length'])

    add_comment_section(det, 'TYPE: FOUR-PACK')
    air_gap = iinfo['tube_separation'] - iinfo['tube_diameter']
    # negative diameter and air gaps to conform with ordering of tubes
    # in the Nexus embedded XML file
    det.addNPack('fourpack', 4, -iinfo['tube_diameter'], -air_gap,
                 type_name=tube_type_name)

    # distance from sample to the center of the eight-pack
    r_eightpack = iinfo['bank_radius'] + iinfo['anchor_offset']
    # shift by delta_r for distance from sample to either of the two fourpacks
    delta_r = iinfo['fourpack_separation'] / 2
    n = iinfo['number_eightpacks']
    slip_angle = 180. / math.pi * iinfo['fourpack_slip'] / (2 * r_eightpack)
    # negative dtheta to conform with ordering of eightpacks in the Nexus
    # embedded XML file

    add_comment_section(det, 'TYPE: FRONT PANEL')
    args = ['front-panel', 'fourpack', n,
            r_eightpack - delta_r, -iinfo['eightpack_angle']]
    det.add_curved_panel(*args, sub_name='bank', theta_0=slip_angle,
                         first_index=1)

    add_comment_section(det, 'TYPE: BACK PANEL')
    args = ['back-panel', 'fourpack', n,
            r_eightpack + delta_r, -iinfo['eightpack_angle']]
    back_panel = det.add_curved_panel(*args, sub_name='bank',
                                      theta_0=-slip_angle, first_index=1+n)

    add_comment_section(det, 'TYPE: DOUBLE PANEL')
    double_panel = le.SubElement(det.root, 'type', name='double-panel')
    le.SubElement(double_panel, 'properties')
    front_panel = le.SubElement(double_panel, 'component', type='front-panel')
    det.addLocation(front_panel, 0., 0., -r_eightpack - delta_r)
    back_panel = le.SubElement(double_panel, 'component', type='back-panel')
    det.addLocation(back_panel, 0., 0., -r_eightpack + delta_r)

    add_comment_section(det, 'COMPONENT: DETECTOR ARRAY')
    panel = det.addComponent('double-panel', idlist='array_list',
                             name=iinfo['array_name'], blank_location=True)
    det.addLocation(panel, 0., 0., 0)

    add_comment_section(det, 'ID ranges for DETECTOR ARRAY')
    det.addDetectorIds('array_list',
                       [0, iinfo['number_eightpacks']*8*256 - 1, 1])
    det.writeGeom(fn)
