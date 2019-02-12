"""
File to test the AS4100 section properties methods
"""

from math import isclose

from pytest import mark

from beamdesign.codecheck.AS4100.AS4100_sect_props import AS4100Section, AS4100Circle
from beamdesign.sections.circle import Circle
from beamdesign.materials.material import Material

as3678_250 = Material.load_material(name="AS3678-2016-250")


def test_AS4100_factory():
    """
    Test the factory method for creating ``AS4100Section`` classes
    """

    c = Circle(material=as3678_250)

    actual = AS4100Section.AS4100_sect_factory(section=c)

    assert isinstance(actual, AS4100Circle)


def test_circle():
    """
    Can we instantiate an AS4100Circle
    """

    c = Circle(material=as3678_250, radius=0.02)

    as4100circle = AS4100Circle(section=c)

    assert as4100circle


@mark.parametrize(
    "radius, expected",
    [
        (0.003, 280e6),
        (0.004, 280e6),
        (0.005, 260e6),
        (0.009, 250e6),
        (0.025, 250e6),
        (0.0255, 240e6),
        (0.040, 240e6),
        (0.060, 230e6),
        (0.075, 230e6),
        (0.100, 220e6),
    ],
)
def test_circle_min_fy(radius, expected):
    """
    Test the circle min_fy method.
    """

    c = Circle(material=as3678_250, radius=radius)

    as4100circle = AS4100Circle(section=c)

    assert isclose(as4100circle.min_fy, expected)

@mark.parametrize(
    "radius, expected",
    [
        (0.003, 410e6),
        (0.004, 410e6),
        (0.005, 410e6),
        (0.009, 410e6),
        (0.025, 410e6),
        (0.0255, 410e6),
        (0.040, 410e6),
        (0.060, 410e6),
        (0.075, 410e6),
        (0.080, 400e6),
        (0.100, 400e6),
    ],
)
def test_circle_min_fu(radius, expected):
    """
    Test the min_fu method.
    """

    c = Circle(material=as3678_250, radius=radius)

    as4100circle = AS4100Circle(section=c)

    assert isclose(as4100circle.min_fu, expected)

def test_circle_Ag():

    assert False

def test_circle_An():

    assert False