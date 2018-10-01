from __future__ import (print_function)
from lxml import etree as le  # python-lxml on rpm based systems
from helper import MantidGeom


class VulcanGeomIDF(MantidGeom):
    """
    An extended class from MantidGeom tailored for VULCAN
    """
    def __init__(self, instname, comment=None, valid_from=None, valid_to=None):
        """
        initialization
        :param instname: name of instrument
        :param comment: comment
        :param valid_from: beginning date
        :param valid_to: end date
        """
        super(VulcanGeomIDF, self).__init__(instname, comment, valid_from, valid_to)

        return

    def add_8pack_group(self, num_8packs, start_pid, pid_gap, center_r, center_2theta, ):
        """
        add a group with 8 packs
        :return:
        """
        # 1. add component with type = "Group3"

        # 2. define of type "Group3" ... polar coordinate with rotation
        # 2a. define component bank4 with idstart, r, 2theta and etc.

        # 3. define type "bank4"
        # 3a. define components

        return

    @staticmethod
    def add_eight_pack_type(root, pixel_width=0.004145):
        """
        Add a type definition for 8 pack
        :return:
        """
        # define type as root
        type_element = le.SubElement(root, "type", name='eightpack')
        le.SubElement(type_element, "properties")

        # add component
        component_root = le.SubElement(type_element, "component", type='tube')

        x_pos = -3.5 * pixel_width
        # even and odd y position of tube
        z_pos_list = [-0.009999,  0.00999]    # TODO - 2018-09-23 - find out the difference between Y
        for tube_id in range(1, 9):
            # loop from tube 0 to tube 9
            tube_name = 'tube{}'.format(tube_id)
            z_pos = z_pos_list[(tube_id+1) % 2]
            le.SubElement(component_root, 'location', x='{}'.format(x_pos), z='{}'.format(z_pos),
                          name=tube_name)
            x_pos += pixel_width
        # END-FOR

        return

    @staticmethod
    def add_tube_type(root, pixel_height, num_pixels):
        """
        add a tube (of eight packs) type definition
        :param root:
        :param pixel_height:
        :param num_pixels:
        :return:
        """
        # define type as root
        type_element = le.SubElement(root, "type", name='tube{}'.format(num_pixels), outline='yes')
        le.SubElement(type_element, "properties")

        # add component
        component_root = le.SubElement(type_element, 'component', type='pixel{}tube'.format(num_pixels))

        y_pos = -(num_pixels/2 - 0.5) * pixel_height
        for pixel_id in range(1, num_pixels+1):
            # loop from tube 0 to tube 9
            pixel_name = 'pixel{}'.format(pixel_id)
            le.SubElement(component_root, 'location', y='{}'.format(y_pos),
                          name=pixel_name)
            y_pos += pixel_height
        # END-FOR

        return

    def add_banks_type(self, root, name, components):
        """

        Args:
            root:
            name: example: detectors
            components: example: ['bank1', 'bank4']

        Returns:

        """
        bank_root = le.SubElement(root, 'type', name=name)

        for component_name in components:
            comp_root = le.SubElement(bank_root, 'component', type=component_name)
            le.SubElement(comp_root, 'location')

        return

    def add_bank(self, root, name, component_name, x, y, z, rot):
        """
        add a bank
        :param root:
        :param name:
        :param component_name:
        :param x:
        :param y:
        :param z:
        :param rot: rotation angle in degree
        :return:
        """
        # type
        pack_root = le.SubElement(root, 'type', name=name)
        # component
        component = le.SubElement(pack_root, 'component', type=component_name)
        # add location
        self.addLocation(root=component, x=x, y=y, z=z, rot_y=rot, rot_z=0)

        return

    def add_n_8packs_type(self, root, name, num_tubes, tube_x, num_tube_pixels):
        """ add an N x 8packs type
        :param root:
        :param name:
        :param num_tubes:
        :param tube_x:
        :param num_tube_pixels: number of tubes in order to s
        :return:
        """
        packs_root = le.SubElement(root, 'type', name=name)
        le.SubElement(packs_root, 'properties')

        comp_root = le.SubElement(packs_root, 'component', type='tube{}'.format(num_tube_pixels))

        tube_x_pos = (-num_tubes/2)*tube_x + tube_x * 0.5
        for tube_index in range(1, num_tubes + 1):
            le.SubElement(comp_root, 'location', name='tube{}'.format(tube_index), x='{}'.format(tube_x_pos))
            tube_x_pos += tube_x
        # END-FOR

        return

    def add_cylinder_pixel(self, root, axis, radius=0.0047, height=0.0063578125, is_monitor=False,
                           pixel_name=None):
        """ add a cylinder pixel
        :param root:
        :param axis:
        :param radius:
        :param height:
        :param is_monitor:
        :param pixel_name:
        :return:
        """
        if is_monitor:
            is_type = 'monitor'
            name = 'monitor'
        else:
            is_type = 'detector'
            name = pixel_name
        pixel_root = le.SubElement(root, 'type', **{'is': is_type, 'name': name})
        # cylinder
        cylinder_root = le.SubElement(pixel_root, 'cylinder', id='cyl-approx')

        le.SubElement(cylinder_root, 'centre-of-bottom-base', p='0.0', r='0.0', t='0.0')
        le.SubElement(cylinder_root, 'axis', x=str(axis[0]), y=str(axis[1]), z=str(axis[2]))
        le.SubElement(cylinder_root, 'radius', val='{}'.format(radius))
        le.SubElement(cylinder_root, 'height', val='{}'.format(height))

        le.SubElement(pixel_root, 'algebra', val='cyl-approx')

        return

    def add_monitor_type(self, root):
        """

        Args:
            root:

        Returns:

        """
        type_root = le.SubElement(root, 'type', name='monitors')
        le.SubElement(type_root, 'component', type='monitor')

    def define_id_list(self, root, id_name, start_id, end_id):
        """ add an entry as the ID list
        :param XML root:
        :param id_name:
        :param start_id:
        :param end_id:
        :return:
        """
        id_list_root = le.SubElement(root, 'idlist', idname=id_name)
        if start_id is not None and end_id is not None:
            le.SubElement(id_list_root, 'id', start='{}'.format(start_id), end='{}'.format(end_id))

        return

    def define_detector_parameters(self, root):
        """ (Hard code) define the detector's parameters
        :param root:
        :return:
        """
        comp_link_root = le.SubElement(root, 'component-link', name='detectors')

        # tube pressure
        param_root = le.SubElement(comp_link_root, 'parameter', name='tube_pressure')
        le.SubElement(param_root, 'value', units='atm', val='6.0')

        # tube thickness
        param_root = le.SubElement(comp_link_root, 'parameter', name='tube_thickness')
        le.SubElement(param_root, 'value', units='metre', val='0.0008')

        # tube temperature
        param_root = le.SubElement(comp_link_root, 'parameter', name='tube_temperature')
        le.SubElement(param_root, 'value', units='K', val='290.0')
