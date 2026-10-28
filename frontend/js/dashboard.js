/* ============================================================
   SEO Critics Studio — dashboard.js
   Handles: triggering a scan, animating the radar/blips during
   crawl, animating the score gauge + count-up, the tabbed results
   console (Overview, Issues, Pages, Crawl, Link Graph, Duplicates,
   Sitemap, robots.txt, Performance, Compare), the Page Details
   drawer, and scan history.
   ============================================================ */

const API_BASE = "";
const GAUGE_CIRCUMFERENCE = 2 * Math.PI * 86; // r=86 from the SVG
const PAGE_SIZE = 15;

const els = {
  urlInput: document.getElementById("urlInput"),
  maxPages: document.getElementById("maxPages"),
  maxDepth: document.getElementById("maxDepth"),
  runBtn: document.getElementById("runScanBtn"),
  statusHint: document.getElementById("statusHint"),
  logPanel: document.getElementById("logPanel"),
  logLines: document.getElementById("logLines"),
  radar: document.getElementById("radar"),
  radarBlips: document.getElementById("radarBlips"),
  radarCaption: document.getElementById("radarCaption"),
  results: document.getElementById("results"),
  scoreHero: document.getElementById("scoreHero"),
  gaugeFill: document.getElementById("gaugeFill"),
  stampScore: document.getElementById("stampScore"),
  stampHealth: document.getElementById("stampHealth"),
  metaWebsite: document.getElementById("metaWebsite"),
  metaDomain: document.getElementById("metaDomain"),
  metaPages: document.getElementById("metaPages"),
  meters: document.getElementById("meters"),
  recList: document.getElementById("recList"),
  recFilter: document.getElementById("recFilter"),
  signalList: document.getElementById("signalList"),
  keywordChips: document.getElementById("keywordChips"),
  dlHtml: document.getElementById("dlHtml"),
  dlCsv: document.getElementById("dlCsv"),
  dlExcel: document.getElementById("dlExcel"),
  dlPdf: document.getElementById("dlPdf"),
  historyToggle: document.getElementById("historyToggle"),
  historyPanel: document.getElementById("historyPanel"),
  historyList: document.getElementById("historyList"),
  body: document.body,

  tabBar: document.getElementById("tabBar"),
  tabCountIssues: document.getElementById("tabCountIssues"),

  issueSeverityFilter: document.getElementById("issueSeverityFilter"),
  issueCategoryFilter: document.getElementById("issueCategoryFilter"),
  issueList: document.getElementById("issueList"),

  pageSearch: document.getElementById("pageSearch"),
  pageFilterRow: document.getElementById("pageFilterRow"),
  pagesTable: document.getElementById("pagesTable"),
  pagesTableBody: document.getElementById("pagesTableBody"),
  pagesPagination: document.getElementById("pagesPagination"),

  crawlStatGrid: document.getElementById("crawlStatGrid"),
  statusDistribution: document.getElementById("statusDistribution"),
  depthDistribution: document.getElementById("depthDistribution"),

  graphNote: document.getElementById("graphNote"),
  graphWrap: document.getElementById("graphWrap"),
  linkGraphSvg: document.getElementById("linkGraphSvg"),

  dupTitles: document.getElementById("dupTitles"),
  dupDescriptions: document.getElementById("dupDescriptions"),
  dupCanonicals: document.getElementById("dupCanonicals"),
  similarNote: document.getElementById("similarNote"),
  similarPairs: document.getElementById("similarPairs"),

  sitemapStatGrid: document.getElementById("sitemapStatGrid"),
  sitemapCoverageNote: document.getElementById("sitemapCoverageNote"),
  sitemapOnlyCount: document.getElementById("sitemapOnlyCount"),
  sitemapOnlyList: document.getElementById("sitemapOnlyList"),
  crawledOnlyCount: document.getElementById("crawledOnlyCount"),
  crawledOnlyList: document.getElementById("crawledOnlyList"),
  bothCount: document.getElementById("bothCount"),
  bothList: document.getElementById("bothList"),

  robotsScopeNote: document.getElementById("robotsScopeNote"),
  robotsInspectorHead: document.getElementById("robotsInspectorHead"),
  robotsInspectorTable: document.getElementById("robotsInspectorTable"),
  uaGroups: document.getElementById("uaGroups"),
  robotsBlockedPanel: document.getElementById("robotsBlockedPanel"),
  robotsBlockedList: document.getElementById("robotsBlockedList"),

  perfStatGrid: document.getElementById("perfStatGrid"),
  perfSlowThreshold: document.getElementById("perfSlowThreshold"),
  perfLargeThreshold: document.getElementById("perfLargeThreshold"),
  perfSlowList: document.getElementById("perfSlowList"),
  perfLargeList: document.getElementById("perfLargeList"),

  comparePrev: document.getElementById("comparePrev"),
  compareCurr: document.getElementById("compareCurr"),
  compareBtn: document.getElementById("compareBtn"),
  compareResults: document.getElementById("compareResults"),

  drawerOverlay: document.getElementById("drawerOverlay"),
  pageDrawer: document.getElementById("pageDrawer"),
  drawerTitle: document.getElementById("drawerTitle"),
  drawerClose: document.getElementById("drawerClose"),
  drawerBody: document.getElementById("drawerBody"),
};

const HEALTH_COLORS = {
  Excellent: "#34D399",
  Good: "#2FE0C4",
  Average: "#F5B942",
  Poor: "#FF8A5B",
  Critical: "#FF5C5C",
};

const SEVERITY_COLORS = {
  CRITICAL: "#FF5C5C",
  HIGH: "#FF8A5B",
  MEDIUM: "#F5B942",
  LOW: "#2FE0C4",
  INFO: "#8B93A9",
};

const CATEGORY_ICONS = {
  metadata: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M7 3h7l7 7v9a2 2 0 01-2 2H7a2 2 0 01-2-2V5a2 2 0 012-2z"/><path d="M14 3v6h6"/><path d="M9 13h6M9 17h4"/></svg>',
  technical: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a4 4 0 10-4.4 4.4l-6 6a1.5 1.5 0 002.1 2.1l6-6a4 4 0 004.3-4.4l-2.6 2.6-2-2z"/></svg>',
  images: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="8.5" cy="9.5" r="1.6"/><path d="M21 16l-5.5-5.5a2 2 0 00-2.8 0L4 19"/></svg>',
  links: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M9.5 14.5l5-5"/><path d="M11 6.5l1-1a3.5 3.5 0 015 5l-1 1"/><path d="M13 17.5l-1 1a3.5 3.5 0 01-5-5l1-1"/></svg>',
  sitemap: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="4.5" r="2"/><circle cx="5" cy="19.5" r="2"/><circle cx="19" cy="19.5" r="2"/><path d="M12 6.5v6M12 12.5L5 17.5M12 12.5l7 5"/></svg>',
  robots: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="9" width="16" height="11" rx="2"/><path d="M12 9V5m0 0a1.5 1.5 0 100-3 1.5 1.5 0 000 3z"/><circle cx="9" cy="14.5" r="1.2" fill="currentColor" stroke="none"/><circle cx="15" cy="14.5" r="1.2" fill="currentColor" stroke="none"/><path d="M2 12v3M22 12v3"/></svg>',
  performance: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21a9 9 0 100-18 9 9 0 000 18z"/><path d="M12 12l4.2-4.2"/><path d="M12 8v1"/></svg>',
  mobile: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="7" y="2" width="10" height="20" rx="2"/><path d="M11 18h2"/></svg>',
  social: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="2.4"/><circle cx="6" cy="12" r="2.4"/><circle cx="18" cy="19" r="2.4"/><path d="M8.2 10.8l7.6-4.1M8.2 13.2l7.6 4.1"/></svg>',
  duplicate: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="13" height="13" rx="2"/><path d="M9 16v3a2 2 0 002 2h8a2 2 0 002-2v-8a2 2 0 00-2-2h-3"/></svg>',
  redirect: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3l4 4-4 4"/><path d="M3 11V9a4 4 0 014-4h14"/><path d="M7 21l-4-4 4-4"/><path d="M21 13v2a4 4 0 01-4 4H3"/></svg>',
};

const PRIORITY_COLORS = { high: "#FF5C5C", medium: "#F5B942", low: "#2FE0C4" };
const PRIORITY_WARN_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 9v4M12 17h.01M10.3 3.86L1.82 18a1.5 1.5 0 001.3 2.25h17.76a1.5 1.5 0 001.3-2.25L14.7 3.86a1.5 1.5 0 00-2.4 0z"/></svg>';

const CATEGORY_LABELS = [
  { key: "metadata_score", max: "metadata", label: "Metadata", icon: "metadata" },
  { key: "technical_score", max: "technical", label: "Technical SEO", icon: "technical" },
  { key: "images_score", max: "images", label: "Images", icon: "images" },
  { key: "links_score", max: "links", label: "Links", icon: "links" },
  { key: "sitemap_score", max: "sitemap", label: "Sitemap", icon: "sitemap" },
  { key: "robots_score", max: "robots", label: "robots.txt", icon: "robots" },
  { key: "performance_score", max: "performance", label: "Performance", icon: "performance" },
];

const CRAWL_LOG_MESSAGES = [
  "resolving domain…", "fetching robots.txt…", "fetching sitemap.xml…",
  "crawling internal pages…", "parsing HTML and extracting metadata…",
  "checking headings, canonical tags and word counts…",
  "checking images for ALT attributes…", "checking internal / external links…",
  "computing SEO score…", "classifying issues…",
  "generating HTML, CSV, Excel and PDF reports…",
];

// ---------------------------------------------------------------------------
// Application state
// ---------------------------------------------------------------------------

const state = {
  websiteId: null,
  domain: null,
  pagesList: [],       // full page rows for the current website
  pagesById: {},        // page_id -> page row
  pageFilter: "all",
  pageSearch: "",
  pageSort: { key: null, dir: "asc" },
  pagePage: 1,
  issuesAll: [],
  issueSeverity: "all",
  issueCategory: "all",
  tabLoaded: {},         // tab name -> bool, reset per website
};

let logInterval = null;
let blipInterval = null;
let currentRecommendations = [];
let currentRecFilter = "all";

// ---------------------------------------------------------------------------
// Small utilities
// ---------------------------------------------------------------------------

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str == null ? "" : String(str);
  return div.innerHTML;
}

function statusBadgeHtml(code) {
  if (!code) return '<span class="badge bad">error</span>';
  if (code >= 200 && code < 300) return `<span class="badge ok">${code}</span>`;
  if (code >= 300 && code < 400) return `<span class="badge warn">${code}</span>`;
  return `<span class="badge bad">${code}</span>`;
}

function setMood(color) {
  document.documentElement.style.setProperty("--mood", color);
  els.body.style.setProperty("--mood-h", color);
}

function animateCountUp(el, target, duration = 900) {
  const start = performance.now();
  function tick(now) {
    const progress = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.round(target * eased);
    if (progress < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

async function fetchJson(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: "Request failed." }));
    throw new Error(err.detail || "Request failed.");
  }
  return response.json();
}

// ---------------------------------------------------------------------------
// Radar / crawl-log visuals (scan in progress)
// ---------------------------------------------------------------------------

function spawnBlip() {
  const angle = Math.random() * Math.PI * 2;
  const radius = 18 + Math.random() * 62;
  const x = 50 + Math.cos(angle) * (radius / 2);
  const y = 50 + Math.sin(angle) * (radius / 2);
  const blip = document.createElement("div");
  blip.className = "blip";
  blip.style.left = `${x}%`;
  blip.style.top = `${y}%`;
  els.radarBlips.appendChild(blip);
  setTimeout(() => blip.remove(), 1800);
}

function startScanVisuals(maxPages) {
  els.logPanel.hidden = false;
  els.logLines.textContent = "";
  els.radarCaption.textContent = "scanning…";
  els.radarBlips.innerHTML = "";

  let i = 0;
  logInterval = setInterval(() => {
    if (i < CRAWL_LOG_MESSAGES.length) {
      els.logLines.textContent += `$ ${CRAWL_LOG_MESSAGES[i]}\n`;
      els.logLines.scrollTop = els.logLines.scrollHeight;
      i += 1;
    }
  }, 500);

  let blips = 0;
  const targetBlips = Math.min(Math.max(maxPages, 4), 18);
  blipInterval = setInterval(() => {
    if (blips < targetBlips) { spawnBlip(); blips += 1; }
  }, 380);
}

function stopScanVisuals(success) {
  if (logInterval) clearInterval(logInterval);
  if (blipInterval) clearInterval(blipInterval);
  els.logLines.textContent += success ? "$ audit complete.\n" : "$ audit failed.\n";
  els.logLines.scrollTop = els.logLines.scrollHeight;
  els.radarCaption.textContent = success ? "audit complete" : "audit failed";
}

// ---------------------------------------------------------------------------
// Scan orchestration
// ---------------------------------------------------------------------------

async function runScan() {
  const rawUrl = els.urlInput.value.trim();
  if (!rawUrl) {
    els.statusHint.textContent = "Please enter a website URL to audit.";
    els.statusHint.classList.add("error");
    return;
  }
  els.statusHint.classList.remove("error");
  els.statusHint.textContent = "Crawling in progress — this can take a moment for larger sites.";

  els.runBtn.disabled = true;
  els.results.hidden = true;

  const maxPagesVal = parseInt(els.maxPages.value, 10) || 10;
  startScanVisuals(maxPagesVal);

  try {
    const data = await fetchJson(`${API_BASE}/api/scan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        url: rawUrl,
        max_pages: maxPagesVal,
        max_depth: parseInt(els.maxDepth.value, 10) || 2,
      }),
    });

    stopScanVisuals(true);
    renderResults(data);
    els.statusHint.textContent = "Audit complete. Explore the tabs below for the full report.";
  } catch (err) {
    stopScanVisuals(false);
    els.statusHint.textContent = `Error: ${err.message}`;
    els.statusHint.classList.add("error");
  } finally {
    els.runBtn.disabled = false;
  }
}

// ---------------------------------------------------------------------------
// Overview tab: score hero, recommendations, category grid, signals, keywords
// ---------------------------------------------------------------------------

function renderRecommendations(recommendations, filter) {
  const filtered = filter === "all" ? recommendations : recommendations.filter((r) => r.priority === filter);
  if (!filtered.length) {
    els.recList.innerHTML = recommendations.length
      ? '<div class="rec-empty">No recommendations at this priority level.</div>'
      : '<div class="rec-empty">No issues detected — this site is in great shape.</div>';
    return;
  }
  els.recList.innerHTML = filtered.map((r) => {
    const color = PRIORITY_COLORS[r.priority] || "#2FE0C4";
    const icon = CATEGORY_ICONS[r.category] || PRIORITY_WARN_ICON;
    const affected = r.affected_pages ? `<span style="color:var(--text-dim);"> · ${r.affected_pages} page(s) affected</span>` : "";
    return `
      <div class="rec-card" style="--rec-color:${color}">
        <div class="rec-icon">${icon}</div>
        <div class="rec-body">
          <div class="rec-top"><span class="rec-priority">${r.priority}</span><span class="rec-title">${escapeHtml(r.title)}</span></div>
          <div class="rec-desc">${escapeHtml(r.description)}${affected}</div>
        </div>
      </div>`;
  }).join("");
}

function renderOverview(data) {
  const scores = data.scores;
  els.meters.innerHTML = "";
  CATEGORY_LABELS.forEach(({ key, max, label, icon }) => {
    const value = scores[key];
    const maxValue = scores.max_scores[max];
    const pctCat = maxValue ? (value / maxValue) * 100 : 0;
    const card = document.createElement("div");
    card.className = "cat-card";
    card.innerHTML = `
      <div class="cat-icon">${CATEGORY_ICONS[icon]}</div>
      <div class="cat-label">${label}</div>
      <div class="cat-value">${value} <span style="color:var(--text-dim); font-size:12px;">/ ${maxValue}</span></div>
      <div class="cat-track"><div class="cat-fill" style="width:0%" data-target="${pctCat}"></div></div>`;
    els.meters.appendChild(card);
  });
  requestAnimationFrame(() => {
    document.querySelectorAll(".cat-fill").forEach((fill) => { fill.style.width = `${fill.dataset.target}%`; });
  });

  const adv = data.advanced_checks || {};
  const totalPages = adv.total_pages || data.pages.length || 1;
  const signalDefs = [
    { key: "pages_with_viewport", label: "Mobile viewport tag" },
    { key: "pages_with_structured_data", label: "Structured data (schema.org)" },
    { key: "pages_with_open_graph", label: "Open Graph tags" },
    { key: "pages_with_twitter_card", label: "Twitter Card tags" },
    { key: "pages_with_lang", label: "Declared page language" },
  ];
  els.signalList.innerHTML = "";
  signalDefs.forEach(({ key, label }) => {
    const count = adv[key] || 0;
    const pct = totalPages ? (count / totalPages) * 100 : 0;
    const row = document.createElement("div");
    row.className = "signal-row";
    row.innerHTML = `
      <span>${label}</span>
      <div class="signal-bar-wrap">
        <div class="signal-track"><div class="signal-fill" style="width:0%" data-target="${pct}"></div></div>
        <span class="signal-count">${count}/${totalPages}</span>
      </div>`;
    els.signalList.appendChild(row);
  });
  requestAnimationFrame(() => {
    document.querySelectorAll(".signal-fill").forEach((fill) => { fill.style.width = `${fill.dataset.target}%`; });
  });

  const keywords = data.site_keywords || [];
  els.keywordChips.innerHTML = keywords.length
    ? keywords.map((kw) => `<span class="keyword-chip">${escapeHtml(kw.keyword)} <b>${kw.count}</b></span>`).join("")
    : '<span class="keyword-empty">No keyword data available.</span>';
}

// ---------------------------------------------------------------------------
// Master render entry point (called after a fresh scan or a history reload)
// ---------------------------------------------------------------------------

function renderResults(data) {
  const scores = data.scores;
  const color = HEALTH_COLORS[scores.health_level] || "#2FE0C4";
  setMood(color);

  const pct = Math.max(0, Math.min(scores.overall_score, 100)) / 100;
  const offset = GAUGE_CIRCUMFERENCE * (1 - pct);
  requestAnimationFrame(() => { els.gaugeFill.style.strokeDashoffset = offset; });
  animateCountUp(els.stampScore, Math.round(scores.overall_score));
  els.stampHealth.textContent = scores.health_level;

  els.metaWebsite.textContent = data.root_url;
  els.metaDomain.textContent = data.domain;
  els.metaPages.textContent = data.pages_scanned;

  els.dlHtml.href = `${API_BASE}/api/download/${data.website_id}/html`;
  els.dlCsv.href = `${API_BASE}/api/download/${data.website_id}/csv`;
  els.dlExcel.href = `${API_BASE}/api/download/${data.website_id}/excel`;
  els.dlPdf.href = `${API_BASE}/api/download/${data.website_id}/pdf`;

  currentRecommendations = data.recommendations || [];
  currentRecFilter = "all";
  els.recFilter.querySelectorAll(".rec-filter-btn").forEach((b) => b.classList.toggle("active", b.dataset.filter === "all"));
  renderRecommendations(currentRecommendations, currentRecFilter);

  renderOverview(data);

  // Reset per-website state and caches
  state.websiteId = data.website_id;
  state.domain = data.domain;
  state.pagesList = data.pages || [];
  state.pagesById = {};
  state.pagesList.forEach((p) => { if (p.page_id) state.pagesById[p.page_id] = p; });
  state.pageFilter = "all";
  state.pageSearch = "";
  els.pageSearch.value = "";
  document.querySelectorAll('[data-pfilter]').forEach((b) => b.classList.toggle("active", b.dataset.pfilter === "all"));
  state.pagePage = 1;
  state.issuesAll = [];
  state.tabLoaded = {};

  if (data.issues_summary) {
    const critHigh = (data.issues_summary.CRITICAL || 0) + (data.issues_summary.HIGH || 0);
    els.tabCountIssues.textContent = data.issue_count ? String(data.issue_count) : "";
    els.tabCountIssues.style.color = critHigh ? "var(--red)" : "";
  }

  renderPagesTable();
  activateTab("overview");
  els.results.hidden = false;
}

// ---------------------------------------------------------------------------
// Tab switching
// ---------------------------------------------------------------------------

function activateTab(tabName) {
  document.querySelectorAll(".tab-btn").forEach((b) => b.classList.toggle("active", b.dataset.tab === tabName));
  document.querySelectorAll("[data-tab-panel]").forEach((p) => { p.hidden = p.dataset.tabPanel !== tabName; });

  if (!state.websiteId) return;
  if (tabName === "issues" && !state.tabLoaded.issues) loadIssuesTab();
  if (tabName === "crawl" && !state.tabLoaded.crawl) loadCrawlTab();
  if (tabName === "graph" && !state.tabLoaded.graph) loadGraphTab();
  if (tabName === "duplicates" && !state.tabLoaded.duplicates) loadDuplicatesTab();
  if (tabName === "sitemap" && !state.tabLoaded.sitemap) loadSitemapTab();
  if (tabName === "robots" && !state.tabLoaded.robots) loadRobotsTab();
  if (tabName === "performance" && !state.tabLoaded.performance) loadPerformanceTab();
  if (tabName === "compare") loadCompareTab();
}

els.tabBar.addEventListener("click", (e) => {
  const btn = e.target.closest(".tab-btn");
  if (btn) activateTab(btn.dataset.tab);
});

// ---------------------------------------------------------------------------
// Issues tab
// ---------------------------------------------------------------------------

async function loadIssuesTab() {
  try {
    const issues = await fetchJson(`${API_BASE}/api/issues/${state.websiteId}`);
    state.issuesAll = issues;
    state.tabLoaded.issues = true;
    buildIssueCategoryFilter(issues);
    renderIssueList();
  } catch (err) {
    els.issueList.innerHTML = `<div class="rec-empty">Could not load issues: ${escapeHtml(err.message)}</div>`;
  }
}

function buildIssueCategoryFilter(issues) {
  const categories = Array.from(new Set(issues.map((i) => i.category))).sort();
  els.issueCategoryFilter.innerHTML = ['<button class="chip-filter active" data-cat="all">All categories</button>']
    .concat(categories.map((c) => `<button class="chip-filter" data-cat="${c}">${escapeHtml(c)}</button>`))
    .join("");
}

function renderIssueList() {
  let filtered = state.issuesAll;
  if (state.issueSeverity !== "all") filtered = filtered.filter((i) => i.severity === state.issueSeverity);
  if (state.issueCategory !== "all") filtered = filtered.filter((i) => i.category === state.issueCategory);

  if (!filtered.length) {
    els.issueList.innerHTML = '<div class="rec-empty">No issues match this filter.</div>';
    return;
  }

  els.issueList.innerHTML = filtered.map((i) => {
    const color = SEVERITY_COLORS[i.severity] || "#8B93A9";
    const icon = CATEGORY_ICONS[i.category] || PRIORITY_WARN_ICON;
    return `
      <div class="rec-card" style="--rec-color:${color}">
        <div class="rec-icon">${icon}</div>
        <div class="rec-body">
          <div class="rec-top"><span class="rec-priority">${i.severity}</span><span class="rec-title">${escapeHtml(i.title)}</span></div>
          <div class="rec-desc">${escapeHtml(i.description)}${i.affected_url ? `<br><a class="issue-link" data-url="${escapeHtml(i.affected_url)}" style="color:var(--cyan); cursor:pointer; font-family:var(--mono); font-size:11px;">${escapeHtml(i.affected_url)}</a>` : ""}</div>
        </div>
      </div>`;
  }).join("");
}

els.issueSeverityFilter.addEventListener("click", (e) => {
  const btn = e.target.closest(".rec-filter-btn");
  if (!btn) return;
  state.issueSeverity = btn.dataset.severity;
  els.issueSeverityFilter.querySelectorAll(".rec-filter-btn").forEach((b) => b.classList.toggle("active", b === btn));
  renderIssueList();
});

els.issueCategoryFilter.addEventListener("click", (e) => {
  const btn = e.target.closest(".chip-filter");
  if (!btn) return;
  state.issueCategory = btn.dataset.cat;
  els.issueCategoryFilter.querySelectorAll(".chip-filter").forEach((b) => b.classList.toggle("active", b === btn));
  renderIssueList();
});

els.issueList.addEventListener("click", (e) => {
  const link = e.target.closest(".issue-link");
  if (!link) return;
  const page = state.pagesList.find((p) => p.page_url === link.dataset.url);
  if (page && page.page_id) openDrawer(page.page_id);
});

// ---------------------------------------------------------------------------
// Pages tab: search + filter + sort + paginate + click-to-drawer
// ---------------------------------------------------------------------------

const PAGE_FILTERS = {
  all: () => true,
  200: (p) => p.status_code >= 200 && p.status_code < 300,
  "3xx": (p) => p.status_code >= 300 && p.status_code < 400,
  "4xx": (p) => p.status_code >= 400 && p.status_code < 500,
  "5xx": (p) => !p.status_code || p.status_code >= 500,
  missing_title: (p) => !p.title,
  missing_desc: (p) => !p.meta_description,
  broken: (p) => (p.broken_links || 0) > 0,
  missing_alt: (p) => (p.images_missing_alt || 0) > 0,
  slow: (p) => (p.response_time_ms || 0) > 1500,
  large: (p) => (p.page_size_kb || 0) > 1500,
};

function getSortValue(p, key) {
  switch (key) {
    case "title_length": return (p.title || "").length;
    case "desc_length": return (p.meta_description || "").length;
    case "canonical_url": return p.canonical_url ? 1 : 0;
    case "is_https": return p.is_https ? 1 : 0;
    case "is_indexable": return p.is_indexable ? 1 : 0;
    default: return p[key];
  }
}

function renderPagesTable() {
  let rows = state.pagesList.filter(PAGE_FILTERS[state.pageFilter] || PAGE_FILTERS.all);

  if (state.pageSearch) {
    const q = state.pageSearch.toLowerCase();
    rows = rows.filter((p) => (p.page_url || "").toLowerCase().includes(q) || (p.title || "").toLowerCase().includes(q));
  }

  if (state.pageSort.key) {
    const { key, dir } = state.pageSort;
    rows = [...rows].sort((a, b) => {
      const va = getSortValue(a, key);
      const vb = getSortValue(b, key);
      if (va == null && vb == null) return 0;
      if (va == null) return 1;
      if (vb == null) return -1;
      if (typeof va === "string") return dir === "asc" ? va.localeCompare(vb) : vb.localeCompare(va);
      return dir === "asc" ? va - vb : vb - va;
    });
  }

  const totalPages = Math.max(1, Math.ceil(rows.length / PAGE_SIZE));
  state.pagePage = Math.min(state.pagePage, totalPages);
  const start = (state.pagePage - 1) * PAGE_SIZE;
  const pageRows = rows.slice(start, start + PAGE_SIZE);

  els.pagesTableBody.innerHTML = "";
  pageRows.forEach((p) => {
    const tr = document.createElement("tr");
    tr.className = "clickable-row";
    if (p.page_id) tr.dataset.pageId = p.page_id;

    const indexBadge = p.is_indexable ? '<span class="badge ok">yes</span>' : '<span class="badge bad">no</span>';
    const httpsBadge = p.is_https ? '<span class="badge ok">yes</span>' : '<span class="badge bad">no</span>';
    const canonicalBadge = p.canonical_url ? '<span class="badge ok">yes</span>' : '<span class="badge warn">no</span>';
    const brokenBadge = p.broken_links > 0 ? `<span class="badge bad">${p.broken_links}</span>` : `<span class="badge ok">0</span>`;
    const altBadge = p.images_missing_alt > 0 ? `<span class="badge warn">${p.images_missing_alt}</span>` : `<span class="badge ok">0</span>`;
    const issueCount = p.issue_count != null ? p.issue_count : "—";
    const issueBadgeClass = p.issue_count > 3 ? "bad" : p.issue_count > 0 ? "warn" : "ok";

    tr.innerHTML = `
      <td class="url-cell" title="${escapeHtml(p.page_url)}">${escapeHtml(p.page_url)}</td>
      <td>${statusBadgeHtml(p.status_code)}</td>
      <td>${indexBadge}</td>
      <td class="url-cell" title="${escapeHtml(p.title || "")}">${escapeHtml((p.title || "—").slice(0, 40))}</td>
      <td>${(p.title || "").length}</td>
      <td>${(p.meta_description || "").length}</td>
      <td>${p.h1_count}</td>
      <td>${canonicalBadge}</td>
      <td>${p.word_count}</td>
      <td>${p.internal_links}</td>
      <td>${p.external_links}</td>
      <td>${brokenBadge}</td>
      <td>${p.image_count}</td>
      <td>${altBadge}</td>
      <td>${p.response_time_ms ?? "—"}</td>
      <td>${p.page_size_kb ?? "—"}</td>
      <td>${httpsBadge}</td>
      <td><span class="badge ${issueBadgeClass}">${issueCount}</span></td>
    `;
    els.pagesTableBody.appendChild(tr);
  });

  if (!pageRows.length) {
    els.pagesTableBody.innerHTML = `<tr><td colspan="18" style="text-align:center; color:var(--text-dim); padding:24px;">No pages match this filter/search.</td></tr>`;
  }

  els.pagesPagination.innerHTML = `
    <button id="pgPrev" ${state.pagePage <= 1 ? "disabled" : ""}>‹ Prev</button>
    <span>Page ${state.pagePage} of ${totalPages} (${rows.length} pages)</span>
    <button id="pgNext" ${state.pagePage >= totalPages ? "disabled" : ""}>Next ›</button>
  `;
  const prevBtn = document.getElementById("pgPrev");
  const nextBtn = document.getElementById("pgNext");
  if (prevBtn) prevBtn.addEventListener("click", () => { state.pagePage -= 1; renderPagesTable(); });
  if (nextBtn) nextBtn.addEventListener("click", () => { state.pagePage += 1; renderPagesTable(); });
}

els.pageSearch.addEventListener("input", (e) => {
  state.pageSearch = e.target.value.trim();
  state.pagePage = 1;
  renderPagesTable();
});

els.pageFilterRow.addEventListener("click", (e) => {
  const btn = e.target.closest("[data-pfilter]");
  if (!btn) return;
  state.pageFilter = btn.dataset.pfilter;
  state.pagePage = 1;
  els.pageFilterRow.querySelectorAll("[data-pfilter]").forEach((b) => b.classList.toggle("active", b === btn));
  renderPagesTable();
});

els.pagesTable.querySelector("thead").addEventListener("click", (e) => {
  const th = e.target.closest("th[data-sort]");
  if (!th) return;
  const key = th.dataset.sort;
  if (state.pageSort.key === key) {
    state.pageSort.dir = state.pageSort.dir === "asc" ? "desc" : "asc";
  } else {
    state.pageSort = { key, dir: "asc" };
  }
  els.pagesTable.querySelectorAll("th").forEach((h) => h.classList.remove("sorted-asc", "sorted-desc"));
  th.classList.add(state.pageSort.dir === "asc" ? "sorted-asc" : "sorted-desc");
  renderPagesTable();
});

els.pagesTableBody.addEventListener("click", (e) => {
  const tr = e.target.closest("tr[data-page-id]");
  if (tr) openDrawer(parseInt(tr.dataset.pageId, 10));
});

// ---------------------------------------------------------------------------
// Crawl Overview tab
// ---------------------------------------------------------------------------

async function loadCrawlTab() {
  try {
    const stats = await fetchJson(`${API_BASE}/api/crawl/${state.websiteId}`);
    state.tabLoaded.crawl = true;
    renderCrawlStats(stats);
  } catch (err) {
    els.crawlStatGrid.innerHTML = `<div class="rec-empty">Could not load crawl stats: ${escapeHtml(err.message)}</div>`;
  }
}

function statTile(value, label, sub) {
  return `<div class="stat-tile"><div class="stat-value">${value}</div><div class="stat-label">${label}</div>${sub ? `<div class="stat-sub" title="${escapeHtml(sub)}">${escapeHtml(sub)}</div>` : ""}</div>`;
}

function renderCrawlStats(stats) {
  els.crawlStatGrid.innerHTML = [
    statTile(stats.pages_crawled ?? "—", "Pages crawled"),
    statTile(stats.status_2xx ?? 0, "2xx OK"),
    statTile(stats.status_3xx ?? 0, "3xx redirects"),
    statTile(stats.status_4xx ?? 0, "4xx errors"),
    statTile(stats.status_5xx_or_failed ?? 0, "5xx / failed"),
    statTile(`${stats.avg_response_time_ms ?? "—"}ms`, "Avg response time"),
    statTile(`${stats.avg_page_size_kb ?? "—"}KB`, "Avg page size"),
    statTile(stats.max_depth ?? 0, "Max crawl depth"),
  ].join("");

  const total = stats.pages_crawled || 1;
  const statusRows = [
    ["200 OK", stats.status_2xx || 0, "var(--green)"],
    ["3xx Redirect", stats.status_3xx || 0, "var(--amber)"],
    ["4xx Client Error", stats.status_4xx || 0, "var(--red)"],
    ["5xx / Failed", stats.status_5xx_or_failed || 0, "var(--red)"],
  ];
  els.statusDistribution.innerHTML = statusRows.map(([label, count, color]) => `
    <div class="bar-row">
      <span class="bar-label">${label}</span>
      <div class="bar-track"><div class="bar-fill" style="width:${(count / total) * 100}%; background:${color};"></div></div>
      <span class="bar-value">${count}</span>
    </div>`).join("");

  const depths = stats.depth_distribution || {};
  const maxDepthCount = Math.max(1, ...Object.values(depths));
  els.depthDistribution.innerHTML = Object.entries(depths).map(([depth, count]) => `
    <div class="bar-row">
      <span class="bar-label">Depth ${depth}</span>
      <div class="bar-track"><div class="bar-fill" style="width:${(count / maxDepthCount) * 100}%;"></div></div>
      <span class="bar-value">${count}</span>
    </div>`).join("") || '<div class="rec-empty">No depth data.</div>';
}

// ---------------------------------------------------------------------------
// Internal Link Graph tab (circular layout, plain SVG)
// ---------------------------------------------------------------------------

async function loadGraphTab() {
  try {
    const graph = await fetchJson(`${API_BASE}/api/link-graph/${state.websiteId}`);
    state.tabLoaded.graph = true;
    renderLinkGraph(graph);
  } catch (err) {
    els.graphNote.textContent = `Could not load link graph: ${err.message}`;
  }
}

function renderLinkGraph(graph) {
  const { nodes, edges, orphan_count, truncated, total_pages } = graph;
  els.graphNote.textContent = truncated
    ? `Showing the ${nodes.length} most-linked pages of ${total_pages} crawled (graph is capped for readability). ${orphan_count} orphan page(s) detected.`
    : `${nodes.length} page(s), ${edges.length} internal link(s). ${orphan_count} orphan page(s) detected (no inbound internal links from other crawled pages).`;

  const size = 640;
  const center = size / 2;
  const radius = size * 0.38;
  const n = Math.max(nodes.length, 1);

  const positions = {};
  nodes.forEach((node, i) => {
    const angle = (i / n) * Math.PI * 2 - Math.PI / 2;
    positions[node.url] = {
      x: center + Math.cos(angle) * (node.is_root ? 0 : radius),
      y: center + Math.sin(angle) * (node.is_root ? 0 : radius),
    };
  });
  if (nodes.some((nd) => nd.is_root)) {
    // root stays at center; already set via radius 0 above
  }

  const healthColor = { good: "#34D399", warn: "#F5B942", bad: "#FF5C5C" };

  let svg = "";
  edges.forEach((edge) => {
    const a = positions[edge.source];
    const b = positions[edge.target];
    if (!a || !b) return;
    svg += `<line class="graph-edge${edge.is_broken ? " broken" : ""}" x1="${a.x}" y1="${a.y}" x2="${b.x}" y2="${b.y}"></line>`;
  });

  nodes.forEach((node) => {
    const pos = positions[node.url];
    if (!pos) return;
    const r = node.is_root ? 12 : Math.min(6 + node.inbound_links * 1.8, 18);
    const color = node.is_orphan ? "#8B7CF6" : (healthColor[node.health] || "#8B93A9");
    const label = node.url.replace(/^https?:\/\//, "").slice(0, 22);
    svg += `
      <g class="graph-node" data-page-id="${node.page_id}">
        <circle cx="${pos.x}" cy="${pos.y}" r="${r}" fill="${color}" fill-opacity="0.85" stroke="${color}" stroke-width="1.5"></circle>
        <text x="${pos.x}" y="${pos.y + r + 10}" text-anchor="middle">${escapeHtml(label)}</text>
      </g>`;
  });

  els.linkGraphSvg.setAttribute("viewBox", `0 0 ${size} ${size}`);
  els.linkGraphSvg.innerHTML = svg;
}

els.linkGraphSvg.addEventListener("click", (e) => {
  const node = e.target.closest(".graph-node");
  if (node) openDrawer(parseInt(node.dataset.pageId, 10));
});

// ---------------------------------------------------------------------------
// Duplicates tab
// ---------------------------------------------------------------------------

async function loadDuplicatesTab() {
  try {
    const data = await fetchJson(`${API_BASE}/api/duplicates/${state.websiteId}`);
    state.tabLoaded.duplicates = true;
    renderDupGroups(els.dupTitles, data.duplicate_titles);
    renderDupGroups(els.dupDescriptions, data.duplicate_descriptions);
    renderDupGroups(els.dupCanonicals, data.duplicate_canonicals);
    els.similarNote.textContent = data.similarity_method_note || "";
    renderSimilarPairs(data.similar_content_pairs || []);
  } catch (err) {
    els.dupTitles.innerHTML = `<div class="dup-empty">Could not load duplicates: ${escapeHtml(err.message)}</div>`;
  }
}

function urlLinkOrSpan(url) {
  const page = state.pagesList.find((p) => p.page_url === url);
  return page && page.page_id
    ? `<a class="dup-url" data-page-id="${page.page_id}">${escapeHtml(url)}</a>`
    : `<span>${escapeHtml(url)}</span>`;
}

function renderDupGroups(container, groups) {
  if (!groups || !groups.length) {
    container.innerHTML = '<div class="dup-empty">No duplicates found.</div>';
    return;
  }
  container.innerHTML = groups.map((g, idx) => `
    <div class="dup-group">
      <div class="dup-group-value">Group #${idx + 1} · ${g.count} pages<br>"${escapeHtml((g.value || "").slice(0, 120))}"</div>
      <div class="dup-group-urls">${g.urls.map(urlLinkOrSpan).join("")}</div>
    </div>`).join("");
}

function renderSimilarPairs(pairs) {
  if (!pairs.length) {
    els.similarPairs.innerHTML = '<div class="dup-empty">No pages with significant keyword overlap found.</div>';
    return;
  }
  els.similarPairs.innerHTML = pairs.map((p) => `
    <div class="dup-group">
      <div class="dup-group-value">Shared keywords: ${p.shared_keywords.map(escapeHtml).join(", ")}</div>
      <div class="dup-group-urls">${urlLinkOrSpan(p.url_a)}${urlLinkOrSpan(p.url_b)}</div>
    </div>`).join("");
}

document.addEventListener("click", (e) => {
  const link = e.target.closest(".dup-url");
  if (link) openDrawer(parseInt(link.dataset.pageId, 10));
});

// ---------------------------------------------------------------------------
// Sitemap coverage tab
// ---------------------------------------------------------------------------

async function loadSitemapTab() {
  try {
    const data = await fetchJson(`${API_BASE}/api/sitemap/${state.websiteId}`);
    state.tabLoaded.sitemap = true;
    els.sitemapStatGrid.innerHTML = [
      statTile(data.sitemap_url_count, "Sitemap URLs"),
      statTile(data.crawled_url_count, "Crawled URLs"),
      statTile(data.both_count, "In both"),
      statTile(data.sitemap_only_count, "Sitemap only"),
      statTile(data.crawled_only_count, "Crawled only"),
    ].join("");
    els.sitemapCoverageNote.textContent = data.note || "";
    els.sitemapOnlyCount.textContent = data.sitemap_only_count;
    els.crawledOnlyCount.textContent = data.crawled_only_count;
    els.bothCount.textContent = data.both_count;
    els.sitemapOnlyList.innerHTML = data.sitemap_only.map((u) => `<div>${escapeHtml(u)}</div>`).join("") || "<div>None</div>";
    els.crawledOnlyList.innerHTML = data.crawled_only.map((u) => `<div>${escapeHtml(u)}</div>`).join("") || "<div>None</div>";
    els.bothList.innerHTML = data.both.map((u) => `<div>${escapeHtml(u)}</div>`).join("") || "<div>None</div>";
  } catch (err) {
    els.sitemapStatGrid.innerHTML = `<div class="rec-empty">Could not load sitemap coverage: ${escapeHtml(err.message)}</div>`;
  }
}

// ---------------------------------------------------------------------------
// robots.txt inspector tab
// ---------------------------------------------------------------------------

async function loadRobotsTab() {
  try {
    const data = await fetchJson(`${API_BASE}/api/robots/${state.websiteId}`);
    state.tabLoaded.robots = true;
    els.robotsScopeNote.textContent = data.scope_note || "";
    els.robotsInspectorHead.innerHTML = `
      <span class="status-indicator ${data.exists ? "on" : "off"}"></span>
      <span class="status-head-label">${data.exists ? "robots.txt found" : "robots.txt not found"}</span>`;
    els.robotsInspectorTable.innerHTML = `
      <tr><td>Rule count</td><td>${data.rule_count ?? 0}</td></tr>
      <tr><td>Sitemap referenced</td><td>${data.sitemap_reference ? "Yes — " + escapeHtml(data.sitemap_reference) : "No"}</td></tr>
      <tr><td>User-agent groups</td><td>${(data.user_agent_groups || []).length}</td></tr>`;

    const groups = data.user_agent_groups || [];
    els.uaGroups.innerHTML = groups.length ? groups.map((g) => `
      <div class="ua-group">
        <div class="ua-group-agent">User-agent: ${escapeHtml(g.user_agent)}</div>
        ${g.disallow.map((r) => `<div class="ua-rule disallow">Disallow: ${escapeHtml(r)}</div>`).join("")}
        ${g.allow.map((r) => `<div class="ua-rule allow">Allow: ${escapeHtml(r)}</div>`).join("")}
      </div>`).join("") : '<div class="dup-empty">No user-agent groups parsed.</div>';

    const blocked = data.blocked_crawled_pages || [];
    els.robotsBlockedPanel.hidden = blocked.length === 0;
    els.robotsBlockedList.innerHTML = blocked.map(urlLinkOrSpan).join("");
  } catch (err) {
    els.robotsInspectorTable.innerHTML = `<tr><td colspan="2">Could not load robots.txt data: ${escapeHtml(err.message)}</td></tr>`;
  }
}

document.addEventListener("click", (e) => {
  const link = e.target.closest("#robotsBlockedList .dup-url");
  if (link) openDrawer(parseInt(link.dataset.pageId, 10));
});

// ---------------------------------------------------------------------------
// Performance tab
// ---------------------------------------------------------------------------

async function loadPerformanceTab() {
  try {
    const data = await fetchJson(`${API_BASE}/api/performance/${state.websiteId}`);
    state.tabLoaded.performance = true;
    els.perfStatGrid.innerHTML = [
      statTile(`${data.avg_response_time_ms}ms`, "Avg response time"),
      statTile(`${data.avg_page_size_kb}KB`, "Avg page size"),
      statTile(data.fastest_page ? `${data.fastest_page.response_time_ms}ms` : "—", "Fastest page", data.fastest_page ? data.fastest_page.url : ""),
      statTile(data.slowest_page ? `${data.slowest_page.response_time_ms}ms` : "—", "Slowest page", data.slowest_page ? data.slowest_page.url : ""),
      statTile(data.largest_page ? `${data.largest_page.page_size_kb}KB` : "—", "Largest page", data.largest_page ? data.largest_page.url : ""),
    ].join("");
    els.perfSlowThreshold.textContent = data.response_threshold_ms;
    els.perfLargeThreshold.textContent = data.size_threshold_kb;
    els.perfSlowList.innerHTML = data.pages_above_response_threshold.map((p) =>
      `<div data-page-id="${p.page_id}">${escapeHtml(p.url)} — ${p.response_time_ms}ms</div>`).join("") || "<div>None above threshold.</div>";
    els.perfLargeList.innerHTML = data.pages_above_size_threshold.map((p) =>
      `<div data-page-id="${p.page_id}">${escapeHtml(p.url)} — ${p.page_size_kb}KB</div>`).join("") || "<div>None above threshold.</div>";
  } catch (err) {
    els.perfStatGrid.innerHTML = `<div class="rec-empty">Could not load performance data: ${escapeHtml(err.message)}</div>`;
  }
}

document.addEventListener("click", (e) => {
  const row = e.target.closest("#perfSlowList div[data-page-id], #perfLargeList div[data-page-id]");
  if (row) openDrawer(parseInt(row.dataset.pageId, 10));
});

// ---------------------------------------------------------------------------
// Compare tab
// ---------------------------------------------------------------------------

async function loadCompareTab() {
  try {
    const history = await fetchJson(`${API_BASE}/api/history`);
    const options = history.map((h) =>
      `<option value="${h.website_id}">${escapeHtml(h.domain_name)} — ${h.overall_score != null ? Math.round(h.overall_score) : "—"}/100 — ${new Date(h.scan_date).toLocaleString()}</option>`
    ).join("");
    els.comparePrev.innerHTML = options;
    els.compareCurr.innerHTML = options;
    if (history.length >= 2) {
      els.comparePrev.selectedIndex = 1;
      els.compareCurr.selectedIndex = 0;
    }
  } catch (err) {
    els.compareResults.innerHTML = `<div class="rec-empty">Could not load scan history: ${escapeHtml(err.message)}</div>`;
  }
}

els.compareBtn.addEventListener("click", async () => {
  const idPrev = els.comparePrev.value;
  const idCurr = els.compareCurr.value;
  if (!idPrev || !idCurr) return;
  if (idPrev === idCurr) {
    els.compareResults.innerHTML = '<div class="rec-empty">Choose two different scans to compare.</div>';
    return;
  }
  els.compareResults.innerHTML = '<div class="rec-empty">Comparing…</div>';
  try {
    const data = await fetchJson(`${API_BASE}/api/compare/${idPrev}/${idCurr}`);
    renderCompare(data);
  } catch (err) {
    els.compareResults.innerHTML = `<div class="rec-empty">Could not compare: ${escapeHtml(err.message)}</div>`;
  }
});

function renderCompare(data) {
  const delta = data.overall_score_delta;
  const deltaClass = delta > 0 ? "delta-pos" : delta < 0 ? "delta-neg" : "";
  const deltaSign = delta > 0 ? "+" : "";

  let html = `<div class="compare-score-row">
    <div class="compare-score-card"><div class="csc-label">Previous</div><div class="csc-value">${data.previous.overall_score ?? "—"}</div></div>
    <div class="compare-score-card"><div class="csc-label">Current</div><div class="csc-value">${data.current.overall_score ?? "—"}</div></div>
    <div class="compare-score-card ${deltaClass}"><div class="csc-label">Change</div><div class="csc-value">${deltaSign}${delta}</div></div>
  </div>`;

  html += '<div class="compare-section-title">Category Score Changes</div>';
  html += Object.entries(data.category_deltas).map(([label, d]) => {
    const dClass = d.delta > 0 ? "delta-pos" : d.delta < 0 ? "delta-neg" : "";
    const sign = d.delta > 0 ? "+" : "";
    return `<div class="compare-issue-row"><span>${escapeHtml(label)}</span><span class="${dClass}">${d.previous} → ${d.current} (<b>${sign}${d.delta}</b>)</span></div>`;
  }).join("");

  const issueSection = (title, issues, colorVar) => {
    if (!issues.length) return `<div class="compare-section-title">${title} (0)</div>`;
    return `<div class="compare-section-title">${title} (${issues.length})</div>` + issues.slice(0, 30).map((i) => `
      <div class="compare-issue-row">
        <span class="sev" style="color:${SEVERITY_COLORS[i.severity] || "var(--text-dim)"}">${i.severity}</span>
        <span>${escapeHtml(i.title)}${i.affected_url ? " — " + escapeHtml(i.affected_url) : ""}</span>
      </div>`).join("");
  };

  html += issueSection("New Issues", data.new_issues);
  html += issueSection("Fixed Issues", data.fixed_issues);
  html += issueSection("Unchanged Issues", data.unchanged_issues);

  els.compareResults.innerHTML = html;
}

// ---------------------------------------------------------------------------
// Page Details drawer
// ---------------------------------------------------------------------------

async function openDrawer(pageId) {
  if (!pageId || !state.websiteId) return;
  els.drawerOverlay.hidden = false;
  els.pageDrawer.hidden = false;
  els.pageDrawer.setAttribute("aria-hidden", "false");
  els.drawerTitle.textContent = "Loading…";
  els.drawerBody.innerHTML = '<div class="rec-empty">Loading page details…</div>';

  try {
    const data = await fetchJson(`${API_BASE}/api/page/${state.websiteId}/${pageId}`);
    renderDrawer(data.page, data.issues);
  } catch (err) {
    els.drawerBody.innerHTML = `<div class="rec-empty">Could not load page: ${escapeHtml(err.message)}</div>`;
  }
}

function closeDrawer() {
  els.drawerOverlay.hidden = true;
  els.pageDrawer.hidden = true;
  els.pageDrawer.setAttribute("aria-hidden", "true");
}

function drawerRow(label, value) {
  return `<div class="drawer-row"><span>${label}</span><strong>${value}</strong></div>`;
}

function renderDrawer(p, issues) {
  els.drawerTitle.textContent = p.page_url;

  const keywordChips = (p.top_keywords || []).slice(0, 8)
    .map((kw) => `<span class="keyword-chip">${escapeHtml(kw.keyword)} <b>${kw.count}</b></span>`).join("") || '<span class="keyword-empty">No keyword data.</span>';

  const issuesHtml = issues.length
    ? issues.map((i) => `
        <div class="rec-card" style="--rec-color:${SEVERITY_COLORS[i.severity] || "#8B93A9"}">
          <div class="rec-icon">${CATEGORY_ICONS[i.category] || PRIORITY_WARN_ICON}</div>
          <div class="rec-body">
            <div class="rec-top"><span class="rec-priority">${i.severity}</span><span class="rec-title">${escapeHtml(i.title)}</span></div>
            <div class="rec-desc">${escapeHtml(i.description)}</div>
          </div>
        </div>`).join("")
    : '<div class="rec-empty">No issues found on this page.</div>';

  els.drawerBody.innerHTML = `
    <div class="drawer-section">
      <h3>Page Overview</h3>
      ${drawerRow("HTTP status", statusBadgeHtml(p.status_code))}
      ${drawerRow("HTTPS", p.is_https ? '<span class="badge ok">yes</span>' : '<span class="badge bad">no</span>')}
      ${drawerRow("Indexable", p.is_indexable ? '<span class="badge ok">yes</span>' : '<span class="badge bad">no</span>')}
      ${drawerRow("Crawl depth", p.crawl_depth ?? "—")}
      ${drawerRow("Response time", p.response_time_ms != null ? p.response_time_ms + "ms" : "—")}
      ${drawerRow("Page size", p.page_size_kb != null ? p.page_size_kb + "KB" : "—")}
      ${drawerRow("Redirects", p.redirect_count || 0)}
    </div>

    <div class="drawer-section">
      <h3>Metadata</h3>
      ${drawerRow("Title", escapeHtml(p.title || "—"))}
      ${drawerRow("Title length", (p.title || "").length)}
      ${drawerRow("Meta description", escapeHtml(p.meta_description || "—"))}
      ${drawerRow("Description length", (p.meta_description || "").length)}
      ${drawerRow("Meta robots", escapeHtml(p.meta_robots || "—"))}
      ${drawerRow("Canonical", escapeHtml(p.canonical_url || "—"))}
    </div>

    <div class="drawer-section">
      <h3>Headings</h3>
      ${drawerRow("H1 count", p.h1_count)}
      ${drawerRow("H2 count", p.h2_count)}
    </div>

    <div class="drawer-section">
      <h3>Content</h3>
      ${drawerRow("Word count", p.word_count)}
      ${drawerRow("Thin content", (p.word_count || 0) < 300 ? '<span class="badge warn">yes</span>' : '<span class="badge ok">no</span>')}
      <div class="drawer-keyword-chips">${keywordChips}</div>
    </div>

    <div class="drawer-section">
      <h3>Links</h3>
      ${drawerRow("Internal links", p.internal_links)}
      ${drawerRow("External links", p.external_links)}
      ${drawerRow("Broken links", p.broken_links)}
    </div>

    <div class="drawer-section">
      <h3>Images</h3>
      ${drawerRow("Image count", p.image_count)}
      ${drawerRow("Missing ALT", p.images_missing_alt)}
      ${drawerRow("Missing dimensions", p.images_missing_dimensions)}
      ${drawerRow("Non-descriptive filenames", p.non_descriptive_images)}
    </div>

    <div class="drawer-section">
      <h3>Technical SEO</h3>
      ${drawerRow("Viewport tag", p.has_viewport ? '<span class="badge ok">yes</span>' : '<span class="badge bad">no</span>')}
      ${drawerRow("Language declared", escapeHtml(p.html_lang || "—"))}
      ${drawerRow("Structured data", p.has_structured_data ? '<span class="badge ok">yes</span>' : '<span class="badge warn">no</span>')}
      ${drawerRow("Open Graph", p.has_open_graph ? '<span class="badge ok">yes</span>' : '<span class="badge warn">no</span>')}
      ${drawerRow("Twitter Card", p.has_twitter_card ? '<span class="badge ok">yes</span>' : '<span class="badge warn">no</span>')}
    </div>

    <div class="drawer-section">
      <h3>Issues on this page (${issues.length})</h3>
      <div class="rec-list">${issuesHtml}</div>
    </div>
  `;
}

els.drawerClose.addEventListener("click", closeDrawer);
els.drawerOverlay.addEventListener("click", closeDrawer);
document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeDrawer(); });

// ---------------------------------------------------------------------------
// History panel + reload of a past scan
// ---------------------------------------------------------------------------

async function loadHistory() {
  els.historyList.innerHTML = "";
  try {
    const history = await fetchJson(`${API_BASE}/api/history`);
    if (!history.length) {
      els.historyList.innerHTML = '<div class="history-empty">No scans yet. Run your first audit above.</div>';
      return;
    }
    history.forEach((item) => {
      const div = document.createElement("div");
      div.className = "history-item";
      const color = HEALTH_COLORS[item.health_level] || "#2FE0C4";
      const scoreLabel = item.overall_score != null ? Math.round(item.overall_score) : "—";
      div.innerHTML = `
        <div class="history-ring" style="border-color:${color}; color:${color};">${scoreLabel}</div>
        <div class="history-text">
          <div class="h-domain">${escapeHtml(item.domain_name)}</div>
          <div class="h-meta">${item.pages_scanned} pages · ${new Date(item.scan_date).toLocaleDateString()}</div>
        </div>`;
      div.addEventListener("click", () => loadReportById(item.website_id));
      els.historyList.appendChild(div);
    });
  } catch (err) {
    els.historyList.innerHTML = '<div class="history-empty">Could not load scan history.</div>';
  }
}

async function loadReportById(websiteId) {
  try {
    const bundle = await fetchJson(`${API_BASE}/api/report/${websiteId}`);
    if (!bundle.website || !bundle.report) return;

    const scores = {
      overall_score: bundle.report.overall_score,
      health_level: bundle.report.health_level,
      metadata_score: bundle.report.metadata_score,
      technical_score: bundle.report.technical_score,
      images_score: bundle.report.images_score,
      links_score: bundle.report.links_score,
      sitemap_score: bundle.report.sitemap_score,
      robots_score: bundle.report.robots_score,
      performance_score: bundle.report.performance_score,
      max_scores: { metadata: 20, technical: 20, images: 15, links: 15, sitemap: 10, robots: 10, performance: 10 },
    };

    renderResults({
      website_id: bundle.website.website_id,
      root_url: bundle.website.root_url,
      domain: bundle.website.domain_name,
      pages_scanned: bundle.pages.length,
      scores,
      pages: bundle.pages,
      recommendations: bundle.report.recommendations || [],
      site_keywords: bundle.report.keywords || [],
      advanced_checks: bundle.report.advanced_checks || {},
      issue_count: null,
      issues_summary: null,
    });

    els.results.scrollIntoView({ behavior: "smooth" });
  } catch (err) {
    console.error(err);
  }
}

// ---------------------------------------------------------------------------
// Global bindings
// ---------------------------------------------------------------------------

els.runBtn.addEventListener("click", runScan);
els.urlInput.addEventListener("keydown", (e) => { if (e.key === "Enter") runScan(); });

els.historyToggle.addEventListener("click", () => {
  const isHidden = els.historyPanel.hidden;
  els.historyPanel.hidden = !isHidden;
  if (isHidden) {
    loadHistory();
    els.historyPanel.scrollIntoView({ behavior: "smooth" });
  }
});

els.recFilter.addEventListener("click", (e) => {
  const btn = e.target.closest(".rec-filter-btn");
  if (!btn) return;
  currentRecFilter = btn.dataset.filter;
  els.recFilter.querySelectorAll(".rec-filter-btn").forEach((b) => b.classList.toggle("active", b === btn));
  renderRecommendations(currentRecommendations, currentRecFilter);
});
