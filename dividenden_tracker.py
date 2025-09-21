import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="📈 Dividenden Tracker", layout="wide")

# --- Portfolio laden ---
PORTFOLIO_FILE = "portfolio.csv"

if not os.path.exists(PORTFOLIO_FILE):
    st.error("❌ portfolio.csv fehlt! Bitte hochladen.")
    st.stop()

@st.cache_data
def load_data():
    return pd.read_csv(PORTFOLIO_FILE)

df = load_data()
st.success("✅ Daten geladen")
st.dataframe(df)

# --- Monatsübersicht ---
st.subheader("📅 Monatliche Dividenden")

monatlich = df.groupby("Monat")["Dividende"].sum().reset_index()

fig, ax = plt.subplots(figsize=(10,4))
ax.bar(monatlich["Monat"], monatlich["Dividende"])
ax.set_xlabel("Monat")
ax.set_ylabel("Dividenden (€)")
ax.set_title("Monatliche Dividenden")
st.pyplot(fig)

# --- Jahresübersicht ---
st.subheader("📆 Jährliche Dividenden")

# Wir gehen davon aus, dass alles ein Jahr betrifft
gesamt = monatlich["Dividende"].sum()
st.metric("📈 Gesamt pro Jahr", f"{gesamt:.2f} €")

# --- Prognose ---
st.subheader("🔮 Prognose")
prognose = gesamt  # sehr einfache Prognose = gleich wie letztes Jahr
st.write(f"Erwartete Dividenden im nächsten Jahr: **{prognose:.2f} €**")
