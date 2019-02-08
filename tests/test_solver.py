"""
This file contains tests for the solver modules intended to solve for utilisations etc.
"""

from hypothesis import given
from hypothesis.strategies import floats

from beamdesign.utility.solvers import sign


@given(floats(min_value=0))
def test_sign_pos(n):
    """
    Test the sign function. Uses hypothesis to cover all the positive numbers.

    :param n: The number to test.
    """

    assert sign(n) == 1


@given(floats(max_value=0, exclude_max=True))
def test_sign_neg(n):
    """
    Test the sign function against negative numbers. Uses hypothesis to cover all the
    negative numbers, excludes 0.

    NOTE: requires hypothesis 4.5.2 or later due to the exclude_max option on floats().

    :param n: The number to test.
    """

    assert sign(n) == -1
