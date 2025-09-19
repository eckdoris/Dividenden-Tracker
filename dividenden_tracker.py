import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from forex_python.converter import CurrencyRates

st.title("📊 Dividenden Tracker")

# Währungsumrechnung
c = CurrencyRates()

# Portfolio laden
st.sidebar.header("📁 Portfolio-Auswahl")
portfolio_file = st.sidebar.text_input("Dateiname (z. B. Demo.csv)", "Demo.csv")

try:
    df = pd.read_csv(f"portfolios/{portfolio_file}")
    st.sidebar.success(f"Portfolio '{portfolio_file}' geladen ✅")
except FileNotFoundError:
    st.error("⚠️ Portfolio-Datei nicht gefunden!")
    st.stop()

results = []
total_dividends = 0.0

for _, row in df.iterrows():
    symbol = row["Symbol"]
    shares = row["Anzahl"]
    tax = row["Steuersatz"]

    try:
        stock = yf.Ticker(symbol)
        info = stock.info

        dividends = stock.dividends
        if dividends.empty:
            continue

        last_div = dividends[-1]
        currency = info.get("currency", "USD")

        annual_div = last_div * 4
        gross_div = annual_div * shares
        net_div = gross_div * (1 - tax / 100)

        try:
            net_div_eur = c.convert(currency, "EUR", net_div)
        except:
            net_div_eur = net_div

        # Wichtig: Nur bei Netto eine reine Zahl speichern
        results.append([
            symbol,
            shares,
            f"{gross_div:.2f} {currency}",
            round(net_div_eur, 2)
        ])
        total_dividends += net_div_eur

    except Exception as e:
        st.warning(f"⚠️ Fehler bei {symbol}: {e}")

if results:
    st.subheader("📋 Übersicht")
    df_results = pd.DataFrame(results, columns=["Symbol", "Anzahl", "Brutto Dividende", "Netto (EUR)"])
    st.dataframe(df_results)

    st.subheader("💶 Gesamte Netto-Dividenden (12 Monate Prognose)")
    st.success(f"≈ {total_dividends:.2f} EUR")

    st.subheader("📈 Verteilung nach Aktie")
    fig, ax = plt.subplots()
    ax.bar(df_results["Symbol"], df_results["Netto (EUR)"])
    ax.set_ylabel("Dividenden in EUR")
    st.pyplot(fig)
else:
    st.warning("Keine Dividenden gefunden.")
