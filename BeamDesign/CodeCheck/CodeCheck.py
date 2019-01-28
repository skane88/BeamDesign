"""
This will contain an Abstract Base Class that all CodeCheck classes should inherit from.
"""

from abc import ABC, abstractmethod
from typing import List, Union

from BeamDesign.Beam import Beam
from BeamDesign.Sections.Section import Section
from BeamDesign.Utility.Exceptions import CodeCheckError


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
        return self._beam

    @property
    def section(self):
        return self._section

    @property
    @abstractmethod
    def tension_capacity(self):
        """
        Get the limiting tension capacity of the member being checked.

        :return: the limiting tension capacity of the member being checked.
        """

        raise NotImplementedError()

    @abstractmethod
    def get_all_sections(self) -> List[Section]:
        """
        Returns all the sections from the elements that make up the ``CodeCheck``
        object.

        :return: A list of all the sections. If there is no beam (and only a section) a
            list is still returned for consistency.
        """

        if self.beam is None:
            return [self.section]

        return self.beam.get_all_sections()

    @abstractmethod
    def get_section(
        self, position: Union[List[float], float] = None
    ) -> List[List[Section]]:
        """
        Gets the section properties at a given position or list of positions.

        :param position: The position to return the section from. If the ``CodeCheck``
            object has only a section property (and not a ``Beam`` property) it returns
            ``self.section``. If ``None`` it returns all sections. If a position is
            given it returns the sections at the given positions.
        :return: Returns a list of lists. This is to allow it to handle both the case of
            multiple positions and / or the case where a position falls on the boundary
            between elements. The list is of the form:

            [
                [section_element_1, ..., section_element_n] # Sections at position 1
                ...
                [section_element_1, ..., section_element_n] # Sections at position n
            ]
        """

        if self.beam is None:
            return [[self.section]]

        if position is None:
            return [self.get_all_sections()]

        return self.beam.get_section(position=position)
