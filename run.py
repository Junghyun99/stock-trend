"""
run.py  ─  원클릭 실행 스크립트
  1. yfinance로 탑 100 주식 3년 데이터 수집
  2. 추세 자동 분류 (강세 / 횡보 / 하락 / 반등)
  3. 인터랙티브 HTML 리포트 생성

Usage:
  python run.py
  python run.py --no-fetch   # 기존 stock_data.json 재사용
"""

import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="US Stock Trend Analyzer")
    parser.add_argument("--no-fetch", action="store_true",
                        help="stock_data.json 재사용 (데이터 수집 생략)")
    args = parser.parse_args()

    if not args.no_fetch:
        print("── Step 1/2  데이터 수집 ───────────────────────────────")
        from analyze_stocks import main as fetch
        fetch()
    else:
        if not Path("stock_data.json").exists():
            print("❌ stock_data.json 없음. --no-fetch 옵션 없이 실행하세요.")
            return

    print("\n── Step 2/2  HTML 리포트 생성 ──────────────────────────")
    from build_report import build_report
    build_report()

    print("\n🎉 완료!  output/us_stock_trend_analysis.html 을 브라우저로 열어보세요.")


if __name__ == "__main__":
    main()
