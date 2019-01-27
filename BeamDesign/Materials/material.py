"""
This file contains a base class describing material properties.
"""

from typing import List, Union, Dict
from abc import ABC, abstractmethod
import json
from pathlib import Path

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

    def __eq__(self, other):
        """
        Override the equality test.
        """

        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__

        return NotImplemented

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
        index = np.searchsorted(self.strengths[0], thickness, side="left")

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

    def __eq__(self, other):
        """
        Override the equality test. Necessary because numpy arrays (used to store the
        steel strengths) do not compare well.
        """

        if isinstance(other, self.__class__):

            for k, v in self.__dict__.items():

                if isinstance(v, np.ndarray):

                    if not np.array_equal(v, other.__dict__[k]):
                        return False

                else:
                    if v != other.__dict__[k]:
                        return False

            return True  # if we have got this far, all items have returned true

        return NotImplemented

    @classmethod
    def load_steel(
        cls, *, file_path: str = None, steel_name: str = None
    ) -> Union["Steel", Dict[str, "Steel"]]:
        """
        This class method creates ``Steel`` objects from a JSON file stored in the
        specified location. If not specified, the default values stored in the package
        are loaded.

        :param file_path: The file_path to load the values from. If not specified, the
            default values will be loaded.
        :param steel_name: The name of the steel to load. If None, a dict of all
            possible ``Steel`` objects are returned.
        :return: A ``Steel`` object or a dictionary of steel objects.
        """

        vals = cls._load_helper(file_path=file_path)

        ret_dict = {}

        for k, v in vals.items():

            ret_dict[k] = cls(**v)

        if steel_name is not None:

            return ret_dict[steel_name]

        return ret_dict

    @classmethod
    def load_list(cls, *, file_path: str = None):
        """
        This class method loads a JSON file stored in the specified location and
        returns a list of available materials that can be loaded into a steel object.

        :param file_path: The file_path to load the values from. If not specified, the
            default values will be loaded.
        :return: A list of all the Steel objects that could be loaded.
        """

        return list(cls._load_helper(file_path=file_path))

    @classmethod
    def _load_helper(cls, *, file_path):
        """
        This class method loads a JSON file stored in the specified location.
        If not specified, the default values stored in the package are loaded.

        This is used as a helper method for the load_xxx clas methods.

        :param file_path: The file_path to load the values from. If not specified, the
            default values will be loaded from the file in the package.
        :return: A dictionary containing the parsed JSON file.
        """

        if file_path is None:
            mod_file = Path(__file__)
            file_path = mod_file.parent / "steel.JSON"

        else:
            file_path = Path(file_path)

        with file_path.open(mode="r") as f:
            vals = json.load(fp=f)

        return vals
