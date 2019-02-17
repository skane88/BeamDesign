"""
Tests the functions in the interp module
"""

import numpy as np

from beamdesign.utility.interp import multi_interp


def test_multi_interp0():

    x = 0.0

    xp = [0.0, 0.0]
    fp = [0.0, 0.0]

    expected = np.interp(x=x, xp=xp, fp=fp)
    actual = multi_interp(x=x, xp=xp, fp=fp)

    assert np.allclose(actual, expected)


def test_multi_interp1():

    x = 1.0

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

    x = 0.5
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

    x = [-0.5, 0.5, 1.5, 2.5]

    xp = [0.0, 1.0, 2.0]
    fp = [[0, 1, 2], [10, 11, 12]]

    left = -50
    right = 50

    actual = multi_interp(x=x, xp=xp, fp=fp, left=left)

    for i in range(actual.shape[0]):

        assert np.allclose(actual[i, :], np.interp(x=x, xp=xp, fp=fp[i], left=left))

    actual = multi_interp(x=x, xp=xp, fp=fp, right=right)

    for i in range(actual.shape[0]):
        assert np.allclose(actual[i, :], np.interp(x=x, xp=xp, fp=fp[i], right=right))

    actual = multi_interp(x=x, xp=xp, fp=fp, left=left, right=right)

    for i in range(actual.shape[0]):
        assert np.allclose(
            actual[i, :], np.interp(x=x, xp=xp, fp=fp[i], left=left, right=right)
        )


def test_multi_interp7():
    """
    Test multi-interp where some xp values are equal.
    """

    x = [-0.5, 0.5, 1.5, 2.5]

    xp = [0.0, 1.0, 1.0, 2.0]
    fp = [[0, 1, 4, 2], [10, 11, 14, 12]]

    left = -50
    right = 50

    actual = multi_interp(x=x, xp=xp, fp=fp, left=left)

    for i in range(actual.shape[0]):
        assert np.allclose(actual[i, :], np.interp(x=x, xp=xp, fp=fp[i], left=left))

    actual = multi_interp(x=x, xp=xp, fp=fp, right=right)

    for i in range(actual.shape[0]):
        assert np.allclose(actual[i, :], np.interp(x=x, xp=xp, fp=fp[i], right=right))

    actual = multi_interp(x=x, xp=xp, fp=fp, left=left, right=right)

    for i in range(actual.shape[0]):
        assert np.allclose(
            actual[i, :], np.interp(x=x, xp=xp, fp=fp[i], left=left, right=right)
        )


def test_multi_interp8():
    """
    Test multi-interp where some x values equal xp values.
    """

    x = [-0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5]

    xp = [0.0, 1.0, 1.0, 2.0]
    fp = [[0, 1, 4, 2], [10, 11, 14, 12]]

    left = -50
    right = 50

    actual = multi_interp(x=x, xp=xp, fp=fp)

    for i in range(actual.shape[0]):
        assert np.allclose(actual[i, :], np.interp(x=x, xp=xp, fp=fp[i]))

    actual = multi_interp(x=x, xp=xp, fp=fp, left=left)

    for i in range(actual.shape[0]):
        assert np.allclose(actual[i, :], np.interp(x=x, xp=xp, fp=fp[i], left=left))

    actual = multi_interp(x=x, xp=xp, fp=fp, right=right)

    for i in range(actual.shape[0]):
        assert np.allclose(actual[i, :], np.interp(x=x, xp=xp, fp=fp[i], right=right))

    actual = multi_interp(x=x, xp=xp, fp=fp, left=left, right=right)

    for i in range(actual.shape[0]):
        assert np.allclose(
            actual[i, :], np.interp(x=x, xp=xp, fp=fp[i], left=left, right=right)
        )
