"""
Contains tests for the Beam and Elements classes
"""

from pytest import mark

from BeamDesign.Beam import Beam, Element


def test_Element_init():
    """
    Can the most basic ``Element`` object be instantiated.
    """

    a = Element.empty_element()

    assert a


@mark.parametrize("length", [None, 1.000, 3.000, 4.532, 1, 3])
def test_Element_get_length(length):
    """
    Test the ``Element.length`` property against a no. of values
    """

    a = Element.empty_element()

    a.length = length

    assert a.length == length

def test_Beam_init():
    """
    Can the most basic ``Beam`` object be instantiated.
    """

    a = Beam.empty_beam()

    assert a
