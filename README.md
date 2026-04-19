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

## 🔄 Latest Update – Rebalancing, Pipeline Orchestration, Snapshots, and Scheduling

### Portfolio Rebalance API
- Added a protected backend rebalance endpoint
- Integrated the decision engine with authenticated portfolio execution
- Enabled manual rebalance triggering from the frontend through a **Rebalance Now** button
- Verified rebalance execution using authenticated requests

### Real Portfolio History with Snapshots
- Added a `portfolio_snapshots` table for storing historical portfolio values
- Inserted snapshots after successful rebalances
- Added a dedicated portfolio snapshot endpoint
- Updated `/api/dashboard/history` to use real stored snapshots instead of placeholder values
- Improved dashboard chart labels to display time-based snapshot points correctly

### Pipeline Endpoints
Implemented backend pipeline endpoints for:
- market data refresh
- feature engineering refresh
- model training
- daily pipeline execution
- weekly pipeline execution

This allows the AI workflow to be triggered from the backend rather than manually running scripts.

### Daily and Weekly Pipeline Flows
- Added a **daily pipeline** flow that runs:
  1. data refresh
  2. feature refresh
  3. model training
  4. portfolio snapshot

- Added a **weekly pipeline** flow that runs:
  1. portfolio rebalance
  2. rebalance snapshot generation

### Scheduling and Automation
- Integrated APScheduler into the backend
- Added scheduled automation support for:
  - daily pipeline jobs
  - weekly rebalance jobs
- Confirmed scheduled jobs can trigger the portfolio workflow automatically while the backend service is running

### Frontend Integration Improvements
- Added a frontend **Rebalance Now** button to trigger authenticated rebalancing directly from the dashboard
- Connected the rebalance trigger to automatic UI refresh behavior through existing live-update logic

### Security and Auth Improvements
- Moved authentication configuration to environment variables
- Removed hardcoded secret loading from source code
- Updated JWT token creation so each login generates a unique token
## 🔄 Latest Update – Registration, Asset Selection, Rebalance Protection, and UI Polish

### User Registration and Onboarding
- Added a backend user registration endpoint
- Automatically creates a default portfolio when a new user registers
- Automatically creates default user settings on registration
- Automatically assigns starter assets to new portfolios
- Added a frontend Register page and linked it from the Login page
- Enabled automatic login immediately after successful registration

### Asset Selection Management
- Added backend portfolio asset management endpoints to fetch and update selected assets
- Integrated asset selection into the Settings page
- Users can now customize which assets PortaAI is allowed to manage in their portfolio

### Rebalance Safety and Asset Exit Logic
- Added backend protection to prevent rebalancing when no assets are selected and no holdings exist
- Updated rebalancing logic so that if a user removes an asset they still hold, PortaAI exits that position on the next rebalance
- Improved weekly pipeline behavior to skip cleanly when there is nothing to rebalance

### Empty-State UX Improvements
- Added empty-state handling across key pages:
  - Dashboard
  - Positions
  - Trades
  - Explainability
- New users and inactive portfolios now see clear guidance instead of empty charts or tables

### Topbar and Sidebar Polish
- Made the topbar sticky so it remains visible while scrolling
- Replaced the static avatar with a dynamic user initial derived from the account email
- Added email tooltip on avatar hover
- Moved logout action to the sidebar for cleaner navigation structure
- Added logout confirmation dialog to prevent accidental sign-out

### Notification Badge UX
- Improved topbar notification badge behavior to display `20+` when unread notifications exceed the visible list limit