#!/usr/bin/env python3

"""VULCAN has undergone a phased upgrade.
Phase I added a single additional bank (bank5) with total No. banks = 3
Phase II added three additional banks, and moved bank5, total No. banks = 6

Thus, note, bank numbering is not inspired by chronology, or geometry
here's a rough sketch from above, dashed line is beam, + is inst centre point.

Phase I:
              |
              |   5
              |
      1       +       2
              |
              |
              V

Phase II:
              |
          5   |   4
              |     3
      1       +       2
        6     |
              |
              V

this script generates the IDF for phase II
"""


import logging
import numpy as np
import pandas as pd
from lxml import etree as le  # python-lxml on rpm based systems
from helper import INCH_TO_METRE, MantidGeom
from rectangle import Rectangle, makeLocation


# -----------------------------------------------------------------------------
# CONSTANTS (subject to change with each survey update)
# -----------------------------------------------------------------------------
SURVEY_RESULTS: str = "SNS/VULCAN/Bank1-2_2021_Bank3-5_2022_Bank6-engineering.csv"
L1: float = -43.755  # meter
TUBE_LENGTH: float = 1.044628  # meter
TUBE_LENGTH_SHORT: float = 0.773575  # meters
TUBE_RADIUS: float = 0.317 * INCH_TO_METRE * 0.5  # given as diameter
TUBE_PIXELS: int = 512
PIXELS_PER_EIGHTPACK: int = 8 * TUBE_PIXELS  # number of actual pixels
PIXELS_PER_PANEL: int = 5000  # reserve extra pixels after the end of the 8-pack
PIXELS_PER_BANK: int = PIXELS_PER_PANEL * 20  # maximum number of 8-pack in a bank
SEPARATION: float = 0.323 * INCH_TO_METRE  # distance between front and back
SLIP: float = 0.434 * INCH_TO_METRE  # distance between 2 and 4
SLIP_PANEL: float = (
    3 * SLIP + 0.460 * INCH_TO_METRE
)  # bonus spacing between panel centers
REC_TOL_LENS = 0.035  # Rectangle builder tolerance


def read_survey_measurements(filename: str = SURVEY_RESULTS) -> pd.DataFrame:
    """
    Read validated and cleaned survey measurements from a csv file.

    Parameters
    ----------
    :@param filename: path to csv file

    Returns
    -------
    :@return: pandas dataframe
    """
    return pd.read_csv(filename)


def addEightPack(instr, name: str, tube_type: str, upsidedown: bool = False):
    """Add an interleaved 8-pack where pixel 1 is in the lower-left
    corner in the back then increases along the tube upward. The bottom
    of tube two is in the front.

    back     1 3 5 7
    front     2 4 6 8

    Setting ``upsidedown=True`` configures the pixels as

    back      2 4 6 8
    front    1 3 5 7

    This is similar to the incomplete function MantidGeometry.add_double_pack.

    UPDATE: FROM PHASE-II ONWARDS UPSIDEDOWN=TRUE IS NO LONGER USED
    """
    type_element = le.SubElement(instr.root, "type", name=name)
    le.SubElement(type_element, "properties")
    component = le.SubElement(type_element, "component", type=tube_type)
    # z plane is centered in middle of the front plane of detectors
    tube_z = (-1.0 * SEPARATION, SEPARATION)  # 2 rows back, front
    # x plane is centered between the leftmost and rightmost tubes
    # this puts the center of the 8-pack somewhere between tubes 4 and 5 (start counting from one)
    # the values -1.25 and -1.75 were emperically found by putting a single
    # 8-pack directly in the beam and shifting it until the outter tubes
    # were equidistant from the center
    if upsidedown:
        x_offset = (-1.25 * SLIP, -1.75 * SLIP)
    else:
        x_offset = (-1.75 * SLIP, -1.25 * SLIP)
    tube_x = np.arange(4, dtype=float) * SLIP  # 4 tube in a row
    for i, x in enumerate(tube_x):
        for j, (z, slip) in enumerate(zip(tube_z, x_offset)):
            le.SubElement(
                component,
                "location",
                name=f"{name}_{i}_{j}",
                x=f"{x + slip:.5f}",
                z=f"{z:.5f}",
            )


def addBankIds(instr, bankname: str, bank_offset: int, num_panels: int):
    ids = []
    for i in range(num_panels):
        panel_offset = bank_offset + PIXELS_PER_PANEL * i
        ids.extend([panel_offset, panel_offset + PIXELS_PER_EIGHTPACK - 1, None])
    instr.addDetectorIds(bankname, ids)


if __name__ == "__main__":
    logging.basicConfig(
        format="[%(levelname)s]%(asctime)s:%(message)s", level=logging.INFO
    )
    #
    df = read_survey_measurements()
    #
    inst_name = "VULCAN"
    xml_outfile = f"{inst_name}_Definition_tmp.xml"
    authors = ["Peter Peterson", "Malcolm Guthrie", "Chen Zhang"]

    # -- ROOT --
    vulcan_geom = MantidGeom(
        inst_name,
        comment="Created by " + ", ".join(authors),
        valid_from="2022-05-15 00:00:01",
    )

    # -- MISC --
    vulcan_geom.addComment("DEFAULTS")
    vulcan_geom.addSnsDefaults()
    vulcan_geom.addComment("SOURCE")
    vulcan_geom.addModerator(L1)
    vulcan_geom.addComment("SAMPLE")
    vulcan_geom.addSamplePosition()

    # -- MONITOR --
    vulcan_geom.addComment("MONITORS")
    vulcan_geom.addMonitors(distance=[4.83, 1.50], names=["monitor2", "monitor3"])

    # -- ADD BANKS --
    # NOTE:
    # To compensate for the curved (1,2,3,4,6) and flat (5) banks, the actual
    # physical positions is stored at the eight-pack level.
    # The bank here is set to (0,0,0) with zero rotations.
    logging.info(f"Add Banks")
    bank_ids = df["bank"].unique()
    lb_pos = ["X", "Y", "Z"]

    for bank_id in bank_ids:
        elem_bank = vulcan_geom.addComponent(
            type_name=f"bank{bank_id}", idlist=f"bank{bank_id}"
        )
        vulcan_geom.addLocation(elem_bank, x=0, y=0, z=0, rot_y=0)

    # -- ADD 8PACKS --
    # NOTE:
    # Assume that the given csv files contains measurements for all eight-packs in each bank
    logging.info(f"Add 8-packs")
    for bank_id in bank_ids:
        # select bank
        bk = df[df["bank"] == bank_id]
        # make top element
        elem_bank = vulcan_geom.makeTypeElement(f"bank{bank_id}")
        # add individual eight packs based on measurements
        eightpack_ids = bk["eightpack"].unique()
        type_name = "eightpackshort" if bank_id == 5 else "eightpack"
        for eightpack_id in eightpack_ids:
            ep = bk[bk["eightpack"] == eightpack_id].sort_values(
                by=["eightpack vertice idx"]
            )
            vertices = ep[["X", "Y", "Z"]].to_numpy()
            # build the rectangle
            # NOTE:
            # this will set both the position and orientation of the 8-pack
            rectangle = Rectangle(*vertices, tolerance_len=REC_TOL_LENS)
            elem_eightpack = vulcan_geom.addComponent(
                type_name=type_name, root=elem_bank, name=f"pack{eightpack_id:02d}"
            )
            rotations = list(rectangle.euler_rot_yzy)
            rotations.reverse()
            makeLocation(vulcan_geom, elem_eightpack, None, rectangle.center, rotations)

    # -- EIGHTPACK --
    # regular 1m long tube
    logging.info("Add eight-pack (full tube)")
    addEightPack(vulcan_geom, "eightpack", "tube")
    vulcan_geom.addComment(f"most banks are 512 pixels across {TUBE_LENGTH}m")
    vulcan_geom.addPixelatedTube(
        name="tube",
        type_name="onepixel",
        num_pixels=TUBE_PIXELS,
        tube_height=TUBE_LENGTH,
    )
    vulcan_geom.addCylinderPixel(
        name="onepixel",
        center_bottom_base=(0.0, 0.0, 0.0),
        axis=(0.0, 1.0, 0.0),
        pixel_radius=TUBE_RADIUS,
        pixel_height=TUBE_LENGTH / TUBE_PIXELS,
    )
    # special 0.7m short tube
    logging.info("Add eight-pack (half tube)")
    addEightPack(vulcan_geom, "eightpackshort", "tubeshort")
    vulcan_geom.addComment(f"bank 5 is 512 pixels across {TUBE_LENGTH_SHORT}m")
    vulcan_geom.addPixelatedTube(
        name="tubeshort",
        type_name="onepixelshort",
        num_pixels=TUBE_PIXELS,
        tube_height=TUBE_LENGTH_SHORT,
    )
    vulcan_geom.addCylinderPixel(
        name="onepixelshort",
        center_bottom_base=(0.0, 0.0, 0.0),
        axis=(0.0, 1.0, 0.0),
        pixel_radius=TUBE_RADIUS,
        pixel_height=TUBE_LENGTH_SHORT / TUBE_PIXELS,
    )

    # -- DETECTOR ID --
    logging.info("Add detector IDs")
    vulcan_geom.addComment("DETECTOR IDs - panel is an 8-pack")
    for i, bank_id in enumerate(bank_ids):
        num_eightpacks = len(df.loc[df["bank"]==bank_id, "eightpack"].unique())
        addBankIds(
            instr=vulcan_geom,
            bankname=f"bank{bank_id}",
            bank_offset=i*PIXELS_PER_BANK,
            num_panels=num_eightpacks,
        )

    # -- MISC --
    logging.info("Add misc")
    # shape for monitors
    vulcan_geom.addComment(" Shape for Monitors")
    vulcan_geom.addComment(" TODO: Update to real shape ")
    vulcan_geom.addDummyMonitor(0.01, 0.03)
    # monitor ids
    vulcan_geom.addComment("MONITOR IDs")
    vulcan_geom.addMonitorIds([-2, -3])

    # -- SAVE --
    logging.info(f"Save new IDF as {xml_outfile}")
    vulcan_geom.writeGeom(xml_outfile)
