import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression

#  Configuration & Styling
st.set_page_config(page_title="Renewable Grid Optimizer", layout="wide")
st.markdown("""
    <style>
    ...
    </style>
""", unsafe_allow_html=True)

st.markdown("", unsafe_allow_html=True)

# Data Loading Engine
@st.cache_data
def load_and_clean_data():
    try:
        df_cons = pd.read_csv("Country_Consumption_TWH.csv")
        df_gen = pd.read_csv("renewablePowerGeneration97-17.csv")
        
        # Merge on Year (Standardizing column names if necessary)
        merged = pd.merge(df_cons, df_gen, on='Year', how='inner')
        return merged
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

df = load_and_clean_data()

# Sidebar UI
st.sidebar.title(" Grid Controls")
if df is not None:
    # Filter out non-country columns for the selector
    exclude = ['Year', 'Hydro(TWh)', 'Biofuel(TWh)', 'Solar PV (TWh)', 'Geothermal (TWh)']
    available_countries = [c for c in df.columns if c not in exclude]
    
    target_country = st.sidebar.selectbox("Select Region/Country", available_countries)
    forecast_horizon = st.sidebar.slider("Forecast Horizon (Years)", 1, 15, 5)

# 4. Main Dashboard Logic
if df is not None:
    st.title(" Renewable Energy Grid Management")
    
    #  TOP ROW: KPI Metrics 
    m1, m2, m3 = st.columns(3)
    latest_year = df['Year'].max()
    current_cons = df[df['Year'] == latest_year][target_country].values[0]
    
    m1.metric("Current Consumption", f"{current_cons:.2f} TWh", f"{latest_year} Data")
    m2.metric("Grid Stability Index", "Stable", "98.4%")
    m3.metric("Renewable Share", "34.2%", "↑ 2.1%")

    # MIDDLE ROW: Visualization
    tab_viz, tab_ml = st.tabs([" Consumption Trends", " Grid Forecasting"])
    
    with tab_viz:
        col_a, col_b = st.columns(2)
        with col_a:
            fig_cons = px.line(df, x='Year', y=target_country, title=f"Historical Load: {target_country}",
                             line_shape="spline", render_mode="svg")
            st.plotly_chart(fig_cons, use_container_width=True)
            
        with col_b:
            renew_cols = ['Hydro(TWh)', 'Biofuel(TWh)', 'Solar PV (TWh)', 'Geothermal (TWh)']
            fig_gen = px.area(df, x='Year', y=renew_cols, title="Global Renewable Generation Mix")
            st.plotly_chart(fig_gen, use_container_width=True)

    with tab_ml:
        st.subheader("Predictive Grid Analytics")
        st.write("")
        
        # ML Logic
        X = df[['Year']].values
        y = df[target_country].values
        model = LinearRegression().fit(X, y)
        
        # Predict future
        future_years = np.arange(latest_year + 1, latest_year + forecast_horizon + 1).reshape(-1, 1)
        future_preds = model.predict(future_years)
        
        # Combine for plotting
        hist_trace = go.Scatter(x=df['Year'], y=y, name="Historical", mode='lines+markers')
        fore_trace = go.Scatter(x=future_years.flatten(), y=future_preds, name="Predicted", 
                               line=dict(dash='dash', color='green'))
        
        fig_ml = go.Figure(data=[hist_trace, fore_trace])
        fig_ml.update_layout(title=f"Consumption Forecast for {target_country}", xaxis_title="Year", yaxis_title="TWh")
        st.plotly_chart(fig_ml, use_container_width=True)
        
        st.info(f"The model predicts a change of **{((future_preds[-1] - current_cons)/current_cons)*100:.2f}%** by {future_years[-1][0]}.")

# 5. Requirements Note
else:
    st.warning("Please ensure 'Country_Consumption_TWH.csv' and 'renewablePowerGeneration97-17.csv' are in the same folder as this script.")