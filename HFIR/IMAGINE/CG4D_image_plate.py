"""
Generate an IDF-style XML instrument definition for the CG4D image plate.
"""

from pathlib import Path
import argparse
import numpy as np


def generate_cg4d_xml(path: Path, *, height: float = 0.45, radius: float = 0.2, cols: int = 5000, rows: int = 1800, banks: int = 50) -> str:
    """Return the XML text for the instrument definition.

    Parameters are the same as the original script. The returned string
    should be written to a file by the caller.
    """

    header = (
        "<?xml version='1.0' encoding='UTF-8'?>\n"
        "<instrument xmlns=\"http://www.mantidproject.org/IDF/1.0\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" "
        "name=\"CG4D\" valid-from=\"2000-01-01 00:00:00\" valid-to=\"2025-09-30 23:59:59\" "
        "last-modified=\"2025-10-02 12:00:00\" xsi:schemaLocation=\"http://www.mantidproject.org/IDF/1.0 http://schema.mantidproject.org/IDF/1.0/IDFSchema.xsd\">\n"
        "  <!--Created by Zachary Morgan-->\n"
        "  <!--DEFAULTS-->\n"
        "  <defaults>\n"
        "    <length unit=\"metre\"/>\n"
        "    <angle unit=\"degree\"/>\n"
        "    <reference-frame>\n"
        "      <along-beam axis=\"z\"/>\n"
        "      <pointing-up axis=\"y\"/>\n"
        "      <handedness val=\"right\"/>\n"
        "      <theta-sign axis=\"x\"/>\n"
        "    </reference-frame>\n"
        "  </defaults>\n"
        "  <!--SOURCE-->\n"
        "  <component type=\"moderator\">\n"
        "    <location z=\"-3.0\"/>\n"
        "  </component>\n"
        "  <type name=\"moderator\" is=\"Source\"/>\n"
        "  <!--SAMPLE-->\n"
        "  <component type=\"sample-position\">\n"
        "    <location y=\"0.0\" x=\"0.0\" z=\"0.0\"/>\n"
        "  </component>\n"
        "  <type name=\"sample-position\" is=\"SamplePos\"/>\n"
        "  <!--DETECTORS-->\n"
    )

    wire_template = '      <location name="wire{}" x="{}" z="{}"/>\n'
    pixel_template = '      <location name="pixel{}" y="{}"/>\n'

    footer_lines = []
    footer_lines.append("<!-- Cylindrical Detector Panel -->")
    footer_lines.append("  <type name=\"panel\">")
    footer_lines.append("    <properties/>")
    footer_lines.append("    <component type=\"wire\">")

    t = np.linspace(-180 / banks, 180 / banks, cols // banks + 1)
    for col in range(cols // banks):
        theta = np.deg2rad((t[col] + t[col + 1]) / 2)
        z, x = radius * (np.cos(theta) - 1), radius * np.sin(theta)
        footer_lines.append(wire_template.format(col + 1, x, z))

    footer_lines.append("    </component>")
    footer_lines.append("  </type>")
    footer_lines.append("  <!--45CM WIRE 1800 PIXELS-->")
    footer_lines.append('  <type name="wire" outline="yes">')
    footer_lines.append('    <properties/>')
    footer_lines.append('    <component type="pixel">')

    y = np.linspace(-height / 2, height / 2, rows + 1)
    for row in range(rows):
        footer_lines.append(pixel_template.format(row + 1, (y[row] + y[row + 1]) / 2))

    pixel_radius = 2 * np.pi * radius / cols
    pixel_height = float(np.diff(y).mean())

    footer_lines.append('    </component>')
    footer_lines.append('  </type>')
    footer_lines.append('  <!--PIXEL FOR WIRE-->')
    footer_lines.append('  <type is="detector" name="pixel">')
    footer_lines.append('    <cylinder id="cyl-approx">')
    footer_lines.append('      <centre-of-bottom-base p="0.0" r="0.0" t="0.0"/>')
    footer_lines.append('      <axis x="0.0" y="1.0" z="0.0"/>')
    footer_lines.append(f'      <radius val="{pixel_radius}"/>')
    footer_lines.append(f'      <height val="{pixel_height}"/>')
    footer_lines.append('    </cylinder>')
    footer_lines.append('    <algebra val="cyl-approx"/>')
    footer_lines.append('  </type>')
    footer_lines.append('  <!--DETECTOR IDs-->')

    # idlist blocks per bank
    for bank in range(banks):
        start = 1 + rows * cols // banks * bank
        end = rows * cols // banks * (bank + 1)
        footer_lines.append(f'  <idlist idname="bank{bank+1}">')
        footer_lines.append(f'    <id end="{end}" start="{start}"/>')
        footer_lines.append('  </idlist>')

    footer_lines.append('  <!--MONITOR IDs-->')
    footer_lines.append('  <idlist idname="monitors">')
    footer_lines.append('    <id val="-1"/>')
    footer_lines.append('  </idlist>')
    footer_lines.append('</instrument>')

    return header + "\n" + "\n".join(footer_lines)


def main():
    parser = argparse.ArgumentParser(description="Generate CG4D image plate IDF XML.")
    parser.add_argument("-o", "--output", type=Path, default=Path("CG4D_Definition.xml"), help="Output file path")
    parser.add_argument("--height", type=float, default=0.45)
    parser.add_argument("--radius", type=float, default=0.2)
    parser.add_argument("--cols", type=int, default=5000)
    parser.add_argument("--rows", type=int, default=1800)
    parser.add_argument("--banks", type=int, default=50)

    args = parser.parse_args()

    xml_text = generate_cg4d_xml(args.output, height=args.height, radius=args.radius, cols=args.cols, rows=args.rows, banks=args.banks)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(xml_text, encoding="utf-8")


if __name__ == "__main__":
    main()
