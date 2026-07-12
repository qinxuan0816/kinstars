from src.data_fetch import get_company_info, get_financials


def compute_scores(ticker):
    info = get_company_info(ticker)
    fin = get_financials(ticker)
    income = fin["income_statement"]

    scores = {}

    # --- Growth: compare latest vs previous year revenue ---
    growth_score = "N/A"
    revenue_growth = None
    if "Total Revenue" in income.index:
        rev = income.loc["Total Revenue"].dropna()
        if len(rev) >= 2:
            latest, prev = float(rev.iloc[0]), float(rev.iloc[1])
            if prev != 0:
                revenue_growth = (latest - prev) / prev * 100
                if revenue_growth > 15:
                    growth_score = "High"
                elif revenue_growth > 5:
                    growth_score = "Medium"
                else:
                    growth_score = "Low"

    # --- Profitability: net margin = net income / revenue ---
    profit_score = "N/A"
    net_margin = None
    if "Total Revenue" in income.index and "Net Income" in income.index:
        rev = income.loc["Total Revenue"].dropna()
        ni = income.loc["Net Income"].dropna()
        if len(rev) >= 1 and len(ni) >= 1 and float(rev.iloc[0]) != 0:
            net_margin = float(ni.iloc[0]) / float(rev.iloc[0]) * 100
            if net_margin > 20:
                profit_score = "High"
            elif net_margin > 8:
                profit_score = "Medium"
            else:
                profit_score = "Low"

    # --- Valuation risk: based on trailing P/E ---
    valuation_risk = "N/A"
    pe = info.get("pe_trailing")
    if pe:
        if pe > 35:
            valuation_risk = "High"
        elif pe > 20:
            valuation_risk = "Medium"
        else:
            valuation_risk = "Low"

    # --- Overall risk level (simple rule combining the above) ---
    risk_points = 0
    if valuation_risk == "High":
        risk_points += 2
    elif valuation_risk == "Medium":
        risk_points += 1
    if growth_score == "Low":
        risk_points += 1
    if profit_score == "Low":
        risk_points += 1

    if risk_points >= 3:
        overall = "High"
    elif risk_points >= 1:
        overall = "Medium"
    else:
        overall = "Low"

    return {
        "ticker": ticker.upper(),
        "growth_score": growth_score,
        "revenue_growth_pct": round(revenue_growth, 1) if revenue_growth is not None else None,
        "profitability_score": profit_score,
        "net_margin_pct": round(net_margin, 1) if net_margin is not None else None,
        "valuation_risk": valuation_risk,
        "pe": round(pe, 1) if pe else None,
        "overall_risk": overall,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(compute_scores("AAPL"), indent=2))