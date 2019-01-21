"""This defines a parent class of "section" objects
for calculating section properties."""

from abc import ABC, abstractmethod


class Section(ABC):
    """
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
    """

    def __init__(self):
        """
        Initialise a section object.
        """

        pass

    @property
    @abstractmethod
    def area(self):
        """
        The area of the shape
        """

        pass

    @property
    @abstractmethod
    def is_circle(self):
        """
        Is the section circular or not?
        """

        return False

    @property
    @abstractmethod
    def is_hollow(self):
        """
        Is the section hollow or not?
        """

        return False
