"""
This file is intended to define a class that will describe beam objects. These
are intended to represent real world structural elements and as such their
properties will be limited to those that are explicitly real world properties,
such as:

* Length
* Cross section
* Material Properties
* Internal loads (i.e. bending moments etc.). At this point in time it is NOT
intended to include descriptions of applied loads and / or to calculate
load diagrams directly, although a sub-class may be created eventually to allow
this.

Information that is design code specific will not be stored. This includes
(but is not limited to):

* Capacity reduction factors, safety factors
* Location and types of restraints in compression / bending etc.
* Capacity ratios / strength calculations etc.

The intent here is to make the ``Beam`` class as generic as possible for use
with multiple design codes.
"""

import numpy as np


class Beam:

    def __init__(self, *, length, section=None, material=None, name: str=None,
                 loads=None, **kwargs):
        self.length = length
        self.section = section
        self.material = material
        self.loads = loads

        # if name is specified, pop off name and give it to the beam element
        self.name = name

        for i, v in kwargs.items():

            if i in self.__dict__:
                raise ValueError(f'Argument {i} already present in the beam '
                                 + f'object.')

            self.__dict__[i] = v

    @property
    def loads(self):
        return self._loads

    @loads.setter
    def loads(self, loads: None):
        loads = np.array(loads)
        self._loads = loads

    def get_loads(self, *, position):

        return [self.get_load_x(position=position),
                self.get_load_y(position=position),
                self.get_load_z(position=position),
                self.get_load_mx(position=position),
                self.get_load_my(position=position),
                self.get_load_mz(position=position)]

    def get_load_x(self, *, position):

        return self.get_load_generic(position=position, load='x')

    def get_load_y(self, *, position):

        return self.get_load_generic(position=position, load='y')

    def get_load_z(self, *, position):

        return self.get_load_generic(position=position, load='z')

    def get_load_mx(self, *, position):

        return self.get_load_generic(position=position, load='mx')

    def get_load_my(self, *,  position):

        return self.get_load_generic(position=position, load='my')

    def get_load_mz(self, *, position):

        return self.get_load_generic(position=position, load='mz')

    def get_load_generic(self, *,  position, load: str):

        raise NotImplementedError()