import streamlit as st
import math
import time
import numpy as np
import pandas as pd

# Configurazione della pagina
st.set_page_config(
    page_title="COSMO-DEX // Quantum Quasicrystal Lab",
    page_icon="⚛️",
    layout="wide"
)

# Stile visivo personalizzato
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    </style>
""", unsafe_allow_html=True)

st.title("⚛️ COSMO-DEX // Aperiodic Quantum Laboratory")
st.markdown("Simulazione interattiva avanzata di reticoli aperiodici e fluttuazioni fasoniche in tempo reale.")

# Sidebar di controllo interattiva
st.sidebar.header("🎛️ Pannello di Controllo")
n_points = st.sidebar.slider("Nodi Quantistici", 100, 2000, 800, 50)
base_speed = st.sidebar.slider("Velocità Fluttuazione Fasonica", 0.0, 0.5, 0.05, 0.01)
noise_level = st.sidebar.slider("Interferenza di Fase", 0.0, 1.0, 0.2, 0.05)

# Stato della sessione per l'animazione continua
if 'phase' not in st.session_state:
    st.session_state.phase = 0.0
if 'running' not in st.session_state:
    st.session_state.running = False

col_btn1, col_btn2 = st.sidebar.columns(2)
if col_btn1.button("▶ Avvia Animazione"):
    st.session_state.running = True
if col_btn2.button("⏸ Pausa"):
    st.session_state.running = False

# Layout a schede per l'interfaccia
tab1, tab2, tab3 = st.tabs(["🌐 Matrice Spaziale", "📊 Telemetria Energetica", "⚙️ Protocollo Nodo"])

with tab1:
    chart_placeholder = st.empty()
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    
    with metric_col1:
        m1 = st.empty()
    with metric_col2:
        m2 = st.empty()
    with metric_col3:
        m3 = st.empty()

    # Loop di generazione dinamica dei punti basato su angolo aureo e fasoni
    PHI = (1 + 5 ** 0.5) / 2
    
    # Aggiornamento fase se l'animazione è attiva
    if st.session_state.running:
        st.session_state.phase += base_speed
        time.sleep(0.05)
        st.rerun()

    # Calcolo coordinate geometriche
    theta = np.arange(n_points) * 2.399963
    r = np.sqrt(np.arange(n_points)) * 0.15
    
    # Applicazione della modulazione fasonica dinamica
    x = r * np.cos(theta) + (math.sin(st.session_state.phase) * noise_level * np.sin(theta))
    y = r * np.sin(theta) + (math.cos(st.session_state.phase) * noise_level * np.cos(theta))
    
    df = pd.DataFrame({"x": x, "y": y, "valore": np.sin(theta + st.session_state.phase)})

    # Visualizzazione grafico avanzato con Streamlit
    with chart_placeholder.container():
        st.scatter_chart(df, x="x", y="y", color="valore", size=30, height=550, use_container_width=True)

    # Aggiornamento metriche in tempo reale
    m1.metric("Fase Fasonica Attuale", f"{st.session_state.phase:.2f} rad")
    m2.metric("Stato Rete", "SINCRONIZZATA" if st.session_state.running else "IN PAUSA")
    m3.metric("Costante di Struttura ($\phi$)", f"{PHI:.5f}")

with tab2:
    st.subheader("Analisi Spettrale del Reticolo")
    st.line_chart(np.sin(np.linspace(0, 20, 100) + st.session_state.phase))
    st.info("I picchi di interferenza mostrano la stabilità armonica della struttura aperiodica.")

with tab3:
    st.subheader("Configurazione di Sistema")
    st.json({
        "engine": "Naressi-Aperiodic-Core",
        "nodes_active": n_points,
        "phase_shift": st.session_state.phase,
        "security_level": "Encrypted-QKD"
    })
