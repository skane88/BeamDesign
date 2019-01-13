"""
This will contain an Abstract Base Class that all CodeCheck classes should inherit from.
"""

from abc import ABC, abstractmethod

from BeamDesign.Beam import Beam


class CodeCheck(ABC):
    def __init__(self, beam: Beam, section):

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
    def tension_capacity(self) -> float:
        """
        Get the limiting tension capacity of the member being checked.

        :return: the limiting tension capacity of the member being checked.
        """

        raise NotImplementedError()

    @abstractmethod
    def section(self, position: float=None):

        if self.beam is None:
            return self.section
        else:
            raise self.beam.get_section(position=position)
