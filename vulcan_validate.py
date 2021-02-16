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
    print(position_to_str(x[obs_index], y[obs_index], z[obs_index]))
    print(position_to_str(expected['X'][index], expected['Y'][index], expected['Z'][index]))
    # TODO shrink the tolerance from .1m to .1mm
    np.testing.assert_almost_equal(x[obs_index], expected['X'][index], decimal=1)
    np.testing.assert_almost_equal(y[obs_index], expected['Y'][index], decimal=1)
    np.testing.assert_almost_equal(z[obs_index], expected['Z'][index], decimal=1)


vulcan = LoadEmptyInstrument(Filename='VULCAN_Definition.xml', OutputWorkspace='vulcan')
compInfo = vulcan.componentInfo()
detInfo = vulcan.detectorInfo()

banks_exp = readPositions()
for name in ['bank1', 'bank2', 'bank5']:
    print('--------------', name)
    pixels = ['D1T1T', 'D20T4T', 'D1T1B', 'D20T4B']
    if name == 'bank5':
        pixels = ['D1T1T', 'D9T4T', 'D1T1B', 'D9T4B']
    for pixel in pixels:
        index = banks_exp[name]['Point'].index(pixel)
        print(pixel, position_to_str(banks_exp[name]['X'][index],
                                     banks_exp[name]['Y'][index],
                                     banks_exp[name]['Z'][index]))

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
        assert np.alltrue(x < 0.)
        np.testing.assert_almost_equal(x[0, 0], x[-2, 0], err_msg="bank1 same plane", decimal=4)
        assert z[0, 0] > z[-1, 0], "bank1 LL={:.4f}  LR={:.4f}".format(z[0, 0], z[-1, 0])
        assert x[0, 0] < x[1, 0], "bank1 plane LL={:.4f} LR={:.4f}".format(x[0, 0], x[1, 0])  # diff plane
    elif name == 'bank2':
        assert np.alltrue(x > 0.)
        np.testing.assert_almost_equal(x[0, 0], x[-2, 0], err_msg="bank1 same plane", decimal=4)
        assert z[0, 0] < z[-1, 0], "bank2 LL={:.4f}  LR={:.4f}".format(z[0, 0], z[-1, 0])
        assert x[0, 0] > x[1, 0], "bank2 plane LL={:.4f} LR={:.4f}".format(x[0, 0], x[1, 0])  # diff plane
    elif name == 'bank5':  # currently in bank4 location
        assert np.alltrue(x > 0.)
        assert np.alltrue(z < 0.)
        assert x[0, 0] < x[-1, 0], "bank5 LL={:.4f}  LR={:.4f}".format(x[0, 0], x[-1, 0])
        assert z[0, 0] < z[-1, 0], "bank5 LL={:.4f}  LR={:.4f}".format(z[0, 0], z[-1, 0])

    # confirm that lower-left is in the correct place
    # positions that are checked to 0.1mm
    assert y[0, 0] == y.min(), 'y-value'  # always gravitationally down
    if name == 'bank1':
        np.testing.assert_almost_equal(x[0, 0], x.min(), err_msg='x-value lower-left', decimal=4)
        np.testing.assert_almost_equal(z[0, 0], z.max(), err_msg='x-value lower-left', decimal=4)
    elif name == 'bank2':
        np.testing.assert_almost_equal(x[0, 0], x.max(), err_msg='x-value lower-left', decimal=4)
        np.testing.assert_almost_equal(z[0, 0], z.min(), err_msg='x-value lower-left', decimal=4)
        # bank2 x-max, z-max
    else:
        # bank5 x in front plane, z-max, but looks complicated
        print(f'NOT checking location of lower-left for {name}')

    # confirm that the positions are increasing in other directions
    np.testing.assert_array_less(y[:, :-1], y[:, 1:], err_msg="everything in same row has increasing y")
    # TODO check X
    # TODO check Z

    # confirm that the y-center bank center
    np.testing.assert_almost_equal(y.mean(), 0., err_msg='detector panel is centered on horizontal plane',
                                   decimal=4)  # y is centered on plane
    if name in ['bank1', 'bank2']:
        np.testing.assert_almost_equal(z.mean(), 0., err_msg='detector panel is centered on sample',
                                       decimal=4)  # y is centered on plane

    # calculate angle constrained in plane - NOT equal to "2theta"
    anglesInPlane = np.abs(np.rad2deg(np.arctan2(x, z)))
    if name in ['bank1']:  # RHS when facing downstream
        np.testing.assert_array_less(anglesInPlane[:-1, 0], anglesInPlane[1:, 0],
                                     err_msg="everything in same row has increasing y")
    elif name in ['bank2', 'bank5']:  # LHS when facing downstream
        np.testing.assert_array_less(anglesInPlane[1:, 0], anglesInPlane[:-1, 0],
                                     err_msg="everything in same row has increasing y")

    # compare with survey/alignment measurements
    #compare_position(x, y, z, banks_exp[name], obs_index=(0,0), point_label='D1T1B')
    #compare_position(x, y, z, banks_exp[name], obs_index=(0, 511), point_label='D1T1T')
