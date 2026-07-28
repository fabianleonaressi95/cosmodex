import streamlit as st
import math
import numpy as np

# Configurazione della pagina Streamlit
st.set_page_config(
    page_title="COSMO-DEX // Quantum Quasicrystal Explorer",
    page_icon="✨",
    layout="wide"
)

# ---------------------------------------------------------------------------
# Generatore di quasicristalli / spirale aurea
# ---------------------------------------------------------------------------
PHI = (1 + 5 ** 0.5) / 2

def generate_quasicrystal(n_points=300, phason=0.0):
    pts_x = []
    pts_y = []
    for i in range(n_points):
        r = math.sqrt(i) * 0.1
        theta = i * 2.399963  # angolo aureo
        # Modulazione fasonica simulata
        shear_x = phason * 0.1 * math.sin(i)
        shear_y = -phason * 0.1 * math.cos(i)
        
        x = (r * math.cos(theta)) + shear_x
        y = (r * math.sin(theta)) + shear_y
        pts_x.append(x)
        pts_y.append(y)
    return pts_x, pts_y

# ---------------------------------------------------------------------------
# Interfaccia grafica (UI)
# ---------------------------------------------------------------------------
st.title("✨ COSMO-DEX // Quantum Quasicrystal Explorer")
st.markdown("Esplorazione interattiva dei reticoli aperiodici e simulazione fasonica.")

# Sidebar per i controlli
st.sidebar.header("Parametri di Simulazione")
n_points = st.sidebar.slider("Numero di nodi quantistici", 50, 1000, 300, 50)
phason_val = st.sidebar.slider("Vettore Fasonico", -5.0, 5.0, 0.0, 0.1)

# Generazione punti
x_pts, y_pts = generate_quasicrystal(n_points, phason_val)

# Visualizzazione grafico a dispersione con Streamlit (Nativo)
chart_data = {"x": x_pts, "y": y_pts}

col1, col2 = st.tabs(["Mappa Spaziale", "Informazioni Blockchain / Schema"])

with col1:
    st.subheader("Reticolo Quasicristallino in tempo reale")
    st.scatter_chart(chart_data, x="x", y="y", height=500, use_container_width=True)

with col2:
    st.subheader("Architettura Aperiodica e Stato Nodo")
    st.info("I dati telemetrici vengono validati sul registro locale aperiodico.")
    st.json({
        "status": "ONLINE",
        "phi_constant": PHI,
        "active_nodes": n_points,
        "phason_shift": phason_val,
        "consensus_engine": "Aperiodic-Proof-of-Symmetry"
    })
