"""
This file is intended to contain a class for AS4100 checks, and also the actual checks
themselves. Specific equations from the code have been split off into other files to
minimise the size of this file.
"""

from BeamDesign.Beam import Beam
from BeamDesign.CodeCheck.CodeCheck import CodeCheck


class AS4100(CodeCheck):
    def __init__(self, *, beam: Beam = None, section=None, **kwargs):

        super().__init__(beam=beam, section=section)

    def tension_capacity(self):

        raise NotImplementedError()

    def get_section(self, position: float = None):

        return super().get_section(position=position)

    @staticmethod
    def S7_tension(Ag: float, An: float, fy: float, fu: float, kt: float):

        raise NotImplemented


