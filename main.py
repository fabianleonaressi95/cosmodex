import streamlit as st
import math
import time
import numpy as np
import pandas as pd

# Configurazione della pagina
st.set_page_config(
    page_title="COSMO-DEX // Quantum Explorer",
    page_icon="⚛️",
    layout="wide"
)

# Stile visivo personalizzato: Estetica Olografica Cyber / Aperiodica
st.markdown("""
    <style>
    .stApp { background-color: #080c14; color: #f0f6fc; font-family: 'Courier New', Courier, monospace; }
    .main { background-color: #080c14; }
    
    /* Pannelli stile HUD */
    .hud-panel {
        background-color: #0e1420;
        border: 2px solid #1e506e;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.1);
        margin-bottom: 20px;
    }
    
    h1, h2, h3 { color: #00d4ff !important; font-family: 'Courier New', Courier, monospace; }
    
    /* Pulsanti personalizzati */
    .stButton>button {
        background-color: #0e1420;
        color: #00d4ff;
        border: 1px solid #00d4ff;
        border-radius: 4px;
        font-family: 'Courier New', Courier, monospace;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #00d4ff;
        color: #080c14;
    }
    </style>
""", unsafe_allow_html=True)

# Intestazione Olografica principale
st.markdown("""
    <div style="background-color: #0e1420; border: 2px solid #1e506e; padding: 15px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <h2 style="margin: 0; color: #00d4ff;">⚛️ COSMO-DEX // QUANTUM EXPLORER</h2>
        <span style="color: #00ff64; font-weight: bold; border: 1px solid #00ff64; padding: 4px 10px; border-radius: 4px;">SATELLITE SCANNER: ONLINE</span>
    </div>
""", unsafe_allow_html=True)

# Sidebar di controllo interattiva
st.sidebar.header("🎛️ Phason Control Vector")
n_points = st.sidebar.slider("Nodi Quantistici", 100, 2000, 800, 50)
base_speed = st.sidebar.slider("Velocità Fluttuazione", 0.0, 0.5, 0.05, 0.01)
noise_level = st.sidebar.slider("Interferenza di Fase (W1/L2)", 0.0, 1.0, 0.2, 0.05)

# Stato della sessione per l'animazione continua
if 'phase' not in st.session_state:
    st.session_state.phase = 0.0
if 'running' not in st.session_state:
    st.session_state.running = False

col_btn1, col_btn2 = st.sidebar.columns(2)
if col_btn1.button("▶ RUN"):
    st.session_state.running = True
if col_btn2.button("⏸ PAUSE"):
    st.session_state.running = False

# Layout a griglia principale (Simulazione dei pannelli dell'immagine)
col_left, col_center, col_right = st.columns([1.2, 2.2, 1.2])

PHI = (1 + 5 ** 0.5) / 2

# Aggiornamento fase se l'animazione è attiva
if st.session_state.running:
    st.session_state.phase += base_speed
    time.sleep(0.05)
    st.rerun()

# Calcolo coordinate geometriche aperiodiche
theta = np.arange(n_points) * 2.399963
r = np.sqrt(np.arange(n_points)) * 0.15
x = r * np.cos(theta) + (math.sin(st.session_state.phase) * noise_level * np.sin(theta))
y = r * np.sin(theta) + (math.cos(st.session_state.phase) * noise_level * np.cos(theta))
df = pd.DataFrame({"x": x, "y": y, "valore": np.sin(theta + st.session_state.phase)})

with col_left:
    st.markdown("""
        <div class="hud-panel">
            <h3>GALAXY MAP</h3>
            <p style="font-size: 12px; color: #8ab4f8;">Reticolo geometrico aperiodico attivo.</p>
        </div>
    """, unsafe_allow_html=True)
    st.metric("Fase Fasonica", f"{st.session_state.phase:.3f} rad")
    st.metric("Struttura ($\phi$)", f"{PHI:.5f}")

with col_center:
    st.markdown("""
        <div class="hud-panel">
            <h3>BRAGG SPECTRUM S(k)</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Grafico principale dei nodi quantistici
    st.scatter_chart(df, x="x", y="y", color="valore", size=25, height=380, use_container_width=True)

with col_right:
    st.markdown("""
        <div class="hud-panel">
            <h3>TELEMETRY</h3>
            <p style="font-size: 13px;">Stato Rete:</p>
        </div>
    """, unsafe_allow_html=True)
    
    status_text = "🟢 SINCRONIZZATA" if st.session_state.running in [True] else "🟡 IN PAUSA"
    st.info(f"Modalità: {status_text}")
    st.write(f"Nodi attivi: **{n_points}**")
    st.write(f"Errore L2: **{(noise_level * 0.1414):.4f}**")

# Mission Log in basso stile HUD
st.markdown("""
    <div class="hud-panel">
        <h3>MISSION LOG // SYSTEM STREAM</h3>
    </div>
""", unsafe_allow_html=True)

log_col1, log_col2, log_col3 = st.columns(3)
with log_col1:
    st.progress(min(int((st.session_state.phase % 10) * 10), 100), text="Analisi Spettrale W1")
with log_col2:
    st.progress(75, text="Stabilità Quasimorice")
with log_col3:
    st.progress(90, text="Crittografia QKD")
