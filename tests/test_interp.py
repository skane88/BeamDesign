"""
Tests the functions in the interp module
"""

import numpy as np

from pytest import mark

from beamdesign.utility.interp import multi_interp


def test_multi_interp1():

    x = 0.5

    xp = [0.0, 1.0]
    fp = [0.0, 1.0]

    expected = np.interp(x=x, xp=xp, fp=fp)
    actual = multi_interp(x=x, xp=xp, fp=fp)

    assert np.allclose(actual, expected)


def test_multi_interp2():

    x = [0.5]

    xp = [0.0, 1.0]
    fp = [0.0, 1.0]

    expected = np.interp(x=x, xp=xp, fp=fp)
    actual = multi_interp(x=x, xp=xp, fp=fp)

    assert np.allclose(actual, expected)


def test_multi_interp3():

    x = np.array(0.5)

    xp = [0.0, 1.0]
    fp = [0.0, 1.0]

    expected = np.interp(x=x, xp=xp, fp=fp)
    actual = multi_interp(x=x, xp=xp, fp=fp)

    assert np.allclose(actual, expected)


def test_multi_interp4():

    x = 0.5

    xp = np.array([0.0, 1.0])
    fp = np.array([0.0, 1.0])

    expected = np.interp(x=x, xp=xp, fp=fp)
    actual = multi_interp(x=x, xp=xp, fp=fp)

    assert np.allclose(actual, expected)


def test_multi_interp5():

    x = [0.5, 1.5]

    xp = [0.0, 1.0, 2.0]
    fp = [[0, 1, 2], [10, 11, 12]]

    actual = multi_interp(x=x, xp=xp, fp=fp)

    for i in range(actual.shape[0]):

        assert np.allclose(actual[i, :], np.interp(x=x, xp=xp, fp=fp[i]))


def test_multi_interp6():
    """
    Need tests of multi_interp where the interpolated values are outside the bounds of
    xp
    """

    assert False
