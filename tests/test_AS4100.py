"""
Tests for the AS4100 class
"""

from math import isclose, pi

from pytest import mark

from beamdesign.codecheck.AS4100.AS4100 import *
from beamdesign.beam import Beam, Element
from beamdesign.sections.circle import Circle
from beamdesign.materials.material import Material
from beamdesign.utility.exceptions import CodeCheckError

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

    e = Element.constant_load_element()
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

    e = Element.constant_load_element()
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

    actual = a.sections()

    assert actual == [s]


def test_AS4100_sections2():
    """
    Test the sections method with a beam that has a single section.
    """

    b = Beam.empty_beam()

    a = AS4100(beam=b, φ_steel=0.9, αu=0.85, kt=1.0)

    actual = a.sections()

    assert actual == [None]


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

    assert a.sections() == [s1, s2, s3]


def test_AS4100_get_section():
    """
    Test the get_section method when there is only a section and not a beam.
    """

    s = Circle(radius=0.02, material=as3678_250)

    a = AS4100(section=s, φ_steel=0.9, αu=0.85, kt=1.0)

    actual = a.get_section()

    assert actual == [[s]]


def test_AS4100_get_section2():
    """
    Test the get_section method with a beam that has a single section.
    """

    b = Beam.empty_beam()

    a = AS4100(beam=b, φ_steel=0.9, αu=0.85, kt=1.0)

    actual = a.get_section(position=0.0)

    assert actual == [[None]]


def test_AS4100_get_section3():
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

    assert a.get_section(position=0.25) == [[s1]]
    assert a.get_section(position=0.50) == [[s1, s2, s3]]
    assert a.get_section(position=0.75) == [[s3]]
    assert a.get_section() == [[s1, s2, s3]]


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
