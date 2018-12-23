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

from typing import List, Dict, Union

from BeamDesign.LoadCase import LoadCase
from BeamDesign.const import LoadComponents


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
        loads: Dict[int, LoadCase]=None
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

        if loads is None:
            # if None, force into a LoadCase object.
            loads = LoadCase()

        self._loads = loads

    @property
    def loads(self) -> Dict[int, LoadCase]:
        """
        The loads on the ``Element``. This is a property decorator to enforce read-only
        status.
        :return: The loads on the element as a dictionary of ``LoadCase`` objects.
        """
        return self._loads

    @property
    def no_load_cases(self) -> int:
        """
        The no. of load cases stored on the element.

        :return: The no. of load cases stored on the element.
        """
        return len(self.loads.keys())

    def get_loads(
        self,
        *,
        load_case: int,
        position: Union[List[float], float] = None,
        min_positions: int = None,
        component: Union[int, str, LoadComponents] = None
    ):
        """
        Gets the load in an ``Element`` in a given load case and at a given position.
        If there are multiple loads at a position it returns all of them. Returns in the
        form of a numpy array of the format:

        [[pos, load_1]
         [pos, load_2]
         ...
         [pos, load_n]
        ]

        If ``component`` is not provided, then an array of all loads at the given
        position is returned:

        [[pos, fx_1, fy_1, fz_1, mx_1, my_1, mz_1]
         [pos, fx_2, fy_2, fz_2, mx_2, my_2, mz_2]
         ...
         [pos, fx_n, fy_n, fz_n, mx_n, my_n, mz_n]
        ]

        :param load_case: The load case to get the loads in. If
        :param position: The position at which to return the load. Position values
            should be entered as floats between 0.0 and 1.0 where 0.0 and 1.0 define
            the ends of the element on which the load case is being applied. Positions
            in real world lengths must be normalised by dividing by the element length.
            length.

            Positions can be a single position or a list of positions. If a list is
            provided, any duplicate values will be ignored, and the order will be
            ignored - return values will be at positions sorted ascending from 0.0 to
            1.0.

            If ``position`` is provided, ``min_positions`` must be ``None`` to
            avoid ambiguity.
        :param min_positions: The minimum number of positions to return. Positions will
            be returned such that loads are returned at equally spaced positions between
            0.0 and 1.0 (inclusive). All stored load positions will also be included to
            ensure that discontinuities are included.

            If ``min_positions`` is provided,
            ``position`` must be ``None`` to avoid ambiguity.
        :param component: The component of load to return.
        :return: A numpy array containing the loads at the specified position.
        """

        load = self.loads[load_case]

        return load.get_load(
            position=position, min_positions=min_positions, component=component
        )
