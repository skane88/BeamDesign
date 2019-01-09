# -*- coding: utf-8 -*-

"""
This module calculates the capacity of a member in shear to AS4100 Section 5.

This section only calculates properties that are independent of loads -
properties dependent on other loads (i.e. moment & shear capacities in S5.12)
will be calculated in a dedicated combined actions module.

Units are assumed to be based on SI units:

Length: m,
Time: s
Mass: kg
Force: N.

Important derived units:
Moment: Nm
Stress: Pa

Note that this contradicts current Australian Practice which uses kN, MPa etc.
However conversion is simple in most cases because the formulas are written
in consistent systems of units.
"""

from typing import List, Union, Dict


def s5_11_4_V_w_Generic(
    *, A_w: float, f_y: float, shear_to_axial: float = 0.6
) -> float:
    """
    Determines the shear yielding capacity of a flat web section to
    AS4100 S5.11.4.

    This method is assumed to be acceptable for determining the shear
    yielding capacity of any section except CHS sections. For example, S9.3
    gives an almost identical equation for the shear strength of a solid
    circular section (bolts) of 0.62 x f_u x A.

    However, allowances for non-uniform shear stress distributions should be
    made with the equation given in S5.11.3.

    :param A_w: the gross sectional area of the web in m². For hot rolled I &
        C sections it is acceptable to use the full depth of the section. For
        welded sections it is necessary to use only the web panel depth due
        to the discontinuity at the flange welds.
    :param f_y: the yield strength of the web section in Pa.
    :param shear_to_axial: the ratio of shear yield to ordinary axial yield
        stress. By default this is 0.6 as per AS4100, which appears to be an
        approximation of the the value 1 / √3 ≈ 0.577 ≈ 0.6.
    :return: The web shear yield strength in N.
    """

    f_y_v = shear_to_axial * f_y  # shear yield stress

    return f_y_v * A_w


def s5_11_4_V_w_CHS(
    *, A_e: float, f_y: float, shear_to_axial: float = 0.6, CHS_shear_area: float = 0.6
) -> float:
    """
    Determine the shear yielding capacity of a CHS section to AS4100 S5.11.4.

    :param A_e: The effective area of the section in m², allowing for holes
        in the section as per AS4100 S5.11.4. Normally the gross area of the
        section will be acceptable as holes are not often made into standard
        sized circular members.
    :param f_y: The yield strength of the CHS section in Pa.
    :param shear_to_axial: The ratio of shear yield to ordinary axial yield
        stress. By default this is 0.6 as per AS4100, which appears to be an
        approximation of the the value 1 / √3 ≈ 0.577 ≈ 0.6.
    :param CHS_shear_area: The proportion of the CHS active in shear. AS4100
        implicitly gives this value as 0.6, based on the fact that the shear
        capacity of a CHS is 0.36 x fy x A - the 0.36 includes the reduction of
        axial yield stress to shear yield stress of 0.6, leaving a factor of 0.6
        for the effective shear area of a CHS.
    :return: The shear yield strength of the section in N.
    """

    # Shear yield stress
    f_y_v = shear_to_axial * f_y

    return CHS_shear_area * f_y_v * A_e


def s5_11_5_α_v(
    *,
    d_p: float,
    t_w: float,
    f_y: float,
    slenderness_limit: float = 82.0,
    f_y_ref: float = 250e6
) -> float:
    """
    Determines the shear buckling coefficient α_v, which reduces the shear
    yielding load as per AS4100 section 5.11.5

    :param d_p: The web panel depth in m.
    :param t_w: The web thickness in m.
    :param f_y: The yield strength in Pa.
    :param slenderness_limit: The slenderness limit. By default this is 82.0,
        which is only valid for a web pin supported top and bottom.
        In some circumstances this value may be very unconservative (i.e.
        shear buckling of an angle leg supported on one side only) Refer to
        "The Behaviour and Design of Steel Structures to AS4100" by Trahair
        et al. for more information.
    :param f_y_ref: The reference yield stress in Pa, used in the slenderness
        limit equations. By default this is 250e6 Pa in line with AS4100.
    :return: Returns the shear buckling coefficient α_v. Note that this may be
        greater than 1.0 - the user of this function should ensure that the
        final shear capacity is limited to the shear yield capacity.
    """

    α_v = 0.0  # place holder for α_v

    if d_p / t_w > ((slenderness_limit) / ((f_y / f_y_ref) ** 0.5)):
        α_v = ((slenderness_limit) / ((d_p / t_w) * ((f_y / f_y_ref) ** 0.5))) ** 2

    return α_v


def s5_11_3_Non_uniform_shear_factor(*, f_vm: float, f_va: float) -> float:
    """
    Determines the non-uniform shear modification factor as per
    AS4100 S5.11.3. This applies for sections such as PFCs, Mono-symmetric
    I sections, angle sections etc.

    :param f_vm: The maximum shear stress in the section from an elastic
        analysis. In Pa.
    :param f_va: The average shear stress in the section from an elastic
        analysis. In Pa.
    :return: Returns the non-uniform shear factor used to reduce the shear
        capacity for non-uniform members.
    """

    return min(2 / (0.9 + (f_vm / f_va)), 1.0)


def s5_11_4_V_w_Weld(*, v_w: Union[List[float], float], Q: float, I: float) -> float:
    """
    Calculates the capacity of section in shear according to AS4100 S5.11.4
    where the capacity is limited by a weld, as is the case with some welded
    I sections to AS3679.2.

    This is only intended to apply to regular sections (fabricated channel,
    I and box sections) where the webs share the shear stress equally. For
    irregular sections where the webs may share the shear stress in an
    un-equal manner this equation will not apply and further analysis will be
    required.

    NOTE: where welds are critical, the value of φ used with the results from
    this function should be the value of φ for the welds in question. Typically
    this is not the same as the value of φ for structural steel.

    :param v_w: The weld capacity connecting the element being considered
        (in N/m). This can be either a float, or if more than one weld is
        used, a List[float].
        I.e. for a welded I-beam with a weld either side of the web, you could
        supply either a single float: (v_w_LHS + v_w_RHS), or a list:
        [v_w_LHS, v_w_RHS].
    :param Q: The first moment of area of the connected component relative
        to the centroid of the section as a whole, in m³.
    :param I: The moment of area / inertia of the section as a whole, in m⁴.
    :return: Returns the shear capacity as limited by welds in N.
    """

    # first convert v_w to a list if required so that it can be summed

    if type(v_w) == float:
        v_w = [v_w]

    v_w = sum(v_w)  # get the sum of the capacity of the welds

    return v_w * I / Q


def s5_11_4_V_w_Interface(
    *,
    t1: Union[List[float], float],
    t2: Union[List[float], float],
    f_y_min: float,
    Q: float,
    I: float,
    shear_to_axial: float = 0.6
) -> Dict:
    """
    Calculates the capacity of a section in shear based on local shear
    yielding of an interface such as the connection between a flange and a web.

    :param t2: A list or float of all the thicknesses of components on one side
        of the interface, with thicknesses in m.
    :param t2: A list or float of all the thicknesses of components on the other
        side of the interface, with thicknesses in m.
    :param f_y_min: The minimum yield strength of the connected parts in Pa.
        The minimum value is used because in most realistic structures there
        is little benefit gained in ultimate capacity from different yield
        strengths, as effects such as buckling tend to be more important.
    :param Q: The first moment of area of the connected component relative
        to the centroid of the section as a whole, in m³.
    :param I: The moment of area / inertia of the section as a whole, in m⁴.
    :param shear_to_axial: The ratio of shear yield stress to ordinary axial
        yield stress. By default this is 0.6 as per AS4100, which appears to be
        an approximation of the the value 1 / √3 ≈ 0.577 ≈ 0.6.
    :return: Returns the shear capacity as limited by interface shear of the
        connected components, in N.
        Results are returned as a dictionary for future use in a calculation
        report:

        {
            'V_w_interface': Strength (N),
            'Intermediate':
                {
                'min_t': 0 or 1
                }
        }

        The value of min_t is either 0 (if t1 is critical) or 1
        (if t2 is critical)
    """

    # if t1 or t2 are not lists make them into lists, so the sum function below
    # will work.
    if type(t1) == float:
        t1 = [t1]
    if type(t2) == float:
        t2 = [t2]

    t1 = sum(t1)
    t2 = sum(t2)

    if t1 < t2:
        t = t1
        results = {"Intermediate": {"min_t": 0}}
    else:
        t = t2
        results = {"Intermediate": {"min_t": 1}}

    f_y_v = f_y_min * shear_to_axial  # shear yield stress

    V_w = f_y_v * t * I / Q  # shear capacity of interface

    # Add the shear capacity into the results.
    results.update({"V_i": V_w})

    return results
