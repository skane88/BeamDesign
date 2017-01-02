'''
This module calculates the capacity of a member in bending
to AS4100 Section 5.

This does NOT include sections calculating the section capacities
considering local buckling etc. It is assumed that all section properties
are calculated separately at this stage.

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
'''

import math

#section capacity methods
#region

def s5_2_M_s(f_y, Z_e):
    '''
    Calculates the member section capacity according to AS4100 S5.2
    
    f_y: the section yield stress.
    Ze: the effective section modulus calculated according to S5.2.
    '''
    
    return f_y * Z_e

#end section capacity methods
#endregion

#member capacity methods
#region

def s5_6_1_M_o(l_e, I_y, J, I_w, β_x = 0.0, E = 200e9, G = 80e9):
    '''
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
    '''

    A = (((math.pi * math.pi) * E * I_y) / (l_e * l_e))
    B = G * J
    C = (((math.pi * math.pi) * E * I_w) / (l_e * l_e))
    D = (β_x / 2)

    return (A**(0.5))*((B+C+(D**2)*A)**(0.5))+D*((A)**(0.5))

def s5_6_1_α_m(M_max, M_2, M_3, M_4, α_m_max = 2.5):
    '''
    Determines the moment modification factor α_m to AS4100 S5.6.1
    based on the member midspan moments & maximum moment.

    NOTE: According to the commentary this clause may be less accurate
    than some of the equations given in Table 5.6.1. 

    M_max: maximum moment in the segment.
    M_2, M_3, M_4: moments at the quarter points (M_2 & M_4) & midspan (M_3).
    α_m_max: the maximum allowable value of α_m. AS4100 specifies 2.5.    
    '''

    α_m = 1.7 * abs(M_max) / ((M_2 * M_2 + M_3 * M_3 + M_4 * M_4)**(0.5))

    return min(α_m, α_m_max)

def s5_6_α_s(M_s, M_o):
    '''
    Determines the slenderness modification factor α_s to AS4100 S5.6.1
    and S5.6.2. Both these sections use an identical equation except for
    using different values of M_o (M_oa and M_ob).
    
    M_s: the section moment capacity about the axis being considered.
    M_o: the reference buckling capacity about the axis being considered.
    '''

    return 0.6 * ((((M_s / M_o)**2 + 3)**(0.5)) - (M_s / M_o))

#end member capacity region
#endregion