from mantid.simpleapi import LoadEmptyInstrument
import numpy as np


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
    for i in range(ids.shape[0]):   # tube
        for j in range(ids.shape[1]):  # pixel along the tube
            x[i, j], y[i, j], z[i, j] = compInfo.position(int(ids[i, j]))
    return x, y, z


vulcan = LoadEmptyInstrument(Filename='VULCAN_Definition.xml', OutputWorkspace='vulcan')
compInfo = vulcan.componentInfo()
detInfo = vulcan.detectorInfo()


for name in ['bank1', 'bank2', 'bank5']:
    print('=========================', name)
    bank = getTubeIds(compInfo, name)
    x, y, z = getPositions(bank, compInfo)

    # confirm that the positions are constant in certain directions
    np.testing.assert_equal(x[:, 1:] - x[:, :-1], 0., err_msg="everything in same tube has same x")
    np.testing.assert_equal(y[1:, :] - y[:-1, :], 0., err_msg="everything in same row has same y")
    np.testing.assert_equal(z[:, 1:] - z[:, :-1], 0., err_msg="everything in same tube has same z")

    # overall positions of some coordinates
    if name == 'bank1':
        assert np.alltrue(x > 0.)
    elif name == 'bank2':
        assert np.alltrue(x < 0.)
    elif name == 'bank5':
        assert np.alltrue(x < 0.)
        assert np.alltrue(z < 0.)

    # confirm that lower-left is in the correct place
    # positions that are checked to 0.1mm
    assert y[0, 0] == y.min(), 'y-value'  # always gravitationally down
    if name == 'bank1':
        np.testing.assert_almost_equal(x[0, 0], x.max(), err_msg='x-value lower-left', decimal=4)
        np.testing.assert_almost_equal(z[0, 0], z.min(), err_msg='x-value lower-left', decimal=4)
    elif name == 'bank2':
        np.testing.assert_almost_equal(x[0, 0], x.min(), err_msg='x-value lower-left', decimal=4)
        np.testing.assert_almost_equal(z[0, 0], z.max(), err_msg='x-value lower-left', decimal=4)
        # bank2 x-max, z-max
    else:
        # bank5 x in front plane, z-max, but looks complicated
        print(f'NOT checking location of lower-left for {name}')

    # confirm that the positions are increasing in other directions
    np.testing.assert_array_less(y[:, :-1], y[:, 1:], err_msg="everything in same row has increasing y")
    # TODO check X
    # TODO check Z

    # calculate angle constrained in plane - NOT equal to "2theta"
    anglesInPlane = np.abs(np.rad2deg(np.arctan2(x, z)))
    if name in ['bank1']:  # RHS when facing downstream
        np.testing.assert_array_less(anglesInPlane[1:, 0], anglesInPlane[:-1, 0],
                                     err_msg="everything in same row has increasing y")
    elif name in ['bank2', 'bank5']:  # LHS when facing downstream
        np.testing.assert_array_less(anglesInPlane[:-1, 0], anglesInPlane[1:, 0],
                                     err_msg="everything in same row has increasing y")
