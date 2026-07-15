import os
import google.generativeai as genai
from dotenv import load_dotenv
from src.data_fetch import get_company_info, get_financials

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

GEN_MODEL = "models/gemini-2.5-flash"


def _summarize_financials_from_list(financials):
    """Build readable text from a list of {year, revenue, ...} dicts."""
    if not financials:
        return "Financial detail not available."
    lines = []
    keys = {"revenue": "Total Revenue", "gross_profit": "Gross Profit",
            "operating_income": "Operating Income", "net_income": "Net Income"}
    for key, label in keys.items():
        vals = [(f["year"], f[key]) for f in financials if key in f]
        if vals:
            s = ", ".join(f"{y}: {v:.1f}B" for y, v in vals)
            lines.append(f"{label}: {s}")
    return "\n".join(lines) if lines else "Financial detail not available."


def generate_report(ticker, info=None, financials=None):
    """Generate a report. If info/financials are provided (from cache),
    use them; otherwise fetch live from yfinance."""
    if info is None:
        info = get_company_info(ticker)

    if financials is not None:
        fin_summary = _summarize_financials_from_list(financials)
    else:
        fin = get_financials(ticker)
        income = fin["income_statement"]
        lines = []
        for row in ["Total Revenue", "Gross Profit", "Operating Income", "Net Income"]:
            if row in income.index:
                vals = income.loc[row].dropna().head(4)
                formatted = ", ".join(
                    f"{col.year if hasattr(col, 'year') else col}: {v/1e9:.1f}B"
                    for col, v in vals.items()
                )
                lines.append(f"{row}: {formatted}")
        fin_summary = "\n".join(lines) if lines else "Financial detail not available."

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