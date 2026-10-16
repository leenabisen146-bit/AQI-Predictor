import streamlit as st
import requests
import pickle
import numpy as np
from datetime import datetime, timezone, timedelta
st.set_page_config(page_title="Live Smart City AQI Predictor", page_icon="🌱")
st.title("🌱 Live Smart City AQI Predictor")
st.caption("Target: SDG Goal 11 - Live Urban Air Quality Integration")
st.caption("Air quality: World Air Quality Index Project (aqicn.org) | Weather: Open-Meteo.com")

TOKEN = st.secrets["WAQI_TOKEN"]
BASE = "https://api.waqi.info"
IST = timezone(timedelta(hours=5, minutes=30))
# US EPA PM2.5 breakpoints: (AQI_low, AQI_high, conc_low, conc_high in ug/m3)
PM25_BP = [(0, 50, 0.0, 12.0), (51, 100, 12.1, 35.4), (101, 150, 35.5, 55.4),
           (151, 200, 55.5, 150.4), (201, 300, 150.5, 250.4),
           (301, 400, 250.5, 350.4), (401, 500, 350.5, 500.4)]

def pm25_aqi_to_conc(aqi):
    """Convert PM2.5 AQI sub-index to approx concentration (ug/m3)."""
    for a_lo, a_hi, c_lo, c_hi in PM25_BP:
        if aqi <= a_hi:
            aqi = max(aqi, a_lo)
            return c_lo + (aqi - a_lo) * (c_hi - c_lo) / (a_hi - a_lo)
    return 500.0

def get_weather(lat, lon):
    r = requests.get("https://api.open-meteo.com/v1/forecast", params={
        "latitude": lat, "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
        "wind_speed_unit": "ms"}, timeout=10).json()
    c = r["current"]
    return c["temperature_2m"], c["relative_humidity_2m"], c["wind_speed_10m"]

@st.cache_resource
def load_model():
    with open("aqi_model.pkl", "rb") as f:
        return pickle.load(f)

city = st.text_input("Enter city name:", "Nagpur")

if city:
    # 1. Find stations in the city
    try:
        found = requests.get(f"{BASE}/search/",
                             params={"token": TOKEN, "keyword": city},
                             timeout=10).json()
    except Exception as e:
        st.error(f"Could not reach the AQI service: {e}")
        st.stop()
    if found.get("status") != "ok" or not found.get("data"):
        st.error(f"No station found. Response: {found.get('data')}")
        st.stop()

    options = {s["station"]["name"]: s["uid"] for s in found["data"]}
    choice = st.selectbox("Select monitoring station:", list(options.keys()))

    # 2. Live air quality of the station
    try:
        resp = requests.get(f"{BASE}/feed/@{options[choice]}/",
                            params={"token": TOKEN}, timeout=10).json()
    except Exception as e:
        st.error(f"Could not fetch station data: {e}")
        st.stop()
    if resp.get("status") != "ok":
        st.error(f"API error: {resp.get('data')}")
        st.stop()

    data = resp["data"]
    iaqi = data.get("iaqi", {})
        t = data.get("time", {})
    st.info(f"📍 **{data['city']['name']}**  \n"
            f"🕒 Station data time: {t.get('s', 'N/A')} (UTC{t.get('tz', '')})  \n"
            f"⏱️ Now (IST): {datetime.now(IST):%d %b %Y, %I:%M %p}")

    # PM2.5 (WAQI gives AQI sub-index -> convert to ug/m3)
    pm25_aqi = iaqi.get("pm25", {}).get("v")
    if pm25_aqi is None and data.get("dominentpol") == "pm25" and isinstance(data.get("aqi"), (int, float)):
        pm25_aqi = data["aqi"]
    pm25 = round(pm25_aqi_to_conc(float(pm25_aqi)), 1) if pm25_aqi is not None else None

    # 3. Weather from Open-Meteo using station coordinates
    temp = hum = wind = None
    try:
        lat, lon = data["city"]["geo"]
        temp, hum, wind = get_weather(lat, lon)
    except Exception:
        pass

    # 4. Anything still missing -> manual input
    def ask(label, value, default):
        if value is not None:
            return float(value)
        st.warning(f"{label} not available. Please enter manually.")
        return st.number_input(label, value=default)

    temp = ask("Temperature (°C)", temp, 30.0)
    hum = ask("Humidity (%)", hum, 55.0)
    pm25 = ask("PM2.5 (µg/m³)", pm25, 45.0)
    wind = ask("Wind speed (m/s)", wind, 2.0)

    c1, c2 = st.columns(2)
    c1.metric("Temperature", f"{temp} °C")
    c2.metric("Humidity", f"{hum} %")
    c3, c4 = st.columns(2)
    c3.metric("PM2.5", f"{pm25} µg/m³")
    c4.metric("Wind", f"{wind} m/s")

    try:
        model = load_model()
        # order must match training: Temperature, Humidity, PM2.5, Wind Speed
        pred = model.predict(np.array([[temp, hum, pm25, wind]]))[0]
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
        
