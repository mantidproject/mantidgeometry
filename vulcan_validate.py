from mantid.simpleapi import LoadEmptyInstrument
import numpy as np
from vulcan_geometry import readPositions


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


def position_to_str(x, y, z):
    return f'{x:7.4f}, {y:7.4f}, {z:7.4f}'


def compare_position(x, y, z, expected, obs_index, point_label):
    index = expected['Point'].index(point_label)
    print('======>', point_label)
    # TODO shrink the tolerance from .1m to .1mm
    np.testing.assert_almost_equal(x[obs_index], expected['X'][index], decimal=3)
    np.testing.assert_almost_equal(y[obs_index], expected['Y'][index], decimal=3)
    np.testing.assert_almost_equal(z[obs_index], expected['Z'][index], decimal=3)


vulcan = LoadEmptyInstrument(Filename='VULCAN_Definition.xml', OutputWorkspace='vulcan')
compInfo = vulcan.componentInfo()
detInfo = vulcan.detectorInfo()

banks_exp = readPositions()
for name in ['bank1', 'bank2', 'bank5']:
    print('--------------', name)
    for point in banks_exp[name].points:
        print(point)

for name in ['bank1', 'bank2', 'bank5']:
    print('=========================', name)
    bank = getTubeIds(compInfo, name)
    x, y, z = getPositions(bank, compInfo)

    # confirm which quadrants things are in - x-axis
    if name in ['bank1']:
        assert np.alltrue(x < 0.)
    elif name in ['bank2', 'bank5']:
        assert np.alltrue(x > 0.)
    # confirm which quadrants things are in - z-axis
    if name in ['bank5']:
        assert np.alltrue(z < 0.)

    # confirm that the y-center bank center
    center_exp = banks_exp[name].center
    np.testing.assert_almost_equal(x.mean(), center_exp.x, err_msg='detector panel is x-center',
                                   decimal=4)
    np.testing.assert_almost_equal(y.mean(), center_exp.y, err_msg='detector panel is y-center',
                                   decimal=4)
    np.testing.assert_almost_equal(z.mean(), center_exp.z, err_msg='detector panel is z-center',
                                   decimal=4)

    # confirm that the positions are constant in certain directions
    np.testing.assert_almost_equal(x[:, 1:] - x[:, :-1], 0., decimal=4,
                                   err_msg="everything in same tube has same x")
    np.testing.assert_almost_equal(y[1:, :] - y[:-1, :], 0., decimal=4,
                                   err_msg="everything in same row has same y")
    np.testing.assert_almost_equal(z[:, 1:] - z[:, :-1], 0., decimal=4,
                                   err_msg="everything in same tube has same z")

    # verify the interleaving tubes
    distances = np.sqrt(np.square(x[:, 256]) + np.square(z[:, 256]))  # distance of in-plane
    delta = distances[1:] - distances[:-1]  # every other tube is same distance
    if name in ['bank1', 'bank2', 'bank5']:
        assert np.alltrue(delta[::2] < 0.)
        assert np.alltrue(delta[1::2] > 0.)

    # confirm that the positions are increasing in other directions
    np.testing.assert_array_less(y[:, :-1], y[:, 1:], err_msg="everything in same row has increasing y")
