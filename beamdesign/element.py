from typing import Dict, List, Union

import numpy as np

from beamdesign.const import LoadComponents
from beamdesign.loadcase import LoadCase
from beamdesign.sections.section import Section
from beamdesign.utility.exceptions import ElementLengthError


class Element:
    """
    This is a basic Element object. It is intended that multiple ``Element`` objects
    will form the basis of a single Beam object, to allow easier mapping between the
    output of FEA models, where multiple FEA elements will correspond to a single
    design ``Beam`` objects.
    """

    def __init__(
        self, *, loads: Dict[int, LoadCase], length=None, section: Section = None
    ):
        """
        Constructor for an ``Element``.

        :param loads: The loads on the ``Element``. Must take the form of a dictionary
            of LoadCase objects mapped to a unique integer ID.
        :param length: The length of the ``Element``, corresponding to its real world
            length.
        :param section: The section of the ``Element``.
        """

        if length is not None:
            if length < 0.0:
                raise ElementLengthError(
                    f"Expected length to be +ve or None, actual length was {length}"
                )

        self.length = length
        self.section = section

        self._loads = loads

    @property
    def loads(self) -> Dict[int, LoadCase]:
        """
        The loads on the ``Element``. This is a property decorator to enforce read-only
        status.

        :return: The loads on the element as a dictionary of ``LoadCase`` objects.
        """
        return self._loads

    @property
    def no_load_cases(self) -> int:
        """
        The no. of load cases stored on the element.

        :return: The no. of load cases stored on the element.
        """
        return len(self.load_cases)

    @property
    def load_cases(self) -> List[int]:
        """
        Returns a list of the load cases on the ``Element``.

        :return: Returns a list of the load cases on the ``Element``. These are the keys
            of the self.loads dictionary.
        """
        return list(self.loads.keys())

    def get_loads(
        self,
        *,
        load_case: int,
        position: Union[List[float], float] = None,
        min_positions: int = None,
        component: Union[int, str, LoadComponents] = None,
    ) -> np.ndarray:
        """
        Gets the load in an ``Element`` in a given load case and at a given position.
        If there are multiple loads at a position it returns all of them. Returns in the
        form of a numpy array of the format:

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

        The values of position are normalised local positions between 0.0 and 1.0.
        To get the true global length along the element they should be multiplied by
        ``self.length``. This is not done at this stage as global lengths will generally
        only be required on a ``Beam`` object which may consist of multiple elements.

        :param load_case: The load case to get the loads in.
        :param position: The position at which to return the load. Position values
            should be entered as floats between 0.0 and 1.0 where 0.0 and 1.0 define
            the ends of the element on which the load case is being applied. Positions
            in global positions (i.e. based on real world length) must be normalised by
            dividing by the element length.

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

        load = self.loads[load_case]

        return load.get_load(
            position=position, min_positions=min_positions, component=component
        )

    def load_positions(self, *, load_case: int):
        """
        Returns all the stored load positions in a given load case. The load case must
        be specified because it is possible that different load cases would have
        different stored positions.

        :param load_case: The load case to return the positions from, as an int that
            can be used to index into the LoadCase Dict.
        :return: Returns all the positions that loads are stored in the given
            ``LoadCase``.
        """

        return self.loads[load_case].load_positions

    @classmethod
    def empty_element(cls, length: float = 0.0, section=None, material=None):
        """
        A constructor for an empty ``Element`` with an empty  ``LoadCase`` object at
        load case 0.

        This is a helper method for easily instantiating ``Elements`` for testing etc.

        :param length: An optional length for the empty ``Element``.
        :param section: The section type of the element.
        :return: An ``Element`` object.
        """

        loads = LoadCase()
        loads = {0: loads}

        return cls(loads=loads, length=length, section=section)

    @classmethod
    def constant_load_element(
        cls,
        case_id: int = 0,
        VX: float = 0,
        VY: float = 0,
        N: float = 0,
        MX: float = 0,
        MY: float = 0,
        T: float = 0,
        length: float = 0,
        section=None,
    ) -> "Element":
        """
        Creates an ``Element`` with a single ``LoadCase`` with constant load along its
        length. Primarily intended to be used for testing purposes.

        :param case_id: The ID to use for the LoadCase.
        :param VX: The VX load component.
        :param VY: The VY load component.
        :param N: The N load component.
        :param MX: The MX load component.
        :param MY: The MY load component.
        :param T: The T load component.
        :param length: The length of the element.
        :param section: The section of the element.
        :return: An ``Element`` with constant load along its length.
        """

        loads = LoadCase.constant_load(VX=VX, VY=VY, N=N, MX=MX, MY=MY, T=T)
        loads = {case_id: loads}

        return cls(loads=loads, length=length, section=section)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            + f"length={self.length}, "
            + f"section={self.section}, "
            + f"material={self.section}, "
            + f"no. load cases={self.no_load_cases}"
            + f")"
        )
