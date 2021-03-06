"""
This defines a class of circular "section" objects for calculating section properties.
It inherits from ``clsSection``.
"""

import math

from beamdesign.sections.section import Section
from beamdesign.materials.material import Material


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
    def is_circle(self) -> bool:

        return True

    @property
    def is_hollow(self) -> bool:

        return False

    @property
    def is_composite(self) -> bool:

        return False

    @property
    def area(self) -> float:
        return math.pi * (self.radius ** 2)

    @property
    def area_net(self) -> float:
        return self.area

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            + f"radius={self.radius}, "
            + f"material={self.material}"
            + f")"
        )
