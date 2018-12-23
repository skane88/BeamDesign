"""
Contains the LoadCase class used for applying loads to an element.
"""

from typing import Union

import numpy as np

from BeamDesign.Utility.Exceptions import LoadCaseError
from BeamDesign.const import LoadComponents


class LoadCase:

    _loads: np.ndarray

    def __init__(self, *, loads=None):
        """
        Initialises a LoadCase object.

        :param case_id: An integer ID to give to the load case.
        :param case_name: A case name.
        :param loads: The loads to set. Must be an object that can be formatted into a
            numpy array of shape (n, 7). The following format is expected:

            [[pos_1, fx_1, fy_1, fz_1, mx_1, my_1, mz_1]
             [pos_2, fx_2, fy_2, fz_2, mx_2, my_2, mz_2]
             ...
             [pos_n, fx_n, fy_n, fz_n, mx_n, my_n, mz_n]
             ]
        """

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
            numpy array of shape (n, 7). The following format is expected:

            [[pos_1, fx_1, fy_1, fz_1, mx_1, my_1, mz_1]
             [pos_2, fx_2, fy_2, fz_2, mx_2, my_2, mz_2]
             ...
             [pos_n, fx_n, fy_n, fz_n, mx_n, my_n, mz_n]
             ]
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

    def get_loads(self, *, component: Union[str, int, LoadComponents]):
        """
        Gets the values for a given load component at all positions available in the
        element.

        :param component: The component of load to return.
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

        # but first check that the component is a component object
        if isinstance(component, str):
            component = LoadComponents[component]

        if isinstance(component, int):
            component = LoadComponents(component)

        # now get the positions column and the load column for the given component
        return self._loads[:, [0, component.value]]

    def get_load(
        self, *, position: float, component: Union[str, LoadComponents] = None
    ):
        """
        Gets the load in a load case at a given position. If there are multiple loads
        at a position it returns all of them. Returns in the form of a
        numpy array of the format:

        [[load_1]
         [load_2]
         ...
         [load_n]
         ]

        If ``component`` is not provided, then an array of all loads at the given
        position is returned:

        [[fx_1, fy_1, fz_1, mx_1, my_1, mz_1]
         [fx_2, fy_2, fz_2, mx_2, my_2, mz_2]
         ...
         [fx_n, fy_n, fz_n, mx_n, my_n, mz_n]
        ]

        :param position: The position at which to return the load. Position values
            should be entered as a float between 0.0 and 1.0 where 0.0 and 1.0 define
            the ends of the element on which the load case is being applied. Positions
            in real world lengths must be normalised by dividing by the element length.
        length.
        :param component: The component of load to return.
        :return: A numpy array containing the loads at the specified position.
        """

        assert (
            0 <= position and position <= 1.0
        ), f"Position must be between 0.0 and 1.0. Position given was {position}."

        def get_load_single_component(
            *, position: float, component: Union[str, int, LoadComponents]
        ):
            """
            A helper function to allow get_load to return either a single component or
            the whole set of components.
            """

            # if loads is None we can simply return None
            if self._loads is None:
                # for consistency with the case where we need to return multiple values
                # we should return as a numpy array
                return np.array([[None]])

            # if not, we need to actually search the loads array

            # but first check that the component is a component object
            if isinstance(component, str):
                component = LoadComponents[component]

            if isinstance(component, int):
                component = LoadComponents(component)

            # if loads is only 1x row long, we just return the value
            if self.num_positions == 1:

                return self.loads[0:1, component.value : component.value + 1]

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

                    return self.loads[
                        idx : idx + count, component.value : component.value + 1
                    ]

            loads = self.get_loads(component=component)

            xs = loads[:, 0]
            ys = loads[:, 1]

            # for consistency with the case where we need to return multiple values
            # we should return as a numpy array

            ret_val = np.array([[np.interp(position, xs, ys)]])
            return ret_val

        if component is None:

            fx = get_load_single_component(
                position=position, component=LoadComponents.FX
            )
            fy = get_load_single_component(
                position=position, component=LoadComponents.FY
            )
            fz = get_load_single_component(
                position=position, component=LoadComponents.FZ
            )
            mx = get_load_single_component(
                position=position, component=LoadComponents.MX
            )
            my = get_load_single_component(
                position=position, component=LoadComponents.MY
            )
            mz = get_load_single_component(
                position=position, component=LoadComponents.MZ
            )

            return np.hstack((fx, fy, fz, mx, my, mz))

        else:
            return get_load_single_component(position=position, component=component)

    def __repr__(self):
        return f"{self.__class__.__name__}(" f"{self.case_name}, {self.loads}" f")"
