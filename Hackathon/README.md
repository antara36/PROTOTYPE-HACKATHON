# FINCAP GUARD — Institutional Portfolio Risk, Control & Safeguard Decision System

[![Status](https://img.shields.io/badge/Status-Operational-success.svg)]()
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)]()
[![Framework](https://img.shields.io/badge/Frontend-Streamlit-red.svg)]()
[![Optimization](https://img.shields.io/badge/Engine-SciPy%20SLSQP-orange.svg)]()

## 🌟 Overview
**FINCAP GUARD** is an institutional financial safeguard and decision system. It does not simply notify the portfolio manager that their portfolio is risky. It:
1. Identifies **why** the risk or limit breach occurred.
2. Simulates severe market shocks across multiple historical and hypothetical stress scenarios.
3. Uses **Machine Learning** to predict systemic market crises in real-time.
4. Synthesizes **3 distinct corrective action options** via SciPy constrained optimization.
5. Recommends the **least-disruptive corrective action (Option B ⭐)** that restores full regulatory compliance with minimal unnecessary turnover and transaction friction.
6. Grounds compliance explanations in institutional policy documents via a **Policy RAG Assistant**.
7. Verifies that all risk limits are cleared before rebalancing trades are committed.

---

## 🏛️ System Architecture

```
FINCAP GUARD
    │
    ▼
┌───────────────┐
│ USER / LOGIN  │ (Firebase Auth / Institutional Session)
└───────┬───────┘
        ▼
┌───────────────┐
│   DASHBOARD   │ (Real-time KPIs, Risk Gauge, ML Regime)
└───────┬───────┘
        ▼
┌───────────────┐
│  PORTFOLIO    │ (Holdings Manager: ₹1 Cr base)
│    ENGINE     │
└───────┬───────┘
        ▼
┌─────────────┼──────────────┐
▼             ▼              ▼
MARKET       LIQUIDITY      POLICY
DATA         DATA           DOCUMENTS
(NIFTY/Gold) (Asset Tiers)  (PDF / MD)
│             │              │
▼             ▼              ▼
RISK ENGINE  LIQUIDITY      RAG ENGINE
│             │              │
└─────────────┼──────────────┘
              ▼
      ┌───────────────┐
      │ CONTROL ENGINE│
      └───────┬───────┘
              │ Breach Detected?
              ├───► NO: SAFE STATUS
              │
              └───► YES: TRIGGER SAFEGUARD
                      │
                      ├─► STRESS SCENARIOS
                      ├─► ML CRISIS PREDICTOR
                      ├─► 3 OPTIMIZATION OPTIONS
                      │    - Option A: Conservative
                      │    - Option B: Least-Disruptive ⭐
                      │    - Option C: Return-Preserving
                      │
                      ├─► DECISION ENGINE
                      ├─► REBALANCE & VERIFY
                      └─► RAG EXPLANATION
```

---

## 📁 Dataset Segregation
To avoid conflating disparate asset timeframes and objectives:
1. **NIFTY 50 Dataset**: Historical Indian equity OHLCV data. Used exclusively for equity returns, historical volatility, and drawdown analysis.
2. **Gold Dataset**: Historical daily gold prices in INR for 10g 24K gold. Used exclusively for gold returns, commodity volatility, and correlation/diversification.
3. **Financial Crisis Dataset**: Multi-market indicators (stock, bond, FX returns and volatilities, VIX). Used exclusively for supervised ML classification (`Crisis_Label`).
4. **Institutional Policies**: Risk caps, liquidity guidelines, stress horizons used for RAG grounding.

---

## 🚀 Quickstart Guide

### 1. Launch the Application
Run the Streamlit frontend with Python 3.11:
```powershell
& "C:\Users\Antra\AppData\Local\Programs\Python\Python311\python.exe" -m streamlit run frontend/app.py
```

### 2. Login Credentials
- **Email**: `risk.officer@fincap.com`
- **Password**: `FincapGuard2026!`
*(Or click Sign In for direct instant evaluator access)*
