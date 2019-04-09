import sys
import datetime
import helper

# Definition of constants
HB3A_L1 = 2.


HB2B_SETUP = {'L1': 2.678898,
              'L2': 0.95, # arm length
              'PixelNumber': {'1K': (1024, 1024), '2K': (2048, 2048)},
              'PixelSize': {'1K': 0.00029296875, '2K': 0.00029296875*0.5}
              }

XRAY_SETUP = {'L1': 2.678898,
              'L2': 0.416,  # arm length
              'PixelNumber': {'1K': (1024, 1024), '2K': (2048, 2048)},
              'PixelSize': {'1K': 0.0004000, '2K': 0.0004000*0.5}
              }


class HB2BGeometry(helper.MantidGeom):
    """
    HB3A geometry extended from MantidGeom
    """
    def __init__(self, instname, comment=None, valid_from=None, valid_to=None):
        """
        initialization
        :param instname: name of instrument
        :param comment: comment
        :param valid_from: beginning date
        :param valid_to: end date
        """
        super(HB2BGeometry, self).__init__(instname, comment, valid_from, valid_to)

        return

    def add_rectangular_detector(self, x_start, x_step, x_pixels,
                                 y_start, y_step, y_pixels,
                                 pixel_size_x, pixel_size_y, pixel_size_z):
        """
        """
        # add detector panel
        self.addRectangularDetector(name='panel', type='pixel',
                                    xstart='{}'.format(x_start), xstep='{}'.format(x_step),
                                    xpixels='{}'.format(x_pixels),
                                    ystart='{}'.format(y_start), ystep='{}'.format(y_step),
                                    ypixels='{}'.format(y_pixels))

        # add pixels
        self.addCuboidPixel(name='pixel', shape_id='pixel-shape',
                            lfb_pt=(pixel_size_x*0.5, -pixel_size_y*0.5, 0),  # left-front-bottom
                            lft_pt=(pixel_size_x*0.5, pixel_size_y*0.5, 0),  # left-front-top
                            lbb_pt=(pixel_size_x*0.5, -pixel_size_y*0.5, -pixel_size_z),  # left-back-bottom
                            rfb_pt=(-pixel_size_x*0.5, -pixel_size_y*0.5, 0)  # right-front-bottom
                            )

        return

# END-DEF-HB3A


def generate_1bank_2d_idf(instrument_name, geom_setup_dict, pixel_setup, output_idf_name):
    """ Generate the general HB2B (or similar X-Ray) IDF file from 2018.12.01
    :param instrument_name:
    :param geom_setup_dict:
    :param pixel_setup:
    :param output_idf_name:
    :return:
    """
    # generate instrument geometry object
    authors = ["Wenduo Zhou"]
    begin_date = '2018-12-01 00:00:01'
    end_date = '2100-10-20 23:59:59'

    # boiler plate stuff
    hb2b = HB2BGeometry(instrument_name,
                        comment="Created by " + ", ".join(authors),
                        valid_from=begin_date,
                        valid_to=end_date)

    # TODO/FIXME - NO HFIR Default
    # hb2b.addComment('DEFAULTS')
    # hb2b.addHfirDefaults()

    # source
    hb2b.addComment("SOURCE")
    hb2b.addModerator(geom_setup_dict['L1'])
    # sample
    hb2b.addComment("SAMPLE")
    hb2b.addSamplePosition()

    # TODO/FIXME - NO Default
    # monitor
    # hb2b.addComment("MONITORS")
    # hb2b.add_monitor_type()

    # Build 'arm'
    # define arm - component
    pixel_row_count, pixel_column_count = geom_setup_dict['PixelNumber'][pixel_setup]
    arm_loc_dict = dict()
    arm_loc_dict['r-position'] = {'value': 0.0}
    arm_loc_dict['t-position'] = {'value': 0.0}
    arm_loc_dict['p-position'] = {'value': 0.0}
    arm_loc_dict['roty'] = {'logfile': 'value+0.0', 'id': '2theta'}  # roty works as 2theta with experiment
    arm_node = hb2b.add_component(type_name='arm', idfillbyfirst='x', idstart=1, idstepbyrow=pixel_column_count)
    arm_loc_node = hb2b.add_location('bank1', arm_node, arm_loc_dict)

    # define type: arm
    # TODO - TONIGHT - Implement add_type
    arm_type_node = hb2b.add_type(type_name='arm')
    """
      <type name="arm">
	  <component type="panel">
		  <location>
			  <parameter name="z">
	                          <logfile eq="1.0*value+0.416" id="cal::arm"/>
			  </parameter>
                           <parameter name="rotx">
                             <logfile eq="value+0.0" id="cal::flip"/>
                           </parameter>
                          <parameter name="roty">
                            <logfile eq="value+0.0" id="cal::roty"/>
                          </parameter>
                          <parameter name="rotz">
                            <logfile eq="value+0.0" id="cal::spin"/>
                          </parameter>
		  </location>
	  </component>
  </type>
    """

    # define component panel under type arm
    panel_loc_dict = {'z': {'logfile': 'value+{}'.format(geom_setup_dict['L2']), 'id': 'cal::arm'},
                      'rotx': {'logfile': 'value+0.0', 'id': 'cal::flip'},
                      'roty': {'logfile': 'value+0.0', 'id': 'cal::roty'},
                      'rotz': {'logfile': 'value+0.0', 'id': 'cal::spin'},
                      }
    panel_node = hb2b.add_component(type_name='panel', parent=arm_type_node)
    hb2b.add_location(None, panel_node, panel_loc_dict)

    # hb2b.add_parameter('r-position', 0.0, arm_loc_node)

    # generate rectangular detector
    pixel_size_x = pixel_size_y = geom_setup_dict['PixelSize'][pixel_setup]
    x_start = (float(pixel_column_count)*0.5 - 0.5) * pixel_size_x
    x_step = - pixel_size_x
    y_start = -(float(pixel_row_count)*0.5 - 0.5) * pixel_size_y
    y_step = pixel_size_y
    hb2b.add_rectangular_detector(x_start=x_start, x_step=x_step, x_pixels=pixel_column_count,
                                  y_start=y_start, y_step=y_step, y_pixels=pixel_row_count,
                                  pixel_size_x=pixel_size_x, pixel_size_y=pixel_size_y,
                                  pixel_size_z=0.0001)


    hb2b.write_terminal()

    return

    # add detectors
    hb2b.addComment('Define detector banks')
    hb2b.addComponent(type_name='detectors', idlist='detectors')
    # define detector type
    hb2b.add_banks_type(name='detectors',
                        components=['bank1'])

    # define center bank
    hb2b.addComment('Define Centre Bank')
    hb2b.add_bank(name='bank1', component_name='square256detector',
                  x=2.0, y=0., z=0., rot=90)

    # 20 x 8 packs
    hb2b.addComment('256 x 256 pack')
    hb2b.angler_detector(name='square256detector', num_linear_pixel=256, tube_x=0.01)

    # write file
    hb2b.writeGeom(output_idf_name)

    return


def main(argv):
    """ Main
    :param argv:
    :return:
    """
    if len(argv) < 3:
        print ('Generate HB2B IDF: {} [hb2b [xray]] [1k [2k]]'.format(argv[0]))
        sys.exit(0)

    instrument = argv[1]
    if instrument == 'hb2b':
        geom_setup_dict = HB2B_SETUP
        instrument_name = 'HB2B'
    elif instrument == 'xray':
        geom_setup_dict = XRAY_SETUP
        instrument_name = 'XRAY'
    else:
        print ('[ERROR] Instrument {} is not supported.'.format(instrument))
        sys.exit(-1)

    # about the number of pixels setup
    pixel_setup = argv[2]
    if pixel_setup == '1k':
        pixel_setup = '1K'
    elif pixel_setup == '2k':
        pixel_setup = '2K'
    else:
        print ('[ERROR] Pixel setup {} is not supported.'.format(pixel_setup))

    # create instrument
    now = datetime.datetime.now()

    output_idf_name = '{}_Definition_{:04}{:02}{:02}_{:02}{:02}.xml' \
                      ''.format(instrument_name, now.year, now.month, now.day,
                                now.hour, now.minute)
    generate_1bank_2d_idf(instrument_name, geom_setup_dict, pixel_setup, output_idf_name)

    return


if __name__ == '__main__':
    main(sys.argv)
