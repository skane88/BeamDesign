"""
Contains files that test the Material class and sub-classes.
"""

from math import isclose

from pytest import mark

from beamdesign.materials.material import Material
from beamdesign.const import MatType
from beamdesign.utility.exceptions import InvalidThicknessError

as3678_250 = [
    [0.008, 0.012, 0.020, 0.050, 0.080, 0.150, 0.200],
    [280e6, 260e6, 250e6, 250e6, 240e6, 230e6, 220e6],
    [410e6, 410e6, 410e6, 410e6, 410e6, 410e6, 400e6],
]
as3678_300 = [
    [0.008, 0.012, 0.020, 0.050, 0.080, 0.150, 0.200],
    [320e6, 310e6, 300e6, 280e6, 270e6, 260e6, 250e6],
    [430e6, 430e6, 430e6, 430e6, 430e6, 430e6, 420e6],
]


def test_material():
    """
    Can a Material object be instantiated.
    """

    vals = {
        "type": "steel",
        "name": "HR250",
        "standard": "AS3678",
        "properties": {"E": 200e9, "strengths": as3678_250},
    }

    s = Material(**vals)

    assert s


def test_material_eq():
    """
    Does the material equality test work?
    """

    vals = {
        "type": "steel",
        "name": "HR250",
        "standard": "AS3678",
        "properties": {"E": 200e9, "strengths": as3678_250},
    }

    vals2 = {
        "type": "steel",
        "name": "HR250",
        "standard": "AS3678",
        "properties": {"E": 200e9, "strengths": as3678_250},
    }

    vals3 = {
        "type": "steel",
        "name": "HR250",
        "standard": "AS3678",
        "properties": {"E": 200e9, "strengths": as3678_300},
    }

    s1 = Material(**vals)
    s2 = Material(**vals2)
    s3 = Material(**vals3)

    assert s1 == s2
    assert s2 != s3


def test_load_material():
    """
    Test the load_steel class method.
    """

    vals = Material.load_material()

    vals250 = {
        "type": "steel",
        "name": "250",
        "standard": "AS3678-2016",
        "properties": {"E": 200e9, "strengths": as3678_250},
    }

    vals300 = {
        "type": "steel",
        "name": "300",
        "standard": "AS3678-2016",
        "properties": {"E": 200e9, "strengths": as3678_300},
    }

    s250 = Material(**vals250)
    s300 = Material(**vals300)

    s250_act = vals["AS3678-2016-250"]
    s300_act = vals["AS3678-2016-300"]

    assert s250_act == s250
    assert s300_act == s300


def test_load_material2():
    """
    Test the load_material class method.
    """

    vals250 = {
        "type": "steel",
        "name": "250",
        "standard": "AS3678-2016",
        "properties": {"E": 200e9, "strengths": as3678_250},
    }

    s250 = Material(**vals250)

    s250_load = Material.load_material(name="AS3678-2016-250")

    assert s250 == s250_load


def test_load_material_propertyless():
    """
    Test the load_material class method with a propertyless object.
    """

    mat = Material.load_material(name="test_propertyless")

    assert mat.properties == {}
