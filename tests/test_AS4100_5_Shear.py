"""
Contains tests for the shear calculation methods.
"""

from math import isclose

import pytest
import pandas as pd

import BeamDesign.Code_Check.AS4100.S5_Shear as S5_Shear


def data_WB():

    df = pd.read_excel(
        r"Excel\AS4100_5_Shear Verification.xlsx",
        sheet_name="Welded Beams",
        index_col=0,
        usecols="B:AA",
    )

    return [(row.Index, row) for row in df.itertuples()]


@pytest.mark.parametrize("name, data", data_WB())
def test_s5_11_4_V_w_Generic(name, data):

    Aw = data.Aw
    fy = data.fy

    expected = data.φVyield
    actual = S5_Shear.s5_11_4_V_w_Generic(A_w=Aw, f_y=fy)

    assert isclose(expected, actual)


def test_s5_11_4_V_w_CHS():

    assert False


def test_s5_11_5_α_v():

    assert False


def test_s5_11_3_Non_uniform_shear_factor():

    assert False


def test_s5_11_4_V_w_Weld():
    assert False


def test_s5_11_4_V_w_Interface():

    assert False
