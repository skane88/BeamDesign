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


class PositionNotInElementError(BeamError):
    """
    Error to throw when trying to find the local position of a *real* position in an Element
    """

    pass
