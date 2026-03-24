import streamlit as st
import pandas as pd
import os
from sqlalchemy import create_engine

# 1. Setup the webpage
st.set_page_config(page_title=" Data Dashboard", layout="wide")
st.title("Live Registration Data")

# 2. Securely get the Database URL from Railway's environment
db_url = os.environ.get("DATABASE_URL")

# SQLAlchemy requires 'postgresql://' but Railway sometimes defaults to 'postgres://'
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# 3. Fetch the data (Cached for 60 seconds so it doesn't overwhelm the database)
@st.cache_data(ttl=60) 
def load_data():
    engine = create_engine(db_url)
    
    # IMPORTANT: Change 'your_table_name' to your actual Postgres table name
    query = "SELECT * FROM ticks;"
    
    df = pd.read_sql(query, engine)
    return df

# 4. Display the data
if db_url:
    try:
        data = load_data()
        
        # Shows a beautiful, interactive table
        st.dataframe(data, use_container_width=True, hide_index=True)
        
        # Optional: Adds a manual refresh button
        if st.button("Refresh Data Now"):
            st.cache_data.clear()
            st.rerun()
            
    except Exception as e:
        st.error(f"Error loading data: {e}")
else:
    st.error("Could not find the database connection. Ensure this app is in the same Railway project as the database.")
