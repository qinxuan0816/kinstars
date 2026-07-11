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