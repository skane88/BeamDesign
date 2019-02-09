"""
This file contains tests for the solver modules intended to solve for utilisations etc.
"""

from math import isclose, inf, nan, isinf, isnan

from hypothesis import given, assume
from hypothesis.strategies import floats

from beamdesign.utility.solvers import bisection, secant


@given(floats(allow_infinity=False, allow_nan=False))
def test_bisection_1(n):
    """
    Test of the bisection method.

    Tests against a line with a slope of 1: x + n, which implies the root is at -n
    """

    def func(x):
        return x + n

    try:
        x, i = bisection(func=func)

        assert isclose(x, -n, abs_tol=1e-9)
    except ValueError:
        # have placed a number of asserts in code to catch errors related to inf, nan
        assert True


@given(floats(allow_infinity=False, allow_nan=False))
def test_secant_1(n):
    """
    Test of the secant method.

    Tests against a line with a slope of 1: x + n, which implies the root is at -n
    """

    assume(100_000 + n != -100_000 + n)  # eliminates a source of floating point errors

    def func(x):
        return x + n

    x, i, b = secant(func=func, x_low=-100_000, x_high=100_000)

    assert isclose(x, -n, abs_tol=1e-9)


@given(
    n=floats(allow_infinity=False, allow_nan=False),
    x_low=floats(allow_infinity=False, allow_nan=False),
    x_high=floats(allow_infinity=False, allow_nan=False),
)
def test_secant_2(n, x_low, x_high):
    """
    Test of the secant method.

    Tests against a line with a slope of 1: x + n, which implies the root is at -n

    Has multiple hypothesis guesses to allow for x_low and x_high to be included in the
    guesses
    """

    def func(x):
        return x + n

    try:
        x, i, b = secant(func=func, x_low=x_low, x_high=x_high)

        assert isclose(x, -n, abs_tol=1e-9)
    except ValueError:
        # we have put ValueErrors in the solver to catch problems related to infinite
        # arithmetic etc.
        assert True
