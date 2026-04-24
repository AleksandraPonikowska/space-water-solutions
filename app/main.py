# this is purely vibe-coded and will be replaced with something better tomorow
# sleeping is cool

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="AquaRisk AI", page_icon="💧", layout="wide")

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

# --- MOCKUP DANYCH (Zastąp to swoimi tabelkami z API) ---
dates = pd.date_range(start="2025-11-01", periods=30, freq='D')
ndvi_values = 0.6 - (np.linspace(0, 0.3, 30)) + np.random.normal(0, 0.02, 30)
df = pd.DataFrame({"Data": dates, "NDVI": ndvi_values})

# --- GŁÓWNY PANEL ---
st.title(f"Raport Ryzyka Wodnego: {city}")
st.write(f"Ostatnia aktualizacja danych satelitarnych: **{dates[-1].strftime('%Y-%m-%d')}**")

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
    st.subheader("📍 Mapa Operacyjna (Sentinel-2)")
    # Tu możesz wstawić swoją mapę NDVI z matplotlib lub folium
    # Na mockupie generujemy losową "mapę"
    map_data = np.random.rand(50, 50)
    fig_map = px.imshow(map_data, color_continuous_scale='RdYlGn', title="Podgląd Stref Wegetacji")
    st.plotly_chart(fig_map, use_container_width=True)

with right_col:
    st.subheader("📈 Trend i Predykcja AI")
    fig_trend = go.Figure()
    # Historia
    fig_trend.add_trace(go.Scatter(x=df['Data'], y=df['NDVI'], name='Dane Historyczne', line=dict(color='blue', width=3)))
    # Predykcja (Mockup)
    future_dates = pd.date_range(start=dates[-1], periods=7, freq='D')
    future_ndvi = np.linspace(ndvi_values[-1], ndvi_values[-1]-0.1, 7)
    fig_trend.add_trace(go.Scatter(x=future_dates, y=future_ndvi, name='Predykcja AI (7 dni)', line=dict(color='red', dash='dash')))
    
    fig_trend.update_layout(yaxis_title="Wskaźnik Kondycji (NDVI/NDMI)", margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig_trend, use_container_width=True)

# 3. REKOMENDACJE I ALERTY GALILEO
st.divider()
st.subheader("🚨 Rekomendacje Systemowe")
if ndvi_values[-1] < 0.4:
    st.error("**ALERT KRYTYCZNY:** Wykryto drastyczny spadek wilgotności. System wysłał automatyczne powiadomienie do lokalnych jednostek zarządzania kryzysowego przez sieć Galileo.")
    st.write("- Sugerowane działanie: Intensywne nawadnianie strefy południowej.")
    st.write("- Przewidywany koszt strat w przypadku braku reakcji: **45,000 PLN**")
else:
    st.success("Warunki w normie. Brak zagrożenia suszą w najbliższych 7 dniach.")

# --- STOPKA ---
st.caption("AquaRisk AI | Cassini Hackathon 2026 | Powered by Copernicus & Galileo")