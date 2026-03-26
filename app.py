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
    return pd.read_sql("SELECT * FROM ticks ORDER BY timestamp ASC;", engine)


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

# Telegram status in sidebar
st.sidebar.divider()
st.sidebar.subheader("Telegram Listener")
try:
    r = requests.get(f"{API_URL}/status", timeout=4)
    tg = r.json().get("telegram", {})
    if not tg.get("enabled"):
        st.sidebar.warning("Disabled (session not set)")
    elif tg.get("connected"):
        st.sidebar.success(f"Connected to @{tg.get('channel', '')}")
        st.sidebar.caption(f"Signals received: {tg.get('signals_received', 0)}")
        if tg.get("last_signal"):
            st.sidebar.caption(f"Last signal: {tg['last_signal']}")
    else:
        st.sidebar.error("Enabled but not connected")
except Exception:
    st.sidebar.caption("Worker unreachable")

# ── Tabs ──────────────────────────────────────────────────────────────
tab_all, tab_tg, tab_manual = st.tabs(["All Coins", "Telegram Signals", "Track a Coin"])


def _show_table(df):
    if df.empty:
        st.info("No data yet.")
        return
    filtered = df if selected == "All Coins" else df[df["symbol"] == selected]
    st.dataframe(filtered, use_container_width=True, hide_index=True)
    st.caption(f"{len(filtered):,} rows | auto-refreshes every 30 s")


# ── Tab 1: All coins ──────────────────────────────────────────────────
with tab_all:
    if db_url:
        try:
            _show_table(raw_data)
        except Exception as e:
            st.error(f"Error loading data: {e}")
    else:
        st.error("DATABASE_URL not set.")

# ── Tab 2: Telegram-only coins ────────────────────────────────────────
with tab_tg:
    if db_url:
        try:
            if not raw_data.empty and "source" in raw_data.columns:
                tg_data = raw_data[raw_data["source"] == "telegram"]
                _show_table(tg_data)
            elif not raw_data.empty:
                st.info("source column not yet present — redeploy worker to enable this tab.")
            else:
                st.info("No Telegram signals tracked yet.")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.error("DATABASE_URL not set.")

# ── Tab 3: Manual / Telegram address input ────────────────────────────
with tab_manual:
    st.subheader("Track a coin by address")
    st.write("Paste any Solana token address below.")

    address_input = st.text_input("Token address", placeholder="e.g. B4xht9gaypZthqtHvCnt1TWUwdxvV8jDKajgrHxPpump")

    if st.button("Start Tracking"):
        addr = address_input.strip()
        if not addr:
            st.warning("Enter a token address first.")
        else:
            try:
                resp = requests.post(f"{API_URL}/track", json={"address": addr}, timeout=10)
                if resp.status_code == 200:
                    st.success(f"Started tracking `{addr[:8]}...` — data appears in All Coins tab within 30 s.")
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
            st.metric("Coins being tracked", data.get("count", 0))
            active = data.get("active", [])
            if active:
                st.write(active)
        except Exception as e:
            st.error(f"Could not reach worker API: {e}")
