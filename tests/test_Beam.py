"""
Contains tests for the Beam and Elements classes
"""

from pytest import mark

from BeamDesign.Beam import Beam, Element
from BeamDesign.Utility.Exceptions import ElementError


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


@mark.xfail(strict=True, raises=ElementError)
@mark.parametrize("elements", [None, [], [None]])
def test_Beam_init_element_errors(elements):
    """
    Test the error raised when there are no elements provided.
    """

    b = Beam(elements=elements)

    assert True


@mark.xfail(strict=True, raises=ElementError)
@mark.parametrize(
    "elements",
    [
        [Element.empty_element(), None],
        [Element.empty_element(), 1],
        [Element.empty_element(), ""],
    ],
)
def test_Beam_init_element_errors2(elements):
    """
    Test the error raised when a list of elements is provided but at least one element
    is not an ``Element``.
    """

    b = Beam(elements=elements)

    assert True


def test_Beam_length():
    """
    Test the ``Beam.length`` property.
    """

    # build some elements.

    e1 = Element.empty_element()
    e2 = Element.empty_element()

    e1.length = 0.5
    e2.length = 2.5

    b = Beam(elements=[e1, e2])

    assert b.length == e1.length + e2.length
