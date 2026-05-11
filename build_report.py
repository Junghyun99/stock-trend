"""
stock_data.json → 인터랙티브 HTML 리포트 생성
- 주가 차트에 선형회귀 추세선 오버레이
- slope / R² / 전후반 기울기 표시
"""

import json
from pathlib import Path
from collections import Counter


def build_report(json_path="stock_data.json",
                 out_path="output/us_stock_trend_analysis.html"):

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    stocks    = data["stocks"]
    generated = data.get("generated_at", "")
    method    = data.get("classify_method", "")
    counts    = Counter(s["trend"] for s in stocks)
    stocks_js = json.dumps(stocks, ensure_ascii=False)

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
  --yellow:#d97706;--yellow-bg:#fffbeb;--yellow-bd:#fcd34d;
  --red:#ef4444;--red-bg:#fef2f2;--red-bd:#fca5a5;
  --blue:#3b82f6;--blue-bg:#eff6ff;--blue-bd:#93c5fd;
  --surface:#f8fafc;--card:#fff;--text:#111827;--text2:#64748b;
  --radius:12px;--shadow:0 1px 8px rgba(0,0,0,.08)
}}
body{{font-family:'Segoe UI',-apple-system,sans-serif;background:#f1f5f9;color:var(--text)}}
.header{{background:linear-gradient(135deg,#0f172a,#1e3a5f);color:#fff;padding:30px 24px 24px}}
.header h1{{font-size:1.6rem;font-weight:700;margin-bottom:5px}}
.header p{{font-size:.82rem;color:#94a3b8;line-height:1.6}}
.badge-method{{display:inline-block;margin-top:8px;background:rgba(99,102,241,.3);border:1px solid rgba(99,102,241,.5);
  border-radius:6px;padding:4px 10px;font-size:.75rem;color:#c7d2fe}}

.summary{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;padding:18px 24px;max-width:1440px;margin:0 auto}}
.scard{{background:var(--card);border-radius:var(--radius);padding:18px 20px;box-shadow:var(--shadow);
  cursor:pointer;border:2px solid transparent;transition:.18s}}
.scard:hover,.scard.active{{border-color:var(--ac);box-shadow:0 4px 16px rgba(0,0,0,.1)}}
.scard .ico{{font-size:1.6rem;margin-bottom:6px}}
.scard .lbl{{font-size:.9rem;font-weight:700;color:var(--ac)}}
.scard .cnt{{font-size:1.9rem;font-weight:800;line-height:1.1}}
.scard .dsc{{font-size:.7rem;color:var(--text2);margin-top:3px;line-height:1.4}}
.scard.g{{--ac:var(--green)}}.scard.y{{--ac:var(--yellow)}}
.scard.r{{--ac:var(--red)}}.scard.b{{--ac:var(--blue)}}

.controls{{max-width:1440px;margin:0 auto;padding:0 24px 14px;display:flex;gap:10px;flex-wrap:wrap;align-items:center}}
.srch{{flex:1;min-width:160px;position:relative}}
.srch input{{width:100%;padding:8px 12px 8px 34px;border:1.5px solid #e2e8f0;border-radius:8px;
  font-size:.85rem;background:#fff;outline:none;transition:.2s}}
.srch input:focus{{border-color:#6366f1}}
.srch .ico{{position:absolute;left:10px;top:50%;transform:translateY(-50%);color:#9ca3af;font-size:.85rem}}
select{{padding:8px 12px;border:1.5px solid #e2e8f0;border-radius:8px;font-size:.85rem;background:#fff;cursor:pointer;outline:none}}
.stat{{font-size:.78rem;color:var(--text2);margin-left:auto;white-space:nowrap}}

.grid{{max-width:1440px;margin:0 auto;padding:0 24px 40px;
  display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:16px}}

.card{{background:var(--card);border-radius:var(--radius);padding:16px 16px 12px;
  box-shadow:var(--shadow);transition:.18s;border-left:4px solid var(--ca);cursor:pointer}}
.card:hover{{box-shadow:0 5px 20px rgba(0,0,0,.1);transform:translateY(-1px)}}
.card.t-bullish{{--ca:var(--green)}}.card.t-sideways{{--ca:var(--yellow)}}
.card.t-bearish{{--ca:var(--red)}}.card.t-recovering{{--ca:var(--blue)}}

.ch{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px}}
.tk{{font-size:1.05rem;font-weight:800;letter-spacing:.02em}}
.badge{{font-size:.66rem;font-weight:700;padding:2px 7px;border-radius:16px;display:flex;align-items:center;gap:2px}}
.badge.t-bullish{{background:var(--green-bg);color:#16a34a;border:1px solid var(--green-bd)}}
.badge.t-sideways{{background:var(--yellow-bg);color:#b45309;border:1px solid var(--yellow-bd)}}
.badge.t-bearish{{background:var(--red-bg);color:var(--red);border:1px solid var(--red-bd)}}
.badge.t-recovering{{background:var(--blue-bg);color:var(--blue);border:1px solid var(--blue-bd)}}
.nm{{font-size:.75rem;color:var(--text2);margin-bottom:1px}}
.sc{{font-size:.66rem;color:#9ca3af}}

.mets{{display:grid;grid-template-columns:repeat(4,1fr);gap:5px;margin:10px 0 6px}}
.met{{text-align:center;padding:6px 2px;background:var(--surface);border-radius:7px}}
.met .v{{font-size:.82rem;font-weight:700}}
.met .l{{font-size:.58rem;color:var(--text2);margin-top:1px}}
.pos{{color:#16a34a}}.neg{{color:var(--red)}}.neu{{color:var(--text2)}}

.cw{{height:85px;margin-top:8px}}

/* 모달 */
.ov{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:1000;align-items:center;justify-content:center}}
.ov.open{{display:flex}}
.modal{{background:#fff;border-radius:16px;width:min(680px,96vw);max-height:92vh;overflow-y:auto;
  padding:26px;box-shadow:0 24px 60px rgba(0,0,0,.25);position:relative}}
.modal h2{{font-size:1.35rem;font-weight:800;margin-bottom:3px}}
.modal .sub{{font-size:.8rem;color:var(--text2);margin-bottom:12px}}
.mc{{height:240px;margin:12px 0 16px}}
.mm{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:12px}}
.mmk{{background:var(--surface);padding:12px;border-radius:9px;text-align:center}}
.mmk .v{{font-size:1.1rem;font-weight:800}}
.mmk .l{{font-size:.68rem;color:var(--text2);margin-top:2px}}
.reg-box{{background:#f8fafc;border:1px solid #e2e8f0;border-radius:9px;padding:12px 14px;font-size:.8rem;line-height:1.8}}
.reg-box b{{color:#334155}}
.xbtn{{position:absolute;top:14px;right:18px;font-size:1.3rem;cursor:pointer;
  color:var(--text2);background:none;border:none;line-height:1}}

@media(max-width:640px){{
  .summary{{grid-template-columns:repeat(2,1fr)}}
  .grid{{grid-template-columns:1fr}}
  .header h1{{font-size:1.25rem}}
  .mets{{grid-template-columns:repeat(2,1fr)}}
}}
</style>
</head>
<body>

<div class="header">
  <h1>📈 미국 상장 탑 100 기업 주가 추세 분석</h1>
  <p>yfinance 3년 월봉 실데이터 · 생성일시: {generated}</p>
  <span class="badge-method">📐 분류 방법: 선형회귀 기울기(slope) + 결정계수(R²) + 전/후반부 기울기 비교</span>
</div>

<div class="summary">
  <div class="scard g active" onclick="filt('bullish',this)">
    <div class="ico">🟢</div><div class="lbl">강세장 (Bullish)</div>
    <div class="cnt">{counts['bullish']}</div>
    <div class="dsc">slope &gt; 0 · R² 양호 · 우상향 추세선</div>
  </div>
  <div class="scard y" onclick="filt('sideways',this)">
    <div class="ico">🟡</div><div class="lbl">횡보장 (Sideways)</div>
    <div class="cnt">{counts['sideways']}</div>
    <div class="dsc">기울기 약하거나 R² 낮음 · 방향성 불명확</div>
  </div>
  <div class="scard r" onclick="filt('bearish',this)">
    <div class="ico">🔴</div><div class="lbl">하락장 (Bearish)</div>
    <div class="cnt">{counts['bearish']}</div>
    <div class="dsc">slope &lt; 0 · R² 양호 · 우하향 추세선</div>
  </div>
  <div class="scard b" onclick="filt('recovering',this)">
    <div class="ico">🔵</div><div class="lbl">반등 중 (Recovering)</div>
    <div class="cnt">{counts['recovering']}</div>
    <div class="dsc">전반 기울기↓ → 후반 기울기↑ (V/U자)</div>
  </div>
</div>

<div class="controls">
  <div class="srch">
    <span class="ico">🔍</span>
    <input id="si" type="text" placeholder="종목 검색 (AAPL, Apple...)" oninput="render()">
  </div>
  <select id="sf" onchange="render()">
    <option value="">전체 섹터</option>
    <option>Technology</option><option>Healthcare</option><option>Financials</option>
    <option>Consumer Disc.</option><option>Consumer Staples</option><option>Industrials</option>
    <option>Energy</option><option>Materials</option><option>Real Estate</option>
    <option>Utilities</option><option>Communication</option>
  </select>
  <select id="ss" onchange="render()">
    <option value="">정렬: 기본</option>
    <option value="slope_d">slope 높은순</option>
    <option value="slope_a">slope 낮은순</option>
    <option value="r2_d">R² 높은순</option>
    <option value="ret_d">3Y 수익률 높은순</option>
  </select>
  <div class="stat" id="st"></div>
</div>

<div class="grid" id="grid"></div>

<div class="ov" id="ov" onclick="closeOv(event)">
  <div class="modal">
    <button class="xbtn" onclick="document.getElementById('ov').classList.remove('open')">✕</button>
    <h2 id="mt">-</h2><div class="sub" id="ms">-</div>
    <div id="mb"></div>
    <div class="mc"><canvas id="mc"></canvas></div>
    <div class="mm" id="mm"></div>
    <div class="reg-box" id="mr"></div>
  </div>
</div>

<script>
const S  = {stocks_js};
const TM = {{
  bullish:    {{ko:"강세장",  e:"🟢", c:"#22c55e", f:"rgba(34,197,94,.12)"}},
  sideways:   {{ko:"횡보장",  e:"🟡", c:"#d97706", f:"rgba(217,119,6,.10)"}},
  bearish:    {{ko:"하락장",  e:"🔴", c:"#ef4444", f:"rgba(239,68,68,.10)"}},
  recovering: {{ko:"반등 중", e:"🔵", c:"#3b82f6", f:"rgba(59,130,246,.10)"}},
}};

let cur="bullish", minis={{}}, mInst=null;
const cv = v => v>0?`<span class="pos">+${{v}}%</span>`:v<0?`<span class="neg">${{v}}%</span>`:`<span class="neu">${{v}}%</span>`;
const fv = v => v>0?`<span class="pos">+${{v}}</span>`:v<0?`<span class="neg">${{v}}</span>`:`<span class="neu">${{v}}</span>`;

function getList(){{
  const q=document.getElementById('si').value.toLowerCase();
  const sc=document.getElementById('sf').value;
  const st=document.getElementById('ss').value;
  let L=S.filter(s=>(!cur||s.trend===cur)&&(!q||s.ticker.toLowerCase().includes(q)||s.name.toLowerCase().includes(q))&&(!sc||s.sector===sc));
  if(st==='slope_d') L.sort((a,b)=>b.slope_pct-a.slope_pct);
  else if(st==='slope_a') L.sort((a,b)=>a.slope_pct-b.slope_pct);
  else if(st==='r2_d')    L.sort((a,b)=>b.r2-a.r2);
  else if(st==='ret_d')   L.sort((a,b)=>b.total_return-a.total_return);
  return L;
}}

function render(){{
  Object.values(minis).forEach(c=>c.destroy()); minis={{}};
  const L=getList();
  document.getElementById('st').textContent=`${{L.length}}개 표시 / 전체 ${{S.length}}개`;
  document.getElementById('grid').innerHTML=L.map(s=>{{
    const m=TM[s.trend];
    return `<div class="card t-${{s.trend}}" onclick="openM('${{s.ticker}}')">
      <div class="ch">
        <div><div class="tk">${{s.ticker}}</div><div class="nm">${{s.name}}</div><div class="sc">${{s.sector}}</div></div>
        <div class="badge t-${{s.trend}}">${{m.e}} ${{m.ko}}</div>
      </div>
      <div class="mets">
        <div class="met"><div class="v">${{fv(s.slope_pct)}}<span style="font-size:.6rem">%/월</span></div><div class="l">slope</div></div>
        <div class="met"><div class="v">${{s.r2}}</div><div class="l">R²</div></div>
        <div class="met"><div class="v">${{cv(s.total_return)}}</div><div class="l">3Y 수익</div></div>
        <div class="met"><div class="v">${{cv(s.return_6m)}}</div><div class="l">6M 수익</div></div>
      </div>
      <div class="cw"><canvas id="mc-${{s.ticker}}"></canvas></div>
    </div>`;
  }}).join('');
  L.forEach(s=>{{
    const el=document.getElementById('mc-'+s.ticker); if(!el) return;
    const m=TM[s.trend];
    minis[s.ticker]=new Chart(el,{{
      type:'line',
      data:{{labels:s.chart_labels, datasets:[
        {{data:s.chart_data, borderColor:m.c, backgroundColor:m.f,
          borderWidth:1.8, pointRadius:0, fill:true, tension:0.3, order:2}},
        {{data:s.regression, borderColor:'rgba(100,116,139,.55)',
          borderWidth:1.5, borderDash:[4,3], pointRadius:0, fill:false, tension:0, order:1}}
      ]}},
      options:{{responsive:true, maintainAspectRatio:false, animation:false,
        plugins:{{legend:{{display:false}},tooltip:{{enabled:false}}}},
        scales:{{x:{{display:false}},y:{{display:false,grace:'8%'}}}}}}
    }});
  }});
}}

function filt(t,el){{
  document.querySelectorAll('.scard').forEach(c=>c.classList.remove('active'));
  el.classList.add('active'); cur=t; render();
}}

function openM(tk){{
  const s=S.find(x=>x.ticker===tk); if(!s) return;
  const m=TM[s.trend];
  document.getElementById('mt').textContent=`${{s.ticker}}  ${{s.name}}`;
  document.getElementById('ms').textContent=`${{s.sector}} · 현재가 $${{s.current_price}}`;
  document.getElementById('mb').innerHTML=`<span class="badge t-${{s.trend}}">${{m.e}} ${{m.ko}}</span><br><br>`;
  document.getElementById('mm').innerHTML=`
    <div class="mmk"><div class="v">${{fv(s.slope_pct)}}<small>%/월</small></div><div class="l">월 기울기 (slope)</div></div>
    <div class="mmk"><div class="v">${{s.r2}}</div><div class="l">결정계수 R²</div></div>
    <div class="mmk"><div class="v">${{cv(s.total_return)}}</div><div class="l">3년 누적 수익</div></div>
    <div class="mmk"><div class="v">${{cv(s.return_1y)}}</div><div class="l">1년 수익</div></div>`;
  document.getElementById('mr').innerHTML=`
    <b>📐 추세선 분석</b><br>
    전반부 기울기 (early 2/3): <b>${{s.slope_early_pct > 0 ? '▲ +' : '▼ '}}${{s.slope_early_pct}}%/월</b><br>
    후반부 기울기 (late  1/3): <b>${{s.slope_late_pct  > 0 ? '▲ +' : '▼ '}}${{s.slope_late_pct}}%/월</b><br>
    전체 추세 방향: <b>${{s.slope_pct > 0 ? '▲ 상승' : '▼ 하락'}}</b> · 추세 명확도: <b>R² = ${{s.r2}}</b>
    ${{s.trend==='recovering' ? '<br>⚡ <b>전반 하락 → 후반 반등 전환 감지</b>' : ''}}`;
  if(mInst){{mInst.destroy();mInst=null;}}
  mInst=new Chart(document.getElementById('mc'),{{
    type:'line',
    data:{{labels:s.chart_labels, datasets:[
      {{label:s.ticker+' 주가 (정규화)',
        data:s.chart_data, borderColor:m.c, backgroundColor:m.f,
        borderWidth:2.5, pointRadius:2, fill:true, tension:0.3, order:2}},
      {{label:'선형회귀 추세선',
        data:s.regression, borderColor:'#64748b',
        borderWidth:2, borderDash:[5,4], pointRadius:0, fill:false, tension:0, order:1}}
    ]}},
    options:{{responsive:true, maintainAspectRatio:false,
      plugins:{{legend:{{position:'top',labels:{{font:{{size:11}},boxWidth:20}}}},
        tooltip:{{callbacks:{{label:c=>` ${{c.parsed.y.toFixed(1)}} (기준=100)`}}}}}},
      scales:{{
        x:{{ticks:{{maxTicksLimit:12,font:{{size:10}}}},grid:{{color:'#f1f5f9'}}}},
        y:{{ticks:{{font:{{size:10}},callback:v=>v.toFixed(0)}},grid:{{color:'#f1f5f9'}}}}
      }}}}
  }});
  document.getElementById('ov').classList.add('open');
}}

function closeOv(e){{if(e.target===document.getElementById('ov')) document.getElementById('ov').classList.remove('open');}}
render();
</script>
</body>
</html>"""

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ HTML 리포트 생성: {out_path}")


if __name__ == "__main__":
    build_report()
