"""
Includes some utility functions for testing.
"""

import pandas as pd

def get_Is():

    df = pd.read_excel(
        r"Excel\AS4100 Verification.xlsx",
        sheet_name="Is",
        index_col=0,
        usecols="B:AU",
        skiprows = [0]
    )

    return [(row.Index, row) for row in df.itertuples()]


def get_PFCs():

    df = pd.read_excel(
        r"Excel\AS4100 Verification.xlsx",
        sheet_name="PFCs",
        index_col=0,
        usecols="B:AV",
        skiprows = [0]
    )

    return [(row.Index, row) for row in df.itertuples()]


def get_CHSs():

    df = pd.read_excel(
        r"Excel\AS4100 Verification.xlsx",
        sheet_name="CHSs",
        index_col=0,
        usecols="B:AD",
        skiprows = [0]
    )

    return [(row.Index, row) for row in df.itertuples()]


def get_Welds():

    df = pd.read_excel(
        r"Excel\AS4100 Verification.xlsx",
        sheet_name="Is",
        index_col=0,
        usecols="B:AU",
        skiprows = [0]
    )

    df = df.drop(df[df["Fabrication Type"] != "Welded"].index)

    return [(row.Index, row) for row in df.itertuples()]


def get_α_vma():

    df = pd.read_excel(
        r"Excel\AS4100 Verification.xlsx",
        sheet_name="Non-Uniform Shear Factor",
        index_col=0,
        usecols="B:E",
        skiprows = [0]
    )

    return [(row.Index, row) for row in df.itertuples()]


def get_Boxes():

    df = pd.read_excel(
        r"Excel\AS4100 Verification.xlsx",
        sheet_name="CustomBoxes",
        index_col=0,
        usecols="B:AH",
        skiprows = [0]
    )

    return [(row.Index, row) for row in df.itertuples()]

data_Is = get_Is()
data_PFCs = get_PFCs()
data_CHSs = get_CHSs()
data_Welds = get_Welds()
data_α_vma = get_α_vma()
data_Boxes = get_Boxes()
data_AllSections = data_Is + data_PFCs + data_CHSs + data_Boxes
