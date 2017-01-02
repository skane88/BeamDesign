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

#end member capacity region
#endregion