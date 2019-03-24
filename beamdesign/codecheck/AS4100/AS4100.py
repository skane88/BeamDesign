"""
This file is intended to contain a class for AS4100 checks, and also the actual checks
themselves. Specific equations from the code have been split off into other files to
minimise the size of this file.
"""

from typing import List, Union, Dict, Tuple
from pathlib import Path

import toml

from beamdesign.beam import Beam
from beamdesign.codecheck.codecheck import CodeCheck
from beamdesign.sections.section import Section
from beamdesign.codecheck.AS4100.AS4100_sect_props import AS4100Section
from beamdesign.utility.exceptions import SectionOnlyError
from beamdesign.utility.solvers import secant
from beamdesign.const import LoadComponents


class AS4100(CodeCheck):
    def __init__(
        self, *, φ_steel: float, αu: float, kt: float, beam: Beam = None, section=None
    ):
        """

        :param beam:
        :param section:
        :param kwargs:
        """

        super().__init__(beam=beam, section=section)

        as4100_sects = []

        for s in self.sections:
            as4100_sects += [AS4100Section.AS4100_sect_factory(section=s)]

        self._as4100_sections = as4100_sects

        self.φ_steel = φ_steel
        self.αu = αu
        self.kt = kt

    @property
    def sections(self) -> List[Section]:

        return super().sections

    @property
    def as4100_sections(self) -> List["AS4100Section"]:
        """
        Returns a list of all the AS4100Sections that make up the AS4100 object. These
        are wrapper classes over the top of the underlying beam element sections, such
        that self.sections[n] is the basis for self.as4100_sections[n].
        """

        return self._as4100_sections

    def tension_capacity(self, *, position: Union[List[float], float] = None):

        return self.φNt(position=position)

    def tension_utilisation(
        self,
        *,
        load_case: Union[int, List[int]] = None,
        position: Union[List[float], float] = None,
    ) -> float:

        if load_case is not None:
            if isinstance(load_case, int):
                # convert into List now for consistency later.
                load_case = [load_case]

        load = load_case

        if position is not None:
            if isinstance(position, float):
                # convert position into List now for consistency later.
                position = [position]

        pos = position

        ret_loads = []
        ret_pos = []
        ret_util = []

        if load is None:
            # if load is None, we need to go over all the load cases.
            load = self.beam.load_cases

        for l in load:

            if pos is None:
                pos = self.beam.list_positions(
                    min_positions=self.assessment_points, load_case=l
                )[0]

            for p in pos:
                # go through every position and get the capacity & load

                t_cap = self.tension_capacity(position=p)

                def cap_func(load):
                    return t_cap

                # next get the tension load at the position to be checked.
                tension = self.get_loads(
                    load_case=l, position=p, component=LoadComponents.N
                )[..., 1]

                for t in tension:
                    # handle the case where multiple loads are at a given position.

                    if t <= 0.0:
                        # handle compression or empty cases - can simply state
                        # utilisation is 0.0
                        x = 0.0
                    else:

                        def util_func(x, load, capacity_func):

                            return (x * load) / capacity_func(x * load) - 1.0

                        x, i, b = secant(
                            util_func,
                            t,
                            cap_func,
                            x_low=-100_000,
                            x_high=100_000,
                            fallback=False,
                        )

                        if x != 0:
                            x = 1 / x

                    ret_loads += [l]
                    ret_pos += [p]
                    ret_util += [x]

        if load_case is None and position is not None:
            # if load case is none but position is not, filter on position.

            ret_util = [ret_util[i] for i, p in enumerate(ret_pos) if p in position]

        if position is None and load_case is not None:
            # if position is None, but load case is not, filter on load case.

            ret_util = [ret_util[i] for i, l in enumerate(ret_loads) if l in load_case]

        return max(ret_util)

    def get_section(
        self,
        *,
        position: Union[List[float], float] = None,
        min_positions: int = None,
        load_case: int = None,
    ) -> Tuple[List[float], List[Section]]:

        return super().get_section(position=position)

    def get_as4100_section(
        self,
        *,
        position: Union[List[float], float] = None,
        min_positions: int = None,
        load_case: int = None,
    ) -> Tuple[List[float], List[AS4100Section]]:
        """
        Gets the AS4100 section properties at a given position or list of positions.

        The positions can either be requested directly, or as a minimum number of
        positions along the beam. If specified as minimum positions, a load case can be
        specified as well (to include load discontinuities etc.

        If the ``CodeCheck`` object is a section based object, it will raise a
        SectionOnlyError.

        :param min_positions: The minimum no. of positions to return.
        :param position: The position to return the section from. If the ``codecheck``
            object has only a section property (and not a ``Beam`` property) it returns
            ``self.section``. If ``None`` it returns all sections. If a position is
            given it returns the sections at the given positions.
        :param load_case: he load case to consider if using min_positions. Can be
            ``None``, in which case only the start & ends of elements are returned.
        :return: Returns a tuple of positions and AS4100 sections:

            (
                [pos_1, ..., pos_n]
                [section_1, ..., section_n]
            )
        """

        if self.beam is None:
            raise SectionOnlyError(
                f"get_section does not apply to Section based CodeCheck objects."
            )

        positions, elements, local_positions = self.beam.list_positions(
            position=position, min_positions=min_positions, load_case=load_case
        )

        as4100_sections = [self.as4100_sections[e] for e in elements]

        return (positions, as4100_sections)

    def get_loads(
        self,
        *,
        load_case: int,
        position: Union[List[float], float] = None,
        min_positions: int = None,
        component: Union[int, str, LoadComponents] = None,
    ):

        return super().get_loads(
            load_case=load_case,
            position=position,
            min_positions=min_positions,
            component=component,
        )

    def Nt(self, *, position: Union[List[float], float] = None):
        """
        Calculates the tension capacity of the AS4100 object.

        :param position: The position to calculate the capacity at. Can be a float, can
            be a list of floats or can be None.

            Note that if None is provided, a single tension capacity is returned which
            is the minimum tension capacity of the entire AS4100 object.
        :return: The calculated tension capacity (minimum of Nty and Ntu).
        """

        return min(self.Nty(position=position), self.Ntu(position=position))

    def φNt(self, *, position: Union[List[float], float] = None):
        """
        Calculates the tension capacity of the AS4100 object.

        :param position: The position to calculate the capacity at. Can be a float, can
            be a list of floats or can be None.

            Note that if None is provided, a single tension capacity is returned which
            is the minimum tension capacity of the entire AS4100 object.
        :return: The calculated tension capacity (minimum of Nty and Ntu) multiplied by
            the capacity reduction factor.
        """

        return self.φ_steel * self.Nt(position=position)

    def Nty(self, *, position: Union[List[float], float] = None) -> float:
        """
        Calculates the tension yield capacity of the AS4100 object.

        :param position: The position to calculate the capacity at. Can be a float, can
            be a list of floats or can be None.

            Note that if None is provided, a single tension capacity is returned which
            is the minimum tension capacity of the entire AS4100 object.
        :return: The calculated yield tension capacity.
        """

        if position is None:
            sections = self.as4100_sections
        else:
            if isinstance(position, float):
                # if a float is provided, wrap it in a list for consistent logic below.
                position = [position]

            positions, sections = self.get_as4100_section(position=position)

        # now we have a list of all sections to check, do the check
        N = [self.s7_2_Nty(Ag=s.Ag, fy=s.min_fy) for s in sections]

        return min(N)

    def φNty(self, *, position: Union[List[float], float] = None):
        """
        Calculates the tension yield capacity of the AS4100 object.

        :param position: The position to calculate the capacity at. Can be a float, can
            be a list of floats or can be None.

            Note that if None is provided, a single tension capacity is returned which
            is the minimum tension capacity of the entire AS4100 object.
        :return: The calculated yield tension capacity, multiplied by the capacity
            reduction factor.
        """

        return self.φ_steel * self.Nty(position=position)

    def Ntu(self, *, position: Union[List[float], float] = None):
        """
        Calculates the tension yield capacity of the AS4100 object.

        :param position: The position to calculate the capacity at. Can be a float, can
            be a list of floats or can be None.

            Note that if None is provided, a single tension capacity is returned which
            is the minimum tension capacity of the entire AS4100 object.
        :return: The calculated ultimate capacity.
        """

        if position is None:
            sections = self.as4100_sections
        else:
            if isinstance(position, float):
                # if a float is provided, wrap it in a list for consistent logic below.
                position = [position]

            positions, sections = self.get_as4100_section(position=position)

        # now we have a list of all sections to check, do the check
        N = [
            self.s7_2_Ntu(An=s.An, fu=s.min_fu, kt=self.kt, αu=self.αu)
            for s in sections
        ]

        return min(N)

    def φNtu(self, *, position: Union[List[float], float] = None):
        """
        Calculates the tension yield capacity of the AS4100 object.

        :param position: The position to calculate the capacity at. Can be a float, can
            be a list of floats or can be None.

            Note that if None is provided, a single tension capacity is returned which
            is the minimum tension capacity of the entire AS4100 object.
        :return: The calculated ultimate tension capacity, multiplied by the capacity
            reduction factor.
        """

        return self.φ_steel * self.Nty(position=position)

    @staticmethod
    def s7_1_Nt(
        *, Ag: float, An: float, fy: float, fu: float, kt: float, αu: float
    ) -> float:
        """
        Calculates the tension capacity of a section according to AS4100 S7.1.

        :param Ag: Gross area of a section in m².
        :param An: Net area of the section in m², allowing for holes as required
            by AS4100.
        :param fy: The yield strength of the section in Pa. If different components
            have different yield strengths the minimum strength of the section
            should be used. Where a section has a significantly different strength
            the result may be too conservative and this function may not be
            appropriate (i.e. a 250 grade web and a 450 grade flange) - more
            detailed analysis (FEA modelling etc.) may be required.
        :param fu: The ultimate strength of the section in Pa.
        :param kt: The connection efficiency factor / eccentric connection factor
            as per AS4100.
        :param αu: A factor for the uncertainty in ultimate strength as per AS4100 S7.2.
            Note that AS4100 does not provide a variable name for this value so αu is
            used, consistent with other uses of α in AS4100. AS4100 provides a value of
            0.85 for this factor.
        :return:
        """

        return min(
            AS4100.s7_2_Nty(Ag=Ag, fy=fy), AS4100.s7_2_Ntu(An=An, fu=fu, kt=kt, αu=αu)
        )

    @staticmethod
    def s7_2_Nty(*, Ag: float, fy: float) -> float:
        """
        Calculates the yield capacity of a member but does not include the capacity
        reduction factor.

        :param Ag: Gross area of a section in m².
        :param fy: Yield strength of a section in Pa.
        :return: Returns the yielding capacity of the member in N.
        """

        return Ag * fy

    @staticmethod
    def s7_2_Ntu(*, An: float, fu: float, kt: float, αu: float) -> float:
        """
        Calculates the ultimate fracture capacity of a section and includes the
        additional uncertainty factor from AS4100.

        :param An: Net area of the section in m², allowing for holes as required
            by AS4100.
        :param fu: The ultimate strength of the section in Pa.
        :param kt: The connection efficiency factor / eccentric connection factor
            as per AS4100.
        :param αu: A factor for the uncertainty in ultimate strength as per AS4100 S7.2.
            Note that AS4100 does not provide a variable name for this value so αu is
            used, consistent with other uses of α in AS4100. AS4100 provides a value of
            0.85 for this factor.
        :return: Returns the ultimate fracture capacity in N.
        """

        return An * fu * kt * αu

    @classmethod
    def default_AS4100(
        cls, beam: Beam = None, section: Section = None, file_path: str = None
    ) -> "AS4100":

        config = cls.get_defaults(file_path=file_path)
        defaults = config["defaults"]

        return cls(beam=beam, section=section, **defaults)

    @classmethod
    def get_defaults(cls, *, file_path: str = None) -> Dict[str, any]:
        """
        This class method loads a JSON file containing default values for AS4100 objects
        that is stored in the specified location.
        If not specified, the default values stored in the package are loaded.

        :param file_path: The file_path to load the values from. If not specified, the
            default values will be loaded from the file in the package.
        :return: A dictionary containing the parsed JSON file.
        """

        if file_path is None:
            mod_file = Path(__file__)
            file_path = mod_file.parent / "AS4100.toml"

        else:
            file_path = Path(file_path)

        with file_path.open(mode="r", encoding="utf-8") as f:
            vals = toml.load(f=f)

        return vals
