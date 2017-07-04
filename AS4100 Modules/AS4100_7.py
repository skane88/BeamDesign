# -*- coding: utf-8 -*-

"""
This module calculates tension capacities of steel members to AS4100
It includes helper functions for determining if pin
connections comply with clause 7.5 as well

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

from typing import Dict

def s7_2_N_t_yield(A_g: float, f_y: float) -> float:
    """
    Calculates the yield capacity of a member but does not include the capacity
    reduction factor.

    :param A_g: Gross area of a section in m².
    :param f_y: Yield strength of a section in Pa.
    :return: Returns the yielding capacity of the member in N.
    """

    return A_g * f_y

def s7_2_Ag(N_t: float, f_y: float) -> float:
    '''
    Calculates the area required to carry the force applied without yielding.
    
    :param N_t: The applied force in N.
    :param f_y: The yield strength of a section in Pa.
    :return: Returns the area required to carry the force applied without
        yielding (in m²).
    '''

    return N_t / f_y

def s7_2_N_t_ultimate(A_n: float, f_u: float, k_t: float,
                           ultimate_uncertainty: float = 0.85) -> float:
    '''
    Calculates the ultimate fracture capacity of a section and includes the
    additional uncertainty factor from AS4100.
    
    :param A_n: Net area of the section in m², allowing for holes as required
        by AS4100.
    :param f_u: The ultimate strength of the section in Pa.
    :param k_t: The connection efficiency factor / eccentric connection factor
        as per AS4100.
    :param ultimate_uncertainty: An uncertainty factor for ultimate strength
        behaviour, by default 0.85.
    :return: Returns the ultimate fracture capacity in N.
    '''
    
    return A_n * f_u * k_t * ultimate_uncertainty

def s7_2_An(N_t: float, f_u: float, k_t: float,
                            ultimate_uncertainty: float = 0.85) -> float:
    '''
    Calculates the area required to carry the force applied without fracture at
    ultimate load.
    
    :param N_t: The applied force in N.
    :param f_u: Ultimate strength of the section in Pa.
    :param k_t: The connection efficiency factor / eccentric connection factor
        as per AS4100.
    :param ultimate_uncertainty: an uncertainty factor for ultimate
        strength behaviour, by default 0.85.
    '''

    return N_t / ultimate_uncertainty / k_t / f_u

def s7_5_a_Unstiffened_Thickness(a_e: float, t: float) -> bool:
    '''
    Determines if the thickness of a pinned connection satisfies the
    requirements of AS4100 S7.5a.

    Note that this cannot be an exhaustive check as it depends
    significantly on the connection geometry which this library
    is not intended to check.

    :param a_e: Edge distance from edge of hole to edge of member in m.
    :param t: Thickness of member in m.
    :returns: Does the thickness of the connection comply with AS4100 S7.5a
        (True or False).
    '''

    if t > 4 * a_e:
        return True
    return False

def s7_5_b_Area_Beyond_Hole(A_reqd: float, A_n: float) -> bool:
    '''
    Determines if the area beyond the hole in a pinned connection complies with
    the requirements of AS4100 S7.5b.

    Note that this cannot be an exhaustive check as it depends
    significantly on the connection geometry which this library
    is not intended to check.

    :param A_reqd: Area required for a member to carry the tension load in m².
        Based on AS4100 S7.2.
    :param A_n: The net area beyond the hole or within 45deg, in m².
    :return: Does the connection comply with AS4100 S7.5b (True or False).
    '''

    if A_n > A_reqd:
        return True
    return False

def s7_5_c_Area_Perpendicular_Hole(A_reqd: float, A_sum: float) -> bool:
    '''
    Determines if the area perpendicular to the hole in a pinned connection
        complies with the requirements of AS4100 S7.5c.
    
    :param A_reqd: Area required for a member to carry the tension load in m².
        Based on AS4100 S7.2.
    :param A_sum: The sum of the area perpendicular to the member axis in m².
    :return: Does the connection comply with AS4100 S7.5c (True or False).
    '''

    if A_sum > 1.33*A_reqd:
        return True
    return False

def s7_1_A_reqd(N_t: float, f_y: float, f_u: float, k_t: float,
                   φ: float = 0.9, ultimate_uncertainty: float = 0.85) -> Dict[
    str, float]:
    '''
    Calculates the area required for a member to AS4100 section 7.1
    
    :param N_t: The applied force in N.
    :param f_y: The yield strength of a section in Pa.
    :param f_u: The ultimate strength of the section in Pa.
    :param k_t: The connection efficiency factor / eccentric connection factor
        as per AS4100.
    :param φ: The capacity reduction factor, by default 0.9.
    :param ultimate_uncertainty: A factor for the uncertainty in ultimate
        strength as per AS4100 S7.2. By default 0.85.
    :return: Returns the area required to carry the applied load without yield
        or fracture as per A4100, in m².

        Returned as a dictionary with the following values:

        {
            'A_g': The gross area required to prevent a yielding failure.

            'A_n': The net area required to prevent an ultimate fracture.

            'φA_g': The gross area required to prevent a yielding failure, with
            the AS4100 capacity reduction factor included.

            'φA_n': The gross area required to prevent an ultimate fracture,
            with the AS4100 capacity reduction factor included.

            'A': The maximum area required.

            'φA: The maximum area required, incorporating the AS4100 capacity
            reduction factor.
        }
    '''

    results = {'A_g': s7_2_Area_Reqd_Ultimate(N_t, f_u, k_t,
                                              ultimate_uncertainty),
               'A_n': s7_2_Area_Reqd_Yield(N_t, f_y)}

    results['A'] = max(results.values())

    results['φA_g'] = results['A_g'] / φ
    results['φA_n'] = results['A_n'] / φ
    results['φA'] = results['A'] / φ

    return results

def s7_1_N_t(A_g: float, A_n: float, f_y: float, f_u: float,
                          k_t: float, φ: float = 0.9,
                          ultimate_uncertainty: float = 0.85) -> Dict[
    str, float]:
    """
    Calculates the tension capacity of a section according to AS4100 S7.1.

    :param A_g: Gross area of a section in m².
    :param A_n: Net area of the section in m², allowing for holes as required
        by AS4100.
    :param f_y: The yield strength of the section in Pa. If different components
        have different yield strengths the minimum strength of the section
        should be used. Where a section has a significantly different strength
        the result may be too conservative and this function may not be
        appropriate (i.e. a 250 grade web and a 450 grade flange) - more
        detailed analysis (FEA modelling etc.) may be required.
    :param f_u: The ultimate strength of the section in Pa.
    :param k_t: The connection efficiency factor / eccentric connection factor
        as per AS4100.
    :param φ: The capacity reduction factor, by default 0.9.
    :param ultimate_uncertainty: A factor for the uncertainty in ultimate
        strength as per AS4100 S7.2. By default 0.85.
    :return: Returns the tensile strength of the section as per AS4100 S7.1,
        in N.

        Results are returned as a dictionary with the following values:

        {
            'N_ty': The yield capacity.

            'φN_ty': The yield capacity including the AS4100 capacity reduction
            factor.

            'N_tu': The ultimate capacity

            'φN_tu': The ultimate capacity including the AS4100 capacity
            reduction factor.

            'N': The minimum of N_ty and N_tu.

            'φN': The minimum capacity including the AS4100 capacity
            reduction factor.
        }
    """

    results = {'N_ty': s7_2_N_t_yield(A_g, f_y),
               'N_tu': s7_2_N_t_ultimate(A_n, f_u, k_t, ultimate_uncertainty)}
    results['N'] = min(results.values())

    results['φN_ty'] = results['N_ty'] * φ
    results['φN_tu'] = results['N_tu'] * φ
    results['φN'] = results['N'] * φ

    return results