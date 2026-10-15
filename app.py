import streamlit as st
import requests
import pickle
import numpy as np

st.set_page_config(page_title="Live Smart City AQI Predictor", page_icon="🌱")
st.title("🌱 Live Smart City AQI Predictor")
st.caption("Target: SDG Goal 11 - Live Urban Air Quality Integration")

TOKEN = st.secrets["WAQI_TOKEN"]

@st.cache_resource
def load_model():
    with open("aqi_model.pkl", "rb") as f:
        return pickle.load(f)

city = st.text_input("Enter city name:", "Nagpur")

if city:
    try:
        url = f"https://api.waqi.info/feed/{requests.utils.quote(city)}/"
        resp = requests.get(url, params={"token": TOKEN}, timeout=10).json()
    except Exception:
        st.error("Could not reach the AQI service. Check internet and try again.")
        st.stop()

    if resp.get("status") != "ok":
        st.error("City not found or no station available. Try another city.")
        st.stop()

    data = resp["data"]
    iaqi = data.get("iaqi", {})          # NOTE: 'iaqi', not 'iaq'
    st.info(f"📍 Data from monitoring station: {data['city']['name']}")

    labels = {"t": "Temperature (°C)", "h": "Humidity (%)",
              "pm25": "PM2.5 (µg/m³)", "w": "Wind speed (m/s)"}
    defaults = {"t": 30.0, "h": 55.0, "pm25": 45.0, "w": 2.0}

    live = {k: iaqi.get(k, {}).get("v") for k in labels}
    missing = [labels[k] for k, v in live.items() if v is None]
    if missing:
        st.warning("Station did not report: " + ", ".join(missing)
                   + ". Please enter these manually below.")

    values = {}
    for k in ["t", "h", "pm25", "w"]:
        if live[k] is not None:
            values[k] = float(live[k])
        else:
            values[k] = st.number_input(labels[k], value=defaults[k])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Temperature", f"{values['t']} °C")
    c2.metric("Humidity", f"{values['h']} %")
    c3.metric("PM2.5", f"{values['pm25']} µg/m³")
    c4.metric("Wind", f"{values['w']} m/s")

    try:
        model = load_model()
        # order must match training: Temperature, Humidity, PM2.5, Wind Speed
        X = np.array([[values["t"], values["h"], values["pm25"], values["w"]]])
        pred = model.predict(X)[0]

        st.markdown("---")
        st.subheader(f"📊 AI Predicted AQI: {pred:.0f}  (Station reported AQI: {data['aqi']})")

        if pred <= 50:
            st.success("🟢 Good / Safe")
        elif pred <= 100:
            st.warning("🟡 Moderate")
        else:
            st.error("🔴 Poor / Unhealthy")
    except Exception as e:
        st.error(f"Model error: {e}")
        st.caption("Data source: World Air Quality Index Project (aqicn.org)")
