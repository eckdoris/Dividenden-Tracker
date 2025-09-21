import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Titel
st.title("📈 Dividenden Tracker")

# Erwartete Spalten
REQUIRED_COLUMNS = ["Aktie", "Stückzahl", "Monat", "Jahr", "Dividende"]

# CSV laden
try:
    portfolio = pd.read_csv("portfolio.csv", delimiter=",")
except FileNotFoundError:
    st.error("❌ Die Datei `portfolio.csv` wurde nicht gefunden. Bitte im Projektordner hochladen.")
    st.stop()

# Spalten prüfen
missing_columns = [col for col in REQUIRED_COLUMNS if col not in portfolio.columns]
if missing_columns:
    st.error(f"❌ In deiner `portfolio.csv` fehlen folgende Spalten: {', '.join(missing_columns)}")
    st.write("👉 Beispiel-Datei:")
    st.code(
        "Aktie,Stückzahl,Monat,Jahr,Dividende\n"
        "Jenoptik,100,März,2024,0.30\n"
        "Starbucks,50,Februar,2024,0.55\n"
        "Realty Income,20,Januar,2024,0.25",
        language="csv"
    )
    st.stop()

# Berechnung: Gesamtdividende = Stückzahl * Dividende
portfolio["Gesamt"] = portfolio["Stückzahl"] * portfolio["Dividende"]

# Gruppieren nach Jahr + Monat
dividenden_monatlich = (
    portfolio.groupby(["Jahr", "Monat"])["Gesamt"].sum().reset_index()
)

# Tabelle anzeigen
st.subheader("📊 Übersicht")
st.dataframe(portfolio)

# Diagramm anzeigen
st.subheader("📅 Monatliche Dividenden")
plt.figure(figsize=(8, 4))
plt.bar(dividenden_monatlich["Monat"], dividenden_monatlich["Gesamt"])
plt.ylabel("Dividende (€)")
plt.title("Monatliche Dividendenerträge")
st.pyplot(plt)
