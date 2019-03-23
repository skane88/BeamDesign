"""
Tests for the AS4100 class
"""

from math import isclose, pi

from pytest import mark

import numpy as np

from beamdesign.codecheck.AS4100.AS4100 import *
from beamdesign.beam import Beam
from beamdesign.element import Element
from beamdesign.sections.circle import Circle
from beamdesign.materials.material import Material
from beamdesign.loadcase import LoadCase
from beamdesign.utility.exceptions import (
    CodeCheckError,
    SectionOnlyError,
    InvalidPositionError,
)

from tests.test_utils import *

as3678_250 = Material.load_material(name="AS3678-2016-250")
as3678_300 = Material.load_material(name="AS3678-2016-300")


def test_AS4100():
    """
    Test whether an AS4100 object can even be instantiated
    """

    kwargs = {"φ_steel": 0.9, "αu": 0.85, "kt": 1.0}

    s = Circle(radius=0.02, material=as3678_250)
    a = AS4100(section=s, **kwargs)

    assert a

    e = Element.constant_load_element(section=s)
    b = Beam(elements=e)

    a = AS4100(beam=b, **kwargs)

    assert a


def test_AS4100_default():
    """
    Can the classmethod default_AS4100 create an AS4100 object?
    """

    s = Circle(radius=0.02, material=as3678_250)
    a = AS4100.default_AS4100(section=s)

    assert a

    e = Element.constant_load_element(section=s)
    b = Beam(elements=e)

    a = AS4100.default_AS4100(beam=b)

    assert a


@mark.xfail(strict=True, raises=CodeCheckError)
def test_AS4100_beam_section_None_error():
    """
    Ensure that an error is thrown when both section & beam are equal to None
    """

    a = AS4100(section=None, beam=None, φ_steel=0.9, αu=0.85, kt=1.0)


def test_AS4100_sections():
    """
    Test the sections method when there is only a section.
    """

    s = Circle(radius=0.02, material=as3678_250)

    a = AS4100(section=s, φ_steel=0.9, αu=0.85, kt=1.0)

    actual = a.sections

    assert actual == [s]


def test_AS4100_sections2():
    """
    Test the sections method with a beam that has a single section.
    """

    s = Circle(radius=0.02, material=as3678_250)
    b = Beam.empty_beam(section=s)

    a = AS4100(beam=b, φ_steel=0.9, αu=0.85, kt=1.0)

    actual = a.sections

    assert actual == [s]


def test_AS4100_sections3():
    """
    Test the sections method on a beam with actual length.
    """

    s1 = Circle(radius=0.02, material=as3678_250)
    s2 = Circle(radius=0.04, material=as3678_250)
    s3 = Circle(radius=0.06, material=as3678_250)

    e1 = Element.empty_element(length=0.5, section=s1)
    e2 = Element.empty_element(length=0.0, section=s2)
    e3 = Element.empty_element(length=0.5, section=s3)

    b = Beam(elements=[e1, e2, e3])

    a = AS4100(beam=b, φ_steel=0.9, αu=0.85, kt=1.0)

    assert a.sections == [s1, s2, s3]


@mark.xfail(strict=True, raises=SectionOnlyError)
def test_AS4100_get_section_error():
    """
    Test the get_section method when there is only a section and not a beam. This should
    raise an exception.
    """

    s = Circle(radius=0.02, material=as3678_250)

    a = AS4100(section=s, φ_steel=0.9, αu=0.85, kt=1.0)

    actual = a.get_section()

    assert True


@mark.xfail(strict=True, raises=InvalidPositionError)
def test_AS4100_get_section_error2():
    """
    Test the get_section method when neither a position or min_positions is provided.
    This should raise an exception.
    """

    s = Circle(radius=0.02, material=as3678_250)
    b = Beam.empty_beam(section=s)

    a = AS4100(beam=b, φ_steel=0.9, αu=0.85, kt=1.0)

    actual = a.get_section()

    assert True


def test_AS4100_get_section():
    """
    Test the get_section method with a beam that has a single section.
    """

    s = Circle(radius=0.02, material=as3678_250)
    b = Beam.empty_beam(section=s)

    a = AS4100(beam=b, φ_steel=0.9, αu=0.85, kt=1.0)

    actual = a.get_section(position=0.0)

    assert actual == ([0.0, 0.0], [s, s])


def test_AS4100_get_section2():
    """
    Test the get_section method on a beam with actual length.
    """

    s1 = Circle(radius=0.02, material=as3678_250)
    s2 = Circle(radius=0.04, material=as3678_250)
    s3 = Circle(radius=0.06, material=as3678_250)

    e1 = Element.empty_element(length=0.5, section=s1)
    e2 = Element.empty_element(length=0.0, section=s2)
    e3 = Element.empty_element(length=0.5, section=s3)

    b = Beam(elements=[e1, e2, e3])

    a = AS4100(beam=b, φ_steel=0.9, αu=0.85, kt=1.0)

    assert a.get_section(position=0.25) == ([0.25], [s1])
    assert a.get_section(position=0.50) == ([0.50, 0.50, 0.50, 0.50], [s1, s2, s2, s3])
    assert a.get_section(position=0.75) == ([0.75], [s3])


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

    s = Circle(radius=0.02, material=as3678_250)

    a = AS4100(section=s, φ_steel=0.9, αu=0.85, kt=1.0)

    expected = 250e6 * pi * 0.02 ** 2
    actual = a.Nt()

    assert isclose(actual, expected)

    φ = 0.9
    expected = φ * 250e6 * pi * 0.02 ** 2
    actual = a.φNt()

    assert isclose(actual, expected)


def test_AS4100_Nt_multiple_sections():
    """
    Test the tension properties instance method where there are multiple sections
    """

    s1 = Circle(radius=0.02, material=as3678_250)
    s2 = Circle(radius=0.04, material=as3678_250)
    s3 = Circle(radius=0.06, material=as3678_250)

    e1 = Element.empty_element(length=0.5, section=s1)
    e2 = Element.empty_element(length=0.0, section=s2)
    e3 = Element.empty_element(length=0.5, section=s3)

    b = Beam(elements=[e1, e2, e3])

    a = AS4100(beam=b, φ_steel=0.9, αu=0.85, kt=1.0)

    expected = 250e6 * pi * 0.02 ** 2
    actual = a.Nt()

    assert isclose(actual, expected)

    φ = 0.9
    expected = φ * 250e6 * pi * 0.02 ** 2
    actual = a.φNt()

    assert isclose(actual, expected)


def test_AS4100_Nt_multiple_grades():
    """
    Test the tension properties instance method where there are multiple steel grades.
    :return:
    """

    s1 = Circle(radius=0.02, material=as3678_250)
    s2 = Circle(radius=0.02, material=as3678_300)

    e1 = Element.empty_element(length=0.5, section=s1)
    e2 = Element.empty_element(length=0.5, section=s2)

    b = Beam(elements=[e1, e2])

    a = AS4100(beam=b, φ_steel=0.9, αu=0.85, kt=1.0)

    expected = 250e6 * pi * 0.02 ** 2
    actual = a.Nt()

    assert isclose(actual, expected)

    φ = 0.9
    expected = φ * 250e6 * pi * 0.02 ** 2
    actual = a.φNt()

    assert isclose(actual, expected)

    expected = 280e6 * pi * 0.02 ** 2
    actual = a.Nt(position=0.75)

    assert isclose(actual, expected)


def test_AS4100_Nty():
    """
    Basic test of the Nty method with a section only.
    """

    s = Circle(radius=0.02, material=as3678_250)

    a = AS4100(section=s, φ_steel=0.9, αu=0.85, kt=1.0)

    expected = 250e6 * pi * 0.02 ** 2

    assert isclose(expected, a.Nty())


def test_AS4100_Nty2():
    """
    Basic test of the Nty method with a beam.
    """

    s1 = Circle(radius=0.02, material=as3678_250)

    e1 = Element.empty_element(length=1.0, section=s1)

    b = Beam(elements=[e1])

    a = AS4100(beam=b, φ_steel=0.9, αu=0.85, kt=1.0)

    expected = 250e6 * pi * 0.02 ** 2

    assert isclose(expected, a.Nty())
    assert isclose(expected, a.Nty(position=0.000))
    assert isclose(expected, a.Nty(position=0.250))
    assert isclose(expected, a.Nty(position=0.500))
    assert isclose(expected, a.Nty(position=0.750))
    assert isclose(expected, a.Nty(position=1.000))


def test_AS4100_Nty3():
    """
    Basic test of the Nty method with multiple section types.
    """

    s1 = Circle(radius=0.02, material=as3678_250)
    s2 = Circle(radius=0.04, material=as3678_250)
    s3 = Circle(radius=0.06, material=as3678_250)

    e1 = Element.empty_element(length=0.5, section=s1)
    e2 = Element.empty_element(length=0.0, section=s2)
    e3 = Element.empty_element(length=0.5, section=s3)

    b = Beam(elements=[e1, e2, e3])

    a = AS4100(beam=b, φ_steel=0.9, αu=0.85, kt=1.0)

    expected = 250e6 * pi * 0.02 ** 2

    assert isclose(expected, a.Nty())
    assert isclose(expected, a.Nty(position=0.25))
    assert isclose(expected, a.Nty(position=0.50))

    expected = 230e6 * pi * 0.06 ** 2

    assert isclose(expected, a.Nty(position=0.75))
    assert isclose(expected, a.Nty(position=1.00))


def test_AS4100_Nty_multi_positions():
    """
    Basic test of the Nty method with multiple section types and multiple positions.
    """

    s1 = Circle(radius=0.02, material=as3678_250)
    s2 = Circle(radius=0.04, material=as3678_250)
    s3 = Circle(radius=0.06, material=as3678_250)

    e1 = Element.empty_element(length=0.5, section=s1)
    e2 = Element.empty_element(length=0.0, section=s2)
    e3 = Element.empty_element(length=0.5, section=s3)

    b = Beam(elements=[e1, e2, e3])

    a = AS4100(beam=b, φ_steel=0.9, αu=0.85, kt=1.0)

    expected = 250e6 * pi * 0.02 ** 2

    assert isclose(expected, a.Nty(position=[0.25, 0.75]))
    assert isclose(expected, a.Nty(position=[0.50, 0.75, 1.00]))

    expected = 230e6 * pi * 0.06 ** 2

    assert isclose(expected, a.Nty(position=[0.75, 1.00]))


def test_AS4100_Ntu():
    """
    Basic test of the Ntu method with a section only.
    """

    s = Circle(radius=0.02, material=as3678_250)

    a = AS4100(section=s, φ_steel=0.9, αu=0.85, kt=1.0)

    expected = 0.85 * 1.0 * 410e6 * pi * 0.02 ** 2

    assert isclose(expected, a.Ntu())


def test_AS4100_Ntu2():
    """
    Basic test of the Ntu method with a beam.
    """

    s1 = Circle(radius=0.02, material=as3678_250)

    e1 = Element.empty_element(length=1.0, section=s1)

    b = Beam(elements=[e1])

    a = AS4100(beam=b, φ_steel=0.9, αu=0.85, kt=1.0)

    expected = 0.85 * 1.0 * 410e6 * pi * 0.02 ** 2

    assert isclose(expected, a.Ntu())
    assert isclose(expected, a.Ntu(position=0.000))
    assert isclose(expected, a.Ntu(position=0.250))
    assert isclose(expected, a.Ntu(position=0.500))
    assert isclose(expected, a.Ntu(position=0.750))
    assert isclose(expected, a.Ntu(position=1.000))


def test_AS4100_Ntu3():
    """
    Basic test of the Ntu method with multiple section types.
    """

    s1 = Circle(radius=0.02, material=as3678_250)
    s2 = Circle(radius=0.04, material=as3678_250)
    s3 = Circle(radius=0.06, material=as3678_250)

    e1 = Element.empty_element(length=0.5, section=s1)
    e2 = Element.empty_element(length=0.0, section=s2)
    e3 = Element.empty_element(length=0.5, section=s3)

    b = Beam(elements=[e1, e2, e3])

    a = AS4100(beam=b, φ_steel=0.9, αu=0.85, kt=1.0)

    expected = 0.85 * 1.0 * 410e6 * pi * 0.02 ** 2

    assert isclose(expected, a.Ntu())
    assert isclose(expected, a.Ntu(position=0.25))
    assert isclose(expected, a.Ntu(position=0.50))

    expected = 0.85 * 1.0 * 410e6 * pi * 0.06 ** 2

    assert isclose(expected, a.Ntu(position=0.75))
    assert isclose(expected, a.Ntu(position=1.00))


def test_AS4100_Ntu_multi_positions():
    """
    Basic test of the Ntu method with multiple section types and multiple positions.
    """

    s1 = Circle(radius=0.02, material=as3678_250)
    s2 = Circle(radius=0.04, material=as3678_250)
    s3 = Circle(radius=0.06, material=as3678_250)

    e1 = Element.empty_element(length=0.5, section=s1)
    e2 = Element.empty_element(length=0.0, section=s2)
    e3 = Element.empty_element(length=0.5, section=s3)

    b = Beam(elements=[e1, e2, e3])

    a = AS4100(beam=b, φ_steel=0.9, αu=0.85, kt=1.0)

    expected = 0.85 * 1.0 * 410e6 * pi * 0.02 ** 2

    assert isclose(expected, a.Ntu(position=[0.25, 0.75]))
    assert isclose(expected, a.Ntu(position=[0.50, 0.75, 1.00]))

    expected = 0.85 * 1.0 * 410e6 * pi * 0.06 ** 2

    assert isclose(expected, a.Ntu(position=[0.75, 1.00]))


def test_AS4100_tension_utilisation():
    """
    Very simple test of the tension_utilisation method.
    """

    load = 100000

    s = Circle(radius=0.02, material=as3678_250)
    e = Element.constant_load_element(length=1.0, section=s, N=load)
    b = Beam(elements=e)
    a = AS4100(beam=b, φ_steel=0.9, αu=0.85, kt=1.0)

    φ = 0.9
    capacity = φ * 250e6 * pi * 0.02 ** 2
    expected = capacity / load
    actual = a.tension_utilisation()

    assert isclose(actual, expected)


def test_AS4100_tension_utilisation2():
    """
    More detailed test of the tension_utilisation method. This will be tested to get
    the maximum utilisation first, and then tested to get the utilisation at specified
    positions and in specified load cases.
    """

    s = Circle(radius=0.02, material=as3678_250)
    l = LoadCase(
        loads=[
            [0.00, 100000, 100000, 100000, 100000, 100000, 100000],
            [0.50, 150000, 150000, 150000, 150000, 150000, 150000],
            [0.50, 200000, 200000, 200000, 200000, 200000, 200000],
        ]
    )
    e = Element(loads={1: l}, length=1.0, section=s)
    b = Beam(elements=e)
    a = AS4100(beam=b, φ_steel=0.9, αu=0.85, kt=1.0)

    φ = 0.9
    capacity = φ * 250e6 * pi * 0.02 ** 2
    expected = capacity / 200000
    actual = a.tension_utilisation()

    assert isclose(actual, expected)

    actual = a.tension_utilisation(load_case=1)

    assert isclose(actual, expected)

    loads = b.get_loads(load_case=1, min_positions=20, component="N")

    positions = list(sorted(set(loads[..., 0])))

    for p in positions:

        load = loads[loads[:, 0] == p]
        load = max(load[..., 1])

        expected = capacity / load

        actual = a.tension_utilisation(position=p)

        assert isclose(actual, expected)

    for p in positions:
        load = loads[loads[:, 0] == p]
        load = max(load[..., 1])

        expected = capacity / load

        actual = a.tension_utilisation(position=p, load_case=1)

        assert isclose(actual, expected)


def test_AS4100_tension_utilisation3():
    """
    Test the tension_utilisation method when there are multiple sections along the beam.
    """

    s1 = Circle(radius=0.02, material=as3678_250)
    s2 = Circle(radius=0.03, material=as3678_250)
    l1 = LoadCase(
        loads=[
            [0.00, 100000, 100000, 100000, 100000, 100000, 100000],
            [1.00, 150000, 150000, 150000, 150000, 150000, 150000],
        ]
    )
    l2 = LoadCase(
        loads=[
            [0.00, 200000, 200000, 200000, 200000, 200000, 200000],
            [1.00, 150000, 150000, 150000, 150000, 150000, 150000],
        ]
    )
    e1 = Element(loads={1: l1}, length=0.5, section=s1)
    e2 = Element(loads={1: l2}, length=0.5, section=s2)
    b = Beam(elements=[e1, e2])
    a = AS4100(beam=b, φ_steel=0.9, αu=0.85, kt=1.0)

    φ = 0.9
    c1 = φ * 250e6 * pi * 0.02 ** 2
    c2 = φ * 240e6 * pi * 0.03 ** 2
    expected = c1 / 200000
    actual = a.tension_utilisation()

    assert isclose(actual, expected)

    actual = a.tension_utilisation(load_case=1)

    assert isclose(actual, expected)

    loads = b.get_loads(load_case=1, min_positions=20, component="N")

    positions = list(sorted(set(loads[..., 0])))

    for p in positions:
        load = loads[loads[:, 0] == p]
        load = max(load[..., 1])

        if p <= 0.5:
            expected = c1 / load
        else:
            expected = c2 / load

        actual = a.tension_utilisation(position=p)

        assert isclose(actual, expected)

    for p in positions:
        load = loads[loads[:, 0] == p]
        load = max(load[..., 1])

        if p <= 0.5:
            expected = c1 / load
        else:
            expected = c2 / load

        actual = a.tension_utilisation(position=p, load_case=1)

        assert isclose(actual, expected)


def test_AS4100_tension_utilisation4():
    """
    Test the tension_utilisation method when there are multiple sections AND multiple
    load cases.
    """

    s1 = Circle(radius=0.02, material=as3678_250)
    s2 = Circle(radius=0.03, material=as3678_250)
    l1_1 = LoadCase(
        loads=[
            [0.00, 100000, 100000, 100000, 100000, 100000, 100000],
            [1.00, 150000, 150000, 150000, 150000, 150000, 150000],
        ]
    )
    l1_2 = LoadCase(
        loads=[
            [0.00, 200000, 200000, 200000, 200000, 200000, 200000],
            [1.00, 150000, 150000, 150000, 150000, 150000, 150000],
        ]
    )

    l2_1 = LoadCase(
        loads=[
            [0.00, 200000, 200000, 200000, 200000, 200000, 200000],
            [1.00, 150000, 150000, 150000, 150000, 150000, 150000],
        ]
    )
    l2_2 = LoadCase(
        loads=[
            [0.00, 100000, 100000, 100000, 100000, 100000, 100000],
            [1.00, 150000, 150000, 150000, 150000, 150000, 150000],
        ]
    )

    e1 = Element(loads={1: l1_1, 2: l2_1}, length=0.5, section=s1)
    e2 = Element(loads={1: l1_2, 2: l2_2}, length=0.5, section=s2)
    b = Beam(elements=[e1, e2])
    a = AS4100(beam=b, φ_steel=0.9, αu=0.85, kt=1.0)

    φ = 0.9
    c1 = φ * 250e6 * pi * 0.02 ** 2
    c2 = φ * 240e6 * pi * 0.03 ** 2

    expected = c1 / 200000
    actual = a.tension_utilisation()

    assert isclose(actual, expected)

    actual = a.tension_utilisation(load_case=1)

    assert isclose(actual, expected)

    loads1 = b.get_loads(load_case=1, min_positions=20, component="N")
    loads2 = b.get_loads(load_case=2, min_positions=20, component="N")

    positions = list(sorted(set(loads1[..., 0])))

    for p in positions:
        load1 = loads1[loads1[:, 0] == p]
        load1 = max(load1[..., 1])

        load2 = loads2[loads2[:, 0] == p]
        load2 = max(load2[..., 1])

        load = max(load1, load2)

        if p <= 0.5:
            expected = c1 / load
        else:
            expected = c2 / load

        actual = a.tension_utilisation(position=p)

        assert isclose(actual, expected)

    for p in positions:
        load = loads1[loads1[:, 0] == p]
        load = max(load[..., 1])

        if p <= 0.5:
            expected = c1 / load
        else:
            expected = c2 / load

        actual = a.tension_utilisation(position=p, load_case=1)

        assert isclose(actual, expected)

    for p in positions:
        load = loads2[loads2[:, 0] == p]
        load = max(load[..., 1])

        if p <= 0.5:
            expected = c1 / load
        else:
            expected = c2 / load

        actual = a.tension_utilisation(position=p, load_case=2)

        assert isclose(actual, expected)


def test_AS4100_tension_utilisation5():
    """
    Test the tension utilisation method with compression loads
    """

    assert False
