"""
Contains tests for the shear calculation methods.
"""

from math import isclose

import pytest
import pandas as pd

import BeamDesign.Code_Check.AS4100.S5_Shear as S5_Shear


def data_Is():

    df = pd.read_excel(
        r"Excel\AS4100_5_Shear Verification.xlsx",
        sheet_name="Is",
        index_col=0,
        usecols="B:AF",
    )

    return [(row.Index, row) for row in df.itertuples()]


def data_PFCs():

    df = pd.read_excel(
        r"Excel\AS4100_5_Shear Verification.xlsx",
        sheet_name="PFCs",
        index_col=0,
        usecols="B:AI",
    )

    return [(row.Index, row) for row in df.itertuples()]


def data_CHSs():

    df = pd.read_excel(
        r"Excel\AS4100_5_Shear Verification.xlsx",
        sheet_name="CHSs",
        index_col=0,
        usecols="B:V",
    )

    return [(row.Index, row) for row in df.itertuples()]


@pytest.mark.parametrize("name, data", data_Is() + data_PFCs())
def test_s5_11_4_V_w_Generic(name, data):

    Aw = data.Aw
    fy = data.fy

    expected = data.Vyield
    actual = S5_Shear.s5_11_4_V_w_Generic(A_w=Aw, f_y=fy)

    assert isclose(expected, actual)  # use default isclose tolerance (rel_tol of 1e-9)


@pytest.mark.parametrize("name, data", data_CHSs())
def test_s5_11_4_V_w_CHS(name, data):

    Ae = data.Ag
    fy = data.fy

    expected = data.Vyield
    actual = S5_Shear.s5_11_4_V_w_CHS(A_e=Ae, f_y=fy)

    assert isclose(expected, actual)  # use default isclose tolerance (rel_tol of 1e-9)


@pytest.mark.parametrize("name, data", data_Is() + data_PFCs())
def test_s5_11_5_α_v(name, data):

    d_p = data.d1
    t_w = data.tw
    f_y = data.fy

    expected = data.αv
    actual = S5_Shear.s5_11_5_α_v(d_p=d_p, t_w=t_w, f_y=f_y)

    assert isclose(expected, actual)  # use default isclose tolerance (rel_tol of 1e-9)


def test_s5_11_3_Non_uniform_shear_factor():

    assert False


def test_s5_11_4_V_w_Weld():
    assert False


def test_s5_11_4_V_w_Interface():

    assert False
