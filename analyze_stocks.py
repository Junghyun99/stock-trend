"""
미국 상장 탑 100 기업 주가 추세 분석기
- yfinance로 3년 실데이터 수집
- 선형회귀 기반 추세 자동 분류 (강세/횡보/하락/반등)
- 결과를 JSON으로 저장
"""

import yfinance as yf
import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime
from collections import Counter
import json, time

# ── 탑 100 종목 리스트 ──────────────────────────────────────────────
TOP_100 = [
    ("AAPL",  "Apple",               "Technology"),
    ("MSFT",  "Microsoft",           "Technology"),
    ("NVDA",  "NVIDIA",              "Technology"),
    ("AMZN",  "Amazon",              "Consumer Disc."),
    ("GOOGL", "Alphabet (A)",        "Technology"),
    ("META",  "Meta Platforms",      "Technology"),
    ("TSLA",  "Tesla",               "Consumer Disc."),
    ("BRK-B", "Berkshire Hathaway",  "Financials"),
    ("TSM",   "TSMC",                "Technology"),
    ("LLY",   "Eli Lilly",           "Healthcare"),
    ("AVGO",  "Broadcom",            "Technology"),
    ("JPM",   "JPMorgan Chase",      "Financials"),
    ("V",     "Visa",                "Financials"),
    ("UNH",   "UnitedHealth",        "Healthcare"),
    ("XOM",   "ExxonMobil",          "Energy"),
    ("MA",    "Mastercard",          "Financials"),
    ("COST",  "Costco",              "Consumer Staples"),
    ("HD",    "Home Depot",          "Consumer Disc."),
    ("JNJ",   "Johnson & Johnson",   "Healthcare"),
    ("PG",    "Procter & Gamble",    "Consumer Staples"),
    ("WMT",   "Walmart",             "Consumer Staples"),
    ("NFLX",  "Netflix",             "Technology"),
    ("ORCL",  "Oracle",              "Technology"),
    ("BAC",   "Bank of America",     "Financials"),
    ("ABBV",  "AbbVie",              "Healthcare"),
    ("CRM",   "Salesforce",          "Technology"),
    ("CVX",   "Chevron",             "Energy"),
    ("KO",    "Coca-Cola",           "Consumer Staples"),
    ("AMD",   "Advanced Micro Dev.", "Technology"),
    ("MRK",   "Merck",               "Healthcare"),
    ("WFC",   "Wells Fargo",         "Financials"),
    ("ASML",  "ASML Holding",        "Technology"),
    ("ACN",   "Accenture",           "Technology"),
    ("TMO",   "Thermo Fisher",       "Healthcare"),
    ("MCD",   "McDonald's",          "Consumer Disc."),
    ("CSCO",  "Cisco Systems",       "Technology"),
    ("NOW",   "ServiceNow",          "Technology"),
    ("ABT",   "Abbott Labs",         "Healthcare"),
    ("ADBE",  "Adobe",               "Technology"),
    ("GS",    "Goldman Sachs",       "Financials"),
    ("IBM",   "IBM",                 "Technology"),
    ("PEP",   "PepsiCo",             "Consumer Staples"),
    ("ISRG",  "Intuitive Surgical",  "Healthcare"),
    ("TXN",   "Texas Instruments",   "Technology"),
    ("MS",    "Morgan Stanley",      "Financials"),
    ("DHR",   "Danaher",             "Healthcare"),
    ("INTU",  "Intuit",              "Technology"),
    ("GE",    "GE Aerospace",        "Industrials"),
    ("QCOM",  "Qualcomm",            "Technology"),
    ("CAT",   "Caterpillar",         "Industrials"),
    ("AMGN",  "Amgen",               "Healthcare"),
    ("BKNG",  "Booking Holdings",    "Consumer Disc."),
    ("SPGI",  "S&P Global",          "Financials"),
    ("NEE",   "NextEra Energy",      "Utilities"),
    ("AXP",   "American Express",    "Financials"),
    ("UBER",  "Uber Technologies",   "Technology"),
    ("T",     "AT&T",                "Communication"),
    ("LOW",   "Lowe's",              "Consumer Disc."),
    ("AMAT",  "Applied Materials",   "Technology"),
    ("DE",    "Deere & Company",     "Industrials"),
    ("BLK",   "BlackRock",           "Financials"),
    ("VRTX",  "Vertex Pharma",       "Healthcare"),
    ("GILD",  "Gilead Sciences",     "Healthcare"),
    ("ETN",   "Eaton Corp",          "Industrials"),
    ("BMY",   "Bristol-Myers Squibb","Healthcare"),
    ("ADP",   "ADP",                 "Technology"),
    ("SYK",   "Stryker",             "Healthcare"),
    ("LRCX",  "Lam Research",        "Technology"),
    ("CB",    "Chubb",               "Financials"),
    ("MDT",   "Medtronic",           "Healthcare"),
    ("KLAC",  "KLA Corp",            "Technology"),
    ("C",     "Citigroup",           "Financials"),
    ("SO",    "Southern Company",    "Utilities"),
    ("MU",    "Micron Technology",   "Technology"),
    ("PLD",   "Prologis",            "Real Estate"),
    ("SCHW",  "Charles Schwab",      "Financials"),
    ("ZTS",   "Zoetis",              "Healthcare"),
    ("MMC",   "Marsh McLennan",      "Financials"),
    ("REGN",  "Regeneron Pharma",    "Healthcare"),
    ("CME",   "CME Group",           "Financials"),
    ("TJX",   "TJX Companies",       "Consumer Disc."),
    ("DUK",   "Duke Energy",         "Utilities"),
    ("PANW",  "Palo Alto Networks",  "Technology"),
    ("ICE",   "Intercontinental Exch","Financials"),
    ("PH",    "Parker Hannifin",     "Industrials"),
    ("CL",    "Colgate-Palmolive",   "Consumer Staples"),
    ("EOG",   "EOG Resources",       "Energy"),
    ("SHW",   "Sherwin-Williams",    "Materials"),
    ("CDNS",  "Cadence Design",      "Technology"),
    ("SNPS",  "Synopsys",            "Technology"),
    ("MSI",   "Motorola Solutions",  "Technology"),
    ("HCA",   "HCA Healthcare",      "Healthcare"),
    ("ITW",   "Illinois Tool Works", "Industrials"),
    ("AMT",   "American Tower",      "Real Estate"),
    ("NSC",   "Norfolk Southern",    "Industrials"),
    ("FCX",   "Freeport-McMoRan",    "Materials"),
    ("WDAY",  "Workday",             "Technology"),
    ("AON",   "Aon plc",             "Financials"),
    ("MELI",  "MercadoLibre",        "Consumer Disc."),
]


# ── 데이터 수집 ──────────────────────────────────────────────────────
def fetch_monthly_close(ticker: str, period: str = "3y") -> pd.Series | None:
    """yfinance로 월봉 종가 시리즈 반환"""
    try:
        hist = yf.Ticker(ticker).history(period=period, interval="1mo")
        if hist.empty or len(hist) < 12:
            return None
        return hist["Close"].dropna()
    except Exception as e:
        print(f"  ⚠  {ticker}: {e}")
        return None


# ── 추세 분류 ────────────────────────────────────────────────────────
def classify_trend(prices: pd.Series) -> tuple[str, float, float, float]:
    """
    Returns
    -------
    trend        : bullish | sideways | bearish | recovering
    total_return : 3년 수익률 (%)
    return_6m    : 최근 6개월 수익률 (%)
    return_1y    : 최근 1년 수익률 (%)
    """
    n = len(prices)

    total_return = round((prices.iloc[-1] / prices.iloc[0] - 1) * 100, 1)
    return_6m    = round((prices.iloc[-1] / prices.iloc[max(0, n - 6)]  - 1) * 100, 1)
    return_1y    = round((prices.iloc[-1] / prices.iloc[max(0, n - 12)] - 1) * 100, 1)

    # 선형회귀 기울기 (정규화)
    x = np.arange(n)
    slope, *_ = stats.linregress(x, prices.values)
    slope_pct  = slope / prices.mean() * 100        # 월평균 대비 %

    # ── 분류 규칙 ──
    # 반등: 전체 수익 나쁘지만 최근 1년이 크게 회복
    if total_return < 15 and return_6m >= 15 and return_1y >= 20:
        trend = "recovering"
    # 하락: 누적 손실 -15% 이하, 최근도 부진
    elif total_return <= -15 and return_6m < 10:
        trend = "bearish"
    # 강세: 3년 +30% 초과 또는 기울기 강하고 수익 양호
    elif total_return >= 30 or (slope_pct >= 0.5 and total_return >= 15):
        trend = "bullish"
    # 나머지: 횡보
    else:
        trend = "sideways"

    return trend, total_return, return_6m, return_1y


# ── 차트용 정규화 시리즈 ─────────────────────────────────────────────
def normalize_prices(prices: pd.Series, max_points: int = 36) -> tuple[list, list]:
    """첫 가격 = 100 으로 정규화, (labels, values) 반환"""
    prices = prices.tail(max_points)
    base   = prices.iloc[0]
    labels = [dt.strftime("%Y-%m") for dt in prices.index]
    values = [round(v / base * 100, 2) for v in prices.values]
    return labels, values


# ── 메인 ─────────────────────────────────────────────────────────────
def main():
    print("=" * 62)
    print("  미국 탑 100 기업 주가 추세 분석  (yfinance · 3Y monthly)")
    print("=" * 62)

    results  = []
    failures = []

    for i, (ticker, name, sector) in enumerate(TOP_100, 1):
        print(f"[{i:3d}/100] {ticker:7s} {name[:28]:28s}", end=" → ")

        prices = fetch_monthly_close(ticker)
        if prices is None:
            print("SKIP")
            failures.append(ticker)
            continue

        trend, total_ret, ret_6m, ret_1y = classify_trend(prices)
        labels, norm_data = normalize_prices(prices)
        current_price = round(float(prices.iloc[-1]), 2)

        sign = lambda v: f"+{v}%" if v > 0 else f"{v}%"
        print(f"{trend:12s} | 3Y:{sign(total_ret):8s}  6M:{sign(ret_6m):7s}  1Y:{sign(ret_1y)}")

        results.append({
            "ticker":        ticker,
            "name":          name,
            "sector":        sector,
            "trend":         trend,
            "total_return":  total_ret,
            "return_6m":     ret_6m,
            "return_1y":     ret_1y,
            "current_price": current_price,
            "chart_labels":  labels,
            "chart_data":    norm_data,
        })

        time.sleep(0.3)     # rate-limit 방지

    # ── 요약 ──
    counts = Counter(r["trend"] for r in results)
    print("\n" + "=" * 62)
    print(f"✅ 완료: {len(results):3d}개   ❌ 실패: {len(failures):2d}개")
    print(f"  🟢 강세장   (Bullish)   : {counts['bullish']:3d}개")
    print(f"  🟡 횡보장   (Sideways)  : {counts['sideways']:3d}개")
    print(f"  🔴 하락장   (Bearish)   : {counts['bearish']:3d}개")
    print(f"  🔵 반등 중  (Recovering): {counts['recovering']:3d}개")
    if failures:
        print(f"\n  실패 종목: {', '.join(failures)}")

    # ── JSON 저장 ──
    # chart_labels 는 모든 종목 공통 (마지막 종목 기준)
    out = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "stocks":       results,
    }
    with open("stock_data.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("\n📁 stock_data.json 저장 완료")


if __name__ == "__main__":
    main()
