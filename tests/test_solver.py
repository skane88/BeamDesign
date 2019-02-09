"""
This file contains tests for the solver modules intended to solve for utilisations etc.
"""

from math import isclose, isinf, sqrt, exp, sin, cos, pi

from pytest import mark

from hypothesis import given, assume
from hypothesis.strategies import floats

from beamdesign.utility.solvers import bisection, secant


@given(
    n=floats(allow_infinity=False, allow_nan=False),
    x_low=floats(allow_infinity=False, allow_nan=False),
    x_high=floats(allow_infinity=False, allow_nan=False),
)
def test_bisection_1(n, x_low, x_high):
    """
    Test of the bisection method.

    Tests against a line with a slope of 1: x + n, which implies the root is at -n
    """

    def func(x):
        return x + n

    assume(not isinf(func(x_low)))
    assume(not isinf(func(x_high)))
    # eliminates a source of floating point errors - there is a guard in the actual
    # method itself that catches this and raises a ValueError.

    assume(func(x_low) * func(x_high) < 0.0)
    # basic assumption of the bisection method.

    x, i = bisection(func=func)

    assert isclose(x, -n, abs_tol=1e-9)


@mark.parametrize(
    "func, x_low, x_high, root",
    [
        (lambda x: x ** 2 - 3, -2, -1, -sqrt(3)),
        (lambda x: x ** 2 - 3, 1, 2, sqrt(3)),
        (
            lambda x: exp(-x) * (3.2 * sin(x) - 0.5 * cos(x)),
            3,
            4,
            3.2965893955137342207663577582129950752528,
        ),
        (lambda x: sin(x), -4, -3, -pi),
        (lambda x: sin(x), 3, 4, pi),
        (lambda x: cos(x), -2, -1, -pi/2),
        (lambda x: cos(x), 1, 2, pi/2),
    ],
)
def test_bisection_2(func, x_low, x_high, root):
    """
    Test the bisection method against some other function types.
    """

    x, i = bisection(func=func, x_low=x_low, x_high=x_high)

    assert isclose(x, root, abs_tol=1e-8)
    # note tol of 1e-8 - solver not quite finding some roots


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

@mark.parametrize(
    "func, x_low, x_high, root",
    [
        (lambda x: x ** 2 - 3, -2, -1, -sqrt(3)),
        (lambda x: x ** 2 - 3, 1, 2, sqrt(3)),
        (
            lambda x: exp(-x) * (3.2 * sin(x) - 0.5 * cos(x)),
            3,
            4,
            3.2965893955137342207663577582129950752528,
        ),
        (lambda x: sin(x), -4, -3, -pi),
        (lambda x: sin(x), 3, 4, pi),
        (lambda x: cos(x), -2, -1, -pi/2),
        (lambda x: cos(x), 1, 2, pi/2),
    ],
)
def test_secant_3(func, x_low, x_high, root):
    """
    Test the bisection method against some other function types.
    """

    x, i, b = secant(func=func, x_low=x_low, x_high=x_high)

    assert isclose(x, root, abs_tol=1e-8)
    # note tol of 1e-8 - solver not quite finding some roots
