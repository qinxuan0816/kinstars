"""
Prefetch data for example tickers and save to JSON files.
Run this LOCALLY (your IP is not rate-limited by Yahoo).
The deployed backend will read these files instead of calling yfinance live.
"""
import os, json
from src.data_fetch import get_company_info, get_price_history, get_financials
from src.scoring import compute_scores

EXAMPLES = ["AAPL", "TSLA", "NVDA", "MSFT"]
CACHE_DIR = "data_cache"


def prefetch(ticker):
    print(f"Fetching {ticker}...")
    info = get_company_info(ticker)

    # price history for all periods the frontend uses
    prices = {}
    for per in ["1mo", "6mo", "1y", "5y"]:
        hist = get_price_history(ticker, per)
        prices[per] = [
            {"date": str(idx.date()), "close": round(float(row["Close"]), 2), "volume": int(row["Volume"])}
            for idx, row in hist.iterrows()
        ]

    # financials
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
    financials = [periods[y] for y in sorted(periods.keys())]

    # scores
    scores = compute_scores(ticker)

    return {"info": info, "prices": prices, "financials": financials, "scores": scores}


if __name__ == "__main__":
    os.makedirs(CACHE_DIR, exist_ok=True)
    for tk in EXAMPLES:
        try:
            data = prefetch(tk)
            path = os.path.join(CACHE_DIR, f"{tk}.json")
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
            print(f"  Saved {path}")
        except Exception as e:
            print(f"  FAILED {tk}: {e}")
    print("Done. Commit the data_cache/ folder to deploy.")