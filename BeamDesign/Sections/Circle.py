"""
This defines a class of circular "section" objects for calculating section properties.
It inherits from ``clsSection``.
"""

from BeamDesign.Sections.Section import Section
import math


class Circle(Section):
    """
    CircleClass implements a class for  calculating
    section properties of a circular section.
    """

    def __init__(self, x=0.0, y=0.0, radius=0.0):
        """
        Initialise the Circle object.

        :param x: the x co-ordinate of the centre of the shape.
        :param y: the y co-ordinate of the centre of the shape.
        :param radius: the radius of the shape.
        """

        super().__init__(x, y)
        self.radius = radius

    @property
    def area(self):
        return math.pi() * (self.radius ** 2)

    @property
    def is_circle(self):
        """
        Is the section circular or not?
        """

        return True

    @property
    def is_hollow(self):
        """
        Is the section hollow or not?
        """

        return False
