"""
HK Temperature Heatmap of Level 1 & 2
CSCE-679 Data Visualization Assignment 1
Kevin Nguyen

This script generates:
1. Level 1: Year/Month heatmap of monthly max/min temperature
2. Level 2: Year/Month heatmap with mini daily temperature line charts
"""

# ============================================================
# Import dependencies
# ============================================================

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# ============================================================
# Initialize variables
# ============================================================

DATA_FILE = "temperature_daily.csv"
LEVEL1_OUTPUT = "level1.html"
LEVEL2_OUTPUT = "level2.html"

# Level 2: focus on last 10 years
LEVEL2_START_YEAR = 2008
LEVEL2_END_YEAR = 2017

# Calibrate scale for temperature in celsius
TEMP_COLORSCALE = [
    [0.0, "#67001f"],  
    [0.2, "#d6604d"],
    [0.4, "#f4a582"],
    [0.6, "#fddbc7"],
    [0.8, "#d1e5f0"],
    [1.0, "#053061"], 
]

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

# ============================================================
# Load data and preparation
# ============================================================

def load_temperature_data(filepath: str) -> pd.DataFrame:
    """Load and parse the daily temperature csv file"""

    df = pd.read_csv(filepath, parse_dates=["date"])

    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day"] = df["date"].dt.day

    return df


def compute_monthly_aggregates(df: pd.DataFrame,
                               temp_col: str) -> pd.DataFrame:
    """
    Aggregate daily temperatures to monthly max/min values

    Args:
        df: Daily temperature DataFrame
        temp_col: Column name to aggregate

    Returns:
        DataFrame with columns ['year', 'month', temp_col]
    """
    monthly = (
        df.groupby(["year", "month"])[temp_col]
          .agg(["max", "min"])
          .reset_index()
    )

    return monthly


def pivot_monthly_matrix(monthly_df: pd.DataFrame,
                         value_col: str) -> pd.DataFrame:
    """
    Convert monthly data into a year x month matrix

    Args:
        monthly_df: DataFrame with ['year', 'month', value_col]
        value_col: Column to pivot

    Returns:
        DataFrame indexed by year, columns = months (1-12)
    """

    # Pivot columns
    matrix = monthly_df.pivot(
        index="year", columns="month", values=value_col
    )

    # Check that all 12 months exist
    for m in range(1, 13):
        # Fill with nan's if it doesn't exist
        if m not in matrix.columns:
            matrix[m] = np.nan

    return matrix[sorted(matrix.columns)]