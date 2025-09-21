import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import os
import requests

st.set_page_config(page_title="📈 dividenden-tracker", layout="wide")

# --- Portfolio laden ---
PORTFOLIO_FILE = "portfolio.csv"

if os.path.exists(PORTFOLIO_FILE):
    portfolio = pd.read_csv(PORTFOLIO_FILE)
else:
    st.error("❌ Keine portfolio.csv gefunden! Bitte Datei ins Repo legen.")
    st.stop()

# --- API-Key für EOD Historical Data aus Streamlit Secrets laden ---
EOD_API_KEY = st.secrets.get("EOD_API_KEY", "")

# --- Mapping Yahoo → EOD ---
TICKER_MAP = {
    "DGE.L": "DGE.LSE",      # Diageo
    "JEN.DE": "JEN.XETRA",   # Jenoptik
    "AAPL": "AAPL.US",       # Apple
    "MSFT": "MSFT.US",       # Microsoft
    "ALV.DE": "ALV.XETRA",   # Allianz
    "EUNL.DE": "EUNL.XETRA", # iShares Core MSCI World
    "VWCE.DE": "VWCE.XETRA"  # Vanguard FTSE All-World
}

# --- Datenquelle 1: Yahoo Finance ---
def get_dividends_yahoo(ticker, shares):
    stock = yf.Ticker(ticker)
    try:
        dividends = stock.dividends
    except Exception:
        return pd.DataFrame()

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

# --- Datenquelle 2: EOD Historical Data ---
def get_dividends_eod(ticker, shares):
    if not EOD_API_KEY:
        return pd.DataFrame()
    try:
        url = f"https://eodhistoricaldata.com/api/div/{ticker}?api_token={EOD_API_KEY}&fmt=json"
        r = requests.get(url)
        data = r.json()
        if not data or not isinstance(data, list):
            return pd.DataFrame()
        df = pd.DataFrame(data)
        df["Datum"] = pd.to_datetime(df["date"])
        df["Dividende"] = df["value"].astype(float)
        df["Jahr"] = df["Datum"].dt.year
        df["Monat"] = df["Datum"].dt.to_period("M")
        df["Stueckzahl"] = shares
        df["Gesamt"] = df["Dividende"] * shares
        df["Ticker"] = ticker
        return df
    except Exception:
        return pd.DataFrame()

# --- Fallback-Funktion: erst Yahoo, dann EOD ---
def get_dividends(ticker, shares):
    # 1️⃣ Versuche Yahoo
    df = get_dividends_yahoo(ticker, shares)
    if not df.empty:
        return df

    # 2️⃣ Versuche mit Mapping → EOD
    eod_ticker = TICKER_MAP.get(ticker, None)
    if eod_ticker:
        df = get_dividends_eod(eod_ticker, shares)
        if not df.empty:
            return df

    # 3️⃣ Versuche denselben Ticker direkt bei EOD
    return get_dividends_eod(ticker, shares)

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
