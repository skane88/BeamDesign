'''
This module calculates the compression capacity of a steel member to AS4100.

This DOES NOT include section property calculations for effective areas
based on local buckling of sections. AS4100 uses an effective area method
which is similar for bending or compression. Also, the section properties
are conceptually independent of the other compression checks. Therefore
these formulas have been moved to their own module.

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

Need to do unit tests
'''

import math
import sympy
import numpy
import functools
from SymmetryClass import Symmetry

#section capacity methods
#region

def s6_2_A_e(A_n, k_f):
    '''
    Calculates the generic effective compression area to AS4100 S6.2.
    Relies on k_f having already been calculated.
    
    A_n: the net area of the section.
    k_f: the compression effective area factor.
    '''

    return A_n * k_f

def s6_2_N_s(A_e, f_y):
    '''
    Calculate the section capacity to AS4100 S6.2

    A_e: effective area, reduced for holes & local buckling.
    f_y: yield strength
    '''
    
    return A_e * f_y

#end section capacity methods
#endregion

#member property methods
#region

def s6_3_2_l_e(l, k_e = 1.):
    '''
    Calculate the effective length according to AS4100 S6.3.2
    
    l: actual member length.
    k_e: effective length factor, by default 1.0.
    '''

    return l * k_e

#end member property methods
#endregion

#Euler buckling methods
#region

def N_euler(E, I, l_e):
    '''
    Calculates the Euler buckling load of a column.
    
    E: the elastic modulus of the section.
    I: the second moment of area of the section.
    l_e: the effective length of the column.
    '''
    
    return (math.pi * math.pi) * E * I / (l_e * l_e)

def f_euler(E, l_e, r):
    '''
    Calculates the Euler buckling load of a column.
    
    E: the elastic modulus of the section.
    l_e: the effective length of the column.
    r: the radius of gyration of the column.
    '''
    
    return (math.pi * math.pi) * E / ((l_e / r)*(l_e / r))

@functools.lru_cache()
def r_ol(r_x, r_y, x_o, y_o):
        '''
        Returns the polar radius of gyration required by AS4600 for a check
        of the torsional buckling capacity.
    
        r_x: radius of gyration about the x-axis at the section centroid.
        r_y: radius of gyration about the y-axis at the section centroid.
        x_o: x co-ordinate of the shear centre.
        y_o: y co-ordinate of the shear centre.
        
        Is wrapped in an lru_cache to speed use of this function.
        '''

        return ((r_x*r_x) + (r_y*r_y) + (x_o*x_o) + (y_o*y_o))**0.5
        #using r_x*r_x rather than r_x**2 to avoid overhead of a power function. 

@functools.lru_cache()
def f_euler_torsion(A, l_ez, r_x, r_y, x_o, y_o, J, I_w, E, G):
    '''
    Returns the Euler buckling stress for a torsional buckling mode.
    
    A: gross or net area of the cross section.
        Net area is conservative.
    l_ez: effective length for torsional buckling.
    r_x, r_y: radii of gyration.
    x_o, y_o: distance between shear centre and section centre.
    J: St Venant's torsion constant.
    I_w: Section warping torsion constant.
    E: Elastic modulus of the section.
    G: Shear modulus of the section.
    
    Wrapped in an lru_cache to speed access.
    '''

    r_o = r_ol(r_x, r_y, x_o, y_o)
    a = (G * J) / (A * r_o * r_o)
    b = ((math.pi*math.pi) * E * I_w) / (G * J * (l_ez*l_ez))

    return a * (1 + b)

#end of Euler buckling methods
#endregion

#member flexural buckling capacity methods
#region

def s6_3_3_λ_n(k_f, l_e, r, f_y, f_ref = 250e6):
    '''
    Calculate the member modified effective slenderness according
    to AS4100 S6.3.3.
    
    k_f: the form factor as per AS4100 S6.2
    l_e: the effective length of the section about the axis under consideration.
    r: the radius of gyration about the axis under consideration.
    f_y: the yield stress of the section under consideration.
    f_ref: the reference yield stress, by default 250.
    '''

    return (l_e / r) * (k_f ** 0.5) * ((f_y / f_ref) ** 0.5)

def s6_3_3_α_c(λ_n, α_b = 1.0):
    '''
    Calculate the buckling coefficient α_c according
    to AS4100 S6.3.3.
    
    k_f: the form factor as per AS4100 S6.2
    l_e: the effective length of the section about the axis under consideration.
    r: the radius of gyration about the axis under consideration.
    f_y: the yield stress of the section under consideration.
    f_ref: the reference yield stress, by default 250.
    α_b: the member section constant for the given value of k_f (see AS4100 T6.3.3(1) & (2)).
    Conservatively can be taken to be 1.0. Default argument of 1.0
    
    Returns all intermediate values from AS4100 S6.3.3. as a dictionary to allow querying of
    intermediate results. for only the slenderness factor call results['α_c'].

    Intermediate results: α_a, λ, η, ξ
    '''
    
    α_a = (2100 * (λ_n - 13.5)) / (λ_n**2 - 15.3*λ_n + 2050)  #modification for member geometric imperfections
    λ = λ_n + α_a * α_b #modified effective slenderness  modified by residual stress and geometric imperfection factors.
    η = max(0.00326 * (λ - 13.5), 0.)
    ξ = ((λ / 90)**2 + 1 + η) / (2 * (λ / 90)**2)
    α_c = ξ * (1 - (1 - (90 / (ξ * λ))**2)**0.5) #Return α_c
    
    return {"Intermediate": {"α_a": α_a, "λ": λ, "η": η, "ξ": ξ}, "α_c": α_c} 

def s6_3_3_N_c(A_n, k_f, l_e, r, f_y, f_ref = 250e6, α_b = 1.0):
    '''
    Calculates the member buckling capacity according to AS4100 S6.3.3
    Note that this is not reduced down to the section capacity, so if
    the member is short the buckling capacity reported could be larger than
    the section capacity.
    
    A_n: the net area of the section
    k_f: the form factor as per AS4100 S6.2
    l_e: the effective length of the section about the axis considered
    r: the radius of gyration about the axis considered.
    f_y: the yield stress of the section.
    f_ref: the reference yield stress, by default 250e6.
    α_b: the member section constant for the given value of k_f (see AS4100
        T6.3.3(1) & (2)). Conservatively can be taken to be 1.0. By default 1.

    Returns a dictionary of results containing intermediate values. Returned
    intermediate values are: l_e, r, λ_n, α_a, λ, η, ξ.
    To get only N_c, use: results_dict['N_c'].
    '''

    N_s = s6_2_N_s(s6_2_A_e(A_n, k_f),f_y)

    λ_n = s6_3_3_λ_n(k_f, l_e, r, f_y)
    α_c = s6_3_3_α_c(λ_n, α_b)

    N_c = N_s * α_c['α_c']
    
    results = {'N_c': N_c}

    results['Intermediate'] = {'λ_n': λ_n, 'λ_n': λ_n}
    results['Intermediate'].update({'α_c': α_c['α_c']})
    results['Intermediate'].update(α_c['Intermediate'])
    results['Intermediate'].update({'l_e': l_e, 'r': r})

    return results

#end member flexural buckling capacity methods
#endregion

#member torsion capacity methods - AS4600
#region

@functools.lru_cache()
def f_oxz(A_n, l_ex, l_ez, r_x, r_y, x_o, y_o, J, I_w, E, G):
    '''
    Calculates the flexural-torsional buckling stress as per AS4600
    Section 3.4.3. Only valid for doubly or singly symmetric sections.
        
    A_n: net area of the section. NOTE: AS4600 uses the full area - using
        net area should be slightly conservative in some cases.
    l_ex, l_ez: effective lengths of the member.
    r_x: radius of gyration.
    x_o: distance from shear centre to section centre.
    r_ol: radius of gyration about the shear centre.
    J: St Venant's torsion constant.
    I_w: the warping constant of the shape.
    E: the elastic modulus.
    G: the shear modulus.
        
    Returns results as a dictionary with intermediate results for
    future reference. Intermediate values returned are f_ox, f_oz, 
    r_x, r_y, x_o, y_o, r_ol and β.
    For only the compressive buckling stress use returnval["f_oxz"].
    '''
    
    r_o = r_ol(r_x, r_y, x_o, y_o)
    β = 1 - (x_o / r_o)**2
    f_ox = f_euler(E, l_ex, r_x)
    f_oz = f_euler_torsion(A_n, l_ez, r_x, r_y, x_o, y_o, J, I_w, E, G)

    f_ = 1/(2 * β) * ((f_ox + f_oz) - ((f_ox + f_oz)**2 -
                                       (4 * β * f_ox * f_oz))**0.5)

    return {"Intermediate": {"β": β, "f_ox": f_ox, "f_oz": f_oz, 'r_x': r_x,
                             'r_y': r_y, 'x_o': x_o, 'y_o': y_o, 'r_ol': r_o},
            "f_oxz": f_}

def f_oc_double_symmetric(A_n, l_ex, l_ez, r_x, r_y, x_o, y_o, J, I_w, E, G,
                          sym = Symmetry(['x', 'y'])):
    '''
    Calcluates the flexural-torsional buckling stress for a doubly symmetric
    section as per AS4600, as required by AS4100 S6.3.3.
    Calculated as per AS4600 S3.4.3
    Ignores the flexural-buckling stress as this is calculated from direct
    AS4100 formulas.
    
    A_n: net area of the section. NOTE: AS4600 uses the full area - 
        using net area should be slightly conservative in some cases.
    l_ex, l_ez: effective lengths of the member.
    r_x, r_y: radius of gyration.
    x_o, y_o: the distance from the shear centre to the centroid of the shape.
    J: St Venant's torsion constant.
    I_w: the warping constant of the shape.
    E: the elastic modulus.
    G: the shear modulus.

    returns a dictionary with intermediate calculation values included.
    Intermediate values returned are f_ox, f_oz, r_x, r_y, x_o, y_o, r_ol, β,
        f_oxz and the 'AS4600 Clause'.
    For the value of f_oc only call returnvals["f_oc"].
    '''

    foxz = f_oxz(A_n, l_ex, l_ez, r_x, r_y, x_o, y_o, J, I_w, E, G)
    foz = f_euler_torsion(A_n, l_ez, r_x, r_y, x_o, y_o, J, I_w, E, G)

    '''
    AS4600 S3.4.3 states that for doubly symmetric sections subject
    to flexural-torsional buckling the critical stress f_oc is either
    the smaller of the euler buckling stress in the y-axis,
    the flexural-torsional buckling stress f_oxz and the euler-torsional
    buckling stress f_oz.

    The euler buckling stress in the y-axis is assumed to be taken care
    of by the AS4100 member capacity checks for the y-axis and is ignored.
    Therefore, only checks of f_oz and f_oxz are done here.
    '''
    
    #Determine if f_oxz or f_oz are the governing torsional modes:
    results = {'f_oc': min(foxz['f_oxz'],foz)}
    #add intermediate results
    results['Intermediate'] = foxz['Intermediate']
    #add a f_oxz & f_oz to intermediate
    results['Intermediate'].update({'f_oxz': foxz['f_oxz']})
    results['Intermediate'].update({'f_oz': foz}) 

    #add the AS4600 clause to the intermediate results
    results["Intermediate"].update({"AS4600 Clause": "AS4600 S3.4.3"})
    results['Intermediate'].update({'Symmetry': sym.symmetry})

    return results

def f_oc_single_symmetric(A_n, l_ex, l_ey, l_ez, r_x, r_y, x_o, y_o, J, I_w,
                          E, G, sym = Symmetry()):
    '''
    Calcluates the flexural-torsional buckling stress for a singly symmetric
    section as per AS4600, as required by AS4100 S6.3.3.
    Calculated as per AS4600 S3.4.3
    Note that the "x" axis for singly symmetric sections is actually the axis
    of symmetry according to AS4600. For most practical monosymmetric sections
    such as I sections with unequal flanges it is expected that this will be
    conservative as this will be the weaker axis anyway. For some sections
    such as PFCs, angles and shallow Is with a very wide flanges
    the stronger axis is actually the axis of symmetry (x axis is the symmetry
    axis) - in this case it is presumed that minor axis flexural buckling is
    more likely to govern and will be covered by other clauses in AS4100 S6.3.
    Ignores the flexural-buckling stress as this is calculated from direct
    AS4100 formulas.
    
    A_n: net area of the section. NOTE: AS4600 uses the full area - 
        using net area should be slightly conservative in some cases.
    l_ex, l_ey, l_ez: effective lengths of the member.
    r_x, r_y: radius of gyration.
    x_o, y_o: distance from shear centre to centroid.
    J: St Venant's torsion constant.
    I_w: the warping constant of the shape.
    E: the elastic modulus.
    G: the shear modulus.
    sym: a Symmetry type object describing the section's axes of symmetry.

    returns a dictionary with intermediate calculation values included.
    For the value of f_oc only call returnvals["f_oc"].
    '''

    if sym.symcount != 1:
        raise ValueError('Expected a single-symmetric section but received a'+
                         ' section with a symmetry of ' + sym.symmetry +
                         ' in ' + sym.symcount + ' axes')

    '''
    AS4600 S3.4.3 requires that the torsional buckling check be carried out
    about the axis of symmetry. Therefore, need to choose the correct axis
    for the symmetry checks. By default if sym() does not provide 'x' or 'y'
    checks will be carried out about the 'y' axis.
    '''
    if sym.axes[0] == 'x':
        f_oc = f_oxz(A_n, l_ex, l_ez, r_x, r_y, x_o, y_o, J, I_w, E, G)
        f_oc['Intermediate'].update({'Axis of Symmetry': 'x'})
    else:
        f_oc = f_oxz(A_n, l_ey, l_ez, r_y, r_x, y_o, x_o, J, I_w, E, G)
        #note that have switched l_ey for l_ex, and positions of r_x & r_y,
        #x_o & y_o
        f_oc['Intermediate'].update({'Axis of Symmetry': 'y'})
    
    
    results = {'f_oc': f_oc['f_oxz']}
    
    #store intermediate results for later
    results['Intermediate'] = f_oc['Intermediate']
    results['Intermediate'].update({'f_oxz': f_oc['f_oxz']})
    results['Intermediate'].update({'Symmetry': sym.symmetry})

    #add the AS4600 clause to the intermediate results
    results["Intermediate"].update({"AS4600 Clause": "AS4600 S3.4.3"})

    return results

def f_oc_point_symmetric(A_n, l_ez, r_x, r_y, x_o, y_o, J, I_w, E, G):
    '''
    Calcluates the flexural-torsional buckling stress for a single
    or doubly symmetric section as per AS4600, as required by
    AS4100 S6.3.3. Calculated as per AS4600 S3.4.4
    Ignores the flexural buckling stresses as these are calculated
    directly using AS4100 equations.
    
    A_n: net area of the section. NOTE: AS4600 uses the full area
        - using net area should be slightly conservative in some cases.
    l_ez: effective lengths of the member.
    r_x, r_y: radii of gyration.
    x_o, y_o: distance from shear centre to section centre.
    J: St Venant's torsion constant.
    I_w: the warping constant of the shape.
    E: the elastic modulus.
    G: the shear modulus.

    For consistency with other f_oc calculations, returns as a dictionary.
    There are no intermediate results. To get f_oc, call results["f_oc"]
    '''

    return {"f_oc": f_euler_torsion(A_n, l_ez, r_x, r_y, x_o, y_o, J, I_w, E, G),
            "Intermediate": {"AS4600 Clause": "AS4600 S3.4.4"}}

def f_oc_unsymmetric(A_n, l_ex, l_ey, l_ez,
                        r_x, r_y, x_o, y_o, J, I_w, E, G):
    '''
    Calculate the buckling stress for a non-symmetric section using AS4600
    as required by AS4100 S6.3.3.
    Calculated according to AS4600 S3.4.5.
    Uses Sympy to solve the cubic equation.
    
    A_n: net area of the section. NOTE: AS4600 uses the full area. Using net
        area should be slightly conservative in some cases.
    l_ex, l_ey, l_ez: effective lengths of the member.
    r_x, r_y: radii of gyration.
    x_o, y_o: location of shear centre relative to the centroid.
    J: St Venant's torsion constant.
    I_w: the warping constant of the shape.
    E: the elastic modulus.
    G: the shear modulus.

    Returns a dictionary with the value of f_oc and also 
    the intermediate results for future reference.
    To simply use f_oc call resultvals["f_oc"].
    '''

    f_ox = f_euler(E, l_ex, r_x)
    f_oy = f_euler(E, l_ey, r_y)
    r_o = r_ol(r_x, r_y, x_o, y_o)
    f_oz = f_euler_torsion(A_n, l_ez, r_x, r_y, x_o, y_o, J, I_w, E, G)
    
    a = (r_o**2) - (x_o**2) * (y_o**2)
    b = (r_o**2) * (f_ox + f_oy + f_oz) - (f_oy * (x_o**2) + f_ox * (y_o**2))
    c = (r_o**2) * (f_ox * f_oy + f_oy * f_oz + f_ox * f_oz)
    d = (r_o**2) * f_ox * f_oy * f_oz
    
    #get the coefficients of the polynomial to solve with numpy.
    eqn = [a, -b, c, -d]
    results = numpy.roots(eqn)

    minstress = None

    for i in results:
        #next check if the result is a real answer
        
        if type(i) is complex:
            #do nothing if i is complex
            pass
        else:
            if i < 0:
                #if i < 0 then don't report. a negative buckling stress
                #does not make sense.
                pass
            elif (minstress == None):
                #if there is nothing in minstress then we should just set
                #minstress equal to the value of i.
                minstress = i
            else:
                #by now we know that a) i is not complex. b) i>=0.
                #c) minstress has at least 1x value. Therefore we
                #need to get the smaller value of the current i & minstress.
                minstress = min(minstress, i)

    #next need to check that we have at least one answer
    if minstress == None:
        raise Exception("No real solution for the buckling stress. " +
                        "Imaginary solutions are: " + str(results))

    return {"f_oc": minstress,
            "Intermediate": {"AS4600 Clause": "S3.4.5", "Equation": eqn,
                                "Solutions": str(results), "f_ox": f_ox,
                                "f_oy": f_oy, "f_oz": f_oz, "a": a, "b": b,
                                "c": c, "d": d}}

def s6_3_3_N_c_torsion(A_n, k_f, l_ex, l_ey, l_ez, r_x, r_y, x_o, y_o, J, I_w,
                       f_y, E, G, sym = Symmetry(), uncertainty_factor = 0.85):
    '''This calculates the torsional buckling capacity to AS4600
    as required by AS4100 S6.3.3 for singly, point and non-symmetric
    shapes.
    Currently ignoes flexural buckling checks and simply checks torsional
    buckling as required by AS4100.
    It also does not reduce the capacity to the section capacity and as
    such could report a larger buckling capcacity than the section
    capacity for short members.
    
    A_n: net area of the section. NOTE: AS4600 uses the full area - using
        net area should be slightly conservative in some cases.
    A_e: effective area of the section.
    l_ex, l_ey, l_ez: effective lengths of the member.
    r_x, r_y: radii of gyration.
    x_o, y_o: location of shear centre relative to the centroid.
    J: St Venant's torsion constant.
    I_w: the warping constant of the shape.
    f_y: the yield stress of the section.
    E: the elastic modulus.
    G: the shear modulus.
    sym: An object whose str method returns one of the following:
        'Double', 'Single', 'Point' or 'None'
        Ideally an object of the 'Symmetry' class or its subclasses.
    uncertainty_factor: an additional uncertainty factor as required
        by AS4100 S6.3.3. Default is 0.85.

    Returns a dictionary with N_cz and a number of intermediate results.
    To return only N_cz use result_vals["N_cz"].
    '''

    #first calculate some required section properties
    A_e = s6_2_A_e(A_n, k_f)

    if sym.symmetry == 'Double':
        '''
        Note: AS4100 does not require torsion tests for doubly symmetric
        shapes. this is potentially conservative, although it is expected
        that in most cases torsional buckling does not govern for doubly
        symmetric sections.
        '''
        
        results = f_oc_double_symmetric(A_n, l_ex, l_ez, r_x, r_y, x_o, y_o,
                                        J, I_w, E, G, sym)
    elif sym.symmetry == 'Single':
        results = f_oc_single_symmetric(A_n, l_ex, l_ey, l_ez, r_x, r_y, x_o,
                                        y_o, J, I_w, E, G, sym)
    elif sym.symmetry == 'Point':
        results = f_oc_point_symmetric(A_n, l_ez, r_x, r_y, x_o, y_o, J, I_w,
                                       E, G)
    elif sym.symmetry == 'None':
        results = f_oc_unsymmetric(A_n,l_ex, l_ey, l_ez, r_x, r_y, x_o, y_o,
                                   J, I_w, E, G)
    else:
        raise ValueError("Error in AS4600 buckling stress check. " + 
                            "Expected a symmetry type")

    f_oc = results["f_oc"]
    λ_c = (f_y / f_oc)**0.5
    f_n = 0.0

    if λ_c <= 1.5:
        f_n = f_y * (0.658**(λ_c * λ_c))
    else:
        f_n = f_y * (0.877 / (λ_c * λ_c))

    N_cz = uncertainty_factor * A_e * f_n

    #this is the return value from the function
    final_results = {"N_cz": N_cz}

    #add all the intermediate results to the final results so we have them
    final_results['Intermediate'] = results["Intermediate"]

    #add some other results to the intermediate results
    final_results["Intermediate"].update({"f_oc": f_oc, "λ_c": λ_c,
                                            "f_n": f_n})

    return final_results

#end member torsion capacity methods - AS4600
#endregion

#member capacity methods
#region

def s6_1_1_Nc(A_n, k_f, l, k_ex, k_ey, k_ez, r_x, r_y, x_o, y_o, J, I_w, f_y,
              E, G, sym = Symmetry(), f_ref=250e6, α_b=1.0,
              uncertainty_factor = 0.85, φ = 0.9, calc_buckling = True,
              calc_torsion = True):
    '''
    This method is intended to provide a "one stop shop" method for the
    AS4100 S6 checks. All calculations within the scope of AS4100 S6 are
    intended to be included, with the exception of those that relate to section
    properties (including k_f, which is considered to be a section property,
    not a compression property) or member properties (i.e. length, effective
    length factors).

    A_n: net area of the section.
    k_f: the form factor of the section.
    l, k_ex, k_ey, k_ez: length & effective length factors of the member about
        the major axes (x,y) and the torsional axis (z).
    r_x, r_y: radii of gyration.
    x_o, y_o: location of shear centre relative to the centroid of the shape.
    J: St Venant's torsion constant.
    I_w: the warping constant of the shape.
    f_y: the yield stress of the section.
    E: the elastic modulus.
    G: the shear modulus.
    sym: An object whose str method returns one of the following: 'Double',
        'Single', 'Point' or 'None'.
    f_ref: the reference yield stress. Default is 250.
    α_b: the residual stress factor. Default is 1.0.
    uncertainty_factor: an additional uncertainty factor as required by
        AS4100 S6.3.3 for torsional buckling. Default is 0.85.
    φ: the capacity reduction factor. Default is 0.9.
    calc_buckling: if False buckling results are not calculated.
    calc_torsion: if False torsional values are not calculated.
    
    Returns a dictionary of results and intermediate values.
    '''

    A_e = s6_2_A_e(A_n, k_f) #calculate effective area, as required for calculations below

    N_s = s6_2_N_s(A_e, f_y)
    φN_s = φ * N_s

    results = {'N_s': N_s, 'φN_s': φN_s}
    
    results["N_s Intermediate"] = {"A_e": A_e, "A_n": A_n, "k_f": k_f,
                                   "f_y": f_y}

    N_c = N_s
    φN_c = φN_s

    #if buckling calculations required, do them.
    if calc_buckling == True: 
        l_ex = s6_3_2_l_e(l, k_ex)
        l_ey = s6_3_2_l_e(l, k_ey)

        N_cx_buckling = s6_3_3_N_c(A_n, k_f, l_ex, r_x, f_y, f_ref, α_b)
        N_cy_buckling = s6_3_3_N_c(A_n, k_f, l_ey, r_y, f_y, f_ref, α_b)

        N_cx = min(N_cx_buckling["N_c"], N_s)
        φN_cx = φ * N_cx
        N_cy = min(N_cy_buckling["N_c"], N_s)
        φN_cy = φ * N_cy

        results['N_cx'] = N_cx #add to dictionary
        results['N_cy'] = N_cy
        results['φN_cx'] = φN_cx
        results['φN_cy'] = φN_cy
        results["N_c Intermediate"] = {'f_ref': f_ref, 'α_b': α_b}
        results["N_cx Intermediate"] = N_cx_buckling["Intermediate"]
        results["N_cy Intermediate"] = N_cy_buckling["Intermediate"]

        #need to update the overall member capacity.
        N_c = min(N_c, N_cx, N_cy) 
        φN_c = min(φN_c, φN_cx, φN_cy)
    
    #calculate torsional capacity if required.
    if calc_buckling == True and calc_torsion == True: 
        l_ez = s6_3_2_l_e(l, k_ez)

        N_cz_results = s6_3_3_N_c_torsion(A_n, k_f, l_ex, l_ey, l_ez, r_x,
                                           r_y, x_o, y_o, J, I_w, f_y, E, G,
                                           sym, uncertainty_factor)

        results["N_cz Intermediate"] = N_cz_results["Intermediate"]
        
        N_cz_buckling = N_cz_results["N_cz"]

        results["N_cz Intermediate"].update({"N_cz_buckling": N_cz_buckling})

        #finally calculate the torsional buckling capacity
        N_cz = min(N_s, N_cz_buckling)
        φN_cz = φ * N_cz
        
        #append to the results dictionary
        results['N_cz'] = N_cz
        results['φN_cz'] = φN_cz

        #update N_c for the lowest capacity.
        N_c = min(N_c, N_cz) 
        φN_c = φ * N_c

    results['N_c'] = N_c
    results['φN_c'] = φN_c

    return results

#end member capacity methods
#endregion