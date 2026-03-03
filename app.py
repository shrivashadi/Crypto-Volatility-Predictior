import streamlit as st
import pandas as pd
import numpy as np
import joblib
from pymongo import MongoClient
import os
from datetime import datetime

# --- MongoDB Configuration ---
# 'db' hostname is linked to the service name in docker-compose.yml
MONGO_URI = os.getenv("MONGO_URI", "mongodb://db:27017/")
client = MongoClient(MONGO_URI)
db = client['crypto_db']
collection = db['predictions']

def save_to_mongo(input_data, prediction_val, category):
    """Saves the input parameters and prediction results to MongoDB"""
    try:
        record = {
            "timestamp": datetime.now(),
            "inputs": input_data,
            "prediction": float(prediction_val),
            "risk_level": category
        }
        collection.insert_one(record)
    except Exception as e:
        st.error(f"Database Error: {e}")

# --- Page Config ---
st.set_page_config(
    page_title="Crypto Volatility Predictor",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Your Full Custom CSS (Restored) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Syne', sans-serif; background-color: #0a0a0f; color: #e8e8f0; }
.stApp { background: radial-gradient(ellipse at top left, #0f1a2e 0%, #0a0a0f 50%, #0d0a1a 100%); min-height: 100vh; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0f1a2e 0%, #0a0f1e 100%); border-right: 1px solid rgba(255, 180, 0, 0.15); }
.hero-header { text-align: center; padding: 2.5rem 0 1.5rem; }
.hero-title { font-family: 'Syne', sans-serif; font-weight: 800; font-size: 3.5rem; background: linear-gradient(135deg, #ffffff 0%, #ffb400 50%, #ff6b35 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.metric-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 1.2rem; text-align: center; }
.result-box { border-radius: 16px; padding: 2rem; margin: 1.5rem 0; text-align: center; border: 1px solid rgba(255,180,0,0.4); }
.result-box.high { background: rgba(255,60,60,0.1); border-color: #ff4444; }
.result-box.medium { background: rgba(255,180,0,0.1); border-color: #ffb400; }
.result-box.low { background: rgba(0,210,120,0.1); border-color: #00d478; }
.gold-divider { height: 1px; background: linear-gradient(90deg, transparent, #ffb400, transparent); margin: 2rem 0; opacity: 0.3; }
.tag { display: inline-block; background: rgba(255,180,0,0.1); color: #ffb400; padding: 0.2rem 0.6rem; border-radius: 4px; margin: 0.2rem; font-size: 0.7rem; }
</style>
""", unsafe_allow_html=True)

# --- Load Model ---
@st.cache_resource
def load_model():
    model  = joblib.load('xgb_model.pkl')
    scaler = joblib.load('scaler.pkl')
    return model, scaler

model, scaler = load_model()

# --- Sidebar ---
with st.sidebar:
    st.markdown("<p style='color:#ffb400; font-family:Space Mono;'>⬡ Input Market Data</p>", unsafe_allow_html=True)
    open_p     = st.number_input("Open Price (USD)", value=30000.0)
    high_p     = st.number_input("High Price (USD)", value=31000.0)
    low_p      = st.number_input("Low Price (USD)", value=29000.0)
    close_p    = st.number_input("Close Price (USD)", value=30500.0)
    volume     = st.number_input("Trading Volume", value=1_000_000_000.0)
    market_cap = st.number_input("Market Cap (USD)", value=500_000_000_000.0)
    predict_btn = st.button("⚡ Predict Volatility")

# --- Hero Section ---
st.markdown("<div class='hero-header'><h1 class='hero-title'>Crypto Volatility Predictor</h1></div>", unsafe_allow_html=True)

# --- Metric Row ---
col1, col2, col3, col4 = st.columns(4)
metrics = [("81%", "R² Accuracy"), ("0.0072", "RMSE Score"), ("0.0047", "MAE Score"), ("3012", "Training Rows")]
for col, (val, label) in zip([col1, col2, col3, col4], metrics):
    col.markdown(f"<div class='metric-card'><div style='color:#ffb400; font-size:1.5rem;'>{val}</div><div style='color:#5a6a80; font-size:0.7rem;'>{label}</div></div>", unsafe_allow_html=True)

# --- Prediction Logic ---
if predict_btn:
    # Feature calculation logic
    price_range = high_p - low_p
    price_range_pct = price_range / close_p if close_p != 0 else 0
    close_open_pct = (close_p - open_p) / open_p if open_p != 0 else 0
    liquidity_ratio = volume / market_cap if market_cap != 0 else 0

    input_data = pd.DataFrame([[
        open_p, high_p, low_p, close_p, volume, close_p, close_p, close_p,
        price_range, price_range_pct, close_open_pct, 0.05, price_range,
        volume, 0.0, 1.0, liquidity_ratio, 0.03, 0.03, 0.03, 0.01, 0.01, 50.0
    ]], columns=['open','high','low','close','volume','MA_7','MA_14','MA_30','price_range','price_range_pct','close_open_pct','BB_width','ATR_14','volume_MA7','volume_change','volume_spike','liquidity_ratio','volatility_lag1','volatility_lag3','volatility_lag7','return_lag1','return_lag3','RSI_14'])

    scaled = scaler.transform(input_data)
    pred = model.predict(scaled)[0]

    # Classification logic
    if pred > 0.05:
        level, icon, label, desc = "high", "🔴", "HIGH VOLATILITY", "Market is highly unstable. High risk."
    elif pred > 0.02:
        level, icon, label, desc = "medium", "🟡", "MEDIUM VOLATILITY", "Market is moderately active."
    else:
        level, icon, label, desc = "low", "🟢", "LOW VOLATILITY", "Market is stable. Good for entries."

    # UI Result Display
    st.markdown(f"""
    <div class='result-box {level}'>
        <div style='font-size:3rem;'>{icon} {pred:.6f}</div>
        <div style='font-weight:bold; color:#ffb400;'>{label}</div>
        <div style='font-size:0.8rem; color:#7a8aa0;'>{desc}</div>
    </div>
    """, unsafe_allow_html=True)

    # --- SAVE TO MONGO ---
    input_summary = {"open": open_p, "high": high_p, "low": low_p, "close": close_p, "volume": volume}
    save_to_mongo(input_summary, pred, label)
    st.toast("Record saved to MongoDB", icon="💾")

# --- Footer ---
st.markdown("<div class='gold-divider'></div><div style='text-align:center;'><span class='tag'>XGBoost</span><span class='tag'>MongoDB Integrated</span></div>", unsafe_allow_html=True)
import streamlit as st
import pandas as pd
import numpy as np
import joblib
from pymongo import MongoClient # For Database
import os
from datetime import datetime

# --- MongoDB Setup ---
# Connects to the 'db' container defined in docker-compose
MONGO_URI = os.getenv("MONGO_URI", "mongodb://db:27017/")
client = MongoClient(MONGO_URI)
db = client['crypto_db']
collection = db['predictions']

def save_to_mongo(input_data, prediction_val, category):
    """Saves inputs and results to MongoDB"""
    try:
        record = {
            "timestamp": datetime.now(),
            "inputs": input_data,
            "prediction": float(prediction_val),
            "risk_level": category
        }
        collection.insert_one(record)
    except Exception as e:
        st.error(f"Database Error: {e}")

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Crypto Volatility Predictor",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS (Original Full Version) ───────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Syne', sans-serif; background-color: #0a0a0f; color: #e8e8f0; }
.stApp { background: radial-gradient(ellipse at top left, #0f1a2e 0%, #0a0a0f 50%, #0d0a1a 100%); min-height: 100vh; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0f1a2e 0%, #0a0f1e 100%); border-right: 1px solid rgba(255, 180, 0, 0.15); }
.hero-header { text-align: center; padding: 2.5rem 0 1.5rem; position: relative; }
.hero-badge { display: inline-block; background: rgba(255, 180, 0, 0.1); border: 1px solid rgba(255, 180, 0, 0.3); color: #ffb400; font-family: 'Space Mono', monospace; font-size: 0.7rem; letter-spacing: 0.25em; padding: 0.3rem 1rem; border-radius: 20px; margin-bottom: 1rem; text-transform: uppercase; }
.hero-title { font-family: 'Syne', sans-serif; font-weight: 800; font-size: clamp(2rem, 5vw, 3.5rem); line-height: 1.1; background: linear-gradient(135deg, #ffffff 0%, #ffb400 50%, #ff6b35 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin: 0; }
.metric-card { flex: 1; min-width: 150px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 1.2rem 1.5rem; text-align: center; transition: border-color 0.3s; }
.metric-value { font-family: 'Space Mono', monospace; font-size: 1.6rem; font-weight: 700; color: #ffb400; }
.result-box { border-radius: 16px; padding: 2rem 2.5rem; margin: 1.5rem 0; text-align: center; position: relative; overflow: hidden; }
.result-box.high { background: linear-gradient(135deg, rgba(255,60,60,0.15), rgba(255,60,60,0.05)); border: 1px solid rgba(255,60,60,0.4); }
.result-box.medium { background: linear-gradient(135deg, rgba(255,180,0,0.15), rgba(255,180,0,0.05)); border: 1px solid rgba(255,180,0,0.4); }
.result-box.low { background: linear-gradient(135deg, rgba(0,210,120,0.15), rgba(0,210,120,0.05)); border: 1px solid rgba(0,210,120,0.4); }
.result-volatility { font-family: 'Space Mono', monospace; font-size: 3rem; font-weight: 700; margin: 0; }
.gold-divider { height: 1px; background: linear-gradient(90deg, transparent, #ffb400, transparent); margin: 2rem 0; opacity: 0.3; }
.tag { display: inline-block; background: rgba(255,180,0,0.1); border: 1px solid rgba(255,180,0,0.25); color: #ffb400; font-family: 'Space Mono', monospace; font-size: 0.7rem; padding: 0.2rem 0.6rem; border-radius: 4px; margin: 0.15rem; }
</style>
""", unsafe_allow_html=True)

# ── Load Model ────────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    model  = joblib.load('xgb_model.pkl')
    scaler = joblib.load('scaler.pkl')
    return model, scaler

model, scaler = load_model()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div style='padding: 1rem 0 0.5rem;'><p class='section-title'>⬡ Input Market Data</p></div>", unsafe_allow_html=True)
    open_p     = st.number_input("Open Price (USD)", min_value=0.0, value=30000.0, step=100.0)
    high_p     = st.number_input("High Price (USD)", min_value=0.0, value=31000.0, step=100.0)
    low_p      = st.number_input("Low Price (USD)", min_value=0.0, value=29000.0, step=100.0)
    close_p    = st.number_input("Close Price (USD)", min_value=0.0, value=30500.0, step=100.0)
    st.markdown("<div class='gold-divider'></div>", unsafe_allow_html=True)
    volume     = st.number_input("Trading Volume", min_value=0.0, value=1_000_000_000.0, step=1_000_000.0, format="%.0f")
    market_cap = st.number_input("Market Cap (USD)", min_value=0.0, value=500_000_000_000.0, step=1_000_000_000.0, format="%.0f")
    predict_btn = st.button("⚡ Predict Volatility", key="predict_btn_v1")

# ── Main Area ─────────────────────────────────────────────────────────────────
st.markdown("<div class='hero-header'><div class='hero-badge'>₿ AI-Powered · XGBoost Model</div><h1 class='hero-title'>Crypto Volatility Predictor</h1></div>", unsafe_allow_html=True)
st.markdown("<div class='gold-divider'></div>", unsafe_allow_html=True)

# ── Metric Cards ──────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
with col1: st.markdown("<div class='metric-card'><div class='metric-value'>81%</div><div class='metric-label'>R² Accuracy</div></div>", unsafe_allow_html=True)
with col2: st.markdown("<div class='metric-card'><div class='metric-value'>0.0072</div><div class='metric-label'>RMSE Score</div></div>", unsafe_allow_html=True)
with col3: st.markdown("<div class='metric-card'><div class='metric-value'>0.0047</div><div class='metric-label'>MAE Score</div></div>", unsafe_allow_html=True)
with col4: st.markdown("<div class='metric-card'><div class='metric-value'>3012</div><div class='metric-label'>Training Rows</div></div>", unsafe_allow_html=True)

# ── Prediction Logic ──────────────────────────────────────────────────────────
if predict_btn:
    price_range = high_p - low_p
    price_range_pct = price_range / close_p if close_p != 0 else 0
    close_open_pct = (close_p - open_p) / open_p if open_p != 0 else 0
    liquidity_ratio = volume / market_cap if market_cap != 0 else 0

    input_data = pd.DataFrame([[
        open_p, high_p, low_p, close_p, volume, close_p, close_p, close_p,
        price_range, price_range_pct, close_open_pct, 0.05, price_range,
        volume, 0.0, 1.0, liquidity_ratio, 0.03, 0.03, 0.03, 0.01, 0.01, 50.0
    ]], columns=['open','high','low','close','volume','MA_7','MA_14','MA_30','price_range','price_range_pct','close_open_pct','BB_width','ATR_14','volume_MA7','volume_change','volume_spike','liquidity_ratio','volatility_lag1','volatility_lag3','volatility_lag7','return_lag1','return_lag3','RSI_14'])

    scaled = scaler.transform(input_data)
    pred = model.predict(scaled)[0]

    if pred > 0.05: level, icon, label, desc = "high", "🔴", "HIGH VOLATILITY", "Market is unstable. High risk."
    elif pred > 0.02: level, icon, label, desc = "medium", "🟡", "MEDIUM VOLATILITY", "Market is moderately active."
    else: level, icon, label, desc = "low", "🟢", "LOW VOLATILITY", "Market is relatively stable."

    st.markdown(f"<div class='result-box {level}'><p class='result-volatility'>{icon} {pred:.6f}</p><p class='result-label'>{label}</p><p class='result-desc'>{desc}</p></div>", unsafe_allow_html=True)

    # ── SAVE TO MONGODB (Final Step) ──────────────────────────────────────────
    input_summary = {"open": open_p, "high": high_p, "low": low_p, "close": close_p, "volume": volume}
    save_to_mongo(input_summary, pred, label)
    st.toast("Record saved to MongoDB", icon="💾")

st.markdown("<div class='gold-divider'></div>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center;'><span class='tag'>XGBoost</span><span class='tag'>Bitcoin</span><span class='tag'>MongoDB Integrated</span></div>", unsafe_allow_html=True)