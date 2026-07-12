import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from src.data_fetch import get_company_info

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

GEN_MODEL = "models/gemini-2.5-flash"


def analyze_macro(ticker):
    info = get_company_info(ticker)

    prompt = f"""You are a macroeconomic analyst. Analyze how key macroeconomic
factors affect the company below. Connect each factor to the company's specific
business, do not give generic textbook answers.

Company:
- Name: {info.get('name')}
- Sector: {info.get('sector')}
- Industry: {info.get('industry')}
- Business: {info.get('summary')}

Analyze these macro factors: interest rates, inflation, currency/FX,
industry regulation or policy, and geopolitical/supply-chain risk.

Return ONLY a JSON array. Each item must have:
- "factor": the macro factor name (in English)
- "impact": either "Positive", "Negative", or "Mixed"
- "explanation": one concise sentence explaining the effect on THIS company

Do not include any text outside the JSON array."""

    model = genai.GenerativeModel(GEN_MODEL)
    response = model.generate_content(prompt)

    text = response.text.strip().replace("```json", "").replace("```", "").strip()
    try:
        factors = json.loads(text)
    except Exception:
        factors = []
    return {"ticker": ticker.upper(), "macro_factors": factors}


if __name__ == "__main__":
    print(json.dumps(analyze_macro("TSLA"), indent=2))