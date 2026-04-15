# PortaAI

AI-Driven Portfolio Management System (Capstone Project)

\# PortaAI — AI Portfolio Management System



PortaAI is an AI-driven portfolio management platform that autonomously manages investment decisions across financial assets using machine learning and data-driven signals.



\## Features (Phase 1)

\- Market data ingestion

\- Feature engineering (technical indicators)

\- Forecasting model (Random Forest)

\- Decision engine (buy/sell/hold)

\- Trade execution

\- Portfolio tracking (positions \& cash)



\## Architecture

\- Backend: Python + SQLAlchemy

\- Database: PostgreSQL

\- AI Engine: ML forecasting + decision logic



\## Status

Phase 1 Complete — Single-asset intelligent portfolio management



\## Next Steps

\- Multi-asset portfolio allocation

\- Sentiment analysis integration

\- Advanced models (LSTM)

\- Frontend dashboard



\## Features (Phase 2)

\- Multi-asset portfolio management

\- Score-based asset allocation

\- Dynamic cash allocation (20%–80%)

\- Full buy/sell/hold rebalancing

\- Portfolio tracking (positions, trades, allocations)



\---



🚀 Latest Progress (Phase 3 — Sentiment \& Model Upgrade)

🧠 Sentiment Analysis Integration

Integrated FinBERT (Transformer-based model) for financial sentiment analysis

Implemented news ingestion pipeline using Yahoo Finance

Stored news and sentiment scores in PostgreSQL

Each headline is classified as positive / negative / neutral with a confidence score



\---



📊 Time-Dependent Sentiment Features

Designed and implemented time-aware sentiment aggregation

For each asset and date, sentiment is computed using:

recent news prior to that date

Added sentiment\_aggregate to engineered features

Enables the model to learn how changing sentiment impacts future returns



\---



🤖 Forecasting Model Upgrade (XGBoost)

Replaced baseline model with XGBoost Regressor

Improved ability to capture:

nonlinear relationships

interactions between technical indicators and sentiment

Observed improved performance on some assets (e.g., AAPL)



\---



📈 Decision Engine Improvements

Integrated sentiment into:

forecasting features

decision scoring (final\_score)

Implemented:

multi-asset allocation

score-based weighting

dynamic cash allocation (20%–80%)

full buy / sell / hold logic



\---



⚙️ Current System Capabilities

Combines:

quantitative signals (technical indicators)

machine learning forecasts (XGBoost)

NLP sentiment analysis (FinBERT)

Produces:

portfolio allocations

trade decisions

capital rebalancing



\---



📍 Project Status

Core AI system is \~90% complete



Next steps:

Model explainability (feature importance / SHAP)

Frontend dashboard

Automation (daily updates \& rebalancing)

---

## 🔍 Explainability (SHAP Integration)

To enhance transparency and interpretability, the system integrates **SHAP (SHapley Additive exPlanations)** to explain model predictions.

### Key Features
- Uses **TreeExplainer** for XGBoost models
- Explains each asset’s predicted return based on feature contributions
- Identifies which features push predictions **up or down**

### Example Explanation
For each asset, the system prints:

- Top 3 most influential features
- Full feature contribution breakdown

Example:BUY MSFT
Top reasons:

momentum_7d → pushes UP
return_7d → pushes UP
sentiment_aggregate → pushes UP


### Purpose
- Improves model transparency
- Provides insight into AI decision-making
- Strengthens trust and interpretability of portfolio actions

---

## 📊 System Capabilities Summary

The system now combines:

- **Quantitative Analysis**
  - Technical indicators (returns, RSI, momentum, volatility)

- **Machine Learning**
  - XGBoost forecasting model

- **Natural Language Processing**
  - FinBERT sentiment analysis on financial news

- **Explainability**
  - SHAP-based feature importance per prediction

- **Portfolio Optimization**
  - Multi-asset allocation
  - Dynamic cash allocation (20%–80%)
  - Buy / Sell / Hold decision engine

---

## 🔄 Latest Update (Frontend Integration, Auth & Notifications)
### 🔐 Authentication System
- Implemented JWT-based login system
- Added password hashing using bcrypt
- Protected backend routes using token-based authentication
- Created frontend protected routes for `/app/*`
- Integrated token storage and automatic attachment to API requests
- Implemented automatic logout on `401 Unauthorized`

---

### 🔗 Frontend ↔ Backend Integration
- Connected all frontend pages to FastAPI backend:
  - Dashboard
  - Positions
  - Predictions
  - Trades
  - Explainability
- Replaced static data with live API data

---

### 🔔 Notifications System
- Created notifications table and backend API
- Built frontend Notifications page
- Added bell icon with unread count in topbar
- Implemented:
  - mark as read
  - mark all as read
  - clear read notifications
  - confirmation dialogs
- Integrated automatic notifications from AI decision engine:
  - BUY trades
  - SELL trades
  - Portfolio rebalance events

---

### 🔄 Live Data Updates
- Implemented polling-based auto-refresh across pages:
  - Dashboard
  - Positions
  - Predictions
  - Trades
  - Explainability
  - Notifications
- Eliminated need for manual page refresh

---

### 🤖 Decision Engine Improvements
- Refactored decision engine to accept dynamic `portfolio_id`
- Integrated notification generation directly within buy/sell logic
- Maintained temporary local execution entry point for testing

---

### 🔐 Security Improvements
- Removed hardcoded `SECRET_KEY`
- Moved authentication configuration to environment variables (`.env`)
- Configured backend to securely load environment variables using `python-dotenv`
- Updated `.gitignore` to exclude `.env` files