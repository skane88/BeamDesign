"""
Contains the LoadCase class used for applying loads to an element.
"""

from typing import Union, List

import numpy as np

from beamdesign.utility.exceptions import LoadCaseError
from beamdesign.const import LoadComponents


class LoadCase:

    _loads: np.ndarray

    def __init__(self, *, loads=None):
        """
        Initialises a LoadCase object.

        :param case_id: An integer ID to give to the load case.
        :param case_name: A case name.
        :param loads: The loads to set. Must be an object that can be formatted into a
            numpy array of shape (n, 7). The following format is expected:

            [[pos_1, vx_1, vy_1, N_1, mx_1, my_1, T_1]
             [pos_2, vx_2, vy_2, N_2, mx_2, my_2, T_2]
             ...
             [pos_n, vx_n, vy_n, N_n, mx_n, my_n, T_n]
             ]
        """

        # set the loads using some setting logic
        self._set_loads(loads=loads)

        pass

    @property
    def loads(self):
        return self._loads

    @property
    def load_positions(self) -> np.ndarray:
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

        return len(self.load_positions)

    def _set_loads(self, *, loads):
        """
        Helper method to set the loads property.

        :param loads: The loads to set. Must be an object that can be formatted into a
            numpy array of shape (n, 7). The following format is expected:

            [[pos_1, vx_1, vy_1, fz_1, mx_1, my_1, T_1]
             [pos_2, vx_2, vy_2, fz_2, mx_2, my_2, T_2]
             ...
             [pos_n, vx_n, vy_n, fz_n, mx_n, my_n, T_n]
             ]
        """

        if loads is None:
            self._loads = None
            return

        arr = np.array(loads)

        if len(arr.shape) == 1:
            # if passed a single row list, see if we can reshape into a 2D numpy array

            # first test if it has a position & 6 load components
            if arr.shape[0] != 7:
                raise LoadCaseError(
                    f"Load cases must form an (n, 7) array. "
                    f"Current array shape is {arr.shape}"
                )

            arr = arr.reshape((1, 7))

        else:
            # else if multi-row list, simply check that it has a
            # position and 6x load components

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

    def _get_input_loads(self, *, component: Union[str, int, LoadComponents]):
        """
        Gets the values for a given load component at all positions stored in the
        LoadCase.

        A helper method for ``self.get_load``.

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

    def _get_load_single_component(
        self, *, position: float, component: Union[str, int, LoadComponents]
    ):
        """
        A helper function for ``self.get_load`` that returns the value of a single
        component at a specified position. If there are multiple loads at a position it
        returns all of them. Returns in the form of a numpy array of the format:

        [[load_1]
         [load_2]
         ...
         [load_n]
         ]

        :param position: The position at which to return the load. Position values
            should be entered as a float between 0.0 and 1.0 where 0.0 and 1.0 define
            the ends of the element on which the load case is being applied. Positions
            in real world lengths must be normalised by dividing by the element length.
        length.
        :param component: The component of load to return.
        :return: A numpy array containing the loads at the specified position.
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

        # First check for the corner case where there is more than one occurrence of
        # position in the table.

        unique, idxs, counts = np.unique(
            self.load_positions, return_index=True, return_counts=True
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

        loads = self._get_input_loads(component=component)

        xs = loads[:, 0]
        ys = loads[:, 1]

        # for consistency with the case where we need to return multiple values
        # we should return as a numpy array

        ret_val = np.array([[np.interp(position, xs, ys)]])
        return ret_val

    def _get_load_single_position(
        self, *, position: float, component: Union[str, int, LoadComponents]
    ):
        """
        Helper function for ``self.get_load``.

        Gets the load in a load case at a given position. If there are multiple loads
        at a position it returns all of them. Returns in the form of a
        numpy array of the format:

        [[pos, load_1]
         [pos, load_2]
         ...
         [pos, load_n]
        ]

        If ``component`` is not provided, then an array of all loads at the given
        position is returned:

        [[pos, vx_1, vy_1, N_1, mx_1, my_1, T_1]
         [pos, vx_2, vy_2, N_2, mx_2, my_2, T_2]
         ...
         [pos, vx_n, vy_n, N_n, mx_n, my_n, T_n]
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
            0 <= position <= 1.0
        ), f"Position must be between 0.0 and 1.0. Position given was {position}."

        if component is None:

            fx = self._get_load_single_component(
                position=position, component=LoadComponents.VX
            )
            fy = self._get_load_single_component(
                position=position, component=LoadComponents.VY
            )
            fz = self._get_load_single_component(
                position=position, component=LoadComponents.N
            )
            mx = self._get_load_single_component(
                position=position, component=LoadComponents.MX
            )
            my = self._get_load_single_component(
                position=position, component=LoadComponents.MY
            )
            mz = self._get_load_single_component(
                position=position, component=LoadComponents.T
            )

            comp = np.hstack((fx, fy, fz, mx, my, mz))

        else:
            comp = self._get_load_single_component(
                position=position, component=component
            )

        rows = comp.shape[0]

        pos = np.full((rows, 1), position)

        return np.hstack((pos, comp))

    def get_load(
        self,
        *,
        position: [float, List[float]] = None,
        min_positions: int = None,
        component: Union[str, LoadComponents] = None,
    ):
        """
        Gets the load in a load case at a given position. If there are multiple loads
        at a position it returns all of them. Returns in the form of a
        numpy array of the format:

        [[pos, load_1]
         [pos, load_2]
         ...
         [pos, load_n]
        ]

        If ``component`` is not provided, then an array of all loads at the given
        position is returned:

        [[pos, vx_1, vy_1, N_1, mx_1, my_1, T_1]
         [pos, vx_2, vy_2, N_2, mx_2, my_2, T_2]
         ...
         [pos, vx_n, vy_n, N_n, mx_n, my_n, T_n]
        ]

        :param position: The position at which to return the load. Position values
            should be entered as floats between 0.0 and 1.0 where 0.0 and 1.0 define
            the ends of the element on which the load case is being applied. Positions
            in real world lengths must be normalised by dividing by the element length.
            length.

            Positions can be a single position or a list of positions. If a list is
            provided, any duplicate values will be ignored, and the order will be
            ignored - return values will be at positions sorted ascending from 0.0 to
            1.0.

            If ``position`` is provided, ``min_positions`` must be ``None`` to
            avoid ambiguity.
        :param min_positions: The minimum number of positions to return. Positions will
            be returned such that loads are returned at equally spaced positions between
            0.0 and 1.0 (inclusive). All stored load positions will also be included to
            ensure that discontinuities are included.

            If ``min_positions`` is provided,
            ``position`` must be ``None`` to avoid ambiguity.
        :param component: The component of load to return.
        :return: A numpy array containing the loads at the specified position.
        """

        # first check for ambiguities in position / min_positions

        assert (
            position is not None or min_positions is not None
        ), "Expected either position or num_positions to be provided. Both were None."

        assert (
            position is None or min_positions is None
        ), "Expected only position or num_positions. Both were provided."

        # now that we have done some basic asserts, need to build a list of positions
        # to get values at.

        if position is not None:
            # if position is not None then we can just use it.

            if isinstance(position, float):
                # if position is a float, convert to a list for consistent code below
                position = [position]

            # now convert to a numpy array for use later
            position = np.array(position)
            position = np.unique(position)

        else:
            # if we are here, we need to build a list of the positions.
            # - we will start from the positions already in the loads document so that
            # we don't miss anything.

            position = self.load_positions

            # now we get an array of positions

            lin_pos = np.linspace(0.0, 1.0, min_positions)

            # now we need to combine them

            position = np.concatenate((position, lin_pos))

            # now we get the unique values

            position = np.unique(position)

            # do an assert to confirm.

            assert len(position) >= min_positions, (
                f"Error generating number of positions. Expected {min_positions}, "
                f"generated {len(position)} positions."
            )

        for i, p in enumerate(position):

            val = self._get_load_single_position(position=p, component=component)

            if i == 0:
                ret_val = val
            else:
                ret_val = np.vstack((ret_val, val))

        return ret_val

    @classmethod
    def constant_load(
        cls,
        *,
        VX: float = 0.0,
        VY: float = 0.0,
        N: float = 0.0,
        MX: float = 0.0,
        MY: float = 0.0,
        T: float = 0.0,
    ) -> "LoadCase":
        """
        Constructor for a ``LoadCase`` object with a constant load along its length.

        :param VX: The VX load component.
        :param VY: The VY load component.
        :param N: The N load component.
        :param MX: The MX load component.
        :param MY: The MY load component.
        :param T: The T load component.
        :return: Returns a ``LoadCase`` object.
        """

        pos = 0.0

        loads = [pos, VX, VY, N, MX, MY, T]

        return cls(loads=loads)

    def __repr__(self):
        return f"{self.__class__.__name__}(" + f"loads={self.loads}" + f")"
