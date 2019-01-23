"""
This file is intended to contain a class for AS4100 checks, and also the actual checks
themselves. Specific equations from the code have been split off into other files to
minimise the size of this file.
"""

from BeamDesign.Beam import Beam
from BeamDesign.CodeCheck.CodeCheck import CodeCheck


class AS4100(CodeCheck):
    def __init__(self, *, beam: Beam = None, section=None, **kwargs):
        """

        :param beam:
        :param section:
        :param kwargs:
        """

        super().__init__(beam=beam, section=section)

    def tension_capacity(self):

        raise NotImplementedError()

    def get_section(self, position: float = None):

        return super().get_section(position=position)

    def Nt(self):
        """

        :return:
        """

        raise NotImplementedError()

    def φNt(self):
        """

        :return:
        """

        raise NotImplementedError()

    @staticmethod
    def s7_1_Nt(
        *, Ag: float, An: float, fy: float, fu: float, kt: float, αu: float = 0.85
    ):
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
        :param αu: A factor for the uncertainty in ultimate srength as per AS4100 S7.2.
            By default 0.85. Note that AS4100 does not provide a variable name for this
            value so αu is used, consistent with other uses of α in AS4100.
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
    def s7_2_Ntu(*, An: float, fu: float, kt: float, αu: float = 0.85) -> float:
        """
        Calculates the ultimate fracture capacity of a section and includes the
        additional uncertainty factor from AS4100.

        :param An: Net area of the section in m², allowing for holes as required
            by AS4100.
        :param fu: The ultimate strength of the section in Pa.
        :param kt: The connection efficiency factor / eccentric connection factor
            as per AS4100.
        :param αu: A factor for the uncertainty in ultimate srength as per AS4100 S7.2.
            By default 0.85. Note that AS4100 does not provide a variable name for this
            value so αu is used, consistent with other uses of α in AS4100.
        :return: Returns the ultimate fracture capacity in N.
        """

        return An * fu * kt * αu
