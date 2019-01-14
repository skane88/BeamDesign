"""
This file is intended to contain a class for AS4100 checks.
"""

from BeamDesign.Beam import Beam
from BeamDesign.CodeCheck.CodeCheck import CodeCheck


class AS4100(CodeCheck):
    def __init__(self, beam: Beam = None, section=None):

        super().__init__(beam=beam, section=section)

    def tension_capacity(self):

        raise NotImplementedError()

    def get_section(self, position: float = None):

        raise NotImplementedError
