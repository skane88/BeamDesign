"""
This file contains the exceptions for the library.
"""


class BeamDesignError(Exception):
    """
    Master exception that all custom exceptions should inherit from.
    """

    pass


class LoadCaseError(BeamDesignError):
    """
    Main exception for ``LoadCase`` errors.
    """

    pass


class BeamError(BeamDesignError):
    """
    Main exception for ``Beam`` object errors.
    """

    pass


class ElementError(BeamError):
    """
    Main Exception for ``Element`` object errors.
    """

    pass


class ElementLengthError(ElementError):
    """
    Error thrown if the beam length is <0, or when requesting local positions on a zero
    length element.
    """

    pass


class ElementCaseError(ElementError):
    """
    Error to throw while checking the element cases that make up a beam object.
    """

    pass


class PositionNotInElementError(ElementError):
    """
    Error to throw when trying to find the local position of a *real* position in an
    Element
    """

    pass


class PositionNotInBeamError(BeamError):
    """
    Error to throw when requesting information from a Beam element at a position that is
    not in the beam.
    """

    pass


class InvalidPositionError(BeamError):
    """
    Error to throw when requesting information from an invalid position on a ``Beam``.
    """

    pass


class MaterialError(BeamDesignError):
    """
    Main exception for ``Material`` object errors.
    """

    pass


class InvalidThicknessError(MaterialError):
    """
    Exception to throw if the thickness entered into the strength_yield or similar
    methods is invalid.
    """

    pass


class CodeCheckError(BeamDesignError):
    """
    Default error to throw in the codecheck classes.
    """

    pass


class InvalidMaterialError(CodeCheckError):
    """
    Error to throw if there is an incorrect material used in a CodeCheck object.
    """

    pass


class SectionOnlyError(CodeCheckError):
    """
    Error to throw if a CodeCheck method tries to use the beam properties when there is
    only a section.
    """

    pass
