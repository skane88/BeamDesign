"""
This module contains functions for calculating effective section properties
as required by AS4100 S5, 6 & 7.
"""

from BeamDesign.Sections.HollowCircle import HollowCircle


def s6_2_λ_e_flatplate(b, t, f_y, f_ref = 250.):
    """
    Calculates the slenderness of a plate element to
    AS4100 S6.2
    
    b: the width of a plate element
    t: thickness of the element
    f_y: the yield strength of the element in MPa
    f_ref: the reference yield stress, by default 250MPa
    """

    return (b / t)*((f_y / f_ref)**0.5)


def s6_2_λ_e_CHS(d_o, t, f_y, f_ref = 250.):
    """
    Calculates the slenderness of a CHS element to
    AS4100 S6.2
    
    d_o: the outside diameter of the CHS
    t: thickness of the element
    f_y: the yield strength of the element in MPa
    f_ref: the reference yield stress, by default 250MPa
    """

    return (d_o / t)*(f_y / f_ref)


def s6_2_b_e_flatplate(b, λ_e, λ_ey):
    """
    Calculates the effective width of a flat plate element to
    AS4100 S6.2
    
    b: the width of the plate element
    λ_e: the effective slenderness of the plate
    λ_ey: the yield slenderness limit for a
    reference plate of similar configuration (AS4100 T6.2.4)
    """

    return min(b * (λ_ey / λ_e), b)


def s6_2_d_e_CHS(d_o, λ_e, λ_ey):
    """
    Calculates the effective diameter of a CHS element to
    AS4100 S6.2
    
    d_o: the outside diameter of the CHS
    λ_e: the effective slenderness of the CHS
    λ_ey: the yield slenderness limit for a
    reference CHS of similar configuration (AS4100 T6.2.4)
    """

    d_e1 = d_o * (λ_ey / λ_e)**0.5
    d_e2 = d_o * (3 * λ_ey / λ_e)**2

    return min(d_e1, d_e2, d_o)


def s6_2_A_e_flatplate(b, t, f_y, λ_ey, f_ref = 250.):
    """
    Calculates the compression area of a flat
    plate element to AS4100 S6.2
    
    b: width of the plate
    t: thickness of the plate
    f_y: yield stress of the plate
    λ_ey: the yield slenderness limit for a
    reference plate of similar configuration (AS4100 T6.2.4)
    f_ref: the reference yield stress, by default 250 MPa
    """
    
    λ_e = s6_2_λ_e_flatplate(b,t,f_y,f_ref) # slenderness of plate
    b_e = s6_2_b_e_flatplate(b,λ_e,λ_ey) # effective width

    return b_e * t


def s6_2_A_e_CHS(d_o, t, f_y, λ_ey, f_ref = 250.):
    """
    Calculates the compression area of a flat
    plate element to AS4100 S6.2
    
    d_o: outside diameter of the plate
    t: thickness of the plate
    f_y: yield stress of the CHS
    λ_ey: the yield slenderness limit for a
    reference CHS of similar configuration (AS4100 T6.2.4)
    f_ref: the reference yield stress, by default 250 MPa
    """
    
    λ_e = s6_2_λ_e_CHS(d_o,t,f_y,f_ref) # effective slenderness
    d_e = s6_2_d_e_CHS(d_o, λ_e, λ_ey) # effective diameter
    
    c = HollowCircle(0,0,d_e/2,d_e/2-t)

    return c.area()


def s6_2_k_f_Form_Factor(A_n, A_e):
    """
    Calculate the form factor to AS4100 S6.2

    A_n: the net area as per AS4100 S6.2
    A_e: the effective area as per AS4100 S6.2
    """

    return A_e / A_n
