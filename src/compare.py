import os
import google.generativeai as genai
from dotenv import load_dotenv
from src.data_fetch import get_company_info
from src.scoring import compute_scores

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

GEN_MODEL = "models/gemini-2.5-flash"


def compare_companies(ticker_a, ticker_b):
    a_info = get_company_info(ticker_a)
    b_info = get_company_info(ticker_b)
    a_sc = compute_scores(ticker_a)
    b_sc = compute_scores(ticker_b)

    def fmt(info, sc):
        return (f"{info.get('name')} ({info.get('ticker')}): "
                f"sector {info.get('sector')}, "
                f"P/E {info.get('pe_trailing')}, "
                f"revenue growth {sc.get('revenue_growth_pct')}%, "
                f"net margin {sc.get('net_margin_pct')}%, "
                f"overall risk {sc.get('overall_risk')}")

    prompt = f"""You are an equity research analyst. Compare these two companies
based ONLY on the data below. Be objective and concise.

Company A — {fmt(a_info, a_sc)}
Company B — {fmt(b_info, b_sc)}

Write a short comparison (3-4 sentences) covering: which company shows stronger
growth, which is more profitable, which carries more valuation risk, and what
type of investor each might suit. Do not invent numbers. Write in English."""

    model = genai.GenerativeModel(GEN_MODEL)
    response = model.generate_content(prompt)
    return {
        "ticker_a": ticker_a.upper(),
        "ticker_b": ticker_b.upper(),
        "summary": response.text,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(compare_companies("AAPL", "MSFT"), indent=2))