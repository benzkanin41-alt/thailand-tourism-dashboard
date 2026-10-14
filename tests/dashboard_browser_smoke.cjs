const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || "playwright");
const baseUrl = process.env.DASHBOARD_URL || "http://127.0.0.1:12009/";
const outputDir = process.env.QA_OUTPUT_DIR || path.join(__dirname, "..", "work", "browser-qa");
const reports = [];
const browserErrors = [];

async function audit(page, name) {
  const report = await page.evaluate(name => {
    const intersections = [];
    for (const chartId of ["arrivalsChart", "growthChart"]) {
      const labels = [...document.querySelectorAll("#" + chartId + " .point-label")]
        .filter(el => el.getAttribute("visibility") !== "hidden" && getComputedStyle(el).display !== "none");
      for (let i = 0; i < labels.length; i += 1) {
        const a = labels[i].getBoundingClientRect();
        for (let j = i + 1; j < labels.length; j += 1) {
          const b = labels[j].getBoundingClientRect();
          const width = Math.min(a.right, b.right) - Math.max(a.left, b.left);
          const height = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
          if (width > 1 && height > 1) {
            intersections.push({ chartId, a: labels[i].textContent, b: labels[j].textContent });
          }
        }
      }
    }
    const overflow = [...document.querySelectorAll(
      "h1,h1 .title-word,.card .label,.card .value,.card .note,.country-metric-label," +
      ".country-metric-value,.country-metric-note,.panel-head h2,.source-pill," +
      ".selected-kicker,.selected-value,.selected-stat strong,#selectedPointPanel .note"
    )].filter(el => el.getClientRects().length && el.scrollWidth > el.clientWidth + 2)
      .map(el => ({ text: el.textContent.trim(), width: el.clientWidth, contentWidth: el.scrollWidth }));
    const model = currentModel();
    const rows = matchingCountryRows();
    const latest = model.monthly.at(-1);
    const expected = rows.length
      ? rows.filter(row => row.date === latest.date).reduce((sum, row) => sum + Number(row.arrivals), 0)
      : DATA.monthly.at(-1).arrivals;
    return {
      name,
      viewport: document.documentElement.clientWidth,
      segment: state.segmentType,
      country: state.selectedCountry,
      grain: state.grain,
      latest: latest.date,
      latestArrivals: latest.arrivals,
      expectedLatest: expected,
      pageOverflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      textOverflow: overflow,
      labelIntersections: intersections,
      arrivalPoints: document.querySelectorAll("#arrivalsChart .point").length,
      visibleArrivalLabels: [...document.querySelectorAll("#arrivalsChart .point-label")]
        .filter(label => label.getAttribute("visibility") !== "hidden").length,
      growthPoints: document.querySelectorAll("#growthChart .point").length,
      countryDetailVisible: !document.getElementById("countryDetailPanel").hidden
    };
  }, name);
  assert.equal(report.pageOverflow, 0, name + ": page overflow");
  assert.equal(report.textOverflow.length, 0, name + ": text overflow");
  assert.equal(Number(report.latestArrivals), Number(report.expectedLatest), name + ": aggregate mismatch");
  assert.ok(report.arrivalPoints > 0, name + ": missing arrival graph");
  reports.push(report);
  return report;
}

(async () => {
  fs.mkdirSync(outputDir, { recursive: true });
  const browser = await chromium.launch({
    executablePath: process.env.PLAYWRIGHT_BROWSER_EXECUTABLE ||
      (process.platform === "win32" ? "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" : undefined),
    headless: true
  });
  try {
    for (const width of [1440, 768, 390, 320]) {
      const context = await browser.newContext({ viewport: { width, height: 1000 } });
      const page = await context.newPage();
      page.on("pageerror", error => browserErrors.push({ width, error: error.message }));
      await page.goto(baseUrl, { waitUntil: "load" });
      await page.waitForSelector("#arrivalsChart svg");
      if (width === 1440) {
        const countryChecks = await page.evaluate(() => {
          const originalCountry = state.selectedCountry;
          const originalSegment = state.segmentType;
          const failures = [];
          for (const country of COUNTRY_OPTIONS) {
            state.segmentType = "country";
            state.selectedCountry = country;
            const sourceRows = matchingCountryRows();
            const model = currentModel();
            for (const row of model.monthly) {
              const expected = sourceRows.filter(source => source.date === row.date)
                .reduce((sum, source) => sum + Number(source.arrivals), 0);
              if (row.arrivals !== expected) failures.push(country + ": monthly " + row.date);
            }
            for (const grain of ["ytd", "quarterly", "annual"]) {
              for (const row of model[grain]) {
                const expected = sourceRows.filter(source => Number(source.year) === row.year && (
                  grain === "annual" || (grain === "ytd" ? Number(source.month) <= row.month
                    : Math.ceil(Number(source.month) / 3) === row.quarter)
                )).reduce((sum, source) => sum + Number(source.arrivals), 0);
                if (row.arrivals !== expected) failures.push(country + ": " + grain + " " + row.date);
              }
            }
          }
          state.segmentType = originalSegment;
          state.selectedCountry = originalCountry;
          return { countries: COUNTRY_OPTIONS.length, failures };
        });
        assert.deepEqual(countryChecks.failures, []);
        console.log("Country aggregate checks: " + countryChecks.countries);
      }
      await audit(page, "national-default-" + width);
      if (width === 1440 || width === 390) {
        await page.screenshot({ path: path.join(outputDir, "overview-" + width + ".jpg"), type: "jpeg", quality: 55 });
      }
      await page.selectOption("#segmentMode", "country");
      await page.selectOption("#countrySelect", "China");
      for (const grain of ["monthly", "ytd", "quarterly", "annual"]) {
        await page.click('[data-grain="' + grain + '"]');
        await audit(page, "China-" + grain + "-" + width);
        if (grain === "ytd") {
          assert.deepEqual(await page.locator("#growthButtons button").allTextContents(), ["YoY"]);
        }
        const arrivalPoint = page.locator("#arrivalsChart .point").last();
        const arrivalId = await arrivalPoint.getAttribute("data-point-id");
        await arrivalPoint.click();
        assert.equal(await page.locator(".point.selected").count(), 1);
        assert.equal(await page.locator(".point.selected").getAttribute("data-point-id"), arrivalId,
          grain + " arrivals selection at " + width);
        assert.ok((await page.locator("#selectedPointPanel").innerText()).length > 30);
        const selectedDetails = await page.evaluate(() => ({
          text: document.getElementById("selectedPointPanel").innerText,
          expected: state.selectedPoint.metricDisplay
        }));
        assert.ok(selectedDetails.text.includes(selectedDetails.expected));
        const growthPoint = page.locator("#growthChart .point").last();
        const growthId = await growthPoint.getAttribute("data-point-id");
        await growthPoint.click();
        assert.equal(await page.locator("#growthChart .point.selected").count(), 1);
        assert.equal(await page.locator(".point.selected").getAttribute("data-point-id"), growthId,
          grain + " growth selection at " + width);
        await audit(page, "China-click-details-" + grain + "-" + width);
        if (grain === "monthly" || grain === "quarterly") {
          const growthModes = await page.locator("#growthButtons button").allTextContents();
          for (const text of growthModes) {
            await page.locator("#growthButtons").getByRole("button", { name: text, exact: true }).click();
            await audit(page, "China-" + grain + "-" + text + "-" + width);
          }
        }
      }
      await page.click('[data-grain="monthly"]');
      const rankTarget = await page.locator("[data-country-select]").nth(1).getAttribute("data-country-select");
      await page.locator("[data-country-select]").nth(1).click();
      assert.equal(await page.locator("#countrySelect").inputValue(), rankTarget);
      await audit(page, "rank-click-" + width);
      await page.locator("#countryDetailPanel").screenshot({
        path: path.join(outputDir, "country-detail-" + width + ".jpg"), type: "jpeg", quality: 55
      });
      const longCountry = await page.evaluate(() =>
        COUNTRY_OPTIONS.slice().sort((a, b) => b.length - a.length)[0]
      );
      await page.selectOption("#countrySelect", longCountry);
      await audit(page, "long-country-" + width);
      await page.selectOption("#countrySelect", "China");
      await page.click("#allYears");
      await audit(page, "all-years-" + width);
      await page.selectOption("#segmentMode", "continent");
      const continents = await page.locator("#continentSelect option").evaluateAll(options =>
        options.map(option => option.value)
      );
      for (const continent of continents) {
        await page.selectOption("#continentSelect", continent);
        for (const grain of ["monthly", "ytd", "quarterly", "annual"]) {
          await page.click('[data-grain="' + grain + '"]');
          await audit(page, continent + "-" + grain + "-" + width);
        }
      }
      await context.close();
    }
    const labelCollisions = reports.filter(report => report.labelIntersections.length);
    fs.writeFileSync(path.join(outputDir, "browser-qa.json"), JSON.stringify({ reports, browserErrors, labelCollisions }, null, 2));
    console.log(JSON.stringify({
      reports: reports.length,
      browserErrors,
      labelCollisionCases: labelCollisions.length,
      collisionSamples: labelCollisions.slice(0, 8).map(report => ({
        name: report.name, collisions: report.labelIntersections.length,
        sample: report.labelIntersections.slice(0, 3)
      }))
    }, null, 2));
    assert.equal(browserErrors.length, 0);
    assert.equal(labelCollisions.length, 0, "Overlapping graph point labels");
  } finally {
    await browser.close();
  }
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
