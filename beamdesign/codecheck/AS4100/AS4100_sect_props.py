"""
This module contains functions for calculating effective section properties
as required by AS4100 S5, 6 & 7.
"""

from abc import ABC, abstractmethod

from typing import List, Union

from beamdesign.sections.section import Section
from beamdesign.sections.circle import Circle
from beamdesign.sections.hollowcircle import HollowCircle
from beamdesign.materials.material import Material
from beamdesign.utility.exceptions import (
    InvalidMaterialError,
    InvalidThicknessError,
    MaterialError,
)
from beamdesign.const import MatType


class AS4100Section(ABC):
    """
    A class for calculating AS4100 section properties.
    """

    section: Section  # type hint on self.section property

    def __init__(self, *, section: Section):
        """
        Constructor for an AS4100_section() object.
        :param section: A valid section object to create the ASA4100 section from.
        """

        self.section = section

        # do some checks that the section is valid.

        if self.section.material.type != MatType.steel:
            raise InvalidMaterialError(
                f"AS4100 is only valid for steel. "
                + f"Provided material was {self.section.material}"
            )

    @property
    @abstractmethod
    def min_fy(self):

        raise NotImplementedError()

    @property
    @abstractmethod
    def min_fu(self):

        raise NotImplementedError()

    @property
    def material(self) -> Material:
        """
        The material from the underlying ``Section`` object.
        """

        return self.section.material

    @property
    def E(self) -> float:
        """
        The Elastic Modulus of the steel.
        """

        return self.material.properties["E"]

    @property
    def _strengths(self) -> List[List[float]]:
        """
        A helper property to return the strengths of the underlying material object.
        """

        return self.material.properties["strengths"]

    @staticmethod
    def _get_f(
        *,
        thickness: float,
        yield_or_ult: Union[bool, str],
        strengths: List[List[float]],
    ) -> float:
        """
        A static method to calculate the yield strength of a specific

        :param thickness: The thickness of the steel.
        :param yield_or_ult: Return the yield strength or ultimate? If True or "y",
            return yield, if False or "u" then return ultimate.
        :param strengths: The strengths of the steel vs the thickness, in a list of
            lists:

            [
                [t_1, ..., t_n],
                [fy_1, ..., fy_n],
                [fu_1, ..., fu_n],
            ]
        :return: The yield strength of the section.
        """

        # do a couple of simple tests

        thicknesses_list = strengths[0]

        if thickness < 0:
            raise InvalidThicknessError(
                f"Thickness used to determine the strength should be > 0. "
                + f"Thickness given was {thickness}"
            )

        # next check the thickness list is sorted
        larger = thicknesses_list[1:]
        smaller = thicknesses_list[:-1]

        for l, s in zip(larger, smaller):

            if l - s <= 0:
                raise InvalidMaterialError(
                    f"Expected that the strengths list in the material object would be "
                    + f"sorted by thickness. Strengths list was {strengths}."
                )

        # now we know it is sorted, check if thickness is less than the largest
        # thickness in the strengths list.

        if thickness > thicknesses_list[-1]:
            raise InvalidThicknessError(
                f"Expected thickness to be within the strength range of the provided "
                + f"strengths. Thickness was {thickness} and strengths were {strengths}"
            )

        # now we need to actually get the strength

        if isinstance(yield_or_ult, str):
            yield_or_ult= yield_or_ult.lower()

        yield_choice = {"y": 1, "u": 2, True: 1, False: 2}

        strength_index = yield_choice[yield_or_ult]

        # now find the index of the next largest thickness
        for i, t in enumerate(thicknesses_list):

            if thickness <= t:
                # since thicknesses_list is sorted we know that the first thickness
                # where thickness is <= t is the index of the first larger thickness

                return strengths[strength_index][i]

        raise MaterialError(
            f"Unknown error determining material yield or ultimate strength."
        )

    @classmethod
    def AS4100_sect_factory(cls, section) -> "AS4100Section":

        if isinstance(section, Circle):
            return AS4100Circle(section=section)
        else:
            raise NotImplementedError()


class AS4100Circle(AS4100Section):

    section: Circle  # tyoe hint on section.

    def __init__(self, *, section: Circle):

        super().__init__(section=section)

    @property
    def min_fy(self):

        return self._get_f(
            thickness=self.section.radius * 2,
            yield_or_ult="Y",
            strengths=self._strengths,
        )

    @property
    def min_fu(self):

        return self._get_f(
            thickness=self.section.radius * 2,
            yield_or_ult="U",
            strengths=self._strengths,
        )


def s6_2_λ_e_flatplate(b, t, f_y, f_ref=250.0):
    """
    Calculates the slenderness of a plate element to
    AS4100 S6.2
    
    b: the width of a plate element
    t: thickness of the element
    f_y: the yield strength of the element in MPa
    f_ref: the reference yield stress, by default 250MPa
    """

    return (b / t) * ((f_y / f_ref) ** 0.5)


def s6_2_λ_e_CHS(d_o, t, f_y, f_ref=250.0):
    """
    Calculates the slenderness of a CHS element to
    AS4100 S6.2
    
    d_o: the outside diameter of the CHS
    t: thickness of the element
    f_y: the yield strength of the element in MPa
    f_ref: the reference yield stress, by default 250MPa
    """

    return (d_o / t) * (f_y / f_ref)


def s6_2_b_e_flatplate(b, λ_e, λ_ey):
    """
    Calculates the effective width of a flat plate element to
    AS4100 S6.2
    
    b: the width of the plate element
    λ_e: the effective slenderness of the plate
    λ_ey: the yield slenderness limit for a
    reference plate of similar configuration (AS4100 T6.2.4)
    """

    return min(b * (λ_ey / λ_e), b)


def s6_2_d_e_CHS(d_o, λ_e, λ_ey):
    """
    Calculates the effective diameter of a CHS element to
    AS4100 S6.2
    
    d_o: the outside diameter of the CHS
    λ_e: the effective slenderness of the CHS
    λ_ey: the yield slenderness limit for a
    reference CHS of similar configuration (AS4100 T6.2.4)
    """

    d_e1 = d_o * (λ_ey / λ_e) ** 0.5
    d_e2 = d_o * (3 * λ_ey / λ_e) ** 2

    return min(d_e1, d_e2, d_o)


def s6_2_A_e_flatplate(b, t, f_y, λ_ey, f_ref=250.0):
    """
    Calculates the compression area of a flat
    plate element to AS4100 S6.2
    
    b: width of the plate
    t: thickness of the plate
    f_y: yield stress of the plate
    λ_ey: the yield slenderness limit for a
    reference plate of similar configuration (AS4100 T6.2.4)
    f_ref: the reference yield stress, by default 250 MPa
    """

    λ_e = s6_2_λ_e_flatplate(b, t, f_y, f_ref)  # slenderness of plate
    b_e = s6_2_b_e_flatplate(b, λ_e, λ_ey)  # effective width

    return b_e * t


def s6_2_A_e_CHS(d_o, t, f_y, λ_ey, f_ref=250.0):
    """
    Calculates the compression area of a flat
    plate element to AS4100 S6.2
    
    d_o: outside diameter of the plate
    t: thickness of the plate
    f_y: yield stress of the CHS
    λ_ey: the yield slenderness limit for a
    reference CHS of similar configuration (AS4100 T6.2.4)
    f_ref: the reference yield stress, by default 250 MPa
    """

    λ_e = s6_2_λ_e_CHS(d_o, t, f_y, f_ref)  # effective slenderness
    d_e = s6_2_d_e_CHS(d_o, λ_e, λ_ey)  # effective diameter

    c = HollowCircle(0, 0, d_e / 2, d_e / 2 - t)

    return c.area()


def s6_2_k_f_Form_Factor(A_n, A_e):
    """
    Calculate the form factor to AS4100 S6.2

    A_n: the net area as per AS4100 S6.2
    A_e: the effective area as per AS4100 S6.2
    """

    return A_e / A_n
