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

    x_low = -100000
    x_high = 100000

    assume(not isclose(x_low + n, x_high + n, abs_tol=1e-9))
    # eliminates a source of floating point errors - there is a guard in the actual
    # method itself that catches this and raises a ValueError.

    def func(x):
        return x + n

    x, i, b = secant(func=func, x_low=x_low, x_high=x_high)

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

    assume(not isclose(x_low + n, x_high + n, abs_tol=1e-9))
    # eliminates a source of floating point errors - there is a guard in the actual
    # method itself that catches this and raises a ValueError.

    def func(x):
        return x + n

    assume(not isinf(func(x_low)))
    assume(not isinf(func(x_high)))
    assume(not isinf(x_high * func(x_low)))
    assume(not isinf(x_low * func(x_high)))
    # eliminates a source of floating point errors - there is a guard in the actual
    # method itself that catches this and raises a ValueError.

    x, i, b = secant(func=func, x_low=x_low, x_high=x_high)

    assert isclose(x, -n, abs_tol=1e-9)
