"""
This file is intended to define a class that will describe beam objects. These
are intended to represent real world structural elements and as such their
properties will be limited to those that are explicitly real world properties,
such as:

* Length
* Cross section
* Material Properties
* Internal loads (i.e. bending moments etc.). At this point in time it is NOT
intended to include descriptions of applied loads and / or to calculate
load diagrams directly, although a sub-class may be created eventually to allow
this.

Information that is design code specific will not be stored. This includes
(but is not limited to):

* Capacity reduction factors, safety factors
* Location and types of restraints in compression / bending etc.
* Capacity ratios / strength calculations etc.

The intent here is to make the ``Beam`` class as generic as possible for use
with multiple design codes.
"""

from typing import Dict

import numpy as np

from BeamDesign.LoadCase import LoadCase

class Beam:
    pass


class Element:
    """
    This is a basic Element object. It is intended that multiple ``Element`` objects
    will form the basis of a single Beam object, to allow easier mapping between the
    output of FEA models, where multiple FEA elements will correspond to a single
    design ``Beam`` objects.
    """

    def __init__(
        self,
        *,
        length=None,
        section=None,
        material=None,
        loads: Dict[int, LoadCase] = None
    ):
        """
        Constructor for an ``Element``.

        :param length: The length of the ``Element``, corresponding to its real world
            length.
        :param section: The section of the ``Element``.
        :param material: The material of the ``Element``.
        :param loads: The loads on the ``Element``. Must take the form of a dictionary
            of LoadCase objects mapped to a unique integer ID.
        """

        self.length = length
        self.section = section
        self.material = material
        self._loads = loads

    @property
    def loads(self) -> Dict[int, LoadCase]:
        """
        The loads on the ``Element``. This is a property decorator to enforce read-only
        status.
        :return: The loads on the element as a dictionary of ``LoadCase`` objects.
        """
        return self._loads

