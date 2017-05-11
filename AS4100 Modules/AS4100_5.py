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
    Z_e: the effective section modulus calculated according to S5.2.
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

def s5_6_3_k_t(d_1, l, t_f, t_w, n_w, restraint_code = "FF"):
    '''
    Calculates the twist restraint factor to AS4100 S5.6.3.

    d_1: the web depth as per AS4100 (ignoring fillets & welds).
    l: the member segment length.
    t_f: flange thickness
    t_w: web thickness
    n_w: no. of webs.
    restraint_code: the restraint code based on AS4100 S5. acceptable values
                    are: FF, FL, LL, FU, FP, PL, PU, PP
    '''

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
    '''
    Determine the effective length for bending to AS4100 S5.6.3.

    k_t: twist restraint factor
    k_l: load height factor
    k_r: lateral rotation restraint factor
    l: member segment length between restraints
    '''

    return k_t * k_l * k_r * l

def s5_6_1_Mb(α_m, α_s, M_s):
    '''
    Determines the member buckling capacity according to AS4100 S5.6.1.

    α_m: moment modification factor.
    α_s: slenderness modification factor.
    M_s: section moment capacity.
    '''

    return α_m * α_s * M_s

#end member capacity region

#endregion

#shear capacity methods

#region

def s5_11_4_V_w_Generic(A_w, f_y):
    '''
    NEED TO ALLOW FOR LIMITING WELDS - PROBABLY DO A SEPARATE METHOD?

    Determine the shear yielding capacity of a flat web section to
    AS4100 S5.11.4.

    This method is assumed to be acceptable for determining the shear
    yielding capacity of any section except CHS sections, although
    allowances for non-uniform shear stress distributions should be made
    with the equation given in S5.11.3. For example, S9.3 gives an almost
    identical equation for the shear strength of a solid circular section
    (bolts) of 0.62 x f_u x A.
        
    A_w: the gross sectional area of the web. For hot rolled I & C sections
         it is acceptable to use the full depth of the section. For welded
         sections it is necessary to use only the web panel depth due to the
         discontinuity at the flange welds.
    f_y: the yield strength of the web section.
    '''
    
    return 0.6 * f_y, A_w

def s5_11_4_V_w_Weldlimited(no_welds, v_w, Q_max, I):
    '''
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

    no_welds: the number of welds to the web panel/s.
    v_w: the weld capacity
    Q_max: the moment of area of the largest flange connected to the section.
    I: the section moment of inertia about the axis perpendicular to the axis
       in which the shear is being applied.
    '''

    return (no_welds * v_w) * I / Q_max

def s5_11_4_V_w_CHS(A_e, f_y):
    '''
    Determine the shear yielding capacity of a CHS section to
    AS4100 S5.11.4.
    
    A_e: the effective area of the section, allowing for holes in the section
         as per AS4100 S5.11.4. Normally the gross area of the section will
         be acceptable as holes are not often made into standard sized
         circular members.
    f_y: the yield strength of the CHS section.    
    '''
    
    return 0.36 * f_y * A_e

def s5_11_4_V_w(A, f_y, is_CHS = False, is_welded = False,
                no_welds = 0.0, v_w = 0.0, Q_max = 0.0, I = 0.0):
    '''
    Determines the capacity of a section in shear yielding to AS4100 S5.11.4.

    NOTE: where the capacity is limited by a weld, as is the case with some
    welded I sections to AS3679.2.

    This is only intended to apply to regular sections (fabricated channel,
    I and box sections) where the webs share the shear stress equally. For
    irregular sections where the webs may share the shear stress in an
    un-equal manner this equation will not apply.

    NOTE: Calculates the capacity of section in shear according to AS4100
    S5.11.4 where the capacity is limited by a weld, as is the case with
    some welded I sections to AS3679.2. Where welds are critical, the value
    of φ used should be the value of φ for the welds in question. Typically
    this is not the same as the value of φ for structural steel.

    The check for shear capacity reduced by weld strength is NOT performed
    for CHS sections.

    A: the shear area of the section, either A_w or A_e, depending on whether
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
    f_y: the yield strength of the component in shear
    is_CHS: is the section a CHS? Default is False.
    is_welded: will welds affect the shear capacity? Default is False.
    no_welds: the number of welds to the web panel/s. Default is 0.0.
    v_w: the weld capacity. Default is 0.0.
    Q_max: the moment of area of the largest flange connected to the section.
           Default is 0.0.
    I: the section moment of inertia about the axis perpendicular to the axis
       in which the shear is being applied. Default is 0.0.
    '''

    if section.is_circle & section.is_hollow:
        V = s5_11_4_V_w_CHS(A, f_y)
    else:
        V = s5_11_4_V_w_Generic(A, f_y)

        if weld_limited:
            V_w = s5_11_4_V_w_Weldlimited(no_welds, v_w, Q_max, I)
            V = min(V, V_w)

    return V

def s5_11_3_Non_uniform_shear_factor(f_vm, f_va):
    '''
    Determines the non-uniform shear modification factor as per
    AS4100 S5.11.3. This applies for sections such as PFCs, Mono-symmetric
    I sections, angle sections etc.
    
    f_vm: the maximum shear stress in the section from an elastic analysis.
    f_va: the average shear stress in the section from an elastic analysis.
    '''

    return 2 / (0.9 + (f_vm / f_va))

def s5_11_5_V_b():

    return 1.0 * 1.0

#end shear capacity methods
#endregion

#bending capacity methods
#region



#end bending capacity method region
#endregion