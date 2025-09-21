import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="📈 Dividenden Tracker", layout="wide")

st.title("📈 Dividenden Tracker")

# --- Aktualisieren-Button ---
if st.button("🔄 Aktualisieren"):
    st.experimental_rerun()

# --- Portfolio laden ---
PORTFOLIO_FILE = "portfolio.csv"

if os.path.exists(PORTFOLIO_FILE):
    portfolio = pd.read_csv(PORTFOLIO_FILE)
else:
    st.error("❌ Keine portfolio.csv gefunden! Bitte Datei ins Repo legen.")
    st.stop()

# --- Dividenden-Daten laden ---
if "Monat" not in portfolio.columns:
    st.error("❌ Die portfolio.csv muss die Spalten: Aktie, Stückzahl, Monat, Dividende enthalten.")
    st.stop()

portfolio["Gesamt"] = portfolio["Stückzahl"] * portfolio["Dividende"]

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["📅 Monatlich", "📆 Jährlich", "🔮 Prognose"])

with tab1:
    st.subheader("📅 Monatliche Dividenden")
    monatlich = portfolio.groupby("Monat")["Gesamt"].sum().reset_index()

    st.dataframe(monatlich)

    plt.figure(figsize=(10, 4))
    plt.bar(monatlich["Monat"], monatlich["Gesamt"])
    plt.xticks(rotation=45)
    plt.ylabel("Dividenden (€)")
    plt.title("Monatliche Dividenden")
    st.pyplot(plt)

with tab2:
    st.subheader("📆 Jährliche Dividenden")
    jaehrlich = portfolio.groupby("Jahr")["Gesamt"].sum().reset_index()

    st.dataframe(jaehrlich)

    plt.figure(figsize=(8, 4))
    plt.bar(jaehrlich["Jahr"], jaehrlich["Gesamt"])
    plt.ylabel("Dividenden (€)")
    plt.title("Jährliche Dividenden")
    st.pyplot(plt)

with tab3:
    st.subheader("🔮 Prognose")
    prognose = portfolio.groupby("Aktie")["Gesamt"].sum().reset_index()
    prognose["Prognose nächstes Jahr"] = prognose["Gesamt"]

    st.dataframe(prognose[["Aktie", "Prognose nächstes Jahr"]])
