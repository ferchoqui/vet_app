# ---------------------------------------------
# IMPORT LIBRARIES
# ---------------------------------------------
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import json

from st_aggrid import AgGrid
from st_aggrid import GridOptionsBuilder

# ---------------------------------------------
# PAGE CONFIG (MUST BE FIRST STREAMLIT CALL)
# ---------------------------------------------
st.set_page_config(
    page_title="Vet Data Explorer",
    page_icon="🐾",
    layout="wide"
)

# ---------------------------------------------
# FUNCTIONS
# ---------------------------------------------
@st.cache_data
def load_data(file_path):
    return pd.read_csv(file_path)

def load_translations():
    with open("translations.json", "r", encoding="utf-8") as f:
        return json.load(f)

# ---------------------------------------------
# LOAD DATA
# ---------------------------------------------
vet_df = load_data("vet_app.csv")
translations = load_translations()
# ---------------------------------------------
# LANGUAGE MENU
# ---------------------------------------------

col1, col2 = st.columns([7,1])

with col2:
    language = st.selectbox(
        "",
        options=["ES", "EN"],
        format_func=lambda x: "🗽 English" if x == "EN" else "🏖️ Español",
        key="language_selector",
        label_visibility="collapsed"
    )

t = translations[language]

# Title
st.title(t["title"])

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([t["bar_chart"], t["pie_chart"], t["visits"], t["dataset"]])


# ---------------------------------------------
# TAB 1: BART CHART
# ---------------------------------------------

with tab1:
    st.subheader(t["bar_chart"])
    
    col1, col2 = st.columns(2)

    with col1:
        content_type = st.radio(
            t["content_phrase"],
            [t["breed"], t["color"]],
            key="content_filter"
        )

    with col2:
        measurements_variable = st.radio(
            t["variable_phrase"],
            [t["weight"], t["height"]],
            key="variable_filter"
        )

    # --- Select grouping column ---
    if content_type == t["breed"]:
        group_col = "breed"
        x_label = t["breed"]
    else:
        group_col = "color"
        x_label = t["color"]

        
    # --- Select metric column ---
    if measurements_variable == t["weight"]:
        value_col = "weight_kg"
        y_label = t["weight"]
    else:
        value_col = "height_cm"
        y_label = t["height"]

    # --- Aggregation (THIS is the key part) ---
    grouped_df = (
        vet_df
        .groupby(group_col)[value_col]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        grouped_df,
        x=group_col,
        y=value_col,
        color=value_col,
        title=f"{y_label} / {x_label}",
        text_auto=True,
        labels={
            "breed": t["breed"],
            "color": t["color"],
            "weight_kg": t["weight"],
            "height_cm": t["height"]
        }
    )

    st.plotly_chart(fig, width='stretch')


# ---------------------------------------------
# TAB 2: PIE CHART
# ---------------------------------------------

with tab2:
    st.subheader(t["pie_chart"])
    
    col1, col2 = st.columns([6,2])
    
    with col1:
        breed_list = sorted(vet_df["breed"].dropna().unique())

        selected_breed = st.selectbox(
            t["select"],
            breed_list,
            key="breed_selector_single"
        )

    with col2:
        measurements_variable_2 = st.radio(
            t["variable_phrase"],
            [t["weight"], t["height"]],
            key="variable_filter_2"
        )

    # --- Filter ---
    filtered_df = vet_df[vet_df["breed"] == selected_breed]

    # --- Select metric ---
    if measurements_variable_2 == t["weight"]:
        value_col = "weight_kg"
        value_label = t["weight"]
    else:
        value_col = "height_cm"
        value_label = t["height"]

    # --- Group by color ---
    grouped_df = (
        filtered_df
        .groupby("color")[value_col]
        .mean()
        .reset_index()
    )

    # --- Select the colors ---
    color_map = {
        "black": "black",
        "brown": "brown",
        "gray": "gray",
        "tan": "#D2B48C",   # tan doesn't exist as a named color in Plotly
        "white": "lightgray"  # pure white is invisible on white background
    }
    
    grouped_df["color_label"] = grouped_df["color"].map(t)

    fig = px.pie(
        grouped_df,
        names="color_label",
        values=value_col,
        title=f"{t['average']} {value_label}",
        hole=0.4,  # donut style (optional but nicer)
        color="color",  # IMPORTANT,
        color_discrete_map=color_map
    )

    st.plotly_chart(fig, width='stretch')


# ---------------------------------------------
# TAB 3: Visits
# ---------------------------------------------
with tab3:
    st.subheader(t["bar_chart"])

    vet_df["date"] = pd.to_datetime(vet_df["date"], format="%d-%m-%y")
    vet_df["year"] = vet_df["date"].dt.year
    df_year = vet_df.groupby("year").size().reset_index(name="count")


    fig = px.bar(
        df_year,
        x="year",
        y="count",
        color="count",
        labels={
            "year": t["year"],
            "count": t["visits"]
        },
        title=t["visits_phrase"]
    )
 
    st.plotly_chart(fig, width='stretch')


# ---------------------------------------------
# TAB 4: DATASET
# ---------------------------------------------
with tab4:
    st.subheader(t["dataset_phrase"])

    gb = GridOptionsBuilder.from_dataframe(vet_df)
    gb.configure_default_column(
        filter=True,
        sortable=True,
        resizable=True
    )

    gridOptions = gb.build()

    AgGrid(
        vet_df,
        gridOptions=gridOptions,
        height=500
    )
