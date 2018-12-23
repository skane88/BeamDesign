"""
Contains tests for the Beam and Elements classes
"""

from pytest import mark

from BeamDesign.Beam import Beam, Element


def test_Element_init():

    a = Beam()

    assert a


@mark.parametrize("length", [None, 1.000, 3.000, 4.532, 1, 3])
def test_Element_get_length(length):

    a = Element(length=length)

    assert a.length == length
