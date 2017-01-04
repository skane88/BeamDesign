"""This defines a parent class of "section" objects
for calculating section properties."""

class SectionClass(object):
    '''
    Section implements a parent class for  calculating
    section properties.

    All child classes should provide at least the following methods
    to override the following methods unless a default return value
    is acceptable:

    Property methods:
    area: returns the area of the shape.

    Query methods:
    is_circle: is the section circular or not?
    is_hollow: is the section hollow or not?
    '''

    def __init__(self, x = 0., y = 0.):
        '''
        Initialise a section object.
        
        x: The x co-ordinate of the centroid of the shape.
        y: The y co-ordinate of the centroid of the shape.
        '''
        
        self.x = x
        self.y = y

    def area():
        '''
        Placeholder method for returning the area of the shape.
        
        Returns 0 by default in this class.
        '''

        return 0.

    def is_circle():
        '''
        Placeholder method returning the answer to a query on the section.

        Is the section circular or not?
        '''

        return False

    def is_hollow():
        '''
        Placeholder method returning the answer to a query on the section.

        Is the section hollow or not?
        '''

        return False