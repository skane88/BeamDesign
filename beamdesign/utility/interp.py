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
) -> np.ndarray:
    """
    Implements an equivalent of np.interp that will interpolate through multiple
    sets of y points.

    NOTE: this is NOT 2D interpolation. It is simply repeated 1d interpolation of the
    same x interpolation through multiple rows of y values.

    :param x: The x points to interpolate.
    :param xp:
    :param fp:
    """

    x = np.array(x)
    xp = np.array(xp)
    fp = np.array(fp)

    # test that xp is sorted:

    if not np.all(xp[1:, ...] - xp[:-1, ...] > 0):
        raise ValueError("Expected input array to be sorted.")

    js = np.searchsorted(xp, x)
    # we now have the co-ordinates of the next largest value to index into xp

    x_high = xp[js, ...]
    x_low = xp[js - 1, ...]

    d = (x - x_low) / (x_high - x_low)

    fp_high = fp[..., js]
    fp_low = fp[..., js - 1]

    interp = fp_low + (fp_high - fp_low) * d

    return interp
