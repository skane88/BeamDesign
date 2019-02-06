"""
This will contain an Abstract Base Class that all codecheck classes should inherit from.
"""

from abc import ABC, abstractmethod
from typing import List, Union, Tuple

from beamdesign.beam import Beam
from beamdesign.sections.section import Section
from beamdesign.utility.exceptions import CodeCheckError, SectionOnlyError


class CodeCheck(ABC):
    """
    This is an abstract base class for carrying out code checks of Beam objects.

    The intent is to require only a minimal set of methods that are common across all
    likely design checks.

    For descriptions of methods that need to be implemented refer to method
    documentation below.
    """

    def __init__(
        self, *, beam: Beam = None, section=None, default_params_fp: str = None
    ):

        if beam is None and section is None:
            raise CodeCheckError(
                f"Expected either a beam or a section, both were None."
                + f" Cannot create a {self.__class__.__name__} instance"
            )

        self._beam = beam
        self._section = section

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
    def tension_capacity(self):
        """
        Get the limiting tension capacity of the member being checked.

        :return: the limiting tension capacity of the member being checked. If the code
            includes capacity reduction factors these will be included.
        """

        raise NotImplementedError()

    @property
    @abstractmethod
    def tension_utilisation(self):
        """
        Get the utilisation ratio of the section in tension.

        The utilisation ratio is a % value indicating that the load is x% of the load
        that will cause load to match capacity.

        NOTE: This should NOT be a simple division equation of load / capacity. Whilst
        true when capacity is independent of loads, many code capacity equations depend
        on the applied load.

        :return: The utilisation of the section in tension.
        """

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
