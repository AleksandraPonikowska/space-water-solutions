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

dates = pd.read_csv('./data/wroclaw/merged.csv'); #zwraca obiekt dataframe
dates_future = pd.read_csv('./data/wroclaw/forecast_1m.csv')

# Normalize forecast date column name if needed.
if 'Forecast_Date' in dates_future.columns and 'Data' not in dates_future.columns:
    dates_future = dates_future.rename(columns={'Forecast_Date': 'Data'})

# Remove any repeated header/description rows.
dates = dates[dates['Data'].astype(str).str.lower() != 'data']
dates_future = dates_future[dates_future['Data'].astype(str).str.lower() != 'data']

# Drop any metadata/description columns if present.
drop_cols = [col for col in dates.columns if 'opis' in col.lower() or 'description' in col.lower()]
dates = dates.drop(columns=drop_cols, errors='ignore')
if 'Data' in dates_future.columns:
    drop_cols_future = [col for col in dates_future.columns if 'opis' in col.lower() or 'description' in col.lower()]
    dates_future = dates_future.drop(columns=drop_cols_future, errors='ignore')

# Normalize historical dates and save last available date from merged.csv only.
dates['Data'] = pd.to_datetime(dates['Data']).dt.date
last_historical_date = dates['Data'].max()

# Normalize forecast dates as well.
if 'Data' in dates_future.columns:
    dates_future['Data'] = pd.to_datetime(dates_future['Data']).dt.date

# Stack current and future records vertically.
dates = pd.concat([dates, dates_future], ignore_index=True)

# Ensure date column is normalized for combined DataFrame.
dates['Data'] = pd.to_datetime(dates['Data']).dt.date
sektor = "S_1"
dzien = "2026-03-01"

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
    [data-testid="stRadio"] *,
    .stRadio * {
        color: #f0f2f6 !important;
    }
    .choice-text {
        color: #f0f2f6 !important;
    }
    </style>
    """, unsafe_allow_html=True)




options = ["WRI","NDWI", "NDVI", "NDMI"]
sidebar_col, main_col = st.columns([1.6, 5], gap=None)

with sidebar_col:
    with st.container(border=True):
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.title("SwS - Space Water Solutions")
        st.subheader("System Wczesnego Ostrzegania")

        city = st.selectbox(
            "Wybierz Region",
            ["Wrocław", "Warszawa", "Poznań", "Gdańsk"]
        )
        choice = st.radio("Wybierz wskaźnik", options, index=2)
        st.markdown(f'<span class="choice-text">Wybrany wskaźnik: {choice}</span>', unsafe_allow_html=True)
        selected_date = st.select_slider(
            "Wybierz datę",
            options=sorted(dates['Data'].unique()),
            value=pd.to_datetime(dzien).date(),
        )
        if selected_date > last_historical_date:
            st.markdown("<div style='color:#093560; font-weight:600;'>Wybrana data to prognozy (predictions).</div>", unsafe_allow_html=True)
        st.divider()

chart_data = dates[dates['Data'] == selected_date]

with main_col:
    city = "Wrocław"
    st.title(f"{city}")

    if chart_data.empty:
        st.warning(f"Brak danych dla daty {selected_date}")
        st.stop()

    kw = {
        "line_cap": "round",
        "fill": True,
        "fill_opacity": 0.6,
        "weight": 0,
    }
    current_values = chart_data[choice].dropna()
    
    if not current_values.empty:
        v_min = current_values.min()
        v_max = current_values.max()
        
        # Zabezpieczenie: jeśli wszystkie wartości są identyczne, 
        # sztucznie rozszerzamy zakres, żeby mapa się nie wykrzaczyła
        if v_min == v_max:
            v_min -= 0.1
            v_max += 0.1
    else:
        v_min, v_max = -1, 1

    # 2. Definiujemy palety kolorów (liniowe)
    palettes = {
        "NDVI": ["red", "yellow", "green"],
        "NDWI": ["#f7fbff", "#6baed6", "#084594"], # od jasnego do ciemnego błękitu
        "NDMI": ["#fff7fb", "#d0d1e6", "#016450"]  # wilgotność
    }
    
    # Wybieramy kolory dla aktualnego wskaźnika
    current_colors = palettes.get(choice, ["red", "yellow", "green"])

    # 3. Tworzymy liniową mapę kolorów z dynamicznym zakresem
    kolor = cm.LinearColormap(
        current_colors,
        vmin=v_min,
        vmax=v_max
    )

    mapa = fl.Map([51.03, 16.81], zoom_start=11)
    
    for sektor in chart_data["Sektor_ID"].unique():
        dane = chart_data[chart_data['Sektor_ID']==sektor]
        #kolor = cm.LinearColormap(["red", "yellow", "green"], vmin=-1, vmax=1)
        lwy_lon = dane["Lon"].iat[0]-0.01
        pwy_lon = dane["Lon"].iat[0]+0.01
        lwy_lat = dane["Lat"].iat[0]-0.01
        pwy_lat = dane["Lat"].iat[0]+0.01
        val = dane[choice].iat[0]
        bounds = [(lwy_lat, lwy_lon), (pwy_lat, pwy_lon)]
        rect = fl.Rectangle(
            bounds=bounds,
            **kw,
            fill_color=kolor(val),
            tooltip=fl.Tooltip(f"<b>Sektor:</b> {sektor}<br><b>{choice}:</b> {val:.4f}")
            #tooltip = f"{sektor}: {choice} {dane[choice].iat[0]:.2f}",
        )
        rect.add_to(mapa)
    kolor.caption = "Legenda"
    mapa.add_child(kolor)
    st_data = st_folium(mapa, width=900, height=650, returned_objects=["last_object_clicked", "last_clicked"])
    st.empty()

with sidebar_col:
        st.markdown("### Wykres")
        clicked = st_data.get("last_object_clicked") or st_data.get("last_clicked")
        center_lon, center_lat = compute_rect_center(clicked)

        if clicked and center_lon is not None and center_lat is not None:
            distances = np.sqrt((chart_data["Lon"] - center_lon) ** 2 + (chart_data["Lat"] - center_lat) ** 2)
            nearest_idx = distances.idxmin()
            selected_row = chart_data.loc[nearest_idx]
            selected_sector = selected_row["Sektor_ID"]
        else:
            selected_sector = sektor

        st.scatter_chart(dates[dates["Sektor_ID"] == selected_sector], x="Data", y=choice)

        st.divider()

        st.markdown("""
            <div class="custom-sidebar-box">
            <div class="custom-sidebar-box-title">Trend i Predykcja AI</div>
            <div class="custom-sidebar-box-text">Tutaj będzie wykres / predykcja AI</div>
            </div>
            """, unsafe_allow_html=True)

        trend_placeholder = st.empty()

        st.divider()



