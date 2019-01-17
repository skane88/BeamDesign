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


def test_AS4100_get_section():
    """
    Test the get_section method on a beam with actual length.
    """

    assert False

@mark.parametrize("name, data", data_AllSections)
def test_AS4100_tension_check(name, data):

    Ag = data.Ag
    An = data.An

    fy = data.fy
    fu = data.fu
    kt = data.kt  # end connection factor

    αu = data.αu

    expected = data.Nty  # approximate expected capacity, probably has more decimals...
    actual = AS4100.s7_2_Nty(Ag=Ag, fy=fy)

    assert isclose(actual, expected)

    expected = data.Ntu  # approximate expected capacity, probably has more decimals...
    actual = AS4100.s7_2_Ntu(An=An, fu=fu, kt=kt, αu=αu)

    assert isclose(actual, expected)

    expected = data.Nt  # approximate expected capacity, probably has more decimals...
    actual = AS4100.s7_1_Nt(Ag=Ag, An=An, fy=fy, fu=fu, kt=kt, αu=αu)

    assert isclose(actual, expected)

