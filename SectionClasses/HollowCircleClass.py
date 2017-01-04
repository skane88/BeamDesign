"""Defines a section properties class for hollow circles,
inherited from SectionClass"""

from SectionClass import SectionClass
from CircleClass import CircleClass

class HollowCircleClass(SectionClass):
    """HollowCircleClass implements a class for  calculating
    section properties of a circular section.
    
    Contains methods:

    area: returns the area of the circle."""

    def __init__(self, x = 0.0, y = 0.0, radius_o = 0., radius_i = 0.):
        """Initialise the HollowCircle object.
        
        x: the x co-ordinate of the centre of the shape. Default is 0.
        y: the y co-ordinate of the centre of the shape. Default is 0.
        radius_o: the exterior radius of the shape. Default is 0.
        radius_i: the interior radius of the shape. Default is 0."""
        super().__init__(x, y)
        self.radius_o = radius_o
        self.radius_i = radius_i

    @property
    def radius_i(self):
        #Set the inner radius with a property decorator.
        #so as to allow use of checking that the inner radius
        #is smaller than the outer in a setter function.
        return self._radius_i

    @radius_i.setter
    def radius_i(self, radius_i = 0.):
        #A setter function to catch the error of the
        #inner radius being larger than the outer radius.
        if radius_i > self.radius_o: #test for the inner radius being larger than the outer.
            raise ValueError("inner radius should be smaller than the outer radius") #raise value error
            self._radius_i = None #if for some reason we get this far set the inner radius to None to force more errors.
        else:
            self._radius_i = radius_i

    def area(self):
        """Return the area of the shape."""
        i = CircleClass(x,y,radius_i)
        o = CircleClass(x,y,radius_o)
        return o.area() - i.area()

    def is_circle(self):
        '''
        Is the section circular or not?
        '''

        return True

    def is_hollow(self):
        '''
        Is the section hollow or not?
        '''

        return True