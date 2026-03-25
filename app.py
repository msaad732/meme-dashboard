import streamlit as st
import pandas as pd
import os
from sqlalchemy import create_engine

# 1. Setup the webpage
st.set_page_config(page_title="Crypto Dashboard", layout="wide")
st.title("Live Registration Data")

# 2. Securely get the Database URL
db_url = os.environ.get("DATABASE_URL")

if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# 3. Fetch the data
@st.cache_data(ttl=30)
def load_data():
    engine = create_engine(db_url)
    # Table remains Ascending (Oldest at top, Newest at bottom)
    query = "SELECT * FROM ticks ORDER BY timestamp ASC;" 
    df = pd.read_sql(query, engine)
    return df

if db_url:
    try:
        raw_data = load_data()
        
        # --- SIDEBAR FILTER LOGIC ---
        # Get unique symbols in order of appearance
        ordered_symbols = list(dict.fromkeys(raw_data['symbol'].tolist()))
        
        # REVERSE the list so the newest symbol is at the top of the sidebar
        newest_first_symbols = ordered_symbols[::-1]
        
        sidebar_options = ["All Coins"] + newest_first_symbols
        
        st.sidebar.header("Filter Options")
        selected_symbol = st.sidebar.selectbox("Select a Symbol:", sidebar_options)

        # 2. Apply the filter to the table
        if selected_symbol == "All Coins":
            filtered_data = raw_data
        else:
            filtered_data = raw_data[raw_data['symbol'] == selected_symbol]
        # ---------------------------

        # Display the table (Sorted ASC by timestamp)
        st.dataframe(filtered_data, use_container_width=True, hide_index=True)
        
        # Sidebar Refresh Button
        if st.sidebar.button("Refresh Data Now"):
            st.cache_data.clear()
            st.rerun()
            
    except Exception as e:
        st.error(f"Error loading data: {e}")
else:
    st.error("DATABASE_URL not found.")
