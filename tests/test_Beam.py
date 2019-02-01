"""
Contains tests for the Beam and Elements classes
"""

from pytest import mark

import numpy as np

from BeamDesign.Beam import Beam, Element
from BeamDesign.LoadCase import LoadCase
from BeamDesign.Sections.Circle import Circle
from BeamDesign.Materials.material import Steel
from BeamDesign.Utility.Exceptions import (
    ElementError,
    ElementLengthError,
    PositionNotInElementError,
    PositionNotInBeamError,
)

as3678_250 = Steel.load_steel(steel_name="AS3678-250")


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


def test_Beam_get_element_start_end_zero_length():
    """
    Test the get_element_start_end method with a 0 length element.
    """

    length = [0.0]
    expected = [0.0, 0.0]

    elements = [Element.empty_element(length=l) for l in length]

    b = Beam(elements=elements)

    actual = b.get_element_start_end(element=0)

    assert actual == expected


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


@mark.xfail(strict=True, raises=ElementLengthError)
def test_Beam_element_local_error():
    """
    Test the ``Beam.element_local_position`` method.
    """

    length = [1.0, 0.0, 2.3, 0.5]

    elements = [Element.empty_element(length=l) for l in length]

    position = 1.0
    element = 1

    a = Beam(elements=elements)
    actual = a.element_local_position(position=position, element=element)

    assert True


@mark.xfail(strict=True, raises=PositionNotInElementError)
@mark.parametrize(
    "position, element", [(-0.5, 0), (0.5, 1), (1.1, 0), (1.1, 1), (3.9, 3)]
)
def test_Beam_element_local_error2(position, element):
    """
    Test for expected errors in the ``Beam.element_local_position`` method.
    """
    length = [1.0, 0.0, 2.3, 0.5]

    elements = [Element.empty_element(length=l) for l in length]

    a = Beam(elements=elements)
    actual = a.element_local_position(position=position, element=element)

    assert True


@mark.parametrize(
    "position, element, expected",
    [
        (0.0, 0, 0.0),
        (0.5, 0, 0.5),
        (1.0, 0, 1.0),
        (0.0, 1, 1.0),
        (0.5, 1, 1.0),
        (1.0, 1, 1.0),
        (0.0, 2, 1.0),
        (0.5, 2, 2.15),
        (1.0, 2, 3.3),
        (0.0, 3, 3.3),
        (0.5, 3, 3.55),
        (1.0, 3, 3.8),
    ],
)
def test_Beam_element_real_position(position, element, expected):
    """
    Test for the Beam.element_real_position method.
    """

    length = [1.0, 0.0, 2.3, 0.5]

    elements = [Element.empty_element(length=l) for l in length]

    a = Beam(elements=elements)

    actual = a.element_real_position(position=position, element=element)

    assert actual == expected


@mark.xfail(strict=True, raises=PositionNotInElementError)
@mark.parametrize("position", [-1, -0.1, 1.1, 2.0])
@mark.parametrize("element", [0, 1, 2, 3])
def test_Beam_element_real_position_error(position, element):
    """
    Test for the Beam.element_real_position method errors.
    """

    length = [1.0, 0.0, 2.3, 0.5]

    elements = [Element.empty_element(length=l) for l in length]

    a = Beam(elements=elements)

    actual = a.element_real_position(position=position, element=element)

    assert True


def test_Beam_get_loads_position():
    """
    Test for the Beam.get_loads method.
    """

    length = [1.0, 0.0, 2.3, 0.5]
    loads = [0.5, 5.0, 2.5, 25.0]

    ll = list(zip(length, loads))

    elements = [
        Element.constant_load_element(VX=lo, VY=lo, N=lo, MX=lo, MY=lo, T=lo, length=le)
        for le, lo in ll
    ]

    b = Beam(elements=elements)

    actual = b.get_loads(load_case=0, position=0.0)
    expected = np.array([[0.0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]])

    assert np.allclose(actual, expected)

    actual = b.get_loads(load_case=0, position=1.0)
    expected = np.array(
        [
            [1.0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
            [1.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0],
            [1.0, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5],
        ]
    )

    assert np.allclose(actual, expected)

    actual = b.get_loads(load_case=0, position=2.0)
    expected = np.array([[2.0, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5]])

    assert np.allclose(actual, expected)

    actual = b.get_loads(load_case=0, position=3.3)
    expected = np.array(
        [[3.3, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5], [3.3, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0]]
    )

    assert np.allclose(actual, expected)

    actual = b.get_loads(load_case=0, position=3.8)
    expected = np.array([[3.8, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0]])

    assert np.allclose(actual, expected)


def test_Beam_get_loads_positions2():
    """
    Test for the Beam.get_loads method. Test multiple positions.
    """

    length = [1.0, 0.0, 2.3, 0.5]
    loads = [0.5, 5.0, 2.5, 25.0]

    ll = list(zip(length, loads))

    elements = [
        Element.constant_load_element(VX=lo, VY=lo, N=lo, MX=lo, MY=lo, T=lo, length=le)
        for le, lo in ll
    ]

    b = Beam(elements=elements)

    actual = b.get_loads(load_case=0, position=[0.5, 1.5, 2.5, 3.5])

    expected = np.array(
        [
            [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
            [1.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5],
            [2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5],
            [3.5, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0],
        ]
    )

    assert np.allclose(actual, expected)


def test_Beam_get_loads_position3():
    """
    Handle the case of getting the position where a 0 length element is present with
    multiple loads on it.
    """

    zero_length_load = {
        0: LoadCase(
            loads=[
                [0.0, 5.00, 5.00, 5.00, 5.00, 5.00, 5.00],
                [0.5, -10.00, -10.00, -10.00, -10.00, -10.00, -10.00],
                [1.0, 5.00, 5.00, 5.00, 5.00, 5.00, 5.00],
            ]
        )
    }

    length = [1.0, 2.3, 0.5]
    loads = [0.5, 2.5, 25.0]

    ll = list(zip(length, loads))

    elements = [
        Element.constant_load_element(VX=lo, VY=lo, N=lo, MX=lo, MY=lo, T=lo, length=le)
        for le, lo in ll
    ]

    elements.insert(1, Element(loads=zero_length_load, length=0))

    b = Beam(elements=elements)

    actual = b.get_loads(load_case=0, position=1.0)

    expected = np.array(
        [
            [1.00, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50],
            [1.00, 5.00, 5.00, 5.00, 5.00, 5.00, 5.00],
            [1.00, -10.00, -10.00, -10.00, -10.00, -10.00, -10.00],
            [1.00, 5.00, 5.00, 5.00, 5.00, 5.00, 5.00],
            [1.00, 2.50, 2.50, 2.50, 2.50, 2.50, 2.50],
        ]
    )

    assert np.allclose(actual, expected)


def test_Beam_get_loads_min_positions():
    """
    Test for the Beam.get_loads method. Test the min_positions argument.
    """

    length = [1.0, 0.0, 2.3, 0.5]
    loads = [0.5, 5.0, 2.5, 25.0]

    ll = list(zip(length, loads))

    elements = [
        Element.constant_load_element(VX=lo, VY=lo, N=lo, MX=lo, MY=lo, T=lo, length=le)
        for le, lo in ll
    ]

    b = Beam(elements=elements)

    actual = b.get_loads(load_case=0, min_positions=5)

    expected = np.array(
        [
            [0.00, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50],
            [0.95, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50],
            [1.00, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50],
            [1.00, 5.00, 5.00, 5.00, 5.00, 5.00, 5.00],
            [1.00, 2.50, 2.50, 2.50, 2.50, 2.50, 2.50],
            [1.90, 2.50, 2.50, 2.50, 2.50, 2.50, 2.50],
            [2.85, 2.50, 2.50, 2.50, 2.50, 2.50, 2.50],
            [3.30, 2.50, 2.50, 2.50, 2.50, 2.50, 2.50],
            [3.30, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0],
            [3.80, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0],
        ]
    )

    assert np.allclose(actual, expected)


def test_Beam_get_loads_min_positions2():
    """
    Test the beam.get_loads method when there is a 0 length element with multiple
    defined load positions
    """

    zero_length_load = {
        0: LoadCase(
            loads=[
                [0.0, 5.00, 5.00, 5.00, 5.00, 5.00, 5.00],
                [0.5, -10.00, -10.00, -10.00, -10.00, -10.00, -10.00],
                [1.0, 5.00, 5.00, 5.00, 5.00, 5.00, 5.00],
            ]
        )
    }

    length = [1.0, 2.3, 0.5]
    loads = [0.5, 2.5, 25.0]

    ll = list(zip(length, loads))

    elements = [
        Element.constant_load_element(VX=lo, VY=lo, N=lo, MX=lo, MY=lo, T=lo, length=le)
        for le, lo in ll
    ]

    elements.insert(1, Element(loads=zero_length_load, length=0))

    b = Beam(elements=elements)

    actual = b.get_loads(load_case=0, min_positions=5)

    expected = np.array(
        [
            [0.00, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50],
            [0.95, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50],
            [1.00, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50],
            [1.00, 5.00, 5.00, 5.00, 5.00, 5.00, 5.00],
            [1.00, -10.00, -10.00, -10.00, -10.00, -10.00, -10.00],
            [1.00, 5.00, 5.00, 5.00, 5.00, 5.00, 5.00],
            [1.00, 2.50, 2.50, 2.50, 2.50, 2.50, 2.50],
            [1.90, 2.50, 2.50, 2.50, 2.50, 2.50, 2.50],
            [2.85, 2.50, 2.50, 2.50, 2.50, 2.50, 2.50],
            [3.30, 2.50, 2.50, 2.50, 2.50, 2.50, 2.50],
            [3.30, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0],
            [3.80, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0],
        ]
    )

    assert np.allclose(actual, expected)


def test_Beam_get_loads_min_positions3():
    """
    Test the beam.get_loads method when there is a discontinuity in the load mid-element
    """

    load = 2.5
    element_0 = Element.constant_load_element(
        VX=load, VY=load, N=load, MX=load, MY=load, T=load, length=1.0
    )

    load_1 = [
        [0.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0],
        [0.5, -3.0, -3.0, -3.0, -3.0, -3.0, -3.0],
        [0.5, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0],
        [0.5, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0],
        [1.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0],
    ]
    load_dict = {0: LoadCase(loads=load_1)}

    element_1 = Element(loads=load_dict, length=1.0)

    elements = [element_0, element_1]

    beam = Beam(elements=elements)

    actual = beam.get_loads(load_case=0, min_positions=4)

    expected = np.array(
        [
            [0.0, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5],
            [2 / 3, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5],
            [1.0, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5],
            [1.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0],
            [4 / 3, -1 / 3, -1 / 3, -1 / 3, -1 / 3, -1 / 3, -1 / 3],
            [1.5, -3.0, -3.0, -3.0, -3.0, -3.0, -3.0],
            [1.5, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0],
            [1.5, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0],
            [2.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0],
        ]
    )

    assert np.allclose(actual, expected)


def test_Beam_get_loads_multiple_load_cases():
    """
    Test the beam.get_loads method when there is more than 1x load case on an element.
    """

    load_0 = LoadCase.constant_load(VX=2.5, VY=2.5, N=2.5, MX=2.5, MY=2.5, T=2.5)
    load_1 = LoadCase.constant_load(VX=5.0, VY=5.0, N=5.0, MX=5.0, MY=5.0, T=5.0)

    load_dict = {0: load_0, 1: load_1}

    element_0 = Element(loads=load_dict, length=1.0)

    beam = Beam(elements=element_0)

    actual = beam.get_loads(load_case=0, position=0.5)
    expected = np.array([[0.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5]])

    assert np.allclose(actual, expected)

    actual = beam.get_loads(load_case=1, position=0.5)
    expected = np.array([[0.5, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0]])

    assert np.allclose(actual, expected)


@mark.xfail(strict=True)
@mark.parametrize("position, min_positions", [(0.5, 10), (None, None)])
def test_Beam_get_loads_error(position, min_positions):
    """
    Test the Beam.get_loads method to ensure that it throws errors if position and
    min_position are both passed or neither is passed.
    """

    length = [1.0, 0.0, 2.3, 0.5]
    loads = [0.5, 5.0, 2.5, 25.0]

    ll = list(zip(length, loads))

    elements = [
        Element.constant_load_element(VX=lo, VY=lo, N=lo, MX=lo, MY=lo, T=lo, length=le)
        for le, lo in ll
    ]

    b = Beam(elements=elements)

    actual = b.get_loads(load_case=0, position=position, min_positions=min_positions)

    assert True


@mark.xfail(strict=True, raises=PositionNotInBeamError)
@mark.parametrize("position", [-0.1, [-0.1, 1.0], [1.0, 4.0], 4.0])
def test_Beam_get_loads_error(position):
    """
    Test that the beam get_loads method throws an error if a position is outside the
    range of the length of the beam.
    """

    length = [1.0, 0.0, 2.3, 0.5]
    loads = [0.5, 5.0, 2.5, 25.0]

    ll = list(zip(length, loads))

    elements = [
        Element.constant_load_element(VX=lo, VY=lo, N=lo, MX=lo, MY=lo, T=lo, length=le)
        for le, lo in ll
    ]

    b = Beam(elements=elements)

    b.get_loads(load_case=0, position=position)

    assert True


def test_Beam_get_all_sections():
    """
     Test the beam get_all_sections method.
     """

    s1 = Circle(radius=0.02, material=as3678_250)
    s2 = Circle(radius=0.04, material=as3678_250)
    s3 = Circle(radius=0.06, material=as3678_250)

    e1 = Element.empty_element(length=0.5, section=s1)
    e2 = Element.empty_element(length=0.0, section=s2)
    e3 = Element.empty_element(length=0.5, section=s3)

    b = Beam(elements=[e1, e2, e3])

    assert b.get_all_sections() == [s1, s2, s3]


def test_Beam_get_section_none():
    """
    Test the beam get_section method.
    """

    # create an element with no specified section
    e = Element.empty_element(length=1.0, section=None)

    b = Beam(elements=e)

    assert b.get_section(position=0.5) == [[None]]


def test_Beam_get_section():
    """
    Test the beam get_section method with actual sections.
    """

    s1 = Circle(radius=0.02, material=as3678_250)
    s2 = Circle(radius=0.04, material=as3678_250)

    e1 = Element.empty_element(length=0.5, section=s1)
    e2 = Element.empty_element(length=0.5, section=s2)

    b = Beam(elements=[e1, e2])

    assert b.get_section(position=0.25) == [[s1]]
    assert b.get_section(position=0.75) == [[s2]]


def test_Beam_get_section_on_element_boundary():
    """
    Test the beam get_section method with a postion on the boundary of elements
    """
    """
    Test the beam get_section method with actual sections.
    """

    s1 = Circle(radius=0.02, material=as3678_250)
    s2 = Circle(radius=0.04, material=as3678_250)

    e1 = Element.empty_element(length=0.5, section=s1)
    e2 = Element.empty_element(length=0.5, section=s2)

    b = Beam(elements=[e1, e2])

    assert b.get_section(position=0.50) == [[s1, s2]]


def test_Beam_get_section_on_zero_length_element():
    """
    Test the beam get_section at a zero length element.
    """

    # create an element with no specified section
    e = Element.empty_element(length=0.0, section=None)

    b = Beam(elements=e)

    assert b.get_section(position=0.0) == [[None]]


def test_Beam_get_section_on_zero_length_element_2():
    """
    Test the beam get_section at a zero length element.
    """

    s1 = Circle(radius=0.02, material=as3678_250)
    s2 = Circle(radius=0.04, material=as3678_250)
    s3 = Circle(radius=0.06, material=as3678_250)

    e1 = Element.empty_element(length=0.5, section=s1)
    e2 = Element.empty_element(length=0.0, section=s2)
    e3 = Element.empty_element(length=0.5, section=s3)

    b = Beam(elements=[e1, e2, e3])

    assert b.get_section(position=0.4999999) == [[s1]]
    assert b.get_section(position=0.50) == [[s1, s2, s3]]
    assert b.get_section(position=0.5000001) == [[s3]]


def test_Beam_get_section_multiple():
    """
    Test the beam get_section at a zero length element.
    """

    s1 = Circle(radius=0.02, material=as3678_250)
    s2 = Circle(radius=0.04, material=as3678_250)
    s3 = Circle(radius=0.06, material=as3678_250)

    e1 = Element.empty_element(length=0.5, section=s1)
    e2 = Element.empty_element(length=0.0, section=s2)
    e3 = Element.empty_element(length=0.5, section=s3)

    b = Beam(elements=[e1, e2, e3])

    assert b.get_section(position=[0.25, 0.50, 0.75]) == [[s1], [s1, s2, s3], [s3]]


@mark.xfail(strict=True, raises=PositionNotInBeamError)
@mark.parametrize("position", [-0.1, 1.1])
def test_Beam_get_section_outside_range_err(position):
    """
    Test to ensure an error thrown if get_section is called beyond the ends of the beam.
    """

    s1 = Circle(radius=0.02, material=as3678_250)
    s2 = Circle(radius=0.04, material=as3678_250)
    s3 = Circle(radius=0.06, material=as3678_250)

    e1 = Element.empty_element(length=0.5, section=s1)
    e2 = Element.empty_element(length=0.0, section=s2)
    e3 = Element.empty_element(length=0.5, section=s3)

    b = Beam(elements=[e1, e2, e3])

    b.get_section(position=position)

    assert True
