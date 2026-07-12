# Kinstars — AI Financial Research Assistant

> Analyze any US stock with real market data, financial trends, risk scoring, macroeconomic insights, and AI-generated research reports — all in one place.

**Live demo:** https://kinstars.vercel.app
**API:** https://kinstars.onrender.com

---

## Overview

Kinstars is an AI-powered financial research assistant that turns a single stock ticker into a complete investment research workflow. Users enter a company (e.g. `AAPL`, `TSLA`, `NVDA`) and instantly get company fundamentals, an interactive price chart, a multi-year financial breakdown, rule-based risk scores, an AI macroeconomic analysis, and a full AI-generated investment research report.

The goal is not to predict stock prices, but to help users **integrate financial data, market trends, and macro factors into a structured, readable research report faster.**

---

## Features

- **Company Search & Overview** — Fetch company profile, sector, market cap, current price, and valuation multiples.
- **Interactive Price Chart** — Historical price trends with selectable ranges (1M / 6M / 1Y / 5Y).
- **Financial Performance Visualization** — Multi-year revenue, gross profit, operating income, and net income as grouped bar charts.
- **Risk & Quality Scoring** — Rule-based scores for growth, profitability, valuation risk, and an overall risk level.
- **AI Macroeconomic Analysis** — An LLM connects interest rates, inflation, FX, policy, and geopolitical risk to the specific company's business.
- **AI Investment Research Report** — A structured report (overview, financials, valuation, opportunities, risks, conclusion) grounded only in the retrieved data to reduce hallucination.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React (Vite), Recharts |
| Backend | FastAPI, Uvicorn |
| Financial Data | yfinance (Yahoo Finance) |
| AI | Google Gemini |
| Deployment | Vercel (frontend), Render (backend) |

---

## Architecture

Kinstars uses a **decoupled frontend/backend architecture**:

- The **FastAPI backend** exposes REST endpoints (`/company`, `/prices`, `/financials`, `/scores`, `/macro`, `/report`) and handles all data fetching, scoring logic, and LLM calls.
- The **React frontend** consumes these endpoints and renders an interactive dashboard.
- Data-fetching logic is isolated in a dedicated module, so the data source can be swapped without touching the API or UI layers.