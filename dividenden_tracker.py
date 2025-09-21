import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Dividenden Tracker", layout="wide")

st.title("📈 Dividenden Tracker – Portfolio")

# Portfolio-Datei automatisch laden
portfolio_file = "portfolio.csv"

if os.path.exists(portfolio_file):
    portfolio = pd.read_csv(portfolio_file)
    st.subheader("📋 Dein Portfolio")
    st.dataframe(portfolio)

    # Tabs für Monats-, Jahres- und Prognose-Ansicht
    tab1, tab2, tab3 = st.tabs(["📅 Monatliche Dividenden", "📆 Jährliche Dividenden", "🔮 Prognose"])

    monat_data = []
    jahr_data = []
    prognose_data = []

    for _, row in portfolio.iterrows():
        ticker = row["Ticker"]
        stueckzahl = row["Stueckzahl"]

        stock = yf.Ticker(ticker)
        dividends = stock.dividends

        if not dividends.empty:
            df = dividends.reset_index()
            df.columns = ["Datum", "Dividende"]
            df["Jahr"] = df["Datum"].dt.year
            df["Monat"] = df["Datum"].dt.to_period("M")
            df["Gesamt"] = df["Dividende"] * stueckzahl

            # Monatsübersicht
            monatlich = df.groupby("Monat")["Gesamt"].sum().reset_index()
            monat_data.append(monatlich.assign(Ticker=ticker))

            # Jahresübersicht
            jaehrlich = df.groupby("Jahr")["Gesamt"].sum().reset_index()
            jahr_data.append(jaehrlich.assign(Ticker=ticker))

            # Prognose: Summe letzte 12 Monate * 1 Jahr
            letzte_12m = df[df["Datum"] > (pd.Timestamp.today() - pd.DateOffset(months=12))]
            prognose = letzte_12m["Gesamt"].sum()
            prognose_data.append({"Ticker": ticker, "Prognose nächstes Jahr": prognose})

        else:
            st.warning(f"⚠️ Keine Dividenden-Daten für {ticker} gefunden.")

    # Tabs befüllen
    with tab1:
        if monat_data:
            monat_df = pd.concat(monat_data)
            st.subheader("📅 Monatliche Dividenden pro Aktie")
            st.dataframe(monat_df)

    with tab2:
        if jahr_data:
            jahr_df = pd.concat(jahr_data)
            st.subheader("📆 Jährliche Dividenden pro Aktie")
            st.dataframe(jahr_df)

    with tab3:
        if prognose_data:
            prognose_df = pd.DataFrame(prognose_data)
            st.subheader("🔮 Prognose für die nächsten 12 Monate")
            st.dataframe(prognose_df)

else:
    st.error("❌ Keine Portfolio-Datei gefunden. Bitte `portfolio.csv` ins Repo legen.")
