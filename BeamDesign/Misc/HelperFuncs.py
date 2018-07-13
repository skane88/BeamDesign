"""This module provides various helper functions

Need to do unit tests."""

import math

def almostEqual(a, b, epsilon=1e-10):
    """An equality tester with a tolerance.
        This allows equality tests to be carried out on floating point numbers.
    Expects:
    a: a float
    b: a float
    epsilon: a float defining the allowable tolerance.
        The default value is 1e-10
    """
    
    if math.fabs(a-b)<epsilon:
        #if the absolute of a-b is less than epsilon they are equal
        #within the required tolerance
        return True
    #if not then we can return false
    return False