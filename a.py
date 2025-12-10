import streamlit as st
import pandas as pd
import numpy as np
import time

# ==========================================
# 1. APP CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="AI Delivery Risk Predictor",
    page_icon="🤖",
    layout="centered"
)

# ==========================================
# 2. THE "DUMMY" ML MODEL
# ==========================================
# In a real project, you would load a trained model here using: 
# model = joblib.load('my_logistic_regression_model.pkl')
# For now, we simulate the model's logic with a function.

def predict_delay_risk(region, ship_mode, category, distance):
    """
    Simulates a Machine Learning prediction.
    Returns: Probability of Delay (0 to 100%)
    """
    base_risk = 10  # 10% base risk
    
    # Logic: Certain regions are riskier
    if region in ['Africa', 'Latin America']:
        base_risk += 30
    elif region == 'Asia Pacific':
        base_risk += 20
        
    # Logic: Standard Class is slower/riskier
    if ship_mode == 'Standard Class':
        base_risk += 40
    elif ship_mode == 'Second Class':
        base_risk += 20
        
    # Logic: Distance adds risk
    base_risk += (distance / 100)  # Add 1% risk for every 100km
    
    # Cap at 99%
    final_risk = min(base_risk + np.random.randint(-5, 5), 99)
    return max(final_risk, 1)

# ==========================================
# 3. THE USER INTERFACE (UI)
# ==========================================
st.title("🤖 Logistics AI Assistant")
st.markdown("### Pre-Shipment Risk Calculator")
st.info("Use this tool BEFORE booking a shipment to see if it will be late.")

st.markdown("---")

# --- USER INPUT FORM ---
with st.form("prediction_form"):
    st.write("#### 📦 Shipment Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        region = st.selectbox("Destination Region", 
            ['North America', 'Europe', 'Asia Pacific', 'Latin America', 'Africa'])
        category = st.selectbox("Product Category", 
            ['Furniture', 'Technology', 'Office Supplies'])
            
    with col2:
        ship_mode = st.selectbox("Shipping Mode", 
            ['Standard Class', 'Second Class', 'First Class', 'Same Day'])
        distance = st.slider("Estimated Distance (km)", 100, 5000, 1200)
        
    submitted = st.form_submit_button("🔮 Predict Risk")

# ==========================================
# 4. PREDICTION OUTPUT
# ==========================================
if submitted:
    with st.spinner('Running Risk Algorithm...'):
        time.sleep(1.5) # Simulate processing time
        
        # Get the prediction
        risk_score = predict_delay_risk(region, ship_mode, category, distance)
        
        st.markdown("---")
        st.subheader("Analysis Result")
        
        # Display Logic
        if risk_score > 60:
            st.error(f"⚠️ HIGH RISK DETECTED: {risk_score:.1f}% Probability of Delay")
            st.write(f"**Recommendation:** Do NOT use {ship_mode}. Upgrade to **First Class** immediately.")
        elif risk_score > 30:
            st.warning(f"⚖️ MODERATE RISK: {risk_score:.1f}% Probability of Delay")
            st.write("**Recommendation:** Monitor this shipment closely.")
        else:
            st.success(f"✅ SAFE TO SHIP: Only {risk_score:.1f}% Probability of Delay")
            st.write("**Recommendation:** Proceed with booking.")
