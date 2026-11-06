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



k1, k2, k3 = st.columns(3)
k1.metric("Consommation totale", f"{df['kwh'].sum() / 1e6:.2f} millions de kWh")
k2.metric("Par abonné et par mois", f"{df['kwh_par_abonne'].mean():.1f} kWh")
k3.metric("Courant par jour", f"{df['heures_courant'].mean():.1f} heures")



onglets = st.tabs([
    "Qui consomme le plus ?",
    "Évolution",
    "Chaleur ou courant ?",
    "Coupures",
    "Relevés atypiques",
])
 
with onglets[0]:
    par_quartier = df.groupby("quartier")["kwh_par_abonne"].mean().round(1).sort_values(ascending=False)
    st.bar_chart(par_quartier)
    premier = par_quartier.index[0]
    st.write(
        f"En {chwa_ane}, **{premier}** consomme le plus par abonné "
        f"({par_quartier.iloc[0]} kWh par mois)."
    )
    par_type = df.groupby("type")["kwh_par_abonne"].mean().round(1)
    if {"Commercial", "Résidentiel"} <= set(par_type.index):
        st.write(
            f"Un abonné commercial consomme en moyenne {par_type['Commercial']} kWh par mois, "
            f"contre {par_type['Résidentiel']} pour un abonné résidentiel."
        )
 
with onglets[1]:
    courbe = deux_ans.groupby(["mois", "commune"]).agg(kwh=("kwh", "sum"), abonnes=("abonnes", "sum"))
    courbe["par_abonne"] = courbe["kwh"] / courbe["abonnes"]
    st.line_chart(courbe["par_abonne"].unstack("commune"))
    totaux = deux_ans.groupby("annee")["kwh"].sum()
    if 2024 in totaux.index and 2025 in totaux.index:
        hausse = (totaux[2025] / totaux[2024] - 1) * 100
        st.write(
            f"Pour les communes choisies, la consommation passe de {totaux[2024] / 1e6:.2f} "
            f"à {totaux[2025] / 1e6:.2f} millions de kWh entre 2024 et 2025 ({hausse:+.1f} %)."
        )
    st.caption(
        "Les deux années sont affichées. Sept des neuf relevés manquants sont en 2025 : "
        "les totaux 2025 sont un peu sous-estimés."
    )
 
with onglets[2]:
    res = deux_ans[deux_ans["type"] == "Résidentiel"]
    if len(res) < 3:
        st.info("Pas assez de quartiers résidentiels dans ce choix de communes.")
    else:
        st.scatter_chart(res, x="heures_courant", y="kwh_par_abonne")
        r_courant = res["kwh_par_abonne"].corr(res["heures_courant"])
        r_chaleur = res["kwh_par_abonne"].corr(res["temperature_c"])
        st.write(
            f"Quartiers résidentiels : la corrélation de la consommation par abonné est de "
            f"**{r_courant:.2f}** avec les heures de courant, et de **{r_chaleur:.2f}** avec la température."
        )
        st.caption("Les deux années sont affichées.")
 
with onglets[3]:
    mediane = df.groupby("commune")["heures_courant"].median().round(1)
    st.bar_chart(mediane)
    plus_basse = mediane.idxmin()
    faibles = df[df["heures_courant"] < 8]
    st.write(
        f"En {chwa_ane}, la médiane la plus basse est à **{plus_basse}** "
        f"({mediane.min()} heures de courant par jour). "
        f"{len(faibles)} relevé(s) ont moins de 8 heures de courant par jour."
    )
 
with onglets[4]:
    top = df.nlargest(3, "kwh")[["mois", "quartier", "type", "kwh"]]
    st.bar_chart(top.assign(releve=top["mois"] + " " + top["quartier"]).set_index("releve")["kwh"])
    if len(top):
        t = top.iloc[0]
        st.write(
            f"Le plus gros releve de {chwa_ane} est celui de **{t['quartier']}** en {t['mois']} "
            f"({t['kwh']:,} kWh).".replace(",", " ")
        )


st.subheader("Conclusion")
st.markdown(
    "**La consommation suit les heures de courant, pas la chaleur.** Chez les résidentiels, "
    "la corrélation avec les heures de courant est de 0,76 (de 0,84 à 0,97 quartier par quartier), "
    "contre -0,15 avec la température. Ce lien est en partie mécanique (sans courant, pas de "
    "consommation) et une corrélation ne dit pas ce qui cause quoi : un facteur commun, comme la "
    "qualité du réseau ou l'activité du quartier, pourrait jouer sur les deux. Elle ne dit pas non "
    "plus ce qui se passerait si l'on rallongeait les heures de courant."
)
 
with st.expander("Voir les données filtrées"):
    st.dataframe(df)
