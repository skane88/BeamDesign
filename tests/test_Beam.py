"""
Contains tests for the Beam and Elements classes
"""

from pytest import mark

from BeamDesign.Beam import Beam, Element
from BeamDesign.Utility.Exceptions import ElementError, ElementLengthError


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


@mark.parametrize("lengths", [[0.5, 2.5], [1.0, 1.0, 1.0], [0.0, 5.0]])
def test_Beam_length(lengths):
    """
    Test the ``Beam.length`` property.
    """

    # build some elements.

    elements = [Element.empty_element(length=l) for l in lengths]

    expected = sum(lengths)

    b = Beam(elements=elements)

    assert b.length == expected
