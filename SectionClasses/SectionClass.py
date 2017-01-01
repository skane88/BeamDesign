"""This defines a parent class of "section" objects
for calculating section properties."""

class SectionClass(object):
    """Section implements a parent class for  calculating
    section properties.

    All child classes should provide at least the following methods
    to override the following methods unless a 0. return value
    is acceptable:

    area: returns the area of the shape."""

    def __init__(self, x = 0., y = 0.):
        """Initialise a section object.
        
        x: The x co-ordinate of the centroid of the shape.
        y: The y co-ordinate of the centroid of the shape."""
        self.x = x
        self.y = y

    def area():
        """Placeholder method for returning the area of the shape.
        
        Returns 0 by default in this class."""
        return 0.