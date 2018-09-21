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

    def add_eight_pack(self):
        """
        modified from N pack
        :return:
        """
        type_element = le.SubElement(self.__root, "type", name=name)
        le.SubElement(type_element, "properties")

        component = le.SubElement(type_element, "component", type=type_name)

        effective_tube_width = tube_width + air_gap

        pack_start = (effective_tube_width / 2.0) * (1 - num_tubes)

        for i in range(8):
            tube_name = "tube%d" % (i + 1)
            x = pack_start + (i * effective_tube_width)
            location_element = le.SubElement(component, "location", name=tube_name, x=str(x))
            if (neutronic):
                if (neutronicIsPhysical):
                    le.SubElement(location_element, "neutronic", x=str(x))
                else:
                    le.SubElement(location_element, "neutronic", x="0.0")

            self.add_tube(i, delta_z)
        # END-FOR

        return

