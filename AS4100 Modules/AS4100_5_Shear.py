# -*- coding: utf-8 -*-

"""
This module calculates the capacity of a member in shear to AS4100 Section 5.

This section only calculates properties that are independent of loads -
properties dependent on other loads (i.e. moment & shear capacities in S5.12)
will be calculated in a dedicated combined actions module.

Units are assumed to be based on SI units:

Length: m,
time: s
Mass: kg
Force: N.

Important derived units:
Moment: Nm
Stress: Pa

Note that this contradicts current Australian Practice which uses kN, MPa etc.
However conversion is simple in most cases because the formulas are written
in consistent systems of units.
"""

import math
from typing import List, Union, Dict, Any

from HollowCircleClass import HollowCircleClass

# shear capacity methods

# region

def s5_11_4_V_w_Generic(A_w: float, f_y: float,
                        shear_to_axial: float = 0.6) -> float:
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

    #shear yield stress
    f_y_v = shear_to_axial * f_y

    return f_y_v * A_w

def s5_11_4_V_w_CHS(A_e: float, f_y: float,
                    shear_to_axial: float = 0.6, CHS_shear_area: float = 0.6)\
        -> float:
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

    #Shear yield stress
    f_y_v = shear_to_axial * f_y

    return CHS_shear_area * f_y_v * A_e

def s5_11_4_V_w_multiple(A: Union(float, List[float]),
                         f_y: Union(float, List[float]),
                         d: Union(float, List[float]),
                         t: Union(float, List[float]),
                         is_CHS: Union(bool, List[bool]),
                         shear_to_axial: float = 0.6,
                         CHS_shear_area: float = 0.6):
    """
    This method calculates the shear yield capacity of multiple shear elements
    based on AS4100 S5.11.4.

    This method only calculates the yield strength in uniform shear. The effect
    of buckling or non-uniform shear stress needs to be calculated separately.

    This method works on either single elements, with input provided as single
    float / bool values as appropriate, or on multiple elements with inputs
    as List[float], List[bool] as appropriate. If multiple elements are
    considered, the length of the lists must be the same.

    :param A: The shear area of the section in m², either A_w or A_e,
        depending on whether the section is a generic section or a CHS.

        A_w: the gross sectional area of the component carrying shear.
        For hot rolled I & C sections it is acceptable to use the full
        depth of the section. For welded sections it is necessary to use
        only the web panel depth due to the discontinuity at the flange
        welds.

        A_e: the effective area of the section, allowing for holes in the
        section as per AS4100 S5.11.4. Normally the gross area of the
        section will be acceptable as holes are not often made into
        standard sized circular members.

        This parameter is a single float or a List of floats
        [1.0, 2.0, 3.0, ..., n] to enable multiple elements to be entered,
        i.e. for the 2x webs in a box girder.

        This is entered separately from the panel depths & thicknesses to
        allow overriding the area (if say holes are present in the web)
        without overriding the buckling calculations.

        To calculate the area directly from the entered values, use -1.0
        for an elements area in A and the area will be directly calculated
        from the provided depth/diameter & thickness.
    :param f_y: The axial stress yield strength of the web section in Pa.
    :param d: This is the depth of the web panel in shear, or the diameter of
        the CHS element that in shear. Units in m.

        This parameter should either be a single float or a List[float].
    :param t: This is the thickness of the web panel in shear, or the thickness
        of the CHS element in shear. Units in m.

        This parameter should either be a single float or a List[float].
    :param is_CHS: Is the element a CHS?

        This parameter should either be a single bool or a List[bool]
    :param shear_to_axial: The ratio of shear yield to ordinary axial yield
        stress. By default this is 0.6 as per AS4100, which appears to be an
        approximation of the the value 1 / √3 ≈ 0.577 ≈ 0.6.
    :param CHS_shear_area: The proportion of the CHS active in shear. AS4100
        implicitly gives this value as 0.6, based on the fact that the shear
        capacity of a CHS is 0.36 x fy x A - the 0.36 includes the reduction of
        axial yield stress to shear yield stress of 0.6, leaving a factor of 0.6
        for the effective shear area of a CHS.
    :return: The shear yield strength of the section in N.
        This is returned in a dictionary with the following structure:

            {
                'V_y': shear yield strength (N)
                'Intermediate':
                    {
                        'f_y_min': minimum yield stress (Pa)
                    }
            }

        To allow for future use in a calculation report.
    """

    #first check that A, f_y, d, t & is_CHS are lists, or make them into lists:
    if type(A) == float:
        A = [A]
    if type(f_y) == float:
        f_y = [f_y]
    if type(d) == float:
        d = [d]
    if type(t) == float:
        t = [t]
    if type(is_CHS) == bool:
        is_CHS = [is_CHS]

    #next, check they are the same lengths:
    list_lens = [len(A), len(f_y), len(d), len(t), len(is_CHS)]

    if min(list_lens) != max(list_lens):
        #if the minimum & maximmum values are not the same, the list lengths are
        #different.

        raise ValueError("Expected that A, f_y, d, t & is_CHS are all the same"
                         + "length. Lengths are: A: " + str(len(A)) + ", f_y: "
                         + str(len(f_y)) + ", d:" + str(len(d)) + ", t:"
                         + str(len(t)) + ", is_CHS: " + str(len(is_CHS)))

    #determine the minimum shear yield strength
    f_y_min = min(f_y)

    #next calculate the yield strength

    #set the shear capacity to 0 by default.
    V_y = 0.0

    for Ai, di, ti, CHSi in zip(A, d, t, is_CHS):
        # Here we iterate through the lists of areas and calculate the yield
        # capacity of the section.

        if Ai >= 0.0:
            #if Ai is >= 0.0, then A_current is simply Ai

            A_current = Ai
        elif Ai == -1.0:
            #if Ai is == -1.0, then A has to be calculated

            if not CHSi:
                #if not a CHS, then the section is a simply rectangle.
                A_current = di * ti

            else:
                CHS = HollowCircleClass(0.0, 0.0, di / 2, (di - 2 * ti) / 2)
                A_current = CHS.area

        else:
            #if Ai is not >= 0.0 OR == -1.0, then Ai is an invalid number.
            raise ValueError("Expected area input A to be either >= 0.0 or "
                             + "== -1.0, current value is: " + str(Ai))

        #next need to calculate the shear capacity

        if not CHSi:
            #if not a CHS, use the generic shear capacity method

            V_current = s5_11_4_V_w_Generic(Ai, f_y_min, shear_to_yield)

        else:
            #else, need to use the CHS method

            V_current = s5_11_4_V_w_CHS(Ai, f_y_min, shear_to_yield)

        #finally, the shear capacity of the multiple sections is simply
        #the sum of the yield capacities

        V_y += V_current

    # create results dictionary with intermediate results
    results = {'V_y': V_y, 'Intermediate': {'f_y_min': f_y_min}}

    # NOTE: this yield capacity could be limited by welds or buckling.
    # these effects need to be calculated separately.

    return results


def s5_11_4_V_w_Interface(t1: Union(List[float], float),
                          t2: Union(List[float], float), f_y_min: float,
                          Q: float, I: float, shear_to_axial: float = 0.6)\
                          -> Dict:
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
        results = {'Intermediate': {'min_t': 0}}
    else:
        t = t2
        results = {'Intermediate': {'min_t': 1}}

    f_y_v = f_y_min * shear_to_axial  # shear yield stress

    V_w = f_y_v * t * I / Q  # shear capacity of interface

    #Add the shear capacity into the results.
    results.update({'V_i': V_w})

    return results

def s5_11_4_V_w_InterfaceMultiple(t1: Union(List[float], List[List[float]]),
                                 t2: Union(List[float], List[List[float]]),
                                 Q: List[float], f_y: Union(List[float], float),
                                 I: float, shear_to_axial: float = 0.6):
    """
    Calculates the capacity of a section in shear based on local shear
    yielding of an interface such as the connection between a flange and a web.

    This method handles multiple interfaces.

    :param t1: The thicknesses on one side of the interface being considered,
        in m. This can be one of the following inputs:

        List[float]: Where each interface consists of only 1x plate element, the
            interface thicknesses can be entered as a list of floats.
        List[List[float]]: Where each interface consists of multiple plate
            elements, the interface thickness can be entered as a list of a list
            of floats. E.g.:

            [
                [thicknesses of interface 1],
                [thicknesses of interface 2]
            ]

        The number of items at the top level of the list should be the same as
        the number of items in t2 and Q.
    :param t2: The thicknesses on the other side of the interface being
        considered, in m. This can be one of the following inputs:

        List[float]: Where each interface consists of only 1x plate element, the
            interface thicknesses can be entered as a list of floats.
        List[List[float]]: Where each interface consists of multiple plate
            elements, the interface thickness can be entered as a list of a list
            of floats. E.g.:

            [
                [thicknesses of interface 1],
                [thicknesses of interface 2]
            ]

        The number of items at the top level of the list should be the same as
        the number of items in t1 and Q.
    :param Q: The first moment of area of the connected component relative
        to the centroid of the section as a whole, in m³. This should be a
        List[float] with the Q value for each interface being considered.

        The number of items in the list should be the same as the number of
        items in t1 and t2.
    :param f_y: The axial yield stress of the plate elements at the interfaces,
        in Pa. If there are multiple yield strengths involved this can be
        entered as a List[float]. This should have the same number of items as
        the number of plates in the interfaces being considered, but does not
        have to match t1, t2 or Q in length.
    :param I: The moment of area / inertia of the section as a whole, in m⁴.
    :param shear_to_axial: The ratio of shear yield stress to ordinary axial
        yield stress. By default this is 0.6 as per AS4100, which appears to be
        an approximation of the the value 1 / √3 ≈ 0.577 ≈ 0.6.
    :return: Returns the minimum interface shear capacity in N. Returns a
        dictionary with the critical interfaces listed for future use.

        {
            'V_i': Minimum interface shear capacity (N),
            'Intermediate': {
                    'Critical Interface': a List[int] with the index of the
                        critical interfaces (0 based). These correspond to the
                        items in t1, t2 & Q which give the critical interfaces.
                }
        }
    """

    #first check that t1, t2 and Q are the same length

    list_lens = [len(t1), len(t2), len(Q)]

    if max(list_lens) != min(list_lens):
        raise ValueError("Error checking interface shear capacity. Where there"
                         + " are multiple interfaces being considered the no."
                         + " of interfaces should be the same in list t1, t2"
                         + " and Q. List lengths provided are t1: "
                         + str(list_lens[0]) + ", t2: " + str(list_lens[1])
                         + " and Q: " + str(list_lens[2]) + ".")

    f_y_min = min(f_y)

    #next go through the interfaces and determine the capacity for each one.
    V_i = 0.0 #default value
    critical_interface = None #place holder for the critical_interface variable

    for t1i, t2i, Qi, i in zip(t1, t2, Q, range(0, len(Q))):
        V_i_current = s5_11_4_V_w_Interface(t1i, t2i, f_y_min, Qi, I,
                                            shear_to_axial)

        if i == 0:
            #if the first interface, by default V_i is the result.
            V_i = V_i_current
            critical_interface = [i]
        else:
            if V_i_current < V_i:
                #if V_i_current is < V_i, replace V_i and the critical interface
                #list.
                V_i = V_i_current
                critical_interface = [i]

            elif V_i_current == V_i:
                #If V_i_current == V_i, add the interface to the
                #critical_interface list.
                critical_interface.append(i)

    #now that V_i is calculated, generate return dictionary.

    results = {'V_i': V_i,
               'Intermediate':
                    {'Critical Interface': critical_interface
                        }
        }

    return results


def s5_11_4_V_w_Weld(v_w: Union(List[float], float), Q: float, I: float)\
                            -> float:
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

    #first convert v_w to a list if required so that it can be summed

    if type(v_w) == float:
        v_w = [v_w]

    v_w = sum(v_w)  # get the sum of the capacity of the welds

    return v_w * I / Q

def s5_11_4_V_w_WeldMultiple(v_w: Union(List[float], List[List[float]]),
                             Q: List[float], I: float):
    """
    Calculates the capacity of section in shear according to AS4100 S5.11.4
    where the capacity is limited by a weld, as is the case with some welded
    I sections to AS3679.2.

    This method checks multiple welded interfaces and calculates the minimum
    shear capacity.

    This is only intended to apply to regular sections (fabricated channel,
    I and box sections) where the webs share the shear stress equally. For
    irregular sections where the webs may share the shear stress in an un-equal
    manner this equation will not apply and further analysis will be required.

    NOTE: where welds are critical, the value of φ used with the results from
    this function should be the value of φ for the welds in question. Typically
    this is not the same as the value of φ for structural steel.

    :param v_w: The weld capacity connecting the element being considered
        (in N/m). This should be either a List[float] where each item is the
        total weld capacity at an interface, or a List[List[float]] of the
        following format:

            [
                [weld capacities at interface 1],
                [weld capacities at interface 2],
                [weld capacities at interface ...],
                ...]
            ]

    :param Q: The first moment of area of the connected component relative to
        the centroid of the section as a whole, in m³. This should be a list of
        the Q values that act at each interface.

        Len(Q) must equal Len(v_w).
    :param I: The moment of area / inertia of the section as a whole, in m⁴.
    :return: Returns the shear capacity as limited by welds in N. Returns a
        dictionary with some intermediate results:

        {
            'V_w': Minimum interface shear capacity (N),
            'Intermediate':
            {
                'Critical Welds': A list of the critical welds, corresponding to
                    the index of the interfaces in v_w and Q.
            }
        }
    """

    #first check that the length of v_w and Q are the same.

    if len(v_w) != len(Q):
        raise ValueError('Expected a list of matching weld capacities v_w and '
                         + 'first moments of area Q for each weld interface. '
                         + 'No. of interface in each list is not the same. '
                         + 'No. v_w: ' + str(len(v_w)) + ', no. Q: '
                         + str(len(Q)) + '.')

    #next go through all the interfaces
    V_w = 0.0
    critical_weld = None #place holder for critical element list

    for vwi, Qi, i in zip(v_w, Q, range(0, len(Q))):

        V_w_current = s5_11_4_V_w_Weld(vwi, Qi, I)

        if i == 0:
            #if the first element, set V_w = V_w_current
            V_w = V_w_current
            critical_weld = [i]
        else:
            #else test if less than V_w
            if V_w_current < V_w:
                #Replace V_w & critical weld list
                V_w = V_w_current
                critical_weld = [i]
            elif V_w_current == V_w:
                #if V_w_current is the same as V_w, then update the critical
                #weld list
                critical_weld.append(i)

    #now that V_w is calculated, create return dictionary

    results = {'V_w': V_w,
               'Intermediate': {
                   'Critical Welds': critical_weld
                   }
        }

    return results

def s5_11_5_α_v(d_p: float, t_w: float, f_y: float,
                slenderness_limit: float = 82.0,
                f_y_ref: float = 250e6) -> float:
    """
    Determines the shear buckling coefficient α_v, which reduces the shear
    yielding load as per AS4100 section 11.5

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

    α_v = 0.0 #place holder for α_v

    if d_p / t_w > ((slenderness_limit) / ((f_y / f_y_ref ) **0.5)):
        α_v = ((slenderness_limit) / ((d_p / t_w ) *((f_y / f_y_ref ) **0.5)) ) **2

    return α_v

def s5_11_5_α_vMultiple(d_p: Union(List[float], float),
                        t_w: Union(List[float], float),
                        f_y: Union(List[float], float),
                        is_CHS: Union(List[bool], bool),
                        slenderness_limit: Union(List[float], float),
                        f_y_ref: float = 250e6):
    """

    The minimum buckling coefficient from the collection of elements is
    returned, with the assumption being that buckling failure of one element
    will cause load to shed to other elements resulting in a progressive
    buckling failure of the section as a whole. This may not be accurate for
    a section with a very thin element that buckles first, where the remaining
    elements may have adequate capacity on their own.

    e.g. if a 500WC440 had a 2mm plate welded across each of its flanges (making
    a 3x web box section), it is clearly plausible that buckling failure of the
    2mm closing plates could occur very early (say an α_v << 0), but the central
    40mm web will have α_v >> 0. The total effect on strength of failure of the
    outer webs will be <10%, but the reported value of α_v will be much greater.

    If the lists of elements include CHS members the highest value of α_v that
    will be returned is 1.0. It is assumed that CHS cannot buckle in shear.
    This is probably not correct but AS4100 provides no guidance on shear
    buckling of CHS sections, so a value higher than yield (i.e. α_v > 1.0) will
    not be returned.

    This could be unconservative for thin CHS members,
    however it is expected that CHS members are generally very robust against
    shear buckling, especially normal sized members.

    :param d_p: The web panel depth in m.
    :param t_w: The web thickness in m.
    :param f_y: The yield strength in Pa.
    :param is_CHS: Is the section a CHS? if true, the highest value of α_v that
        will be returned is 1.0.
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

    #first check the number of items in d_p, t_w, y_y and slenderness_limit are
    #the same.

    list_lens = [len(d_p), len(t_w), len(f_y), len(is_CHS),
                 len(slenderness_limit)]

    if max(list_lens) != min(list_lens):
        raise ValueError("Error calculating the buckling load parameter α_v"
                         + ", expected that the input lists d_p, t_w, f_y,"
                         + "is_CHS and slenderness_limit would be the same"
                         + " length. Lengths are: d_p: " + str(list_lens[0])
                         + ', t_w: ' +  str(list_lens[1]) + ', f_y: '
                         + str(list_lens[2]) + ", is_CHS: " + str(list_lens[3])
                         + ' and slenderness_limit: ' + str(list_lens[4]) + '.')

    α_v = 0.0 #place holder
    critical_element = None #place holder

    for d_pi, t_wi, f_yi, is_CHSi, slenderness_limit_i, i in zip(d_p, t_w, f_y, is_CHS, slenderness_limit, range(d_p)):

        # go through all the ranges to determine the values of α_v

        if not is_CHS:
            #if not a CHS, get α_v
            α_v_current = s5_11_5_α_v(d_pi, t_wi, f_yi, slenderness_limit_i)
        else:
            #if a CHS, α_v = 1.0 is the assumption.
            α_v_current = 1.0

        #next check if α_v_current is the minimum:

        if i == 0:
            #if the first element in the list, α_v is simply α_v_current
            α_v = α_v_current
            critical_element = [i]
        else:
            if α_v_current < α_v:
                #if α_v_current is < α_v, replace α_v and the critical
                #element list
                α_v = α_v_current
                critical_element = [i]
            elif α_v_current == α_v:
                #If α_v == α_v_current, add current element to the critical
                #element list
                critical_element.append(i)

    results = {
        'α_v': α_v,
        'Intermdiate': {
            'Critical Element (α_v)': critical_element
            }
        }

    return results

def s5_11_3_Non_uniform_shear_factor(f_vm: float, f_va: float) -> float:
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


def s5_11_2_V_p(A: Union(List[float], float), f_y: Union(List[float], float),
                is_CHS: Union(List[bool], bool), d: Union(List[float], float),
                t: Union(List[float], float), slenderness_limit: Union(List[float], float),
                shear_to_axial: float = 0.6, is_uniform: bool = True, f_vm: float = 1.0, f_va: float = 1.0,) -> \
                Dict[str, Dict[str, Union[float, Any]]]:
    """
    Determines the shear capacity of a section based on AS4100 S5.11.2-5.
    This is the shear capacity based on the web panel capacity only.
    Web stiffeners (S5.11.5.2) are NOT included in this calculation.

    Other methods are required to adjust this capacity based on weld capacity
    or shear interface capacity (i.e. web-flange joints).

    This method handles sections composed of multiple elements by allowing
    data to be entered as lists of elements.

    Yield strength is taken to be the minimum strength of any element in the
    section considered.

    The buckling factor α_v is based on the worst case buckling factor of
    any element in the section. The assumption is that buckling of one
    element will result in a progressive failure as other elements take up
    the shear and buckle in turn. This could be very conservative if there is
    an element in the section which is very slender compared to the other
    elements.

    :return:
    """

    #determine the minimum shear yield strength
    f_y_min = min(f_y)

    #next calculate the yield strength

    #set the shear capacity to 0 by default.
    V_y = 0.0

    for Ai, di, ti, CHSi in zip(A, d, t, is_CHS):
        # Here we iterate through the lists of areas and calculate the yield
        # capacity of the section.

        if Ai >= 0.0:
            #if Ai is >= 0.0, then A_current is simply Ai

            A_current = Ai
        elif Ai == -1.0:
            #if Ai is == -1.0, then A has to be calculated

            if not CHSi:
                #if not a CHS, then the section is a simply rectangle.
                A_current = di * ti

            else:
                CHS = HollowCircleClass(0.0, 0.0, di / 2, (di - 2 * ti) / 2)
                A_current = CHS.area

        else:
            #if Ai is not >= 0.0 OR == -1.0, then Ai is an invalid number.
            raise ValueError("Expected area input A to be either >= 0.0 or "
                             + "== -1.0, current value is: " + str(Ai))

        #next need to calculate the shear capacity

        if not CHSi:
            #if not a CHS, use the generic shear capacity method

            V_current = s5_11_4_V_w_Generic(Ai, f_y_min, shear_to_yield)

        else:
            #else, need to use the CHS method

            V_current = s5_11_4_V_w_CHS(Ai, f_y_min, shear_to_yield)

        #finally, the shear capacity of the multiple sections is simply
        #the sum of the yield capacities

        V_y += V_current

    # create results dictionary with intermediate results
    results = {'Intermediate': {'V_y': V_y, 'f_y_min': f_y_min}}

    # NOTE: this yield capacity could be limited by welds or buckling.
    # these effects are calculated below.

    #check buckling capacity

    α_v = 1.0  # by default
    crit_element = []  # a list to store the critical element in.

    # next need to calculate the buckling capacity of every element.

    for i in range(len(d)):
        # go through all elements.
        if not is_CHS[i]:
            # Assumed that CHS cannot buckle in shear. This is probably
            # not correct but AS4100 provides no guidance on shear buckling
            # of CHS sections. It is expected that CHS members are generally
            # very robust against shear buckling, especially normal sized
            # members.

            # If not a CHS then check for buckling and return the minimum
            # of the current buckling parameter and the calculated one for
            # the item in question. The assumption is that when buckling of
            # the first panel occurs all remaining panels buckle in a
            # progressive collapse mechanism. This may be too conservative
            # in sections with very thin elements.

            α_v_current = s5_11_5_α_v(d[i], t[i], f_y[i],
                                      slenderness_limit[i], f_y_ref)

            # get smallest α_v and also generate a list of critical elements

            if α_v_current < α_v:
                crit_element = [i]
                α_v = α_v_current  # need to update α_v
            elif α_v_current == α_v:
                crit_element.append(i)
                # in this case there is no need to update α_v

    # add the buckling parameter to intermediate results
    results['Intermediate'].update({'α_v': α_v})

    # next add the critical elements list into the return dictionary
    if all(is_CHS):
        results['Intermediate'].update({'Critical Elements': 'All CHS'})
    else:
        results['Intermediate'].update({'Critical Elements': crit_element})

    #determine the non-uniform shear factor

    uniform_shear_factor = 1.0  # by default

    if not is_uniform:
        uniform_shear_factor = s5_11_3_Non_uniform_shear_factor(f_vm, f_va)

    # update results
    results['Intermediate'].update({'Uniform Shear Factor': uniform_shear_factor})

    V_p = α_v * V_y * uniform_shear_factor

    results.update({"V_p": V_p})

    return results

def s5_11_2_V_v(A: Union(List[float], float), f_y: Union(List[float], float),
                is_CHS: Union(List[bool], bool), d: Union(List[float], float),
                t: Union(List[float], float),
                slenderness_limit: Union(List[float], float),
                Q: Union(List[float] ,float),
                v_w: Union(List[Union(float, List[float])], float),
                t_i1: Union(Union(List[float], float), float),
                t_i2: Union(Union(List[float], float), float),
                f_y_ref = 250e6,
                I: float = 0.0, is_uniform: bool = True,
                f_vm: float = 1.0, f_va: float = 1.0,
                is_welded: bool = False,
                check_interface: bool = False, φ_steel: float = 0.9,
                φ_weld: float = 0.8) -> Dict[str, Any]:
    """
    Determines the shear capacity of a member according to AS4100 S5.11.2.
    Considers all clauses of S5.11 except 5.11.5.2 - it is assumed that
    webs are unstiffened.

    Yield strength is taken to be the minimum strength of any element in the
    section considered.

    The buckling factor α_v is based on the worst case buckling factor of
    any element in the section. The assumption is that buckling of one
    element will result in a progressive failure as other elements take up
    the shear and buckle in turn. This could be very conservative if there is
    an element in the section which is very slender compared to the other
    elements.

    This method can also determine if the shear capacity is limited by weld
    capacity, as is the case in some WC sections, and potentially the case
    in custom fabricated girders. It also checks if capacity is limited by
    shear across an interface, which could occur where (for example) a very
    thin web element meets a thick flange.

    :param A: the shear area of the section in m², either A_w or A_e,
        depending on whether the section is a generic section or a CHS.

        A_w: the gross sectional area of the component carrying shear.
        For hot rolled I & C sections it is acceptable to use the full
        depth of the section. For welded sections it is necessary to use
        only the web panel depth due to the discontinuity at the flange
        welds.

        A_e: the effective area of the section, allowing for holes in the
        section as per AS4100 S5.11.4. Normally the gross area of the
        section will be acceptable as holes are not often made into
        standard sized circular members.

        This parameter is a single float or a List of floats
        [1.0, 2.0, 3.0, ..., n] to enable multiple elements to be entered,
        i.e. for the 2x webs in a box girder.

        This is entered separately from the panel depths & thicknesses to
        allow overriding the area (if say holes are present in the web)
        without overriding the buckling calculations.

        To calculate the area directly from the entered values, use -1.0
        for an elements area in A and the area will be directly calculated
        from the provided depth/diameter & thickness.
    :param f_y: The yield strength of the component in shear. This parameter
        is either a single float or a list of floats matching A in length.

        Only the minimum yield strength is used to determine the yield
        strength of the section.

        FEA models determining the capacity of
        sections with different yield strengths in their components typically
        show that there is very little additional capacity to be gained, as
        load shedding in the post yield plateau and buckling are much more
        important factors in realistic structures. f_y IS considered on an
        element by element basis to determine the buckling factor of each
        element though as this is a pre-yield phenomenon.
    :param is_CHS: Is the section a CHS? This should be a single bool, or
        a list of bools matching A in length.
    :param d: The web panel depth or CHS outside diameter, in m. This should
        be a single float or a list of floats, matching A in length.
    :param t: The web or CHS thickness in m. This should be a single float
        or a list of floats, matching A & d in length.
    :param slenderness_limit: The slenderness limit. Typically this would be
        82.0, but this is only valid for a web pin supported top and bottom.
        In some circumstances this value may be very unconservative (i.e.
        shear buckling of an angle leg supported on one side only) Refer to
        "The Behaviour and Design of Steel Structures to AS4100" by Trahair
        et al. for more information.
        This should be a float or a list of floats, matching the no. of
        elements in A, d & t.
    :param Q: The moment of area of the element connected to the rest of the
        structure (i.e. a flange, or a web element), in m³. A list can be
        provided to allow consideration of multiple elements that make up a
        section.
    :param v_w: The weld capacity in N/m. Default is 0.0.
        A list of weld capacities can be provided. Each item in the list
        should correspond to the weld capacity of the welds that connect
        an element of a given Q value below to the rest of the element. For
        each weld group, either a float should be provided (if there is 1x
        weld) or a list of floats. I.e. either: 1.0 or [1.0, 2.0, 3.0] or
        [1.0, [1.0, 1.0], 3.0] or [[1.0], [1.0, 2.0], [3.0]] are valid.
    :param t_i1: The interface thickness on one side of the interfaces in m,
        corresponding with the welded connections. This should either be a
        float (i.e. in a T section with a single welded connection), a list
        of floats (i.e. an I girder with 2x welded connections this list might
        be [t_web_top, t_web_btm]) or a list of a list of floats where each
        list contains the multiple thicknesses meeting at an interface (i.e.
        in a box girder, which might have 2x webs [[t_web_1_btm, t_web_2_btm],
        [t_web_1_top, t_web_2_top]].
    :param t_i2: The interface thickness on the other side of the interfaces
        in m, corresponding with the welded connections.

        If t_i1 were the web thicknesses, t_i2 would be the thickness of the
        flange that they are connected to for example.

        This should either be a float (i.e. in a T section with a single
        welded connection), a list of floats (i.e. an I girder with 2x welded
        connections this list might be [t_web_top, t_web_btm]) or a list of a
        list of floats where each list contains the multiple thicknesses
        meeting at an interface (i.e. in a box girder, which might have 2x webs
        [[t_web_1_btm, t_web_2_btm], [t_web_1_top, t_web_2_top]].
    :param f_y_ref: The reference yield stress used in the slenderness limit
        equations. By default this is 250e6 Pa in line with AS4100.
    :param I: The section moment of inertia in m⁴ about the axis perpendicular
        to the axis in which the shear is being applied. Default is 0.0.
    :param is_uniform: Is the shear on the section uniform? Default is True.
    :param f_vm: The maximum shear stress in the section from an elastic
        analysis, in Pa.
    :param f_va: The average shear stress in the section from an elastic
        analysis, in Pa.
    :param is_welded: Will welds affect the shear capacity? Default is False.
    :param check_interface: Does interface shear need to be checked?
    :param φ_steel: The capacity reduction factor for steel in shear as per
        AS4100.
    :param φ_weld: The capacity reduction factor for the welds at shear
        interfaces as per AS4100. Note that if the capacity is already given
        as an ultimate capacity (i.e. from AS3679) this value should be 1.0,
        (smaller values will be overly conservative).
    :return: Returns the shear capacity of the section in N.
    """

    # Input check region
    # region

    # region

    # check if A, f_y, is_CHS, d, t and slenderness_limit are lists.
    # if not, convert to lists.
    if type(A) != list:
        A = [A]
    if type(f_y) != list:
        f_y = [f_y]
    if type(is_CHS) != list:
        is_CHS = [is_CHS]
    if type(d) != list:
        d = [d]
    if type(t) != list:
        t = [t]
    if type(slenderness_limit) != list:
        slenderness_limit = [slenderness_limit]

    # build a list of the List lengths to check that min & max are OK.
    list_lens = [len(A), len(f_y), len(is_CHS), len(d), len(t),
                 len(slenderness_limit)]

    if min(list_lens) != max(list_lens):
        # if the minimum list length <> maximum list length there is an error
        raise IndexError("Expected lists A, f_y, is_CHS, d, t & "+
                         "slenderness_limit to be of the same size.")
    if list_lens[0] <= 0:
        # if the list length is <0 there are no items to check
        raise ValueError("Expected a list of shear elements to check. Input" +
                         "does not contain any shear elements. " +
                         "Check parameters A, f_y, is_CHS, d, t & " +
                         "slenderness_limit.")

    # endregion

    # region

    # need to do the same checks for the v_w, t_1, t_2 and Q lists.
    # convert values to lists if not a list.
    if type[v_w] != list:
        v_w = [v_w]
    if type [Q] != list:
        Q = [Q]
    if type [t_i1] != list:
        t_i1 = [t_i1]
    if type [t_i2] != list:
        t_i2 = [t_i2]

    # build a list of lengths to check min & max lengths

    list_lens = [len(v_w), len(Q), len(t_i1), len(t_i2)]

    if min(list_lens) != max(list_lens):
        # if the minimum list length <> maximum list length there is an error
        raise IndexError("Expected lists v_w, Q, t_i1 & t_i2 to be of the same"
                         +"size")
    if list_lens[0] <= 0:
        # if the list length is <0 there are no items to check
        raise ValueError("Expected a list of shear weld elements to check. " +
                         "Input does not contain any shear weld elements. " +
                         'Check parameters v_w, Q, t_i1, t_i2.')

    # endregion

    # endregion

    # determine the minimum shear yield strength.
    f_y_min = min(f_y)

    # calculate the yield strength

    # region

    # set the shear capacity to 0 by default
    V_y = 0.0
    A_current = 0.0
    V_current = 0.0

    for i in range(len(A)):
        # here we iterate through the list of areas & calculate the yield
        # capacity of the section.
        if A[i] != -1.0:
            # if area <> -1.0, then area is simply A.
            A_current = A[i]
        else:
            # need to calculate the area
            if not is_CHS:
                # assume if not a CHS that it is a simple rectangle
                A_current = d[i] * t[i]
            else:
                # If CHS, need to calculate the area of a hollow circle
                CHS = HollowCircleClass(0.0, 0.0, d[i] / 2, (d[i] - 2 * t) / 2)
                A_current = CHS.area()

        # next calculate the shear capacity

        if not is_CHS:
            # if not a CHS use the generic shear capacity method
            V_current = s5_11_4_V_w_Generic(A_current, f_y_min)
        else:
            # if a CHS, use the CHS method.
            V_current = s5_11_4_V_w_CHS(A_current, f_y_min)

        # the total shear strength in yield is the sum of all element types:
        V_y = V_y + V_current

    # create results dictionary with intermediate results
    results = {'Intermediate': {'V_y': V_y, 'f_y_min': f_y_min}}

    # NOTE: this yield capacity could be limited by welds or buckling.
    # these effects are calculated below.

    # endregion

    # check buckling capacity.

    # region

    α_v = 1.0 # by default
    crit_element = [] #a list to store the critical element in.

    # next need to calculate the buckling capacity of every element.

    for i in range(len(d)):
        # go through all elements.
        if not is_CHS[i]:
            # Assumed that CHS cannot buckle in shear. This is probably
            # not correct but AS4100 provides no guidance on shear buckling
            # of CHS sections. It is expected that CHS members are generally
            # very robust against shear buckling, especially normal sized
            # members.

            # If not a CHS then check for buckling and return the minimum
            # of the current buckling parameter and the calculated one for
            # the item in question. The assumption is that when buckling of
            # the first panel occurs all remaining panels buckle in a
            # progressive collapse mechanism. This may be too conservative
            # in sections with very thin elements.

            α_v_current = s5_11_5_α_v(d[i], t[i], f_y[i],
                                      slenderness_limit[i], f_y_ref)

            #get smallest α_v and also generate a list of critical elements

            if α_v_current < α_v:
                crit_element = [i]
                α_v = α_v_current #need to update α_v
            elif α_v_current == α_v:
                crit_element.append(i)
                #in this case there is no need to update α_v

    #add the buckling parameter to intermediate results
    results['Intermediate'].update({'α_v': α_v})

    #next add the critical elements list into the return dictionary
    if all(is_CHS):
        results['Intermediate'].update({'Critical Elements': 'All CHS'})
    else:
        results['Intermediate'].update({'Critical Elements': crit_element})

    # endregion

    # non-uniform shear check

    # region

    uniform_shear_factor = 1.0 # by default

    if not is_uniform:
        uniform_shear_factor = s5_11_3_Non_uniform_shear_factor(f_vm, f_va)

    #update results
    results['Intermediate'].update({'Uniform Shear Factor': uniform_shear_factor})

    # endregion

    # using the uniform shear factor and the buckling factor a panel capacity
    # is determined. This is the sum of all the individual panel capacities
    # as reduced by the buckling and non-uniform shear factors.
    V_p = α_v * V_y * uniform_shear_factor
    φV_p = φ_steel * V_p

    #update results dictionary
    results['Intermediate'].update({'V_panel': V_p, 'φV_panel': φV_p})

    # check weld capacity.

    # region

    V_w = 0.0  # default value set to 0.0
    crit_weld = []

    if is_welded:
        # first check if welded, otherwise there is no point reducing capacity.
        # otherwise check capacity with welds.

        for i in range(len(Q)):

            V_w_current = s5_11_4_V_w_WeldLimited(v_w[i], Q[i], I)

            # for each value, check if the current weld capacity is less
            # than the minimum already calculated, also add to the critical
            #element list.

            if i == 0:
                # initialise the value of V_w to a non 0.0 value.
                V_w = V_w_current
                crit_weld = [i]
            else:
                if V_w_current < V_w:
                    V_w = V_w_current #update V_w
                    crit_weld = [i]
                elif V_w_current == V_w:
                    crit_weld.append(i)
                    #in this case no need to update V_w

        #finally, update the results dictionary
        results['Intermediate'].update({'Critical Weld': crit_weld})
    else:
        results['Intermediate'].update({'Critical Weld': 'Not Welded'})

    φV_w = φ_weld * V_w
    results['Intermediate'].update({'V_w': V_w, 'φV_w': φV_w})

    # note that V_w is not reduced by the buckling or non-uniform shear factors
    # as this is not a buckling mechanism and the use of Q for any individual
    # component directly accounts for the uniformity of the shear.

    # endregion

    #check interface shear capacity

    # region

    V_i = 0.0 #default value
    crit_interface = []

    if check_interface:

        for i in len(Q):
            #go through each interface

            V_i_current = s5_11_4_V_w_WeldInterfaceLimited(t_i1[i], t_i2[i],
                                                           f_y_min, Q[i], I)

            if i == 0:
                V_i = V_i_current
                crit_interface = [i]
            else
                if V_i_current < V_i:
                    V_i = V_i_current #update V_i
                    crit_interface = [i] #update the critical interface
                elif V_i_current == V_i:
                    crit_interface.append(i) #update the critical interface
                                             #but no need to update V_i

        results['Intermediate'].update({'Critical Interface': crit_interface})
    else:
        results['Intermediate'].update({'Critical Interface': "Not Checked"})


     φV_i = φ_steel * V_i
    results['Intermediate'].update({'V_i': V_i, 'φV_i': φV_i})

    # endregion

    # finally, determine V_u

    if is_welded and check_interface:
        # shear capacity is limited by weld & interface shear as well as
        # panel strength.

        φV_u = min(φV_p, φV_w, φV_i)

        if φV_p == φV_u:
            V_u = V_p
        elif φV_w == φV_u:
            V_u = V_w
        else:
            V_u = V_i

    elif is_welded:
        # shear capacity is lower of the panel capacity or the welds that
        # connect it together

        φV_u = min(φV_p, φV_w)

        if φV_p == φV_u:
            V_u = V_p
        else:
            V_u = V_w

    elif check_interface:
        # shear capacity is limited by interface shear.
        φV_u = min(φV_p, φV_i)

        if φV_p == φV_u:
            V_u = V_p
        else:
            V_u = V_i

    else:
        # if not welded or interface limited, shear capacity is just V_p
        V_u = V_p
        φV_u = φV_p

    results.update({'V_u': V_u, 'φV_u': φV_u})

    return results

    # end shear capacity methods

    # endregion