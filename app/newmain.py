from pathlib import Path
from PIL import Image


import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk
import plotly
import folium as fl
import branca.colormap as cm
from streamlit_folium import st_folium


def compute_rect_center(clicked):
    if not clicked:
        return None, None

    geometry = clicked.get("geometry") or {}
    coords = geometry.get("coordinates")
    if coords and len(coords) > 0 and len(coords[0]) > 0:
        ring = coords[0]
        lons = [point[0] for point in ring]
        lats = [point[1] for point in ring]
        return sum(lons) / len(lons), sum(lats) / len(lats)

    return clicked.get("lng"), clicked.get("lat")


# --- KONFIGURACJA STRONY ---
icon_path = "./assets/cozaikona.png"
icon = Image.open(icon_path)

dates = pd.read_csv('./data/wroclaw_small/clean.csv'); #zwraca obiekt dataframe
#dates.interpolate("linear",0) #przyda sie po zmianie na mniej czyste dane
del dates['NDVI']
del dates['NDWI']
ndvi_values = [1,2]
sektor = "S_1"
dzien = "2025-07-01"

st.set_page_config(
    page_title="SwS - Space Water Solutions",
    page_icon=icon,
    layout="wide"
)


# --- DANE ie ruszac
# dates = pd.read_csv('./data/wroclaw_clean_data.csv'); #zwraca obiekt dataframe
# #dates.interpolate("linear",0) #przyda sie po zmianie na mniej czyste dane
# del dates['NDVI']
# del dates['NDWI']
# ndvi_values = [1,2]
# sektor = "S_1"
# dzien = "2025-07-01"
# nie ruszac
# --- CSS dla lepszego wyglądu (Hackathon Style) ---


st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .custom-sidebar-box {
        background-color: #EEEBD3;
        border: 1px solid #594F41;
        border-radius: 14px;
        padding: 30px;
        margin-top: 10px;
        margin-bottom: 10px;
        min-height: 500px;
    }

    .custom-sidebar-box-title {
        color: #594F41;
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 18px;
    }

    .custom-sidebar-box-text {
        color: #093560;
        font-size: 16px;
        opacity: 0.75;
    }
    .stMetric { 
        background-color: #ffffff; 
        padding: 50px; 
        border-radius: 10px; 
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1); 
    }

    .block-container {
        padding-left: 0rem;
        padding-right: 0rem;
        padding-top: 0rem;
        padding-bottom: 0rem;
        max-width: 100%;
        height: 100vh;
        overflow: hidden;
    }

    [data-testid="stAppViewContainer"] {
        overflow: hidden;
    }

    [data-testid="stHorizontalBlock"] {
        gap: 0rem;
    }

    [data-testid="stHorizontalBlock"] > div:nth-child(1) {
        height: 100vh;
        overflow-y: auto;
        padding: 1rem;
        border-right: 1px solid #d9d9d9;
        background-color: #093560;
        }
        [data-testid="stHorizontalBlock"] > div:nth-child(1) h1,
        [data-testid="stHorizontalBlock"] > div:nth-child(1) h2,
        [data-testid="stHorizontalBlock"] > div:nth-child(1) h3,
        [data-testid="stHorizontalBlock"] > div:nth-child(1) label {
        color: #EEEBD3;
    }
    

    [data-testid="stHorizontalBlock"] > div:nth-child(2) {
        height: 100vh;
        overflow-y: auto;
        padding: 1.5rem;
        background-color: #f0f2f6;
    }
    </style>
    """, unsafe_allow_html=True)




chart_data = dates[dates['Data']==dzien]
dane = chart_data[chart_data['Sektor_ID']=="S_1"]

sidebar_col, main_col = st.columns([1.6, 5], gap=None)

with main_col:
    city = "Wrocław"
    st.title(f"{city}")

    kw = {
        "line_cap": "round",
        "fill": True,
        "fill_opacity": 0.6,
        "weight": 2,
    }
    mapa = fl.Map([51.03,16.81], zoom_start=10)
    for sektor in chart_data["Sektor_ID"]:
        dane = chart_data[chart_data['Sektor_ID']==sektor]
        kolor = cm.LinearColormap(["red", "yellow", "green"], vmin=-1, vmax=1)
        lwy_lon = dane["Lon"].iat[0]-0.01
        pwy_lon = dane["Lon"].iat[0]+0.01
        lwy_lat = dane["Lat"].iat[0]-0.01
        pwy_lat = dane["Lat"].iat[0]+0.01
        bounds = [(lwy_lat, lwy_lon), (pwy_lat, pwy_lon)]
        rect = fl.Rectangle(
            bounds=bounds,
            **kw,
            fill_color=kolor(dane["NDMI"].iat[0]),
            #tooltip = f"{sektor}: NDMI {dane['NDMI'].iat[0]:.2f}",
        )
        rect.add_to(mapa)
    kolor.caption = "Legenda"
    mapa.add_child(kolor)
    st_data = st_folium(mapa, width=900, height=650, returned_objects=["last_object_clicked", "last_clicked"])
    st.empty()

with sidebar_col:
    with st.container(border=True):
        st.title("SwS - Space Water Solutions")
        st.subheader("System Wczesnego Ostrzegania")

        city = st.selectbox(
            "Wybierz Region",
            ["Wrocław", "Warszawa", "Poznań", "Gdańsk"]
        )

        st.divider()

        st.markdown("### Wykres")
        clicked = st_data.get("last_object_clicked") or st_data.get("last_clicked")
        center_lon, center_lat = compute_rect_center(clicked)

        if clicked and center_lon is not None and center_lat is not None:
            distances = np.sqrt((chart_data["Lon"] - center_lon) ** 2 + (chart_data["Lat"] - center_lat) ** 2)
            nearest_idx = distances.idxmin()
            selected_row = chart_data.loc[nearest_idx]
            selected_sector = selected_row["Sektor_ID"]
        else:
            st.info("Kliknij prostokąt na mapie")
            selected_sector = sektor

        st.scatter_chart(dates[dates["Sektor_ID"] == selected_sector], x="Data", y="NDMI")

        st.divider()

        st.markdown("""
            <div class="custom-sidebar-box">
            <div class="custom-sidebar-box-title">Trend i Predykcja AI</div>
            <div class="custom-sidebar-box-text">Tutaj będzie wykres / predykcja AI</div>
            </div>
            """, unsafe_allow_html=True)

        trend_placeholder = st.empty()

        st.divider()



