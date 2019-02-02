"""
This file is intended to contain a class for AS4100 checks, and also the actual checks
themselves. Specific equations from the code have been split off into other files to
minimise the size of this file.
"""

import itertools
from typing import List, Union, Dict
from pathlib import Path

import toml

from beamdesign.beam import Beam
from beamdesign.codecheck.codecheck import CodeCheck
from beamdesign.sections.section import Section


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

        self.φ_steel = φ_steel
        self.αu = αu
        self.kt = kt

    def tension_capacity(self):

        return self.φNt()

    def tension_utilisation(self):

        raise NotImplementedError()

    def sections(self) -> List[Section]:

        return super().sections()

    def get_section(
        self, position: Union[List[float], float] = None
    ) -> List[List[Section]]:

        return super().get_section(position=position)

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

        if isinstance(position, float):
            # if a float is provided, wrap it in a list for consistent logic below.
            position = [position]

        sections = self.get_section(position=position)

        # now flatten list to make it easier to check the values:
        sections = list(itertools.chain.from_iterable(sections))

        # now we have a list of all sections to check, do the check
        N = [self.s7_2_Nty(Ag=s.area, fy=s.min_strength_yield) for s in sections]

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

        if isinstance(position, float):
            # if a float is provided, wrap it in a list for consistent logic below.
            position = [position]

        sections = self.get_section(position=position)

        # now flatten list to make it easier to check the values:
        sections = list(itertools.chain.from_iterable(sections))

        # now we have a list of all sections to check, do the check
        N = [
            self.s7_2_Ntu(
                An=s.area_net, fu=s.min_strength_ultimate, kt=self.kt, αu=self.αu
            )
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
        defaults = config['defaults']

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

        with file_path.open(mode="r", encoding='utf-8') as f:
            vals = toml.load(f=f)

        return vals
