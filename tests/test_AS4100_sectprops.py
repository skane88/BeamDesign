"""
File to test the AS4100 section properties methods
"""

from beamdesign.codecheck.AS4100.AS4100_sect_props import AS4100Section, AS4100Circle
from beamdesign.sections.circle import Circle
from beamdesign.materials.material import Material

as3679_1_250 = Material.load_material(name="AS3679.1-2016-300")


def test_AS4100_factory():

    c = Circle(material=as3679_1_250)

    actual = AS4100Section.AS4100_sect_factory(section=c)

    assert isinstance(actual, AS4100Circle)


def test_circle():

    c = Circle(material=as3679_1_250, radius=0.02)

    as4100circle = AS4100Circle(section=c)

    assert as4100circle

def test_circle_min_fy():

    assert False

def test_circle_min_fu():

    assert False