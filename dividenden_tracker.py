import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Dividenden Tracker", layout="wide")

st.title("📈 Dividenden Tracker")

# Eingabe: Tickersymbol(e)
tickers_input = st.text_input("Gib ein oder mehrere Tickersymbole ein (z. B. AAPL, MSFT, T)", "AAPL")

if tickers_input:
    tickers = [t.strip().upper() for t in tickers_input.split(",")]
    data = {}

    for ticker in tickers:
        stock = yf.Ticker(ticker)
        dividends = stock.dividends

        if not dividends.empty:
            df = dividends.reset_index()
            df.columns = ["Datum", "Dividende"]
            df["Jahr"] = df["Datum"].dt.year
            yearly = df.groupby("Jahr")["Dividende"].sum().reset_index()

            data[ticker] = yearly

            st.subheader(f"📊 {ticker} – Dividendenhistorie")
            st.dataframe(df)

            # Plot
            fig, ax = plt.subplots()
            ax.bar(yearly["Jahr"], yearly["Dividende"])
            ax.set_title(f"{ticker} – jährliche Dividenden")
            ax.set_ylabel("Dividende (USD)")
            st.pyplot(fig)

        else:
            st.warning(f"Keine Dividenden-Daten für {ticker} gefunden.")
