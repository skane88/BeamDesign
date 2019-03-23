"""
Contains tests for the Element class.
"""

from pytest import mark

from beamdesign.element import Element
from beamdesign.utility.exceptions import ElementLengthError


def test_Element_init():
    """
    Can the most basic ``Element`` object be instantiated.
    """

    a = Element.empty_element()

    assert a


@mark.xfail(strict=True, raises=ElementLengthError)
def test_Element_init_length_error():

    a = Element.empty_element(length=-1.0)

    assert True


@mark.parametrize("length", [None, 1.000, 3.000, 4.532, 1, 3])
def test_Element_get_length(length):
    """
    Test the ``Element.length`` property against a no. of values
    """

    a = Element.empty_element()

    a.length = length

    assert a.length == length
