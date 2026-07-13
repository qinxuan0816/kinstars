"""
Numeric accuracy eval:
Check whether the AI-generated report contains numbers that contradict
the ground-truth financial data from yfinance.
"""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_fetch import get_company_info, get_financials
from src.report import generate_report
import re

# Companies to test
TEST_TICKERS = ["AAPL", "MSFT", "NVDA"]


def extract_ground_truth(ticker):
    """Pull key numbers we consider authoritative from yfinance."""
    info = get_company_info(ticker)
    fin = get_financials(ticker)
    income = fin["income_statement"]

    truth = {}
    if info.get("pe_trailing"):
        truth["trailing_pe"] = round(info["pe_trailing"], 1)
    if "Total Revenue" in income.index:
        rev = income.loc["Total Revenue"].dropna()
        if len(rev) >= 1:
            truth["latest_revenue_b"] = round(float(rev.iloc[0]) / 1e9, 1)
    if "Net Income" in income.index:
        ni = income.loc["Net Income"].dropna()
        if len(ni) >= 1:
            truth["latest_net_income_b"] = round(float(ni.iloc[0]) / 1e9, 1)
    return truth


def numbers_in_text(text):
    """Extract all numbers (with optional B/T/% and $) from report text."""
    # captures things like $391.0B, 38.17, 93.7%
    return [float(x) for x in re.findall(r"[-+]?\d+\.?\d*", text)]


def check_report(ticker):
    truth = extract_ground_truth(ticker)
    report = generate_report(ticker)
    report_numbers = numbers_in_text(report)

    results = []
    for key, true_val in truth.items():
        # a value is "present" if some number in the report is within 2% of it
        tolerance = abs(true_val) * 0.02
        found = any(abs(n - true_val) <= tolerance for n in report_numbers)
        results.append({
            "metric": key,
            "ground_truth": true_val,
            "found_in_report": found,
        })
    return results, report


if __name__ == "__main__":
    total, passed = 0, 0
    print("=" * 60)
    print("NUMERIC ACCURACY EVAL")
    print("=" * 60)

    for ticker in TEST_TICKERS:
        print(f"\n### {ticker} ###")
        try:
            results, _ = check_report(ticker)
            for r in results:
                total += 1
                status = "PASS" if r["found_in_report"] else "MISS"
                if r["found_in_report"]:
                    passed += 1
                print(f"  [{status}] {r['metric']}: ground truth = {r['ground_truth']}")
        except Exception as e:
            print(f"  ERROR: {e}")

    print("\n" + "=" * 60)
    rate = (passed / total * 100) if total else 0
    print(f"RESULT: {passed}/{total} metrics correctly reflected  ({rate:.0f}%)")
    print("=" * 60)