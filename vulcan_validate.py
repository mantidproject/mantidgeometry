#!/usr/bin/env python3

"""
Validate default output VULCAN IDF file from vulcan_geometry.py
"""

import logging
import numpy as np
from vulcan_geometry import read_survey_measurements
from mantid.simpleapi import LoadEmptyInstrument


def getTubeIds(compInfo, name):
    # the component index for the bank as a whole
    bankID = int(compInfo.indexOfAny(name))

    # the bank is made of 8-packs
    bank = []
    eightpacks = compInfo.children(bankID)
    for eightpack in eightpacks:
        tubes = compInfo.children(int(eightpack))

        eightpack = [compInfo.children(int(tube)) for tube in tubes]
        bank.extend(eightpack)

    # convert the result into a 2d array of integer indices
    return np.asarray(bank, dtype=int)


def getPositions(ids, compInfo):
    x = np.zeros(ids.shape, dtype=float)
    y = np.zeros(ids.shape, dtype=float)
    z = np.zeros(ids.shape, dtype=float)
    for i in range(ids.shape[0]):  # tube
        for j in range(ids.shape[1]):  # pixel along the tube
            x[i, j], y[i, j], z[i, j] = compInfo.position(int(ids[i, j]))
    return x, y, z


def position_to_str(x, y, z):
    return f"{x:7.4f}, {y:7.4f}, {z:7.4f}"


if __name__ == "__main__":
    logging.basicConfig(
        format="[%(levelname)s]%(asctime)s:%(message)s", level=logging.INFO
    )
    #
    lb_bank = 'bank'
    lb_8pack = 'eightpack'
    lb_pos = ['X','Y','Z']
    df_survey = read_survey_measurements()
    logging.info("Load sanitized survey measurements.")
    logging.info(f"\n{df_survey.groupby(lb_bank)[lb_pos].mean()}")
    for bank_id in df_survey[lb_bank].unique():
        logging.info(f"bank_{bank_id}\n{df_survey[df_survey[lb_bank]==bank_id][lb_pos]}")
    #
    logging.info("Loading VULCAN instrument definition.")
    vulcan = LoadEmptyInstrument(
        Filename="VULCAN_Definition_tmp.xml", OutputWorkspace="vulcan"
    )
    compInfo = vulcan.componentInfo()
    detInfo = vulcan.detectorInfo()

    # -- Verify banks are in desired quadrants
    #
    #              bank5 | bank4
    #                    |      bank 3
    # bank1------------sample---------->(x) bank2
    #              bank6 |
    #                    v     incident beam
    #                   (z)
    logging.info("Verify banks are in desired quadrants.")
    for name in ['bank1', 'bank2', 'bank3', 'bank4', 'bank5', 'bank6']:
        logging.info(f"Checking {name}")
        bank = getTubeIds(compInfo, name)
        x, y, z = getPositions(bank, compInfo)
        if name in ['bank1','bank5', 'bank6']:
            assert np.alltrue(x < 0.)
        elif name in ['bank4', 'bank3','bank2']:
            assert np.alltrue(x > 0.)
        # confirm which quadrants things are in - z-axis
        if name in ['bank3','bank4','bank5']:
            assert np.alltrue(z < 0.)
        if name in ["bank6"]:
            assert np.alltrue(z > 0.)

    # -- Verify center positions of 8-packs in each bank
    # bank_1: 20
    # bank_2: 20
    # bank_3: 18
    # bank_4: 18
    # bank_5: 9
    # bank_6: 11
    logging.info("Verify center positions of 8-packs in each bank.")
    instr = vulcan.getInstrument()
    offset = 2  # bank1 is the 4th item in the list
    for bank_id in df_survey[lb_bank].unique():
        # from survey measurements
        bank_survey = df_survey[df_survey[lb_bank]==bank_id]
        centers_survey = bank_survey.groupby(lb_8pack).mean()[lb_pos]
        logging.info(f"Bank {bank_id}'s 8-pack center positions from survey:\n{centers_survey}")
        # from IDF
        bank_id_mantid = int(bank_id) + offset
        bank_mantid = instr[bank_id_mantid]
        centers_mantid = np.array([bank_mantid[pack_id].getPos() for pack_id in range(bank_mantid.nelements())])
        logging.info(f"Bank {bank_id}'s 8-pack center positions from IDF:\n{centers_mantid}")
        # verify
        np.testing.assert_array_almost_equal(
            centers_survey.to_numpy(),
            centers_mantid,
            err_msg=f"Bank {bank_id}'s 8-pack center positions do not match.",
            decimal=4,
        )

    # -- Verify the interleaving tubes
    logging.info("Verify the interleaving tubes.")
    instr = vulcan.getInstrument()
    offset = 2  # bank1 is the 4th item in the list
    for bank_id in df_survey[lb_bank].unique():
        bank_id_mantid = int(bank_id) + offset
        bank_mantid = instr[bank_id_mantid]
        for pack_id in range(bank_mantid.nelements()):
            pack = bank_mantid[pack_id]
            pack_name = pack.getName()
            tube_L2s = []
            for tube_id in range(pack.nelements()):
                tube = pack[tube_id]
                tube_name = tube.getName()
                tube_L2 = np.linalg.norm(tube.getPos())
                logging.info(f"Bank{bank_id}'s 8-pack {pack_name}'s tube {tube_name}'s L2: {tube_L2}")
                tube_L2s.append(tube_L2)
            tube_L2s = np.array(tube_L2s)
            # verify
            back_minus_front_l2 = tube_L2s[:-1:2] - tube_L2s[1::2]
            if not np.alltrue(back_minus_front_l2 > 0.0):
                logging.error(f"back: {tube_L2s[:-1:2]}")
                logging.error(f"front: {tube_L2s[1::2]}")
                logging.error(f"back-front: {back_minus_front_l2}")
            assert np.alltrue(back_minus_front_l2 > 0.0)

    # -- Verify the positions  are increasing in other directions
    logging.info("Verify the positions are increasing in other directions.")
    for name in ['bank1', 'bank2', 'bank3', 'bank4', 'bank5', 'bank6']:
        logging.info(f"Checking {name}")
        bank = getTubeIds(compInfo, name)
        x, y, z = getPositions(bank, compInfo)
        np.testing.assert_array_less(y[:, :-1], y[:, 1:], err_msg="everything in same row has increasing y")
