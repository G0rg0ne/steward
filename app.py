import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os

st.set_page_config(
    page_title="Flight Deals Dashboard",
    page_icon="✈️",
    layout="wide"
)

def load_flight_data():
    """Load flight data from the JSON file"""
    try:
        with open('logs/flight_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def main():
    st.title("✈️ Flight Deals Dashboard")
    
    # Load flight data
    flight_data = load_flight_data()
    
    if not flight_data:
        st.warning("No flight data available yet. Check back later!")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(flight_data)
    
    # Display latest update time
    latest_update = datetime.fromisoformat(df['timestamp'].max())
    st.write(f"Last updated: {latest_update.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create tabs for different routes
    routes = df['route'].unique()
    tabs = st.tabs([f"Route: {route}" for route in routes])
    
    for tab, route in zip(tabs, routes):
        with tab:
            route_data = df[df['route'] == route].sort_values('timestamp', ascending=False)
            
            # Display latest results
            latest_results = route_data.iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Outbound Flights")
                outbound_df = pd.DataFrame(latest_results['outbound'])
                if not outbound_df.empty:
                    st.dataframe(outbound_df)
                else:
                    st.info("No outbound flights found")
            
            with col2:
                st.subheader("Return Flights")
                return_df = pd.DataFrame(latest_results['return'])
                if not return_df.empty:
                    st.dataframe(return_df)
                else:
                    st.info("No return flights found")
            
            # Display AI analysis
            st.subheader("AI Analysis")
            st.write(latest_results['analysis'])

if __name__ == "__main__":
    main() 