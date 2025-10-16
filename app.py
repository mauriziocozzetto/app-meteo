import streamlit as st
import requests
from datetime import date, timedelta
import plotly.express as px
import pandas as pd


st.title("Visualizzatore delle temperature")
st.info("👈 Per piacere scegli la città e le due date sulla sidebar, poi premi sul pulsante.")

# Sidebar controls
st.sidebar.header("Controlli")

# Location selector
locations = {
    "Bergamo": (45.6993, 9.8033),
    "Milano": (45.4642, 9.1900),
    "Roma": (41.9028, 12.4964),
    "Venezia": (45.4408, 12.3155),
    "Brescia": (45.5390, 10.2200)
}

selected_location = st.sidebar.selectbox(
    "Scegli la città", options=list(locations.keys()))

start_date = st.sidebar.date_input(
    "Data di inizio",
    value=date.today() - timedelta(days=6),
    min_value=date.today() - timedelta(days=29),
    max_value=date.today()
)

end_date = st.sidebar.date_input(
    "Data di fine",
    value=date.today(),
    min_value=date.today() - timedelta(days=30),
    max_value=date.today()
)

update_button = st.sidebar.button(
    label="Visualizza temperature", type="primary")

if update_button:

    if start_date >= end_date:
        st.error(
            "Errore, scegli le date in maniera corretta, la data di inizio deve essere inferiore alla data di fine.")
        st.stop()

    # Get coordinates for selected location
    latitude, longitude = locations[selected_location]

    response = requests.get(
        "https://archive-api.open-meteo.com/v1/archive",
        params={
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "daily": "temperature_2m_max,temperature_2m_min,temperature_2m_mean",
            "timezone": "Europe/Berlin"
        }
    )

    if response.status_code == 200:
        data = response.json()

        print(data)

        # Create DataFrame
        df = pd.DataFrame({
            "Date": pd.date_range(start_date, end_date).date,
            "Temperatura Max (°C)": data["daily"]["temperature_2m_max"],
            "Temperatura Min (°C)": data["daily"]["temperature_2m_min"],
            "Temperatura Media (°C)": data["daily"]["temperature_2m_mean"]
        })

        # Create temperature chart with all three lines
        st.subheader(f"Trend delle temperature - {selected_location}")

        # Create figure with multiple lines
        fig = px.line(df, x="Date", y=["Temperatura Max (°C)", "Temperatura Media (°C)", "Temperatura Min (°C)"],
                      markers=True)

        # Customize line colors
        fig.update_traces(
            selector=dict(name="Temperatura Max (°C)"), line_color="red",
            line=dict(width=3)
        )
        fig.update_traces(
            selector=dict(name="Temperatura Media (°C)"), line_color="orange",
            line=dict(width=2.5)
        )
        fig.update_traces(
            selector=dict(name="Temperatura Min (°C)"), line_color="blue",
            line=dict(width=3)
        )

        # Update layout
        fig.update_layout(
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,    # Posiziona la legenda sopra il grafico
                xanchor="center",
                x=0.5,     # Centra orizzontalmente
                bgcolor="rgba(255,255,255,0.8)"  # Sfondo semi-trasparente
            )
        )

        st.plotly_chart(fig)

        # 4 colonne
        c1, c2, c3, c4 = st.columns(4)

        # temp. notevoli e numero giorni
        temp_max = df['Temperatura Max (°C)'].max()
        temp_min = df['Temperatura Min (°C)'].min()
        temp_mean = df['Temperatura Media (°C)'].mean()
        giorni_calcolati = len(df)

        c1.metric("Temperatura Max", f"{temp_max:.1f}°C")
        c2.metric("Temperatura Min", f"{temp_min:.1f}°C")
        c3.metric("Temperatura Media", f"{temp_mean:.1f}°C")
        c4.metric("Giorni Calcolati", giorni_calcolati)

        # Display raw data
        st.subheader("Temperature giorno per giorno")
        st.dataframe(df)
    else:
        st.error(
            f"Errore: {response.status_code} - {response.text}")
