# PortaAI — AI-Driven Portfolio Management System

PortaAI is an AI-powered portfolio management system that automates investment decisions using machine learning, financial data analysis, and sentiment analysis. The system allows users to select assets while the AI manages capital allocation, executes trades, and provides explainability for its decisions.

---

## 🚀 Features

* **Automated Portfolio Rebalancing**
  Generates buy, sell, and hold decisions based on AI predictions.

* **User-Controlled Asset Selection**
  Users choose which assets the system manages.

* **Trade Tracking and History**
  All transactions are recorded and displayed.

* **Sentiment Analysis Integration**
  Financial news is analyzed using NLP to enhance predictions.

* **Explainability Module**
  Provides insight into the reasoning behind AI decisions.

* **Notifications System**
  Alerts users about portfolio updates and executed trades.

---

## 🧠 System Overview

The system follows a modular architecture:

Frontend (React)
⬇
Backend API (FastAPI)
⬇
AI Engine (Data Processing + Forecasting + Decision Engine)
⬇
PostgreSQL Database

External data sources provide market data and financial news.

---

## 🔁 AI Pipeline

```text
Market Data + News Data
        ↓
Feature Engineering (technical indicators + sentiment)
        ↓
Forecasting Model (XGBoost)
        ↓
Predicted Returns
        ↓
Decision Engine (Buy / Sell / Hold)
        ↓
Portfolio Updates
```

---

## 🛠️ Technologies Used

### Backend

* Python
* FastAPI
* SQLAlchemy
* PostgreSQL

### Frontend

* React
* Tailwind CSS
* Recharts
* lucide-react

### Machine Learning

* XGBoost (forecasting model)
* FinBERT (sentiment analysis)

### Data & Utilities

* Pandas
* NumPy
* yfinance

---

## ⚙️ Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/adamshehadehh/PortaAI.git
cd PortaAI
```

---

### 2. Backend Setup

```bash
cd ~/PortaAI
pip install -r backend/requirements.txt
```

Create a `.env` file inside the backend folder:

```env
SECRET_KEY=your_secret_key
DATABASE_URL=your_database_url
SMTP_USERNAME=your_email
SMTP_PASSWORD=your_password
```

Run backend:

```bash
PYTHONPATH="$PWD:$PWD/backend" python -m uvicorn app.main:app --reload --app-dir backend
```

Backend runs at:

```
http://127.0.0.1:8000
```

---

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at:

```
http://localhost:5173
```

---

## ▶️ Usage

1. Register a new user account
2. Log in to the system
3. Select assets from the settings page
4. View portfolio dashboard
5. Click **Rebalance Now** to execute decisions
6. Monitor trades and explainability outputs

---

## 🧪 Testing

* Unit testing for core modules (authentication, decision engine, portfolio logic)
* Integration testing across frontend, backend, and AI pipeline
* Edge cases handled (e.g., no selected assets, empty portfolio)

---

## 🔮 Future Improvements

* Real-time data streaming
* Advanced deep learning models
* Risk management strategies (e.g., stop-loss)
* Cloud deployment (AWS/Azure)

---

## 📌 Notes

* Sentiment analysis is integrated into the model as a feature
* The decision engine uses predicted returns to generate actions
* The system currently operates on periodic updates
* The FinBERT model is stored locally on the development environment and is not included in the repository due to its large size.

---

## 👨‍💻 Author

Adam Shehadeh
Lebanese American University
Computer Science

---

## 📄 License

This project is for academic purposes.
