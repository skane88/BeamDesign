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


class BeamError(Exception):
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
    Error thrown if the beam length is <0.
    """

    pass


class ElementCaseError(ElementError):
    """
    Error to throw while checking the element cases that make up a beam object.
    """

    pass
