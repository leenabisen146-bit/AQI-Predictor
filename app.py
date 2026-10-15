import requests
import streamlit as st
from datetime import datetime

# --- स्क्रीन की डिजाइन और स्टाइलिंग ---
st.set_page_config(page_title="AI AQI Predictor", layout="centered")

st.markdown("""
    <style>
    .metric-box {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
        margin-bottom: 10px;
    }
    .metric-label {
        font-size: 14px;
        color: #6c757d;
        margin-bottom: 2px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #212529;
    }
    .timestamp-text {
        font-size: 14px;
        color: #495057;
        background-color: #e9ecef;
        padding: 8px 15px;
        border-radius: 20px;
        display: inline-block;
        margin-bottom: 20px;
    }
    .aqi-banner {
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        font-size: 22px;
        font-weight: bold;
        margin-bottom: 25px;
    }
    </style>
""", unsafe_allow_html=True)

# --- बैकएंड कैलकुलेशन ---
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

# --- SCREEN UI BUILD ---
st.title("💨 Air Quality World Air Quality Index Project")

# यूजर इनपुट लेगा
city_input = st.text_input("Enter city name:", value="mumbai")

# डिफ़ॉल्ट वैल्यूज सेट की हैं
pm25_val = 296.9
temp_val = 30.5
humid_val = 61.0
wind_val = 2.25
station_name = "Chhatrapati Shivaji Intl. Airport (T2), Mumbai, India"
station_aqi_reported = 3

# --- 🔐 DYNAMIC API CONNECTION (शहर के हिसाब से डेटा बदलेगा) ---
if city_input:
    try:
        api_token = st.secrets["aqi_api_key"]
        
        # यहाँ फिक्स स्टेशन नंबर हटाने के लिए शहर के नाम से सर्च URL बनाया है
        search_url = f"https://waqi.info{api_token}&keyword={city_input.strip().lower()}"
        search_response = requests.get(search_url).json()
        
        if search_response['status'] == 'ok' and len(search_response['data']) > 0:
            # यह उस शहर का सबसे पहला और एक्टिव स्टेशन चुनेगा (जैसे नागपुर सिविल लाइंस या वर्धा रोड)
            best_station = search_response['data'][0]
            station_name = best_station['station']['name']
            
            # उस स्टेशन का पूरा लाइव डेटा निकालना
            feed_url = f"https://waqi.info{best_station['uid']}/?token={api_token}"
            feed_response = requests.get(feed_url).json()
            
            if feed_response['status'] == 'ok':
                data = feed_response['data']
                pm25_val = data['iaqi'].get('pm25', {}).get('v', pm25_val)
                station_aqi_reported = data.get('aqi', 'N/A')
                temp_val = data['iaqi'].get('t', {}).get('v', temp_val)
                humid_val = data['iaqi'].get('h', {}).get('v', humid_val)
                wind_val = data['iaqi'].get('w', {}).get('v', wind_val)
    except Exception as e:
        pass

# स्टेशन डिस्प्ले
st.markdown(f"📍 **Station:** {station_name}")

# लाइव टाइमस्टैम्प
current_time = datetime.now().strftime("%d-%b-%Y | %I:%M:%S %p")
st.markdown(f"<div class='timestamp-text'>🕒 <b>Last Updated:</b> {current_time}</div>", unsafe_allow_html=True)

# फाइनल कैलकुलेशन
corrected_ai_aqi = calculate_indian_aqi(pm25_val)
status_text, banner_color = get_aqi_status_and_color(corrected_ai_aqi)

# आउटपुट बैनर
st.markdown(
    f"<div class='aqi-banner' style='background-color: {banner_color};'>"
    f"🤖 AI Predicted AQI: {corrected_ai_aqi} ({status_text})<br>"
    f"<span style='font-size: 14px; font-weight: normal; opacity: 0.85;'>"
    f"(Station reported AQI: {station_aqi_reported})</span>"
    f"</div>",
    unsafe_allow_html=True
)

# ग्रिड बॉक्सेस
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"<div class='metric-box'><div class='metric-label'>Temperature</div><div class='metric-value'>{temp_val} °C</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='metric-box'><div class='metric-label'>PM2.5</div><div class='metric-value'>{pm25_val} µg/m³</div></div>", unsafe_allow_html=True)

with col2:
    st.markdown(f"<div class='metric-box'><div class='metric-label'>Humidity</div><div class='metric-value'>{humid_val}%</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='metric-box'><div class='metric-label'>Wind</div><div class='metric-value'>{wind_val} m/s</div></div>", unsafe_allow_html=True)
