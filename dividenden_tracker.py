import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="📈 Dividenden Tracker", layout="wide")

# --- Portfolio laden ---
def finde_portfolio_datei():
    moegliche_namen = ["portfolio.csv", "Portfolio.csv"]
    for name in moegliche_namen:
        if os.path.exists(name):
            return name
    # Suche in Unterordnern
    for root, dirs, files in os.walk("."):
        for name in moegliche_namen:
            if name in files:
                return os.path.join(root, name)
    return None

PORTFOLIO_FILE = finde_portfolio_datei()

if PORTFOLIO_FILE:
    portfolio = pd.read_csv(PORTFOLIO_FILE)
else:
    st.error("❌ Keine portfolio.csv / Portfolio.csv gefunden! Bitte Datei ins Repo legen.")
    st.stop()

# --- Daten von Yahoo Finance laden ---
def get_dividends(ticker, shares):
    stock = yf.Ticker(ticker)
    try:
        dividends = stock.dividends
    except Exception:
        dividends = pd.Series(dtype="float64")

    if dividends.empty:
        return pd.DataFrame()

    df = dividends.reset_index()
    df.columns = ["Datum", "Dividende"]
    df["Jahr"] = df["Datum"].dt.year
    df["Monat"] = df["Datum"].dt.to_period("M")
    df["Stueckzahl"] = shares
    df["Gesamt"] = df["Dividende"] * shares
    df["Ticker"] = ticker
    return df

# --- Alle Aktien laden ---
alle_dividenden = []
for _, row in portfolio.iterrows():
    df = get_dividends(row["Ticker"], row["Stueckzahl"])
    if not df.empty:
        alle_dividenden.append(df)

if not alle_dividenden:
    st.warning("⚠️ Keine Dividenden-Daten gefunden.")
    st.stop()

dividenden_df = pd.concat(alle_dividenden)

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["📅 Monatlich", "📆 Jährlich", "🔮 Prognose"])

with tab1:
    st.subheader("📅 Monatliche Dividenden")
    monatlich = dividenden_df.groupby(["Monat"])["Gesamt"].sum().reset_index()
    monatlich["Monat"] = monatlich["Monat"].astype(str)

    st.dataframe(monatlich)

    plt.figure(figsize=(10, 4))
    plt.bar(monatlich["Monat"], monatlich["Gesamt"])
    plt.xticks(rotation=45)
    plt.ylabel("Dividenden (€)")
    plt.title("Monatliche Dividenden")
    st.pyplot(plt)

with tab2:
    st.subheader("📆 Jährliche Dividenden")
    jaehrlich = dividenden_df.groupby("Jahr")["Gesamt"].sum().reset_index()

    st.dataframe(jaehrlich)

    plt.figure(figsize=(8, 4))
    plt.bar(jaehrlich["Jahr"], jaehrlich["Gesamt"])
    plt.ylabel("Dividenden (€)")
    plt.title("Jährliche Dividenden")
    st.pyplot(plt)

with tab3:
    st.subheader("🔮 Prognose")
    letztes_jahr = dividenden_df[dividenden_df["Jahr"] == dividenden_df["Jahr"].max()]
    prognose = letztes_jahr.groupby("Ticker")["Gesamt"].sum().reset_index()
    prognose["Prognose nächstes Jahr"] = prognose["Gesamt"]

    st.dataframe(prognose[["Ticker", "Prognose nächstes Jahr"]])
