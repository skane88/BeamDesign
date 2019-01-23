"""
This will contain an Abstract Base Class that all CodeCheck classes should inherit from.
"""

from abc import ABC, abstractmethod

from BeamDesign.Beam import Beam


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
    def get_section(self, position: float = None):

        if self.beam is None:
            return self.section
        else:
            return self.beam.get_section(position=position)
