"""
Tests for the AS4100 class
"""

from BeamDesign.CodeCheck.AS4100.AS4100 import AS4100


def test_AS4100():
    """
    Test whether an AS4100 object can even be instantiated
    """


    a = AS4100()

    assert a

def test_AS4100_get_section():
    """
    Test the get section method
    """

    assert False