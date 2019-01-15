"""
Tests for the AS4100 class
"""

from BeamDesign.CodeCheck.AS4100.AS4100 import AS4100
from BeamDesign.Beam import Beam, Element


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
