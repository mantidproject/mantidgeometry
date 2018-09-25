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

    """
    <!--STANDARD 8-PACK-->
    <type name="eightpack">
    <properties/>
    <component type="tube">
      <location x="0.0145075"  name="tube1"/>
      <location x="0.0103625"  name="tube2"/>
      <location x="0.0062175"  name="tube3"/>
      <location x="0.0020725"  name="tube4"/>
      <location x="-0.0020725" name="tube5"/>
      <location x="-0.0062175" name="tube6"/>
      <location x="-0.0103625" name="tube7"/>
      <location x="-0.0145075" name="tube8"/>
    </component>
    </type>
    """
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

    """
    <!--STANDARD 1.2m 128 PIXEL TUBE-->
    <type name="tube" outline="yes">
    <properties/>
    <component type="pixeltwo">
    <location y="-0.3845718750" name="pixel1"/>
    <location y="-0.3815556250" name="pixel2"/>
    <location y="-0.3785393750" name="pixel3"/>
    <location y="-0.3755231250" name="pixel4"/>
    <location y="-0.3725068750" name="pixel5"/>
    <location y="-0.3694906250" name="pixel6"/>
    <location y="-0.3664743750" name="pixel7"/>
    """
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
        type_element = le.SubElement(root, "type", name='tube', outline='yes')
        le.SubElement(type_element, "properties")

        # add component
        component_root = le.SubElement(type_element, 'component', type='pixel')

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

        Args:
            root:
            name:
            component_name:
            x:
            y:
            z:
            rot:

        Returns:

        """
        # type
        pack_root = le.SubElement(root, 'type', name=name)
        # component
        component = le.SubElement(pack_root, 'component', type=component_name)
        # add location
        self.addLocation(root=component, x=x, y=y, z=z, rot_y=rot, rot_z=rot)

        return

    def add_n_8packs_type(self, root, name, num_tubes, tube_x):
        """

        Args:
            name:
            num_tubes:
            tube_x:

        Returns:

        """
        packs_root = le.SubElement(root, 'type', name=name)
        le.SubElement(packs_root, 'properties')

        comp_root = le.SubElement(packs_root, 'component', type='tube')

        tube_x_pos = (-num_tubes/2)*tube_x + tube_x * 0.5
        for tube_index in range(1, num_tubes + 1):
            le.SubElement(comp_root, 'location', name='tube{}'.format(tube_index), x='{}'.format(tube_x_pos))
            tube_x_pos += tube_x
        # END-FOR

        return

    def add_cylinder_pixel(self, root, axis, radius=0.0047, height=0.0063578125):
        """

        Args:
            axis:
            radius:
            height:

        Returns:

        """
        pixel_root = le.SubElement(root, 'type', **{'is': 'detector', 'name': 'pixel'})
        # cylinder
        cylinder_root = le.SubElement(pixel_root, 'cylinder', id='cyl-approx')

        le.SubElement(cylinder_root, 'centre-of-bottom-base', p='0.0', r='0.0', t='0.0')
        le.SubElement(cylinder_root, 'axis', x=str(axis[0]), y=str(axis[1]), z=str(axis[2]))
        le.SubElement(cylinder_root, 'radius', val='{}'.format(radius))
        le.SubElement(cylinder_root, 'height', val='{}'.format(height))

        le.SubElement(pixel_root, 'algebra', val='cyl-approx')

        return
