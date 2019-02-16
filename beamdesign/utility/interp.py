"""
Contains some helper interpolation functions.
"""

from typing import Union, List

import numpy as np


def multi_interp(
    *,
    x: Union[float, List[float], np.ndarray],
    xp: Union[List[float], np.ndarray],
    fp: Union[List[float], List[List[float]], np.ndarray],
    left: float = None,
    right: float = None,
) -> Union[float, np.ndarray]:
    """
    Implements an equivalent of np.interp that will interpolate through multiple
    sets of y points.

    NOTE: this is NOT 2D interpolation. It is simply repeated 1d interpolation of the
    same x interpolation through multiple rows of y values. If fp has a single row, this
    is equivalent to calling the numpy function np.interp.

    :param x: The x points to interpolate.
    :param xp: The original x data points. Must be sorted. Raises a value error if not
        sorted.
    :param fp: The original y data points to interpolate.
    :param left: An optional fill value to use if a value in x is less than the values
        in xp (and thus cannot be interpolated). If None, the value of fp at min(xp)
        will be used.
    :param right: An optional fill value to use if a value in x is greater than the
        values in xp (and thus cannot be interpolated). If None, the value of fp at
        max(xp) will be used.
    """

    if x is None:
        raise ValueError(f"Expected a value to interpolate. Actual x provided: x={x}")
    if x == []:
        raise ValueError(f"Expected a value to interpolate. Actual x provided: x={x}")

    x = np.array(x)
    fp = np.array(fp)

    if len(fp.shape) == 1:
        interp = np.interp(x=x, xp=xp, fp=fp, left=left, right=right)
    else:
        interp = np.vstack(
            [np.interp(x=x, xp=xp, fp=f, left=left, right=right) for f in fp]
        )

    return interp
