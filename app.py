import streamlit as st
import pandas as pd
import os
import requests
from sqlalchemy import create_engine

st.set_page_config(page_title="Crypto Dashboard", layout="wide")
st.title("Live Meme Coin Tracker")

db_url  = os.environ.get("DATABASE_URL")
api_url = "https://worker-production-45e2.up.railway.app"

if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

@st.cache_data(ttl=30)
def load_data():
    engine = create_engine(db_url)
    df = pd.read_sql("SELECT * FROM ticks ORDER BY timestamp ASC;", engine)
    return df

if db_url:
    try:
        raw_data = load_data()
        ordered_symbols    = list(dict.fromkeys(raw_data['symbol'].tolist()))
        newest_first       = ordered_symbols[::-1]
        sidebar_options    = ["All Coins"] + newest_first

        st.sidebar.header("Filter Options")
        selected_symbol = st.sidebar.selectbox("Select a Symbol:", sidebar_options)
        filtered_data   = raw_data if selected_symbol == "All Coins" else raw_data[raw_data['symbol'] == selected_symbol]

        st.sidebar.markdown("---")
        st.sidebar.subheader("Track a Coin Manually")
        addr = st.sidebar.text_input("Token Address")
        if st.sidebar.button("Start Tracking"):
            if addr.strip():
                try:
                    res = requests.post(f"{api_url}/track", json={"address": addr.strip()}, timeout=10)
                    if res.status_code == 200:
                        st.sidebar.success("Started! Data appears in ~30 seconds.")
                    elif res.status_code == 409:
                        st.sidebar.warning("Already tracking this coin.")
                    else:
                        st.sidebar.error(res.json().get("error", "Error starting tracker."))
                except Exception as e:
                    st.sidebar.error(f"API error: {e}")
            else:
                st.sidebar.warning("Please enter a token address.")

        st.sidebar.markdown("---")
        st.sidebar.subheader("Active Trackers")
        try:
            status = requests.get(f"{api_url}/status", timeout=5).json()
            st.sidebar.metric("Running", status.get("count", 0))
            for a in status.get("active", []):
                st.sidebar.caption(f"• {a[:8]}...")
        except Exception:
            st.sidebar.caption("Could not fetch status.")

        st.sidebar.markdown("---")
        if st.sidebar.button("Refresh Data Now"):
            st.cache_data.clear()
            st.rerun()

        st.dataframe(filtered_data, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Error loading data: {e}")
else:
    st.error("DATABASE_URL not found.")
