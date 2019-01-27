"""
This file contains a base class describing material properties.
"""

from typing import List, Union
from abc import ABC, abstractmethod

import numpy as np

from BeamDesign.Utility.Exceptions import InvalidThicknessError


class Material(ABC):
    """
    An base class for materials to inherit from.
    """

    def __init__(self, *, name: str, standard: str):
        """
        Constructor for a Material object.

        :param name: The name of the material.
        :param standard: The standard that the material complies with.
        """

        self.name = name
        self.standard = standard

    @abstractmethod
    def E(self) -> float:
        """
        The elastic modulus of the material.

        :return: Return the Elastic Modulus of the material.
        """
        raise NotImplementedError

    @abstractmethod
    def strength_yield(self, *, thickness=None) -> float:
        """
        Returns the yield strength of the material.

        :param thickness: For materials where the yield strength depends on the
            thickness, thickness should be entered. Otherwise the method should receive
            ``None`` and ignore it.
        :return: The yield strength of the material.
        """
        raise NotImplementedError

    @abstractmethod
    def strength_ultimate(self) -> float:
        """
        Returns the ultimate strength of the material.

        :return: The ultimate strength of the material.
        """
        raise NotImplementedError

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            + f"name={self.name}, "
            + f"standard={self.standard}"
            + f")"
        )


class Steel(Material):
    """
    A class to represent a steel material.
    """

    def __init__(
        self,
        *,
        name: str,
        standard: str,
        E: float,
        strengths: Union[List[List[float]], np.ndarray],
    ):
        """
        Constructor for a Steel Material object.

        :param name: The name of the material.
        :param standard: The standard that the material complies with.
        :param E: The elastic modulus of the steel
        :param strengths: The strength of the steel in the form of a 2D list or numpy
            array:
            [[thickness, ...], [yield_strengths, ...], [ultimate_strength, ...]]
        """

        super().__init__(name=name, standard=standard)

        self._E = E

        self._strengths = np.array(strengths)

        # finally do a check to ensure the thicknesses are sorted:
        if not np.all(np.diff(self.strengths[0]) > 0):
            raise InvalidThicknessError(
                f"The thicknesses are expected to be sorted in increasing order. "
                + f"Provided thicknesses were {strengths[0]}."
            )

    def E(self):

        return self._E

    def strength_yield(self, *, thickness: float = None):
        """
        Calculates the yield strength of the material. This is taken to be the yield
        strength of the next largest stored thickness. I.e. if the following yield
        strength profile is taken to apply:

        thickness = 10mm, yield strength = 260MPa
        thickness = 15mm, yield strength = 250MPa

        An input parameter of thickness = 9mm will return 260MPa, and an inpt of 12mm
        will return a yield strength of 250MPa.

        :param thickness: The thickness of the material. Note that if thickness is
            ``None``, or <0 or > the largest value in the thickness lists an error will
            be returned.
        :return: The yield strength of the material.
        """

        return self.fy(thickness=thickness)

    def strength_ultimate(self):
        """
        Return the ultimate strength of the material.

        :return: The ultimate strength of the material.
        """

        return self.fu()

    def fy(self, *, thickness: float):
        """
        Calculates the yield strength of the material. This is taken to be the yield
            strength of the next largest stored thickness. I.e. if the following yield
            strength profile is taken to apply:

            thickness = 10mm, yield strength = 260MPa
            thickness = 15mm, yield strength = 250MPa

            An input parameter of thickness = 9mm will return 260MPa, and an inpt of 12mm
            will return a yield strength of 250MPa.

        :param thickness: The thickness of the material.
        :return: The yield strength of the material.
        """

        if thickness is None:
            raise InvalidThicknessError(f"Thickness cannot be None")
        elif thickness < 0:
            raise InvalidThicknessError(
                f"Thickness must be >=0. Thickness was {thickness}"
            )
        elif thickness > self.max_thickness:
            raise InvalidThicknessError(
                f"Thickness is expected to be <= largest stored thickness value. "
                + f"Thickness entered was {thickness}, "
                + f"largest stored thickness is {self.max_thickness}"
            )

        # first find the index of the next largest number
        index = np.searchsorted(self.strengths[0], thickness, side='left')

        return self.strengths[1, index]

    def fu(self):
        """
        Return the ultimate strength of the material.

        :return: The ultimate strength of the material.
        """

        return np.amin(self.strengths[2])

    @property
    def strengths(self) -> np.ndarray:
        """
        The list of strengths which are stored in the ``Steel`` object.

        :return: The list of strengths as a numpy array.
        """

        return self._strengths

    @property
    def max_thickness(self):
        """
        Determines the maximum valid thickness that the strength methods can be called
        upon, based on the largest thickness in self.strengths.

        :return: The maximum thickness.
        """

        return np.amax(self.strengths[0])
