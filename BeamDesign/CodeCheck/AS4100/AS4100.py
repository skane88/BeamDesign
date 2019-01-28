"""
This file is intended to contain a class for AS4100 checks, and also the actual checks
themselves. Specific equations from the code have been split off into other files to
minimise the size of this file.
"""

from typing import List

from BeamDesign.Beam import Beam
from BeamDesign.CodeCheck.CodeCheck import CodeCheck
from BeamDesign.Sections.Section import Section


class AS4100(CodeCheck):
    def __init__(
        self,
        *,
        φ: float,
        αu: float,
        kt: float,
        beam: Beam = None,
        section=None,
    ):
        """

        :param beam:
        :param section:
        :param kwargs:
        """

        super().__init__(
            beam=beam, section=section
        )

        self.φ = φ
        self.αu = αu
        self.kt = kt

    def tension_capacity(self):

        raise NotImplementedError()

    def get_all_sections(self) -> List[Section]:

        return super().get_all_sections()

    def get_section(self, position: float = None) -> List[List[Section]]:

        return super().get_section(position=position)

    def Nt(self):
        """

        :return:
        """

        return min(self.Nty(), self.Ntu())

    def φNt(self):
        """

        :return:
        """

        return self.φ * self.Nt()

    def Nty(self):
        """
        Calculates the
        :return:
        """

        Ag = self.section.area
        fy = self.section.min_strength_yield

        return self.s7_2_Nty(Ag=Ag, fy=fy)

    def φNty(self):

        return self.φ * self.Nty()

    def Ntu(self):

        An = self.section.area
        fu = self.section.min_strength_ultimate

        return self.s7_2_Ntu(An=An, fu=fu, kt=self.kt, αu=self.αu)

    def φNtu(self):
        return self.φ * self.Nty()

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
