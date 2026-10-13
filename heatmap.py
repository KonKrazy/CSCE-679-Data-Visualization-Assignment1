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
    [0.0, "#053061"],
    [0.2, "#d1e5f0"],
    [0.4, "#fddbc7"],
    [0.6, "#f4a582"],
    [0.8, "#d6604d"],
    [1.0, "#67001f"],
]

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

# ============================================================
# Load data and preparation
# ============================================================

def load_temperature_data(filepath: str) -> pd.DataFrame:
    # Process the dataframe
    df = pd.read_csv(filepath, parse_dates=["date"])

    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day"] = df["date"].dt.day

    return df


def compute_monthly_aggregates(df: pd.DataFrame,
                               temp_col: str) -> pd.DataFrame:
    # Aggregate
    monthly = (
        df.groupby(["year", "month"])[temp_col]
          .agg(["max", "min"])
          .reset_index()
    )

    return monthly


def pivot_monthly_matrix(monthly_df: pd.DataFrame,
                         value_col: str) -> pd.DataFrame:
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

# ============================================================
# LEVEL 1
# ============================================================

def build_level1_figure(max_matrix: pd.DataFrame,
                        min_matrix: pd.DataFrame) -> go.Figure:

    # Extract labels
    years = max_matrix.index.tolist()
    months = max_matrix.columns.tolist()
    month_labels = [MONTH_NAMES[m - 1] for m in months]

    # Flatten matrices for plotting
    z_max = max_matrix.values
    z_min = min_matrix.values

    # Shared color axis range
    zmin = np.nanmin([np.nanmin(z_max), np.nanmin(z_min)])
    zmax = np.nanmax([np.nanmax(z_max), np.nanmax(z_min)])

    fig = go.Figure()

    # Trace max temperature
    fig.add_trace(go.Heatmap(
        z=z_max,
        x=years,
        y=month_labels,
        colorscale=TEMP_COLORSCALE,
        zmin=zmin,
        zmax=zmax,
        colorbar=dict(title="Temperature (°C)"),
        hovertemplate=(
            "Date: %{x}-%{y}<br>"
            "Max Temp: %{z}°C<extra></extra>"
        ),
        name="Max Temperature",
    ))

    # Trace min temperature
    fig.add_trace(go.Heatmap(
        z=z_min,
        x=years,
        y=month_labels,
        colorscale=TEMP_COLORSCALE,
        zmin=zmin,
        zmax=zmax,
        showscale=False,
        hovertemplate=(
            "Date: %{x}-%{y}<br>"
            "Min Temp: %{z}°C<extra></extra>"
        ),
        name="Min Temperature",
        visible=False,
    ))

    # Create a dropdown for min/max toggle
    fig.update_layout(
        updatemenus=[dict(
            type="dropdown",
            direction="down",
            buttons=[
                dict(label="Max Temperature",
                     method="update",
                     args=[{"visible": [True, False]}]),
                dict(label="Min Temperature",
                     method="update",
                     args=[{"visible": [False, True]}]),
            ],
            x=1.15,
            y=1.0,
            showactive=True,
        )],
        title="Hong Kong Monthly Temperature Heatmap (Level 1)",
        xaxis_title="Year",
        yaxis_title="Month",
        yaxis=dict(
            categoryorder="array",
            categoryarray=month_labels,
        ),
        height=700,
        width=1000,
    )

    return fig

# ============================================================
# LEVEL 2
# ============================================================

def build_level2_figure(df: pd.DataFrame) -> go.Figure:
    # Filter to the target years (10 year duration)
    df_l2 = df[(df["year"] >= LEVEL2_START_YEAR) &
               (df["year"] <= LEVEL2_END_YEAR)].copy()

    years = sorted(df_l2["year"].unique())
    months = list(range(1, 13))
    month_labels = MONTH_NAMES

    # Compute monthly averages for the heatmap background color
    monthly_avg = (
        df_l2.groupby(["year", "month"])["max_temperature"]
             .mean()
             .reset_index()
    )

    avg_matrix = monthly_avg.pivot(
        index="year", columns="month", values="max_temperature"
    )

    # Ensure all months present
    for m in months:
        # Replace values with nan if doesn't exist
        if m not in avg_matrix.columns:
            avg_matrix[m] = np.nan

    avg_matrix = avg_matrix[months]

    # Create subplot grid
    n_rows = len(months)
    n_cols = len(years)

    fig = make_subplots(
        rows=n_rows,
        cols=n_cols,
        shared_xaxes=False,
        shared_yaxes=False,
        horizontal_spacing=0.02,
        vertical_spacing=0.02,
        subplot_titles=None,
    )

    # Color range for background heatmap
    zmin = np.nanmin(avg_matrix.values)
    zmax = np.nanmax(avg_matrix.values)
    daily_min = df_l2["min_temperature"].min()
    daily_max = df_l2["max_temperature"].max()

    # Add background heatmap
    for r, month in enumerate(months, start=1):
        for c, year in enumerate(years, start=1):
            val = avg_matrix.loc[year, month]
            fig.add_trace(
                go.Heatmap(
                    # Repeat the value at the corners so the background
                    # fills the same day/temperature space as the lines.
                    z=[[val, val], [val, val]],
                    x=[1, 31],
                    y=[daily_min, daily_max],
                    colorscale=TEMP_COLORSCALE,
                    zmin=zmin,
                    zmax=zmax,
                    showscale=(r == 1 and c == 1),
                    colorbar=dict(
                        title="Avg Max Temp (°C)",
                        len=0.5,
                        y=0.5,
                    ),
                    hoverinfo="skip",
                    showlegend=False,
                ),
                row=r, col=c,
            )

    # Add mini line charts
    for r, month in enumerate(months, start=1):
        for c, year in enumerate(years, start=1):
            cell_df = df_l2[
                (df_l2["year"] == year) & (df_l2["month"] == month)
            ].sort_values("day")

            if cell_df.empty:
                continue

            days = cell_df["day"].tolist()
            max_temps = cell_df["max_temperature"].tolist()
            min_temps = cell_df["min_temperature"].tolist()

            # Max temperature line
            fig.add_trace(
                go.Scatter(
                    x=days,
                    y=max_temps,
                    mode="lines",
                    line=dict(color="#2ca02c", width=1),
                    hovertemplate=(
                        f"Date: {year}-{month:02d}-%{{x}}<br>"
                        f"Max: %{{y}}°C<extra></extra>"
                    ),
                    showlegend=False,
                    name=f"{year}-{month:02d} Max",
                ),
                row=r, col=c,
            )

            # Min temperature line
            fig.add_trace(
                go.Scatter(
                    x=days,
                    y=min_temps,
                    mode="lines",
                    line=dict(color="#1f77b4", width=1),
                    hovertemplate=(
                        f"Date: {year}-{month:02d}-%{{x}}<br>"
                        f"Min: %{{y}}°C<extra></extra>"
                    ),
                    showlegend=False,
                    name=f"{year}-{month:02d} Min",
                ),
                row=r, col=c,
            )

    # Y axis label
    for r, month in enumerate(months, start=1):
        fig.update_yaxes(
            title_text=MONTH_NAMES[month - 1] if r == 1 else "",
            row=r, col=1,
            range=[daily_min, daily_max],
            showticklabels=(r == 1),
            ticks="",
        )

    # X axis label
    for c, year in enumerate(years, start=1):
        fig.update_xaxes(
            title_text=str(year),
            row=n_rows, col=c,
            range=[1, 31],
            showticklabels=True,
        )

    # Hide repeated ticks while keeping the outer labels readable.
    for r in range(1, n_rows + 1):
        for c in range(1, n_cols + 1):
            if r != n_rows:
                fig.update_xaxes(showticklabels=False, row=r, col=c)
            if c != 1:
                fig.update_yaxes(showticklabels=False, row=r, col=c)

    fig.update_layout(
        title="Hong Kong Daily Temperature Trends (Level 2)",
        height=900,
        width=1200,
        showlegend=False,
    )

    return fig


# ============================================================
# Main
# ============================================================

def main():
    df = load_temperature_data(DATA_FILE)

    # Level 1
    print("Building Level 1 figure:")
    monthly_max = compute_monthly_aggregates(df, "max_temperature")
    monthly_min = compute_monthly_aggregates(df, "min_temperature")

    max_matrix = pivot_monthly_matrix(monthly_max, "max")
    min_matrix = pivot_monthly_matrix(monthly_min, "min")

    fig1 = build_level1_figure(max_matrix, min_matrix)
    fig1.write_html(LEVEL1_OUTPUT)
    print(f"Saved Level 1 to {LEVEL1_OUTPUT}")

    # ---- Level 2 ----
    print("Building Level 2 figure:")
    fig2 = build_level2_figure(df)
    fig2.write_html(LEVEL2_OUTPUT)
    print(f"Saved Level 2 to {LEVEL2_OUTPUT}")


if __name__ == "__main__":
    main()