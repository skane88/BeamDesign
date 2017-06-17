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
                        shear_to_yield: float = 0.6) -> float:
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
    :param shear_to_yield: the ratio of shear yield to ordinary yield stress.
        By default this is 0.6 as per AS4100, which appears to be an
        approximation of the the value 1 / √3 ≈ 0.577 ≈ 0.6.
    :return: The web shear yield strength in N.
    """

    return shear_to_yield * f_y, A_w

def s5_11_4_V_w_WeldInterfaceLimited(t1: Union(List[float], float),
                                     t2: Union(List[float], float),
                                     f_y_min: float, Q: float, I: float,
                                     shear_to_yield: float = 0.6) -> Dict:
    """
    Calculates the capacity of a section in shear based on local shear
    yielding of an interface such as the connection between a flange and a web.

    This

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
    :param shear_to_yield: the ratio of shear yield to ordinary yield stress.
        By default this is 0.6 as per AS4100, which appears to be an
        approximation of the the value 1 / √3 ≈ 0.577 ≈ 0.6.
    :return: Returns the shear capacity as limited by interface shear of the
        connected components, in N.
        Results are returned as a dictionary:
        {'V_w_interface': Strength (N), 'Intermediate': {'min_t', 0 or 1}}
        The value of min_t is either 0 (if t1 is critical) or 1
        (if t2 is critical)
    """


    t1 = sum(t1)
    t2 = sum(t2)

    if t1 < t2:
        t = t1
        results = {'Intermediate': {'min_t': 0}}
    else:
        t = t2
        results = {'Intermediate': {'min_t': 1}}

    f_y_v = f_y_min * shear_to_yield  # shear yield stress

    V_w = f_y_v * t * I / Q  # shear capacity of interface

    results['V_w_interface'] = V_w # add the shear capacity into the results.

    return results

def s5_11_4_V_w_WeldLimited(v_w: Union(List[float], float), Q: float = 0.0,
                            I: float = 0.0) -> float:
    """
    Calculates the capacity of section in shear according to AS4100 S5.11.4
    where the capacity is limited by a weld, as is the case with some welded
    I sections to AS3679.2.

    This is only intended to apply to regular sections (fabricated channel,
    I and box sections) where the webs share the shear stress equally. For
    irregular sections where the webs may share the shear stress in an
    un-equal manner this equation will not apply.

    NOTE: where welds are critical, the value of φ used should be the value
    of φ for the welds in question. Typically this is not the same as the
    value of φ for structural steel.

    :param v_w: The weld capacity connecting the element being considered
        (in N/m). This can be either a float, or if more than one weld is
        used, a list of floats. I.e. for a welded I-beam with a weld either
        side of the web, you could supply either a single float:
        (v_w_LHS + v_w_RHS), or a list: [v_w_LHS, v_w_RHS].
    :param Q: The first or area moment of element that is being connected to
        the main section.
    :param I: The section moment of inertia about the axis perpendicular to
        the axis in which the shear is being applied.
    :return: Returns the shear capacity as limited by welds in N.
    """

    v_w = sum(v_w)  # get the sum of the capacity of the welds

    return v_w * I / Q

def s5_11_4_V_w_CHS(A_e: float, f_y: float,
                    shear_to_yield: float = 0.6) -> float:
    """
    Determine the shear yielding capacity of a CHS section to AS4100 S5.11.4.

    :param A_e: The effective area of the section in m², allowing for holes
        in the section as per AS4100 S5.11.4. Normally the gross area of the
        section will be acceptable as holes are not often made into standard
        sized circular members.
    :param f_y: The yield strength of the CHS section in Pa.
    :return: The shear yield strength of the section in N.
    """

    return 0.6 * shear_to_yield * f_y * A_e

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
    :return: Returns the shear buckling coefficient α_v.
    """

    α_v = 1.0

    if d_p / t_w > ((slenderness_limit) / ((f_y / f_y_ref ) **0.5)):
        α_v = ((slenderness_limit) / ((d_p / t_w ) *((f_y / f_y_ref ) **0.5)) ) **2

    return min(α_v, 1.0)

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

def s5_11_2_V_u(A: Union(List[float], float), f_y: Union(List[float], float),
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
                check_interface: bool = False) -> Dict[str, Any]:
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
    in custom fabricated girders.

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

    #update results dictionary
    results['Intermediate'].update({'V_panel': V_p})

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

    results['Intermediate'].update({'V_w': V_w})

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

    results['Intermediate'].update({'V_i': V_i})

    # endregion

    # finally, determine V_u

    if is_welded and check_interface:
        V_u = min(V_p, V_w, V_i) #shear capacity is limited by weld &
                                 #interface shear as well as panel strength.
    elif is_welded:
        V_u = min(V_p, V_w)  #shear capacity is lower of the panel capacity or
                             #the welds that connect it together
    elif check_interface
        V_u = min(V_p, V_i) #shear capacity is limited by interface shear.
    else:
        # if not welded or interface limited, shear capacity is just V_p
        V_u = V_p

    results.update({'V_u': V_u})

    return results

    # end shear capacity methods

    # endregion