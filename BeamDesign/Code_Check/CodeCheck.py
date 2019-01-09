"""
This will contain an Abstract Base Class that all CodeCheck classes should inherit from.
"""

from abc import ABC, abstractmethod


class CodeCheck(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def tension_capacity(self) -> float:
        """
        Get the limiting tension capacity of the member being checked.

        :return: the limiting tension capacity of the member being checked.
        """

        pass
