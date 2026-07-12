from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.data_fetch import get_company_info, get_price_history
from src.report import generate_report

app = FastAPI(title="Kinstars API")

# Allow the React frontend (running on a different port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # for development; tighten later
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Kinstars API is running"}


@app.get("/company/{ticker}")
def company(ticker: str):
    """Return basic company info for a ticker."""
    return get_company_info(ticker)


@app.get("/prices/{ticker}")
def prices(ticker: str, period: str = "1y"):
    """Return price history. Converts DataFrame to a simple list for JSON."""
    hist = get_price_history(ticker, period)
    # Turn the DataFrame into a JSON-friendly list of {date, close, volume}
    data = [
        {
            "date": str(idx.date()),
            "close": round(float(row["Close"]), 2),
            "volume": int(row["Volume"]),
        }
        for idx, row in hist.iterrows()
    ]
    return {"ticker": ticker.upper(), "period": period, "prices": data}

@app.get("/report/{ticker}")
def report(ticker: str):
    """Generate an AI investment research report for a ticker."""
    text = generate_report(ticker)
    return {"ticker": ticker.upper(), "report": text}

@app.get("/financials/{ticker}")
def financials(ticker: str):
    """Return key financial metrics by year for charting."""
    from src.data_fetch import get_financials
    fin = get_financials(ticker)
    income = fin["income_statement"]

    wanted = {
        "Total Revenue": "revenue",
        "Gross Profit": "gross_profit",
        "Operating Income": "operating_income",
        "Net Income": "net_income",
    }

    # Build a list of {year, revenue, gross_profit, ...} per period
    periods = {}
    for row_name, key in wanted.items():
        if row_name in income.index:
            series = income.loc[row_name].dropna()
            for col, val in series.items():
                year = str(col.year) if hasattr(col, "year") else str(col)
                if year not in periods:
                    periods[year] = {"year": year}
                # convert to billions for readability
                periods[year][key] = round(float(val) / 1e9, 2)

    # sort by year ascending
    data = [periods[y] for y in sorted(periods.keys())]
    return {"ticker": ticker.upper(), "financials": data}

@app.get("/scores/{ticker}")
def scores(ticker: str):
    """Return rule-based risk/quality scores for a ticker."""
    from src.scoring import compute_scores
    return compute_scores(ticker)

@app.get("/macro/{ticker}")
def macro(ticker: str):
    """Return AI macroeconomic factor analysis for a ticker."""
    from src.macro import analyze_macro
    return analyze_macro(ticker)