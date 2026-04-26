# this is purely vibe-coded and will be replaced with something better tomorow
# sleeping is cool

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

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="AquaRisk AI", page_icon="💧", layout="wide")


# --- DANE ie ruszac
dates = pd.read_csv('./data/wroclaw_small/clean.csv'); #zwraca obiekt dataframe
#dates.interpolate("linear",0) #przyda sie po zmianie na mniej czyste dane
del dates['NDVI']
del dates['NDWI']
ndvi_values = [1,2]
sektor = "S_1"
dzien = "2025-07-01"


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

# nie ruszac
# --- CSS dla lepszego wyglądu (Hackathon Style) ---
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR (Nawigacja) ---
st.sidebar.title("💧 AquaRisk AI")
st.sidebar.subheader("System Wczesnego Ostrzegania")
city = st.sidebar.selectbox("Wybierz Region", ["Wrocław", "Warszawa", "Poznań", "Gdańsk"])
st.sidebar.divider()
st.sidebar.info("Używamy danych Copernicus Sentinel-2 oraz Sentinel-1 (Radar SAR) do monitorowania wilgotności gleby.")




# --- GŁÓWNY PANEL ---
st.title(f"Raport Ryzyka Wodnego: {city}")
#st.write(f"Ostatnia aktualizacja danych satelitarnych: **{dates[-1].strftime('%Y-%m-%d')}**")

# 1. METRYKI (Kluczowe wskaźniki)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Średnie NDVI", f"{ndvi_values[-1]:.2f}", "-5% vs poprz. tydzień")
with col2:
    st.metric("Wilgotność Gleby", "42%", "-12%", delta_color="inverse")
with col3:
    st.metric("Obszar Ryzyka", "18.5 ha", "Powiększa się")
with col4:
    st.metric("Status Systemu", "ALARM", delta_color="off")

st.divider()

# 2. MAPA I WYKRES TRENDU
left_col, right_col = st.columns([1, 1])

with left_col: 
    #nie ruszac
    chart_data = dates[dates['Data']==dzien]
    dane=chart_data[chart_data['Sektor_ID']=="S_1"] 

    kw = {
        "line_cap": "round",
        "fill": True,
        "fill_opacity": 0.6,
        "weight": 2,
    }
    mapa = fl.Map([51.03,16.81],zoom_start = 10) #0,02 z kazdej strony
    for sektor in chart_data["Sektor_ID"]:
        dane = chart_data[chart_data["Sektor_ID"]==sektor]
        kolor = cm.LinearColormap(["red", "yellow", "green"], vmin = -1, vmax = 1)
        lwy_lon = dane["Lon"].iat[0]-0.01
        pwy_lon = dane["Lon"].iat[0]+0.01
        lwy_lat = dane["Lat"].iat[0]-0.01
        pwy_lat = dane["Lat"].iat[0]+0.01
        bounds = [(lwy_lat,lwy_lon),(pwy_lat,pwy_lon)]
        rect = fl.Rectangle( #od -1 do 1 duze git
            bounds = bounds,
            **kw,
            fill_color = kolor(dane["NDMI"].iat[0]),
            #tooltip = f"{sektor}: NDMI {dane['NDMI'].iat[0]:.2f}",
        )
        rect.add_to(mapa)
    kolor.caption = "Legenda"
    mapa.add_child(kolor)
    st_data = st_folium(mapa, returned_objects=["last_object_clicked", "last_clicked"])


with right_col:
    clicked = st_data["last_object_clicked"]
    center_lon, center_lat = compute_rect_center(clicked)

    if clicked and center_lon is not None and center_lat is not None:

        distances = np.sqrt((chart_data["Lon"] - center_lon) ** 2 + (chart_data["Lat"] - center_lat) ** 2)
        nearest_idx = distances.idxmin()
        selected_row = chart_data.loc[nearest_idx]

        selected_sector = selected_row["Sektor_ID"]
    else:
        st.info("Kliknij prostokąt na mapie")
        selected_sector = sektor

    st.subheader("📈 Trend i Predykcja AI")
    st.scatter_chart(dates[dates["Sektor_ID"] == selected_sector], x="Data", y="NDMI")
