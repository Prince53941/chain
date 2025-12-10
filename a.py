import streamlit as st
import numpy as np
import time

# ==========================================
# 1. APP CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="India Logistics AI Predictor",
    page_icon="🚚",
    layout="centered"
)

# ==========================================
# 2. THE "INDIAN CONTEXT" LOGIC
# ==========================================
def predict_indian_delivery_risk(state, ship_mode, category, distance):
    """
    Simulates delay risk based on Indian Geography & Infrastructure.
    Returns: Probability of Delay (0 to 100%)
    """
    base_risk = 10  # Base risk for any shipment
    
    # --- LOGIC A: GEOGRAPHY (State Infrastructure) ---
    # High Risk: North East & Hill States (Terrain/Connectivity issues)
    high_risk_states = ['Assam', 'Jammu & Kashmir', 'Himachal Pradesh', 'Arunachal Pradesh']
    # Low Risk: Major Industrial Hubs (Better Roads/Connectivity)
    low_risk_states = ['Maharashtra', 'Delhi', 'Karnataka', 'Gujarat', 'Tamil Nadu']
    
    if state in high_risk_states:
        base_risk += 40  # Hard to reach areas
    elif state in low_risk_states:
        base_risk -= 10  # Good connectivity
    else:
        base_risk += 15  # Average connectivity (UP, MP, Bihar, etc.)
        
    # --- LOGIC B: SHIPPING MODE ---
    if ship_mode == 'Standard Post (India Post)':
        base_risk += 35
    elif ship_mode == 'Surface (Trucking)':
        base_risk += 20
    elif ship_mode == 'Express Air':
        base_risk -= 15  # Fastest option
        
    # --- LOGIC C: DISTANCE IMPACT ---
    # In India, >1500km via Surface increases risk significantly
    if distance > 1500 and ship_mode != 'Express Air':
        base_risk += 20
    
    # Add random noise (Real life is unpredictable)
    final_risk = min(base_risk + np.random.randint(-5, 5), 99)
    return max(final_risk, 1)

# ==========================================
# 3. THE UI (USER INTERFACE)
# ==========================================
st.title("🇮🇳 Indian Logistics AI")
st.markdown("### 🚚 Pre-Shipment Delay Predictor")
st.info("Select destination state and mode to predict delivery success rate.")

st.markdown("---")

# --- USER INPUT FORM ---
with st.form("prediction_form"):
    st.write("#### 📍 Shipment Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # List of major Indian States
        state = st.selectbox("Destination State", 
            ['Maharashtra', 'Delhi', 'Karnataka', 'Tamil Nadu', 'West Bengal', 
             'Gujarat', 'Rajasthan', 'Uttar Pradesh', 'Assam', 'Kerala', 
             'Jammu & Kashmir', 'Himachal Pradesh', 'Madhya Pradesh'])
             
        category = st.selectbox("Product Category", 
            ['Electronics', 'Clothing', 'Perishable Food', 'Furniture'])
            
    with col2:
        ship_mode = st.selectbox("Shipping Mode", 
            ['Standard Post (India Post)', 'Surface (Trucking)', 'Express Air'])
            
        distance = st.slider("Distance (km)", 50, 3000, 800)
        
    submitted = st.form_submit_button("🔮 Predict Delay Risk")

# ==========================================
# 4. PREDICTION OUTPUT
# ==========================================
if submitted:
    with st.spinner('Analyzing Route & Traffic Conditions...'):
        time.sleep(1.5) # Aesthetic delay
        
        # Get the prediction
        risk_score = predict_indian_delivery_risk(state, ship_mode, category, distance)
        
        st.markdown("---")
        
        # Display Logic
        if risk_score > 65:
            st.error(f"⚠️ HIGH DELAY RISK: {risk_score:.1f}% Chance of Delay")
            st.write(f"**Insight:** Shipping to **{state}** via **{ship_mode}** for {distance}km is risky.")
            st.write("**Recommendation:** Upgrade to **Express Air** or split the shipment.")
            
        elif risk_score > 30:
            st.warning(f"⚖️ MODERATE RISK: {risk_score:.1f}% Chance of Delay")
            st.write("**Recommendation:** Allow 1-2 days buffer time.")
            
        else:
            st.success(f"✅ EXCELLENT ROUTE: Only {risk_score:.1f}% Chance of Delay")
            st.write(f"**Insight:** **{state}** has strong logistics connectivity.")
