"""
Hallucination eval (LLM-as-judge):
A second LLM checks whether claims in the AI report are grounded in the
source data, flagging any unsupported/fabricated statements.
"""
import sys, os, json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import google.generativeai as genai
from dotenv import load_dotenv
from src.data_fetch import get_company_info, get_financials
from src.report import generate_report

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
JUDGE_MODEL = "models/gemini-2.5-flash"

TEST_TICKERS = ["AAPL", "MSFT", "NVDA"]


def build_source_context(ticker):
    info = get_company_info(ticker)
    fin = get_financials(ticker)
    income = fin["income_statement"]
    lines = [
        f"Name: {info.get('name')}",
        f"Sector: {info.get('sector')}",
        f"Industry: {info.get('industry')}",
        f"Market Cap (USD): {info.get('market_cap')}",
        f"Trailing P/E: {info.get('pe_trailing')}",
        f"Forward P/E: {info.get('pe_forward')}",
        f"Current Price: {info.get('current_price')}",
        f"Business Summary: {info.get('summary')}",
    ]
    # label each financial figure WITH its year so the judge can verify
    for row in ["Total Revenue", "Gross Profit", "Operating Income", "Net Income"]:
        if row in income.index:
            series = income.loc[row].dropna().head(4)
            parts = []
            for col, val in series.items():
                year = col.year if hasattr(col, "year") else str(col)
                parts.append(f"{year}: {val/1e9:.1f}B")
            lines.append(f"{row} by year: {', '.join(parts)}")
    return "\n".join(lines)


def judge_report(ticker):
    source = build_source_context(ticker)
    report = generate_report(ticker)

    prompt = f"""You are a fact-checking judge for AI-generated financial reports.
Below is the SOURCE DATA and a REPORT generated from it.

Flag a claim as a hallucination ONLY if it states a SPECIFIC fact, number, company
event, or product that directly contradicts the source data OR presents a specific
unverifiable figure not derivable from the source. The source financial figures are
labeled by year — use them to verify any numbers.

Do NOT flag: general industry observations (e.g. "faces competition"), reasonable
qualitative commentary, or facts that are clearly derivable from the business summary
provided. Only flag concrete, verifiable claims that conflict with or go beyond the data.

Return ONLY a JSON object:
{{
  "total_claims": <int, approximate number of factual claims in the report>,
  "hallucinations": [<list of specific unsupported claims, as short strings>],
  "grounded": <true if no hallucinations, false otherwise>
}}

SOURCE DATA:
{source}

REPORT:
{report}

JSON:"""

    model = genai.GenerativeModel(JUDGE_MODEL)
    resp = model.generate_content(prompt)
    text = resp.text.strip().replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(text)
    except Exception:
        return {"total_claims": None, "hallucinations": ["<parse error>"], "grounded": None}


if __name__ == "__main__":
    print("=" * 60)
    print("HALLUCINATION EVAL (LLM-as-judge)")
    print("=" * 60)

    clean = 0
    for ticker in TEST_TICKERS:
        print(f"\n### {ticker} ###")
        try:
            result = judge_report(ticker)
            halls = result.get("hallucinations", [])
            if result.get("grounded") and not halls:
                clean += 1
                print(f"  [GROUNDED] No hallucinations detected "
                      f"(~{result.get('total_claims')} claims checked)")
            else:
                print(f"  [FLAGGED] {len(halls)} potential hallucination(s):")
                for h in halls:
                    print(f"     - {h}")
        except Exception as e:
            print(f"  ERROR: {e}")

    print("\n" + "=" * 60)
    print(f"RESULT: {clean}/{len(TEST_TICKERS)} reports fully grounded")
    print("=" * 60)