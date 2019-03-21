"""
Contains the LoadCase class used for applying loads to an element.
"""

from typing import Union, List

import numpy as np

from beamdesign.utility.exceptions import LoadCaseError
from beamdesign.const import LoadComponents
from beamdesign.utility.interp import multi_interp


class LoadCase:

    _loads: np.ndarray

    def __init__(self, *, loads=None):
        """
        Initialises a LoadCase object.

        :param case_id: An integer ID to give to the load case.
        :param case_name: A case name.
        :param loads: The loads to set. Must be an object that can be formatted into a
            numpy array of shape (n, 7). The following format is expected:
            [
                [pos_1, vx_1, vy_1, N_1, mx_1, my_1, T_1]
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
        """
        The loads stored in the loadcase object.

        NOTE: this is a read-only property.
        """
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
        component: Union[str, LoadComponents, List[LoadComponents]] = None,
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

        position = self.list_positions(
            min_positions=min_positions, position=position
        )

        if self.loads is not None:
            # then we can do proper interpolation

            load_positions = self.loads[:, 0].transpose()

            # need to handle the special case where pos matches a load position directly
            # as there can be multiple load positions of the same value where there are
            # load discontinuities
            pos_direct = [p for p in position if p in load_positions]
            pos_interp = [p for p in position if p not in load_positions]
            pos_interp = np.array(pos_interp)

            if component is None:

                components = [
                    LoadComponents.VX,
                    LoadComponents.VY,
                    LoadComponents.N,
                    LoadComponents.MX,
                    LoadComponents.MY,
                    LoadComponents.T,
                ]

            elif isinstance(component, str):
                components = [LoadComponents[component]]
            elif isinstance(component, int):
                components = [LoadComponents(component)]
            elif isinstance(component, LoadComponents):
                components = [component]
            else:
                components = component

            components = [c.value for c in components]

            if np.array_equal(position, np.unique(self.load_positions)):
                # shortcut - if the positions exactly matches the load positions
                # we can just return the loads
                return self.loads[:, [0] + components]

            loads_direct = None
            loads_interp = None

            # now get the loads that come out of the positions that match loads directly
            if len(pos_direct) > 0:
                # first we find all rows where position is in pos_direct
                index_direct = np.in1d(self.loads[:, 0], pos_direct)

                # then we get the loads at these positions
                # note that we are using the np.ix_ function because combining a boolean
                # and an integer indexing array does not work as expected.
                loads_direct = self.loads[np.ix_(index_direct, [0] + components)]
                loads_direct = loads_direct.reshape((-1, len([0] + components)))

            if len(pos_interp) > 0:
                loads_to_interp = self.loads[:, components].transpose()

                loads_interp = multi_interp(
                    x=pos_interp, xp=load_positions, fp=loads_to_interp
                ).transpose()

                loads_interp = np.hstack((pos_interp.reshape((-1,1)), loads_interp))

            if loads_direct is not None and loads_interp is not None:
                # add a new column with an index value to allow us to sort
                # once we combine both arrays
                indices = np.arange(loads_direct.shape[0]).reshape((-1, 1))
                loads_direct = np.hstack((indices, loads_direct))

                indices = np.arange(loads_interp.shape[0]).reshape((-1, 1))
                loads_interp = np.hstack((indices, loads_interp))

                ret_val = np.vstack((loads_direct, loads_interp))
                # now sort on the secondary index
                ret_val = ret_val[ret_val[:, 0].argsort()]
                # next sort on the position (which is more important. Use 'mergesort'
                # to maintain the position where there are multiple rows at the same
                # position
                # (ref https://stackoverflow.com/questions/2828059/sorting-arrays-in-numpy-by-column)
                ret_val = ret_val[ret_val[:, 1].argsort(kind="mergesort")]
                # now drop the index column
                ret_val = ret_val[:, 1:]
            elif loads_direct is not None:
                # if so we can just return the direct loads
                ret_val = loads_direct
            else:
                # otherwise return the interpreted loads.
                ret_val = loads_interp
        else:
            # in the case where self.loads is none, we need to build a return array
            # of Nones
            position = np.array(position).reshape((-1, 1))
            loads = np.empty(shape=position.shape, dtype=object)
            ret_val = np.hstack((position, loads))


        # for i, p in enumerate(position):
        #
        #    val = self._get_load_single_position(position=p, component=component)
        #
        #   if i == 0:
        #        ret_val = val
        #    else:
        #        ret_val = np.vstack((ret_val, val))

        return ret_val

    def list_positions(
        self, *, min_positions: int = None, position: Union[float, List[float]] = None
    ) -> List[float]:
        """
        Given a minimum no. of positions or a

        NOTE: if a single position is provided the return is simply the input position,
        or a list of positions, the return is simply the input positions converted to a
        list for use later.

        NOTE 2: if both min_positions & position are None or provided an error will be
        raised.

        :param min_positions: The minimum no. of positions to generate. NOTE: this is
        the minimum no. of positions - the function will return all intermediate load
        positions etc. in addition to equally spaced positions.
        :param position:
        :return: A list of positions on the LoadCase, between 0.0 and 1.0.
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

            # now convert to a unique and sorted list.
            position = list(sorted(set(position)))

        else:
            # if we are here, we need to build a list of the positions.
            # - we will start from the positions already in the loads document so that
            # we don't miss anything.

            position = set(self.load_positions)

            # now we get an array of positions

            lin_pos = np.linspace(0.0, 1.0, min_positions)

            # now we need to combine them

            position.update(lin_pos)

            # now we convert to a sorted list

            position = list(sorted(position))

            # do an assert to confirm.

            assert len(position) >= min_positions, (
                f"Error generating number of positions. Expected {min_positions}, "
                f"generated {len(position)} positions."
            )
        return position

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
