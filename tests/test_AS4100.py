"""
Tests for the AS4100 class
"""

from math import isclose

from BeamDesign.CodeCheck.AS4100.AS4100 import *
from BeamDesign.Beam import Beam, Element
from BeamDesign.Sections.Circle import Circle


def test_AS4100():
    """
    Test whether an AS4100 object can even be instantiated
    """

    a = AS4100()

    assert a


def test_AS4100_get_section():
    """
    Test the get section method
    """

    b = Beam.empty_beam()

    a = AS4100(beam=b)

    actual = a.get_section()
    expected = [None]

    assert actual == expected

    actual = a.get_section(position=0.0)

    assert actual == expected


def test_AS4100_get_section():
    """
    Test the get_section method on a beam with actual length.
    """

    assert False

def test_AS4100_tension_check():

    s = Circle(radius=0.02).area

    fy = 250e6  # yield strength
    fu = 410e6  # ultimate strength
    kt = 1.0  # end connection factor

    expected = 314159.3  # approximate expected capacity, probably has more decimals...

    actual = AS4100.S7_tension(Ag=s.area, An=s.area, fy=fy, fu=fu, kt=kt)

    assert isclose(actual, expected)