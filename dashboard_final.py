import streamlit as st
import pandas as pd
import requests
import numpy as np
import plotly.express as px
import os

# Function to fetch exoplanet data from NASA Exoplanet Archive API
@st.cache_data
def fetch_exoplanet_data():
    url = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
    query = """
        SELECT pl_name,pl_bmasse,pl_rade,pl_orbper,st_spectype,discoverymethod,pl_orbsmax,pl_orbeccen,pl_eqt
        FROM ps
        WHERE pl_bmasse IS NOT NULL AND pl_rade IS NOT NULL
    """
    params = {
        "query": query,
        "format": "json"
    }
    try:
        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data)
        if df.empty:
            return pd.DataFrame()
        # Rename columns for clarity
        df.rename(columns={
            "pl_name": "Exoplanet Name",
            "pl_bmasse": "Mass (Earth Masses)",
            "pl_rade": "Radius (Earth Radii)",
            "pl_orbper": "Orbital Period (days)",
            "st_spectype": "Star Type",
            "discoverymethod": "Discovery Method",
            "pl_orbsmax": "Orbital Distance (AU)",
            "pl_orbeccen": "Eccentricity",
            "pl_eqt": "Equilibrium Temperature (K)"
        }, inplace=True)
        # Convert numeric columns to float, handle missing data
        numeric_cols = [
            "Mass (Earth Masses)", "Radius (Earth Radii)", "Orbital Period (days)",
            "Orbital Distance (AU)", "Eccentricity", "Equilibrium Temperature (K)"
        ]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        # Add Habitability Indicator: crude proxy, e.g., in habitable zone (0.95 < AU < 1.67) and temp 180-310K
        df["Habitability Indicator"] = np.where(
            (df["Orbital Distance (AU)"] > 0.95) &
            (df["Orbital Distance (AU)"] < 1.67) &
            (df["Equilibrium Temperature (K)"] > 180) &
            (df["Equilibrium Temperature (K)"] < 310),
            1, 0
        )
        # Set Habitability Indicator to NaN if either AU or Temp is missing
        df.loc[
            df["Orbital Distance (AU)"].isna() | df["Equilibrium Temperature (K)"].isna(),
            "Habitability Indicator"
        ] = np.nan
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

# Load data
exoplanets_df = fetch_exoplanet_data()

# If data is empty, show message
if exoplanets_df.empty:
    st.warning("No data available to display.")
    st.stop()

# Function to categorize exoplanets based on size and mass
def categorize_exoplanet(row):
    if pd.isnull(row["Radius (Earth Radii)"]) or pd.isnull(row["Mass (Earth Masses)"]):
        return "Unknown"
    radius = row["Radius (Earth Radii)"]
    mass = row["Mass (Earth Masses)"]
    if radius < 1.5 and mass < 5:
        return "Terrestrial"
    elif 1.5 <= radius <= 2.5 and 5 <= mass <= 10:
        return "Super-Earth"
    elif 2.5 < radius <= 6 and 10 < mass <= 100:
        return "Gas Giant"
    elif radius > 6:
        return "Large Gas Giant"
    else:
        return "Other"

# Add category column
exoplanets_df["Category"] = exoplanets_df.apply(categorize_exoplanet, axis=1)

# Streamlit App
st.title("Exoplanet Classification and Analysis Dashboard")
st.write("An interactive dashboard to explore, categorize, and understand exoplanets using NASA API data.")

# Sidebar filters
st.sidebar.header("Filters")
star_type_options = sorted([x for x in exoplanets_df["Star Type"].dropna().unique() if x != ""])
discovery_method_options = sorted([x for x in exoplanets_df["Discovery Method"].dropna().unique() if x != ""])
habitability_options = ["Habitable", "Non-Habitable", "Unknown"]

# Filter by Star Type
selected_star_type = st.sidebar.multiselect("Star Type", options=star_type_options, default=star_type_options)

# Filter by Discovery Method
selected_discovery_method = st.sidebar.multiselect("Discovery Method", options=discovery_method_options, default=discovery_method_options)

# Filter by Habitability
habitability_filter = st.sidebar.selectbox("Habitability", options=habitability_options, index=0)

# Apply filters
filtered_df = exoplanets_df[
    (exoplanets_df["Star Type"].isin(selected_star_type)) &
    (exoplanets_df["Discovery Method"].isin(selected_discovery_method))
]

# Habitability filter
if habitability_filter == "Habitable":
    filtered_df = filtered_df[filtered_df["Habitability Indicator"] == 1]
elif habitability_filter == "Non-Habitable":
    filtered_df = filtered_df[filtered_df["Habitability Indicator"] == 0]
elif habitability_filter == "Unknown":
    filtered_df = filtered_df[filtered_df["Habitability Indicator"].isna()]

# Summary statistics
st.header("Summary Statistics")
col1, col2, col3 = st.columns(3)

with col1:
    total_planets = len(filtered_df)
    st.metric("Total Exoplanets", total_planets)

with col2:
    if not filtered_df.empty:
        categories_counts = filtered_df["Category"].value_counts()
        most_common_category = categories_counts.idxmax() if not categories_counts.empty else "N/A"
        st.metric("Most Common Category", most_common_category)
    else:
        st.metric("Most Common Category", "N/A")

with col3:
    if not filtered_df.empty and filtered_df["Equilibrium Temperature (K)"].notnull().any():
        avg_temp = filtered_df["Equilibrium Temperature (K)"].mean()
        st.metric("Average Equilibrium Temp (K)", f"{avg_temp:.2f}")
    else:
        st.metric("Average Equilibrium Temp (K)", "N/A")

# Visualization: Radius vs Mass scatter plot
st.header("Radius vs. Mass of Exoplanets")
if not filtered_df.empty:
    fig_scatter = px.scatter(
        filtered_df,
        x="Radius (Earth Radii)",
        y="Mass (Earth Masses)",
        color="Category",
        hover_data=["Exoplanet Name", "Star Type", "Discovery Method", "Habitability Indicator"],
        title="Exoplanet Radius vs. Mass"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
else:
    st.info("No data available for scatter plot.")

# Visualization: Histogram of Orbital Periods
st.header("Distribution of Orbital Periods")
if not filtered_df.empty and filtered_df["Orbital Period (days)"].notnull().any():
    fig_hist = px.histogram(
        filtered_df,
        x="Orbital Period (days)",
        nbins=50,
        title="Orbital Period Distribution"
    )
    st.plotly_chart(fig_hist, use_container_width=True)
else:
    st.info("No data available for orbital period histogram.")

# Visualization: Pie chart of Discovery Methods
st.header("Discovery Methods Distribution")
if not filtered_df.empty and filtered_df["Discovery Method"].notnull().any():
    discovery_counts = filtered_df["Discovery Method"].value_counts()
    fig_pie = px.pie(
        values=discovery_counts.values,
        names=discovery_counts.index,
        title="Discovery Methods"
    )
    st.plotly_chart(fig_pie, use_container_width=True)
else:
    st.info("No data available for discovery methods pie chart.")

# Visualization: Habitability Indicator Map (Bar Chart)
st.header("Habitability Indicators")
if not filtered_df.empty and filtered_df["Habitability Indicator"].notnull().any():
    habitability_counts = filtered_df["Habitability Indicator"].value_counts(dropna=False)
    habitability_labels = {
        1: "Habitable",
        0: "Non-Habitable",
        np.nan: "Unknown"
    }
    index_labels = []
    for i in habitability_counts.index:
        if pd.isna(i):
            index_labels.append("Unknown")
        else:
            index_labels.append(habitability_labels.get(i, "Unknown"))
    fig_bar = px.bar(
        x=index_labels,
        y=habitability_counts.values,
        labels={"x": "Habitability", "y": "Number of Exoplanets"},
        title="Habitability Distribution"
    )
    st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.info("No data available for habitability bar chart.")

# Detailed Data Table
st.header("Filtered Exoplanet Data")
if not filtered_df.empty:
    st.dataframe(filtered_df.reset_index(drop=True))
else:
    st.info("No data available to display in table.")
