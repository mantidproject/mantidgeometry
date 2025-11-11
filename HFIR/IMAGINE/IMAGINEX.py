"""
Generate an IDF-style XML instrument definition for IMAGINEX.
"""

from pathlib import Path
import argparse
import numpy as np


def generate_imaginex_xml(*, height: float = 0.12190399999999988,
                          distance: float = 0.34939881768689486,
                          pixelation: int = 512,
                          cols: int = 10,
                          rows: int = 8,
                          ts_west=None,
                          ts_east=None,
                          valid_from: str = "2025-10-01 00:00:00",
                          valid_to: str = "2100-01-31 23:59:59") -> str:
    """Return the IMAGINEX instrument XML as a string.

    Parameters mirror the original script defaults. `ts_west` and
    `ts_east` may be provided as lists of angles in radians; if omitted,
    the original defaults are used.
    """

    if ts_west is None:
        ts_west = [-2.9233986918473254, -2.5810842557247136, -2.238799595263872,
                   -1.8962564484452789, -1.5539094249485785]
    if ts_east is None:
        ts_east = [0.21819340287863892, 0.560508155423846, 0.902793058325921,
                   1.2453352898624561, 1.5876832769702256]

    header = f"""<?xml version='1.0' encoding='UTF-8'?>
<!-- For help on the notation used to specify an Instrument Definition File
     see http://www.mantidproject.org/IDF -->
<instrument xmlns="http://www.mantidproject.org/IDF/1.0"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://www.mantidproject.org/IDF/1.0 http://schema.mantidproject.org/IDF/1.0/IDFSchema.xsd"
            name="IMAGINE" valid-from   ="{valid_from}"
                           valid-to     ="{valid_to}"
                           last-modified="2025-10-02 00:00:01">
  <!--DEFAULTS-->
  <defaults>
    <length unit="metre"/>
    <angle unit="degree"/>
    <reference-frame>
      <along-beam axis="z"/>
      <pointing-up axis="y"/>
      <handedness val="right"/>
      <theta-sign axis="x"/>
    </reference-frame>
  </defaults>

  <!--SOURCE-->
  <component type="moderator">
    <location z="-3.0"/>
  </component>
  <type name="moderator" is="Source"/>

  <!--SAMPLE-->
  <component type="sample-position">
    <location y="0.0" x="0.0" z="0.0"/>
  </component>
  <type name="sample-position" is="SamplePos"/>

  <!--MONITORS-->
  <idlist idname="Downstream_monitor">
    <id val="-2"/>
  </idlist>
  <component type="Downstream_monitor" idlist="Downstream_monitor">
    <properties />
    <location  />
  </component>
  <type is="monitor" name="Downstream_monitor">
   <component type="monitor">
    <location x="0.0" y="0.0" z="0.4" name="monitor2" />
   </component>
  </type>

  <idlist idname="monitors">
    <id val="-1"/>
  </idlist>
  <component type="monitors" idlist="monitors">
    <location/>
  </component>
  <type is="monitor" name="monitors">
    <component type="monitor">
      <location x="0.0" y="0.0" z="-4.0" name="monitor1"/>
    </component>
  </type>

  <!--DETECTORS-->
"""

    footer_template = """<!-- Rectangular Detector Panel -->
  <type name="panel" is="rectangular_detector" type="pixel"
      xpixels="{pixelation}" xstart="{xstart}" xstep="{xstep}"
      ypixels="{pixelation}" ystart="{ystart}" ystep="{ystep}" >
    <properties/>
  </type>

  <!-- Pixel for Detectors-->
  <type is="detector" name="pixel">
    <cuboid id="pixel-shape">
      <left-front-bottom-point y="-{py}" x="-{px}" z="0.0"/>
      <left-front-top-point y="{py}" x="-{px}" z="0.0"/>
      <left-back-bottom-point y="-{py}" x="-{px}" z="-0.0001"/>
      <right-front-bottom-point y="{py}" x="{px}" z="0.0"/>
    </cuboid>
    <algebra val="pixel-shape"/>
  </type>

  <!-- Shape for Monitors-->
  <!-- TODO: Update to real shape -->
  <type is="monitor" name="monitor">
    <cylinder id="some-shape">
      <centre-of-bottom-base p="0.0" r="0.0" t="0.0"/>
      <axis y="0.0" x="0.0" z="1.0"/>
      <radius val="0.01"/>
      <height val="0.03"/>
    </cylinder>
    <algebra val="some-shape"/>
  </type>

</instrument>
"""

    # Build top header
    parts = [header]

    # Build bank/component blocks using original logic
    # follow the original ordering and values
    j = 0
    k = 0

    for col in range(1, cols + 1):
        if col <= 5:
            col_angle = ts_west[j]
            j += 1
        else:
            col_angle = ts_east[k]
            k += 1

        for row in range(1, rows + 1):
            comp = []
            comp.append(f'  <component type="bank{col}{row}">')
            comp.append(f'    <location x="{0}" y="{(-rows//2+row-0.5)*height}" z="{0}"/>')
            comp.append('  </component>')
            comp.append(f'  <type name="bank{col}{row}">')
            idstart = int((-1 + row) * pixelation ** 2 + (-1 + col) * pixelation ** 2 * rows)
            comp.append(f'    <component type="panel" idfillbyfirst="y" idstart="{idstart}" idstepbyrow="{pixelation}">')
            comp.append('      <location>')
            comp.append('        <parameter name="r-position">')
            comp.append(f'          <value val="{distance}"/>')
            comp.append('        </parameter>')
            comp.append('        <parameter name="t-position">')
            comp.append(f'          <value val="{col_angle*180/np.pi}"/>')
            comp.append('        </parameter>')
            comp.append('        <parameter name="roty">')
            comp.append(f'          <value val="{col_angle*180/np.pi}"/>')
            comp.append('        </parameter>')
            comp.append('      </location>')
            comp.append('    </component>')
            comp.append('  </type>')
            comp.append('')
            parts.append('\n'.join(comp))

    # footer values
    pixel_height = float(height / pixelation)
    footer = footer_template.format(pixelation=pixelation, xstart=-height/2, xstep=height/pixelation,
                                    ystart=-height/2, ystep=height/pixelation, px=height/pixelation, py=height/pixelation)

    parts.append(footer)

    return "\n".join(parts)


def main():
    parser = argparse.ArgumentParser(description="Generate IMAGINEX instrument XML.")
    parser.add_argument("-o", "--output", type=Path, default=Path("IMAGINE_Definition.xml"), help="Output file path")
    parser.add_argument("--height", type=float, default=0.12190399999999988)
    parser.add_argument("--distance", type=float, default=0.34939881768689486)
    parser.add_argument("--pixelation", type=int, default=512)
    parser.add_argument("--cols", type=int, default=10)
    parser.add_argument("--rows", type=int, default=8)
    args = parser.parse_args()

    xml_text = generate_imaginex_xml(height=args.height, distance=args.distance,
                                     pixelation=args.pixelation, cols=args.cols, rows=args.rows)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(xml_text, encoding="utf-8")


if __name__ == "__main__":
    main()
# import mantid algorithms, numpy and matplotlib
from mantid.simpleapi import *
import matplotlib.pyplot as plt
import numpy as np

filename = '/HFIR/CG4D/shared/instrument/IMAGINE_Definition.xml'

height = 0.12190399999999988
distance = 0.34939881768689486
pixelation = 512

cols = 10
rows = 8

ts_west = [-2.9233986918473254, -2.5810842557247136, -2.238799595263872, -1.8962564484452789, -1.5539094249485785]
ts_east = [0.21819340287863892, 0.560508155423846, 0.902793058325921, 1.2453352898624561, 1.5876832769702256]

header = """<?xml version='1.0' encoding='UTF-8'?>
<!-- For help on the notation used to specify an Instrument Definition File
     see http://www.mantidproject.org/IDF -->
<instrument xmlns="http://www.mantidproject.org/IDF/1.0"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://www.mantidproject.org/IDF/1.0 http://schema.mantidproject.org/IDF/1.0/IDFSchema.xsd"
            name="IMAGINE" valid-from   ="2025-10-01 00:00:00"
                           valid-to     ="2100-01-31 23:59:59"
		           last-modified="2025-10-02 00:00:01">
  <!--DEFAULTS-->
  <defaults>
    <length unit="metre"/>
    <angle unit="degree"/>
    <reference-frame>
      <along-beam axis="z"/>
      <pointing-up axis="y"/>
      <handedness val="right"/>
      <theta-sign axis="x"/>
    </reference-frame>
  </defaults>

  <!--SOURCE-->
  <component type="moderator">
    <location z="-3.0"/>
  </component>
  <type name="moderator" is="Source"/>

  <!--SAMPLE-->
  <component type="sample-position">
    <location y="0.0" x="0.0" z="0.0"/>
  </component>
  <type name="sample-position" is="SamplePos"/>

  <!--MONITORS-->
  <idlist idname="Downstream_monitor">
    <id val="-2"/>
  </idlist>
  <component type="Downstream_monitor" idlist="Downstream_monitor">
    <properties />
    <location  />
  </component>
  <type is="monitor" name="Downstream_monitor">
   <component type="monitor">
    <location x="0.0" y="0.0" z="0.4" name="monitor2" />
   </component>
  </type>

  <idlist idname="monitors">
    <id val="-1"/>
  </idlist>
  <component type="monitors" idlist="monitors">
    <location/>
  </component>
  <type is="monitor" name="monitors">
    <component type="monitor">
      <location x="0.0" y="0.0" z="-4.0" name="monitor1"/>
    </component>
  </type>

  <!--DETECTORS-->
  """

footer = """<!-- Rectangular Detector Panel -->
  <type name="panel" is="rectangular_detector" type="pixel"
      xpixels="{}" xstart="{}" xstep="{}"
      ypixels="{}" ystart="{}" ystep="{}" >
    <properties/>
  </type>

  <!-- Pixel for Detectors-->
  <type is="detector" name="pixel">
    <cuboid id="pixel-shape">
      <left-front-bottom-point y="-{}" x="-{}" z="0.0"/>
      <left-front-top-point y="{}" x="-{}" z="0.0"/>
      <left-back-bottom-point y="-{}" x="-{}" z="-0.0001"/>
      <right-front-bottom-point y="{}" x="{}" z="0.0"/>
    </cuboid>
    <algebra val="pixel-shape"/>
  </type>

  <!-- Shape for Monitors-->
  <!-- TODO: Update to real shape -->
  <type is="monitor" name="monitor">
    <cylinder id="some-shape">
      <centre-of-bottom-base p="0.0" r="0.0" t="0.0"/>
      <axis y="0.0" x="0.0" z="1.0"/>
      <radius val="0.01"/>
      <height val="0.03"/>
    </cylinder>
    <algebra val="some-shape"/>
  </type>

</instrument>
""".format(pixelation, -height/2, height/pixelation, pixelation, -height/2, height/pixelation, height/pixelation, height/pixelation, height/pixelation, height/pixelation, height/pixelation, height/pixelation, height/pixelation, height/pixelation)

f = open(filename, 'w')
f.write(header)
f.write('\n')

# if col <= 5:
#     col_angle = np.pi+2*np.arcsin(0.5*height/distance)*(col-1)+np.arcsin(0.5*height/distance)
# else:
#     col_angle = 0+2*np.arcsin(0.5*height/distance)*(col-6)+np.arcsin(0.5*height/distance)

j = 0
k = 0

for col in range(1,cols+1):

    if col <= 5:
        col_angle = ts_west[j] # backward
        j += 1
    else:
        col_angle = ts_east[k] # forward
        k += 1

    for row in range(1,rows+1):

        f.write('  <component type="bank{}{}">\n'.format(col,row))
        f.write('    <location x="{}" y="{}" z="{}"/>\n'.format(0,(-rows//2+row-0.5)*height,0))
        # f.write('      <rot axis-x="0" axis-y="1" axis-z="0" val="{}">\n'.format(col_angle*180/np.pi))
        # f.write('        <rot axis-x="1" axis-y="0" axis-z="0" val="0">\n')
        # f.write('          <rot axis-x="0" axis-y="0" axis-z="1" val="0"/>\n')
        # f.write('        </rot>\n')
        # f.write('      </rot>\n')
        f.write('  </component>\n')

        f.write('  <type name="bank{}{}">\n'.format(col,row))
        f.write('    <component type="panel" idfillbyfirst="y" idstart="{}" idstepbyrow="{}">\n'.format((-1+row)*pixelation**2+(-1+col)*pixelation**2*rows,pixelation))
        f.write('      <location>\n')
        f.write('        <parameter name="r-position">\n')
        f.write('          <value val="{}"/>\n'.format(distance))
        f.write('        </parameter>\n')
        f.write('        <parameter name="t-position">\n')
        f.write('          <value val="{}"/>\n'.format(col_angle*180/np.pi))
        f.write('        </parameter>\n')
        f.write('        <parameter name="roty">\n')
        f.write('          <value val="{}"/>\n'.format(col_angle*180/np.pi))
        f.write('        </parameter>\n')
        # f.write('        <parameter name="r-position">\n')
        # f.write('          <logfile eq="value/1000" id="{}_trans"/>\n'.format(panel))
        # f.write('        </parameter>\n')
        # f.write('        <parameter name="t-position">\n')
        # f.write('          <logfile eq="value" id="{}_2theta"/>\n'.format(panel))
        # f.write('        </parameter>\n')
        # f.write('        <parameter name="roty">\n')
        # f.write('          <logfile eq="value" id="{}_2theta"/>\n'.format(panel))
        # f.write('        </parameter>\n')
        f.write('      </location>\n')
        f.write('    </component>\n')
        f.write('  </type>\n')
        f.write('\n')

f.write(footer)
f.close()