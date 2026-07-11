import yfinance as yf


def get_company_info(ticker):
    """Return basic company profile and key metrics."""
    stock = yf.Ticker(ticker)
    info = stock.info
    return {
        "ticker": ticker.upper(),
        "name": info.get("longName"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "market_cap": info.get("marketCap"),
        "pe_trailing": info.get("trailingPE"),
        "pe_forward": info.get("forwardPE"),
        "current_price": info.get("currentPrice"),
        "currency": info.get("currency"),
        "summary": info.get("longBusinessSummary"),
    }


def get_price_history(ticker, period="1y"):
    """Return historical price data as a DataFrame.
    period options: '1mo', '6mo', '1y', '5y', etc."""
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    return hist


def get_financials(ticker):
    """Return income statement, balance sheet, and cash flow as DataFrames."""
    stock = yf.Ticker(ticker)
    return {
        "income_statement": stock.financials,
        "balance_sheet": stock.balance_sheet,
        "cash_flow": stock.cashflow,
    }


if __name__ == "__main__":
    # Quick test
    ticker = "AAPL"
    print(f"Testing data functions for {ticker}\n")

    info = get_company_info(ticker)
    print("Company:", info["name"])
    print("Sector:", info["sector"])
    print("Market Cap:", info["market_cap"])
    print("Current Price:", info["current_price"])
    print("P/E:", info["pe_trailing"])

    print("\nPrice history rows (1y):")
    hist = get_price_history(ticker, "1y")
    print(f"  Got {len(hist)} days of price data")
    print(f"  Latest close: {hist['Close'].iloc[-1]:.2f}")

    fin = get_financials(ticker)
    print("\nFinancial statements available:")
    for name, df in fin.items():
        print(f"  {name}: {df.shape[1]} periods, {df.shape[0]} line items")