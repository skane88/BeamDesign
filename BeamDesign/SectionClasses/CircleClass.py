"""This defines a class of circular "section" objects
for calculating section properties. It inherits from
"clsSection"."""

from BeamDesign.SectionClasses.SectionClass import SectionClass
import math

class CircleClass(SectionClass):
    '''
    CircleClass implements a class for  calculating
    section properties of a circular section.
    '''

    def __init__(self, x = 0., y = 0., radius = 0.):
        '''
        Initialise the Circle object.
        
        x: the x co-ordinate of the centre of the shape. Default is 0.
        y: the y co-ordinate of the centre of the shape. Default is 0.
        radius_i: the interior radius of the shape. Default is 0.
        radius_o: the exterior radius of the shape. Default is 0.
        '''
        super().__init__(x, y)
        self.radius = radius

    def area(self):
        return math.pi() * (radius ** 2)

    def is_circle(self):
        '''
        Is the section circular or not?
        '''

        return True

    def is_hollow(self):
        '''
        Is the section hollow or not?
        '''

        return False