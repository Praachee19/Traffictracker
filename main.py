import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.set_page_config(page_title="Tariff Tracker", layout="wide")

# ----------------------------------------------------------
# HEADER
# ----------------------------------------------------------
st.title("Tariff Tracker Dashboard")

st.write("Upload your retail dataset or use sample synthetic data.")


# ----------------------------------------------------------
# FILE UPLOAD
# ----------------------------------------------------------
uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

use_sample = st.sidebar.checkbox("Use sample data instead", value=False)


# ----------------------------------------------------------
# FUNCTION: CLEAN NUMERIC COLUMNS
# ----------------------------------------------------------
def clean_numeric(df, numeric_cols):
    for col in numeric_cols:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", "")
                .str.replace(" ", "")
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df[numeric_cols] = df[numeric_cols].fillna(0)
    return df


# ----------------------------------------------------------
# LOAD DATA
# ----------------------------------------------------------
if uploaded_file and not use_sample:
    df = pd.read_csv(uploaded_file)
    st.success("CSV uploaded successfully.")

else:
    st.warning("Using synthetic sample dataset.")
    
    # SAMPLE SYNTHETIC DATA
    np.random.seed(42)
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    years = [2023, 2024, 2025]

    def create_yearly_series(base, noise=0.15):
        return [base * (1 + np.random.randn()*noise) for _ in months]

    data = []
    for y in years:
        data.append(pd.DataFrame({
            "Month": months,
            "Year": y,
            "Production": create_yearly_series(900000 if y==2023 else 950000 if y==2024 else 1100000),
            "AvgPrice": create_yearly_series(65 if y==2023 else 67 if y==2024 else 72, noise=0.05),
            "Sellout": create_yearly_series(1000000 if y==2023 else 1200000 if y==2024 else 1450000)
        }))

    df = pd.concat(data)


# ----------------------------------------------------------
# FORCE NUMERIC COLUMNS
# ----------------------------------------------------------
numeric_cols = ["Production", "AvgPrice", "Sellout"]

df = clean_numeric(df, numeric_cols)

# Show dtypes for debugging
# st.write(df.dtypes)


# ----------------------------------------------------------
# SIDEBAR FILTERS
# ----------------------------------------------------------
st.sidebar.title("Filters")

time_view = st.sidebar.radio("Time Range", ["Week", "Month"])

regions = ["All Regions"]
if "Region" in df.columns:
    regions += sorted(df["Region"].dropna().unique())
region = st.sidebar.selectbox("Select Region", regions)

categories = ["All Categories"]
if "Category" in df.columns:
    categories += sorted(df["Category"].dropna().unique())
category = st.sidebar.selectbox("Select Category", categories)


# APPLY FILTERS
if region != "All Regions" and "Region" in df.columns:
    df = df[df["Region"] == region]

if category != "All Categories" and "Category" in df.columns:
    df = df[df["Category"] == category]


# ----------------------------------------------------------
# KPIs SECTION
# ----------------------------------------------------------
col1, col2, col3 = st.columns(3)
col1.metric("New product launches", "1.2M", "+25%")
col2.metric("Average discount %", "32%", "+9%")
col3.metric("Replenishment rate", "61.8%", "-1%")


# ----------------------------------------------------------
# PRODUCTION CHART
# ----------------------------------------------------------
st.subheader("How are tariffs impacting production?")

chart1 = (
    alt.Chart(df)
    .mark_line(point=True)
    .encode(
        x="Month:N",
        y=alt.Y("Production:Q", title="Production"),
        color="Year:N",
        tooltip=["Month", "Year", "Production"]
    )
    .properties(height=300)
)

st.altair_chart(chart1, use_container_width=True)


# ----------------------------------------------------------
# AVG PRICE CHART
# ----------------------------------------------------------
st.subheader("How are tariffs impacting pricing?")

chart2 = (
    alt.Chart(df)
    .mark_line(point=True)
    .encode(
        x="Month:N",
        y=alt.Y("AvgPrice:Q", title="Average Price"),
        color="Year:N",
        tooltip=["Month", "Year", "AvgPrice"]
    )
    .properties(height=300)
)

st.altair_chart(chart2, use_container_width=True)


# ----------------------------------------------------------
# SELLOUT CHART
# ----------------------------------------------------------
st.subheader("How are tariffs impacting sellouts?")

chart3 = (
    alt.Chart(df)
    .mark_line(point=True)
    .encode(
        x="Month:N",
        y=alt.Y("Sellout:Q", title="Sellout"),
        color="Year:N",
        tooltip=["Month", "Year", "Sellout"]
    )
    .properties(height=300)
)

st.altair_chart(chart3, use_container_width=True)


# ----------------------------------------------------------
# CATEGORY PRICING TABLE IF AVAILABLE
# ----------------------------------------------------------
if "Category" in df.columns and "AvgPrice" in df.columns:
    st.subheader("Category Pricing Overview")

    df_table = df.groupby("Category")[["AvgPrice"]].mean().reset_index()
    st.dataframe(df_table, use_container_width=True)
