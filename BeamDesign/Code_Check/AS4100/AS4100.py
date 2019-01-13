"""
This file is intended to contain a class for AS4100 checks.
"""

from BeamDesign.Code_Check.CodeCheck import CodeCheck


class AS4100(CodeCheck):
    def __init__(self, beam, section):

        super().__init__(beam=beam, section=section)
