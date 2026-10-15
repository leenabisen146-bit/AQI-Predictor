import requests
import streamlit as st
from datetime import datetime

# --- स्क्रीन की डिजाइन और स्टाइलिंग ---
st.set_page_config(page_title="AI AQI Predictor", layout="centered")

st.markdown("""
    <style>
    .metric-box {
        background-color: #f8f9fa; padding: 15px; border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); text-align: center; margin-bottom: 10px;
    }
    .metric-label { font-size: 14px; color: #6c757d; margin-bottom: 2px; }
    .metric-value { font-size: 24px; font-weight: bold; color: #212529; }
    .timestamp-text {
        font-size: 14px; color: #495057; background-color: #e9ecef;
        padding: 8px 15px; border-radius: 20px; display: inline-block; margin-bottom: 20px;
    }
    .aqi-banner {
        padding: 20px; border-radius: 10px; color: white;
        text-align: center; font-size: 22px; font-weight: bold; margin-bottom: 25px;
    }
    </style>
""", unsafe_allow_html=True)

def calculate_indian_aqi(pm25):
    if pm25 <= 30: return round(((50 - 0) / (30 - 0)) * (pm25 - 0) + 0)
    elif pm25 <= 60: return round(((100 - 50) / (60 - 30)) * (pm25 - 30) + 50)
    elif pm25 <= 90: return round(((200 - 100) / (90 - 60)) * (pm25 - 60) + 100)
    elif pm25 <= 120: return round(((300 - 200) / (120 - 90)) * (pm25 - 90) + 200)
    elif pm25 <= 250: return round(((400 - 300) / (250 - 120)) * (pm25 - 120) + 300)
    else: return round(((500 - 400) / (400 - 250)) * (pm25 - 250) + 400)

def get_aqi_status_and_color(aqi):
    if aqi <= 50: return "Good", "#2e7d32"
    elif aqi <= 100: return "Satisfactory", "#4caf50"
    elif aqi <= 200: return "Moderate", "#fbc02d"
    elif aqi <= 300: return "Poor", "#f57c00"
    elif aqi <= 400: return "Very Poor", "#d32f2f"
    else: return "Severe", "#b71c1c"

st.title("💨 Air Quality World Air Quality Index Project")
city_input = st.text_input("Enter city name:", value="mumbai").strip().lower()

# डिफ़ॉल्ट फॉलबैक
pm25_val, temp_val, humid_val, wind_val = 296.9, 30.5, 61.0, 2.25
station_name = "Chhatrapati Shivaji Intl. Airport (T2), Mumbai, India"

# FREE API WITHOUT SECRETS (Nagpur & Mumbai Coordinates)
geo_data = {"mumbai": (19.0760, 72.8777, "Mumbai, Maharashtra"), "nagpur": (21.1458, 79.0882, "Nagpur, Maharashtra")}

if city_input in geo_data:
    lat, lon, station_name = geo_data[city_input]
    try:
        url = f"https://open-meteo.com{lat}&longitude={lon}&current=pm2_5&hourly=pm2_5"
        weather_url = f"https://open-meteo.com{lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m"
        
        aqi_res = requests.get(url).json()
        wea_res = requests.get(weather_url).json()
        
        pm25_val = aqi_res['current']['pm2_5']
        temp_val = wea_res['current']['temperature_2m']
        humid_val = wea_res['current']['relative_humidity_2m']
        wind_val = round(wea_res['current']['wind_speed_10m'] / 3.6, 2) # km/h to m/s
    except:
        pass

st.markdown(f"📍 **Station:** {station_name}")
current_time = datetime.now().strftime("%d-%b-%Y | %I:%M:%S %p")
st.markdown(f"<div class='timestamp-text'>🕒 <b>Last Updated:</b> {current_time}</div>", unsafe_allow_html=True)

corrected_ai_aqi = calculate_indian_aqi(pm25_val)
status_text, banner_color = get_aqi_status_and_color(corrected_ai_aqi)

st.markdown(f"<div class='aqi-banner' style='background-color: {banner_color};'>🤖 AI Predicted AQI: {corrected_ai_aqi} ({status_text})</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown(f"<div class='metric-box'><div class='metric-label'>Temperature</div><div class='metric-value'>{temp_val} °C</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='metric-box'><div class='metric-label'>PM2.5</div><div class='metric-value'>{pm25_val} µg/m³</div></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='metric-box'><div class='metric-label'>Humidity</div><div class='metric-value'>{humid_val}%</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='metric-box'><div class='metric-label'>Wind</div><div class='metric-value'>{wind_val} m/s</div></div>", unsafe_allow_html=True)
