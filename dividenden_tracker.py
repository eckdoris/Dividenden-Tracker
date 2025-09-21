import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="📊 Dividenden Tracker", layout="wide")

st.title("📈 Dividenden Tracker")

# CSV hochladen
uploaded_file = st.file_uploader("📂 Lade deine Dividenden-CSV hoch", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, sep=",")
    st.subheader("Deine Daten")
    st.dataframe(df)

    # Monatliche Dividenden berechnen
    monthly = df.groupby("Monat")["Dividende"].sum().reindex(range(1, 13), fill_value=0)

    # Balkendiagramm für 1 Jahr
    st.subheader("📊 Monatliche Dividenden im Jahr")
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    ax1.bar(monthly.index, monthly.values, color="skyblue")
    ax1.set_xticks(range(1, 13))
    ax1.set_xticklabels(["Jan","Feb","Mär","Apr","Mai","Jun","Jul","Aug","Sep","Okt","Nov","Dez"])
    ax1.set_ylabel("Dividende (€)")
    ax1.set_title("Monatliche Dividenden im Jahr")
    st.pyplot(fig1)

    # Prognose für das nächste Jahr (einfach gleiche Werte übernehmen)
    st.subheader("🔮 Prognose für nächstes Jahr")
    forecast = monthly.copy()
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    ax2.plot(monthly.index, monthly.values, marker="o", label="Ist 2024")
    ax2.plot(forecast.index, forecast.values, marker="x", linestyle="--", label="Prognose 2025")
    ax2.set_xticks(range(1, 13))
    ax2.set_xticklabels(["Jan","Feb","Mär","Apr","Mai","Jun","Jul","Aug","Sep","Okt","Nov","Dez"])
    ax2.set_ylabel("Dividende (€)")
    ax2.set_title("Dividenden Prognose")
    ax2.legend()
    st.pyplot(fig2)

    # Gesamtsumme
    st.subheader("📌 Übersicht")
    st.write(f"👉 Gesamt Dividenden dieses Jahr: **{monthly.sum():.2f} €**")
    st.write(f"👉 Erwartete Dividenden nächstes Jahr: **{forecast.sum():.2f} €**")
else:
    st.info("Bitte lade zuerst deine CSV hoch 📂")
