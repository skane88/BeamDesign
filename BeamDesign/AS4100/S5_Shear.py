# -*- coding: utf-8 -*-

"""
This module calculates the capacity of a member in shear to AS4100 Section 5.

This section only calculates properties that are independent of loads -
properties dependent on other loads (i.e. moment & shear capacities in S5.12)
will be calculated in a dedicated combined actions module.

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

import math
from typing import List, Union, Dict, Any

from BeamDesign.SectionClasses.HollowCircleClass import HollowCircleClass

# shear capacity methods

# region

def s5_11_4_V_w_Generic(*, A_w: float, f_y: float,
                        shear_to_axial: float = 0.6) -> float:
    """
    Determines the shear yielding capacity of a flat web section to
    AS4100 S5.11.4.

    This method is assumed to be acceptable for determining the shear
    yielding capacity of any section except CHS sections. For example, S9.3
    gives an almost identical equation for the shear strength of a solid
    circular section (bolts) of 0.62 x f_u x A.

    However, allowances for non-uniform shear stress distributions should be
    made with the equation given in S5.11.3.

    :param A_w: the gross sectional area of the web in m². For hot rolled I &
        C sections it is acceptable to use the full depth of the section. For
        welded sections it is necessary to use only the web panel depth due
        to the discontinuity at the flange welds.
    :param f_y: the yield strength of the web section in Pa.
    :param shear_to_axial: the ratio of shear yield to ordinary axial yield
        stress. By default this is 0.6 as per AS4100, which appears to be an
        approximation of the the value 1 / √3 ≈ 0.577 ≈ 0.6.
    :return: The web shear yield strength in N.
    """

    #shear yield stress
    f_y_v = shear_to_axial * f_y

    return f_y_v * A_w

def s5_11_4_V_w_CHS(*, A_e: float, f_y: float,
                    shear_to_axial: float = 0.6,
                    CHS_shear_area: float = 0.6) -> float:
    """
    Determine the shear yielding capacity of a CHS section to AS4100 S5.11.4.

    :param A_e: The effective area of the section in m², allowing for holes
        in the section as per AS4100 S5.11.4. Normally the gross area of the
        section will be acceptable as holes are not often made into standard
        sized circular members.
    :param f_y: The yield strength of the CHS section in Pa.
    :param shear_to_axial: The ratio of shear yield to ordinary axial yield
        stress. By default this is 0.6 as per AS4100, which appears to be an
        approximation of the the value 1 / √3 ≈ 0.577 ≈ 0.6.
    :param CHS_shear_area: The proportion of the CHS active in shear. AS4100
        implicitly gives this value as 0.6, based on the fact that the shear
        capacity of a CHS is 0.36 x fy x A - the 0.36 includes the reduction of
        axial yield stress to shear yield stress of 0.6, leaving a factor of 0.6
        for the effective shear area of a CHS.
    :return: The shear yield strength of the section in N.
    """

    #Shear yield stress
    f_y_v = shear_to_axial * f_y

    return CHS_shear_area * f_y_v * A_e


def s5_11_4_V_w_multiple(*, A: Union[float, List[float]],
                         f_y: Union[float, List[float]],
                         d: Union[float, List[float]],
                         t: Union[float, List[float]],
                         is_CHS: Union[bool, List[bool]],
                         shear_to_axial: float = 0.6,
                         CHS_shear_area: float = 0.6):
    """
    This method calculates the shear yield capacity of multiple shear elements
    based on AS4100 S5.11.4.

    This method only calculates the yield strength in uniform shear. The effect
    of buckling or non-uniform shear stress needs to be calculated separately.

    This method works on either single elements, with input provided as single
    float / bool values as appropriate, or on multiple elements with inputs
    as List[float], List[bool] as appropriate. If multiple elements are
    considered, the length of the lists must be the same.

    :param A: The shear area of the section in m², either A_w or A_e,
        depending on whether the section is a generic section or a CHS.

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
        [1.0, 2.0, 3.0, ..., n] to enable multiple elements to be entered,
        i.e. for the 2x webs in a box girder.

        This is entered separately from the panel depths & thicknesses to
        allow overriding the area (if say holes are present in the web)
        without overriding the buckling calculations.

        To calculate the area directly from the entered values, use -1.0
        for an elements area in A and the area will be directly calculated
        from the provided depth/diameter & thickness.
    :param f_y: The axial stress yield strength of the web section in Pa. This
        should be a single float or a List[float] where each element is the
        yield strength of a individual shear component (e.g. each web in a box
        section).
    :param d: This is the depth of the web panel in shear, or the diameter of
        the CHS element that in shear. Units in m.

        This parameter should either be a single float or a List[float].
    :param t: This is the thickness of the web panel in shear, or the thickness
        of the CHS element in shear. Units in m.

        This parameter should either be a single float or a List[float].
    :param is_CHS: Is the element a CHS?

        This parameter should either be a single bool or a List[bool].
    :param shear_to_axial: The ratio of shear yield to ordinary axial yield
        stress. By default this is 0.6 as per AS4100, which appears to be an
        approximation of the the value 1 / √3 ≈ 0.577 ≈ 0.6.
    :param CHS_shear_area: The proportion of the CHS active in shear. AS4100
        implicitly gives this value as 0.6, based on the fact that the shear
        capacity of a CHS is 0.36 x fy x A - the 0.36 includes the reduction of
        axial yield stress to shear yield stress of 0.6, leaving a factor of 0.6
        for the effective shear area of a CHS.
    :return: The shear yield strength of the section in N.
        This is returned in a dictionary with the following structure:

            {
                'V_y': shear yield strength (N)
                'Intermediate':
                    {
                        'f_y_min': minimum yield stress (Pa)
                    }
            }

        To allow for future use in a calculation report.
    """

    #first check that A, f_y, d, t & is_CHS are lists, or make them into lists:
    if type(A) == float:
        A = [A]
    if type(f_y) == float:
        f_y = [f_y]
    if type(d) == float:
        d = [d]
    if type(t) == float:
        t = [t]
    if type(is_CHS) == bool:
        is_CHS = [is_CHS]

    #next, check they are the same lengths:
    list_lens = [len(A), len(f_y), len(d), len(t), len(is_CHS)]

    if min(list_lens) != max(list_lens):
        #if the minimum & maximmum values are not the same, the list lengths are
        #different.

        raise ValueError("Expected that A, f_y, d, t & is_CHS are all the same"
                         + "length. Lengths are: A: " + str(len(A)) + ", f_y: "
                         + str(len(f_y)) + ", d:" + str(len(d)) + ", t:"
                         + str(len(t)) + ", is_CHS: " + str(len(is_CHS)))

    #determine the minimum shear yield strength
    f_y_min = min(f_y)

    #next calculate the yield strength

    #set the shear capacity to 0 by default.
    V_y = 0.0

    for Ai, di, ti, CHSi in zip(A, d, t, is_CHS):
        # Here we iterate through the lists of areas and calculate the yield
        # capacity of the section.

        if Ai >= 0.0:
            #if Ai is >= 0.0, then A_current is simply Ai

            A_current = Ai
        elif Ai == -1.0:
            #if Ai is == -1.0, then A has to be calculated

            if not CHSi:
                #if not a CHS, then the section is a simply rectangle.
                A_current = di * ti

            else:
                CHS = HollowCircleClass(0.0, 0.0, di / 2, (di - 2 * ti) / 2)
                A_current = CHS.area

        else:
            #if Ai is not >= 0.0 OR == -1.0, then Ai is an invalid number.
            raise ValueError("Expected area input A to be either >= 0.0 or "
                             + "== -1.0, current value is: " + str(Ai))

        #next need to calculate the shear capacity

        if not CHSi:
            #if not a CHS, use the generic shear capacity method

            V_current = s5_11_4_V_w_Generic(A_w=Ai, f_y=f_y_min,
                                            shear_to_axial=shear_to_axial)

        else:
            #else, need to use the CHS method

            V_current = s5_11_4_V_w_CHS(A_e=Ai, f_y=f_y_min,
                                        shear_to_axial=shear_to_axial)

        #finally, the shear capacity of the multiple sections is simply
        #the sum of the yield capacities

        V_y += V_current

    # create results dictionary with intermediate results
    results = {'V_y': V_y, 'Intermediate': {'f_y_min': f_y_min}}

    # NOTE: this yield capacity could be limited by welds or buckling.
    # these effects need to be calculated separately.

    return results

def s5_11_5_α_v(*, d_p: float, t_w: float, f_y: float,
                slenderness_limit: float = 82.0,
                f_y_ref: float = 250e6) -> float:
    """
    Determines the shear buckling coefficient α_v, which reduces the shear
    yielding load as per AS4100 section 5.11.5

    :param d_p: The web panel depth in m.
    :param t_w: The web thickness in m.
    :param f_y: The yield strength in Pa.
    :param slenderness_limit: The slenderness limit. By default this is 82.0,
        which is only valid for a web pin supported top and bottom.
        In some circumstances this value may be very unconservative (i.e.
        shear buckling of an angle leg supported on one side only) Refer to
        "The Behaviour and Design of Steel Structures to AS4100" by Trahair
        et al. for more information.
    :param f_y_ref: The reference yield stress in Pa, used in the slenderness
        limit equations. By default this is 250e6 Pa in line with AS4100.
    :return: Returns the shear buckling coefficient α_v. Note that this may be
        greater than 1.0 - the user of this function should ensure that the
        final shear capacity is limited to the shear yield capacity.
    """

    α_v = 0.0 #place holder for α_v

    if d_p / t_w > ((slenderness_limit) / ((f_y / f_y_ref ) **0.5)):
        α_v = ((slenderness_limit) / ((d_p / t_w ) *((f_y / f_y_ref ) **0.5)) ) **2

    return α_v

def s5_11_5_α_vMultiple(*, d_p: Union[List[float], float],
                        t_w: Union[List[float], float],
                        f_y: Union[List[float], float],
                        check_buckle: Union[List[bool], bool],
                        slenderness_limit: Union[List[float], float],
                        f_y_ref: float = 250e6):
    """
    Determines the shear buckling coefficient α_v, which reduces the shear
    yielding load as per AS4100 section 5.11.5.

    The minimum buckling coefficient from the collection of elements is
    returned, with the assumption being that buckling failure of one element
    will cause load to shed to other elements resulting in a progressive
    buckling failure of the section as a whole. This may not be accurate for
    a section with a very thin element that buckles first, where the remaining
    elements may have adequate capacity on their own.

    e.g. if a 500WC440 had a 2mm plate welded across each of its flanges (making
    a 3x web box section), it is clearly plausible that buckling failure of the
    2mm closing plates could occur very early (say an α_v << 0), but the central
    40mm web will have α_v >> 0. The total effect on strength of failure of the
    outer webs will be <10%, but the reported value of α_v will be much greater.

    The yield stress used to check each element is that of the particular
    element, not the minimum yield stress of the whole section. This is done
    because buckling is a pre-yield effect and therefore the yield strength
    still matters, not a plastic effect (where the actual yield strength matters
    less once plastification of the section as a whole occurs).

    If an element is included in the list that is not checked for buckling, the
    highest value of α_v that will be returned is 1.0 as it does not make sense
    to report a higher value. This implies that the buckling load will be the
    same as the yielding load.

    Elements that should not be checked for shear buckling include:

        * Elements that are unlikely to buckle due to their shape such as
            solid rounds, hexagons & squares.
        * Shapes that AS4100 does not provide any guidance on their shear
            buckling coefficients. These include flats not supported on both
            edges, CHS sections etc. However, if the user has some information
            on an appropriate shear buckling slenderness coefficient this could
            be explicitly entered. "The Behaviour and Design of Steel Structures
            to AS4100" by Trahair & Bradford provides guidance on determining
            apropriate buckling slenderness coefficients.

    Many of these shapes may either not be prone to shear buckling, or would be
    likely to buckle in other modes much earlier than in shear. For example,
    flats un-supported on any edge (simple rectangular section) seem intuitively
    likely to buckle about their minor axis or in flexural-torsional buckling at
    midspan before shear buckling in high shear regions at their ends occurs.
    CHS sections also seem unlikely to suffer from shear buckling due to the
    inherent resistance to buckling provided by their non-planar shape.

    :param d_p: The web panel depth in m. This should either be a single float
        or a List[float] if more than one element is being considered. If the
        section is not being checked for buckling, any value can be entered at
        the appropriate index in the list and will simply be ignored.

        The no. of elements in d_p, t_w, f_y, check_buckle and slenderness_limit
        must be the same.
    :param t_w: The web thickness in m. This should either be a single float
        or a List[float] if more than one element is being considered. If the
        section is not being checked for buckling, any value can be entered at
        the appropriate index in the list and will simply be ignored.

        The no. of elements in d_p, t_w, f_y, check_buckle and slenderness_limit
        must be the same.
    :param f_y: The yield strength in Pa for each element. This should either be
        a single float or a List[float] if more than one element is being
        considered. If the section is not being checked for buckling, any value
        can be entered at the appropriate index in the list and will simply be
        ignored.

        The no. of elements in d_p, t_w, f_y, check_buckle and slenderness_limit
        must be the same.
    :param check_buckle: Should the element be checked for buckling?
        If false, the highest value of α_v that will be returned is 1.0.
        This should be either a bool or a List[bool].

        The no. of elements in d_p, t_w, f_y, check_buckle and slenderness_limit
        must be the same.
    :param slenderness_limit: The slenderness limit. By default this is 82.0,
        which is only valid for a web pin supported top and bottom.
        In some circumstances this value may be very unconservative (i.e.
        shear buckling of an angle leg supported on one side only) Refer to
        "The Behaviour and Design of Steel Structures to AS4100" by Trahair &
        Bradford for more information.

        The no. of elements in d_p, t_w, f_y, check_buckle and slenderness_limit
        must be the same.
    :param f_y_ref: The reference yield stress in Pa, used in the slenderness
        limit equations. By default this is 250e6 Pa in line with AS4100.
    :return: Returns the shear buckling coefficient α_v. Note that this may be
        greater than 1.0 - the user of this function should ensure that the
        final shear capacity is limited to the shear yield capacity.

        This is returned as a dictionary with the following form:

        {

        'α_v': α_v,

        'Intermediate':
            {
            'Critical Element (α_v)':
                A list[int] of the critical elements, with each item in the list
                corresponding to the index of the critical elements in the entry
                lists. If no elements are checked (i.e. all
                check_buckle == False) the return is List[None].
            }
        }
    """

    #first check the input elements are lists, as they are checked based on
    #iterating through a list.

    if type(d_p) == float:
        d_p = [d_p]
    if type(t_w) == float:
        t_w = [t_w]
    if type(f_y) == float:
        f_y = [f_y]
    if type(check_buckle) == bool:
        check_buckle = [check_buckle]
    if type(slenderness_limit) == float:
        slenderness_limit = [slenderness_limit]

   # Next check the number of items in d_p, t_w, y_y and slenderness_limit are
   # the same.

    list_lens = [len(d_p), len(t_w), len(f_y), len(check_buckle),
                 len(slenderness_limit)]

    if max(list_lens) != min(list_lens):
        raise ValueError("Error calculating the buckling load parameter α_v"
                         + ", expected that the input lists d_p, t_w, f_y,"
                         + "is_CHS and slenderness_limit would be the same"
                         + " length. Lengths are: d_p: " + str(list_lens[0])
                         + ', t_w: ' +  str(list_lens[1]) + ', f_y: '
                         + str(list_lens[2]) + ", check_buckle: "
                         + str(list_lens[3]) + ' and slenderness_limit: '
                         + str(list_lens[4]) + '.')

    α_v = 0.0 #place holder
    critical_element = None #place holder

    if any(check_buckle):
        # for speed, check that there are at least some elements requiring
        # checking before going through the elements

        for d_pi, t_wi, f_yi, check_buckle_i, slenderness_limit_i, i \
            in zip(d_p, t_w, f_y, check_buckle, slenderness_limit, range(d_p)):

            # go through all the ranges to determine the values of α_v

            if check_buckle_i:
                #if buckling check is required, get α_v
                α_v_current = s5_11_5_α_v(d_p=d_pi, t_w=t_wi, f_y=f_yi,
                                          slenderness_limit=slenderness_limit_i)
            else:
                #if buckling is not checked, α_v = 1.0 is the assumption.
                α_v_current = 1.0

            #next check if α_v_current is the minimum:

            if i == 0:
                #if the first element in the list, α_v is simply α_v_current
                α_v = α_v_current
                critical_element = [i]
            else:
                if α_v_current < α_v:
                    #if α_v_current is < α_v, replace α_v and the critical
                    #element list
                    α_v = α_v_current
                    critical_element = [i]
                elif α_v_current == α_v:
                    #If α_v == α_v_current, add current element to the critical
                    #element list
                    critical_element.append(i)

    else:
        #if none of the elements required checking
        α_v = 1.0
        critical_element = [None]

    results = {
        'α_v': α_v,
        'Intermediate': {
            'Critical Element (α_v)': critical_element
            }
        }

    return results

def s5_11_3_Non_uniform_shear_factor(*, f_vm: float, f_va: float) -> float:
    """
    Determines the non-uniform shear modification factor as per
    AS4100 S5.11.3. This applies for sections such as PFCs, Mono-symmetric
    I sections, angle sections etc.

    :param f_vm: The maximum shear stress in the section from an elastic
        analysis. In Pa.
    :param f_va: The average shear stress in the section from an elastic
        analysis. In Pa.
    :return: Returns the non-uniform shear factor used to reduce the shear
        capacity for non-uniform members.
    """

    return min(2 / (0.9 + (f_vm / f_va)), 1.0)


def s5_11_2_V_v(A: Union[List[float], float], f_y: Union[List[float], float],
                d: Union[List[float], float], t: Union[List[float], float],
                is_CHS: Union[List[bool], bool],
                check_buckle: Union[List[bool], bool],
                slenderness_limit: Union[List[float], float],
                shear_to_axial: float = 0.6, CHS_shear_area: float = 0.6,
                f_y_ref: float = 250e6, is_uniform: bool = True,
                f_vm: float = 1.0, f_va: float = 1.0):
    """
    Determines the shear capacity of a section based on AS4100 S5.11.2-5.
    This is the shear capacity based on the web yield or buckling capacities
    only. Web stiffeners (S5.11.5.2) are NOT included in this calculation.

    Other methods are required to adjust this capacity based on weld capacity
    or shear interface capacity (i.e. web-flange joints).

    This method handles sections composed of multiple elements by allowing
    data to be entered as lists of elements.

    Yield strength is based on the minimum strength of any element in the
    section considered.

    Buckling capacity is determined using the yield strength of each element to
    identify the critical element. The resulting buckling factor α_v is based on
    the worst case buckling factor of any element in the section. The assumption
    is that buckling of one element will result in a progressive failure as
    other elements take up the shear and buckle in turn. This could be very
    conservative if there is an element in the section which is very slender
    compared to the other elements.

    :param A: The shear area of the section in m², either A_w or A_e,
        depending on whether the section is a generic section or a CHS.

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
        [1.0, 2.0, 3.0, ..., n] to enable multiple elements to be entered,
        i.e. for the 2x webs in a box girder.

        This is entered separately from the panel depths & thicknesses to
        allow overriding the area (if say holes are present in the web)
        without overriding the buckling calculations.

        To calculate the area directly from the entered values, use -1.0
        for an elements area in A and the area will be directly calculated
        from the provided depth/diameter & thickness.
    :param f_y: The axial stress yield strength of the web section in Pa. This
        should be a single float or a List[float] where each element is the
        yield strength of a individual shear component (e.g. each web in a box
        section).
    :param d: This is the depth of the web panel in shear, or the diameter of
        the CHS element that in shear. Units in m.

        This parameter should either be a single float or a List[float].
    :param t: This is the thickness of the web panel in shear, or the thickness
        of the CHS element in shear. Units in m.

        This parameter should either be a single float or a List[float].
    :param is_CHS: Is the element a CHS?

        This parameter should either be a single bool or a List[bool].
    :param check_buckle: Should the element be checked for buckling?
        If false, the highest value of α_v that will be returned is 1.0.

        This should be either a bool or a List[bool].
    :param slenderness_limit: The slenderness limit. By default this is 82.0,
        which is only valid for a web pin supported top and bottom.
        In some circumstances this value may be very unconservative (i.e.
        shear buckling of an angle leg supported on one side only) Refer to
        "The Behaviour and Design of Steel Structures to AS4100" by Trahair &
        Bradford for more information.
    :param shear_to_axial: The ratio of shear yield to ordinary axial yield
        stress. By default this is 0.6 as per AS4100, which appears to be an
        approximation of the the value 1 / √3 ≈ 0.577 ≈ 0.6.
    :param CHS_shear_area: The proportion of the CHS active in shear. AS4100
        implicitly gives this value as 0.6, based on the fact that the shear
        capacity of a CHS is 0.36 x fy x A - the 0.36 includes the reduction of
        axial yield stress to shear yield stress of 0.6, leaving a factor of 0.6
        for the effective shear area of a CHS.
    :param f_y_ref: The reference yield stress in Pa, used in the slenderness
        limit equations. By default this is 250e6 Pa in line with AS4100.
    :param is_uniform: Is the shear stress uniform or not?
    :param f_vm: The maximum shear stress in the section from an elastic
        analysis. In Pa.
    :param f_va: The average shear stress in the section from an elastic
        analysis. In Pa.
    :return: Returns a dictionary with the following information:

    {
        'V_y': The shear yield strength (N),

        'V_b': The shear buckling strength (N). Note that this may be greater
            than the yield strength - the user should ensure that they use the
            smaller value if required.,

        'V_w': The shear strength based on the lower of yield or buckling
            capacities (N).,

        'Intermediate':

        {
            'f_y_min': The minimum yield stress used in the calculations (Pa),

            'α_v': The critical buckling load factor.,

            'Critical Element (α_v)': A list of the elements which are critical
                for the buckling capacity.

        }
    }

    """

    #confirm that everything is in lists, as the methods used to determine
    #capacities depend on lists.
    if type(A) == float:
        A = [A]
    if type(f_y) == float:
        f_y = [f_y]
    if type(d) == float:
        d = [d]
    if type(t) == float:
        t = [t]
    if type(is_CHS) == bool:
        is_CHS = [is_CHS]
    if type(check_buckle) == bool:
        check_buckle = [check_buckle]
    if type(slenderness_limit) == float:
        slenderness_limit = [slenderness_limit]

    #test the input lists are the same lengths
    list_lens = [
        len(A),
        len(f_y),
        len(d),
        len(t),
        len(is_CHS),
        len(check_buckle),
        len(slenderness_limit)
        ]

    if max(list_lens) != min(list_lens):
        raise ValueError('Expected that the no. of items in each input list'
                         + ' would be the same. The no. of items in each list'
                         + ' is: A: ' + str(list_lens[0]) + ', f_y: '
                         + str(list_lens[1]) + ', d: ' + str(list_lens[2])
                         + ', t: ' + str(list_lens[3]) + ', is_CHS: '
                         + str(list_lens[4]) + ', check_buckle: '
                         + str(list_lens[5]) + ' and slenderness_limit: '
                         + str(list_lens[6]) + '.')

    #first determine the yield strength
    V_y_results = s5_11_4_V_w_multiple(A=A, f_y=f_y, d=d, t=t, is_CHS=is_CHS,
                                       shear_to_axial=shear_to_axial,
                                       CHS_shear_area=CHS_shear_area)

    V_y = V_y_results['V_y'] #actual yield strength

    #add to results dictionary
    results = {
        'V_y': V_y_results['V_y'],
        'Intermediate': V_y_results['Intermediate']
    }

    #next determine the buckling factor
    α_v_results = s5_11_5_α_vMultiple(d_p=d, t_w=t, f_y=f_y,
                                      check_buckle=check_buckle,
                                      slenderness_limit=slenderness_limit,
                                      f_y_ref=f_y_ref)

    α_v = α_v_results['α_v']

    #add to results dictionary
    results['Intermediate'].update(
        {
        'α_v': α_v_results['α_v']
        }
        )
    results['Intermediate'].update(α_v_results['Intermediate'])

    #determine the non-uniform shear factor

    uniform_shear_factor = 1.0  #by default

    if not is_uniform:
        uniform_shear_factor = s5_11_3_Non_uniform_shear_factor(f_vm=f_vm,
                                                                f_va=f_va)

    # update results
    results['Intermediate'].update(
        {
        'Uniform Shear Factor': uniform_shear_factor
            }
        )


    V_b = α_v * V_y * uniform_shear_factor #shear buckling capacity
    V_w = min(α_v, 1.0) * V_y * uniform_shear_factor #shear capacity

    results.update(
        {
            'V_b': V_b,
            'V_w': V_w
            }
        )

    return results

def s5_11_4_V_w_Weld(*, v_w: Union[List[float], float], Q: float,
                     I: float) -> float:
    """
    Calculates the capacity of section in shear according to AS4100 S5.11.4
    where the capacity is limited by a weld, as is the case with some welded
    I sections to AS3679.2.

    This is only intended to apply to regular sections (fabricated channel,
    I and box sections) where the webs share the shear stress equally. For
    irregular sections where the webs may share the shear stress in an
    un-equal manner this equation will not apply and further analysis will be
    required.

    NOTE: where welds are critical, the value of φ used with the results from
    this function should be the value of φ for the welds in question. Typically
    this is not the same as the value of φ for structural steel.

    :param v_w: The weld capacity connecting the element being considered
        (in N/m). This can be either a float, or if more than one weld is
        used, a List[float].
        I.e. for a welded I-beam with a weld either side of the web, you could
        supply either a single float: (v_w_LHS + v_w_RHS), or a list:
        [v_w_LHS, v_w_RHS].
    :param Q: The first moment of area of the connected component relative
        to the centroid of the section as a whole, in m³.
    :param I: The moment of area / inertia of the section as a whole, in m⁴.
    :return: Returns the shear capacity as limited by welds in N.
    """

    #first convert v_w to a list if required so that it can be summed

    if type(v_w) == float:
        v_w = [v_w]

    v_w = sum(v_w)  # get the sum of the capacity of the welds

    return v_w * I / Q

def s5_11_4_V_w_WeldMultiple(*, v_w: Union[List[float], List[List[float]]],
                             Q: List[float], I: float):
    """
    Calculates the capacity of section in shear according to AS4100 S5.11.4
    where the capacity is limited by a weld, as is the case with some welded
    I sections to AS3679.2.

    This method checks multiple welded interfaces and calculates the minimum
    shear capacity.

    This is only intended to apply to regular sections (fabricated channel,
    I and box sections) where the webs share the shear stress equally. For
    irregular sections where the webs may share the shear stress in an un-equal
    manner this equation will not apply and further analysis will be required.

    NOTE: where welds are critical, the value of φ used with the results from
    this function should be the value of φ for the welds in question. Typically
    this is not the same as the value of φ for structural steel.

    :param v_w: The weld capacity connecting the element being considered
        (in N/m). This should be either a List[float] where each item is the
        total weld capacity at an interface, or a List[List[float]] of the
        following format:

            [
                [weld capacities at interface 1],
                [weld capacities at interface 2],
                [weld capacities at interface ...],
                ...]
            ]

    :param Q: The first moment of area of the connected component relative to
        the centroid of the section as a whole, in m³. This should be a list of
        the Q values that act at each interface.

        Len(Q) must equal Len(v_w).
    :param I: The moment of area / inertia of the section as a whole, in m⁴.
    :return: Returns the shear capacity as limited by welds in N. Returns a
        dictionary with some intermediate results:

        {
            'V_weld': Minimum interface shear capacity (N),
            'Intermediate':
            {
                'Critical Welds': A list of the critical welds, corresponding to
                    the index of the interfaces in v_w and Q.
            }
        }
    """

    #first check that the length of v_w and Q are the same.

    if len(v_w) != len(Q):
        raise ValueError('Expected a list of matching weld capacities v_w and '
                         + 'first moments of area Q for each weld interface. '
                         + 'No. of interface in each list is not the same. '
                         + 'No. v_w: ' + str(len(v_w)) + ', no. Q: '
                         + str(len(Q)) + '.')

    #next go through all the interfaces
    V_w = 0.0
    critical_weld = None #place holder for critical element list

    for vwi, Qi, i in zip(v_w, Q, range(0, len(Q))):

        V_w_current = s5_11_4_V_w_Weld(v_w=vwi, Q=Qi, I=I)

        if i == 0:
            #if the first element, set V_w = V_w_current
            V_w = V_w_current
            critical_weld = [i]
        else:
            #else test if less than V_w
            if V_w_current < V_w:
                #Replace V_w & critical weld list
                V_w = V_w_current
                critical_weld = [i]
            elif V_w_current == V_w:
                #if V_w_current is the same as V_w, then update the critical
                #weld list
                critical_weld.append(i)

    #now that V_w is calculated, create return dictionary

    results = {'V_weld': V_w,
               'Intermediate': {
                   'Critical Welds': critical_weld
                   }
        }

    return results

def s5_11_4_V_w_Interface(*, t1: Union[List[float], float],
                          t2: Union[List[float], float], f_y_min: float,
                          Q: float, I: float,
                          shear_to_axial: float = 0.6) -> Dict:
    """
    Calculates the capacity of a section in shear based on local shear
    yielding of an interface such as the connection between a flange and a web.

    :param t2: A list or float of all the thicknesses of components on one side
        of the interface, with thicknesses in m.
    :param t2: A list or float of all the thicknesses of components on the other
        side of the interface, with thicknesses in m.
    :param f_y_min: The minimum yield strength of the connected parts in Pa.
        The minimum value is used because in most realistic structures there
        is little benefit gained in ultimate capacity from different yield
        strengths, as effects such as buckling tend to be more important.
    :param Q: The first moment of area of the connected component relative
        to the centroid of the section as a whole, in m³.
    :param I: The moment of area / inertia of the section as a whole, in m⁴.
    :param shear_to_axial: The ratio of shear yield stress to ordinary axial
        yield stress. By default this is 0.6 as per AS4100, which appears to be
        an approximation of the the value 1 / √3 ≈ 0.577 ≈ 0.6.
    :return: Returns the shear capacity as limited by interface shear of the
        connected components, in N.
        Results are returned as a dictionary for future use in a calculation
        report:

        {
            'V_w_interface': Strength (N),
            'Intermediate':
                {
                'min_t': 0 or 1
                }
        }

        The value of min_t is either 0 (if t1 is critical) or 1
        (if t2 is critical)
    """

    # if t1 or t2 are not lists make them into lists, so the sum function below
    # will work.
    if type(t1) == float:
        t1 = [t1]
    if type(t2) == float:
        t2 = [t2]

    t1 = sum(t1)
    t2 = sum(t2)

    if t1 < t2:
        t = t1
        results = {'Intermediate': {'min_t': 0}}
    else:
        t = t2
        results = {'Intermediate': {'min_t': 1}}

    f_y_v = f_y_min * shear_to_axial  # shear yield stress

    V_w = f_y_v * t * I / Q  # shear capacity of interface

    #Add the shear capacity into the results.
    results.update({'V_i': V_w})

    return results

def s5_11_4_V_w_InterfaceMultiple(*, t1: Union[List[float], List[List[float]]],
                                 t2: Union[List[float], List[List[float]]],
                                 Q: List[float],
                                 f_y1: Union[List[float], float],
                                 f_y2: Union[List[float], float],
                                 I: float, shear_to_axial: float = 0.6):
    """
    Calculates the capacity of a section in shear based on local shear
    yielding of an interface such as the connection between a flange and a web.

    This method handles multiple interfaces.

    :param t1: The thicknesses on one side of the interface being considered,
        in m. This can be one of the following inputs:

        List[float]: Where each interface consists of only 1x plate element, the
            interface thicknesses can be entered as a list of floats.
        List[List[float]]: Where each interface consists of multiple plate
            elements, the interface thickness can be entered as a list of a list
            of floats. E.g.:

            [
                [thicknesses of interface 1],
                [thicknesses of interface 2]
            ]

        The number of items at the top level of the list should be the same as
        the number of items in t2 and Q.
    :param t2: The thicknesses on the other side of the interface being
        considered, in m. This can be one of the following inputs:

        List[float]: Where each interface consists of only 1x plate element, the
            interface thicknesses can be entered as a list of floats.
        List[List[float]]: Where each interface consists of multiple plate
            elements, the interface thickness can be entered as a list of a list
            of floats. E.g.:

            [
                [thicknesses of interface 1],
                [thicknesses of interface 2]
            ]

        The number of items at the top level of the list should be the same as
        the number of items in t1 and Q.
    :param Q: The first moment of area of the connected component relative
        to the centroid of the section as a whole, in m³. This should be a
        List[float] with the Q value for each interface being considered.

        The number of items in the list should be the same as the number of
        items in t1 and t2.
    :param f_y1: The axial yield stress of the plate elements at the t1 side of,
        the interface, in Pa. If there are multiple yield strengths involved
        this can be entered as a List[float].

        The number of items in the list should be the same as the number of
        items in t1 and t2.
    :param f_y2: The axial yield stress of the plate elements at the t1 side of,
        the interface, in Pa. If there are multiple yield strengths involved
        this can be entered as a List[float].

        The number of items in the list should be the same as the number of
        items in t1 and t2.
    :param I: The moment of area / inertia of the section as a whole, in m⁴.
    :param shear_to_axial: The ratio of shear yield stress to ordinary axial
        yield stress. By default this is 0.6 as per AS4100, which appears to be
        an approximation of the the value 1 / √3 ≈ 0.577 ≈ 0.6.
    :return: Returns the minimum interface shear capacity in N. Returns a
        dictionary with the critical interfaces listed for future use.

        {
            'V_interface': Minimum interface shear capacity (N),

            'Intermediate':

                {
                    'Critical Interface': a List[int] with the index of the
                        critical interfaces (0 based). These correspond to the
                        items in t1, t2 & Q which give the critical interfaces.
                }
        }
    """

    #First check that things are lists:
    if type(t1) == float:
        t1 = [t1]
    if type(t2) == float:
        t2 = [t2]
    if type(Q) == float:
        Q = [Q]
    if type(f_y1) == float:
        f_y1 = [f_y1]
    if type(f_y2) == float:
        f_y2 = [f_y2]

    #Next check that t1, t2 and Q are the same length

    list_lens = [len(t1), len(t2), len(Q), len(f_y1), len(f_y2)]

    if max(list_lens) != min(list_lens):
        raise ValueError("Error checking interface shear capacity. Where there"
                         + " are multiple interfaces being considered the no."
                         + " of interfaces should be the same in list t1, t2,"
                         + " Q, f_y1 & f_y2. List lengths provided are t1: "
                         + str(list_lens[0]) + ", t2: " + str(list_lens[1])
                         + ", Q: " + str(list_lens[2]) + ", f_y1: "
                         + str(list_lens[3]) + " and f_y2: "
                         + str(list_lens[4]) + ".")

    #next go through the interfaces and determine the capacity for each one.

    V_i = 0.0 #default value
    critical_interface = None #place holder for the critical_interface variable

    for t1i, t2i, Qi, f_y1i, f_y2i, i in zip(t1, t2, Q, f_y1, f_y2,
                                             range(0, len(Q))):
        V_i_current = s5_11_4_V_w_Interface(t1=t1i, t2=t2i,
                                            f_y_min=min(f_y1i, f_y2i), Q=Qi,
                                            I=I,
                                            shear_to_axial=shear_to_axial)

        if i == 0:
            #if the first interface, by default V_i is the result.
            V_i = V_i_current
            critical_interface = [i]
        else:
            if V_i_current < V_i:
                #if V_i_current is < V_i, replace V_i and the critical interface
                #list.
                V_i = V_i_current
                critical_interface = [i]

            elif V_i_current == V_i:
                #If V_i_current == V_i, add the interface to the
                #critical_interface list.
                critical_interface.append(i)

    #now that V_i is calculated, generate return dictionary.

    results = {'V_interface': V_i,
               'Intermediate':
                    {'Critical Interface': critical_interface
                        }
        }

    return results

def s5_11_2_V_v(*, A: Union[List[float], float], f_y: Union[List[float], float],
                d: Union[List[float], float], t: Union[List[float], float],
                is_CHS: Union[List[bool], bool],
                check_buckle: Union[List[bool], bool],
                slenderness_limit: Union[List[float], float],
                v_w: Union[float, List[float]], Q: Union[List[float] ,float],
                t_i1: Union[List[float], float],
                t_i2: Union[List[float], float],
                f_y1: Union[List[float], float],
                f_y2: Union[List[float], float], I: float,
                shear_to_axial: float = 0.6, CHS_shear_area: float = 0.6,
                f_y_ref: float = 250e6, is_uniform: bool = True,
                f_vm: float = 1.0, f_va: float = 1.0, check_welds: bool = False,
                check_interface: bool = False, φ_steel: float = 0.9,
                φ_weld: float = 0.8):
    '''

    :param A: The shear area of the section in m², either A_w or A_e,
        depending on whether the section is a generic section or a CHS.

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
        [1.0, 2.0, 3.0, ..., n] to enable multiple elements to be entered,
        i.e. for the 2x webs in a box girder.

        This is entered separately from the panel depths & thicknesses to
        allow overriding the area (if say holes are present in the web)
        without overriding the buckling calculations.

        To calculate the area directly from the entered values, use -1.0
        for an elements area in A and the area will be directly calculated
        from the provided depth/diameter & thickness.
    :param f_y: The axial stress yield strength of the web section in Pa. This
        should be a single float or a List[float] where each element is the
        yield strength of a individual shear component (e.g. each web in a box
        section).
    :param d: This is the depth of the web panel in shear, or the diameter of
        the CHS element that in shear. Units in m.

        This parameter should either be a single float or a List[float].
    :param t: This is the thickness of the web panel in shear, or the thickness
        of the CHS element in shear. Units in m.

        This parameter should either be a single float or a List[float].
    :param is_CHS: Is the element a CHS?

        This parameter should either be a single bool or a List[bool].
    :param check_buckle: Should the element be checked for buckling?
        If false, the highest value of α_v that will be returned is 1.0.

        This should be either a bool or a List[bool].
    :param slenderness_limit: The slenderness limit. By default this is 82.0,
        which is only valid for a web pin supported top and bottom.
        In some circumstances this value may be very unconservative (i.e.
        shear buckling of an angle leg supported on one side only) Refer to
        "The Behaviour and Design of Steel Structures to AS4100" by Trahair &
        Bradford for more information.
    :param v_w: The weld capacity connecting the element being considered
        (in N/m). This should be either a List[float] where each item is the
        total weld capacity at an interface, or a List[List[float]] of the
        following format:

            [
                [weld capacities at interface 1],
                [weld capacities at interface 2],
                [weld capacities at interface ...],
                ...]
            ]

    :param Q: The first moment of area of the connected component relative to
        the centroid of the section as a whole, in m³. This should be a list of
        the Q values that act at each interface.

        Len(Q) must equal Len(v_w).
    :param t_i1: The thicknesses on one side of the interface being considered,
        in m. This can be one of the following inputs:

        List[float]: Where each interface consists of only 1x plate element, the
            interface thicknesses can be entered as a list of floats.
        List[List[float]]: Where each interface consists of multiple plate
            elements, the interface thickness can be entered as a list of a list
            of floats. E.g.:

            [
                [thicknesses of interface 1],
                [thicknesses of interface 2]
            ]

        The number of items at the top level of the list should be the same as
        the number of items in t2 and Q.
    :param t2: The thicknesses on the other side of the interface being
        considered, in m. This can be one of the following inputs:

        List[float]: Where each interface consists of only 1x plate element, the
            interface thicknesses can be entered as a list of floats.
        List[List[float]]: Where each interface consists of multiple plate
            elements, the interface thickness can be entered as a list of a list
            of floats. E.g.:

            [
                [thicknesses of interface 1],
                [thicknesses of interface 2]
            ]

        The number of items at the top level of the list should be the same as
        the number of items in t1 and Q.
    :param f_y1: The axial yield stress of the plate elements at the t1 side of,
        the interface, in Pa. If there are multiple yield strengths involved
        this can be entered as a List[float].

        The number of items in the list should be the same as the number of
        items in t1 and t2.
    :param f_y2: The axial yield stress of the plate elements at the t1 side of,
        the interface, in Pa. If there are multiple yield strengths involved
        this can be entered as a List[float].

        The number of items in the list should be the same as the number of
        items in t1 and t2.
    :param I: The moment of area / inertia of the section as a whole, in m⁴.
    :param shear_to_axial: The ratio of shear yield to ordinary axial yield
        stress. By default this is 0.6 as per AS4100, which appears to be an
        approximation of the the value 1 / √3 ≈ 0.577 ≈ 0.6.
    :param CHS_shear_area: The proportion of the CHS active in shear. AS4100
        implicitly gives this value as 0.6, based on the fact that the shear
        capacity of a CHS is 0.36 x fy x A - the 0.36 includes the reduction of
        axial yield stress to shear yield stress of 0.6, leaving a factor of 0.6
        for the effective shear area of a CHS.
    :param f_y_ref: The reference yield stress in Pa, used in the slenderness
        limit equations. By default this is 250e6 Pa in line with AS4100.
    :param is_uniform: Is the shear stress uniform or not?
    :param f_vm: The maximum shear stress in the section from an elastic
        analysis. In Pa.
    :param f_va: The average shear stress in the section from an elastic
        analysis. In Pa
    :param check_welds: Does the weld capacity need to be checked.
    :param check_interface: Does interface capacity need to be checked.
    :param φ_steel: The capacity reduction factor for steel.
    :param φ_weld: THe capacity reduction factor for welds.
    :return: Returns a dictionary with the following information:

        {
            'V_y': The shear yield strength (N).

            'V_b': The shear buckling strength (N). Note that this may be
            greater than the yield strength - the user should ensure that
            they use the smaller value if required.

            'V_w': The shear strength based on the lower of yield or buckling
            capacities (N).

            'V_weld': Minimum interface shear capacity (N). Only returned if
            check_weld = True.

            'V_interface': Minimum interface shear capacity (N). Only returned
            if check_interface = True.

            'Intermediate':
                {
                    'f_y_min' The minimum yield stress used in the calculations
                    (Pa).

                    'α_v' The critical buckling load factor.

                    'Critical Element (α_v)' A list of the elements which are
                    critical for the buckling capacity.

                    'Critical Welds' A list of the critical welds
                    corresponding to the index of the interfaces in v_w
                    and Q. Only returned if check_weld = True.

                    'Critical Interface' a list with the index of the critical
                    interfaces. Only returned if check_interface = True.
                }
        }

    '''

    # determine the member capacity.
    V_w_results = s5_11_2_V_v(A, f_y, d, t, is_CHS, check_buckle,
                              slenderness_limit, shear_to_axial, CHS_shear_area,
                              f_y_ref, is_uniform, f_vm, f_va)

    results = V_w_results
    results['φV_y'] = results['V_y'] * φ_steel
    results['φV_b'] = results['V_b'] * φ_steel
    results['φV_w'] = results['V_w'] * φ_steel

    if check_welds:
        #If welds need to be checked

        V_weld_results = s5_11_4_V_w_WeldMultiple(v_w=v_w, Q=Q, I=I)
        results['V_weld'] = V_weld_results['V_weld']
        results['φV_weld'] = V_weld_results['V_weld'] * φ_weld
        results['Intermediate'].update(V_weld_results['Intermediate'])

    if check_interface:
        # If interface needs to be checked.

        V_interface_results = s5_11_4_V_w_InterfaceMultiple(t1=t_i1, t2=t_i2,
                                                            Q=Q, f_y1=f_y1,
                                                            f_y2=f_y2, I=I,
                                                            shear_to_axial=shear_to_axial)

        results['V_interface'] = V_interface_results['V_interface']
        results['φV_interface'] = V_interface_results['V_interface'] * φ_steel
        results['Intermediate'].update(V_interface_results['Intermediate'])

    return results
