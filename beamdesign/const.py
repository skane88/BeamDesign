"""
Contains constants used throughout the program such as enumerations etc.
"""

from enum import Enum


class LoadComponents(Enum):
    VX = 1
    VY = 2
    N = 3
    MX = 4
    MY = 5
    T = 6


class MatType(Enum):
    steel = "steel"
    concrete = "concrete"
