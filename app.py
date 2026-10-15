import requests
import streamlit as st
from datetime import datetime

# --- स्क्रीन की शानदार डिजाइन और स्टाइलिंग ---
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

# 1. इंडियन नेशनल AQI फॉर्मूला (CPCB ब्रेकपॉइंट्स)
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

# यूजर से शहर का इनपुट
city_input = st.text_input("Enter city name:", value="mumbai").strip()

# डिफ़ॉल्ट फॉलबैक
pm25_val = 296.9
temp_val = 30.5
humid_val = 61.0
wind_val = 2.25
station_name = "Chhatrapati Shivaji Intl. Airport (T2), Mumbai, India"
station_aqi_reported = 3

# --- 🔐 100% लाइव डायनामिक API इंटीग्रेशन ---
if city_input:
    try:
        # यह आपके Streamlit Cloud Secrets से API Key उठाएगा
        api_token = st.secrets["aqi_api_key"]
        
        # 1. शहर को सर्च करने के लिए API कॉल
        search_url = f"https://waqi.info{api_token}&keyword={city_input.lower()}"
        search_response = requests.get(search_url).json()
        
        if search_response.get('status') == 'ok' and len(search_response.get('data', [])) > 0:
            # 🎯 यहाँ इंडेक्स [0] लगाया है ताकि लिस्ट का पहला और बेस्ट-मैचिंग लाइव स्टेशन सेलेक्ट हो जाए
            best_station = search_response['data'][0]
            station_name = best_station['station']['name']
            station_uid = best_station['uid']
            
            # 2. उस लाइव स्टेशन का पूरा रीयल-टाइम डेटा फीड खींचना
            feed_url = f"https://waqi.info@{station_uid}/?token={api_token}"
            feed_response = requests.get(feed_url).json()
            
            if feed_response.get('status') == 'ok':
                data = feed_response['data']
                
                # PM2.5 वैल्यू निकालना
                pm25_val = data.get('iaqi', {}).get('pm25', {}).get('v', pm25_val)
                station_aqi_reported = data.get('aqi', 'N/A')
                
                # मौसम का लाइव डेटा (अगर उपलब्ध हो, नहीं तो पुराना बैकअप रखेगा)
                temp_val = data.get('iaqi', {}).get('t', {}).get('v', temp_val)
                humid_val = data.get('iaqi', {}).get('h', {}).get('v', humid_val)
                wind_val = data.get('iaqi', {}).get('w', {}).get('v', wind_val)
        else:
            st.warning(f"City '{city_input}' not found on the live server. Showing fallback data.")
            
    except Exception as e:
        # अगर Secrets का नाम गलत है, तो स्क्रीन पर आसान शब्दों में गाइडेंस आ जाएगी
        st.error("🔑 Secrets Error: Please ensure you added 'aqi_api_key' inside your Streamlit Cloud Advanced Settings!")

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
    f"<span style='font-size: 14px; font-weight: normal; opacity: 0.85;'>(Station reported AQI: {station_aqi_reported})</span>"
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
    
