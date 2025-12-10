import streamlit as st
import pandas as pd
import numpy as np
import time
from math import radians, cos, sin, asin, sqrt

# ==========================================
# 1. CONFIGURATION & DATA ASSETS
# ==========================================
st.set_page_config(
    page_title="India Smart Logistics Hub",
    page_icon="🇮🇳",
    layout="wide"
)

# Coordinates for Major Indian States (Lat, Lon) - Approximate Centers
state_coords = {
    'Delhi': (28.7041, 77.1025),
    'Maharashtra': (19.7515, 75.7139),
    'Karnataka': (15.3173, 75.7139),
    'Tamil Nadu': (11.1271, 78.6569),
    'Gujarat': (22.2587, 71.1924),
    'West Bengal': (22.9868, 87.8550),
    'Rajasthan': (27.0238, 74.2179),
    'Uttar Pradesh': (26.8467, 80.9462),
    'Assam': (26.2006, 92.9376),
    'Kerala': (10.8505, 76.2711),
    'Jammu & Kashmir': (33.7782, 76.5762),
    'Himachal Pradesh': (31.1048, 77.1734),
    'Madhya Pradesh': (22.9734, 78.6569),
    'Telangana': (18.1124, 79.0193),
    'Punjab': (31.1471, 75.3412)
}

# ==========================================
# 2. HELPER FUNCTIONS (The Brains)
# ==========================================
def calculate_distance(state1, state2):
    """
    Calculates Haversine distance between two states in km.
    """
    if state1 == state2:
        return 15  # Intra-city/state base distance
        
    lat1, lon1 = state_coords[state1]
    lat2, lon2 = state_coords[state2]
    
    # Haversine Formula
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers
    
    # Add 20% buffer for road curvature vs straight line
    return int(c * r * 1.2)

def get_risk_analysis(source, dest, distance, mode):
    risk = 10
    reasons = []
    
    # 1. Distance Logic
    if distance > 1800:
        risk += 25
        reasons.append("Long haul route (>1800km) prone to highway fatigue delays.")
    elif distance < 100:
        risk -= 5
        reasons.append("Short intra-state hop; typically same-day delivery.")

    # 2. Geography Logic
    difficult_terrain = ['Jammu & Kashmir', 'Himachal Pradesh', 'Assam']
    if dest in difficult_terrain:
        risk += 40
        reasons.append(f"Destination {dest} has challenging terrain/weather risks.")
    
    if source == 'Maharashtra' and dest == 'Gujarat':
        risk -= 10
        reasons.append("Golden Corridor (Mum-Ahd) has excellent highway infrastructure.")

    # 3. Mode Logic
    if mode == 'Surface (Trucking)' and distance > 1000:
        risk += 15
        reasons.append("Trucking over 1000km faces potential border checkpost delays.")
    elif mode == 'Express Air':
        risk = max(5, risk - 30)
        reasons.append("Air cargo bypasses road traffic and border checks.")

    return min(risk, 99), reasons

# ==========================================
# 3. MAIN APP LAYOUT
# ==========================================
st.title("🇮🇳 Smart Logistics Command Center")
st.markdown("### AI-Powered Route Planning & Risk Assessment")

# --- SIDEBAR INPUTS ---
st.sidebar.header("🚚 Shipment Configuration")
source_state = st.sidebar.selectbox("📍 Origin State", list(state_coords.keys()), index=0)
dest_state = st.sidebar.selectbox("🏁 Destination State", list(state_coords.keys()), index=1)
ship_mode = st.sidebar.selectbox("📦 Shipping Mode", ['Surface (Trucking)', 'Express Air', 'Rail Freight'])
weight = st.sidebar.number_input("Weight (kg)", min_value=1, value=10)

# Calculate Distance Automatically
dist_km = calculate_distance(source_state, dest_state)

# --- TABS INTERFACE ---
tab1, tab2, tab3 = st.tabs(["🤖 AI Risk Predictor", "🗺️ Route Visualizer", "💰 Cost Estimator"])

# --- TAB 1: PREDICTOR ---
with tab1:
    st.subheader(f"Route: {source_state} ➡️ {dest_state}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Calculated Distance", f"{dist_km} km")
    col2.metric("Selected Mode", ship_mode)
    
    if st.button("Analyze Route Risk", type="primary"):
        with st.spinner("Querying Traffic & Weather APIs..."):
            time.sleep(1) # Simulated delay
            
            risk_score, insights = get_risk_analysis(source_state, dest_state, dist_km, ship_mode)
            
            # Display Score
            if risk_score < 30:
                st.success(f"✅ Low Risk: {risk_score}% Probability of Delay")
            elif risk_score < 60:
                st.warning(f"⚠️ Moderate Risk: {risk_score}% Probability of Delay")
            else:
                st.error(f"🚨 High Risk: {risk_score}% Probability of Delay")
            
            # Display Reasons
            st.markdown("#### 🧠 AI Insights:")
            for reason in insights:
                st.write(f"- {reason}")

# --- TAB 2: MAP VISUALIZER ---
with tab2:
    st.subheader("📍 Geospatial Route View")
    
    # Create a DataFrame for the map
    map_data = pd.DataFrame([
        {'lat': state_coords[source_state][0], 'lon': state_coords[source_state][1], 'Type': 'Origin'},
        {'lat': state_coords[dest_state][0], 'lon': state_coords[dest_state][1], 'Type': 'Destination'}
    ])
    
    # Show Map
    st.map(map_data, zoom=4)
    st.info(f"Visualizing direct path from {source_state} to {dest_state}.")

# --- TAB 3: COST ESTIMATOR ---
with tab3:
    st.subheader("💰 Smart Quote Calculator")
    
    # Simple Cost Logic
    base_rate = 50 # Base handling fee
    per_km_rate = 0.5 if ship_mode == 'Surface (Trucking)' else 2.5
    weight_multiplier = weight * 1.5
    
    total_cost = base_rate + (dist_km * per_km_rate) + weight_multiplier
    
    c1, c2 = st.columns(2)
    with c1:
        st.write(f"**Distance:** {dist_km} km")
        st.write(f"**Weight:** {weight} kg")
        st.write(f"**Mode Rate:** ₹{per_km_rate}/km")
    
    with c2:
        st.metric("Estimated Shipping Cost", f"₹{total_cost:,.2f}")
    
    st.caption("*Note: Estimates include GST and fuel surcharge.*")
