"""
HK Temperature Heatmap of Level 1 & 2
CSCE-679 Data Visualization Assignment 1
Kevin Nguyen

This script generates:
1. Level 1: Year/Month heatmap of monthly max/min temperature
2. Level 2: Year/Month heatmap with mini daily temperature line charts
"""

# ============================================================
# import dependencies
# ============================================================

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# ============================================================
# initialize variables
# ============================================================

DATA_FILE = "temperature_daily.csv"
LEVEL1_OUTPUT = "level1.html"
LEVEL2_OUTPUT = "level2.html"

# Level 2: focus on last 10 years
LEVEL2_START_YEAR = 2008
LEVEL2_END_YEAR = 2017

# calibrate scale for temperature in celsius
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