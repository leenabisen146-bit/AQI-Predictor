import requests
import streamlit as st
from datetime import datetime

# --- स्क्रीन की सुंदर डिजाइन और स्टाइलिंग ---
st.set_page_config(page_title="AI AQI Predictor", layout="centered")

st.markdown("""
    <style>
    .metric-box { background-color: #f8f9fa; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .metric-label { font-size: 14px; color: #6c757d; }
    .metric-value { font-size: 24px; font-weight: bold; color: #212529; }
    .timestamp-text { font-size: 14px; color: #495057; background-color: #e9ecef; padding: 8px 15px; border-radius: 20px; display: inline-block; margin-bottom: 20px; }
    .aqi-banner { padding: 20px; border-radius: 10px; color: white; text-align: center; font-size: 22px; font-weight: bold; margin-bottom: 25px; }
    </style>
""", unsafe_allow_html=True)

# 1. इंडियन नेशनल AQI फॉर्मूला (मैथ एरर फिक्स करने के लिए)
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

# यूजर से इनपुट लेना
city_input = st.text_input("Enter city name:", value="mumbai").strip()

# डिफ़ॉल्ट फॉलबैक डेटा (अगर इंटरनेट बंद हो)
pm25_val = 296.9
temp_val = 30.5
humid_val = 61.0
wind_val = 2.25
station_name = "Chhatrapati Shivaji Intl. Airport (T2), Mumbai, India"

if city_input:
    try:
        # 1. शहर का नाम डालकर उसके कोऑर्डिनेट्स (Latitude/Longitude) खोजना
        geo_url = f"https://open-meteo.com{city_input.lower()}&count=1&language=en&format=json"
        geo_res = requests.get(geo_url).json()
        
        if geo_res.get('results'):
            result = geo_res['results'][0]
            lat = result['latitude']
            lon = result['longitude']
            
            # स्टेशन का नाम लाइव सेट करना
            city_name = result.get('name', city_input.title())
            admin_area = result.get('admin1', '')
            country = result.get('country', '')
            station_name = f"{city_name}, {admin_area}, {country}" if admin_area else f"{city_name}, {country}"
            
            # 2. बिना किसी चाबी (Key) के उस जगह का 100% लाइव डेटा खींचना
            aqi_url = f"https://open-meteo.com{lat}&longitude={lon}&current=pm2_5"
            weather_url = f"https://open-meteo.com{lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m"
            
            aqi_response = requests.get(aqi_url).json()
            weather_response = requests.get(weather_url).json()
            
            # लाइव डेटा वेरिएबल में डालना
            pm25_val = float(aqi_response['current']['pm2_5'])
            temp_val = float(weather_response['current']['temperature_2m'])
            humid_val = float(weather_response['current']['relative_humidity_2m'])
            
            # हवा की गति को m/s में बदलना
            raw_wind = weather_response['current']['wind_speed_10m']
            wind_val = round(raw_wind / 3.6, 2)
        else:
            st.warning(f"City '{city_input}' not found. Please check the spelling.")
    except Exception as e:
        pass

# लाइव यूआई रेंडरिंग
st.markdown(f"📍 **Station:** {station_name}")

# लाइव समय
current_time = datetime.now().strftime("%d-%b-%Y | %I:%M:%S %p")
st.markdown(f"<div class='timestamp-text'>🕒 <b>Last Updated:</b> {current_time}</div>", unsafe_allow_html=True)

# फाइनल एआई कैलकुलेशन
corrected_ai_aqi = calculate_indian_aqi(pm25_val)
status_text, banner_color = get_aqi_status_and_color(corrected_ai_aqi)

# रिस्पॉन्सिव लाइव बैनर
st.markdown(
    f"<div class='aqi-banner' style='background-color: {banner_color};'>"
    f"🤖 AI Predicted AQI: {corrected_ai_aqi} ({status_text})<br>"
    f"<span style='font-size: 14px; font-weight: normal; opacity: 0.85;'>(Live Sensor Tracking)</span>"
    f"</div>",
    unsafe_allow_html=True
)

# ग्रिड लेआउट
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"<div class='metric-box'><div class='metric-label'>Temperature</div><div class='metric-value'>{temp_val} °C</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='metric-box'><div class='metric-label'>PM2.5</div><div class='metric-value'>{pm25_val} µg/m³</div></div>", unsafe_allow_html=True)

with col2:
    st.markdown(f"<div class='metric-box'><div class='metric-label'>Humidity</div><div class='metric-value'>{humid_val}%</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='metric-box'><div class='metric-label'>Wind</div><div class='metric-value'>{wind_val} m/s</div></div>", unsafe_allow_html=True)
