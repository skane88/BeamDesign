"""
This defines a class of circular "section" objects for calculating section properties.
It inherits from ``clsSection``.
"""

import math

from BeamDesign.Sections.Section import Section
from BeamDesign.Materials.material import Material


class Circle(Section):
    """
    CircleClass implements a class for  calculating
    section properties of a circular section.
    """

    def __init__(self, *, material: Material, radius=0.0):
        """
        Initialise the Circle object.

        :param radius: the radius of the shape.
        """

        assert radius >= 0.0

        super().__init__(material=material)

        self.radius = radius

    @property
    def area(self) -> float:
        return math.pi * (self.radius ** 2)

    @property
    def area_net(self) -> float:
        return self.area

    @property
    def is_circle(self) -> bool:
        """
        Is the section circular or not?
        """

        return True

    @property
    def is_hollow(self) -> bool:
        """
        Is the section hollow or not?
        """

        return False

    @property
    def min_strength_yield(self) -> float:
        """
        Return the minimum yield strength of the section.
        """

        return self.material.strength_yield(thickness=self.radius * 2)

    @property
    def min_strength_ultimate(self) -> float:
        """
        Return the minimum ultimate strength of the section.
        """

        return self.material.strength_ultimate()

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            + f"radius={self.radius}, "
            + f"material={self.material}"
            + f")"
        )
