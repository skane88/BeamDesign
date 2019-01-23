"""
Tests for the AS4100 class
"""

from math import isclose

from pytest import mark

from BeamDesign.CodeCheck.AS4100.AS4100 import *
from BeamDesign.Beam import Beam, Element
from BeamDesign.Sections.Circle import Circle

from tests.test_utils import *


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


def test_AS4100_get_section2():
    """
    Test the get_section method on a beam with actual length.
    """

    s1 = Circle(radius=0.02)
    s2 = Circle(radius=0.04)

    e1 = Element.empty_element(length=0.5, section=s1)
    e2 = Element.empty_element(length=0.5, section=s2)

    b = Beam(elements=[e1, e2])

    assert b.get_section(position=0.25) == [s1]
    assert b.get_section(position=0.75) == [s2]
    assert b.get_section() == [s1, s2]


@mark.parametrize("name, data", data_AllSections)
def test_AS4100_s7_Nt(name, data):
    """
    Test the AS4100 s7_Nty, Ntu and Nt methods.
    """

    Ag = data.Ag
    An = data.An

    fy = data.fy
    fu = data.fu
    kt = data.kt

    αu = data.αu

    expected = data.Nty
    actual = AS4100.s7_2_Nty(Ag=Ag, fy=fy)

    assert isclose(actual, expected)

    expected = data.Ntu
    actual = AS4100.s7_2_Ntu(An=An, fu=fu, kt=kt, αu=αu)

    assert isclose(actual, expected)

    expected = data.Nt
    actual = AS4100.s7_1_Nt(Ag=Ag, An=An, fy=fy, fu=fu, kt=kt, αu=αu)

    assert isclose(actual, expected)

def test_AS4100_Nt():
    """
    Test the tension properties instance method.
    """

    s = Circle(radius=0.02)

    a = AS4100(section=s)

    expected = 1
    actual = a.Nt()

    assert isclose(actual, expected)

    φ = 0.9
    expected = φ * 1
    actual = a.φNt()

    assert isclose(actual, expected)

