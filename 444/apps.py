import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression

#  Page Config 
st.set_page_config(page_title="Renewable Grid Optimizer", layout="wide")

@st.cache_data
def load_and_merge_data():
    try:
        # Loading files (Ensure these are in your local directory)
        df_cons = pd.read_csv("Country_Consumption_TWH.csv")
        df_gen = pd.read_csv("renewablePowerGeneration97-17.csv")

        df_cons['Year'] = pd.to_numeric(df_cons['Year'], errors='coerce')
        df_gen['Year'] = pd.to_numeric(df_gen['Year'], errors='coerce')
        
        merged_df = pd.merge(df_cons, df_gen, on='Year', how='inner')
        
        renew_cols = ['Hydro(TWh)', 'Biofuel(TWh)', 'Solar PV (TWh)', 'Geothermal (TWh)']
        merged_df['Total_Renewable_TWh'] = merged_df[renew_cols].sum(axis=1)
        
        return merged_df, renew_cols
    except Exception as e:
        st.error(f"Error: {e}")
        return None, None

df, renewable_cols = load_and_merge_data()

if df is not None:
    # Sidebar: Grid Controls
    st.sidebar.title(" Grid Controls")
    
    excluded = ['Year', 'Total_Renewable_TWh'] + renewable_cols
    countries = [col for col in df.columns if col not in excluded]
    selected_country = st.sidebar.selectbox("Select Region", countries)
    
    #  NEW FEATURE: Grid Stability Logic 
    st.sidebar.markdown("---")
    st.sidebar.subheader(" Stability Monitor")
    
    latest_data = df.iloc[-1]
    demand = latest_data[selected_country]
    supply = latest_data['Total_Renewable_TWh']
    
    # Stability is a ratio of supply vs demand
    stability_ratio = (supply / demand)
    
    if stability_ratio > 1.2:
        status = "Surplus"
        color = "green"
        info = "Grid is highly stable. Excess energy available."
    elif 0.9 <= stability_ratio <= 1.2:
        status = "Balanced"
        color = "blue"
        info = "Supply matches demand. Optimal performance."
    else:
        status = "Critical"
        color = "red"
        info = "Demand exceeds renewable supply. Backup required."

    st.sidebar.metric("Grid Status", status, f"{stability_ratio:.2f} S/D Ratio")
    st.sidebar.write(f":{color}[{info}]")
    
    # Manual Stability Simulation Slider
    sim_load = st.sidebar.slider("Simulate Load Stress (%)", 50, 150, 100)
    current_load = demand * (sim_load / 100)
    
    # Main Dashboard 
    st.title("Renewable Energy Grid Management")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Live Load", f"{current_load:.2f} TWh", f"{sim_load-100}% Shift")
    m2.metric("Renewable Capacity", f"{supply:.2f} TWh")
    m3.metric("Grid Frequency", "50.01 Hz", "Normal")

    #  Visualizations 
    t1, t2 = st.tabs(["Analytics", "Stability Mapping"])
    
    with t1:
        fig_mix = px.area(df, x='Year', y=renewable_cols, title="Generation Mix Over Time")
        st.plotly_chart(fig_mix, use_container_width=True)
        
    with t2:
        st.subheader("Supply vs Demand Gap")
        fig_gap = go.Figure()
        fig_gap.add_trace(go.Bar(x=['Renewable Supply', 'Projected Demand'], 
                                 y=[supply, current_load],
                                 marker_color=[ 'green', 'orange']))
        fig_gap.update_layout(yaxis_title="Terawatt-hours (TWh)")
        st.plotly_chart(fig_gap, use_container_width=True)

else:
    st.info("Please ensure your CSV files are in the directory to activate the Stability Monitor.")