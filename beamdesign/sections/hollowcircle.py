"""Defines a section properties class for hollow circles,
inherited from SectionClass"""

from beamdesign.sections.section import Section
from beamdesign.sections.circle import Circle


class HollowCircle(Section):
    """HollowCircle implements a class for  calculating
    section properties of a hollow circular section.
    """

    def __init__(self, x=0.0, y=0.0, radius_o=0.0, radius_i=0.0):
        """Initialise the HollowCircle object.
        
        x: the x co-ordinate of the centre of the shape.
        y: the y co-ordinate of the centre of the shape.
        radius_o: the exterior radius of the shape.
        radius_i: the interior radius of the shape."""

        super().__init__(x, y)
        self.radius_o = radius_o
        self.radius_i = radius_i

    @property
    def radius_i(self):
        # Set the inner radius with a property decorator.
        # so as to allow use of checking that the inner radius
        # is smaller than the outer in a setter function.

        return self._radius_i

    @radius_i.setter
    def radius_i(self, radius_i=0.0):
        # A setter function to catch the error of the
        # inner radius being larger than the outer radius.

        if radius_i > self.radius_o:
            # test for the inner radius being larger than the outer.
            raise ValueError("inner radius should be smaller than the outer radius")
        else:
            self._radius_i = radius_i

    @property
    def area(self):
        """
        Return the area of the shape.
        """

        i = Circle(self.x, self.y, self.radius_i)
        o = Circle(self.x, self.y, self.radius_o)
        return o.area() - i.area()

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

        return True
