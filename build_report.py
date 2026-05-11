"""
stock_data.json → 인터랙티브 HTML 리포트 생성
의존: stock_data.json (analyze_stocks.py 실행 후 생성)
"""

import json
from pathlib import Path
from collections import Counter


def build_report(json_path: str = "stock_data.json",
                 out_path:  str = "output/us_stock_trend_analysis.html") -> None:

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    stocks     = data["stocks"]
    generated  = data.get("generated_at", "")
    counts     = Counter(s["trend"] for s in stocks)
    stocks_json = json.dumps(stocks,  ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>미국 탑 100 기업 주가 추세 분석</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --green:#22c55e;--green-bg:#f0fdf4;--green-bd:#86efac;
  --yellow:#eab308;--yellow-bg:#fefce8;--yellow-bd:#fde047;
  --red:#ef4444;--red-bg:#fef2f2;--red-bd:#fca5a5;
  --blue:#3b82f6;--blue-bg:#eff6ff;--blue-bd:#93c5fd;
  --surface:#f9fafb;--card:#fff;--text:#111827;--text2:#6b7280;
  --radius:12px;--shadow:0 2px 12px rgba(0,0,0,.08)
}}
body{{font-family:'Segoe UI',-apple-system,sans-serif;background:#f1f5f9;color:var(--text);min-height:100vh}}
.header{{background:linear-gradient(135deg,#1e293b,#334155);color:#fff;padding:32px 24px 28px}}
.header h1{{font-size:1.75rem;font-weight:700;margin-bottom:6px}}
.header p{{font-size:.875rem;color:#94a3b8}}
.note{{display:inline-block;margin-top:10px;background:rgba(255,255,255,.1);border-radius:6px;padding:6px 12px;font-size:.78rem;color:#cbd5e1}}
.summary{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;padding:20px 24px;max-width:1400px;margin:0 auto}}
.scard{{background:var(--card);border-radius:var(--radius);padding:20px 22px;box-shadow:var(--shadow);cursor:pointer;border:2px solid transparent;transition:.2s}}
.scard:hover,.scard.active{{border-color:var(--accent);box-shadow:0 4px 20px rgba(0,0,0,.12)}}
.scard .emoji{{font-size:1.8rem;margin-bottom:8px}}
.scard .label{{font-size:1rem;font-weight:700;color:var(--accent)}}
.scard .count{{font-size:2rem;font-weight:800;line-height:1.1}}
.scard .desc{{font-size:.72rem;color:var(--text2);margin-top:4px;line-height:1.4}}
.scard.green{{--accent:var(--green)}}.scard.yellow{{--accent:var(--yellow)}}
.scard.red{{--accent:var(--red)}}.scard.blue{{--accent:var(--blue)}}
.controls{{max-width:1400px;margin:0 auto;padding:0 24px 16px;display:flex;gap:12px;flex-wrap:wrap;align-items:center}}
.search-wrap{{flex:1;min-width:180px;position:relative}}
.search-wrap input{{width:100%;padding:9px 14px 9px 36px;border:1.5px solid #e2e8f0;border-radius:8px;font-size:.875rem;background:#fff;outline:none;transition:.2s}}
.search-wrap input:focus{{border-color:#6366f1}}
.search-wrap .icon{{position:absolute;left:10px;top:50%;transform:translateY(-50%);color:#9ca3af}}
select{{padding:9px 14px;border:1.5px solid #e2e8f0;border-radius:8px;font-size:.875rem;background:#fff;cursor:pointer;outline:none}}
.stat-bar{{font-size:.8rem;color:var(--text2);margin-left:auto;padding:9px 0;white-space:nowrap}}
.grid{{max-width:1400px;margin:0 auto;padding:0 24px 40px;display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:18px}}
.stock-card{{background:var(--card);border-radius:var(--radius);padding:18px 18px 14px;box-shadow:var(--shadow);transition:.2s;border-left:4px solid var(--ca);cursor:pointer}}
.stock-card:hover{{box-shadow:0 6px 24px rgba(0,0,0,.12);transform:translateY(-1px)}}
.stock-card.t-bullish{{--ca:var(--green)}}.stock-card.t-sideways{{--ca:var(--yellow)}}
.stock-card.t-bearish{{--ca:var(--red)}}.stock-card.t-recovering{{--ca:var(--blue)}}
.card-header{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px}}
.ticker{{font-size:1.1rem;font-weight:800;letter-spacing:.03em}}
.badge{{font-size:.68rem;font-weight:700;padding:3px 8px;border-radius:20px;display:flex;align-items:center;gap:3px}}
.badge.t-bullish{{background:var(--green-bg);color:var(--green);border:1px solid var(--green-bd)}}
.badge.t-sideways{{background:var(--yellow-bg);color:#a16207;border:1px solid var(--yellow-bd)}}
.badge.t-bearish{{background:var(--red-bg);color:var(--red);border:1px solid var(--red-bd)}}
.badge.t-recovering{{background:var(--blue-bg);color:var(--blue);border:1px solid var(--blue-bd)}}
.company-name{{font-size:.78rem;color:var(--text2);margin-bottom:2px}}
.sector-tag{{font-size:.68rem;color:#9ca3af}}
.metrics{{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin:12px 0}}
.metric{{text-align:center;padding:7px 4px;background:var(--surface);border-radius:8px}}
.metric .val{{font-size:.92rem;font-weight:700}}
.metric .lbl{{font-size:.6rem;color:var(--text2);margin-top:1px}}
.pos{{color:var(--green)}}.neg{{color:var(--red)}}.neu{{color:var(--text2)}}
.chart-wrap{{height:90px;margin-top:10px}}
.modal-overlay{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:1000;align-items:center;justify-content:center}}
.modal-overlay.open{{display:flex}}
.modal{{background:#fff;border-radius:16px;width:min(640px,96vw);max-height:90vh;overflow-y:auto;padding:28px;box-shadow:0 20px 60px rgba(0,0,0,.25);position:relative}}
.modal h2{{font-size:1.4rem;font-weight:800;margin-bottom:4px}}
.modal .sub{{font-size:.82rem;color:var(--text2);margin-bottom:14px}}
.modal-chart{{height:220px;margin:14px 0 18px}}
.modal-metrics{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}}
.modal-metric{{background:var(--surface);padding:14px;border-radius:10px;text-align:center}}
.modal-metric .val{{font-size:1.2rem;font-weight:800}}
.modal-metric .lbl{{font-size:.72rem;color:var(--text2);margin-top:3px}}
.close-btn{{position:absolute;top:16px;right:20px;font-size:1.4rem;cursor:pointer;color:var(--text2);background:none;border:none}}
@media(max-width:640px){{.summary{{grid-template-columns:repeat(2,1fr)}}.grid{{grid-template-columns:1fr}}.header h1{{font-size:1.3rem}}}}
</style>
</head>
<body>
<div class="header">
  <h1>📈 미국 상장 탑 100 기업 주가 추세 분석</h1>
  <p>yfinance 3년 실데이터 기반 · 생성일시: {generated}</p>
  <span class="note">⚠️ 본 데이터는 분석 목적의 참고용이며 투자 권고가 아닙니다.</span>
</div>

<div class="summary">
  <div class="scard green active" onclick="filterTrend('bullish',this)">
    <div class="emoji">🟢</div>
    <div class="label">강세장 (Bullish)</div>
    <div class="count">{counts['bullish']}</div>
    <div class="desc">3년 수익률 +30% 이상 · 뚜렷한 상승 추세</div>
  </div>
  <div class="scard yellow" onclick="filterTrend('sideways',this)">
    <div class="emoji">🟡</div>
    <div class="label">횡보장 (Sideways)</div>
    <div class="count">{counts['sideways']}</div>
    <div class="desc">-15% ~ +30% · 방향성 없이 등락 반복</div>
  </div>
  <div class="scard red" onclick="filterTrend('bearish',this)">
    <div class="emoji">🔴</div>
    <div class="label">하락장 (Bearish)</div>
    <div class="count">{counts['bearish']}</div>
    <div class="desc">3년 -15% 이하 · 하락 추세 지속</div>
  </div>
  <div class="scard blue" onclick="filterTrend('recovering',this)">
    <div class="emoji">🔵</div>
    <div class="label">반등 중 (Recovering)</div>
    <div class="count">{counts['recovering']}</div>
    <div class="desc">하락 후 최근 6개월 +15% 이상 반등</div>
  </div>
</div>

<div class="controls">
  <div class="search-wrap">
    <span class="icon">🔍</span>
    <input id="searchInput" type="text" placeholder="종목 검색 (AAPL, Apple...)" oninput="renderCards()">
  </div>
  <select id="sectorFilter" onchange="renderCards()">
    <option value="">전체 섹터</option>
    <option>Technology</option><option>Healthcare</option><option>Financials</option>
    <option>Consumer Disc.</option><option>Consumer Staples</option><option>Industrials</option>
    <option>Energy</option><option>Materials</option><option>Real Estate</option>
    <option>Utilities</option><option>Communication</option>
  </select>
  <select id="sortSelect" onchange="renderCards()">
    <option value="default">정렬: 기본순</option>
    <option value="ret_desc">3Y 수익률 높은순</option>
    <option value="ret_asc">3Y 수익률 낮은순</option>
    <option value="6m_desc">6M 수익률 높은순</option>
    <option value="name_asc">종목명순</option>
  </select>
  <div class="stat-bar" id="statBar"></div>
</div>

<div class="grid" id="cardGrid"></div>

<div class="modal-overlay" id="modal" onclick="closeModal(event)">
  <div class="modal">
    <button class="close-btn" onclick="document.getElementById('modal').classList.remove('open')">✕</button>
    <h2 id="mTitle">-</h2>
    <div class="sub" id="mSub">-</div>
    <div id="mBadge"></div>
    <div class="modal-chart"><canvas id="modalChart"></canvas></div>
    <div class="modal-metrics" id="mMetrics"></div>
  </div>
</div>

<script>
const STOCKS = {stocks_json};
const TREND_META = {{
  bullish:    {{ko:"강세장",  emoji:"🟢", color:"#22c55e", fill:"rgba(34,197,94,.1)"}},
  sideways:   {{ko:"횡보장",  emoji:"🟡", color:"#eab308", fill:"rgba(234,179,8,.1)"}},
  bearish:    {{ko:"하락장",  emoji:"🔴", color:"#ef4444", fill:"rgba(239,68,68,.1)"}},
  recovering: {{ko:"반등 중", emoji:"🔵", color:"#3b82f6", fill:"rgba(59,130,246,.1)"}},
}};

let currentFilter = 'bullish';
let miniCharts = {{}};
let modalChart  = null;

const cv = v => v > 0 ? `<span class="pos">+${{v}}%</span>`
               : v < 0 ? `<span class="neg">${{v}}%</span>`
               :          `<span class="neu">${{v}}%</span>`;

function getFiltered() {{
  const q  = document.getElementById('searchInput').value.toLowerCase();
  const sc = document.getElementById('sectorFilter').value;
  const st = document.getElementById('sortSelect').value;
  let list = STOCKS.filter(s =>
    (!currentFilter || s.trend === currentFilter) &&
    (!q  || s.ticker.toLowerCase().includes(q) || s.name.toLowerCase().includes(q)) &&
    (!sc || s.sector === sc)
  );
  if      (st === 'ret_desc') list.sort((a,b)=>b.total_return-a.total_return);
  else if (st === 'ret_asc')  list.sort((a,b)=>a.total_return-b.total_return);
  else if (st === '6m_desc')  list.sort((a,b)=>b.return_6m-a.return_6m);
  else if (st === 'name_asc') list.sort((a,b)=>a.name.localeCompare(b.name));
  return list;
}}

function renderCards() {{
  Object.values(miniCharts).forEach(c=>c.destroy()); miniCharts={{}};
  const list = getFiltered();
  document.getElementById('statBar').textContent = `${{list.length}}개 표시 중 / 전체 ${{STOCKS.length}}개`;
  document.getElementById('cardGrid').innerHTML = list.map(s => {{
    const m = TREND_META[s.trend];
    return `<div class="stock-card t-${{s.trend}}" onclick="openModal('${{s.ticker}}')">
      <div class="card-header">
        <div>
          <div class="ticker">${{s.ticker}}</div>
          <div class="company-name">${{s.name}}</div>
          <div class="sector-tag">${{s.sector}}</div>
        </div>
        <div class="badge t-${{s.trend}}">${{m.emoji}} ${{m.ko}}</div>
      </div>
      <div class="metrics">
        <div class="metric"><div class="val">${{cv(s.total_return)}}</div><div class="lbl">3Y 수익률</div></div>
        <div class="metric"><div class="val">${{cv(s.return_6m)}}</div><div class="lbl">6M 수익률</div></div>
        <div class="metric"><div class="val">${{cv(s.return_1y)}}</div><div class="lbl">1Y 수익률</div></div>
      </div>
      <div class="chart-wrap"><canvas id="mc-${{s.ticker}}"></canvas></div>
    </div>`;
  }}).join('');
  list.forEach(s => {{
    const el = document.getElementById('mc-' + s.ticker);
    if (!el) return;
    const m = TREND_META[s.trend];
    miniCharts[s.ticker] = new Chart(el, {{
      type:'line',
      data:{{labels:s.chart_labels, datasets:[{{data:s.chart_data, borderColor:m.color,
        backgroundColor:m.fill, borderWidth:1.8, pointRadius:0, fill:true, tension:0.4}}]}},
      options:{{responsive:true, maintainAspectRatio:false, animation:false,
        plugins:{{legend:{{display:false}},tooltip:{{enabled:false}}}},
        scales:{{x:{{display:false}},y:{{display:false,grace:'5%'}}}}}}
    }});
  }});
}}

function filterTrend(t, el) {{
  document.querySelectorAll('.scard').forEach(c=>c.classList.remove('active'));
  el.classList.add('active'); currentFilter = t; renderCards();
}}

function openModal(ticker) {{
  const s = STOCKS.find(x=>x.ticker===ticker); if(!s) return;
  const m = TREND_META[s.trend];
  document.getElementById('mTitle').textContent = `${{s.ticker}}  ${{s.name}}`;
  document.getElementById('mSub').textContent   = `${{s.sector}} · 현재가 $${{s.current_price}}`;
  document.getElementById('mBadge').innerHTML   = `<span class="badge t-${{s.trend}}">${{m.emoji}} ${{m.ko}}</span>`;
  document.getElementById('mMetrics').innerHTML = `
    <div class="modal-metric"><div class="val">${{cv(s.total_return)}}</div><div class="lbl">3년 누적 수익률</div></div>
    <div class="modal-metric"><div class="val">${{cv(s.return_6m)}}</div><div class="lbl">최근 6개월</div></div>
    <div class="modal-metric"><div class="val">${{cv(s.return_1y)}}</div><div class="lbl">최근 1년</div></div>`;
  if (modalChart) {{ modalChart.destroy(); modalChart=null; }}
  modalChart = new Chart(document.getElementById('modalChart'), {{
    type:'line',
    data:{{labels:s.chart_labels, datasets:[{{label:`${{s.ticker}} (정규화 · 기준=100)`,
      data:s.chart_data, borderColor:m.color, backgroundColor:m.fill,
      borderWidth:2.5, pointRadius:2, fill:true, tension:0.4}}]}},
    options:{{responsive:true, maintainAspectRatio:false,
      plugins:{{legend:{{position:'top',labels:{{font:{{size:11}}}}}},
        tooltip:{{callbacks:{{label:c=>` ${{c.parsed.y.toFixed(1)}} (기준 100)`}}}}}},
      scales:{{x:{{ticks:{{maxTicksLimit:12,font:{{size:10}}}},grid:{{color:'#f1f5f9'}}}},
               y:{{ticks:{{font:{{size:10}},callback:v=>v.toFixed(0)}},grid:{{color:'#f1f5f9'}}}}}}}}
  }});
  document.getElementById('modal').classList.add('open');
}}

function closeModal(e) {{
  if (e.target===document.getElementById('modal'))
    document.getElementById('modal').classList.remove('open');
}}

renderCards();
</script>
</body>
</html>"""

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ HTML 리포트 생성 완료: {out_path}")


if __name__ == "__main__":
    build_report()
