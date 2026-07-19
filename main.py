import os
import json
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from src.data_fetch import get_company_info, get_price_history

app = FastAPI(title="Kinstars API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CACHE_DIR = "data_cache"


def load_cache(ticker):
    """Return cached data dict for a ticker, or None if not cached."""
    path = os.path.join(CACHE_DIR, f"{ticker.upper()}.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None


@app.get("/")
def root():
    return {"message": "Kinstars API is running"}


@app.get("/company/{ticker}")
def company(ticker: str):
    cached = load_cache(ticker)
    if cached:
        return cached["info"]
    return get_company_info(ticker)


@app.get("/prices/{ticker}")
def prices(ticker: str, period: str = "1y"):
    cached = load_cache(ticker)
    if cached:
        data = cached["prices"].get(period, cached["prices"].get("1y", []))
        return {"ticker": ticker.upper(), "period": period, "prices": data}
    hist = get_price_history(ticker, period)
    data = [
        {"date": str(idx.date()), "close": round(float(row["Close"]), 2), "volume": int(row["Volume"])}
        for idx, row in hist.iterrows()
    ]
    return {"ticker": ticker.upper(), "period": period, "prices": data}


@app.get("/financials/{ticker}")
def financials(ticker: str):
    cached = load_cache(ticker)
    if cached:
        return {"ticker": ticker.upper(), "financials": cached["financials"]}
    from src.data_fetch import get_financials
    fin = get_financials(ticker)
    income = fin["income_statement"]
    wanted = {"Total Revenue": "revenue", "Gross Profit": "gross_profit",
              "Operating Income": "operating_income", "Net Income": "net_income"}
    periods = {}
    for row_name, key in wanted.items():
        if row_name in income.index:
            for col, val in income.loc[row_name].dropna().items():
                year = str(col.year) if hasattr(col, "year") else str(col)
                periods.setdefault(year, {"year": year})[key] = round(float(val) / 1e9, 2)
    data = [periods[y] for y in sorted(periods.keys())]
    return {"ticker": ticker.upper(), "financials": data}


@app.get("/scores/{ticker}")
def scores(ticker: str):
    cached = load_cache(ticker)
    if cached:
        return cached["scores"]
    from src.scoring import compute_scores
    return compute_scores(ticker)


@app.get("/report/{ticker}")
def report(ticker: str):
    from src.report import generate_report
    cached = load_cache(ticker)
    if cached:
        text = generate_report(ticker, info=cached["info"], financials=cached["financials"])
    else:
        text = generate_report(ticker)
    return {"ticker": ticker.upper(), "report": text}


@app.get("/macro/{ticker}")
def macro(ticker: str):
    from src.macro import analyze_macro
    cached = load_cache(ticker)
    if cached:
        return analyze_macro(ticker, info=cached["info"])
    return analyze_macro(ticker)


@app.get("/compare/{ticker_a}/{ticker_b}")
def compare(ticker_a: str, ticker_b: str):
    from src.compare import compare_companies
    cache_a = load_cache(ticker_a)
    cache_b = load_cache(ticker_b)
    return compare_companies(
        ticker_a, ticker_b,
        info_a=cache_a["info"] if cache_a else None,
        scores_a=cache_a["scores"] if cache_a else None,
        info_b=cache_b["info"] if cache_b else None,
        scores_b=cache_b["scores"] if cache_b else None,
    )

@app.get("/report_stream/{ticker}")
def report_stream(ticker: str):
    from src.report import generate_report_stream
    cached = load_cache(ticker)
    info = cached["info"] if cached else None
    financials = cached["financials"] if cached else None

    def event_generator():
        for chunk in generate_report_stream(ticker, info=info, financials=financials):
            yield chunk

    return StreamingResponse(event_generator(), media_type="text/plain")