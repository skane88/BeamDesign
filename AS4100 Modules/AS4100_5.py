# -*- coding: utf-8 -*-

"""
This module calculates the capacity of a member in bending
to AS4100 Section 5.

This does NOT include sections calculating the section capacities
considering local buckling etc. It is assumed that all section properties
are calculated separately at this stage.

This section only calculates properties that are independent of loads - 
properties dependent on other loads (i.e. shear capacities in S5.12)
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
from typing import List, Union
from HollowCircleClass import HollowCircleClass

#section capacity methods

#region

def s5_2_M_s(f_y, Z_e):
    """
    Calculates the member section capacity according to AS4100 S5.2
    
    f_y: the section yield stress.
    Z_e: the effective section modulus calculated according to S5.2.
    """
    
    return f_y * Z_e

#end section capacity methods

#endregion

#member capacity methods

#region

def s5_6_1_M_o(l_e, I_y, J, I_w, β_x = 0.0, E = 200e9, G = 80e9):
    """
    Calculates the reference buckling moment according to AS4100 S5.6.1.2.
    This equation is the same as the equation given for Mo in S5.6.1.1, 
    however allows for non-symmetric sections through the mono-symmetry
    constant β_x. For symmetric sections, β_x = 0.0 and the equation
    resolves to the same equation given in S5.6.1.1.

    l_e: The buckling effective length equation.
    I_y: The second moment of area about the minor principle axis.
    J: St Venant's torsion constant.
    I_w: The warping constant.
    E: The elastic modulus of the section.
    G: The shear modulus of the section.
    """

    A = (((math.pi * math.pi) * E * I_y) / (l_e * l_e))
    B = G * J
    C = (((math.pi * math.pi) * E * I_w) / (l_e * l_e))
    D = (β_x / 2)

    return (A**(0.5))*((B+C+(D**2)*A)**(0.5))+D*((A)**(0.5))

def s5_6_1_α_m(M_max, M_2, M_3, M_4, α_m_max = 2.5):
    """
    Determines the moment modification factor α_m to AS4100 S5.6.1
    based on the member midspan moments & maximum moment.

    NOTE: According to the commentary this clause may be less accurate
    than some of the equations given in Table 5.6.1. 

    M_max: maximum moment in the segment.
    M_2, M_3, M_4: moments at the quarter points (M_2 & M_4) & midspan (M_3).
    α_m_max: the maximum allowable value of α_m. AS4100 specifies 2.5.    
    """

    α_m = 1.7 * abs(M_max) / ((M_2 * M_2 + M_3 * M_3 + M_4 * M_4)**(0.5))

    return min(α_m, α_m_max)

def s5_6_α_s(M_s, M_o):
    """
    Determines the slenderness modification factor α_s to AS4100 S5.6.1
    and S5.6.2. Both these sections use an identical equation except for
    using different values of M_o (M_oa and M_ob).
    
    M_s: the section moment capacity about the axis being considered.
    M_o: the reference buckling capacity about the axis being considered.
    """

    return 0.6 * ((((M_s / M_o)**2 + 3)**(0.5)) - (M_s / M_o))

def s5_6_3_k_t(d_1, l, t_f, t_w, n_w, restraint_code = "FF"):
    """
    Calculates the twist restraint factor to AS4100 S5.6.3.

    d_1: the web depth as per AS4100 (ignoring fillets & welds).
    l: the member segment length.
    t_f: flange thickness
    t_w: web thickness
    n_w: no. of webs.
    restraint_code: the restraint code based on AS4100 S5. acceptable values
                    are: FF, FL, LL, FU, FP, PL, PU, PP
    """

    if restraint_code in ['FF', 'FL', 'LL', 'FU']:
        kt = 1.0
    elif restraint_code in ['FP', 'PL', 'PU']:
        kt = 1 + ((d_1 / l) * (t_f / (2 * t_w))**3) / n_w
    elif restraint_code in ['PP']:
        kt = 1 + (2 * (d_1 / l) * (t_f / (2 * t_w))**3) / n_w
    else:
        raise ValueError("Inappropriate restraint code provided. " + 
                         "expected FF, FL, LL, FU, FP, PL, PU or PP. " +
                         "Value provided was " + restraint_code + ".")

    return kt

def s5_6_3_l_e(k_t, k_l, k_r, l):
    """
    Determine the effective length for bending to AS4100 S5.6.3.

    k_t: twist restraint factor
    k_l: load height factor
    k_r: lateral rotation restraint factor
    l: member segment length between restraints
    """

    return k_t * k_l * k_r * l

def s5_6_1_Mb(α_m, α_s, M_s):
    """
    Determines the member buckling capacity according to AS4100 S5.6.1.

    α_m: moment modification factor.
    α_s: slenderness modification factor.
    M_s: section moment capacity.
    """

    return α_m * α_s * M_s

#end member capacity region

#endregion

#shear capacity methods

#region

def s5_11_4_V_w_Generic(A_w: float, f_y: float):
    """
    Determines the shear yielding capacity of a flat web section to
    AS4100 S5.11.4.

    This method is assumed to be acceptable for determining the shear
    yielding capacity of any section except CHS sections. For example, S9.3
    gives an almost identical equation for the shear strength of a solid
    circular section (bolts) of 0.62 x f_u x A.
    
    However, allowances for non-uniform shear stress distributions should be
    made with the equation given in S5.11.3. 
        
    :param A_w: the gross sectional area of the web. For hot rolled I & C
        sections it is acceptable to use the full depth of the section. For
        welded sections it is necessary to use only the web panel depth due
        to the discontinuity at the flange welds.
    :param f_y: the yield strength of the web section.
    :return: The web shear yield strength.
    """
    
    return 0.6 * f_y, A_w

def s5_11_4_V_w_Weldlimited(v_w: Union(List[float], float), Q: float,
                            I: float):
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
    :param I: the section moment of inertia about the axis perpendicular to
        the axis in which the shear is being applied.
    """

    #first check if v_w is a list or not
    if type(v_w) != list:
        #if not, convert it to a list so that the return equation does not
        #need to be different for lists & floats.
        v_w = [v_w]

    return sum(v_w) * I / Q

def s5_11_4_V_w_CHS(A_e: float, f_y: float):
    """
    Determine the shear yielding capacity of a CHS section to
    AS4100 S5.11.4.
    
    A_e: the effective area of the section, allowing for holes in the section
         as per AS4100 S5.11.4. Normally the gross area of the section will
         be acceptable as holes are not often made into standard sized
         circular members.
    f_y: the yield strength of the CHS section.    
    """
    
    return 0.36 * f_y * A_e

def s5_11_5_α_v(d_p: float, t_w: float, f_y: float,
                slenderness_limit: float = 82.0, f_y_ref: float = 250e6):
    """
    Determines the shear buckling coefficient α_v, which reduces the shear
    yielding load as per AS4100 section 11.5
    
    :param d_p: The web panel depth
    :param t_w: The web thickness
    :param f_y: The yield strength
    :param slenderness_limit: The slenderness limit. By default this is 82.0, 
        which is only valid for a web pin supported top and bottom. 
        In some circumstances this value may be very unconservative (i.e.
        shear buckling of an angle leg supported on one side only) Refer to
        "The Behaviour and Design of Steel Structures to AS4100" by Trahair
        et al. for more information.
    :param f_y_ref: The reference yield stress used in the slenderness limit
        equations. By default this is 250.0 in line with AS4100.
    :return: Returns the shear buckling coefficient α_v.
    """

    α_v = 1.0

    if d_p / t_w > ((slenderness_limit) / ((f_y / f_y_ref)**0.5)):
        α_v = ((slenderness_limit) / ((d_p / t_w)*((f_y / f_y_ref)**0.5)))**2

    return min(α_v, 1.0)

def s5_11_3_Non_uniform_shear_factor(f_vm: float, f_va: float):
    """
    Determines the non-uniform shear modification factor as per
    AS4100 S5.11.3. This applies for sections such as PFCs, Mono-symmetric
    I sections, angle sections etc.

    :param f_vm: The maximum shear stress in the section from an elastic analysis.
    :param f_va: The average shear stress in the section from an elastic analysis.
    :return: Returns the non-uniform shear factor used to reduce the shear capacity
        for non-uniform members.
    """

    return min(2 / (0.9 + (f_vm / f_va)), 1.0)

def s5_11_2_V_u(A: Union(List[float], float), f_y: Union(List[float], float),
                is_CHS: Union(List[bool], bool), d: Union(List[float], float),
                t: Union(List[float], float),
                slenderness_limit: Union(List[float], float),
                no_welds: Union(List[int], int),
                v_w: Union(List[float], float), Q: Union(List[float],float),
                f_y_ref = 250e6,
                is_welded = False, v_w: float = 0.0,
                I: float = 0.0, is_uniform: bool = True,
                f_vm: float = 1.0, f_va: float = 1.0) -> float:
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
    
    :param A: the shear area of the section, either A_w or A_e, depending on whether
    the section is a generic section or a CHS.
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
        [1.0, 2.0, 3.0, ..., n] to enable multiple elements to be entered.
        This is entered separately from the panel depths & thicknesses to
        allow overriding the area (if say holes are present in the web) 
        without overriding the buckling calculations. To calculate the area
        directly from the entered values, use 0.0 for an elements area in A
        and the area will be directly calculated.
    :param f_y: The yield strength of the component in shear. This parameter
        is either a float, or if multiple units are present, a list of floats
        can be used to enable multiple shear components to be considered.
        Only the minimum yield strength is used.
    :param is_CHS: Is the section a CHS?
    :param d: The web panel depth or CHS outside diameter.
    :param t: The web or CHS thickness.
    :param slenderness_limit: The slenderness limit. Typically this would be
        82, but this is only valid for a web pin supported top and bottom. 
        In some circumstances this value may be very unconservative (i.e.
        shear buckling of an angle leg supported on one side only) Refer to
        "The Behaviour and Design of Steel Structures to AS4100" by Trahair
        et al. for more information.
    :param no_welds: The number of welds between the web panel/s and the rest
        of the section at the critical interface (i.e. between web and top
        flange, or between web and bottom flange).
        A list of nos of welds can be provided, to allow for checks of
        multiple welded parts. Each element should be the no. of welds that
        connect the part with a corresponding Q value below to the rest of
        the element.
        Only used if is_welded = True.
    :param v_w: The weld capacity. Default is 0.0.
        A list of weld capacities can be provided. Each item in the list
        should correspond to the weld capacity of the welds that connect
        an element of a given Q value below to the rest of the element.
    :param Q: The moment of area of the element connected to the rest of the
        structure (i.e. a flange, or a web element). A list can be provided
        to allow consideration of multiple elements that make up a section.
    :param f_y_ref: The reference yield stress used in the slenderness limit
        equations. By default this is 250.0 in line with AS4100.
    :param is_welded: Will welds affect the shear capacity? Default is False.
    :param I: The section moment of inertia about the axis perpendicular to the
        axis in which the shear is being applied. Default is 0.0.
    :param is_uniform: Is the shear on the section uniform? Default is True.
    :param f_vm: The maximum shear stress in the section from an elastic
        analysis.
    :param f_va: The average shear stress in the section from an elastic
        analysis.
    :return: Returns the shear capacity of the section.
    """

    #Input check region
    #region

    #region

    #check if A, f_y, is_CHS, d, t and slenderness_limit are lists.
    #if not, convert to lists.
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

    #build a list of the List lengths to check that min & max are OK.
    list_lens = [len(A), len(f_y), len(is_CHS), len(d), len(t),
                 len(slenderness_limit)]

    if min(list_lens) != max(list_lens):
        #if the minimum list length <> maximum list length there is an error
        raise IndexError("Expected all entry lists to be of the same size")
    if list_lens[0] <= 0:
        #if the list length is <0 there are no items to check
        raise ValueError("Expected a list of shear elements to check. Input" +
                         "does not contain any shear elements")

    #endregion

    #region

    #need to do the same checks for the no_welds, v_w and Q lists.
    #convert values to lists if not a list.
    if type[no_welds] != list:
        no_welds = [no_welds]
    if type[v_w] != list:
        v_w = [v_w]
    if type [Q] != list:
        Q = [Q]

    #build a list of lengths to check min & max lengths

    list_lens = [len(no_welds), len(v_w), len(Q)]

    if min(list_lens) != max(list_lens):
        # if the minimum list length <> maximum list length there is an error
        raise IndexError("Expected all entry lists to be of the same size")
    if list_lens[0] <= 0:
        # if the list length is <0 there are no items to check
        raise ValueError("Expected a list of shear weld elements to check. " +
                         "Input does not contain any shear weld elements")

    #endregion

    #endregion

    #determine the minimum shear yield strength.
    f_y_min = min(f_y)

    #calculate the yield strength

    #region

    #set the shear capacity to 0 by default
    V_y = 0.0
    A_current = 0.0
    V_current = 0.0

    for i in range(len(A)):
        #here we iterate through the list of areas & calculate the yield
        #capacity of the section.
        if A[i] !=0:
            #if area <> 0, then area is simply A.
            A_current = A[i]
        else:
            #need to calculate the area
            if not is_CHS:
                #assume if not a CHS that it is a simple rectangle
                A_current = d[i] * t[i]
            else:
                #If CHS, need to calculate the area of a hollow circle
                CHS = HollowCircleClass(0.0, 0.0 ,d[i] / 2, (d[i] - 2*t) / 2)
                A_current = CHS.area()

        #next calculate the shear capacity

        if not is_CHS:
            #if not a CHS use the generic shear capacity method
            V_current = s5_11_4_V_w_Generic(A_current,f_y_min)
        else:
            #if a CHS, use the CHS method.
            V_current = s5_11_4_V_w_CHS(A_current, f_y_min)

        #the total shear strength in yield is the sum of all element types:
        V_y = V_y + V_current

    #NOTE: by default yield strength is set equal to V_w. In reality this
    #could be limited by the welds, but to guard against this the yield
    #strength is re-calculated below

    #endregion

    α_v = 1.0 #by default

    #next need to calculate the buckling capacity of every element.

    if not is_CHS:
        V_y = s5_11_4_V_w_Generic(A, f_y) #buckling only applies to yield
                                          #strength not to the weld limited
                                          #capacity
        α_v = s5_11_5_α_v(d, t, f_y, slenderness_limit, f_y_ref)

    V_u = min(α_v * V_y, V_w) #shear capacity is lower of yield or weld
                              #limited capacity.

    uniform_shear_factor = 1.0 #by default

    if not is_uniform:
        uniform_shear_factor = s5_11_3_Non_uniform_shear_factor(f_vm, f_va)

    V_u = α_v * V_w * uniform_shear_factor

    return V_u

#end shear capacity methods

#endregion

#bending capacity methods

#region



#end bending capacity method region

#endregion
