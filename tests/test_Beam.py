"""
Contains tests for the Beam and Elements classes
"""

from pytest import mark

import numpy as np

from BeamDesign.Beam import Beam, Element
from BeamDesign.Utility.Exceptions import (
    ElementError,
    ElementLengthError,
    PositionNotInElementError,
)


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


@mark.parametrize(
    "lengths, expected",
    [
        ([1.0, 2.0], [[0.0, 1.0], [1.0, 3.0]]),
        ([1.0, 2.3, 0.5], [[0.0, 1.0], [1.0, 3.3], [3.3, 3.8]]),
        ([1.2345, 4.5678, 2.3456], [[0.0, 1.2345], [1.2345, 5.8023], [5.8023, 8.1479]]),
    ],
)
def test_Beam_starts_ends(lengths, expected):
    """
    Test the element_starts_ends property
    """

    elements = [Element.empty_element(length=l) for l in lengths]

    a = Beam(elements=elements)
    starts_ends = a.element_starts_ends

    assert starts_ends == expected


def test_Beam_get_element_start_end():
    """
    Test the get_element_start_end method
    """

    length = [1.0, 2.3, 0.5]
    expected = [[0.0, 1.0], [1.0, 3.3], [3.3, 3.8]]

    elements = [Element.empty_element(length=l) for l in length]

    a = Beam(elements=elements)

    for i in range(0, len(length)):
        actual = a.get_element_start_end(element=i)

        assert actual == expected[i]


@mark.parametrize(
    "position, expected",
    [
        (-0.10, []),
        (3.9, []),
        (0.5, [0]),
        (1.5, [1]),
        (3.5, [2]),
        (0, [0]),
        (3.8, [2]),
        (1.0, [0, 1]),
        (3.3, [1, 2]),
    ],
)
def test_Beam_in_element(position, expected):
    """
    Test the ``Beam.in_element`` method.
    :return:
    """

    length = [1.0, 2.3, 0.5]

    elements = [Element.empty_element(length=l) for l in length]

    a = Beam(elements=elements)
    actual = a.in_elements(position=position)

    assert actual == expected


@mark.parametrize(
    "position, element, expected",
    [
        (0.5, 0, 0.5),
        (1.0, 0, 1.0),
        (1.0, 1, 0.0),
        (1.0, 2, 0.0),
        (1.5, 2, 0.5 / 2.3),
        (3.3, 2, 1.0),
        (3.3, 3, 0.0),
        (3.55, 3, 0.5),
        (3.8, 3, 1.0),
    ],
)
def test_Beam_element_local(position, element, expected):
    """
    Test the ``Beam.element_local_position`` method.
    """
    length = [1.0, 0.0, 2.3, 0.5]

    elements = [Element.empty_element(length=l) for l in length]

    a = Beam(elements=elements)
    actual = a.element_local_position(position=position, element=element)

    assert actual == expected


@mark.xfail(strict=True, raises=PositionNotInElementError)
@mark.parametrize(
    "position, element", [(-0.5, 0), (0.5, 1), (1.1, 0), (1.1, 1), (3.9, 3)]
)
def test_Beam_element_local_error(position, element):
    """
    Test for expected errors in the ``Beam.element_local_position`` method.
    """
    length = [1.0, 0.0, 2.3, 0.5]

    elements = [Element.empty_element(length=l) for l in length]

    a = Beam(elements=elements)
    actual = a.element_local_position(position=position, element=element)

    assert True



def test_Beam_get_loads():

    length = [1.0, 0.0, 2.3, 0.5]
    loads = [0.5, 5.0, 2.5, 25.0]

    ll = list(zip(length, loads))

    elements = [
        Element.constant_load_element(
            FX=lo, FY=lo, FZ=lo, MX=lo, MY=lo, MZ=lo, length=le
        )
        for le, lo in ll
    ]

    b = Beam(elements=elements)

    actual = b.get_loads(load_case=0, position=0.0)
    expected = np.array([[0.0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]])

    assert np.allclose(actual, expected)

    actual = b.get_loads(load_case=0, position=1.0)
    expected = np.array([[1.0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
                         [1.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0],
                         [1.0, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5]])

    assert np.allclose(actual, expected)

    actual = b.get_loads(load_case=0, position=2.0)
    expected = np.array([[2.0, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5]])

    assert np.allclose(actual, expected)

    actual = b.get_loads(load_case=0, position=3.3)
    expected = np.array([[3.3, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5],
                         [3.3, 25., 25., 25., 25., 25., 25.]])

    assert np.allclose(actual, expected)

    actual = b.get_loads(load_case=0, position = 3.8)
    expected = np.array([[3.8, 25., 25., 25., 25., 25., 25.]])

    assert np.allclose(actual, expected)
