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

import numpy as np

from BeamDesign.LoadCase import LoadCase
from BeamDesign.const import LoadComponents
from BeamDesign.Utility.Exceptions import (
    ElementError,
    ElementCaseError,
    ElementLengthError,
    PositionNotInElementError,
)


class Element:
    """
    This is a basic Element object. It is intended that multiple ``Element`` objects
    will form the basis of a single Beam object, to allow easier mapping between the
    output of FEA models, where multiple FEA elements will correspond to a single
    design ``Beam`` objects.
    """

    def __init__(
        self, *, loads: Dict[int, LoadCase], length=None, section=None, material=None
    ):
        """
        Constructor for an ``Element``.

        :param loads: The loads on the ``Element``. Must take the form of a dictionary
            of LoadCase objects mapped to a unique integer ID.
        :param length: The length of the ``Element``, corresponding to its real world
            length.
        :param section: The section of the ``Element``.
        :param material: The material of the ``Element``.
        """

        if length is not None:
            if length < 0.0:
                raise ElementLengthError(
                    f"Expected length to be +ve or None, actual length was {length}"
                )

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

    @property
    def no_load_cases(self) -> int:
        """
        The no. of load cases stored on the element.

        :return: The no. of load cases stored on the element.
        """
        return len(self.loads.keys())

    @property
    def load_cases(self) -> List[int]:
        """
        Returns a list of the load cases on the ``Element``.

        :return: Returns a list of the load cases on the ``Element``. These are the keys
            of the self.loads dictionary.
        """
        return list(self.loads.keys())

    def get_loads(
        self,
        *,
        load_case: int,
        position: Union[List[float], float] = None,
        min_positions: int = None,
        component: Union[int, str, LoadComponents] = None,
    ) -> np.ndarray:
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

        The values of position are normalised between 0.0 and 1.0. To get the true real
        world length along the element they should be multiplied by ``self.length``.
        This is not done at this stage as real-world lengths will generally only be
        required on a ``Beam`` object which may consist of multiple elements.

        :param load_case: The load case to get the loads in.
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

    def get_load_positions(self, *, load_case: int):
        """
        Returns all the stored load positions in a given load case. The load case must
        be specified because it is possible that different load cases would have
        different stored positions.

        :param load_case: The load case to return the positions from, as an int that
            can be used to index into the LoadCase Dict.
        :return: Returns all the positions that loads are stored in the given
            ``LoadCase``.
        """

        return self.loads[load_case].load_positions

    @classmethod
    def empty_element(cls, length: float = None):
        """
        A constructor for an empty ``Element`` with no properties except an empty
        ``LoadCase`` object at load case 0.

        This is a helper method for easily instantiating ``Elements`` for testing etc.

        :param length: An optional length for the empty ``Element``.
        :return: An ``Element`` object.
        """

        loads = LoadCase()
        loads = {0: loads}

        return cls(loads=loads, length=length)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            + f"length={self.length}, "
            + f"section={self.section}, "
            + f"material={self.section}, "
            + f"no. load cases={self.no_load_cases}"
            + f")"
        )


class Beam:
    """
    This is a ``Beam`` object, intended to form the basis of all design checks. It is a
    wrapper object around at least 1x ``Element`` object which corresponds to
    (for example) an FEA beam element. This allows a ``Beam`` object to correspond to
    multiple FEA elements (as will often be the case in a real design scenario).
    """

    def __init__(self, *, elements: Union[Element, List[Element]]):
        """
        Constructor for the ``Beam`` object.

        :param elements: A list of ``Element`` objects that underly the ``Beam`` object.
           They should be ordered consistently, as should the ``LoadCase`` objects in
           them, such that:

           Element_0 length=1.0 == Element_1 length=0.0
           Element_1 length=1.0 == Element_2 length=0.0

           and so-on.
        """

        # first do some consistency checking of the elements.

        if isinstance(elements, Element):
            # make into a list for consistent handling below.
            elements = [elements]

        self._check_elements(elements=elements)

        self._elements = elements

    def _check_elements(self, *, elements: List[Element]):
        """
        A helper method for checking the elements provided to the __init__ method for
        consistency.

        Has no side-effects other than calling appropriate errors as required.

        :param elements: The elements to check for consistency.
        """

        # first check that there is at least an element.

        if elements == None or elements == [] or elements == [None]:
            raise ElementError(
                f"Expected at least one element to create the Beam. "
                f"Was given the following elements: {elements}"
            )

        # next check for any Nones

        if not all(isinstance(e, Element) for e in elements):
            raise ElementError(
                f"At least one provided element in the elements list is not an "
                f"Element object."
            )

        # next check that each element has a matching no of load cases.

        no_cases = [i.no_load_cases for i in elements]
        first_no_cases = no_cases[0]

        if not all(c == first_no_cases for c in no_cases):
            raise ElementCaseError(
                f"No. of load cases should match across all Elements in a Beam. "
                f"No. of cases for each element is: {no_cases}"
            )

        # next check that the elements match.

        cases = [i.load_cases for i in elements]
        first_cases = cases[0]

        if not all(c == first_cases for c in cases):
            raise ElementCaseError(
                f"The index used for load cases should match across "
                f"all Elements in a Beam. At least one Element has non-matching cases."
            )

    @property
    def elements(self) -> List[Element]:
        """
        Return the elements that make up the ``Beam``.

        :return: Returns the elements that make up the ``Beam``.
        """

        return self._elements

    @property
    def length(self) -> float:
        """
        Get the total length of the ``Beam`` object.

        :return: Returns the length of the ``Beam`` object.
        """

        return sum([e.length for e in self._elements])

    @property
    def no_elements(self) -> int:
        """
        Get the no. of elements that make up the ``Beam``.

        :return: The no. of elements.
        """

        return len(self._elements)

    @property
    def no_load_cases(self) -> int:
        """
        Get the no. of load cases available on the ``Element`` objects that make the
        ``Beam``.

        :return: The no. of load cases.
        """

        # Relies on the fact that the elements are checked for consistency when the
        # ``Beam`` to ensure that a correct no. of load cases is returned.

        return self.elements[0].no_load_cases

    @property
    def load_cases(self) -> List[int]:
        """
        Gets a list of the load cases that are available on the ``Element`` objects that
        make up the ``Beam``.

        :return: A list of the load cases.
        """

        # Relies on the fact that the elements are checked for consistency when the
        # ``Beam`` to ensure that a correct no. of load cases is returned.

        return self.elements[0].load_cases

    @property
    def element_starts_ends(self) -> List[List[float]]:
        """
        Returns the ``Element`` starting & ending points as positions from the
        start of the ``Beam``. ``Beam.elements[0]`` always starts at 0.0.
        ``Beam.elements[n]`` (where n is the last element) always ends at
        ``Beam.length``.

        Return is a list of the form:

        [[start_0, end_0]
         [start_1, end_1]
         ...
         [start_n, end_n]
         ]

        :return: The element starting & ending points.
        """

        starts_ends = []

        for i, e in enumerate(self.elements):

            if i == 0:
                starts_ends += [[0.0, e.length]]

            else:

                prev_end = starts_ends[i - 1][1]

                starts_ends += [[prev_end, prev_end + e.length]]

        return starts_ends

    def get_element_start_end(self, *, element: int) -> List[float]:
        """
        Gets the start & end positions of a given ``Element`` in the ``Beam``.

        :param element: The id of the ``Element`` to get the start & end positions of.
        :return: Returns a List of the start & end postions [start, end]
        """

        return self.element_starts_ends[element]

    def in_elements(self, *, position: float) -> List[int]:
        """
        Returns a list of all elements that a given position along the beam fits into.

        If the position is part-way along the length of an ``Element`` only a single
        value will be returned. If exactly at the boundary between 2x or more elements
        multiple element ids will be returned. The list takes the following format:

        [element_id_n, element_id_n+1, ..., element_id_n+o]

        NOTE: if position is > ``Beam.Length`` or < 0.0, returns an empty list []

        :param position: The position to test.
        :return: A list of elements that the position overlaps.
        """

        ret_list = []

        for i in range(0, len(self.elements)):

            start_end = self.get_element_start_end(element=i)

            if position >= start_end[0] and position <= start_end[1]:
                ret_list += [i]

        return ret_list

    def element_local_position(self, *, position: float, element: int) -> float:
        """
        Gets the local position of a *real* position normalised onto an ``Element``.

        :param position: The position to test.
        :param element: The element to get the local position on.
        :return: The local position of the *real* position as a value between 0.0 and
            1.0
        """

        start = self.get_element_start_end(element=element)[0]
        length = self.elements[element].length

        overlap = position - start

        if overlap < 0 or overlap > length:
            raise PositionNotInElementError(
                "Expected position to be within element {element}."
            )

        if length == 0.0:
            return 0.0
        else:
            return (position - start) / length

    def element_real_position(self, *, position: float, element: int) -> float:
        """
        Gets the *real* position of an ``Element`` local position on the ``Beam``
        object.

        :param position: The local position between 0.0 and 1.0 to convert to a *real*
            position on the ``Beam``.
        :param element: The element on which the position applies.
        :return: Returns the real position of the local element position.
        """

        if position < 0 or position > 1.0:
            raise PositionNotInElementError(
                f"Expected position to be between 0.0 and 1.0. "
                + f"Position given was {position}"
            )

        start = self.get_element_start_end(element=element)
        length = self.elements[element].length

        return start + position * length

    def get_loads(
        self,
        *,
        load_case,
        position: Union[List[float], float] = None,
        min_positions: int = None,
        component: Union[int, str, LoadComponents] = None,
    ) -> np.ndarray:
        """
        Gets the load in a ``Beam`` in a given load case and at a given position.
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

        The values of position are 'real' positions along the beam.

        :param load_case: The load case to get the loads in.
        :param position: The position at which to return the load. Position values
            should be entered as floats between 0.0 and ``Beam.length``

            Positions can be a single position or a list of positions. If a list is
            provided, any duplicate values will be ignored, and the order will be
            ignored - return values will be at positions sorted ascending from 0.0 to
            ``Beam.length``.

            If ``position`` is provided, ``min_positions`` must be ``None`` to
            avoid ambiguity.
        :param min_positions: The minimum number of positions to return. Positions will
            be returned such that loads are returned at equally spaced positions between
            0.0 and ``Beam.length`` (inclusive). All stored load positions will also be
            included to ensure that discontinuities are included.

            If ``min_positions`` is provided,
            ``position`` must be ``None`` to avoid ambiguity.
        :param component: The component of load to return.
        :return: A numpy array containing the loads at the specified position.
        """

        # first check for ambiguities in position / min_positions

        assert (
            position is not None or min_positions is not None
        ), "Expected either position or num_positions to be provided. Both were None."

        assert (
            position is None or min_positions is None
        ), "Expected only position or num_positions. Both were provided."

        # next build a list of positions.

        elements = self.elements  # call now to prevent having to call it multiple times

        if position is not None:
            # if position is the provided value then use it.

            if isinstance(position, float):
                # if position is just a float, wrap it in a list for consistency with
                # following code.
                position = [position]

            # convert to a numpy array for use later.
            position = np.array(position)
            position = np.unique(position)

        else:
            # else if min_positions is provided we need to build a list of positions to
            # get the loads at.

            lin_pos = np.linspace(0.0, self.length, min_positions)

            # next concatenate with all the load positions in the elements.
            # to do this we need to get all the load positions on the elements and
            # convert them to real positions. They will be converted back later into
            # element local positions, which may be some double handling, but keeps the
            # logic easier to follow.

            position = []

            for i, e in enumerate(elements):

                element_pos = e.get_load_positions(load_case=load_case)

                # now convert to *real* positions

                real_pos = [
                    self.element_real_position(position=p, element=i)
                    for p in element_pos
                ]

                # now add to the collecting list.
                position += real_pos

            position = np.array(position)
            position = np.concatenate((lin_pos, position))

            position = np.unique(position)  # get rid of duplicate positions

        # we now have a list of all the positions at which we intend to get the loads.
        # next step is to figure out which elements each position maps to.

        element_map = []

        for p in position:

            containing_elements = self.in_elements(position=p)

            for e in containing_elements:
                element_map += [[p, e]]

        # we now have a list which contains all the positions and all the elements that
        # they map to.
        # then start from the lowest position and working to the highest, get all
        # the loads at these positions.

        for i, e in enumerate(element_map):

            pos = e[0]
            e_id = e[1]
            local_pos = self.element_local_position(position=pos, element=e_id)

            val = elements[e[1]].get_loads(
                load_case=load_case, position=local_pos, component=component
            )

            if i == 0:
                ret_val = val
            else:
                ret_val = np.vstack((ret_val, val))

        return ret_val

    @classmethod
    def empty_beam(cls) -> "Beam":
        """
        Helper constructor to build an empty Beam object with an empty element object,
        primarly for testing purposes.

        :return: Returns a ``Beam`` object.
        """

        element = Element.empty_element()

        return cls(elements=element)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            + f"length={self.length}, "
            + f"no. elements={self.no_elements}, "
            + f"no. load cases={self.no_load_cases}"
            + f")"
        )
