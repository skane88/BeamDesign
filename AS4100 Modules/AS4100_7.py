"""This module calculates tension capacities to AS4100
It includes helper functions for determining if pin
connections comply with clause 7.5 as well"""

def s7_2_Tensile_Yield(A_g, f_y):
    """Calculates the yield capacity of a member
    but does not include the capacity reduction factor
    
    A_g: gross area of a section
    f_y: yield strength of a section"""

    return A_g * f_y

def s7_2_Area_Reqd_Yield(N_t, f_y):
    """Calculates the area required to carry the force applied without
    yielding.
    
    N_t: applied force
    f_y: yield strength of a section"""

    return N_t / f_y

def s7_2_Ultimate_Fracture(A_n, f_u, k_t, ultimate_uncertainty = 0.85):
    """Calculates the ultimate fracture capacity of a section
    and includes the additional uncertainty factor from AS4100.
    
    A_n: net area of a section
    f_u: ultimate strength of a section
    k_t: eccentric connection factor
    ultimate_uncertainty: an uncertainty factor for ultimate
        strength behaviour, by default 0.85."""
    
    return A_n * f_u * k_t * ultimate_uncertainty

def s7_2_Area_Reqd_Ultimate(N_t, f_u, k_t, ultimate_uncertainty = 0.85):
    """Calculates the area required to carry the force applied without
    Fracture at ultimate load.
    
    N_t: applied force
    f_u: ultimate strength of a section
    k_t: eccentric connection factor
    ultimate_uncertainty: an uncertainty factor for ultimate
        strength behaviour, by default 0.85."""

    return N_t / ultimate_uncertainty / k_t / f_u

def s7_5_a_Unstiffened_Thickness(a_e, t):
    """Determines if the thickness satisfies the requirements
    of AS4100 S7.5a).
    
    a_e: edge distance from edge of hole to edge of member
    t: thickness of member.
    
    Note that this cannot be an exhaustive check as it depends
    significantly on the connection geometry which this library
    is not intended to check."""

    if t > 4 * a_e:
        return True
    return False

def s7_5_b_Area_Beyond_Hole(A_reqd, A_n):
    """Determines if the area beyond the hole complies with
    the requirements of AS4100 S7.5b)
    
    A_reqd: Area required for a member to carry the tension load
        based on AS4100 S7.2
    A_n: the net area beyond the hole or within 45deg"""

    if A_n > A_reqd:
        return True
    return False

def s7_5_c_Area_Perpendicular_Hole(A_reqd, A_sum):
    """Determines if the area perpendicular to the hole complies with
    the requirements of AS4100 S7.5c)
    
    A_reqd: Area required for a member to carry the tension load
        based on AS4100 S7.2
    A_sum: the sum of the area perpendicular to the member axis"""

    if A_sum > 1.33*A_reqd:
        return True
    return False

def s7_1_Area_Reqd(N_t, f_y, f_u, k_t, φ = 0.9, ultimate_uncertainty = 0.85):
    """Calculates the area required for a member to AS4100 section 7.1
    
    N_t: the design force.
    f_y: the yield strength of the section
    f_u: the ultimate strength of the section
    k_t: the connection efficiency factor
    φ: the capacity reduction factor, by default 0.9
    ultimate_uncertainty: a factor for the uncertainty in ultimate strength
    as per AS4100 S7.2. By default 0.85."""

    return max(s7_2_Area_Reqd_Ultimate(N_t,f_u,k_t,ultimate_uncertainty),s7_2_Area_Reqd_Yield(N_t,f_y))/φ

def s7_1_Tension_Capacity(A_g, A_n, f_y, f_u, k_t, φ = 0.9, ultimate_uncertainty = 0.85):
    """Calculates the tension capacity of a section according to AS4100 S7.1
    
    A_g: gross section area
    A_n: net section area
    f_y: yield strength. If different components have different yield strengths
    the minimum strength of the section should be used. Where a section has a
    significantly different strength the result may be too conservative and 
    this function may not be appropriate (i.e. a 250 grade web and a 450 grade flange)
    f_u: ultimate strength
    k_t: connection efficiency factor.
    φ: Capacity reduction factor, default is 0.9
    ultimate_uncertainty: a factor for uncertainty about the ultimate strength of a section,
    default is 0.85 as per AS4100 S7.2."""

    return φ * min(s7_2_Tensile_Yield(A_g,f_y),s7_2_Ultimate_Fracture(A_n,f_u,ultimate_uncertainty))