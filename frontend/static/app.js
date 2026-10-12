/* ==========================================================================
   CivicAgent — Humanoid Civic Intelligence Platform (Frontend Application)
   ========================================================================== */

// ── Agent Definitions ─────────────────────────────────────────────────────
const AGENT_DEFS = [
  { name: "Vision & Evidence Agent",         desc: "Photometric defect & severity audit",      icon: "VI" },
  { name: "Research & Jurisdiction Agent",   desc: "Ward & statutory authority assignment",    icon: "RE" },
  { name: "Safety & Public Impact Agent",    desc: "Hazard exposure & urgency calculation",    icon: "SA" },
  { name: "Multi-Agent Deliberation",        desc: "Adversarial debate & civic consensus",     icon: "DB" },
  { name: "Statutory Decision Agent",        desc: "Priority scoring & resolution SLA",        icon: "DE" },
  { name: "Action & Dispatch Agent",         desc: "Formal complaint drafting & dispatch",     icon: "AC" },
];

// ── Global State ──────────────────────────────────────────────────────────
const state = {
  cases:         [],
  currentFilter: "ALL",
  searchQuery:   "",
  currentResult: null,
};

// ── Utilities ─────────────────────────────────────────────────────────────
function $ (id) { return document.getElementById(id); }

function escapeHtml(s) {
  return String(s || "").replace(/[&<>"']/g, m => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
  }[m]));
}

function formatDate(ts) {
  if (!ts) return "—";
  const d = new Date(ts * 1000);
  return d.toLocaleDateString("en-IN", {
    day: "2-digit", month: "short", year: "numeric",
    hour: "2-digit", minute: "2-digit"
  });
}

function showToast(msg, type = "success", duration = 3200) {
  const el = $("toast");
  if (!el) return;
  el.textContent = msg;
  el.className = `toast ${type}`;
  el.classList.remove("hidden");
  clearTimeout(el._timer);
  el._timer = setTimeout(() => el.classList.add("hidden"), duration);
}

// ── Page Navigation ───────────────────────────────────────────────────────
function showPage(page) {
  document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));
  document.querySelectorAll(".nav-item").forEach(a => a.classList.remove("active"));

  const target = $(`page-${page}`);
  if (target) target.classList.add("active");

  const navLink = document.querySelector(`[data-page="${page}"]`);
  if (navLink) navLink.classList.add("active");

  // Lazy render on page switch
  if (page === "overview")  renderOverview();
  if (page === "network")   renderNetworkPage();
  if (page === "cases")     renderCasesPage();
  if (page === "analytics") loadAnalytics();

  // Close mobile navigation drawer if open
  $("sidebar")?.classList.remove("open");
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function toggleSidebar() {
  $("sidebar")?.classList.toggle("open");
}

// ── Health Check ──────────────────────────────────────────────────────────
async function checkHealth() {
  try {
    const r = await fetch("/api/health");
    if (!r.ok) return;
    const d = await r.json();

    const badge = $("aiBadge");
    const txt   = $("aiStatusText");

    if (badge && txt) {
      if (d.ai_configured) {
        txt.textContent = `Live AI · ${d.model || "gpt-4.1-mini"}`;
      } else {
        txt.textContent = "Civic Engine Active";
      }
    }

    const statAiMode = $("statAiMode");
    if (statAiMode) {
      statAiMode.textContent = d.ai_configured ? "LIVE AI" : "CIVIC ENGINE";
    }

    const archModeTitle = $("archModeTitle");
    const archModeDesc  = $("archModeDesc");
    if (archModeTitle) {
      archModeTitle.textContent = d.ai_configured ? "Live Multi-Agent LLM Engine" : "Autonomous Civic Intelligence Engine";
      if (archModeDesc) {
        archModeDesc.textContent = d.ai_configured
          ? `Operating on ${d.model}. Real-time generation across all 6 specialized agents.`
          : "Deterministic civic reasoning rules active. Provides instant statutory routing and complaint drafting without external latency.";
      }
    }

    const mobileStatus = $("mobileStatus");
    if (mobileStatus) {
      mobileStatus.textContent = d.ai_configured ? "LIVE AI" : "ENGINE ACTIVE";
    }
  } catch (err) {
    console.warn("Health check unreachable:", err);
  }
}

// ── Load Cases ────────────────────────────────────────────────────────────
async function loadCases() {
  try {
    const r = await fetch("/api/cases");
    if (!r.ok) return;
    const d = await r.json();
    state.cases = Array.isArray(d) ? d : (d.cases || []);
    updateStats();
  } catch (err) {
    console.warn("Failed to load cases:", err);
  }
}

function updateStats() {
  const cases = state.cases || [];
  if ($("statTotal")) $("statTotal").textContent = cases.length;

  const criticalCount = cases.filter(c => ((c.decision?.priority || "").toUpperCase() === "CRITICAL")).length;
  if ($("statCritical")) $("statCritical").textContent = criticalCount;

  const scores = cases
    .map(c => c.decision?.priority_score_0_to_100)
    .filter(s => typeof s === "number" && !isNaN(s));

  if ($("statAvgScore")) {
    $("statAvgScore").textContent = scores.length
      ? Math.round(scores.reduce((a, b) => a + b, 0) / scores.length) + "/100"
      : "—";
  }
}

// ── Overview Page ─────────────────────────────────────────────────────────
function renderOverview() {
  updateStats();
  renderRecentCases();
  renderAgentNetworkOverview();
}

function renderRecentCases() {
  const el = $("recentCases");
  if (!el) return;

  const recent = [...state.cases].reverse().slice(0, 5);
  if (!recent.length) {
    el.innerHTML = `<div class="empty-state-sm">No recorded cases. File the first grievance.</div>`;
    return;
  }

  el.innerHTML = recent.map(c => {
    const p = (c.decision?.priority || "MEDIUM").toUpperCase();
    return `
      <div class="recent-case-item" onclick="openCaseModal('${c.case_id}')">
        <div>
          <div class="rc-id">${escapeHtml(c.case_id)}</div>
          <div class="rc-desc">${escapeHtml(c.description || "Civic infrastructure issue")}</div>
        </div>
        <span class="rc-priority ${p}">${p}</span>
      </div>
    `;
  }).join("");
}

function renderAgentNetworkOverview() {
  const el = $("agentNetworkOverview");
  if (!el) return;

  el.innerHTML = AGENT_DEFS.map(a => `
    <div class="agent-row">
      <div class="agent-avatar">${a.icon}</div>
      <div>
        <b>${escapeHtml(a.name)}</b>
        <small>${escapeHtml(a.desc)}</small>
      </div>
      <span class="agent-row-state badge-green">READY</span>
    </div>
  `).join("");
}

// ── Report Issue Form Handling ────────────────────────────────────────────
function initReportForm() {
  renderPipelineAgents({});

  const desc = $("description");
  if (desc) {
    desc.addEventListener("input", function() {
      if ($("charCount")) $("charCount").textContent = this.value.length;
    });
  }

  const drop = $("fileDrop");
  if (drop) {
    drop.addEventListener("dragover", e => {
      e.preventDefault();
      drop.style.background = "var(--card-bg-hover)";
    });
    drop.addEventListener("dragleave", () => {
      drop.style.background = "";
    });
    drop.addEventListener("drop", e => {
      e.preventDefault();
      drop.style.background = "";
      const files = e.dataTransfer?.files;
      if (files?.[0]) {
        const dt = new DataTransfer();
        dt.items.add(files[0]);
        const imgInput = $("image");
        if (imgInput) {
          imgInput.files = dt.files;
          handleFileSelect(imgInput);
        }
      }
    });
  }
}

function handleFileSelect(input) {
  const file = input.files?.[0];
  if (!file) return;

  if (file.size > 10 * 1024 * 1024) {
    showToast("Photographic evidence must be under 10MB", "error");
    input.value = "";
    return;
  }

  const reader = new FileReader();
  reader.onload = e => {
    $("imagePreview").src = e.target.result;
    $("imagePreviewContainer").classList.remove("hidden");
    $("fileDropContent").classList.add("hidden");
    $("fileDrop").style.display = "none";
  };
  reader.readAsDataURL(file);
}

function removeImage() {
  $("image").value = "";
  $("imagePreviewContainer").classList.add("hidden");
  $("fileDropContent").classList.remove("hidden");
  $("fileDrop").style.display = "";
}

function renderPipelineAgents(states) {
  const el = $("agentPipeline");
  if (!el) return;

  el.innerHTML = AGENT_DEFS.map(a => {
    const s = states[a.name] || "standby";
    const cls = s === "RUNNING" ? "running" : s === "DONE" ? "done" : s === "ERROR" ? "error" : "";
    const stateLabel = s === "RUNNING" ? "Executing..." : s === "DONE" ? "Complete" : s === "ERROR" ? "Failed" : "Standby";

    return `
      <div class="pipeline-agent ${cls}">
        <div class="pip-av ${cls}">${a.icon}</div>
        <div>
          <div class="pip-name">${escapeHtml(a.name)}</div>
          <div class="pip-desc">${escapeHtml(a.desc)}</div>
        </div>
        <div class="pip-state ${cls}">${stateLabel}</div>
      </div>
    `;
  }).join("");
}

function setAllAgentStates(s) {
  const states = {};
  AGENT_DEFS.forEach(a => states[a.name] = s);
  renderPipelineAgents(states);
}

// Form Submission Event
$("reportForm")?.addEventListener("submit", async e => {
  e.preventDefault();

  const descVal = $("description").value.trim();
  if (!descVal) {
    showToast("Please enter an issue description", "error");
    return;
  }

  const btn = $("analyzeBtn");
  btn.disabled = true;
  $("btnText").classList.add("hidden");
  $("btnSpinner").classList.remove("hidden");
  $("pipelineStatus").className = "badge-yellow";
  $("pipelineStatus").textContent = "INVESTIGATING";
  $("resultSection")?.classList.add("hidden");

  // Step-by-step pipeline animation
  let agentIdx = 0;
  const animInterval = setInterval(() => {
    if (agentIdx < AGENT_DEFS.length) {
      const states = {};
      AGENT_DEFS.forEach((a, i) => {
        states[a.name] = i < agentIdx ? "DONE" : i === agentIdx ? "RUNNING" : "standby";
      });
      renderPipelineAgents(states);
      agentIdx++;
    } else {
      clearInterval(animInterval);
    }
  }, 450);

  const fd = new FormData();
  fd.append("description", descVal);
  fd.append("location", $("location").value.trim());

  const file = $("image").files[0];
  if (file) fd.append("image", file);

  try {
    const r = await fetch("/api/analyze", { method: "POST", body: fd });
    const data = await r.json();
    clearInterval(animInterval);

    if (!r.ok || data.error) {
      throw new Error(data.error || "Analysis pipeline failed");
    }

    setAllAgentStates("DONE");
    $("pipelineStatus").className = "badge-green";
    $("pipelineStatus").textContent = "COMPLETE";
    if ($("networkBadge")) {
      $("networkBadge").textContent = "COMPLETE";
      $("networkBadge").className = "badge-green";
    }

    state.currentResult = data;
    renderResult(data);
    await loadCases();
    renderOverview();
    showToast(`Case ${data.case_id} recorded successfully`, "success");

    setTimeout(() => {
      $("resultSection")?.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 250);

  } catch (err) {
    clearInterval(animInterval);
    setAllAgentStates("ERROR");
    $("pipelineStatus").className = "badge-red";
    $("pipelineStatus").textContent = "ERROR";
    showToast(err.message, "error", 5000);
  } finally {
    btn.disabled = false;
    $("btnText").classList.remove("hidden");
    $("btnSpinner").classList.add("hidden");
  }
});

// ── Render Investigation Result ───────────────────────────────────────────
function renderResult(d) {
  const resultSec = $("resultSection");
  if (!resultSec) return;
  resultSec.classList.remove("hidden");

  // Header & Status
  $("caseId").textContent = d.case_id || "CA-RECORD";
  $("resultTimestamp").textContent = formatDate(d.timestamp);
  $("resultAiMode").textContent = d.ai_mode ? "AI VERIFIED" : "ENGINE VERIFIED";

  const dec = d.decision || {};
  const priority = (dec.priority || "HIGH").toUpperCase();
  const pb = $("priorityBadge");
  pb.textContent = priority;
  pb.className = `priority-badge ${priority}`;

  // Metrics
  const score = dec.priority_score_0_to_100 ?? 75;
  const conf  = dec.confidence_0_to_1 ?? 0.85;

  $("metScore").textContent     = score + "/100";
  $("metAuthority").textContent  = dec.authority || "Municipal Corporation";
  $("metDepartment").textContent = dec.department || "Public Works";
  $("metConfidence").textContent = Math.round(conf * 100) + "%";
  $("metSLA").textContent        = dec.recommended_sla || "24-48 hours";

  setTimeout(() => {
    if ($("scoreBar")) $("scoreBar").style.width = `${Math.min(100, score)}%`;
    if ($("confBar"))  $("confBar").style.width  = `${Math.min(100, Math.round(conf * 100))}%`;
  }, 80);

  renderIntelligenceTab(d);
  renderDebateTab(d);
  renderActionTab(d);
  renderComplaintTab(d);

  // Switch to primary tab
  switchTab("intelligence", document.querySelector(".tab-btn"));
}

function renderIntelligenceTab(d) {
  const a = d.agents || {};
  const cards = [
    {
      name: "Vision & Evidence Agent",
      badge: "VI",
      fields: [
        { label: "Detected Issue", val: a.vision?.issue },
        { label: "Defect Class",   val: a.vision?.category },
        { label: "Audit Severity", val: a.vision?.severity_1_to_10 ? `${a.vision.severity_1_to_10} / 10` : null },
        { label: "Confidence",     val: a.vision?.confidence_0_to_1 ? `${Math.round(a.vision.confidence_0_to_1 * 100)}%` : null },
      ],
      reasoning: a.vision?.reasoning,
      tags: a.vision?.objects_detected || [],
    },
    {
      name: "Research & Jurisdiction Agent",
      badge: "RE",
      fields: [
        { label: "Statutory Authority", val: a.research?.authority },
        { label: "Assigned Division",   val: a.research?.department },
        { label: "Service Category",    val: a.research?.service_category },
        { label: "Escalation Officer",  val: a.research?.suggested_escalation },
      ],
      reasoning: a.research?.reasoning,
      tags: [],
    },
    {
      name: "Safety & Public Impact Agent",
      badge: "SA",
      fields: [
        { label: "Hazard Classification", val: a.safety?.risk_level },
        { label: "Public Hazard Index",   val: a.safety?.risk_score_0_to_100 ? `${a.safety.risk_score_0_to_100} / 100` : null },
        { label: "Statutory Urgency",     val: a.safety?.urgency },
        { label: "Audit Confidence",      val: a.safety?.confidence_0_to_1 ? `${Math.round(a.safety.confidence_0_to_1 * 100)}%` : null },
      ],
      reasoning: a.safety?.reasoning,
      tags: a.safety?.affected_groups || [],
    },
    {
      name: "Statutory Decision Agent",
      badge: "DE",
      fields: [
        { label: "Priority Level",      val: a.decision?.priority },
        { label: "Composite Score",     val: a.decision?.priority_score_0_to_100 ? `${a.decision.priority_score_0_to_100} / 100` : null },
        { label: "Enforcing Authority", val: a.decision?.authority },
        { label: "Statutory SLA",       val: a.decision?.recommended_sla },
      ],
      reasoning: a.decision?.rationale,
      tags: [],
    },
  ];

  $("intelGrid").innerHTML = cards.map(c => `
    <div class="intel-card">
      <div class="intel-card-head">
        <b>${escapeHtml(c.name)}</b>
        <span class="intel-badge badge-muted">${c.badge}</span>
      </div>
      ${c.fields.filter(f => f.val).map(f => `
        <div style="margin-bottom:8px">
          <div class="metric-label">${escapeHtml(f.label)}</div>
          <div style="font-size:13px;font-weight:600;color:var(--ink-primary)">${escapeHtml(String(f.val))}</div>
        </div>
      `).join("")}
      ${c.reasoning ? `<div class="intel-reasoning">${escapeHtml(c.reasoning)}</div>` : ""}
      ${c.tags.length ? `<div class="intel-tags">${c.tags.map(t => `<span class="intel-tag">${escapeHtml(t)}</span>`).join("")}</div>` : ""}
    </div>
  `).join("");
}

function renderDebateTab(d) {
  const db = d.debate || {};
  const conf = db.debate_confidence_0_to_1;

  $("debateCards").innerHTML = `
    <div class="debate-card">
      <div class="debate-card-label">Position A · Immediate Mitigation</div>
      <p>${escapeHtml(db.position_a || "Prioritize rapid temporary site barricading and emergency patching to remove public hazard exposure immediately.")}</p>
    </div>
    <div class="debate-card">
      <div class="debate-card-label">Position B · Structural Repair</div>
      <p>${escapeHtml(db.position_b || "Advocate thorough engineering inspection and drainage rectification to prevent recurring infrastructure failure.")}</p>
    </div>
    <div class="debate-card">
      <div class="debate-card-label">Deliberated Consensus</div>
      <p>${escapeHtml(db.consensus || "Execute rapid emergency rectification within SLA window, followed by ward engineering structural audit.")}</p>
      ${conf ? `<div style="margin-top:12px;font-size:11.5px;color:var(--ink-muted)">Consensus Confidence: <b>${Math.round(conf * 100)}%</b></div>` : ""}
    </div>
  `;

  if (db.unresolved_questions?.length) {
    $("debateCards").innerHTML += `
      <div class="debate-card" style="grid-column: 1 / -1;">
        <div class="debate-card-label">Unresolved Jurisdictional Inquiries</div>
        <ul style="list-style:disc;padding-left:18px;margin-top:6px">
          ${db.unresolved_questions.map(q => `
            <li style="font-size:12.5px;color:var(--ink-secondary);margin-bottom:5px">${escapeHtml(q)}</li>
          `).join("")}
        </ul>
      </div>
    `;
  }
}

function renderActionTab(d) {
  const ac = d.action || {};
  const steps = ac.action_steps || [];

  $("actionSteps").innerHTML = `
    <ol class="step-list">
      ${steps.map((s, i) => `
        <li class="step-item">
          <div class="step-num">${i + 1}</div>
          <div class="step-text">${escapeHtml(s)}</div>
        </li>
      `).join("")}
    </ol>
    ${ac.follow_up ? `
      <div style="margin-top:16px;padding:16px;background:var(--card-bg);border-radius:var(--radius-md);box-shadow:var(--shadow-card);font-size:13px;color:var(--ink-secondary)">
        <b style="color:var(--ink-primary)">Administrative Escalation Protocol:</b> ${escapeHtml(ac.follow_up)}
      </div>
    ` : ""}
  `;
}

function renderComplaintTab(d) {
  const ac = d.action || {};

  $("complaintView").innerHTML = `
    <div class="complaint-block">
      <div class="complaint-block-label">Formal Administrative Grievance Memorandum</div>
      <h4>${escapeHtml(ac.complaint_subject || "Formal Civic Complaint")}</h4>
      <p>${escapeHtml(ac.complaint_body || "—")}</p>
    </div>
    ${ac.evidence_checklist?.length ? `
      <div class="complaint-block">
        <div class="complaint-block-label">Statutory Evidence Checklist</div>
        <ul class="checklist">
          ${ac.evidence_checklist.map(item => `<li>${escapeHtml(item)}</li>`).join("")}
        </ul>
      </div>
    ` : ""}
    ${ac.citizen_message ? `
      <div class="citizen-msg">
        <b style="color:var(--ink-primary);display:block;margin-bottom:4px">Citizen Advisory &amp; Tracking Notice:</b>
        ${escapeHtml(ac.citizen_message)}
      </div>
    ` : ""}
  `;
}

// ── Tab Switching ─────────────────────────────────────────────────────────
function switchTab(name, btn) {
  document.querySelectorAll(".tab-content").forEach(t => t.classList.remove("active"));
  document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));

  $(`tab-${name}`)?.classList.add("active");
  if (btn) btn.classList.add("active");
}

// ── Export Case Record ────────────────────────────────────────────────────
function exportCase() {
  if (!state.currentResult) return;
  const json = JSON.stringify(state.currentResult, null, 2);
  const blob = new Blob([json], { type: "application/json" });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement("a");
  a.href = url;
  a.download = `${state.currentResult.case_id || "CivicCase"}.json`;
  a.click();
  URL.revokeObjectURL(url);
  showToast("Dossier exported as JSON", "success");
}

// ── Agent Pipeline Page ───────────────────────────────────────────────────
function renderNetworkPage() {
  const el = $("liveAgentList");
  if (!el) return;

  el.innerHTML = AGENT_DEFS.map(a => `
    <div class="agent-row">
      <div class="agent-avatar">${a.icon}</div>
      <div>
        <b>${escapeHtml(a.name)}</b>
        <small>${escapeHtml(a.desc)}</small>
      </div>
      <span class="badge-green" style="margin-left:auto">ACTIVE</span>
    </div>
  `).join("");
}

// ── Cases Page (Registry) ─────────────────────────────────────────────────
function renderCasesPage() {
  filterCases(state.searchQuery);
}

function filterCases(query) {
  state.searchQuery = (query || "").toLowerCase();
  renderCasesGrid();
}

function filterByPriority(priority, btn) {
  state.currentFilter = priority;
  document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
  btn?.classList.add("active");
  renderCasesGrid();
}

function renderCasesGrid() {
  const grid = $("casesGrid");
  if (!grid) return;

  let filtered = [...state.cases].reverse();

  if (state.currentFilter !== "ALL") {
    filtered = filtered.filter(c => (c.decision?.priority || "").toUpperCase() === state.currentFilter);
  }

  if (state.searchQuery) {
    filtered = filtered.filter(c =>
      (c.case_id || "").toLowerCase().includes(state.searchQuery) ||
      (c.description || "").toLowerCase().includes(state.searchQuery) ||
      (c.location || "").toLowerCase().includes(state.searchQuery) ||
      (c.decision?.authority || "").toLowerCase().includes(state.searchQuery)
    );
  }

  if (!filtered.length) {
    grid.innerHTML = `
      <div class="empty-state">
        <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14,2 14,8 20,8"/></svg>
        <h3>${state.cases.length === 0 ? "No grievances logged" : "No matching records found"}</h3>
        <p>${state.cases.length === 0 ? "Submit your first report to populate the registry." : "Try adjusting your search query or priority filters."}</p>
        ${state.cases.length === 0 ? `<button class="btn-primary" onclick="showPage('report')">File Grievance</button>` : ""}
      </div>
    `;
    return;
  }

  grid.innerHTML = filtered.map(c => {
    const priority = (c.decision?.priority || "MEDIUM").toUpperCase();
    const score    = c.decision?.priority_score_0_to_100;

    return `
      <div class="case-card" onclick="openCaseModal('${c.case_id}')">
        <div class="case-card-top">
          <span class="case-card-id">${escapeHtml(c.case_id)}</span>
          <span class="rc-priority ${priority}">${priority}</span>
        </div>
        <div class="case-card-desc">${escapeHtml(c.description || "Grievance details")}</div>
        <div class="case-card-meta">
          ${c.location ? `<span class="case-meta-item">📍 ${escapeHtml(c.location)}</span>` : ""}
          ${c.timestamp ? `<span class="case-meta-item">⏱️ ${formatDate(c.timestamp)}</span>` : ""}
          ${c.decision?.authority ? `<span class="case-meta-item">🏛️ ${escapeHtml(c.decision.authority)}</span>` : ""}
        </div>
        ${typeof score === "number" ? `
          <div style="margin-top:14px;display:flex;align-items:center;gap:12px">
            <div class="metric-bar-track" style="flex:1">
              <div class="metric-bar-fill" style="width:${Math.min(100, score)}%"></div>
            </div>
            <span style="font-weight:700;font-size:12.5px;color:var(--ink-primary)">${score}/100</span>
          </div>
        ` : ""}
      </div>
    `;
  }).join("");
}

// ── Case Detail Modal ─────────────────────────────────────────────────────
function openCaseModal(caseId) {
  const c = state.cases.find(x => x.case_id === caseId);
  if (!c) return;

  $("modalCaseId").textContent = c.case_id;
  const dec = c.decision || {};
  const ac  = c.action  || {};
  const priority = (dec.priority || "MEDIUM").toUpperCase();

  $("modalBody").innerHTML = `
    <div class="modal-section">
      <div class="modal-section-title">Case Metadata</div>
      <div class="modal-grid">
        <div class="modal-field">
          <div class="modal-field-label">Statutory Priority</div>
          <div class="modal-field-value"><span class="rc-priority ${priority}">${priority}</span></div>
        </div>
        <div class="modal-field">
          <div class="modal-field-label">Priority Rating</div>
          <div class="modal-field-value">${dec.priority_score_0_to_100 ?? "—"} <small style="color:var(--ink-muted)">/ 100</small></div>
        </div>
        <div class="modal-field">
          <div class="modal-field-label">Assigned Body</div>
          <div class="modal-field-value" style="font-size:12.5px">${escapeHtml(dec.authority || "Municipal Council")}</div>
        </div>
        <div class="modal-field">
          <div class="modal-field-label">Department</div>
          <div class="modal-field-value" style="font-size:12.5px">${escapeHtml(dec.department || "Public Works")}</div>
        </div>
        <div class="modal-field">
          <div class="modal-field-label">Statutory Resolution SLA</div>
          <div class="modal-field-value" style="font-size:12.5px">${escapeHtml(dec.recommended_sla || "24-48 hours")}</div>
        </div>
        <div class="modal-field">
          <div class="modal-field-label">Filing Timestamp</div>
          <div class="modal-field-value" style="font-size:12.5px">${formatDate(c.timestamp)}</div>
        </div>
      </div>
    </div>

    <div class="modal-section">
      <div class="modal-section-title">Grievance Description</div>
      <div style="background:var(--card-bg-subtle);border-radius:var(--radius-md);padding:14px 16px;font-size:13px;line-height:1.6;color:var(--ink-primary)">
        ${escapeHtml(c.description || "No description")}
      </div>
      ${c.location ? `<div style="margin-top:8px;font-size:12px;color:var(--ink-muted)">📍 Location: <b>${escapeHtml(c.location)}</b></div>` : ""}
    </div>

    ${dec.rationale ? `
      <div class="modal-section">
        <div class="modal-section-title">Decision Rationale</div>
        <div style="font-size:12.5px;color:var(--ink-secondary);line-height:1.6">
          ${escapeHtml(dec.rationale)}
        </div>
      </div>
    ` : ""}

    ${ac.complaint_subject ? `
      <div class="modal-section">
        <div class="modal-section-title">Administrative Complaint Draft</div>
        <div class="complaint-block">
          <h4>${escapeHtml(ac.complaint_subject)}</h4>
          <p>${escapeHtml(ac.complaint_body || "—")}</p>
        </div>
      </div>
    ` : ""}
  `;

  $("caseModal")?.classList.remove("hidden");
  document.body.style.overflow = "hidden";
}

function closeCaseModal(e) {
  if (e && e.target !== $("caseModal")) return;
  $("caseModal")?.classList.add("hidden");
  document.body.style.overflow = "";
}

document.addEventListener("keydown", e => {
  if (e.key === "Escape") closeCaseModal();
});

// ── Analytics Dashboard ───────────────────────────────────────────────────
async function loadAnalytics() {
  try {
    const r = await fetch("/api/analytics");
    if (!r.ok) throw new Error();
    const d = await r.json();
    renderAnalytics(d);
  } catch {
    renderAnalyticsFromState();
  }
}

function renderAnalytics(d) {
  renderPriorityChart(d.priority_counts || {});
  renderCategoryChart(d.category_counts || {});
  renderTimeline(d.timeline || []);
  renderAuthorityChart(d.authority_counts || {});
  renderRiskChart(d.risk_distribution || []);
}

function renderAnalyticsFromState() {
  const cases = state.cases;
  const pCount = {};
  const catCount = {};
  const authCount = {};

  cases.forEach(c => {
    const p = (c.decision?.priority || "MEDIUM").toUpperCase();
    pCount[p] = (pCount[p] || 0) + 1;

    const cat = c.agents?.vision?.category || "Infrastructure";
    catCount[cat] = (catCount[cat] || 0) + 1;

    const auth = c.decision?.authority || "Municipal Corporation";
    authCount[auth] = (authCount[auth] || 0) + 1;
  });

  renderPriorityChart(pCount);
  renderCategoryChart(catCount);
  renderTimeline([]);
  renderAuthorityChart(authCount);
  renderRiskChart([]);
}

function renderPriorityChart(counts) {
  const total = Object.values(counts).reduce((a, b) => a + b, 0) || 1;
  const items = [
    { label: "CRITICAL", count: counts.CRITICAL || 0, color: "var(--tone-critical-fg)" },
    { label: "HIGH",     count: counts.HIGH || 0,     color: "var(--tone-high-fg)" },
    { label: "MEDIUM",   count: counts.MEDIUM || 0,   color: "var(--tone-medium-fg)" },
    { label: "LOW",      count: counts.LOW || 0,      color: "var(--tone-low-fg)" },
  ];
  renderBarChart("priorityChart", items, total);
}

function renderCategoryChart(counts) {
  const total = Object.values(counts).reduce((a, b) => a + b, 0) || 1;
  const colors = [
    "var(--accent-espresso)",
    "var(--accent-walnut)",
    "var(--tone-high-fg)",
    "var(--tone-medium-fg)",
    "var(--tone-low-fg)",
    "var(--tone-critical-fg)"
  ];

  const items = Object.entries(counts).map(([label, count], i) => ({
    label, count, color: colors[i % colors.length]
  }));

  if (!items.length) {
    $("categoryChart").innerHTML = `<div class="no-data">No data available</div>`;
    return;
  }
  renderBarChart("categoryChart", items, total);
}

function renderBarChart(id, items, total) {
  const el = $(id);
  if (!el) return;

  if (!items.length || total === 0) {
    el.innerHTML = `<div class="no-data">No data available</div>`;
    return;
  }

  el.innerHTML = `
    <div class="bar-group">
      ${items.map(item => `
        <div class="bar-row">
          <div class="bar-label">${escapeHtml(item.label)}</div>
          <div class="bar-track">
            <div class="bar-fill" style="width:${Math.round(item.count / total * 100)}%;background:${item.color}"></div>
          </div>
          <div class="bar-value">${item.count}</div>
        </div>
      `).join("")}
    </div>
  `;
}

function renderTimeline(timeline) {
  const el = $("timelineChart");
  if (!el) return;

  if (!timeline.length) {
    const byDate = {};
    state.cases.forEach(c => {
      if (!c.timestamp) return;
      const d = new Date(c.timestamp * 1000);
      const key = `${d.getMonth() + 1}/${d.getDate()}`;
      byDate[key] = (byDate[key] || 0) + 1;
    });
    timeline = Object.entries(byDate).map(([date, count]) => ({ date, count })).slice(-14);
  }

  if (!timeline.length) {
    el.innerHTML = `<div class="no-data">No activity timeline recorded yet</div>`;
    return;
  }

  const max = Math.max(...timeline.map(t => t.count), 1);

  el.innerHTML = `
    <div class="timeline-bars">
      ${timeline.map(t => `
        <div class="tl-bar-col">
          <div class="tl-bar-fill" style="height:${Math.max(8, Math.round(t.count / max * 110))}px" title="${t.count} cases"></div>
          <div class="tl-label">${t.date}</div>
        </div>
      `).join("")}
    </div>
  `;
}

function renderAuthorityChart(counts) {
  const total = Object.values(counts).reduce((a, b) => a + b, 0) || 1;
  const colors = [
    "var(--accent-espresso)",
    "var(--accent-walnut)",
    "var(--tone-medium-fg)",
    "var(--tone-high-fg)",
    "var(--tone-low-fg)"
  ];

  const items = Object.entries(counts).slice(0, 5).map(([label, count], i) => ({
    label, count, color: colors[i % colors.length]
  }));

  const el = $("authorityChart");
  if (!el) return;

  if (!items.length) {
    el.innerHTML = `<div class="no-data">No jurisdiction records</div>`;
    return;
  }

  el.innerHTML = `
    <div class="donut-list">
      ${items.map(item => `
        <div class="donut-item">
          <div class="donut-dot" style="background:${item.color}"></div>
          <div class="donut-name">${escapeHtml(item.label)}</div>
          <div class="donut-bar">
            <div class="donut-bar-fill" style="width:${Math.round(item.count / total * 100)}%;background:${item.color}"></div>
          </div>
          <div class="donut-pct">${item.count}</div>
        </div>
      `).join("")}
    </div>
  `;
}

function renderRiskChart(distribution) {
  const el = $("riskChart");
  if (!el) return;

  const scores = state.cases.map(c => c.agents?.safety?.risk_score_0_to_100).filter(s => typeof s === "number");

  if (!scores.length) {
    el.innerHTML = `<div class="no-data">No risk score records</div>`;
    return;
  }

  const buckets = [
    { label: "Low Hazard (0–25)",        count: scores.filter(s => s <= 25).length,           color: "var(--tone-low-fg)" },
    { label: "Moderate (26–50)",          count: scores.filter(s => s > 25 && s <= 50).length,  color: "var(--tone-medium-fg)" },
    { label: "High Hazard (51–75)",      count: scores.filter(s => s > 50 && s <= 75).length,  color: "var(--tone-high-fg)" },
    { label: "Critical Hazard (76–100)", count: scores.filter(s => s > 75).length,            color: "var(--tone-critical-fg)" },
  ];

  renderBarChart("riskChart", buckets, scores.length);
}

// ── Application Initialization ────────────────────────────────────────────
async function init() {
  initReportForm();
  renderAgentNetworkOverview();
  await Promise.all([checkHealth(), loadCases()]);
  renderOverview();
}

// Initialize on DOM load
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}
