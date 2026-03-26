import streamlit as st
import pandas as pd
import os
import requests
from sqlalchemy import create_engine

st.set_page_config(page_title="Meme Coin Tracker", layout="wide")
st.title("Meme Coin Tracker — Live Data")

# Database setup
db_url = os.environ.get("DATABASE_URL")
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

API_URL = os.environ.get("WORKER_URL", "https://worker-production-45e2.up.railway.app")


@st.cache_data(ttl=30)
def load_data():
    engine = create_engine(db_url)
    query = "SELECT * FROM ticks ORDER BY timestamp ASC;"
    return pd.read_sql(query, engine)


# ── Sidebar ───────────────────────────────────────────────────────────
st.sidebar.header("Filter")

if db_url:
    try:
        raw_data = load_data()
        ordered_symbols = list(dict.fromkeys(raw_data["symbol"].tolist()))
        newest_first = ordered_symbols[::-1]
        selected = st.sidebar.selectbox("Symbol", ["All Coins"] + newest_first)
    except Exception:
        raw_data = pd.DataFrame()
        selected = "All Coins"
else:
    raw_data = pd.DataFrame()
    selected = "All Coins"

if st.sidebar.button("Refresh Now"):
    st.cache_data.clear()
    st.rerun()

# ── Tabs ──────────────────────────────────────────────────────────────
tab_data, tab_manual = st.tabs(["Live Data", "Track a Coin"])

# ── Tab 1: Live data table ────────────────────────────────────────────
with tab_data:
    if db_url:
        try:
            if not raw_data.empty:
                filtered = raw_data if selected == "All Coins" else raw_data[raw_data["symbol"] == selected]
                st.dataframe(filtered, use_container_width=True, hide_index=True)
                st.caption(f"{len(filtered):,} rows | auto-refreshes every 30 s")
            else:
                st.info("No data yet — tracker is warming up.")
        except Exception as e:
            st.error(f"Error loading data: {e}")
    else:
        st.error("DATABASE_URL not set.")

# ── Tab 2: Manual / Telegram address tracking ─────────────────────────
with tab_manual:
    st.subheader("Track a coin by address")
    st.write("Paste any Solana token address below. Works for coins found on Telegram or anywhere else.")

    address_input = st.text_input("Token address", placeholder="e.g. B4xht9gaypZthqtHvCnt1TWUwdxvV8jDKajgrHxPpump")

    if st.button("Start Tracking"):
        addr = address_input.strip()
        if not addr:
            st.warning("Enter a token address first.")
        else:
            try:
                resp = requests.post(f"{API_URL}/track", json={"address": addr}, timeout=10)
                if resp.status_code == 200:
                    st.success(f"Started tracking `{addr[:8]}...` — data will appear in Live Data tab within 30 s.")
                elif resp.status_code == 409:
                    st.info("Already tracking this address.")
                else:
                    st.error(f"API error {resp.status_code}: {resp.text}")
            except Exception as e:
                st.error(f"Could not reach worker API: {e}")

    st.divider()
    st.subheader("Active trackers")
    if st.button("Check status"):
        try:
            resp = requests.get(f"{API_URL}/status", timeout=5)
            data = resp.json()
            count = data.get("count", 0)
            active = data.get("active", [])
            st.metric("Coins being tracked", count)
            if active:
                st.write(active)
        except Exception as e:
            st.error(f"Could not reach worker API: {e}")
