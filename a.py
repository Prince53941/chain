import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import random
from datetime import datetime, timedelta

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Supply Chain Analytics Dashboard",
    page_icon="📦",
    layout="wide"
)

# ==========================================
# 2. DATA GENERATION & CACHING
# ==========================================
@st.cache_data
def load_data():
    """Generates synthetic supply chain data for demonstration."""
    rows = 2000
    shipping_modes = ['Standard Class', 'First Class', 'Second Class', 'Same Day']
    regions = ['North America', 'Europe', 'Asia Pacific', 'Latin America', 'Africa']
    categories = ['Furniture', 'Office Supplies', 'Technology']
    
    data = []
    for _ in range(rows):
        order_date = datetime(2023, 1, 1) + timedelta(days=random.randint(0, 365))
        scheduled_days = random.randint(2, 5)
        # Introduce randomness for delays
        actual_days = scheduled_days + random.randint(-1, 3) 
        
        data.append({
            'Order_ID': f"ORD-{random.randint(10000, 99999)}",
            'Order_Date': order_date,
            'Ship_Mode': random.choice(shipping_modes),
            'Region': random.choice(regions),
            'Category': random.choice(categories),
            'Sales': round(random.uniform(50, 2000), 2),
            'Scheduled_Days': scheduled_days,
            'Actual_Days': actual_days
        })
    
    df = pd.DataFrame(data)
    
    # Feature Engineering (Analysis Logic)
    conditions = [
        (df['Actual_Days'] > df['Scheduled_Days']),
        (df['Actual_Days'] < df['Scheduled_Days']),
        (df['Actual_Days'] == df['Scheduled_Days'])
    ]
    choices = ['Late', 'Early', 'On Time']
    df['Delivery_Status'] = np.select(conditions, choices, default='Unknown')
    
    # Calculate Delay Severity (0 if not late)
    df['Days_Delayed'] = df['Actual_Days'] - df['Scheduled_Days']
    df['Days_Delayed'] = df['Days_Delayed'].apply(lambda x: x if x > 0 else 0)
    
    # Calculate Revenue at Risk (Assuming 5% loss on late orders)
    df['Revenue_Loss_Risk'] = np.where(df['Delivery_Status'] == 'Late', df['Sales'] * 0.05, 0)
    
    return df

# Load the data
df = load_data()

# ==========================================
# 3. SIDEBAR FILTERS
# ==========================================
st.sidebar.header("🔍 Filter Options")

# Filter by Region
region_filter = st.sidebar.multiselect(
    "Select Region:",
    options=df['Region'].unique(),
    default=df['Region'].unique()
)

# Filter by Shipping Mode
mode_filter = st.sidebar.multiselect(
    "Select Shipping Mode:",
    options=df['Ship_Mode'].unique(),
    default=df['Ship_Mode'].unique()
)

# Apply filters
df_selection = df.query(
    "Region == @region_filter & Ship_Mode == @mode_filter"
)

# ==========================================
# 4. MAIN DASHBOARD UI
# ==========================================
st.title("📦 Supply Chain Performance Dashboard")
st.markdown("### Real-time analytics for Delivery Efficiency and Risk")
st.markdown("---")

# --- TOP KPI METRICS ---
total_sales = df_selection['Sales'].sum()
total_loss = df_selection['Revenue_Loss_Risk'].sum()
late_rate = (df_selection[df_selection['Delivery_Status'] == 'Late'].shape[0] / df_selection.shape[0]) * 100
avg_delay = df_selection[df_selection['Delivery_Status'] == 'Late']['Days_Delayed'].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Sales", f"${total_sales:,.0f}")
col2.metric("Revenue at Risk (Late)", f"${total_loss:,.0f}", "-Loss", delta_color="inverse")
col3.metric("Late Delivery Rate", f"{late_rate:.1f}%", "-High Risk" if late_rate > 25 else "Normal")
col4.metric("Avg Delay (Days)", f"{avg_delay:.1f} Days")

st.markdown("---")

# --- ROW 1: CHARTS ---
c1, c2 = st.columns((2, 1))

with c1:
    st.subheader("📅 Delivery Status Distribution")
    # Pie Chart
    fig_pie = px.pie(
        df_selection, 
        names='Delivery_Status', 
        values='Sales',
        title='Sales Volume by Delivery Status',
        color='Delivery_Status',
        color_discrete_map={'Late':'#FF4B4B', 'On Time':'#00CC96', 'Early':'#636EFA'}
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with c2:
    st.subheader("⚠️ Risk by Ship Mode")
    # Bar Chart for Delays
    avg_delay_by_mode = df_selection.groupby('Ship_Mode')['Days_Delayed'].mean().reset_index()
    fig_bar = px.bar(
        avg_delay_by_mode,
        x='Ship_Mode',
        y='Days_Delayed',
        title='Avg Delay Days by Mode',
        color='Days_Delayed',
        color_continuous_scale='Reds'
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# --- ROW 2: DETAILED ANALYSIS ---
c3, c4 = st.columns(2)

with c3:
    st.subheader("🌎 Regional Performance")
    # Interactive Bar/Map proxy
    fig_region = px.histogram(
        df_selection, 
        x='Region', 
        y='Revenue_Loss_Risk', 
        color='Region',
        title='Total Revenue at Risk by Region'
    )
    st.plotly_chart(fig_region, use_container_width=True)

with c4:
    st.subheader("📈 Trend Over Time")
    # Time Series
    # Group by Month for cleaner trend
    df_selection['Month'] = df_selection['Order_Date'].dt.to_period('M').astype(str)
    monthly_late = df_selection[df_selection['Delivery_Status'] == 'Late'].groupby('Month').size().reset_index(name='Late_Count')
    
    fig_line = px.line(
        monthly_late,
        x='Month',
        y='Late_Count',
        markers=True,
        title='Number of Late Deliveries per Month'
    )
    st.plotly_chart(fig_line, use_container_width=True)

# --- DATA TABLE VIEW ---
with st.expander("🔎 View Raw Data"):
    st.dataframe(df_selection)
