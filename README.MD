# 🪙 Cryptocurrency Volatility Prediction



![Python](https://img.shields.io/badge/Python-3.10-blue)




![XGBoost](https://img.shields.io/badge/Model-XGBoost-orange)




![Streamlit](https://img.shields.io/badge/Deployment-Streamlit-red)




![R2](https://img.shields.io/badge/R²%20Score-0.8183-green)



## 📌 Project Overview
Cryptocurrency markets are highly volatile. This project builds a Machine Learning model to predict Bitcoin volatility using historical OHLC data, trading volume, and market capitalization. The final model is deployed as a Streamlit web application for real-time predictions.

---

## 🎯 Objective
- Predict 7-day rolling volatility of Bitcoin
- Help traders identify high risk periods
- Enable informed investment decisions
- Provide real-time volatility predictions via web app

---

## 📊 Dataset
| Property | Value |
|----------|-------|
| Source | Cryptocurrency Historical Prices |
| Total Records | 72,946 |
| Cryptocurrencies | 50+ |
| Focus | Bitcoin |
| Final Rows | 3,012 |
| Total Features | 23 |
| Date Range | 2013 to 2023 |

---

## 🗂️ Project Structure
crypto/
│
├── 📓 work.ipynb
├── 📓 02_feature_engineering.ipynb
├── 📓 03_EDA.ipynb
├── 📓 04_model_training.ipynb
├── 🚀 app.py
│
├── 📁 docs/
│   ├── 📄 HLD.docx
│   ├── 📄 LLD.docx
│   ├── 📄 Pipeline_Architecture.docx
│   └── 📄 Final_Report.docx
│
├── 💾 bitcoin_clean.csv
├── 💾 bitcoin_features.csv
├── 🤖 xgb_model.pkl
└── ⚖️ scaler.pkl
---

## 🔄 Project Pipeline
Raw Dataset (72,946 rows)
↓
Data Collection & Cleaning
↓
Feature Engineering (23 features)
↓
Exploratory Data Analysis
↓
Model Training (XGBoost)
↓
Model Evaluation (R² = 0.8183)
↓
Streamlit Deployment
↓
Real-time Prediction
---

## ⚙️ Feature Engineering
| Category | Features | Count |
|----------|----------|-------|
| Target Variable | volatility_7d | 1 |
| Price Features | MA_7, MA_14, MA_30, price_range, price_range_pct, close_open_pct | 6 |
| Technical Indicators | BB_width, ATR_14, RSI_14 | 3 |
| Volume Features | volume_MA7, volume_change, volume_spike, liquidity_ratio | 4 |
| Lag Features | volatility_lag1, lag3, lag7, return_lag1, return_lag3 | 5 |
| Base OHLCV | open, high, low, close, volume | 5 |
| *Total* | | *23* |

---

## 🤖 Model Results
| Model | RMSE | MAE | R² Score |
|-------|------|-----|----------|
| Random Forest | 0.007467 | 0.005019 | 0.8046 |
| *XGBoost ✅* | *0.007201* | *0.004658* | *0.8183* |

### Why XGBoost Won
- Lower RMSE (0.007201 vs 0.007467)
- Lower MAE (0.004658 vs 0.005019)
- Higher R² Score (0.8183 vs 0.8046)
- R² = 0.8183 means model is 81.83% accurate

---

## 🔑 Key Insights
1. *Past Volatility* is the strongest predictor (78% feature importance)
2. *Price Range* indicates upcoming volatile periods
3. *Volume Spikes* often precede high volatility events
4. *Bollinger Bands* width strongly correlates with volatility
5. *Bitcoin* showed extreme volatility during 2017-2018 and 2020-2021

---

## 🚀 How To Run

### 1. Clone Repository
```bash
git clone https://github.com/shrivashadi/Crypto-Volatility-Prediction.git
cd Crypto-Volatility-Prediction