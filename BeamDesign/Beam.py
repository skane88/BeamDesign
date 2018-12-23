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
from BeamDesign.Utility.Exceptions import ElementError, ElementCaseError


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

        The values of position are normalised between 0.0 and 1.0. To get the true real
        world length along the element they should be multiplied by ``self.length``.
        This is not done at this stage as real-world lengths will generally only be
        required on a ``Beam`` object which may consist of multiple elements.

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

    @classmethod
    def empty_element(cls):
        """
        A constructor for an empty ``Element`` with no properties except an empty
        ``LoadCase`` object at load case 0.

        This is a helper method for easily instantiating ``Elements`` for testing etc.

        :return: An ``Element`` object.
        """

        loads = LoadCase()
        loads = {0: loads}

        return cls(loads=loads)

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

        if elements == [] or elements == [None]:
            raise ElementError(
                f"Expected at least one element to create the Beam. "
                f"Was given the following elements {elements}"
            )

        # next check for any Nones

        if any(e == None for e in elements):
            raise ElementError(
                f"At least one provided element in the elements list is " f"None."
            )

        # next check that each element has a matching no of load cases.

        no_cases = [i.no_load_cases for i in elements]
        first_no_cases = no_cases[0]

        if not all(c == first_no_cases for c in no_cases):
            raise ElementCaseError(
                f"No. of load cases should match across all Elements in a Beam. "
                f"No. of cases for each element is {no_cases}"
            )

        # next check that the elements match.

        cases = [i.load_cases for i in elements]
        first_cases = cases[0]

        if not all(c == first_cases for c in cases):
            raise ElementCaseError(
                f"The index used for load cases should match across "
                f"all Elements in a Beam. At least one Element has non-matching cases."
            )

    @classmethod
    def empty_beam(cls):
        """
        Helper constructor to build an empty Beam object with an empty element object,
        primarly for testing purposes.

        :return: Returns a ``Beam`` object.
        """

        element = Element.empty_element()

        return cls(elements=element)
