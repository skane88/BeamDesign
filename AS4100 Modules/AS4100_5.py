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
from typing import List, Union, Dict
from HollowCircleClass import HollowCircleClass

#section capacity methods

#region

def s5_2_M_s(f_y: float, Z_e: float) -> float:
    """
    Calculates the member section capacity according to AS4100 S5.2
    
    :param f_y: the section yield stress in Pa.
    :param Z_e: the effective section modulus in m³.
        Calculated according to S5.2.
    :return: Returns the member section capacity in Nm.
    """
    
    return f_y * Z_e

#end section capacity methods

#endregion

#member capacity methods

#region

def s5_6_1_M_o(l_e: float, I_y: float, J: float, I_w: float,
               β_x: float = 0.0, E: float = 200e9, G: float = 80e9) -> float:
    """
    Calculates the reference buckling moment according to AS4100 S5.6.1.2.
    This equation is the same as the equation given for Mo in S5.6.1.1, 
    however allows for non-symmetric sections through the mono-symmetry
    constant β_x. For symmetric sections, β_x = 0.0 and the equation
    resolves to the same equation given in S5.6.1.1.

    :param l_e: The buckling effective length in m.
    :param I_y: The second moment of area about the minor principal axis
        in m⁴.
    :param J: St Venant's torsion constant in m⁴.
    :param I_w: The warping constant in m⁶.
    :param E: The elastic modulus of the section in Pa.
    :param G: The shear modulus of the section in Pa.
    :return: The reference buckling moment in Nm as per AS4100 S5.6.1.
    """

    A = (((math.pi * math.pi) * E * I_y) / (l_e * l_e))
    B = G * J
    C = (((math.pi * math.pi) * E * I_w) / (l_e * l_e))
    D = (β_x / 2)

    return (A**(0.5))*((B+C+(D**2)*A)**(0.5))+D*((A)**(0.5))

def s5_6_1_α_m(M_max: float, M_2: float, M_3: float, M_4: float,
               α_m_max: float = 2.5):
    """
    Determines the moment modification factor α_m to AS4100 S5.6.1.
    based on the member midspan moments & maximum moment.

    NOTE: According to the commentary this clause may be less accurate
    than some of the equations given in Table 5.6.1. 

    :param M_max: Maximum moment in the segment, in Nm.
    :param M_2: Moments at the quarter point in Nm.
    :param M_3: Moments at the midspan in Nm.
    :param M_4: Moments at the quarter point in Nm.
    :param α_m_max: The maximum allowable value of α_m. AS4100 specifies 2.5.
    :return: Returns the moment modification factor α_m to AS4100 S5.6.1.
    """

    α_m = 1.7 * abs(M_max) / ((M_2 * M_2 + M_3 * M_3 + M_4 * M_4)**(0.5))

    return min(α_m, α_m_max)

def s5_6_α_s(M_s: float, M_o: float) -> float:
    """
    Determines the slenderness modification factor α_s to AS4100 S5.6.1
    and S5.6.2. Both these sections use an identical equation except for
    using different values of M_o (M_oa and M_ob).
    
    :param M_s: The section moment capacity about the axis being considered,
        in Nm.
    :param M_o: The reference buckling capacity about the axis being
        considered, in Nm.
    :return: Returns the slenderness modification factor to AS4100 S5.6.1.
    """

    return 0.6 * ((((M_s / M_o)**2 + 3)**(0.5)) - (M_s / M_o))

def s5_6_3_k_t(d_1: float, l: float, t_f: float, t_w: float, n_w: float,
               restraint_code: str = "FF") -> float:
    """
    Calculates the twist restraint factor to AS4100 S5.6.3.

    :param d_1: The web depth as per AS4100 (ignoring fillets & welds) in m.
    :param l: The member segment length in m.
    :param t_f: Flange thickness in m.
    :param t_w: Web thickness in m.
    :param n_w: Number of webs.
    :param restraint_code: The restraint code based on AS4100 S5 as a string.
        Acceptable values are: 'FF', 'FL', 'LL', 'FU', 'FP', 'PL', 'PU', 'PP'.
    :return: Returns the twist restraint factor as per AS4100 S5.6.3.
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

def s5_6_3_l_e(k_t: float, k_l: float, k_r: float, l: float) -> float:
    """
    Determine the effective length for bending to AS4100 S5.6.3.

    :param k_t: Twist restraint factor.
    :param k_l: Load height factor.
    :param k_r: Lateral rotation restraint factor.
    :param l: Member segment length between restraints.
    :return: The effective length as per AS4100 S5.6.3.1.
    """

    return k_t * k_l * k_r * l

def s5_6_1_Mb(M_s: float, α_m: float = 1.0, α_s: float = 1.0) -> float:
    """
    Determines the member buckling capacity according to AS4100 S5.6.1.

    :param M_s: section moment capacity in Nm.
    :param α_m: moment modification factor.
    :param α_s: slenderness modification factor.
    :return: The member moment capacity in Nm.
    """

    return α_m * α_s * M_s

#end member capacity region

#endregion

#bending capacity methods

#region



#endregion
