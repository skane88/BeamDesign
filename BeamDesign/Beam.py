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

from typing import Union
from enum import Enum

import numpy as np

from BeamDesign.Utility.Exceptions import LoadCaseError


class Beam:
    pass


class Element:
    def __init__(
        self,
        *,
        length=None,
        section=None,
        material=None,
        name: str = None,
        loads=None,
        **kwargs,
    ):
        """
        A simple beam Element object. It is intended that multiple Elements can be
        combined into a single Beam element.

        :param length:
        :param section:
        :param material:
        :param name:
        :param loads:
        :param kwargs:
        """

        self.length = length
        self.section = section
        self.material = material
        self.name = name
        self.loads = loads

        for i, v in kwargs.items():

            if i in self.__dict__:
                raise ValueError(
                    f"Argument {i} already present in the beam " + f"object."
                )

            self.__dict__[i] = v

    @property
    def loads(self):
        return self._loads

    @loads.setter
    def loads(self, loads: None):

        if loads is None:
            self._loads = loads
            return

        loads = np.array(loads)

        self._loads = loads

    def get_loads(self, *, position):

        return [
            position,
            self.get_load_x(position=position),
            self.get_load_y(position=position),
            self.get_load_z(position=position),
            self.get_load_mx(position=position),
            self.get_load_my(position=position),
            self.get_load_mz(position=position),
        ]

    def get_load_x(self, *, position):

        return self.get_load_generic(position=position, load="x")

    def get_load_y(self, *, position):

        return self.get_load_generic(position=position, load="y")

    def get_load_z(self, *, position):

        return self.get_load_generic(position=position, load="z")

    def get_load_mx(self, *, position):

        return self.get_load_generic(position=position, load="mx")

    def get_load_my(self, *, position):

        return self.get_load_generic(position=position, load="my")

    def get_load_mz(self, *, position):

        return self.get_load_generic(position=position, load="mz")

    def get_load_generic(self, *, position, load: str):

        if self._loads is None:
            return None

        # first get the loads and their positions as numpy arrays:

        p = self.loads[0, :]  # select the entire first row of the array

        l_index = self._load_map[load]

        raise NotImplementedError()


class Components(Enum):
    FX = "FX"
    FY = "FY"
    FZ = "FZ"
    MX = "MX"
    MY = "MY"
    MZ = "MZ"


class LoadCase:

    _loads: np.ndarray
    _load_map = {
        "l": 0,
        Components.FX: 1,
        Components.FY: 2,
        Components.FZ: 3,
        Components.MX: 4,
        Components.MY: 5,
        Components.MZ: 6,
    }

    def __init__(self, *, section=None, loads=None):

        self._section = section

        # set the loads using some setting logic
        self._set_loads(loads=loads)

        pass

    @property
    def loads(self):
        return self._loads

    @property
    def positions(self) -> np.ndarray:
        """
        Returns an array of the positions that loads are available in. Position values
        are stored as a float between 0.0 and 1.0 where 0.0 and 1.0 define the ends of
        the element on which the load case is being applied. To get the true positions
        along the element's lengths these values must be multiplied by the element
        length.

        :return: An array of the position values.
        """

        return self._loads[:, 0]

    @property
    def num_positions(self) -> int:
        """
        Returns the number of positions that loads are stored at.

        :return:
        """

        return len(self.positions)

    def _set_loads(self, *, loads):
        """
        Helper method to set the loads property.

        :param loads: The loads to set. Must be an object that can be formatted into a
            numpy array of shape (n, 7).
        """

        if loads is None:
            self._loads = None
            return

        arr = np.array(loads)

        if len(arr.shape) == 1:
            # if passed a single row list, reshape into a 2D numpy array
            arr = arr.reshape((1, 7))

        # test if array has a position and FX, FY, FZ, MX, MY, MZ
        if arr.shape[1] != 7:
            raise LoadCaseError(
                f"Load cases must form an (n, 7) array. "
                f"Current array shape is {arr.shape}"
            )

        # get a position array for use in further testing
        pos = arr[:, 0]

        # positions should be ascending
        assert np.all(np.diff(pos) >= 0), "Positions should be in ascending order"
        assert np.all(pos <= 1.0) and np.all(
            pos >= 0.0
        ), "Positions should be between 0 & 1.0"

        self._loads = arr

    def _get_row(self, position: float, row_before: bool = True):

        if self._loads.shape[0] == 1:
            return 0

        pass

    def get_loads(self, *, component: Union[str, Components]):
        """
        Gets the values for a given load component at all positions available in the
        element.

        :param component: The component to return.
        :return: Returns a numpy array containing the position and load components in
            the following format:

            [[position1, component_val1]
             [position2, component_val2]
             [position3, component_val3]
             ]
        """

        # if loads is None we can simply return None
        if self._loads is None:
            return None

        # else return the whole component
        if isinstance(component, str):
            component = Components[component]

        comp_idx = self._load_map[component]

        # now get the positions column and the load column for the given component
        return self._loads[:, [0, comp_idx]]

    def get_load(self, *, position: float, component: Union[str, Components]):

        assert (
            0 <= position and position <= 1.0
        ), f"Position must be between 0.0 and 1.0. Position given was {position}."

        # if loads is None we can simply return None
        if self._loads is None:
            # for consistency with the case where we need to return multiple values
            # we should return as a numpy array
            return np.array([[None]])

        # if not, we need to actually search the loads array
        if isinstance(component, str):
            component = Components[component]

        comp_idx = self._load_map[component]

        # if loads is only 1x row long, we just return the value
        if self.num_positions == 1:

            return self.loads[0:1, comp_idx : comp_idx + 1]

        # if loads is greater than 1 then we need to do some interpolation etc.

        # First check for the corner case where there is more than one occurence of
        # position in the table.

        unique, idxs, counts = np.unique(
            self.positions, return_index=True, return_counts=True
        )
        counts_dict = dict(zip(unique, counts))
        idx_dict = dict(zip(unique, idxs))

        if position in counts_dict:

            count = counts_dict[position]

            if count > 1:
                # need to return all instances of the load for the given positions

                idx = idx_dict[position]

                return self.loads[idx : idx + count, comp_idx : comp_idx + 1]

        loads = self.get_loads(component=component)

        xs = loads[:, 0]
        ys = loads[:, 1]

        # for consistency with the case where we need to return multiple values
        # we should return as a numpy array

        ret_val = np.array([[np.interp(position, xs, ys)]])
        return ret_val
