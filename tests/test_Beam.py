from pytest import mark

from BeamDesign.Beam import Beam, Element, LoadCase


def test_Element_init():

    a = Beam()

    assert a


@mark.parametrize("length", [None, 1.000, 3.000, 4.532, 1, 3])
def test_Element_get_length(length):

    a = Element(length=length)

    assert a.length == length


def test_loads_init():

    l = LoadCase()

    assert l

def test_loads_1():

    a = LoadCase()

    position = 1.0

    assert a.get_load(position=position, component='FX') is None
    assert a.get_load(position=position, component='FY') is None
    assert a.get_load(position=position, component='FZ') is None
    assert a.get_load(position=position, component='MX') is None
    assert a.get_load(position=position, component='MY') is None
    assert a.get_load(position=position, component='MZ') is None


def test_loads_2():

    a = LoadCase(loads=[0.5, 1, 1, 1, 1, 1, 1])

    position = 0.25

    assert a.get_load(position=position, component='FX') == 1
    assert a.get_load(position=position, component='FY') == 1
    assert a.get_load(position=position, component='FZ') == 1
    assert a.get_load(position=position, component='MX') == 1
    assert a.get_load(position=position, component='MY') == 1
    assert a.get_load(position=position, component='MZ') == 1

