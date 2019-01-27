"""
Contains files that test the Material class and sub-classes.
"""

from math import isclose

from pytest import mark

from BeamDesign.material import Steel
from BeamDesign.Utility.Exceptions import InvalidThicknessError

as3678_250 = [
    [0.008, 0.012, 0.05, 0.08, 0.15],
    [280e6, 260e6, 250e6, 240e6, 230e6],
    [410e6, 410e6, 410e6, 410e6, 410e6],
]


def test_steel():
    """
    Can a Steel object be instantiated.
    """

    s = Steel(name="HR250", standard="AS3678", E=200e9, strengths=as3678_250)

    assert s


@mark.parametrize(
    "test_vals",
    [
        (0.000, 280e6, 410e6),
        (0.007, 280e6, 410e6),
        (0.008, 280e6, 410e6),
        (0.009, 260e6, 410e6),
        (0.012, 260e6, 410e6),
        (0.025, 250e6, 410e6),
        (0.050, 250e6, 410e6),
        (0.075, 240e6, 410e6),
        (0.080, 240e6, 410e6),
        (0.130, 230e6, 410e6),
        (0.150, 230e6, 410e6),
    ],
    ids=lambda x: (
        f"t = {x[0]:.3f}m, expected f_y= {x[1] / 1e6:0}MPa, f_u= {x[2] / 1e6}MPa"
    ),
)
def test_steel_strength(test_vals):
    """
    Test the strength_yield method against standard 250 grade steel.
    """

    thickness = test_vals[0]
    f_y = test_vals[1]
    f_u = test_vals[2]

    s = Steel(name="HR250", standard="AS3678", E=200e9, strengths=as3678_250)

    assert isclose(s.strength_yield(thickness=thickness), f_y)
    assert isclose(s.strength_ultimate(), f_u)


@mark.xfail(strict=True, raises=InvalidThicknessError)
@mark.parametrize("thickness", [-0.005, 0.151, None])
def test_steel_strength_yield_error(thickness):
    """
    Test that the steel strength methods return appropriate errors.
    """

    s = Steel(name="HR250", standard="AS3678", E=200e9, strengths=as3678_250)

    f_y = s.strength_yield(thickness=thickness)

    assert True
