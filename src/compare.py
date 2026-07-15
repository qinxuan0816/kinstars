import os
import google.generativeai as genai
from dotenv import load_dotenv
from src.data_fetch import get_company_info
from src.scoring import compute_scores

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

GEN_MODEL = "models/gemini-2.5-flash"


def compare_companies(ticker_a, ticker_b, info_a=None, scores_a=None, info_b=None, scores_b=None):
    if info_a is None:
        info_a = get_company_info(ticker_a)
    if scores_a is None:
        scores_a = compute_scores(ticker_a)
    if info_b is None:
        info_b = get_company_info(ticker_b)
    if scores_b is None:
        scores_b = compute_scores(ticker_b)

    def fmt(info, sc):
        return (f"{info.get('name')} ({info.get('ticker')}): "
                f"sector {info.get('sector')}, "
                f"P/E {info.get('pe_trailing')}, "
                f"revenue growth {sc.get('revenue_growth_pct')}%, "
                f"net margin {sc.get('net_margin_pct')}%, "
                f"overall risk {sc.get('overall_risk')}")

    prompt = f"""You are an equity research analyst. Compare these two companies
based ONLY on the data below. Be objective and concise.

Company A — {fmt(info_a, scores_a)}
Company B — {fmt(info_b, scores_b)}

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