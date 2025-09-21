import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="📈 Dividenden Tracker", layout="wide")

st.title("📊 Dividenden Tracker")
st.write("✅ App gestartet – wir prüfen jetzt die CSV-Datei...")

# --- Portfolio laden ---
PORTFOLIO_FILE = "portfolio.csv"

if not os.path.exists(PORTFOLIO_FILE):
    st.error("❌ Keine portfolio.csv gefunden! Bitte Datei ins Repo legen.")
    st.stop()

try:
    portfolio = pd.read_csv(PORTFOLIO_FILE)
    st.success("📂 Portfolio erfolgreich geladen")
    st.dataframe(portfolio.head())
except Exception as e:
    st.error(f"❌ Fehler beim Laden der CSV: {e}")
    st.stop()

# --- Erwartete Spalten prüfen ---
expected_cols = {"Ticker", "Stueckzahl", "Jahr", "Monat", "Dividende"}
if not expected_cols.issubset(set(portfolio.columns)):
    st.error(f"❌ Falsches Format in portfolio.csv! Erwartet: {expected_cols}")
    st.stop()

# --- Gesamtbetrag berechnen ---
portfolio["Gesamt"] = portfolio["Dividende"] * portfolio["Stueckzahl"]

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["📅 Monatlich", "📆 Jährlich", "📊 Übersicht"])

with tab1:
    st.subheader("📅 Monatliche Dividenden")

    monatlich = portfolio.groupby(["Jahr", "Monat"])["Gesamt"].sum().reset_index()

    if monatlich.empty:
        st.warning("⚠️ Keine monatlichen Daten gefunden.")
    else:
        st.dataframe(monatlich)

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.bar(monatlich["Monat"].astype(str), monatlich["Gesamt"])
        ax.set_ylabel("Dividenden (€)")
        ax.set_title("Monatliche Dividenden")
        st.pyplot(fig)

with tab2:
    st.subheader("📆 Jährliche Dividenden")

    jaehrlich = portfolio.groupby("Jahr")["Gesamt"].sum().reset_index()

    if jaehrlich.empty:
        st.warning("⚠️ Keine jährlichen Daten gefunden.")
    else:
        st.dataframe(jaehrlich)

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(jaehrlich["Jahr"].astype(str), jaehrlich["Gesamt"])
        ax.set_ylabel("Dividenden (€)")
        ax.set_title("Jährliche Dividenden")
        st.pyplot(fig)

with tab3:
    st.subheader("📊 Übersicht pro Aktie")

    uebersicht = portfolio.groupby("Ticker")["Gesamt"].sum().reset_index()

    if uebersicht.empty:
        st.warning("⚠️ Keine Daten pro Aktie gefunden.")
    else:
        st.dataframe(uebersicht)
