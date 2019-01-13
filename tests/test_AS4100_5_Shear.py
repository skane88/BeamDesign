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
        usecols="B:AM",
    )

    return [(row.Index, row) for row in df.itertuples()]


def data_PFCs():

    df = pd.read_excel(
        r"Excel\AS4100_5_Shear Verification.xlsx",
        sheet_name="PFCs",
        index_col=0,
        usecols="B:AN",
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


def data_Welds():

    df = pd.read_excel(
        r"Excel\AS4100_5_Shear Verification.xlsx",
        sheet_name="Is",
        index_col=0,
        usecols="B:AL",
    )

    df = df.drop(df[df["Fabrication Type"] != "Welded"].index)

    return [(row.Index, row) for row in df.itertuples()]


def data_α_vma():

    df = pd.read_excel(
        r"Excel\AS4100_5_Shear Verification.xlsx",
        sheet_name="Non-Uniform Shear Factor",
        index_col=0,
        usecols="B:E",
    )

    return [(row.Index, row) for row in df.itertuples()]


def data_Boxes():

    df = pd.read_excel(
        r"Excel\AS4100_5_Shear Verification.xlsx",
        sheet_name="CustomBoxes",
        index_col=0,
        usecols="B:Z",
    )

    return [(row.Index, row) for row in df.itertuples()]


@pytest.mark.parametrize("name, data", data_Is() + data_PFCs() + data_Boxes())
def test_s5_11_4_V_w_Generic(name, data):

    Aw = data.Aw
    fy = data.fy_web

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


@pytest.mark.parametrize("name, data", data_Is() + data_PFCs() + data_Boxes())
def test_s5_11_5_α_v(name, data):

    d_p = data.d1
    t_w = data.tw
    f_y = data.fy_web

    expected = data.αv
    actual = S5_Shear.s5_11_5_α_v(d_p=d_p, t_w=t_w, f_y=f_y)

    assert isclose(expected, actual)  # use default isclose tolerance (rel_tol of 1e-9)


@pytest.mark.parametrize("name, data", data_α_vma())
def test_s5_11_3_α_vma(name, data):

    f_vm = data.fvm
    f_va = data.fva

    expected = data.αvma
    actual = S5_Shear.s5_11_3_α_vma(f_vm=f_vm, f_va=f_va)

    assert isclose(expected, actual)  # use default isclose tolerance (rel_tol of 1e-9)


@pytest.mark.parametrize("name, data", data_Welds())
def test_s5_11_4_V_w_Weld(name, data):

    v_w = data.vw
    Q = data.Qflange
    Ix = data.Ix

    expected = data.Vweld
    actual = S5_Shear.s5_11_4_V_w_Weld(v_w=v_w, Q=Q, I=Ix)

    assert isclose(expected, actual)  # use default isclose tolerance (rel_tol of 1e-9)


@pytest.mark.parametrize("name, data", data_Is() + data_PFCs())
def test_s5_11_4_V_w_Interface(name, data):

    tw = data.tw  # web side of interface
    fy = min(data.fy_web, data.fy_flange)
    Q = data.Qflange
    Ix = data.Ix

    expected = data.Vinterface
    actual = S5_Shear.s5_11_4_V_w_Interface(t_interface=tw, f_y_interface=fy, Q=Q, I=Ix)

    assert isclose(expected, actual)  # use default isclose tolerance


@pytest.mark.parametrize("name, data", data_Boxes())
def test_s5_11_4_V_w_Interface_2(name, data):

    tw = data.tw * 2

    fy = min(data.fy_flange, data.fy_web)

    Q = data.Qflange
    Ix = data.Ix

    expected = data.Vinterface

    actual = S5_Shear.s5_11_4_V_w_Interface(t_interface=tw, f_y_interface=fy, Q=Q, I=Ix)

    assert isclose(expected, actual)  # use default isclose tolerance
