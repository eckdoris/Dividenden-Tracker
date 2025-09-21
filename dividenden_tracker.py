import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="📈 Dividenden Tracker", layout="wide")

# --- Portfolio laden ---
PORTFOLIO_FILE = "portfolio.csv"

if not os.path.exists(PORTFOLIO_FILE):
    st.error("❌ Keine portfolio.csv gefunden!")
    st.stop()

df = pd.read_csv(PORTFOLIO_FILE)

# Berechnen: Gesamt pro Eintrag
df["Gesamt"] = df["Stueckzahl"] * df["Dividende_pro_Aktie"]

# Monatsweise summieren
monatlich = df.groupby("Monat")["Gesamt"].sum().reset_index()

# Jahresweise summieren
jaehrlich = df.groupby("Aktie")["Gesamt"].sum().reset_index()
jaehrlich_total = pd.DataFrame([["Gesamt", jaehrlich["Gesamt"].sum()]], columns=["Aktie", "Gesamt"])
jaehrlich = pd.concat([jaehrlich, jaehrlich_total])

# Prognose: gleiche Werte für die nächsten 5 Jahre
jahres_summe = jaehrlich_total["Gesamt"].iloc[0]
prognose = pd.DataFrame({
    "Jahr": range(2025, 2030),
    "Dividenden": [jahres_summe] * 5
})

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["📅 Monatlich", "📆 Jährlich", "🔮 Prognose"])

with tab1:
    st.subheader("📅 Monatliche Dividenden")
    st.dataframe(monatlich)

    plt.figure(figsize=(10, 4))
    plt.bar(monatlich["Monat"], monatlich["Gesamt"])
    plt.xticks(range(1, 13))
    plt.ylabel("Dividenden (€)")
    plt.title("Monatliche Dividenden")
    st.pyplot(plt)

with tab2:
    st.subheader("📆 Jährliche Dividenden")
    st.dataframe(jaehrlich)

    plt.figure(figsize=(8, 4))
    plt.bar(jaehrlich["Aktie"], jaehrlich["Gesamt"])
    plt.ylabel("Dividenden (€)")
    plt.title("Jährliche Dividenden pro Aktie")
    st.pyplot(plt)

with tab3:
    st.subheader("🔮 Prognose für die nächsten 5 Jahre")
    st.dataframe(prognose)

    plt.figure(figsize=(8, 4))
    plt.plot(prognose["Jahr"], prognose["Dividenden"], marker="o")
    plt.ylabel("Dividenden (€)")
    plt.title("Dividenden-Prognose (gleichbleibend)")
    st.pyplot(plt)
