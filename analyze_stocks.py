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
import json, time, argparse

from fetch_universe import get_top_n


# ── 데이터 수집 ──────────────────────────────────────────────────────
def fetch_monthly_close(ticker: str, period: str = "3y") -> pd.Series | None:
    try:
        hist = yf.Ticker(ticker).history(period=period, interval="1mo")
        if hist.empty or len(hist) < 18:
            return None
        return hist["Close"].dropna()
    except Exception as e:
        print(f"  ⚠  {ticker}: {e}")
        return None


# ── 추세 분류 (선형회귀 기반) ────────────────────────────────────────
def classify_trend(prices: pd.Series) -> dict:
    """
    그래프 추세선 형태로 분류
    
    핵심 지표
    ---------
    slope_pct  : 전체 선형회귀 기울기 (월평균가 대비 %, 방향·속도)
    r2         : 결정계수 (추세의 명확성 0~1)
    slope_early: 전반 2/3 구간 기울기
    slope_late : 후반 1/3 구간 기울기  ← 반등 감지 핵심
    
    분류 규칙
    ---------
    반등 : 전반 기울기 < 0  AND  후반 기울기 > 0  (V자 혹은 U자)
    강세 : 전체 기울기 > 임계값  AND  R² 양호
    하락 : 전체 기울기 < -임계값 AND  R² 양호
    횡보 : 나머지 (기울기 약하거나 R² 낮아 추세 불명확)
    """
    n    = len(prices)
    vals = prices.values
    x    = np.arange(n, dtype=float)

    # ── 전체 선형회귀 ──
    slope_all, intercept, r_val, p_val, _ = stats.linregress(x, vals)
    r2        = r_val ** 2
    slope_pct = slope_all / vals.mean() * 100   # 월 기울기 (평균가 대비 %)

    # ── 전반부 2/3 vs 후반부 1/3 기울기 ──
    split     = max(6, int(n * 2 / 3))
    x_e, v_e  = x[:split],  vals[:split]
    x_l, v_l  = x[split:],  vals[split:]

    slope_e, *_ = stats.linregress(x_e, v_e)
    slope_l, *_ = stats.linregress(x_l, v_l)

    slope_e_pct = slope_e / v_e.mean() * 100   # 전반부 기울기 %
    slope_l_pct = slope_l / v_l.mean() * 100   # 후반부 기울기 %

    # ── 회귀선 (차트 오버레이용) ──
    regression_line = [round(float(intercept + slope_all * i), 2) for i in x]

    # ── 수익률 (보조 지표) ──
    total_return = round((vals[-1] / vals[0] - 1) * 100, 1)
    return_6m    = round((vals[-1] / vals[max(0, n-6)] - 1) * 100, 1)
    return_1y    = round((vals[-1] / vals[max(0, n-12)] - 1) * 100, 1)

    # ── 분류 ──
    # 반등: 전반 하락 추세 → 후반 상승 전환 (V자/U자)
    if slope_e_pct < -0.2 and slope_l_pct > 0.4:
        trend = "recovering"

    # 강세: 전체 기울기 양수 + 추세 명확 (R² ≥ 0.35)
    elif slope_pct > 0.3 and r2 >= 0.35:
        trend = "bullish"

    # 하락: 전체 기울기 음수 + 추세 명확
    elif slope_pct < -0.3 and r2 >= 0.35:
        trend = "bearish"

    # 횡보: 기울기 약하거나 R² 낮아 방향성 불명확
    else:
        trend = "sideways"

    return {
        "trend":           trend,
        "slope_pct":       round(slope_pct, 3),      # 월 기울기 (평균가 %)
        "r2":              round(r2, 3),              # 결정계수
        "slope_early_pct": round(slope_e_pct, 3),    # 전반부 기울기
        "slope_late_pct":  round(slope_l_pct, 3),    # 후반부 기울기
        "total_return":    total_return,
        "return_6m":       return_6m,
        "return_1y":       return_1y,
        "regression_line": regression_line,
    }


# ── 차트용 정규화 시리즈 ─────────────────────────────────────────────
def normalize_prices(prices: pd.Series, max_points: int = 36) -> tuple[list, list, list]:
    """base=100 정규화, (labels, price_values, regression_values) 반환"""
    prices = prices.tail(max_points)
    base   = prices.iloc[0]
    labels = [dt.strftime("%Y-%m") for dt in prices.index]
    values = [round(v / base * 100, 2) for v in prices.values]
    return labels, values


# ── 메인 ─────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n",      type=int,  default=100,  help="분석 종목 수 (기본 100)")
    parser.add_argument("--force", action="store_true",     help="유니버스 캐시 무시하고 재조회")
    args = parser.parse_args()

    print("=" * 62)
    print(f"  미국 탑 {args.n} 기업 주가 추세 분석  (yfinance · 3Y monthly)")
    print("  분류 기준: 선형회귀 기울기 + R² + 전/후반 기울기 비교")
    print("=" * 62)

    # 동적 유니버스 조회 (S&P 500 시가총액 상위 N개)
    universe = get_top_n(n=args.n, force_refresh=args.force)
    print(f"\n📋 분석 대상: {len(universe)}개 종목\n")

    results  = []
    failures = []

    for i, (ticker, name, sector) in enumerate(universe, 1):
        print(f"[{i:3d}/{args.n}] {ticker:7s} {name[:25]:25s}", end=" → ")

        prices = fetch_monthly_close(ticker)
        if prices is None:
            print("SKIP")
            failures.append(ticker)
            continue

        info     = classify_trend(prices)
        labels, norm_data = normalize_prices(prices)

        # 회귀선도 정규화
        base = prices.dropna().iloc[0]
        reg_raw = info.pop("regression_line")
        reg_norm = [round(v / base * 100, 2) for v in reg_raw[-len(norm_data):]]

        trend = info["trend"]
        s_pct = info["slope_pct"]
        r2    = info["r2"]
        print(f"{trend:12s} | slope:{s_pct:+.3f}%/월  R²:{r2:.2f}  "
              f"early:{info['slope_early_pct']:+.3f}  late:{info['slope_late_pct']:+.3f}")

        results.append({
            "ticker":        ticker,
            "name":          name,
            "sector":        sector,
            "current_price": round(float(prices.iloc[-1]), 2),
            "chart_labels":  labels,
            "chart_data":    norm_data,
            "regression":    reg_norm,
            **info,
        })
        time.sleep(0.3)

    # ── 요약 ──
    counts = Counter(r["trend"] for r in results)
    print("\n" + "=" * 62)
    print(f"✅ 완료: {len(results):3d}개   ❌ 실패: {len(failures):2d}개")
    print(f"  🟢 강세장   (Bullish)   : {counts['bullish']:3d}개")
    print(f"  🟡 횡보장   (Sideways)  : {counts['sideways']:3d}개")
    print(f"  🔴 하락장   (Bearish)   : {counts['bearish']:3d}개")
    print(f"  🔵 반등 중  (Recovering): {counts['recovering']:3d}개")

    out = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "classify_method": "linear_regression_slope_r2",
        "stocks": results,
    }
    with open("stock_data.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("\n📁 stock_data.json 저장 완료")


if __name__ == "__main__":
    main()
