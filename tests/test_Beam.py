
from pytest import mark

from BeamDesign.Beam import Beam, LoadCase

def test_Beam_init():

    a = Beam()

    assert a

@mark.parametrize('length', [None, 1.000, 3.000, 4.532, 1, 3])
def test_beam_get_length(length):

    a = Beam(length=length)

    assert a.length==length

def test_loads_1():

    a = LoadCase()

    position = 1.

    assert a.get_load_x(position=position) is None
    assert a.get_load_y(position=position) is None
    assert a.get_load_z(position=position) is None
    assert a.get_load_mx(position=position) is None
    assert a.get_load_my(position=position) is None
    assert a.get_load_mz(position=position) is None

    expected = [position, None, None, None, None, None, None]

    assert a.get_loads(position=position) == expected

def test_loads_2():

    a = LoadCase(loads=[0.5, 1, 1, 1, 1, 1, 1])

    position = 0.25

    assert a.get_load_x(position=position) == 1
    assert a.get_load_y(position=position) == 1
    assert a.get_load_z(position=position) == 1
    assert a.get_load_mx(position=position) == 1
    assert a.get_load_my(position=position) == 1
    assert a.get_load_mz(position=position) == 1

    expected = [position, 1, 1, 1, 1, 1, 1]

    assert a.get_loads(position=position) == expected