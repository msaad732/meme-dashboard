
# 📈 Solana Meme Coin Tracker — Live Dashboard

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)

**The real-time data visualization frontend and control interface for the Solana Meme Coin Tracker system.**

---

## 🌍 The Big Picture
This repository contains the interactive dashboard component of the broader Meme Coin Tracking ecosystem. While the backend worker handles the heavy lifting of API polling, blockchain scraping, and data insertion, this application serves as the user-facing command center.

Built with **Streamlit**, it connects directly to the system's PostgreSQL database to visualize high-frequency trading data and interacts with the backend worker via REST APIs to control tracking parameters on the fly.

## ✨ Core Features
* **Real-Time Data Matrix:** Polls the database every 30 seconds to display live metrics (market cap, buy/sell ratios, sniper bot percentages) for all actively tracked tokens.
* **Telegram Signal Integration:** Dedicated filtering to isolate and monitor coins discovered autonomously via the Telegram scraper.
* **API Command Center:** Includes a manual tracking interface that sends `POST` requests directly to the background worker (`/track`) to force-initiate tracking on newly discovered contract addresses.
* **System Status Polling:** Pings the backend worker's `/status` endpoint to monitor active tracker counts and Telegram listener health in real time.

---

## 💻 Technical Architecture
* **Frontend Framework:** Streamlit (leveraging `@st.cache_data` with TTL for optimized, low-latency database polling without overloading the server).
* **Data Handling:** Pandas for rapid dataframe manipulation and UI rendering.
* **Database Connection:** SQLAlchemy for secure, read-only querying of the PostgreSQL metrics database.
* **Microservice Communication:** Python `requests` library for sending commands to the isolated backend worker instance.

---

## 🚀 Developer Quick Start

### 1. Environment Setup
Clone the repository and set up your Python virtual environment:
```bash
git clone [https://github.com/msaad732/meme-dashboard.git](https://github.com/msaad732/meme-dashboard.git)
cd meme-dashboard
python -m venv venv

# Activate the virtual environment:
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

pip install -r requirements.txt
````

### 2\. Environment Variables

This dashboard requires access to both the database and the backend worker API. Create a `.env` file or export these variables in your terminal:

```env
# The direct connection string to your PostgreSQL database
DATABASE_URL=postgresql://user:password@localhost:5432/meme_db

# The URL where your backend tracker worker is hosted
WORKER_URL=[https://your-worker-url.up.railway.app](https://your-worker-url.up.railway.app)
```

### 3\. Launch the Dashboard

Run the Streamlit server:

```bash
streamlit run app.py
```

The live dashboard will be accessible at `http://localhost:8501`.

-----

## 🔗 Related Repositories

  * **[Solana-Meme-Coin-Tracker](https://www.google.com/search?q=https://github.com/msaad732/Solana-Meme-Coin-Tracker):** The core backend worker responsible for blockchain data scraping, Telegram listening, and writing to the database.

