import numpy as np

filename = '/HFIR/CG4D/shared/instrument/CG4D_Definition.xml'

height = 0.45
radius = 0.2

p = 2*np.pi*radius

cols = 5000
rows = 1800

banks = 50

header = """\
<?xml version='1.0' encoding='UTF-8'?>
<instrument xmlns="http://www.mantidproject.org/IDF/1.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" name="CG4D" valid-from="2000-01-01 00:00:00" valid-to="2025-09-30 23:59:59" last-modified="2025-10-02 12:00:00" xsi:schemaLocation="http://www.mantidproject.org/IDF/1.0 http://schema.mantidproject.org/IDF/1.0/IDFSchema.xsd">
  <!--Created by Zachary Morgan-->
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
  <!--DETECTORS-->
  """
  
wire = """      <location name="wire{}" x="{}" z="{}"/>\n"""
pixel = """      <location name="pixel{}" y="{}"/>\n"""

footer = """<!-- Cylindrical Detector Panel -->\
  <type name="panel">
    <properties/>
    <component type="wire">
    """    

t = np.linspace(-180 / banks, 180 / banks, cols // banks + 1)

for col in range(cols // banks):
    theta = np.deg2rad((t[col] + t[col + 1])/2)
    z, x = radius * (np.cos(theta) - 1), radius * np.sin(theta)
    footer += wire.format(col + 1, x, z)

footer += """\
    </component>
  </type>
  <!--45CM WIRE 1800 PIXELS-->
  <type name="wire" outline="yes">
    <properties/>
    <component type="pixel">
"""

y = np.linspace(-height / 2, height / 2, rows + 1)

for row in range(rows):
    footer += pixel.format(row + 1, (y[row] + y[row + 1])/2)

footer += """\
    </component>
  </type>
  <!--PIXEL FOR WIRE-->
  <type is="detector" name="pixel">
    <cylinder id="cyl-approx">
      <centre-of-bottom-base p="0.0" r="0.0" t="0.0"/>
      <axis x="0.0" y="1.0" z="0.0"/>
      <radius val="{}"/>
      <height val="{}"/>
    </cylinder>
    <algebra val="cyl-approx"/>
  </type>
  <!--DETECTOR IDs-->
""".format(2 * np.pi * radius / cols, np.diff(y).mean())

bank_no = \
"""
  <idlist idname="bank{}">
    <id end="{}" start="{}"/>
  </idlist>
"""

for bank in range(banks):
    footer += bank_no.format(bank + 1, rows * cols // banks * (bank + 1),  1 + rows * cols // banks * bank)

footer += """\
  <!--MONITOR IDs-->
  <idlist idname="monitors">
    <id val="-1"/>
  </idlist>
</instrument>
"""

f = open(filename, 'w')
f.write(header)
f.write('\n')

bank_lines = """\
  <component idlist="bank{}" type="bank{}">
    <location>
      <parameter name="y">
        <value val="{}"/>
      </parameter>
    </location>
  </component>
  <type name="bank{}">
    <component type="panel">
      <location>
        <parameter name="r-position">
          <value val="{}"/>
        </parameter>
        <parameter name="t-position">
          <value val="{}"/>
        </parameter>
        <parameter name="roty">
          <value val="{}"/>
        </parameter>
      </location>
    </component>
  </type>
"""

t = np.linspace(-180, 180, banks + 1)

for bank in range(banks):
    f.write(bank_lines.format(bank + 1, bank + 1, 0, bank + 1, radius, (t[bank] + t[bank + 1]) / 2, (t[bank] + t[bank + 1]) / 2))

f.write(footer)
f.close()
