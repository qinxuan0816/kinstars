import yfinance as yf

# Try Apple as a test
ticker = "AAPL"
stock = yf.Ticker(ticker)

# 1. Basic company info
info = stock.info
print("===== COMPANY INFO =====")
print("Name:", info.get("longName"))
print("Sector:", info.get("sector"))
print("Industry:", info.get("industry"))
print("Market Cap:", info.get("marketCap"))
print("P/E (trailing):", info.get("trailingPE"))
print("Current Price:", info.get("currentPrice"))

# 2. Recent stock price history (last 1 month)
print("\n===== PRICE HISTORY (last 5 days) =====")
hist = stock.history(period="1mo")
print(hist[["Close", "Volume"]].tail())

# 3. Financials (income statement)
print("\n===== INCOME STATEMENT (columns = years) =====")
fin = stock.financials
print(fin.index.tolist()[:10])  # show what financial rows are available