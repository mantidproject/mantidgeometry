#!/usr/bin/python3
from lxml import etree as le # python-lxml on rpm based systems
import sys
from helper import MantidGeom
from dateutil.parser import parse as parse_date
from collections import OrderedDict

"""
Instrument requirements from meeting at HFIR on May 07, 2019
- One bank for the fron panel and one bank for the back panel
- (optional) divide each bank into fourpacks
- Pixel ID's start at tube1 of bank1, then continue in tube1 of bank2, then
  continue in tube2 of bank1,  then continue in tube2 of bank2, and so on
"""

"""
Instrument hierarchy in Nexus file:
- 48 banks, 4 tubes per bank, 256 pixels per tube. The first eigthpack
  is made of banks 1 and 25, although the eightpack construct is not
  used. Useful when comparing with the hiearchy of current IDF.
- front panel (close to the sample) contains banks 1 through 24.
- bank number increases with decreasing X-coordinate values.
- tube number increases with decreasing X-coordinate values.
- pixel number increases with increasing Y-coordinate values.

Instrument hierarchy in current IDF to match hieararchy of Nexus file:
- 24 eightpacks, two fourpacks per eightpack, four tubes per fourpack,
  256 pixels per tube.
- eighpack number increases with decreasing X-coordinate values.
- fourpack front to back with increasing Z-coordinate values.
- tube number increases with decreasing X-coordinate values.
- pixel number increases with increasing Y-coordinate values.
"""

"""
Rules for the generals_instrument block
    - String representing floats must contain decimal point symbol '.'
    - Strings representing string must be enclosed in double quotes
"""
generals_instrument = """
valid_from          "2019-01-01 00:00:00"
valid_to            "2100-12-31 23:59:59"
comment             "Created by Jose Borregero, borreguerojm@ornl.gov"
instrument_name     "EQSANS"
source-sample-distance 14.122
array_name          "detector1"
tube_length         1.046
tube_diameter       0.00805
pixels_per_tube     256
tube_separation     0.0110  # distance between consecutive tube axis
fourpack_separation 0.0082  # distance between front and back fourpacks
fourpack_slip       0.0055  # slip vector between the two fourpacks along X-axis
bank_radius         5.0     # distance between focal-point and anchor point
anchor_offset       0.0041  # add this to bank_radius for distance between focal-point and eightpack midline
eightpack_angle     0.5041  # angle subtended by each eightpack, in degrees
eightpack_quantity  24      # number of eight-packs in the detector array
"""


def assign_type(d):
    r"""Find out the type of each value in a dictionary

    Valid types: `str`, `int`, and `float`

    Rules:
        - String representing floats must contain '.'
        - Strings representing string must be enclosed in double quotes
"""
    for k, v in d.items():
        try:
            w = float(v)
            if '.' in v:
                d[k] = w
            else:
                d[k] = int(v)
        except:
            d[k] = v.strip('"')


def read_generals(gen):
    r"""Return a dictionary from a generals block

    Parameters
    ----------
    gen: str
        block comment with general options

    Returns
    -------
    dict
    """
    gen_dict = dict()
    for line in gen.split('\n'):
        if len(line) == 0:
            continue  # first and last lines are empty
        entry = line.split('#')[0].strip()  # remove comment and bracketing spaces
        key = entry.split()[0]
        gen_dict[key] = entry[len(key):].strip()
    assign_type(gen_dict)
    return gen_dict


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


def arc_detector(det, type_pack, radius, dtheta, population):
    r"""
    (r, t, p) positions for the eightpack components of a detector spanning
    an arc segment.

    Parameters
    ----------
    radius: float
        Radius of the arc
    dtheta: float
        Angle spanned by each eight-pack
    population: int
        Number of eight-packs

    Returns
    -------
    list
        List elements are the
    """


if __name__ == '__main__':
    bs = read_generals(generals_instrument)  # basic settings
    det = MantidGeom(bs['instrument_name'],
                     **kw(bs, 'comment', 'valid_from', 'valid_to'))
    defaults_element = det.addSnsDefaults(default_view="3D",
                                          axis_view_3d="Z-")

    fn = make_filename(*ag(bs, 'instrument_name', 'valid_from','valid_to'))

    add_comment_section(det, 'COMPONENT and TYPE: SOURCE AND SAMPLE POSITION')
    det.addModerator(-bs['source-sample-distance'])
    det.addSamplePosition()

    add_comment_section(det, 'TYPE: PIXEL FOR STANDARD 256 PIXEL TUBE')
    center_bottom_base = (0.0, 0.0, 0.0)
    pixel_axis = (0.0, 1.0, 0.0)
    pixel_radius = bs['tube_diameter'] / 2.0
    pixel_height = bs['tube_length'] / bs['pixels_per_tube']
    det.addCylinderPixel("pixel", center_bottom_base, pixel_axis,
                         pixel_radius, pixel_height)

    add_comment_section(det, 'TYPE: STANDARD 256 PIXEL TUBE')
    tube_type_name = 'tube'
    det.addPixelatedTube(tube_type_name, bs['pixels_per_tube'],
                         bs['tube_length'])

    add_comment_section(det, 'TYPE: FOUR-PACK')
    air_gap = bs['tube_separation'] - bs['tube_diameter']
    # negative diameter and air gaps to conform with ordering of tubes
    # in the Nexus embedded XML file
    det.addNPack('fourpack', 4, -bs['tube_diameter'], -air_gap,
                 type_name=tube_type_name)

    add_comment_section(det, 'TYPE: EIGHT-PACK')
    det.add_double_pack('eightpack', 'fourpack',
                      bs['fourpack_separation'], slip=-bs['fourpack_slip'])

    add_comment_section(det, 'TYPE: DETECTOR ARRAY')
    r = bs['bank_radius'] + bs['anchor_offset']
    # negative dtheta to conform with ordering of eightpacks in the Nexus
    # embedded XML file
    panel = det.add_curved_panel(bs['array_name'], 'eightpack',
                                 bs['eightpack_quantity'],
                                 r, -bs['eightpack_angle'])

    add_comment_section(det, 'COMPONENT: DETECTOR ARRAY')
    panel = det.addComponent(bs['array_name'], idlist='array_list',
                     blank_location=False)
    det.addLocation(panel, 0., 0., -r)

    add_comment_section(det, 'ID ranges for DETECTOR ARRAY')
    det.addDetectorIds('array_list', [0, bs['eightpack_quantity']*8*256 - 1, 1])

    det.writeGeom(fn)
