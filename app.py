from pathlib import Path

import pandas as pd
import streamlit as st

DOSSIER = Path(__file__).parent / "donnees"

st.set_page_config(page_title="L'électricité dans 12 quartiers", page_icon="⚡", layout="wide")

st.title("L'électricité dans 12 quartiers")
st.caption("Relevés mensuels de janvier 2024 à décembre 2025. Données fictives.")

brut = pd.read_csv(DOSSIER / "consommation_brut.csv")
st.write(f"Le fichier brut compte {len(brut)} lignes.")
st.dataframe(brut.head(10), hide_index=True)

@st.cache_data
def chaje():
    return pd.read_csv("donnees/consommation_propre.csv")

done = chaje()

st.title("L'électricité dans 12 quartiers")
st.markdown(
    "Deux ans de relevés (2024 et 2025) pour 12 quartiers de Port-au-Prince, Delmas, "
    "Pétion-Ville et Cap-Haïtien. Question du directeur : **la consommation suit-elle "
    "la chaleur, ou les heures de courant ?**"
)

komin = sorted(done["commune"].unique())
ane = sorted(done["annee"].unique())
 
chwa_komin = st.sidebar.multiselect("komin", komin, default=komin)
chwa_ane = st.sidebar.selectbox("Année", ane, index=len(ane) - 1)
 
if not chwa_komin:
    st.warning("Choisissez au moins une commune dans la barre latérale.")
    st.stop()
 

deux_ans = done[done["commune"].isin(chwa_komin)]
df = deux_ans[deux_ans["annee"] == chwa_ane]
