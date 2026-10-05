import streamlit as st
import pickle
import numpy as np

# 1. Load the permanent AI model
with open('aqi_model.pkl', 'rb') as file:
    model = pickle.load(file)

st.set_page_config(page_title="Smart City AQI Predictor", page_icon="🌱")
st.title("🌱 Smart City AQI Predictor")
st.caption("Target: SDG Goal 11 - Sustainable Cities and Communities")
st.write("Adjust the sliders below to predict the Air Quality Index (AQI) in real-time.")

# 2. Interactive Sliders for the User Interface
temp = st.slider("Temperature (°C)", 15.0, 45.0, 30.0)
humidity = st.slider("Humidity (%)", 30.0, 90.0, 60.0)
pm25 = st.slider("PM2.5 Levels (µg/m³)", 10.0, 150.0, 50.0)
wind = st.slider("Wind Speed (km/h)", 1.0, 20.0, 10.0)

if st.button("Predict Air Quality Status"):
    features = np.array([[temp, humidity, pm25, wind]])
    prediction = model.predict(features)
    
    st.markdown("---")
    st.subheader(f"🚨 Predicted AQI: {prediction:.2f}")
    
    if prediction <= 50:
        st.success("🟢 Status: Good / Safe. Perfect for outdoor activities!")
    elif prediction <= 100:
        st.warning("🟡 Status: Moderate. Acceptable air quality.")
    else:
        st.error("🔴 Status: Poor / Unhealthy. Action required under SDG 11!")
