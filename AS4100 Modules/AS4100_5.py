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

#section capacity methods

def s5_2_Ms(f_y, Z_e):
    '''
    Calculates the member section capacity according to AS4100 S5.2
    
    f_y: the section yield stress.
    Ze: the effective section modulus calculated according to S5.2.
    '''
    
    return fy * Ze