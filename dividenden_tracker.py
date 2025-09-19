import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from forex_python.converter import CurrencyRates

st.set_page_config(page_title="📊 Dividenden Tracker", layout="wide")
st.title("📊 Dividenden Tracker (robustere Berechnung + Debug)")

c = CurrencyRates()

# Einstellungen
st.sidebar.header("Einstellungen")
portfolio_file = st.sidebar.text_input("Dateiname (z. B. Demo.csv)", "MeinPortfolio.csv")
debug = st.sidebar.checkbox("Debugmodus anzeigen (mehr Infos pro Ticker)", value=False)

# Portfolio laden
try:
    df = pd.read_csv(f"portfolios/{portfolio_file}")
    st.sidebar.success(f"Portfolio '{portfolio_file}' geladen ✅")
except FileNotFoundError:
    st.error("⚠️ Portfolio-Datei nicht gefunden! Bitte portfolios/<Datei>.csv prüfen.")
    st.stop()

results = []
details = []   # für Debug-Tabelle
total_net_eur = 0.0

for _, row in df.iterrows():
    symbol = str(row["Symbol"]).strip()
    shares = float(row["Anzahl"])
    tax = float(row["Steuersatz"])

    try:
        stock = yf.Ticker(symbol)
        info = stock.info

        # Roh-Dividendenserie (index: Timestamp), kann leer sein
        divs = stock.dividends  # pd.Series
        currency = info.get("currency", "USD")

        # FX-Rate (fallback = 1.0)
        try:
            fx_rate = c.get_rate(currency, "EUR") if currency else 1.0
            fx_ok = True
        except Exception:
            fx_rate = 1.0
            fx_ok = False

        # --- Jahresberechnung: SUMME der letzten 12 Monate (robuster) ---
        if not divs.empty:
            one_year_ago = pd.Timestamp.now() - pd.DateOffset(days=365)
            divs_12m = divs[divs.index >= one_year_ago]
            if not divs_12m.empty:
                annual_div_per_share = divs_12m.sum()
                source = "sum(12M)"
            else:
                # Fallback: letzte 4 Zahlungen, sonst Mittelwert hochgerechnet
                if len(divs) >= 4:
                    annual_div_per_share = divs.tail(4).sum()
                    source = "sum(last4)"
                else:
                    avg = divs.mean() if len(divs) > 0 else 0.0
                    annual_div_per_share = avg * 4
                    source = "avg*4 (fallback)"
        else:
            annual_div_per_share = 0.0
            source = "no_divs"

        # Brutto / Netto / Umrechnung
        gross_annual = annual_div_per_share * shares * fx_rate  # in EUR (wenn fx ok)
        net_annual = gross_annual * (1 - tax / 100)

        # Sammle Ergebnisse (Netto als reine Zahl!)
        results.append({
            "Symbol": symbol,
            "Anzahl": shares,
            "Brutto (orig)": round(annual_div_per_share * shares, 6),  # in original currency
            "Währung": currency,
            "FX_rate": round(fx_rate, 6),
            "Brutto (EUR)": round(gross_annual, 2),
            "Netto (EUR)": round(net_annual, 2),
            "Berechnungsquelle": source
        })
        total_net_eur += net_annual

        # Detail für Debug
        if debug:
            divs_preview = divs.tail(8).apply(lambda x: round(x,6)).to_dict()
            details.append({
                "Symbol": symbol,
                "divs_last_values": divs_preview,
                "annual_div_per_share": float(annual_div_per_share),
                "currency": currency,
                "fx_ok": fx_ok,
                "fx_rate": fx_rate,
                "source": source
            })

    except Exception as e:
        st.warning(f"Fehler beim Ticker {symbol}: {e}")
        # weiterhin weitermachen

# Ausgabe
if results:
    res_df = pd.DataFrame(results)
    st.subheader("📋 Übersicht")
    st.dataframe(res_df.style.format({"Brutto (orig)": "{:.4f}", "Brutto (EUR)": "{:.2f}", "Netto (EUR)": "{:.2f}"}))

    st.subheader("💶 Gesamte Netto-Dividenden (12 Monate Prognose)")
    st.success(f"≈ {total_net_eur:.2f} EUR")

    st.subheader("📈 Verteilung nach Aktie (Netto EUR)")
    fig, ax = plt.subplots()
    ax.bar(res_df["Symbol"], res_df["Netto (EUR)"])
    ax.set_ylabel("Netto (EUR)")
    st.pyplot(fig)

    if debug and details:
        st.subheader("🔍 Debug-Details pro Ticker (Rohdaten)")
        st.write(pd.DataFrame(details))
else:
    st.warning("Keine Dividendendaten gefunden. Prüfe Ticker und CSV.")
