"""
Tests for the AS4100 class
"""

from math import isclose

from pytest import mark

from BeamDesign.CodeCheck.AS4100.AS4100 import *
from BeamDesign.Beam import Beam, Element
from BeamDesign.Sections.Circle import Circle
from BeamDesign.Materials.material import Steel
from BeamDesign.Utility.Exceptions import CodeCheckError

from tests.test_utils import *

as3678_HR250 = Steel.load_steel(steel_name='AS3678-HR250')

def test_AS4100():
    """
    Test whether an AS4100 object can even be instantiated
    """

    kwargs = {"φ": 0.9, "αu": 0.85, "kt":1.0}

    s = Circle(radius=0.02, material=as3678_HR250)
    a = AS4100(section=s, **kwargs)

    assert a

    e = Element.constant_load_element()
    b = Beam(elements=e)

    a = AS4100(beam=b, **kwargs)

    assert a


@mark.xfail(strict=True, raises=CodeCheckError)
def test_AS4100_beam_section_None_error():
    """
    Ensure that an error is thrown when both section & beam are equal to None
    """

    a = AS4100(section=None, beam=None, φ=0.9, αu=0.85, kt=1.0)


def test_AS4100_default_params():

    assert False


def test_AS4100_default_params_fp_error_1():

    assert False


def test_AS4100_defatul_params_fp_error_2():

    assert False

def test_AS4100_get_all_sections():
    """
    Test the get_all_sections method when there is only a section.
    """

    s = Circle(radius=0.02, material=as3678_HR250)

    a = AS4100(section=s, φ=0.9, αu=0.85, kt=1.0)

    actual = a.get_all_sections()

    assert actual == [s]

def test_AS4100_get_all_sections2():
    """
    Test the get_all_sections method with a beam that has a single section.
    """

    b = Beam.empty_beam()

    a = AS4100(beam=b, φ=0.9, αu=0.85, kt=1.0)

    actual = a.get_all_sections()

    assert actual == [None]

def test_AS4100_get_all_sections3():
    """
    Test the get_all_sections method on a beam with actual length.
    """

    s1 = Circle(radius=0.02, material=as3678_HR250)
    s2 = Circle(radius=0.04, material=as3678_HR250)
    s3 = Circle(radius=0.06, material=as3678_HR250)

    e1 = Element.empty_element(length=0.5, section=s1)
    e2 = Element.empty_element(length=0.0, section=s2)
    e3 = Element.empty_element(length=0.5, section=s3)

    b = Beam(elements=[e1, e2, e3])

    a = AS4100(beam=b, φ=0.9, αu=0.85, kt=1.0)

    assert a.get_all_sections() == [s1, s2, s3]

def test_AS4100_get_section():
    """
    Test the get_section method when there is only a section and not a beam.
    """

    s = Circle(radius=0.02, material=as3678_HR250)

    a = AS4100(section=s, φ=0.9, αu=0.85, kt=1.0)

    actual = a.get_section()

    assert actual == [[s]]

def test_AS4100_get_section2():
    """
    Test the get_section method with a beam that has a single section.
    """

    b = Beam.empty_beam()

    a = AS4100(beam=b, φ=0.9, αu=0.85, kt=1.0)

    actual = a.get_section(position=0.0)

    assert actual == [[None]]


def test_AS4100_get_section3():
    """
    Test the get_section method on a beam with actual length.
    """

    s1 = Circle(radius=0.02, material=as3678_HR250)
    s2 = Circle(radius=0.04, material=as3678_HR250)
    s3 = Circle(radius=0.06, material=as3678_HR250)

    e1 = Element.empty_element(length=0.5, section=s1)
    e2 = Element.empty_element(length=0.0, section=s2)
    e3 = Element.empty_element(length=0.5, section=s3)

    b = Beam(elements=[e1, e2, e3])

    a = AS4100(beam=b, φ=0.9, αu=0.85, kt=1.0)

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

    s = Circle(radius=0.02)

    a = AS4100(section=s, φ=0.9, αu=0.85, kt=1.0)

    expected = 1
    actual = a.Nt()

    assert isclose(actual, expected)

    φ = 0.9
    expected = φ * 1
    actual = a.φNt()

    assert isclose(actual, expected)

def test_AS4100_Nt_multiple_sections():
    """
    Test the tension properties instance method where there are multiple sections
    """

    assert False
