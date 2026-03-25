import streamlit as st
import pandas as pd
import os
from sqlalchemy import create_engine

# 1. Setup the webpage
st.set_page_config(page_title="Crypto Tick Dashboard", layout="wide")
st.title("Live Registration Data")

# 2. Securely get the Database URL
db_url = os.environ.get("DATABASE_URL")

if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# 3. Fetch the data
@st.cache_data(ttl=30) # Reduced to 30s for more frequent updates
def load_data():
    engine = create_engine(db_url)
    query = "SELECT * FROM ticks ORDER BY timestamp DESC;" # Added ORDER BY to see newest first
    df = pd.read_sql(query, engine)
    return df

if db_url:
    try:
        raw_data = load_data()
        
        # --- NEW FILTER SECTION ---
        # Get unique symbols for the dropdown
        symbols = ["All Coins"] + sorted(raw_data['symbol'].unique().tolist())
        
        st.sidebar.header("Filter Options")
        selected_symbol = st.sidebar.selectbox("Select a Symbol:", symbols)

        # Apply the filter
        if selected_symbol == "All Coins":
            filtered_data = raw_data
        else:
            filtered_data = raw_data[raw_data['symbol'] == selected_symbol]
        # ---------------------------

        # Display the table
        st.dataframe(filtered_data, use_container_width=True, hide_index=True)
        
        # Manual Refresh
        if st.sidebar.button("Refresh Data Now"):
            st.cache_data.clear()
            st.rerun()
            
    except Exception as e:
        st.error(f"Error loading data: {e}")
else:
    st.error("DATABASE_URL not found.")
