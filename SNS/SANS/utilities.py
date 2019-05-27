#!/usr/bin/python3
import math
import numpy as np
from dateutil.parser import parse as parse_date
from collections import OrderedDict
from lxml import etree as le  # python-lxml on rpm based systems


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


def add_source_and_sample(det, ssd):
    r"""

    Parameters
    ----------
    det: MantidGeom
    ssd: float
        Distance between source and sample
    """
    add_comment_section(det, 'COMPONENT and TYPE: SOURCE AND SAMPLE POSITION')
    det.addModerator(-ssd)
    det.addSamplePosition()


def add_pixel_type(det, diameter, height):
    r"""

    Parameters
    ----------
    det: MantidGeom
    diameter: float
        Pixel diameter
    height: float
        Effective pixel height
    """
    add_comment_section(det, 'TYPE: PIXEL FOR STANDARD 256 PIXEL TUBE')
    center_bottom_base = (0.0, 0.0, 0.0)
    pixel_axis = (0.0, 1.0, 0.0)
    det.addCylinderPixel("pixel", center_bottom_base, pixel_axis,
                         diameter / 2.0, height)


def add_tube_type(det, length, n_pixels):
    add_comment_section(det, 'TYPE: STANDARD 256 PIXEL TUBE')
    det.addPixelatedTube('tube', n_pixels, length)


def add_fourpack_type(det, diameter, separation):
    add_comment_section(det, 'TYPE: FOUR-PACK')
    air_gap = separation - diameter
    # negative diameter and air gaps to conform with ordering of tubes
    # in the Nexus embedded XML file
    det.addNPack('fourpack', 4, -diameter, -air_gap, type_name='tube')


def add_basic_types(det, iinfo):
    add_source_and_sample(det, iinfo['source_sample_distance'])
    add_pixel_type(det, iinfo['tube_diameter'],
                   iinfo['tube_length'] / iinfo['pixels_per_tube'])
    add_tube_type(det, iinfo['tube_length'], iinfo['pixels_per_tube'])
    add_fourpack_type(det, iinfo['tube_diameter'], iinfo['tube_separation'])


def add_flat_panel_type(det, num_elem, width, gap, type_elem='fourpack',
                        name_elem=None, first_index=1, assemb_type='panel'):
    r"""

    Parameters
    ----------
    det: MantidGeom
    num_elem: int
        Number of elements making up the panel
    width: float
        Size of each element making up the panel
    gap: float
        Separation between consecutive elements making up the panel
    type_elem: str
        Type of the elements making up the panel
    name_elem: str
        Root name of the elements making up the panel. Use `type_elem`
        if None
    first_index: int
        Elements are named as `name_elem{i}` with
        `first_index <= i <= first_index + num_elem`
    assemb_type: str
        Type of the assembly of elements
    Returns
    -------
    lxml.etree.subelement
        Handle to the flat panel object
    """
    add_comment_section(det, 'TYPE: FLAT PANEL')
    assembly = le.SubElement(det.root, 'type', name=assemb_type)
    le.SubElement(assembly, 'properties')
    component = le.SubElement(assembly, 'component', type=type_elem)
    effective_width = width + gap
    pack_start = (effective_width / 2.0) * (1 - num_elem)
    for i in range(num_elem):
        kwargs = dict(name=f'{name_elem}{first_index+i}',
                      x=str(pack_start + (i * effective_width)))
        le.SubElement(component, 'location', **kwargs)
    return assembly


def add_double_pack(det, assembly_type, pack_type, separation, slip=0.0):
    r"""
    Place two packs of the same type along their normal, like two slices
    of the same type of bread making a sandwich.

    For instance, SNS-EQSANS, HFIR-BIOSANS, HFIR-GPSANS
    use double four-packs

    Parameters
    ----------
    assembly_type: str
        Type name of the resulting dual pack
    pack_type: str
        Type name of each pack
    separation: float
        Distance between the two packs along their
        normal (usually the Z-axis)
    slip: float
        Distance between the two packs along the axis perpendicular to
        the tubes axis and pack normal (usually the X-axis)
    """
    assembly = le.SubElement(det.root, 'type', name=assembly_type)
    le.SubElement(assembly, 'properties')
    component = le.SubElement(assembly, 'component', type=pack_type)
    pack_start_z = -separation / 2.0
    pack_start_x = -slip / 2.0
    prefix = ('front', 'back')
    for i in range(2):
        kwargs = dict(name=f'{prefix[i]}-{pack_type}',
                      x=str(pack_start_x + slip * i),
                      z=str(pack_start_z + separation * i))
        le.SubElement(component, 'location', **kwargs)
    return assembly


def add_double_flat_panel_type(det, iinfo):
    r"""

    Parameters
    ----------
    det
    iinfo

    Returns
    -------
    lxml.etree.subelement
        Handle to the double panel type
    """
    width = 3 * iinfo['tube_separation']
    args = [det, iinfo['number_eightpacks'], width, iinfo['tube_separation']]
    # Insert type for front panel
    kwargs = dict(name_elem=iinfo['bank_name'], first_index=1,
                  assemb_type=iinfo['flat_panel_types']['front'])
    add_flat_panel_type(*args, **kwargs)
    # Insert type for back panel
    kwargs = dict(name_elem=iinfo['bank_name'], first_index=1 + iinfo['number_eightpacks'],
                  assemb_type=iinfo['flat_panel_types']['back'])
    add_flat_panel_type(*args, **kwargs)
    # Insert type for double flat panel type
    add_comment_section(det, 'TYPE: DOUBLE FLAT PANEL')
    double_panel = le.SubElement(det.root, 'type', name='double-flat-panel')
    x = iinfo['fourpack_slip'] / 2
    z = iinfo['fourpack_separation'] / 2
    le.SubElement(double_panel, 'properties')
    front_panel = le.SubElement(double_panel, 'component', type='front-panel')
    det.addLocation(front_panel, -x, 0., -z)
    back_panel = le.SubElement(double_panel, 'component', type='back-panel')
    det.addLocation(back_panel, x, 0., z)
    return double_panel


def add_double_flat_panel_component(double_panel, idlist, det, name):
    r"""

    Parameters
    ----------
    double_panel
    idlist
    det
    name

    Returns
    -------
    lxml.etree.subelement
        Handle to the double panel component
    """
    add_comment_section(det, 'COMPONENT: DOUBLE FLAT PANEL')
    kwargs = dict(type=double_panel.attrib['name'], idlist=idlist, name=name)
    comp = le.SubElement(det.root, 'component', **kwargs)
    det.addLocation(comp, 0., 0., 0)
    return comp


def add_curved_panel_type(det, num_elem, radius, dtheta, theta_0=0.,
                          type_elem='fourpack', name_elem=None, first_index=1,
                          assemb_type='panel'):
    r"""

    Parameters
    ----------
    det: MantidGeom
    num_elem: int
        Number of elements making up the panel
    radius: float
        Radius of the circle arc
    dtheta: float
        Angle separation between consecutive subelements
    theta_0: float
        Additional angle shift for the angular position of the subelements
    type_elem: str
        Type of the elements making up the panel
    name_elem: str
        Root name of the elements making up the panel. Use `type_elem`
        if None
    first_index: int
        Elements are named as `name_elem{i}` with
        `first_index <= i <= first_index + num_elem`
    assemb_type: str
        Type of the assembly of elements

    Returns
    -------
    lxml.etree.subelement
        Handle to the curved panel object
    """
    add_comment_section(det, 'TYPE: CURVED PANEL')
    type_assembly = le.SubElement(det.root, 'type', name=assemb_type)
    le.SubElement(type_assembly, 'properties')
    component = le.SubElement(type_assembly, 'component', type=type_elem)
    theta_angles = dtheta * (0.5 + np.arange(num_elem)) -\
        num_elem * dtheta / 2 + theta_0
    rot = [f'{v:.4f}' for v in theta_angles]
    rot_axis = {'axis-x': '0', 'axis-y': '1', 'axis-z': '0'}
    for i in range(num_elem):
        kwargs = dict(name=f'{name_elem}{first_index+i}', r=str(radius),
                      t=rot[i], rot=rot[i])
        kwargs.update(rot_axis)
        le.SubElement(component, 'location', **kwargs)
    return type_assembly


def add_double_curved_panel_type(det, iinfo):
    r"""
    Create a type for the double curved panel using a type for the front
    and a type for the back  panels.

    The double panel is returned with its center at (0, 0, r) with `r`
    the radius of the curved panel

    Parameters
    ----------
    det: MantidGeom
    iinfo: dict
        Options for the instrument. Assumed to contain the following
        keys: bank_radius, anchor_offset, fourpack_separation, fourpack_slip,
        number_eightpacks, eightpack_angle, curved_panel_types

    Returns
    -------
    lxml.etree.subelement
        Handle to the double panel type
    """
    # distance from sample to the center of the eight-pack
    r_eightpack = iinfo['bank_radius'] + iinfo['anchor_offset']
    # shift by delta_r for distance from sample to either of the two fourpacks
    delta_r = iinfo['fourpack_separation'] / 2
    slip_angle = 180. / math.pi * iinfo['fourpack_slip'] / (2 * r_eightpack)
    # negative dtheta to conform with ordering of eightpacks in the Nexus
    # embedded XML file

    args = [det, iinfo['number_eightpacks'], r_eightpack - delta_r,
            -iinfo['eightpack_angle']]
    # Insert type for front panel
    kwargs = dict(name_elem=iinfo['bank_name'], theta_0=slip_angle,
                  assemb_type=iinfo['curved_panel_types']['front'])
    front = add_curved_panel_type(*args, **kwargs)
    # Insert type for back panel
    args = [det, iinfo['number_eightpacks'], r_eightpack + delta_r,
            -iinfo['eightpack_angle']]
    kwargs = dict(name_elem=iinfo['bank_name'], theta_0=-slip_angle,
                  assemb_type=iinfo['curved_panel_types']['back'],
                  first_index=1+iinfo['number_eightpacks'])
    back = add_curved_panel_type(*args, **kwargs)
    # Insert type for double panel
    add_comment_section(det, 'TYPE: DOUBLE CURVED PANEL')
    double_panel = le.SubElement(det.root, 'type', name='double-curved-panel')
    le.SubElement(double_panel, 'properties')
    front_panel = le.SubElement(double_panel, 'component',
                                type=front.attrib['name'])
    det.addLocation(front_panel, 0., 0., 0.)
    back_panel = le.SubElement(double_panel, 'component',
                               type=back.attrib['name'])
    det.addLocation(back_panel, 0., 0., 0.)
    return double_panel


def add_double_curved_panel_component(double_panel, idlist, det, name):
    r"""

    Parameters
    ----------
    double_panel
    idlist
    det
    name

    Returns
    -------

    """
    add_comment_section(det, 'COMPONENT: DOUBLE CURVED PANEL')
    kwargs = dict(type=double_panel.attrib['name'], idlist=idlist, name=name)
    comp = le.SubElement(det.root, 'component', **kwargs)
    return comp
