"""
This file contains a number of solvers used by the CodeCheck methods.
"""

from sys import float_info


def sign(num):
    """
    Check the sign of a number. Returns -1 if less than 0, otherwise returns 1.
    """

    if num < 0:
        return -1
    else:
        return 1


def bisection(
    func,
    *args,
    x_low: float = float_info.min,
    x_high: float = float_info.max,
    tol: float = 1e-10,
    max_its: int = None,
    fail_on_max_its: bool = True,
    **kwargs,
):
    """
    Implements the bi-section method of finding roots.

    Guaranteed to find a root if one exists between the guesses. If more than one root
    exists though there is no guarantee about which one will be returned.

    :param func: A function with a single input parameter ('x') to be solved for 0.
    :param x_low: The lower bounds of the range to check.
    :param x_high: The upper bounds of the range to check.
    :param tol: The solution tolerance.
    :param max_its: A maximum number of iterations to perform. If convergence is not
        achieved within tol when max_its is reached, an error is raised.

        If ``None``, the solver will continue until convergence is reached (potentially
        infinitely, although it is likely that your computer's numerical precision will
        result in convergence before an infinite number of iterations is reached)
    :param fail_on_max_its: Raise an error or simply return on maximum iterations?
    :param args: Any positional arguments for func.
    :param kwargs: Any keyword arguments for func.
    :returns: Returns a tuple: (root, no. of iterations)
    """

    if x_high == x_low:
        raise ValueError("Expected guesses to be different.")

    if max_its is not None:
        if max_its <= 1:
            raise ValueError("Maximum no. of iterations should be > 1")

    i = 0

    while abs(x_high - x_low) > tol and x_high != x_low:

        i += 1

        y_low = func(x_low, *args, **kwargs)
        y_high = func(x_high, *args, **kwargs)

        if sign(y_low) == sign(y_high):
            raise ValueError("Expected the guesses to bracket the root")

        x_mid = (x_low + x_high) / 2
        y_mid = func(x_mid, *args, **kwargs)

        if sign(y_low) == sign(y_mid):
            x_low = x_mid
        else:
            x_high = x_mid

        if max_its is not None:
            if i >= max_its:
                if fail_on_max_its:
                    raise ValueError(
                        f"Exceeded maximum number of iterations. "
                        + f"Current root approximation is {x_mid}."
                    )
                else:
                    break

    return (x_low + x_high) / 2, i


def secant(
    func,
    *args,
    x_low: float,
    x_high: float,
    tol: float = 1e-10,
    max_its: int = None,
    fallback: bool = True,
    **kwargs,
):
    """
    Implements the secant method of finding roots.

    This is typically much faster than the bisection method and does not require that
    the guesses bracket the solution.

    However, note:

    * There is no guarantee that the method will find a root. If a guarantee is
        required, use the bisection method.
    * There is no guarantee that the method will find a root within the range
        x_low -> x_high - it may find roots outside the original range. To minimise
        the risk of finding roots outside the range x_low -> x_high, choose x_low and
        x_high to bracket the root as closely as possible. Alternatively, use the
        bisection method which cannot find roots outside the given bracket.

    :param func: A function with a single input parameter ('x') to be solved for 0.
    :param x_low: The first initial guess.
    :param x_high: The second initial guess.
    :param tol: The solution tolerance.
    :param max_its: A maximum number of iterations to perform. If convergence is not
        achieved within tol when max_its is reached, an error is raised.

        If ``None``, the solver will continue until convergence is reached (potentially
        infinitely, although it is likely that your computer's numerical precision will
        result in convergence before an infinite number of iterations is reached)
    :param fallback: If a root is not found within max_its, can the function fallback
        to the bisection method? If True, the bisection method will be called with
        the bracket of x_low, x_high, and no maximum no. of iterations.
        If x_low and x_high do not bracket the root then the bisection method will
        fail.
    :param args: Any positional arguments for func.
    :param kwargs: Any keyword arguments for func.
    :returns: Returns a tuple: (root, no. of iterations, bisection_used).
        bisection_used is True if the method falls back to the bisection method.
    """

    i = 0
    x_1 = x_low
    x_2 = x_high

    while abs(x_2 - x_1) > tol and x_1 != x_2:

        i += 1

        x_3 = (x_1 * func(x_2, *args, **kwargs) - x_2 * func(x_1, *args, **kwargs)) / (
            func(x_2, *args, **kwargs) - func(x_1, *args, **kwargs)
        )

        x_1 = x_2
        x_2 = x_3

        if max_its is not None:
            if i >= max_its:

                if fallback:
                    x, i = bisection(
                        func=func, x_low=x_low, x_high=x_high, tol=tol, *args, **kwargs
                    )
                    return x, i, True

                raise ValueError(
                    f"Exceeded maximum number of iterations. "
                    + f"Current root approximation is {x_3}."
                )

    return x_3, i, False
