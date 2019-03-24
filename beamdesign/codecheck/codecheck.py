"""
This will contain an Abstract Base Class that all codecheck classes should inherit from.
"""

from abc import ABC, abstractmethod
from typing import List, Union, Tuple

import numpy as np

from beamdesign.beam import Beam
from beamdesign.sections.section import Section
from beamdesign.utility.exceptions import CodeCheckError, SectionOnlyError
from beamdesign.const import LoadComponents

DEFAULT_ASSESSMENT_POINTS = 20


class CodeCheck(ABC):
    """
    This is an abstract base class for carrying out code checks of Beam objects.

    The intent is to require only a minimal set of methods that are common across all
    likely design checks.

    For descriptions of methods that need to be implemented refer to method
    documentation below.
    """

    def __init__(
        self, *, beam: Beam = None, section=None, assessment_points: int = None
    ):
        """
        Constructor for a ``CodeCheck`` object.

        :param beam: A beam object to be checked. Can be ``None`` if a section is
            provided instead.
        :param section: A section object to be checked. Can be ``None`` if a beam is
            provided instead.
        :param assessment_points: The minimum number of points to be checked when
            determining utilisations etc. Note that more points may actually be checked
            due to load and element discontinuities etc.
        """

        if beam is None and section is None:
            raise CodeCheckError(
                f"Expected either a beam or a section, both were None."
                + f" Cannot create a {self.__class__.__name__} instance"
            )

        self._beam = beam
        self._section = section

        if assessment_points is None:
            self._assessment_points = DEFAULT_ASSESSMENT_POINTS
        else:
            self._assessment_points = assessment_points

    @property
    def beam(self) -> Beam:
        """
        The ``Beam`` object that the ``CodeCheck`` object is checking.

        :return: The ``Beam`` object that the ``CodeCheck`` object is checking. May be
            ``None`` if the ``CodeCheck`` object is based on a ``Section``.
        """

        return self._beam

    @property
    def section(self):
        """

        :return: The ``Section`` object that the ``CodeCheck`` object contains. May be
            ``None`` if the ``CodeCheck`` object is based on a ``Beam``.
        """

        return self._section

    @property
    @abstractmethod
    def sections(self) -> List[Section]:
        """
        Returns all the sections from the elements that make up the ``codecheck``
        object.

        :return: A list of all the sections. If there is no beam (and only a section) a
            list is still returned for consistency.
        """

        if self.beam is None:
            return [self.section]

        return self.beam.sections

    @property
    def assessment_points(self) -> int:
        """
        The minimum number of points at which utilisation etc. will be assessed.

        The actual no. of points may vary as the ``CodeCheck`` obects are expected to
        be able to handle discontinuities at loads and starts / ends of elements etc.
        """
        return self._assessment_points

    @assessment_points.setter
    def assessment_points(self, assessment_points: int):
        """
        The minimum number of points at which utilisation etc. will be assessed.

        The actual no. of points may vary as the ``CodeCheck`` obects are expected to
        be able to handle discontinuities at loads and starts / ends of elements etc.
        :param assessment_points: The minimum number of assessment points.
        """

        self._assessment_points = assessment_points

    @abstractmethod
    def tension_capacity(self, *, position: Union[List[float], float] = None):
        """
        Get the limiting tension capacity of the member being checked.

        :param position: The position to calculate the capacity at. Can be a float, can
            be a list of floats or can be None.

            Note that if None is provided, a single tension capacity is returned which
            is the minimum tension capacity of the entire object.
        :return: the limiting tension capacity of the member being checked. If the code
            includes capacity reduction factors these will be included.
        """

        raise NotImplementedError()

    @abstractmethod
    def tension_utilisation(
        self, *, load_case: int = None, position: Union[List[float], float] = None
    ) -> float:
        """
        Get the utilisation ratio of the section in tension.

        The utilisation ratio is a % value indicating that the load is x% of the load
        that will cause load to match capacity.

        NOTE: This should NOT be a simple division equation of load / capacity. Whilst
        true when capacity is independent of loads, many code capacity equations depend
        on the applied load.

        :param position: The position to calculate the utilisation at. Can be a float,
            can be a list of floats or can be None.

            Note that if None is provided, a single tension utilisation is returned
            which is the highest tension utilisation of the entire object.
        :param load_case: The load case to get the utilisation ratio in - if ``None``,
            return the highest utilisation ratio of any load case.
        :return: The utilisation of the section in tension.
        """

        raise NotImplementedError()

    @abstractmethod
    def get_section(
        self,
        *,
        position: Union[List[float], float] = None,
        min_positions: int = None,
        load_case: int = None,
    ) -> Tuple[List[float], List[Section]]:
        """
        Gets the section properties at a given position or list of positions.

        The positions can either be requested directly, or as a minimum number of
        positions along the beam. If specified as minimum positions, a load case can be
        specified as well (to include load discontinuities etc.

        If the ``CodeCheck`` object is a section based object, it will raise a
        SectionOnlyError.

        :param min_positions: The minimum no. of positions to return.
        :param position: The position to return the section from. If the ``codecheck``
            object has only a section property (and not a ``Beam`` property) it returns
            ``self.section``. If ``None`` it returns all sections. If a position is
            given it returns the sections at the given positions.
        :param load_case: he load case to consider if using min_positions. Can be
            ``None``, in which case only the start & ends of elements are returned.
        :return: Returns a tuple of positions and sections:

            (
                [pos_1, ..., pos_n]
                [section_1, ..., section_n]
            )
        """

        if self.beam is None:
            raise SectionOnlyError(
                f"get_section does not apply to Section based CodeCheck objects."
            )

        return self.beam.get_section(
            position=position, min_positions=min_positions, load_case=load_case
        )

    @abstractmethod
    def get_loads(
        self,
        *,
        load_case: int,
        position: Union[List[float], float] = None,
        min_positions: int = None,
        component: Union[int, str, LoadComponents] = None,
    ) -> np.ndarray:
        """
        Gets the load on a ``CodeCheck`` object in a given load case and at a given
        position.

        If there are multiple loads at a position it returns all of them. Returns in the
        form of a numpy array of the format:

        [[pos, load_1]
         [pos, load_2]
         ...
         [pos, load_n]
        ]

        If ``component`` is not provided, then an array of all loads at the given
        position is returned:

        [[pos, vx_1, vy_1, N_1, mx_1, my_1, T_1]
         [pos, vx_2, vy_2, N_2, mx_2, my_2, T_2]
         ...
         [pos, vx_n, vy_n, N_n, mx_n, my_n, T_n]
        ]

        The values of position are 'real' positions along the underlying beam.

        :param load_case: The load case to get the loads in.
        :param position: The position at which to return the load. Position values
            should be entered as floats between 0.0 and ``Beam.length``

            Positions can be a single position or a list of positions. If a list is
            provided, any duplicate values will be ignored, and the order will be
            ignored - return values will be at positions sorted ascending from 0.0 to
            ``Beam.length``. If the specified position is at an element or load
            discontinuity multiple values may be returned.

            If ``position`` is provided, ``min_positions`` must be ``None`` to
            avoid ambiguity.
        :param min_positions: The minimum number of positions to return. Positions will
            be returned such that loads are returned at equally spaced positions between
            0.0 and ``Beam.length`` (inclusive). All stored load positions and element
            start / end positions will also be included to ensure that discontinuities
            are included.

            If ``min_positions`` is provided,
            ``position`` must be ``None`` to avoid ambiguity.
        :param component: The component of load to return.
        :return: A numpy array containing the loads at the specified position.
        """

        if self.beam is None:
            raise SectionOnlyError(
                "The CodeCheck object is a section only object and has no stored loads."
            )

        return self.beam.get_loads(
            load_case=load_case,
            position=position,
            min_positions=min_positions,
            component=component,
        )

    @abstractmethod
    def get_tension(
        self, *, load_case, position=None, min_positions=None
    ) -> np.ndarray:
        """
        Gets the tension load on a ``CodeCheck`` object in a given load case and at a
        given position.

        If there are multiple loads at a position it returns all of them. Returns in the
        form of a numpy array of the format:

        [[pos, tension_1]
         [pos, tension_2]
         ...
         [pos, tension_n]
        ]

        The values of position are 'real' positions along the underlying beam.

        Always returns positive values or 0.0. If the axial load at a given position is
        -ve (i.e. in compression) it returns 0.0.

        :param load_case: The load case to get the loads in.
        :param position: The position at which to return the load. Position values
            should be entered as floats between 0.0 and ``Beam.length``

            Positions can be a single position or a list of positions. If a list is
            provided, any duplicate values will be ignored, and the order will be
            ignored - return values will be at positions sorted ascending from 0.0 to
            ``Beam.length``. If the specified position is at an element or load
            discontinuity multiple values may be returned.

            If ``position`` is provided, ``min_positions`` must be ``None`` to
            avoid ambiguity.
        :param min_positions: The minimum number of positions to return. Positions will
            be returned such that loads are returned at equally spaced positions between
            0.0 and ``Beam.length`` (inclusive). All stored load positions and element
            start / end positions will also be included to ensure that discontinuities
            are included.

            If ``min_positions`` is provided,
            ``position`` must be ``None`` to avoid ambiguity.
        :return: A numpy array containing the loads at the specified position.
        """

        tension = self.beam.get_loads(
            load_case=load_case,
            position=position,
            min_positions=min_positions,
            component="N",
        )

        # replace all the tension elements that are in compression with 0.

        tension[:, 1][tension[:, 1] < 0] = 0

        return tension
