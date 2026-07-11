import os
import google.generativeai as genai
from dotenv import load_dotenv
from src.data_fetch import get_company_info, get_financials

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

GEN_MODEL = "models/gemini-2.5-flash"


def _summarize_financials(fin):
    """Pull a few key rows from the income statement into readable text."""
    income = fin["income_statement"]
    lines = []
    wanted = ["Total Revenue", "Gross Profit", "Operating Income", "Net Income"]
    for row in wanted:
        if row in income.index:
            vals = income.loc[row].dropna()
            # take up to 4 most recent periods
            recent = vals.head(4)
            formatted = ", ".join(
                f"{col.year if hasattr(col, 'year') else col}: {v/1e9:.1f}B"
                for col, v in recent.items()
            )
            lines.append(f"{row}: {formatted}")
    return "\n".join(lines) if lines else "Financial detail not available."


def generate_report(ticker):
    info = get_company_info(ticker)
    fin = get_financials(ticker)
    fin_summary = _summarize_financials(fin)

    mc = info.get("market_cap")
    mc_str = f"{mc/1e9:.1f}B" if mc else "N/A"

    prompt = f"""You are a professional equity research analyst. Write a structured
investment research report for the company below, based ONLY on the data provided.
Do not invent specific numbers that are not given. Be objective and balanced.

Company data:
- Name: {info.get('name')}
- Ticker: {info.get('ticker')}
- Sector: {info.get('sector')}
- Industry: {info.get('industry')}
- Market Cap: {mc_str}
- Current Price: {info.get('current_price')}
- Trailing P/E: {info.get('pe_trailing')}
- Forward P/E: {info.get('pe_forward')}

Financial highlights (in USD, B = billions):
{fin_summary}

Business summary:
{info.get('summary')}

Write the report with these exact sections (use these headings):
1. Company Overview
2. Financial Performance
3. Valuation
4. Key Opportunities
5. Key Risks
6. Investment Conclusion

Keep each section concise (2-4 sentences). Write in English."""

    model = genai.GenerativeModel(GEN_MODEL)
    response = model.generate_content(prompt)
    return response.text


if __name__ == "__main__":
    ticker = "AAPL"
    print(f"Generating report for {ticker}...\n")
    report = generate_report(ticker)
    print(report)