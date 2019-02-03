"""This defines a parent class of "section" objects
for calculating section properties."""

from abc import ABC, abstractmethod

from beamdesign.materials.material import Material


class Section(ABC):
    """
    Section implements a parent class for  calculating section properties.

    Additionally, a material is stored on the section, as this corresponds to the real
    life situation. A "Beam" can consist of many "Elements" along its length, each of
    which has a specific "Section" and "Material".

    The reason for storing a "Material" on the section object rather than the element is
    to allow for composite sections in future, which will consist of many sections where
    each section may have differing materials.

    Note that the section properties returned by the section properties object will be
    purely geometrical, and should NOT consider any material non-linearity; either due
    to the presence of multiple materials in composite sections, due to material
    non-linearity or due to elastic bucklign non-linearity. This is because different
    design codes handle these calculations differently.

    In some simple situations where a material behaves linearly (such as a compact steel
    section) the geometrical values may approximate the design section properties.
    """

    def __init__(self, *, material: Material = None):
        """
        Initialise a section object.
        """

        self.material = material

    @property
    @abstractmethod
    def is_circle(self) -> bool:
        """
        Is the section circular or not?
        """

        return False

    @property
    @abstractmethod
    def is_hollow(self) -> bool:
        """
        Is the section hollow or not?
        """

        return False

    @property
    @abstractmethod
    def is_composite(self) -> bool:
        """
        Is the section composite or not?
        """

        return False

    @property
    @abstractmethod
    def area(self):
        """
        The area of the shape
        """

        pass

    @property
    @abstractmethod
    def area_net(self):
        """
        The net area of the section after accounting for bolt holes etc. - for simple
        shapes this will usually be equivalent to self.area.
        """

        pass
