from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "work" / "data" / "dashboard_data.json"
OUT_DIR = ROOT / "outputs"
OUT_HTML = OUT_DIR / "thailand_tourism_dashboard.html"
OUT_INDEX = OUT_DIR / "index.html"


def main() -> int:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    data_json = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    build_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    html = HTML_TEMPLATE.replace("__DATA_JSON__", data_json).replace("__BUILD_DATE__", build_date)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(html, encoding="utf-8")
    OUT_INDEX.write_text(html, encoding="utf-8")
    (OUT_DIR / ".nojekyll").write_text("", encoding="utf-8")
    for filename in [
        "tourism_monthly.csv",
        "tourism_quarterly.csv",
        "tourism_annual.csv",
        "tourism_country_monthly.csv",
        "validation_annual_worldbank.csv",
        "validation_country_monthly.csv",
    ]:
        shutil.copy2(ROOT / "work" / "data" / filename, OUT_DIR / filename)
    print(f"Wrote {OUT_HTML}")
    print(f"Wrote {OUT_INDEX}")
    return 0


HTML_TEMPLATE = r"""<!doctype html>
<html lang="th">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Thailand International Tourist Arrivals Dashboard</title>
  <style>
    :root {
      --bg: #f3f6fb;
      --panel: #ffffff;
      --ink: #182230;
      --muted: #667085;
      --line: #d7dee8;
      --soft: #edf2f7;
      --teal: #0e9384;
      --blue: #2563eb;
      --amber: #d97706;
      --rose: #e11d48;
      --shadow: 0 12px 32px rgba(16, 24, 40, 0.08);
      --radius: 8px;
    }

    * { box-sizing: border-box; }
    html, body {
      overflow-x: hidden;
    }

    body {
      margin: 0;
      font-family: "Segoe UI", Tahoma, Arial, sans-serif;
      color: var(--ink);
      background: var(--bg);
    }

    a { color: #175cd3; text-decoration: none; }
    a:hover { text-decoration: underline; }

    .shell {
      width: min(1440px, 100%);
      margin: 0 auto;
      padding: 24px;
    }

    .topbar {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 18px;
      align-items: start;
      margin-bottom: 16px;
    }

    h1 {
      margin: 0;
      font-size: clamp(26px, 3.4vw, 44px);
      line-height: 1.08;
      letter-spacing: 0;
      overflow-wrap: anywhere;
    }

    .subtitle {
      margin: 8px 0 0;
      max-width: 900px;
      color: var(--muted);
      font-size: 15px;
      line-height: 1.55;
      overflow-wrap: anywhere;
    }

    .source-pill {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      min-height: 36px;
      padding: 8px 12px;
      color: #073b35;
      background: #dff7f3;
      border: 1px solid #a6e7dd;
      border-radius: 999px;
      font-size: 13px;
      white-space: nowrap;
    }

    .cards {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin: 18px 0;
    }

    .card, .panel {
      background: var(--panel);
      border: 1px solid #e4e9f2;
      border-radius: var(--radius);
      box-shadow: var(--shadow);
    }

    .card {
      padding: 16px;
      min-height: 124px;
      display: grid;
      align-content: space-between;
      gap: 12px;
    }

    .card .label {
      color: var(--muted);
      font-size: 13px;
      line-height: 1.35;
    }

    .card .value {
      font-weight: 750;
      font-size: clamp(24px, 2.5vw, 36px);
      line-height: 1;
      letter-spacing: 0;
    }

    .card .note {
      color: var(--muted);
      font-size: 12px;
      line-height: 1.45;
    }

    .card .delta {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      width: fit-content;
      padding: 4px 8px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 650;
      background: #eef4ff;
      color: #1849a9;
    }

    .delta.positive { background: #dcfae6; color: #067647; }
    .delta.negative { background: #ffe4e8; color: #a11043; }
    .delta.neutral { background: #f2f4f7; color: #475467; }

    .toolbar {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 12px;
      align-items: center;
      margin: 18px 0;
      padding: 12px;
      background: rgba(255, 255, 255, 0.82);
      border: 1px solid #e4e9f2;
      border-radius: var(--radius);
      box-shadow: 0 10px 22px rgba(16, 24, 40, 0.06);
      position: sticky;
      top: 0;
      z-index: 10;
      backdrop-filter: blur(10px);
    }

    .controls {
      display: flex;
      flex-wrap: wrap;
      gap: 10px 12px;
      align-items: center;
    }

    .segmented, .quick-actions {
      display: inline-flex;
      gap: 4px;
      padding: 4px;
      background: var(--soft);
      border: 1px solid #dde5ef;
      border-radius: var(--radius);
    }

    .select-group {
      display: inline-flex;
      flex-wrap: wrap;
      gap: 6px;
      align-items: center;
    }

    .select-group select {
      min-height: 42px;
      max-width: min(320px, 100%);
      padding: 8px 34px 8px 10px;
      border: 1px solid #ccd6e3;
      border-radius: 6px;
      color: var(--ink);
      background: #fff;
      font: inherit;
      font-size: 13px;
    }

    .select-group select[hidden] {
      display: none;
    }

    button, .check {
      font: inherit;
      color: var(--ink);
    }

    button {
      border: 0;
      border-radius: 6px;
      padding: 8px 12px;
      background: transparent;
      cursor: pointer;
      min-height: 34px;
    }

    button.active {
      background: var(--panel);
      box-shadow: 0 1px 3px rgba(16, 24, 40, 0.12);
      color: #0b4a6f;
      font-weight: 700;
    }

    button:focus-visible, input:focus-visible, select:focus-visible {
      outline: 3px solid rgba(37, 99, 235, 0.28);
      outline-offset: 2px;
    }

    .check {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      color: var(--muted);
      font-size: 13px;
      white-space: nowrap;
    }

    .year-strip {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      align-items: center;
      margin: 10px 0 18px;
    }

    .chip {
      border: 1px solid #d0d8e4;
      background: #fff;
      color: #334155;
      border-radius: 999px;
      min-height: 30px;
      padding: 5px 10px;
      font-size: 12px;
      cursor: pointer;
    }

    .chip.active {
      color: #fff;
      border-color: var(--chip-color, var(--blue));
      background: var(--chip-color, var(--blue));
    }

    .grid {
      display: grid;
      grid-template-columns: minmax(0, 1.55fr) minmax(360px, 0.9fr);
      gap: 14px;
      align-items: start;
    }

    .panel {
      min-width: 0;
      overflow: hidden;
    }

    .panel-head {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: start;
      padding: 16px 18px 8px;
      border-bottom: 1px solid #eef2f7;
    }

    .panel h2 {
      margin: 0;
      font-size: 18px;
      letter-spacing: 0;
    }

    .panel .hint {
      margin-top: 4px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.45;
    }

    .chart {
      width: 100%;
      min-height: 430px;
      padding: 6px 8px 16px;
    }

    svg {
      display: block;
      width: 100%;
      height: auto;
    }

    .axis text, .legend text {
      fill: var(--muted);
      font-size: 12px;
    }

    .grid-line {
      stroke: #e8edf4;
      stroke-width: 1;
    }

    .axis-line {
      stroke: #aab4c3;
      stroke-width: 1.2;
    }

    .series-line {
      fill: none;
      stroke-width: 2.25;
      stroke-linecap: round;
      stroke-linejoin: round;
    }

    .point {
      stroke: #fff;
      stroke-width: 1.5;
      cursor: pointer;
    }

    .point.selected {
      stroke: #101828;
      stroke-width: 3;
    }

    .point-label {
      fill: #344054;
      font-size: 10px;
      paint-order: stroke;
      stroke: #fff;
      stroke-width: 3px;
      stroke-linejoin: round;
      pointer-events: none;
    }

    .legend {
      display: flex;
      flex-wrap: wrap;
      gap: 8px 12px;
      padding: 0 18px 14px;
      color: var(--muted);
      font-size: 12px;
    }

    .legend-item {
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }

    .legend-swatch {
      width: 18px;
      height: 3px;
      border-radius: 999px;
      background: var(--swatch);
    }

    .stack {
      display: grid;
      gap: 14px;
    }

    .table-wrap {
      overflow: auto;
      max-height: 560px;
      border-top: 1px solid #eef2f7;
    }

    .selected-detail {
      padding: 16px 18px 18px;
      border-top: 1px solid #eef2f7;
    }

    .selected-empty {
      color: var(--muted);
      font-size: 13px;
      line-height: 1.55;
    }

    .selected-main {
      display: grid;
      gap: 10px;
    }

    .selected-kicker {
      color: var(--muted);
      font-size: 12px;
    }

    .selected-value {
      font-size: 32px;
      line-height: 1;
      font-weight: 750;
      letter-spacing: 0;
    }

    .selected-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px;
    }

    .selected-stat {
      padding: 10px;
      background: #f8fafc;
      border: 1px solid #e4e9f2;
      border-radius: var(--radius);
    }

    .selected-stat span {
      display: block;
      color: var(--muted);
      font-size: 11px;
    }

    .selected-stat strong {
      display: block;
      margin-top: 3px;
      font-size: 14px;
    }

    .selected-actions {
      display: flex;
      justify-content: flex-end;
      margin-top: 10px;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 12px;
    }

    th, td {
      padding: 9px 10px;
      text-align: right;
      border-bottom: 1px solid #eef2f7;
      white-space: nowrap;
    }

    th {
      position: sticky;
      top: 0;
      z-index: 2;
      background: #f8fafc;
      color: #475467;
      font-weight: 700;
    }

    td:first-child, th:first-child,
    td:nth-child(2), th:nth-child(2) {
      text-align: left;
    }

    .method {
      margin-top: 14px;
      padding: 18px;
      display: grid;
      grid-template-columns: minmax(0, 1.2fr) minmax(320px, 0.8fr);
      gap: 16px;
    }

    .method h2, .method h3 {
      margin: 0 0 8px;
      letter-spacing: 0;
    }

    .method p, .method li {
      color: var(--muted);
      font-size: 13px;
      line-height: 1.55;
    }

    .method ul {
      margin: 8px 0 0;
      padding-left: 18px;
    }

    .validation-list {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px;
    }

    .validation-badge {
      border: 1px solid #e4e9f2;
      border-radius: var(--radius);
      padding: 10px;
      background: #fbfcfe;
    }

    .validation-badge strong {
      display: block;
      font-size: 13px;
    }

    .validation-badge span {
      color: var(--muted);
      font-size: 12px;
    }

    .tooltip {
      position: fixed;
      z-index: 50;
      max-width: min(360px, calc(100vw - 24px));
      padding: 10px 12px;
      color: #fff;
      background: rgba(16, 24, 40, 0.96);
      border-radius: 8px;
      font-size: 12px;
      line-height: 1.5;
      pointer-events: none;
      opacity: 0;
      transform: translate(-50%, -110%);
      transition: opacity 0.08s ease;
      box-shadow: 0 12px 28px rgba(16, 24, 40, 0.28);
    }

    .tooltip.visible { opacity: 1; }
    .tooltip b { color: #fff; }
    .tooltip .muted { color: #cbd5e1; }

    @media (max-width: 1120px) {
      .cards { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .grid, .method { grid-template-columns: 1fr; }
    }

    @media (max-width: 720px) {
      .shell { width: 100%; max-width: 100vw; padding: 16px; overflow: hidden; }
      h1 { word-break: break-all; }
      h1 span { display: block; }
      .subtitle { word-break: break-word; }
      .subtitle span { display: block; }
      .topbar, .toolbar { grid-template-columns: 1fr; }
      .cards { grid-template-columns: 1fr; }
      .controls { align-items: stretch; }
      .segmented, .quick-actions { width: 100%; overflow-x: auto; }
      .select-group, .select-group select { width: 100%; }
      button { flex: 1; min-width: max-content; }
      .chart { min-height: 360px; }
      .validation-list { grid-template-columns: 1fr; }
      .source-pill { white-space: normal; }
    }
  </style>
</head>
<body>
  <script id="dashboard-data" type="application/json">__DATA_JSON__</script>
  <div class="shell">
    <header class="topbar">
      <div>
        <h1><span>Dashboard จำนวนนักท่องเที่ยว</span> <span>ต่างชาติของประเทศไทย</span></h1>
        <p class="subtitle"><span>ข้อมูลรายเดือน/ไตรมาส/ปี ตั้งแต่ 2555 ถึงล่าสุด</span> <span>จากแหล่งภาครัฐ พร้อมการตรวจซ้ำหลายแหล่ง</span></p>
      </div>
      <div class="source-pill" id="freshnessPill">กำลังโหลดข้อมูล</div>
    </header>

    <section class="cards" id="kpiCards"></section>

    <section class="toolbar" aria-label="Dashboard controls">
      <div class="controls">
        <div class="segmented" id="grainButtons">
          <button type="button" data-grain="monthly" class="active">รายเดือน</button>
          <button type="button" data-grain="quarterly">รายไตรมาส</button>
          <button type="button" data-grain="annual">รายปี</button>
        </div>
        <div class="select-group" aria-label="ตัวกรองพื้นที่ต้นทาง">
          <select id="segmentMode" aria-label="เลือกมุมมองรวม ทวีป หรือประเทศ">
            <option value="total">รวมทั้งหมด</option>
            <option value="continent">รายทวีป</option>
            <option value="country">รายประเทศ</option>
          </select>
          <select id="continentSelect" aria-label="เลือกทวีป"></select>
          <select id="countrySelect" aria-label="เลือกประเทศ"></select>
        </div>
        <div class="segmented" id="growthButtons"></div>
        <label class="check"><input id="labelToggle" type="checkbox" checked /> แสดงตัวเลขบนกราฟ</label>
      </div>
      <div class="quick-actions">
        <button type="button" id="lastSix">ล่าสุด 3 ปี</button>
        <button type="button" id="allYears">ทุกปี</button>
        <button type="button" id="clearYears">ล้าง</button>
      </div>
    </section>

    <div class="year-strip" id="yearStrip"></div>

    <main class="grid">
      <section class="stack">
        <article class="panel">
          <div class="panel-head">
            <div>
              <h2 id="arrivalsTitle">จำนวนผู้เดินทางเข้าไทย</h2>
              <div class="hint" id="arrivalsHint"></div>
            </div>
          </div>
          <div class="chart" id="arrivalsChart"></div>
          <div class="legend" id="arrivalsLegend"></div>
        </article>

        <article class="panel">
          <div class="panel-head">
            <div>
              <h2 id="growthTitle">การเติบโต</h2>
              <div class="hint" id="growthHint"></div>
            </div>
          </div>
          <div class="chart" id="growthChart"></div>
          <div class="legend" id="growthLegend"></div>
        </article>
      </section>

      <aside class="stack">
        <article class="panel">
          <div class="panel-head">
            <div>
              <h2>ข้อมูลจุดที่เลือก</h2>
              <div class="hint">คลิกจุดบนกราฟเพื่อแสดงข้อมูลค้างไว้ตรงนี้</div>
            </div>
          </div>
          <div class="selected-detail" id="selectedPointPanel"></div>
        </article>

        <article class="panel">
          <div class="panel-head">
            <div>
              <h2>ตารางข้อมูล</h2>
              <div class="hint" id="tableHint"></div>
            </div>
          </div>
          <div class="table-wrap">
            <table id="detailTable"></table>
          </div>
        </article>

        <article class="panel">
          <div class="panel-head">
            <div>
              <h2>ตรวจสอบตัวเลข</h2>
              <div class="hint" id="validationHint">สรุปผล reconciliation ของยอดรวมรายปี</div>
            </div>
          </div>
          <div class="table-wrap" style="max-height: 360px;">
            <table id="validationTable"></table>
          </div>
        </article>
      </aside>
    </main>

    <section class="panel method">
      <div>
        <h2>แหล่งข้อมูลและวิธีคำนวณ</h2>
        <p>ตัวเลขหลักคือจำนวนนักท่องเที่ยวต่างชาติที่เดินทางเข้าประเทศไทย หน่วยเป็นคน รายเดือนตั้งแต่ปี 2556 ถึง พ.ค. 2569 และรายปีเริ่มปี 2555 โดยปี 2555 เป็น annual-only เพราะไม่พบไฟล์ภาครัฐที่ให้ monthly split ที่เชื่อถือได้จากชุดที่ตรวจสอบในรอบนี้ ส่วนตัวกรองรายประเทศ/รายทวีปใช้ข้อมูลที่ reconcile กับยอดรวมรายเดือนได้ตั้งแต่ปี 2558 ถึงข้อมูลล่าสุด</p>
        <ul id="sourceList"></ul>
      </div>
      <div>
        <h3>การเติบโตที่ใช้ใน dashboard</h3>
        <div class="validation-list">
          <div class="validation-badge"><strong>MoM</strong><span>เดือนนี้เทียบเดือนก่อนหน้า ใช้ในรายเดือน</span></div>
          <div class="validation-badge"><strong>QoQ</strong><span>ไตรมาสนี้เทียบไตรมาสก่อนหน้า ใช้ในรายไตรมาส</span></div>
          <div class="validation-badge"><strong>YoY</strong><span>เทียบช่วงเดียวกันของปีก่อน ใช้รายเดือน รายไตรมาส และรายปี</span></div>
          <div class="validation-badge"><strong>YTD</strong><span>ปี 2569 เป็นยอด ม.ค.-พ.ค. ยังไม่ใช่ทั้งปี</span></div>
        </div>
      </div>
    </section>
  </div>

  <div class="tooltip" id="tooltip"></div>

  <script>
    const DATA = JSON.parse(document.getElementById("dashboard-data").textContent);
    const MONTHS_TH = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."];
    const COLORS = [
      "#2563eb", "#0e9384", "#d97706", "#e11d48", "#7c3aed", "#0891b2",
      "#65a30d", "#ea580c", "#be123c", "#475569", "#16a34a", "#9333ea",
      "#0284c7", "#ca8a04", "#db2777", "#0f766e"
    ];
    const COUNTRY_MONTHLY = DATA.country_monthly || [];
    const COUNTRY_OPTIONS = DATA.country_options || [...new Set(COUNTRY_MONTHLY.map(row => row.country))].sort();
    const CONTINENT_OPTIONS = DATA.continent_options || [...new Set(COUNTRY_MONTHLY.map(row => row.continent))].sort();
    const DEFAULT_CONTINENT = CONTINENT_OPTIONS.includes("Asia and the Pacific") ? "Asia and the Pacific" : (CONTINENT_OPTIONS[0] || "");
    const DEFAULT_COUNTRY = COUNTRY_OPTIONS.includes("China") ? "China" : (COUNTRY_OPTIONS[0] || "");
    const segmentCache = { key: "", model: null };

    const state = {
      grain: "monthly",
      growth: "both",
      segmentType: "total",
      selectedContinent: DEFAULT_CONTINENT,
      selectedCountry: DEFAULT_COUNTRY,
      selectedYears: new Set(),
      labels: true,
      selectedPoint: null,
      pointLookup: new Map()
    };

    function be(year) { return Number(year) + 543; }
    function number(value) { return Number(value || 0).toLocaleString("en-US"); }
    function shortNumber(value) {
      const abs = Math.abs(Number(value || 0));
      if (abs >= 1000000) return (value / 1000000).toFixed(abs >= 10000000 ? 1 : 2).replace(/\.0$/, "") + "m";
      if (abs >= 1000) return (value / 1000).toFixed(0) + "k";
      return String(value ?? "");
    }
    function pct(value) {
      if (value === null || value === undefined || Number.isNaN(Number(value))) return "n/a";
      return `${Number(value).toFixed(1)}%`;
    }
    function pctChange(value, base) {
      if (value === null || value === undefined || base === null || base === undefined || Number(base) === 0) return null;
      return (Number(value) / Number(base) - 1) * 100;
    }
    function deltaClass(value) {
      if (value === null || value === undefined || Number.isNaN(Number(value))) return "neutral";
      return Number(value) > 0 ? "positive" : Number(value) < 0 ? "negative" : "neutral";
    }
    function dateText(iso) {
      const d = new Date(`${iso}T00:00:00`);
      return `${MONTHS_TH[d.getMonth()]} ${be(d.getFullYear())}`;
    }
    function htmlEscape(value) {
      return String(value ?? "").replace(/[&<>"']/g, ch => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch]));
    }
    function attrEscape(value) { return htmlEscape(value).replace(/`/g, "&#96;"); }
    function uniqueYears(rows) { return [...new Set(rows.map(row => row.year))].sort((a, b) => a - b); }
    function yearColor(year) {
      const years = uniqueYears(DATA.monthly.concat(DATA.annual));
      const idx = years.indexOf(year);
      return COLORS[(idx < 0 ? 0 : idx) % COLORS.length];
    }

    function selectedSegmentLabel() {
      if (state.segmentType === "continent") return `ทวีป: ${state.selectedContinent || "ทั้งหมด"}`;
      if (state.segmentType === "country") return `ประเทศ: ${state.selectedCountry || "ทั้งหมด"}`;
      return "รวมทุกประเทศ";
    }

    function ensureSegmentDefaults() {
      if (!state.selectedContinent && DEFAULT_CONTINENT) state.selectedContinent = DEFAULT_CONTINENT;
      if (!state.selectedCountry && DEFAULT_COUNTRY) state.selectedCountry = DEFAULT_COUNTRY;
      if (state.segmentType === "continent" && !CONTINENT_OPTIONS.includes(state.selectedContinent)) {
        state.selectedContinent = DEFAULT_CONTINENT;
      }
      if (state.segmentType === "country" && !COUNTRY_OPTIONS.includes(state.selectedCountry)) {
        state.selectedCountry = DEFAULT_COUNTRY;
      }
    }

    function resetSelection() {
      state.selectedPoint = null;
      state.pointLookup = new Map();
      segmentCache.key = "";
      segmentCache.model = null;
    }

    function currentSegmentKey() {
      return `${state.segmentType}|${state.selectedContinent}|${state.selectedCountry}`;
    }

    function matchingCountryRows() {
      if (state.segmentType === "country") {
        return COUNTRY_MONTHLY.filter(row => row.country === state.selectedCountry);
      }
      if (state.segmentType === "continent") {
        return COUNTRY_MONTHLY.filter(row => row.continent === state.selectedContinent);
      }
      return [];
    }

    function aggregateMonthlyRows(rows) {
      const grouped = new Map();
      rows.forEach(row => {
        const year = Number(row.year);
        const month = Number(row.month);
        const key = `${year}-${month}`;
        if (!grouped.has(key)) {
          grouped.set(key, {
            year,
            month,
            date: `${year}-${String(month).padStart(2, "0")}-01`,
            arrivals: 0,
            source_published: row.source_published,
            source_file_url: row.source_file_url,
            segment_type: state.segmentType,
            segment_label: selectedSegmentLabel()
          });
        }
        const target = grouped.get(key);
        target.arrivals += Number(row.arrivals || 0);
        if (!target.source_file_url && row.source_file_url) target.source_file_url = row.source_file_url;
        if (!target.source_published && row.source_published) target.source_published = row.source_published;
      });
      const sorted = [...grouped.values()].sort((a, b) => a.year - b.year || a.month - b.month);
      const lookup = new Map(sorted.map(row => [`${row.year}-${row.month}`, row.arrivals]));
      let previous = null;
      return sorted.map(row => {
        const out = {
          ...row,
          mom_pct: pctChange(row.arrivals, previous),
          yoy_pct: pctChange(row.arrivals, lookup.get(`${row.year - 1}-${row.month}`)),
          month_name: MONTHS_TH[row.month - 1]
        };
        previous = row.arrivals;
        return out;
      });
    }

    function deriveQuarterlyRows(monthlyRows) {
      const byYear = new Map();
      monthlyRows.forEach(row => {
        if (!byYear.has(row.year)) byYear.set(row.year, new Map());
        byYear.get(row.year).set(row.month, row);
      });
      const rows = [];
      byYear.forEach((monthMap, year) => {
        for (let quarter = 1; quarter <= 4; quarter += 1) {
          const months = [(quarter - 1) * 3 + 1, (quarter - 1) * 3 + 2, (quarter - 1) * 3 + 3];
          if (!months.every(month => monthMap.has(month))) continue;
          const monthRows = months.map(month => monthMap.get(month));
          rows.push({
            year,
            quarter,
            period: `Q${quarter}`,
            date: `${year}-${String(months[0]).padStart(2, "0")}-01`,
            arrivals: monthRows.reduce((sum, row) => sum + Number(row.arrivals || 0), 0),
            source_published: monthRows[monthRows.length - 1].source_published,
            source_file_url: monthRows[monthRows.length - 1].source_file_url,
            segment_type: state.segmentType,
            segment_label: selectedSegmentLabel()
          });
        }
      });
      rows.sort((a, b) => a.year - b.year || a.quarter - b.quarter);
      const lookup = new Map(rows.map(row => [`${row.year}-${row.quarter}`, row.arrivals]));
      let previous = null;
      rows.forEach(row => {
        row.qoq_pct = pctChange(row.arrivals, previous);
        row.yoy_pct = pctChange(row.arrivals, lookup.get(`${row.year - 1}-${row.quarter}`));
        previous = row.arrivals;
      });
      return rows;
    }

    function deriveAnnualRows(monthlyRows) {
      const byYear = new Map();
      monthlyRows.forEach(row => {
        if (!byYear.has(row.year)) byYear.set(row.year, []);
        byYear.get(row.year).push(row);
      });
      const rows = [...byYear.entries()].map(([year, yearRows]) => {
        const months = [...new Set(yearRows.map(row => row.month))].sort((a, b) => a - b);
        const latestSource = yearRows.slice().sort((a, b) => a.month - b.month).at(-1) || {};
        return {
          year,
          date: `${year}-01-01`,
          arrivals: yearRows.reduce((sum, row) => sum + Number(row.arrivals || 0), 0),
          months: months.length,
          is_full_year: months.length === 12,
          annual_only: false,
          source_published: latestSource.source_published,
          source_file_url: latestSource.source_file_url,
          segment_type: state.segmentType,
          segment_label: selectedSegmentLabel()
        };
      }).sort((a, b) => a.year - b.year);
      const monthlyLookup = new Map(monthlyRows.map(row => [`${row.year}-${row.month}`, row.arrivals]));
      const annualLookup = new Map(rows.map(row => [row.year, row.arrivals]));
      rows.forEach(row => {
        if (row.months === 12) {
          row.yoy_basis = "full_year";
          row.yoy_pct = pctChange(row.arrivals, annualLookup.get(row.year - 1));
        } else {
          const baseMonths = Array.from({ length: row.months }, (_, idx) => idx + 1).map(month => monthlyLookup.get(`${row.year - 1}-${month}`));
          const base = baseMonths.every(value => value !== undefined) ? baseMonths.reduce((sum, value) => sum + Number(value), 0) : null;
          row.yoy_basis = `YTD same ${row.months} months`;
          row.yoy_pct = pctChange(row.arrivals, base);
        }
      });
      return rows;
    }

    function currentModel() {
      ensureSegmentDefaults();
      if (state.segmentType === "total") {
        return { monthly: DATA.monthly, quarterly: DATA.quarterly, annual: DATA.annual };
      }
      const key = currentSegmentKey();
      if (segmentCache.key === key && segmentCache.model) return segmentCache.model;
      const monthly = aggregateMonthlyRows(matchingCountryRows());
      const model = {
        monthly,
        quarterly: deriveQuarterlyRows(monthly),
        annual: deriveAnnualRows(monthly)
      };
      segmentCache.key = key;
      segmentCache.model = model;
      return model;
    }

    function rowsForGrain(grain = state.grain) {
      const model = currentModel();
      if (grain === "quarterly") return model.quarterly;
      if (grain === "annual") return model.annual;
      return model.monthly;
    }
    function defaultYears() {
      const years = uniqueYears(rowsForGrain());
      return years.slice(Math.max(0, years.length - 3));
    }
    function ensureYears() {
      const available = new Set(uniqueYears(rowsForGrain()));
      const filtered = [...state.selectedYears].filter(year => available.has(year));
      if (!filtered.length) filtered.push(...defaultYears());
      state.selectedYears = new Set(filtered);
    }

    function setupControls() {
      document.querySelectorAll("#grainButtons button").forEach(button => {
        button.addEventListener("click", () => {
          state.grain = button.dataset.grain;
          state.growth = state.grain === "annual" ? "yoy" : "both";
          resetSelection();
          ensureYears();
          render();
        });
      });
      document.getElementById("segmentMode").addEventListener("change", event => {
        state.segmentType = event.target.value;
        ensureSegmentDefaults();
        resetSelection();
        state.selectedYears = new Set(defaultYears());
        render();
      });
      document.getElementById("continentSelect").addEventListener("change", event => {
        state.selectedContinent = event.target.value;
        resetSelection();
        state.selectedYears = new Set(defaultYears());
        render();
      });
      document.getElementById("countrySelect").addEventListener("change", event => {
        state.selectedCountry = event.target.value;
        resetSelection();
        state.selectedYears = new Set(defaultYears());
        render();
      });
      document.getElementById("labelToggle").addEventListener("change", event => {
        state.labels = event.target.checked;
        state.selectedPoint = null;
        render();
      });
      document.getElementById("lastSix").addEventListener("click", () => {
        state.selectedYears = new Set(defaultYears());
        resetSelection();
        render();
      });
      document.getElementById("allYears").addEventListener("click", () => {
        state.selectedYears = new Set(uniqueYears(rowsForGrain()));
        resetSelection();
        render();
      });
      document.getElementById("clearYears").addEventListener("click", () => {
        state.selectedYears = new Set();
        resetSelection();
        render();
      });
    }

    function renderSegmentControls() {
      const mode = document.getElementById("segmentMode");
      const continentSelect = document.getElementById("continentSelect");
      const countrySelect = document.getElementById("countrySelect");
      mode.value = state.segmentType;
      continentSelect.hidden = state.segmentType !== "continent";
      countrySelect.hidden = state.segmentType !== "country";
      continentSelect.innerHTML = CONTINENT_OPTIONS.map(item => `<option value="${attrEscape(item)}">${htmlEscape(item)}</option>`).join("");
      countrySelect.innerHTML = COUNTRY_OPTIONS.map(item => `<option value="${attrEscape(item)}">${htmlEscape(item)}</option>`).join("");
      continentSelect.value = state.selectedContinent;
      countrySelect.value = state.selectedCountry;
    }

    function renderGrowthButtons() {
      const host = document.getElementById("growthButtons");
      const options = state.grain === "monthly"
        ? [["both", "MoM + YoY"], ["mom", "MoM"], ["yoy", "YoY"]]
        : state.grain === "quarterly"
          ? [["both", "QoQ + YoY"], ["qoq", "QoQ"], ["yoy", "YoY"]]
          : [["yoy", "YoY"]];
      host.innerHTML = options.map(([key, label]) => `<button type="button" data-growth="${key}" class="${state.growth === key ? "active" : ""}">${label}</button>`).join("");
      host.querySelectorAll("button").forEach(button => {
        button.addEventListener("click", () => {
          state.growth = button.dataset.growth;
          state.selectedPoint = null;
          render();
        });
      });
    }

    function renderYearStrip() {
      const years = uniqueYears(rowsForGrain());
      const host = document.getElementById("yearStrip");
      host.innerHTML = years.map(year => {
        const active = state.selectedYears.has(year);
        return `<button type="button" class="chip ${active ? "active" : ""}" style="--chip-color:${yearColor(year)}" data-year="${year}" title="${year} / ${be(year)}">${be(year)}</button>`;
      }).join("");
      host.querySelectorAll("button").forEach(button => {
        button.addEventListener("click", () => {
          const year = Number(button.dataset.year);
          if (state.selectedYears.has(year)) state.selectedYears.delete(year);
          else state.selectedYears.add(year);
          state.selectedPoint = null;
          render();
        });
      });
    }

    function selectedRows() {
      ensureYears();
      return rowsForGrain().filter(row => state.selectedYears.has(row.year));
    }

    function renderKpis() {
      const model = currentModel();
      const latestMonth = model.monthly[model.monthly.length - 1];
      if (!latestMonth) {
        document.getElementById("kpiCards").innerHTML = `
          <article class="card">
            <div class="label">${htmlEscape(selectedSegmentLabel())}</div>
            <div>
              <div class="value">n/a</div>
              <div class="note">ไม่มีข้อมูลสำหรับตัวกรองนี้</div>
            </div>
            <div class="delta neutral">No data</div>
          </article>
        `;
        document.getElementById("freshnessPill").textContent = `ไม่มีข้อมูล | build __BUILD_DATE__`;
        return;
      }
      const currentYtdYear = latestMonth.year;
      const ytdMonths = latestMonth.month;
      const currentYtd = model.monthly.filter(row => row.year === currentYtdYear && row.month <= ytdMonths).reduce((sum, row) => sum + row.arrivals, 0);
      const previousYtd = model.monthly.filter(row => row.year === currentYtdYear - 1 && row.month <= ytdMonths).reduce((sum, row) => sum + row.arrivals, 0);
      const ytdYoY = previousYtd ? ((currentYtd - previousYtd) / previousYtd) * 100 : null;
      const fullYears = model.annual.filter(row => row.is_full_year && row.months === 12);
      const latestFull = fullYears[fullYears.length - 1];
      const peak = fullYears.length ? fullYears.reduce((best, row) => row.arrivals > best.arrivals ? row : best, fullYears[0]) : null;
      const cards = [
        {
          label: `เดือนล่าสุด ${dateText(latestMonth.date)} | ${selectedSegmentLabel()}`,
          value: shortNumber(latestMonth.arrivals),
          note: `${number(latestMonth.arrivals)} คน`,
          delta: `YoY ${pct(latestMonth.yoy_pct)}`,
          deltaValue: latestMonth.yoy_pct
        },
        {
          label: `YTD ${MONTHS_TH[0]}-${MONTHS_TH[ytdMonths - 1]} ${be(currentYtdYear)}`,
          value: shortNumber(currentYtd),
          note: `${number(currentYtd)} คน เทียบ ${number(previousYtd)} คนในปีก่อน`,
          delta: `YoY ${pct(ytdYoY)}`,
          deltaValue: ytdYoY
        },
        {
          label: latestFull ? `ปีล่าสุดเต็มปี ${be(latestFull.year)}` : "ปีล่าสุดเต็มปี",
          value: latestFull ? shortNumber(latestFull.arrivals) : "n/a",
          note: latestFull ? `${number(latestFull.arrivals)} คน` : "ยังไม่มีปีเต็มในตัวกรองนี้",
          delta: latestFull ? `YoY ${pct(latestFull.yoy_pct)}` : "n/a",
          deltaValue: latestFull ? latestFull.yoy_pct : null
        },
        {
          label: peak ? `ปีสูงสุดในชุดข้อมูล ${be(peak.year)}` : "ปีสูงสุดในชุดข้อมูล",
          value: peak ? shortNumber(peak.arrivals) : "n/a",
          note: peak ? `${number(peak.arrivals)} คน` : "ยังไม่มีปีเต็มในตัวกรองนี้",
          delta: peak ? "Peak full-year" : "n/a",
          deltaValue: null
        }
      ];
      document.getElementById("kpiCards").innerHTML = cards.map(card => `
        <article class="card">
          <div class="label">${card.label}</div>
          <div>
            <div class="value">${card.value}</div>
            <div class="note">${card.note}</div>
          </div>
          <div class="delta ${deltaClass(card.deltaValue)}">${card.delta}</div>
        </article>
      `).join("");
      document.getElementById("freshnessPill").textContent = `ข้อมูลล่าสุด: ${dateText(latestMonth.date)} | ${selectedSegmentLabel()} | build __BUILD_DATE__`;
    }

    function xDomainForGrain() {
      if (state.grain === "monthly") return Array.from({ length: 12 }, (_, idx) => idx + 1);
      if (state.grain === "quarterly") return [1, 2, 3, 4];
      return uniqueYears(selectedRows());
    }

    function xLabel(value) {
      if (state.grain === "monthly") return MONTHS_TH[value - 1];
      if (state.grain === "quarterly") return `Q${value}`;
      return String(be(value));
    }

    function buildArrivalSeries(rows) {
      if (state.grain === "annual") {
        return [{
          key: "รายปี",
          metricLabel: "จำนวน",
          color: "#2563eb",
          dash: "",
          values: rows.sort((a, b) => a.year - b.year).map(row => ({
            x: row.year,
            y: row.arrivals,
            label: shortNumber(row.arrivals),
            row,
            tip: annualTip(row, "จำนวน")
          }))
        }];
      }
      const group = new Map();
      rows.forEach(row => {
        if (!group.has(row.year)) group.set(row.year, []);
        group.get(row.year).push({
          x: state.grain === "monthly" ? row.month : row.quarter,
          y: row.arrivals,
          label: shortNumber(row.arrivals),
          row,
          tip: periodTip(row, "จำนวน", row.arrivals)
        });
      });
      return [...group.entries()].map(([year, values]) => ({
        key: String(be(year)),
        metricLabel: "จำนวน",
        color: yearColor(year),
        dash: "",
        values: values.sort((a, b) => a.x - b.x)
      }));
    }

    function growthFields() {
      if (state.grain === "monthly") {
        if (state.growth === "mom") return [["mom_pct", "MoM", ""]];
        if (state.growth === "yoy") return [["yoy_pct", "YoY", "6 4"]];
        return [["mom_pct", "MoM", ""], ["yoy_pct", "YoY", "6 4"]];
      }
      if (state.grain === "quarterly") {
        if (state.growth === "qoq") return [["qoq_pct", "QoQ", ""]];
        if (state.growth === "yoy") return [["yoy_pct", "YoY", "6 4"]];
        return [["qoq_pct", "QoQ", ""], ["yoy_pct", "YoY", "6 4"]];
      }
      return [["yoy_pct", "YoY", ""]];
    }

    function buildGrowthSeries(rows) {
      if (state.grain === "annual") {
        return [{
          key: "YoY",
          metricLabel: "YoY",
          color: "#0e9384",
          dash: "",
          values: rows.sort((a, b) => a.year - b.year)
            .filter(row => row.yoy_pct !== null && row.yoy_pct !== undefined)
            .map(row => ({
              x: row.year,
              y: row.yoy_pct,
              label: pct(row.yoy_pct),
              row,
              tip: annualTip(row, "YoY", row.yoy_pct)
            }))
        }];
      }
      const fields = growthFields();
      const out = [];
      const years = uniqueYears(rows);
      years.forEach(year => {
        fields.forEach(([field, label, dash]) => {
          const values = rows
            .filter(row => row.year === year && row[field] !== null && row[field] !== undefined)
            .sort((a, b) => (state.grain === "monthly" ? a.month - b.month : a.quarter - b.quarter))
            .map(row => ({
              x: state.grain === "monthly" ? row.month : row.quarter,
              y: row[field],
              label: pct(row[field]),
              row,
              tip: periodTip(row, label, row[field])
            }));
          out.push({ key: `${be(year)} ${label}`, color: yearColor(year), dash, values });
          out[out.length - 1].metricLabel = label;
        });
      });
      return out;
    }

    function periodName(row) {
      if (state.grain === "monthly") return `${MONTHS_TH[row.month - 1]} ${be(row.year)}`;
      if (state.grain === "quarterly") return `Q${row.quarter} ${be(row.year)}`;
      return String(be(row.year));
    }

    function periodTip(row, label, value) {
      const growth = state.grain === "monthly"
        ? `MoM ${pct(row.mom_pct)} | YoY ${pct(row.yoy_pct)}`
        : `QoQ ${pct(row.qoq_pct)} | YoY ${pct(row.yoy_pct)}`;
      const main = label === "จำนวน" ? `${number(value)} คน` : pct(value);
      return `<b>${periodName(row)}</b><br>${htmlEscape(row.segment_label || selectedSegmentLabel())}<br>${label}: ${main}<br><span class="muted">จำนวน: ${number(row.arrivals)} คน<br>${growth}</span>`;
    }

    function annualTip(row, label, value = row.arrivals) {
      const suffix = row.is_full_year ? "เต็มปี" : `${row.months} เดือน`;
      const yoyBasis = row.yoy_basis === "full_year" ? "full-year" : (row.yoy_basis || "");
      const main = label === "จำนวน" ? `${number(value)} คน` : pct(value);
      return `<b>ปี ${be(row.year)} (${row.year})</b><br>${htmlEscape(row.segment_label || selectedSegmentLabel())}<br>${label}: ${main}<br><span class="muted">สถานะ: ${suffix}<br>YoY: ${pct(row.yoy_pct)} ${yoyBasis ? "(" + yoyBasis + ")" : ""}</span>`;
    }

    function renderLineChart(targetId, legendId, series, options) {
      const target = document.getElementById(targetId);
      const legend = document.getElementById(legendId);
      const xDomain = xDomainForGrain();
      const values = series.flatMap(item => item.values).filter(point => point.y !== null && point.y !== undefined && Number.isFinite(Number(point.y)));
      if (!values.length || !xDomain.length) {
        target.innerHTML = `<div class="hint" style="padding:24px;">ไม่มีข้อมูลสำหรับตัวกรองนี้</div>`;
        legend.innerHTML = "";
        return;
      }

      const W = 1000;
      const H = 420;
      const M = { top: 24, right: 30, bottom: 56, left: 72 };
      const plotW = W - M.left - M.right;
      const plotH = H - M.top - M.bottom;
      const minRaw = Math.min(...values.map(point => point.y));
      const maxRaw = Math.max(...values.map(point => point.y));
      let minY = options.zeroBase ? 0 : Math.min(0, minRaw);
      let maxY = maxRaw;
      if (minY === maxY) { minY -= 1; maxY += 1; }
      const pad = (maxY - minY) * 0.08;
      if (!options.zeroBase) minY -= pad;
      maxY += pad;

      const xPos = value => {
        const idx = xDomain.indexOf(value);
        if (xDomain.length === 1) return M.left + plotW / 2;
        return M.left + (idx / (xDomain.length - 1)) * plotW;
      };
      const yPos = value => M.top + ((maxY - value) / (maxY - minY)) * plotH;
      const yTicks = Array.from({ length: 5 }, (_, idx) => minY + ((maxY - minY) / 4) * idx);
      const maxSelectedLabels = state.selectedYears.size <= 6;
      const labelAll = state.labels && maxSelectedLabels;
      const labelEndpoints = state.labels && !maxSelectedLabels;
      let pointSerial = 0;

      let svg = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${attrEscape(options.title)}">`;
      yTicks.forEach(tick => {
        const y = yPos(tick);
        svg += `<line class="grid-line" x1="${M.left}" x2="${W - M.right}" y1="${y}" y2="${y}"></line>`;
        svg += `<text x="${M.left - 10}" y="${y + 4}" text-anchor="end" class="axis">${options.yFormatter(tick)}</text>`;
      });
      svg += `<line class="axis-line" x1="${M.left}" x2="${W - M.right}" y1="${H - M.bottom}" y2="${H - M.bottom}"></line>`;
      svg += `<line class="axis-line" x1="${M.left}" x2="${M.left}" y1="${M.top}" y2="${H - M.bottom}"></line>`;
      xDomain.forEach(value => {
        const x = xPos(value);
        svg += `<text x="${x}" y="${H - 24}" text-anchor="middle" class="axis">${xLabel(value)}</text>`;
      });

      series.forEach(item => {
        const points = item.values.filter(point => xDomain.includes(point.x) && point.y !== null && point.y !== undefined);
        if (!points.length) return;
        const path = points.map((point, idx) => `${idx ? "L" : "M"}${xPos(point.x).toFixed(1)},${yPos(point.y).toFixed(1)}`).join(" ");
        svg += `<path class="series-line" d="${path}" stroke="${item.color}" stroke-dasharray="${item.dash}"></path>`;
        points.forEach((point, idx) => {
          const x = xPos(point.x);
          const y = yPos(point.y);
          const pointId = `${targetId}-${pointSerial++}`;
          const metricLabel = point.metricLabel || item.metricLabel || options.metricLabel || item.key;
          const metricDisplay = point.metricDisplay || (options.zeroBase ? `${number(point.y)} คน` : pct(point.y));
          state.pointLookup.set(pointId, {
            id: pointId,
            chartTitle: options.title,
            seriesKey: item.key,
            color: item.color,
            period: periodName(point.row),
            xLabel: xLabel(point.x),
            metricLabel,
            metricDisplay,
            metricValue: point.y,
            row: point.row
          });
          const selectedClass = state.selectedPoint && state.selectedPoint.id === pointId ? " selected" : "";
          svg += `<circle class="point${selectedClass}" cx="${x}" cy="${y}" r="4.8" fill="${item.color}" data-tip="${attrEscape(point.tip)}" data-point-id="${attrEscape(pointId)}" tabindex="0" role="button" aria-label="${attrEscape(`${metricLabel} ${periodName(point.row)} ${metricDisplay}`)}"></circle>`;
          if (labelAll || (labelEndpoints && idx === points.length - 1)) {
            const yOffset = options.zeroBase ? -9 : (point.y >= 0 ? -9 : 16);
            svg += `<text class="point-label" x="${x}" y="${y + yOffset}" text-anchor="middle">${htmlEscape(point.label)}</text>`;
          }
        });
      });
      svg += `</svg>`;
      target.innerHTML = svg;

      const concise = series.length > 18 ? series.filter((_, idx) => idx % Math.ceil(series.length / 18) === 0) : series;
      legend.innerHTML = concise.map(item => `<span class="legend-item"><span class="legend-swatch" style="--swatch:${item.color}; ${item.dash ? "border-top:3px dashed " + item.color + "; background:transparent;" : ""}"></span>${htmlEscape(item.key)}</span>`).join("");
      attachTooltips(target);
    }

    function attachTooltips(scope) {
      const tip = document.getElementById("tooltip");
      scope.querySelectorAll("[data-tip]").forEach(node => {
        node.addEventListener("mousemove", event => {
          tip.innerHTML = node.dataset.tip;
          tip.style.left = `${event.clientX}px`;
          tip.style.top = `${event.clientY - 12}px`;
          tip.classList.add("visible");
        });
        node.addEventListener("mouseleave", () => tip.classList.remove("visible"));
        node.addEventListener("click", () => selectPoint(node));
        node.addEventListener("keydown", event => {
          if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            selectPoint(node);
          }
        });
      });
    }

    function selectPoint(node) {
      const selected = state.pointLookup.get(node.dataset.pointId);
      if (!selected) return;
      state.selectedPoint = selected;
      document.querySelectorAll(".point.selected").forEach(item => item.classList.remove("selected"));
      node.classList.add("selected");
      renderSelectedPoint();
      document.getElementById("selectedPointPanel").scrollIntoView({ block: "nearest", behavior: "smooth" });
    }

    function renderSelectedPoint() {
      const host = document.getElementById("selectedPointPanel");
      const selected = state.selectedPoint;
      if (!selected) {
        host.innerHTML = `<div class="selected-empty">คลิกจุดบนกราฟจำนวนหรือกราฟการเติบโต ข้อมูลของจุดนั้นจะแสดงค้างไว้ตรงนี้โดยไม่ต้องเอาเมาส์วาง</div>`;
        return;
      }
      const row = selected.row;
      const isMonthly = row.month !== undefined;
      const isQuarterly = row.quarter !== undefined;
      const periodGrowth = isMonthly
        ? [["MoM", row.mom_pct], ["YoY", row.yoy_pct]]
        : isQuarterly
          ? [["QoQ", row.qoq_pct], ["YoY", row.yoy_pct]]
          : [["YoY", row.yoy_pct], ["เกณฑ์ YoY", row.yoy_basis === "full_year" ? "เต็มปี" : (row.yoy_basis || "n/a")]];
      const status = row.is_full_year === false ? "YTD" : row.annual_only ? "Annual-only" : "ปกติ";
      const segment = row.segment_label || selectedSegmentLabel();
      const source = row.source_file_url ? `<a href="${htmlEscape(row.source_file_url)}">เปิดไฟล์ต้นทาง</a>` : "รวมจากข้อมูลรายเดือน";
      host.innerHTML = `
        <div class="selected-main">
          <div>
            <div class="selected-kicker">${htmlEscape(segment)} | ${htmlEscape(selected.seriesKey)} | ${htmlEscape(selected.metricLabel)}</div>
            <div class="selected-value" style="color:${htmlEscape(selected.color)}">${htmlEscape(selected.metricDisplay)}</div>
            <div class="note">${htmlEscape(selected.period)} | จำนวน ${number(row.arrivals)} คน</div>
          </div>
          <div class="selected-grid">
            ${periodGrowth.map(([label, value]) => `
              <div class="selected-stat">
                <span>${htmlEscape(label)}</span>
                <strong class="${typeof value === "number" ? deltaClass(value) : "neutral"}">${typeof value === "number" ? pct(value) : htmlEscape(value)}</strong>
              </div>
            `).join("")}
            <div class="selected-stat">
              <span>สถานะ</span>
              <strong>${htmlEscape(status)}</strong>
            </div>
            <div class="selected-stat">
              <span>แหล่งข้อมูล</span>
              <strong>${source}</strong>
            </div>
          </div>
          <div class="selected-actions">
            <button type="button" id="clearSelectedPoint">ล้างจุดที่เลือก</button>
          </div>
        </div>
      `;
      document.getElementById("clearSelectedPoint").addEventListener("click", () => {
        state.selectedPoint = null;
        document.querySelectorAll(".point.selected").forEach(item => item.classList.remove("selected"));
        renderSelectedPoint();
      });
    }

    function renderCharts() {
      state.pointLookup = new Map();
      const rows = selectedRows();
      const period = state.grain === "monthly" ? "รายเดือน" : state.grain === "quarterly" ? "รายไตรมาส" : "รายปี";
      const segment = selectedSegmentLabel();
      document.getElementById("arrivalsTitle").textContent = `จำนวนผู้เดินทางเข้าไทย (${period}) | ${segment}`;
      document.getElementById("arrivalsHint").textContent = state.grain === "annual"
        ? "เส้นรายปีแสดงยอดรวมของแต่ละปีในตัวกรองนี้ โดยปี 2569 เป็น YTD ถ้ามีข้อมูลถึงล่าสุด"
        : "หนึ่งเส้นต่อหนึ่งปี สีแยกปีตามตัวกรอง";
      document.getElementById("growthTitle").textContent = `การเติบโต (${growthFields().map(item => item[1]).join(" + ")})`;
      document.getElementById("growthHint").textContent = state.grain === "annual"
        ? "YoY เทียบยอดรวมรายปีกับปีก่อนหน้าของตัวกรองเดียวกัน"
        : "เส้นทึบคือ period-on-period และเส้นประคือ YoY เมื่อเลือกดูพร้อมกัน";
      renderLineChart("arrivalsChart", "arrivalsLegend", buildArrivalSeries(rows), {
        title: "Tourist arrivals",
        zeroBase: true,
        yFormatter: shortNumber
      });
      renderLineChart("growthChart", "growthLegend", buildGrowthSeries(rows), {
        title: "Growth",
        zeroBase: false,
        yFormatter: value => `${value.toFixed(0)}%`
      });
    }

    function renderDetailTable() {
      const rows = selectedRows().slice().sort((a, b) => {
        const ax = state.grain === "monthly" ? a.month : state.grain === "quarterly" ? a.quarter : 0;
        const bx = state.grain === "monthly" ? b.month : state.grain === "quarterly" ? b.quarter : 0;
        return b.year - a.year || bx - ax;
      });
      const table = document.getElementById("detailTable");
      document.getElementById("tableHint").textContent = `${rows.length} แถว | ${selectedSegmentLabel()} | จากตัวกรองปีที่เลือก`;
      let header = "";
      let body = "";
      if (state.grain === "monthly") {
        header = "<tr><th>ช่วงเวลา</th><th>ปี</th><th>จำนวน</th><th>MoM</th><th>YoY</th><th>เผยแพร่</th><th>แหล่งไฟล์</th></tr>";
        body = rows.map(row => `<tr>
          <td>${MONTHS_TH[row.month - 1]} ${be(row.year)}</td>
          <td>${row.year}</td>
          <td>${number(row.arrivals)}</td>
          <td class="${deltaClass(row.mom_pct)}">${pct(row.mom_pct)}</td>
          <td class="${deltaClass(row.yoy_pct)}">${pct(row.yoy_pct)}</td>
          <td>${row.source_published ? row.source_published.slice(0, 10) : ""}</td>
          <td>${row.source_file_url ? `<a href="${htmlEscape(row.source_file_url)}">MOTS</a>` : "รวม"}</td>
        </tr>`).join("");
      } else if (state.grain === "quarterly") {
        header = "<tr><th>ช่วงเวลา</th><th>ปี</th><th>จำนวน</th><th>QoQ</th><th>YoY</th><th>หมายเหตุ</th></tr>";
        body = rows.map(row => `<tr>
          <td>Q${row.quarter} ${be(row.year)}</td>
          <td>${row.year}</td>
          <td>${number(row.arrivals)}</td>
          <td class="${deltaClass(row.qoq_pct)}">${pct(row.qoq_pct)}</td>
          <td class="${deltaClass(row.yoy_pct)}">${pct(row.yoy_pct)}</td>
          <td>รวมจากข้อมูลรายเดือน</td>
        </tr>`).join("");
      } else {
        header = "<tr><th>ปี</th><th>ค.ศ.</th><th>จำนวน</th><th>เดือน</th><th>YoY</th><th>เกณฑ์ YoY</th><th>สถานะ</th></tr>";
        body = rows.map(row => `<tr>
          <td>${be(row.year)}</td>
          <td>${row.year}</td>
          <td>${number(row.arrivals)}</td>
          <td>${row.months}</td>
          <td class="${deltaClass(row.yoy_pct)}">${pct(row.yoy_pct)}</td>
          <td>${row.yoy_basis === "full_year" ? "เต็มปี" : htmlEscape(row.yoy_basis || "")}</td>
          <td>${row.is_full_year ? "เต็มปี" : "YTD"}</td>
        </tr>`).join("");
      }
      table.innerHTML = `<thead>${header}</thead><tbody>${body}</tbody>`;
    }

    function renderValidation() {
      const table = document.getElementById("validationTable");
      const rows = DATA.validation.slice().sort((a, b) => b.year - a.year);
      const countryValidation = DATA.country_validation || [];
      const countryMatches = countryValidation.filter(row => row.status === "Match").length;
      const countryNoRows = countryValidation.filter(row => row.status === "No country rows").length;
      const countryYears = uniqueYears(DATA.country_monthly || []);
      document.getElementById("validationHint").textContent =
        `ยอดรวมรายปี + รายประเทศ: ${countryMatches} เดือน reconcile ตรงกับยอดรวม; ${countryNoRows} เดือนเป็น total-only | รายประเทศครอบคลุม ${countryYears.length ? be(countryYears[0]) + "-" + be(countryYears[countryYears.length - 1]) : "n/a"}`;
      table.innerHTML = `<thead><tr><th>ปี</th><th>ยอด MOTS</th><th>แหล่งตรวจซ้ำ</th><th>ผลต่าง</th><th>สถานะ</th></tr></thead><tbody>
        ${rows.map(row => {
          const hasWb = row.world_bank_total !== null && row.world_bank_total !== undefined && row.world_bank_total !== "";
          const hasReceipt = row.receipt_total !== null && row.receipt_total !== undefined && row.receipt_total !== "";
          const cross = hasWb ? `World Bank ${number(row.world_bank_total)}` : hasReceipt ? `MOTS receipts ${number(row.receipt_total)}` : "";
          const diff = hasWb ? number(row.difference) : hasReceipt ? number(row.receipt_difference) : "";
          return `<tr>
            <td>${be(row.year)}</td>
            <td>${number(row.mots_total)}</td>
            <td>${cross}</td>
            <td>${diff}</td>
            <td>${htmlEscape(row.status)}</td>
          </tr>`;
        }).join("")}
      </tbody>`;
    }

    function renderSources() {
      const meta = DATA.metadata;
      const trendResource = (meta.trend_inbound_result.resources || [])[0] || {};
      const statResource = (meta.data_go_result.resources || [])[0] || {};
      const latest = DATA.monthly[DATA.monthly.length - 1];
      const countryYears = uniqueYears(DATA.country_monthly || []);
      const sourceList = document.getElementById("sourceList");
      sourceList.innerHTML = `
        <li><a href="${htmlEscape(meta.mots_category_url)}">MOTS สถิตินักท่องเที่ยว category 411</a> แหล่งเผยแพร่ไฟล์รายเดือนของสำนักงานปลัดกระทรวงการท่องเที่ยวและกีฬา</li>
        <li><a href="${htmlEscape(meta.data_go_package_api)}">data.go.th: ${htmlEscape(meta.data_go_result.title)}</a> metadata modified ${htmlEscape((meta.data_go_result.metadata_modified || "").slice(0, 10))}; resource ชี้ไปหน้า MOTS category 411</li>
        <li><a href="${htmlEscape(meta.trend_inbound_package_api)}">data.go.th: ${htmlEscape(meta.trend_inbound_result.title)}</a> metadata modified ${htmlEscape((meta.trend_inbound_result.metadata_modified || "").slice(0, 10))}; CSV resource updated ${htmlEscape(trendResource.resource_last_updated_date || (trendResource.last_modified || "").slice(0, 10))}</li>
        <li><a href="${htmlEscape(latest.source_file_url)}">MOTS latest workbook</a> เผยแพร่ ${htmlEscape((latest.source_published || "").slice(0, 10))} ครอบคลุมถึง ${dateText(latest.date)}</li>
        <li>ตัวกรองรายประเทศ/รายทวีปใช้ country-level CSV จาก data.go.th/MOTS ร่วมกับ workbook รายเดือนล่าสุดของ MOTS ครอบคลุม ${countryYears.length ? be(countryYears[0]) + "-" + be(countryYears[countryYears.length - 1]) : "n/a"}; ไฟล์ประเทศปี 2556-2557 ที่ตรวจพบถูกกันออกจาก filter เพราะยอดประเทศรวมแล้วไม่ตรงกับ Grand Total</li>
        <li><a href="${htmlEscape(meta.world_bank_api)}">World Bank ST.INT.ARVL API</a> ใช้ตรวจยอดรายปี 2555-2562 โดยต่างกันเพียงระดับ rounding ของ annual arrivals</li>
      `;
    }

    function render() {
      ensureSegmentDefaults();
      ensureYears();
      document.querySelectorAll("#grainButtons button").forEach(button => button.classList.toggle("active", button.dataset.grain === state.grain));
      renderSegmentControls();
      renderGrowthButtons();
      renderYearStrip();
      renderKpis();
      renderCharts();
      renderDetailTable();
      renderValidation();
      renderSources();
    }

    setupControls();
    state.selectedYears = new Set(defaultYears());
    render();
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    raise SystemExit(main())
