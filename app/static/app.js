// Mini-SIEM Command Center Console Logic

const API_BASE = "";

// State
let isolatedIpsSet = new Set();
let suspendedUsersSet = new Set();
let lastAlertsDataHash = "";
let lastLogsDataHash = "";
let lastAuditDataHash = "";
let lastWhitelistDataHash = "";
let lastIsolatedDataHash = "";
let lastSuspendedDataHash = "";

// Elements
const alertList = document.getElementById("alertList");
const logTableBody = document.getElementById("logTableBody");
const whitelistTableBody = document.getElementById("whitelistTableBody");
const whitelistForm = document.getElementById("whitelistForm");
const btnReset = document.getElementById("btnReset");

// SOAR Elements
const valIsolatedCount = document.getElementById("valIsolatedCount");
const valSuspendedUsersCount = document.getElementById("valSuspendedUsersCount");
const valBlockedCount = document.getElementById("valBlockedCount");
const isolatedCountBadge = document.getElementById("isolatedCountBadge");
const isolatedTableBody = document.getElementById("isolatedTableBody");
const suspendedUsersTableBody = document.getElementById("suspendedUsersTableBody");
const isolateForm = document.getElementById("isolateForm");
const soarAuditList = document.getElementById("soarAuditList");

// Metric elements
const valTotalLogs = document.getElementById("valTotalLogs");
const valCriticalAlerts = document.getElementById("valCriticalAlerts");
const valHighAlerts = document.getElementById("valHighAlerts");
const valMediumAlerts = document.getElementById("valMediumAlerts");
const valWhitelistCount = document.getElementById("valWhitelistCount");
const valWatchlistCount = document.getElementById("valWatchlistCount");
const valColdCount = document.getElementById("valColdCount");
const alertCountBadge = document.getElementById("alertCountBadge");
const logCountBadge = document.getElementById("logCountBadge");

// UI/UX Pro Max: Stream Ordering & Severity Mode Elements
const btnViewChronological = document.getElementById("btnViewChronological");
const btnViewSeverity = document.getElementById("btnViewSeverity");
const severityFilterChips = document.getElementById("severityFilterChips");
const criticalCounterBadge = document.getElementById("criticalCounterBadge");
const timelineTitleIcon = document.getElementById("timelineTitleIcon");
const timelineTitleText = document.getElementById("timelineTitleText");
const timelineModeTag = document.getElementById("timelineModeTag");
const countFilterCritical = document.getElementById("countFilterCritical");
const countFilterHigh = document.getElementById("countFilterHigh");
const countFilterMedium = document.getElementById("countFilterMedium");

let currentCachedAlerts = [];
let incidentViewMode = localStorage.getItem("mini_siem_incident_view_mode") || "chrono";
let currentSeverityFilter = "ALL";

// Modal Elements
const modalOverlay = document.getElementById("modalOverlay");
const modalTitle = document.getElementById("modalTitle");
const modalMessage = document.getElementById("modalMessage");
const modalInputWrapper = document.getElementById("modalInputWrapper");
const modalInputLabel = document.getElementById("modalInputLabel");
const modalInputField = document.getElementById("modalInputField");
const modalCancelBtn = document.getElementById("modalCancelBtn");
const modalConfirmBtn = document.getElementById("modalConfirmBtn");
const modalCloseBtn = document.getElementById("modalCloseBtn");
const toastContainer = document.getElementById("toastContainer");

// Connection Resilience Elements
const statusIndicator = document.getElementById("statusIndicator");
const statusText = document.getElementById("statusText");
const connectionBanner = document.getElementById("connectionBanner");
const btnRetryConnection = document.getElementById("btnRetryConnection");

let consecutivePollErrors = 0;
let isConnectionOnline = true;

const IPV4_REGEX = /^(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}$/;

function setConnectionState(online) {
    if (isConnectionOnline === online) return;
    isConnectionOnline = online;

    if (online) {
        if (statusIndicator) statusIndicator.classList.remove("offline");
        if (statusText) statusText.textContent = "Live Correlation Engine (2s Interval)";
        if (connectionBanner) connectionBanner.hidden = true;
        showToast("Koneksi ke SIEM Gateway tersambung kembali", "success");
    } else {
        if (statusIndicator) statusIndicator.classList.add("offline");
        if (statusText) statusText.textContent = "Gateway Disconnected (Retrying...)";
        if (connectionBanner) connectionBanner.hidden = false;
        showToast("Koneksi ke SIEM Gateway terputus. Mencoba rekoneksi...", "error");
    }
}

if (btnRetryConnection) {
    btnRetryConnection.addEventListener("click", () => {
        pollCycle();
    });
}

let activeModalResolve = null;

// Tab Switching Initialization
function initTabs() {
    const tabs = [
        { btn: document.getElementById("tabBtnSoar"), pane: document.getElementById("tabPaneSoar") },
        { btn: document.getElementById("tabBtnWhitelist"), pane: document.getElementById("tabPaneWhitelist") },
        { btn: document.getElementById("tabBtnSimulator"), pane: document.getElementById("tabPaneSimulator") }
    ];

    tabs.forEach(({ btn, pane }) => {
        if (!btn || !pane) return;
        btn.addEventListener("click", () => {
            tabs.forEach(t => {
                if (!t.btn || !t.pane) return;
                const isActive = t.btn === btn;
                t.btn.classList.toggle("active", isActive);
                t.btn.setAttribute("aria-selected", isActive ? "true" : "false");
                t.pane.classList.toggle("active", isActive);
                t.pane.hidden = !isActive;
            });
        });
    });
}
initTabs();

// ======================= UI/UX PRO MAX: INCIDENT STREAM VIEW SWITCHER =======================

function setIncidentViewMode(mode) {
    if (mode !== "chrono" && mode !== "severity") mode = "chrono";
    incidentViewMode = mode;
    localStorage.setItem("mini_siem_incident_view_mode", mode);

    const isChrono = mode === "chrono";
    if (btnViewChronological) {
        btnViewChronological.classList.toggle("active", isChrono);
        btnViewChronological.setAttribute("aria-selected", isChrono ? "true" : "false");
    }
    if (btnViewSeverity) {
        btnViewSeverity.classList.toggle("active", !isChrono);
        btnViewSeverity.setAttribute("aria-selected", !isChrono ? "true" : "false");
    }
    if (severityFilterChips) {
        severityFilterChips.hidden = isChrono;
    }
    if (timelineTitleIcon) timelineTitleIcon.textContent = isChrono ? "⏱️" : "🚨";
    if (timelineTitleText) timelineTitleText.textContent = isChrono ? "Chronological Incident Timeline Stream" : "Prioritized Incident Stream (Highest Severity)";
    if (timelineModeTag) timelineModeTag.textContent = isChrono ? "CHRONOLOGICAL EVENT STREAM" : "PRIORITIZED SEVERITY RANKING";

    // Force re-render with active view mode
    lastAlertsDataHash = "";
    renderAlerts(currentCachedAlerts);
}

function initIncidentStreamControls() {
    if (btnViewChronological) {
        btnViewChronological.addEventListener("click", () => setIncidentViewMode("chrono"));
    }
    if (btnViewSeverity) {
        btnViewSeverity.addEventListener("click", () => setIncidentViewMode("severity"));
    }

    if (severityFilterChips) {
        severityFilterChips.addEventListener("click", (e) => {
            const chip = e.target.closest(".chip-filter");
            if (!chip) return;
            const filter = chip.dataset.filter || "ALL";
            currentSeverityFilter = filter;

            severityFilterChips.querySelectorAll(".chip-filter").forEach(c => {
                const isActive = c === chip;
                c.classList.toggle("active", isActive);
                c.setAttribute("aria-checked", isActive ? "true" : "false");
            });

            lastAlertsDataHash = "";
            renderAlerts(currentCachedAlerts);
        });
    }

    // Set initial active state based on stored preference
    setIncidentViewMode(incidentViewMode);
}
initIncidentStreamControls();

// ======================= NON-BLOCKING MODAL & TOAST SYSTEM =======================

let previouslyFocusedElement = null;

function closeModal(result = null) {
    if (modalOverlay) {
        modalOverlay.hidden = true;
    }
    if (previouslyFocusedElement && typeof previouslyFocusedElement.focus === "function") {
        previouslyFocusedElement.focus();
        previouslyFocusedElement = null;
    }
    if (activeModalResolve) {
        const resolve = activeModalResolve;
        activeModalResolve = null;
        resolve(result);
    }
}

if (modalCloseBtn) modalCloseBtn.addEventListener("click", () => closeModal(null));
if (modalCancelBtn) modalCancelBtn.addEventListener("click", () => closeModal(null));
if (modalOverlay) {
    modalOverlay.addEventListener("click", (e) => {
        if (e.target === modalOverlay) closeModal(null);
    });
}

// Focus trap & Escape listener for modal dialog (WAI-ARIA compliance)
window.addEventListener("keydown", (e) => {
    if (!modalOverlay || modalOverlay.hidden) return;

    if (e.key === "Escape") {
        e.preventDefault();
        closeModal(null);
        return;
    }

    if (e.key === "Tab") {
        const focusable = Array.from(modalOverlay.querySelectorAll(
            'button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
        )).filter(el => !el.hidden && el.offsetParent !== null);

        if (focusable.length === 0) return;

        const first = focusable[0];
        const last = focusable[focusable.length - 1];

        if (e.shiftKey) {
            if (document.activeElement === first || !modalOverlay.contains(document.activeElement)) {
                e.preventDefault();
                last.focus();
            }
        } else {
            if (document.activeElement === last || !modalOverlay.contains(document.activeElement)) {
                e.preventDefault();
                first.focus();
            }
        }
    }
});

function showConfirmModal({ title = "Confirm Action", message = "", confirmText = "Confirm", cancelText = "Cancel", danger = false }) {
    return new Promise((resolve) => {
        activeModalResolve = resolve;
        if (!modalOverlay) return resolve(false);

        previouslyFocusedElement = document.activeElement;
        modalTitle.textContent = title;
        modalMessage.textContent = message;
        modalInputWrapper.hidden = true;
        modalCancelBtn.hidden = false;
        modalCancelBtn.textContent = cancelText;
        modalConfirmBtn.textContent = confirmText;

        if (danger) {
            modalConfirmBtn.className = "btn btn-danger";
        } else {
            modalConfirmBtn.className = "btn btn-primary";
        }

        modalOverlay.hidden = false;
        modalConfirmBtn.onclick = () => closeModal(true);
        modalConfirmBtn.focus();
    });
}

function showPromptModal({ title = "Input Required", message = "", defaultValue = "", placeholder = "", confirmText = "Submit", cancelText = "Cancel" }) {
    return new Promise((resolve) => {
        activeModalResolve = resolve;
        if (!modalOverlay) return resolve(null);

        previouslyFocusedElement = document.activeElement;
        modalTitle.textContent = title;
        modalMessage.textContent = message;
        modalInputWrapper.hidden = false;
        modalInputField.value = defaultValue;
        modalInputField.placeholder = placeholder;
        modalCancelBtn.hidden = false;
        modalCancelBtn.textContent = cancelText;
        modalConfirmBtn.textContent = confirmText;
        modalConfirmBtn.className = "btn btn-primary";

        modalOverlay.hidden = false;
        modalInputField.focus();
        modalInputField.select();

        modalConfirmBtn.onclick = () => {
            const val = modalInputField.value.trim();
            closeModal(val || defaultValue || "");
        };

        modalInputField.onkeydown = (e) => {
            if (e.key === "Enter") {
                e.preventDefault();
                modalConfirmBtn.click();
            } else if (e.key === "Escape") {
                e.preventDefault();
                closeModal(null);
            }
        };
    });
}

function showNoticeModal({ title = "System Report", message = "" }) {
    return new Promise((resolve) => {
        activeModalResolve = resolve;
        if (!modalOverlay) return resolve();

        previouslyFocusedElement = document.activeElement;
        modalTitle.textContent = title;
        modalMessage.textContent = message;
        modalInputWrapper.hidden = true;
        modalCancelBtn.hidden = true;
        modalConfirmBtn.textContent = "Close";
        modalConfirmBtn.className = "btn btn-primary";

        modalOverlay.hidden = false;
        modalConfirmBtn.onclick = () => closeModal();
        modalConfirmBtn.focus();
    });
}

function showToast(message, type = "info") {
    if (!toastContainer) return;

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.setAttribute("role", "status");

    const textDiv = document.createElement("div");
    textDiv.className = "toast-message";
    textDiv.textContent = message;

    const closeBtn = document.createElement("button");
    closeBtn.className = "toast-close";
    closeBtn.type = "button";
    closeBtn.setAttribute("aria-label", "Close notification");
    closeBtn.innerHTML = "&times;";

    toast.appendChild(textDiv);
    toast.appendChild(closeBtn);
    toastContainer.appendChild(toast);

    let dismissed = false;
    const dismiss = () => {
        if (dismissed) return;
        dismissed = true;
        toast.style.opacity = "0";
        toast.style.transform = "translateX(10px)";
        setTimeout(() => toast.remove(), 200);
    };

    closeBtn.addEventListener("click", dismiss);
    setTimeout(dismiss, 4000);
}

// Format Date Utility
function formatTimestamp(isoStr) {
    if (!isoStr) return "-";
    try {
        const d = new Date(isoStr);
        return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) + 
               " " + d.toISOString().slice(0, 10);
    } catch {
        return isoStr;
    }
}

// ======================= ALERT FEED & RECONCILIATION =======================

async function fetchAlerts() {
    try {
        const res = await fetch(`${API_BASE}/api/alerts?limit=50`);
        if (!res.ok) return;
        const alerts = await res.json();
        renderAlerts(alerts);
        processAlertsForAttackMap(alerts);
    } catch (err) {
        console.error("Error fetching alerts:", err);
    }
}

function createAlertCardElement(a, rankNumber = null) {
    const isHostContained = a.ip_address && isolatedIpsSet.has(a.ip_address);
    const isUserSuspended = a.user_id && suspendedUsersSet.has(a.user_id);
    const isContained = a.status === "CONTAINED" || isHostContained || isUserSuspended;

    const card = document.createElement("div");
    card.className = `alert-card ${a.severity} ${isContained ? 'CONTAINED' : ''}`;
    card.id = `alert-${a.id}`;

    const metaDetails = a.details ? Object.entries(a.details)
        .map(([k, v]) => `<span class="meta-item"><strong>${escapeHtml(k)}:</strong> ${typeof v === 'object' ? escapeHtml(JSON.stringify(v)) : escapeHtml(String(v))}</span>`)
        .join("") : "";

    let hostButtonHtml = "";
    if (a.ip_address) {
        if (isHostContained) {
            hostButtonHtml = `<button class="btn-action-release" data-action="release-host" data-ip="${escapeHtml(a.ip_address)}" type="button">🔓 Release Host</button>`;
        } else {
            hostButtonHtml = `<button class="btn-action-isolate" data-action="isolate-host" data-ip="${escapeHtml(a.ip_address)}" data-alert="${a.id}" type="button">🔒 Isolate Host</button>`;
        }
    }

    let userButtonHtml = "";
    if (a.user_id) {
        if (isUserSuspended) {
            userButtonHtml = `<button class="btn-action-release" data-action="unsuspend-user" data-user="${escapeHtml(a.user_id)}" type="button">🔓 Unsuspend User</button>`;
        } else {
            userButtonHtml = `<button class="btn-action-suspend" data-action="suspend-user" data-user="${escapeHtml(a.user_id)}" data-alert="${a.id}" type="button">🚫 Suspend User</button>`;
        }
    }

    // Cortex Threat Intelligence (CTI) Enrichment Block
    let ctiBlock = "";
    if (a.threat_intel) {
        const ti = a.threat_intel;
        const verdictColor = ti.verdict === "MALICIOUS" ? "#f87171" : (ti.verdict === "SUSPICIOUS" ? "#fbbf24" : "#34d399");
        const verdictBg = ti.verdict === "MALICIOUS" ? "rgba(239, 68, 68, 0.15)" : (ti.verdict === "SUSPICIOUS" ? "rgba(245, 158, 11, 0.15)" : "rgba(16, 185, 129, 0.15)");
        const verdictBorder = ti.verdict === "MALICIOUS" ? "rgba(239, 68, 68, 0.35)" : (ti.verdict === "SUSPICIOUS" ? "rgba(245, 158, 11, 0.35)" : "rgba(16, 185, 129, 0.35)");
        
        const indicatorsHtml = (ti.indicators || []).map(ind => `<span style="font-size: 0.68rem; background: rgba(255,255,255,0.06); padding: 1px 5px; border-radius: 3px; color: #cbd5e1;">${escapeHtml(ind)}</span>`).join(" ");

        ctiBlock = `
            <div class="alert-cti" style="margin-top: 0.55rem; padding: 0.45rem 0.65rem; background: rgba(15, 23, 42, 0.6); border: 1px solid ${verdictBorder}; border-radius: 4px; font-size: 0.75rem;">
                <div style="display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 0.2rem;">
                    <div style="display: flex; align-items: center; gap: 0.4rem;">
                        <span>${ti.flag || '🌐'}</span>
                        <strong style="color: #f1f5f9;">${escapeHtml(ti.country || 'Unknown')}</strong>
                        <span style="color: #64748b;">&bull;</span>
                        <span style="color: #94a3b8; font-family: monospace;">${escapeHtml(ti.asn || '')}</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.4rem;">
                        <span style="background: ${verdictBg}; color: ${verdictColor}; border: 1px solid ${verdictBorder}; padding: 1px 6px; border-radius: 3px; font-weight: 700; font-size: 0.7rem;">
                            ${ti.verdict} (${ti.abuse_score}%)
                        </span>
                        ${ti.threat_actor ? `<span style="background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.35); padding: 1px 6px; border-radius: 3px; font-size: 0.7rem;">👤 ${escapeHtml(ti.threat_actor)}</span>` : ''}
                    </div>
                </div>
                <div style="color: #94a3b8; font-size: 0.72rem; display: flex; align-items: center; gap: 0.4rem; flex-wrap: wrap;">
                    <span>Kategori: <em style="color: #e2e8f0;">${escapeHtml(ti.category)}</em></span>
                    ${indicatorsHtml ? `<span style="color: #475569;">|</span> ${indicatorsHtml}` : ''}
                </div>
            </div>
        `;
    }

    const rankBadgeHtml = rankNumber !== null ? `
        <span class="badge-priority-rank rank-${(a.severity || '').toLowerCase()}">RANK #${rankNumber}</span>
    ` : '';

    card.innerHTML = `
        <div class="alert-header">
            <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                ${rankBadgeHtml}
                <span class="alert-badge ${a.severity}">${a.severity}</span>
                ${a.rule_id ? `<span class="badge-rule-id" style="font-size: 0.7rem; font-family: monospace; background: rgba(59,130,246,0.15); border: 1px solid rgba(59,130,246,0.4); color: #60a5fa; padding: 2px 6px; border-radius: 4px;">🏷️ ${escapeHtml(a.rule_id)}</span>` : ""}
                ${a.mitre ? `<span class="badge-mitre" style="font-size: 0.7rem; font-family: monospace; background: rgba(245,158,11,0.15); border: 1px solid rgba(245,158,11,0.4); color: #fbbf24; padding: 2px 6px; border-radius: 4px;">🎯 MITRE ${escapeHtml(a.mitre.technique_id)} &bull; ${escapeHtml(a.mitre.tactic)}</span>` : ""}
                ${isHostContained ? `<span class="badge-contained">🔒 HOST QUARANTINED</span>` : ""}
                ${isUserSuspended ? `<span class="badge-contained" style="border-color: rgba(239,68,68,0.5); color: #f87171;">🚫 USER SUSPENDED</span>` : ""}
            </div>
            <div style="display: flex; align-items: center; gap: 0.45rem; flex-wrap: wrap;">
                <span class="alert-time">⏱️ ${formatTimestamp(a.timestamp)} (ID: ${a.id})</span>
                ${hostButtonHtml}
                ${userButtonHtml}
                <button class="btn-action-escalate" data-action="escalate-case" data-alert="${a.id}" type="button" style="background: rgba(168, 85, 247, 0.2); border: 1px solid rgba(168, 85, 247, 0.5); color: #c084fc; padding: 2px 8px; border-radius: 4px; font-size: 0.72rem; cursor: pointer;">📁 Escalate</button>
            </div>
        </div>
        <div class="alert-rule">${escapeHtml(a.rule_name)}</div>
        <div class="alert-desc">${escapeHtml(a.description)}</div>
        ${ctiBlock}
        ${metaDetails ? `<div class="alert-meta">${metaDetails}</div>` : ""}
    `;

    return card;
}

function renderAlerts(alerts) {
    currentCachedAlerts = alerts || [];

    // Calculate dynamic severity totals
    const criticalCount = currentCachedAlerts.filter(a => a.severity === "KRITIS").length;
    const highCount = currentCachedAlerts.filter(a => a.severity === "TINGGI").length;
    const mediumCount = currentCachedAlerts.filter(a => a.severity === "MENENGAH").length;

    if (countFilterCritical) countFilterCritical.textContent = criticalCount;
    if (countFilterHigh) countFilterHigh.textContent = highCount;
    if (countFilterMedium) countFilterMedium.textContent = mediumCount;

    if (criticalCounterBadge) {
        if (criticalCount > 0) {
            criticalCounterBadge.textContent = criticalCount;
            criticalCounterBadge.hidden = false;
        } else {
            criticalCounterBadge.hidden = true;
        }
    }

    if (alertCountBadge) alertCountBadge.textContent = `${alerts.length} Total`;

    if (!alerts || alerts.length === 0) {
        if (lastAlertsDataHash !== "empty") {
            lastAlertsDataHash = "empty";
            alertList.className = `alert-list mode-${incidentViewMode}`;
            alertList.innerHTML = `
                <div class="empty-state">
                    Awaiting security incident detection.<br>
                    Trigger an attack scenario from the Simulator tab to evaluate detection rules.
                </div>`;
        }
        return;
    }

    const currentHash = `${incidentViewMode}_${currentSeverityFilter}_` + alerts.map(a => `${a.id}_${a.severity}_${a.status}_${isolatedIpsSet.has(a.ip_address)}_${suspendedUsersSet.has(a.user_id)}`).join("|");
    if (currentHash === lastAlertsDataHash) {
        return; // No DOM mutation needed, prevents selection wipe and repaint
    }
    lastAlertsDataHash = currentHash;

    const fragment = document.createDocumentFragment();

    if (incidentViewMode === "chrono") {
        // Mode 1: Chronological Incident Timeline Stream (Vertical Spine Line)
        alertList.className = "alert-list mode-chrono";
        alerts.forEach(a => {
            fragment.appendChild(createAlertCardElement(a, null));
        });
    } else {
        // Mode 2: Highest Severity Ranking (UI/UX Pro Max Priority Tiers)
        alertList.className = "alert-list mode-severity";

        const severityOrder = { "KRITIS": 3, "TINGGI": 2, "MENENGAH": 1 };

        let filteredAlerts = [...alerts];
        if (currentSeverityFilter !== "ALL") {
            filteredAlerts = filteredAlerts.filter(a => a.severity === currentSeverityFilter);
        }

        // Sort by Severity first (KRITIS -> TINGGI -> MENENGAH), then by timestamp descending
        filteredAlerts.sort((a, b) => {
            const weightA = severityOrder[a.severity] || 0;
            const weightB = severityOrder[b.severity] || 0;
            if (weightB !== weightA) return weightB - weightA;
            return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
        });

        if (filteredAlerts.length === 0) {
            const emptyEl = document.createElement("div");
            emptyEl.className = "empty-state";
            emptyEl.textContent = `Tidak ditemukan temuan insiden dengan tingkat keparahan ${currentSeverityFilter}.`;
            fragment.appendChild(emptyEl);
        } else {
            // Group into visible severity tiers for rapid SOC triage
            const grouped = {
                KRITIS: filteredAlerts.filter(a => a.severity === "KRITIS"),
                TINGGI: filteredAlerts.filter(a => a.severity === "TINGGI"),
                MENENGAH: filteredAlerts.filter(a => a.severity === "MENENGAH")
            };

            let globalRank = 1;

            const tiers = [
                { id: "KRITIS", name: "🔴 TIER 1: KRITIS (IMMEDIATE MITIGATION REQUIRED)", items: grouped.KRITIS, classSuffix: "kritis" },
                { id: "TINGGI", name: "🟠 TIER 2: TINGGI (ELEVATED ATTACK VECTORS)", items: grouped.TINGGI, classSuffix: "tinggi" },
                { id: "MENENGAH", name: "🔵 TIER 3: MENENGAH (OPERATIONAL ANOMALIES)", items: grouped.MENENGAH, classSuffix: "menengah" }
            ];

            tiers.forEach(tier => {
                if (tier.items.length === 0) return;

                // Render UI/UX Pro Max Tier Header
                const tierHeader = document.createElement("div");
                tierHeader.className = `severity-tier-header tier-${tier.classSuffix}`;
                tierHeader.innerHTML = `
                    <span>${tier.name}</span>
                    <span class="tier-badge-pill">${tier.items.length} Temuan Aktif</span>
                `;
                fragment.appendChild(tierHeader);

                tier.items.forEach(a => {
                    fragment.appendChild(createAlertCardElement(a, globalRank++));
                });
            });
        }
    }

    alertList.innerHTML = "";
    alertList.appendChild(fragment);
}

// Event Delegation for Alert Buttons
alertList.addEventListener("click", async (e) => {
    const btn = e.target.closest("button");
    if (!btn) return;

    const action = btn.dataset.action;
    if (action === "isolate-host") {
        const ip = btn.dataset.ip;
        const alertId = btn.dataset.alert;
        await window.isolateHost(ip, `Active containment for Incident #${alertId}`);
    } else if (action === "release-host") {
        const ip = btn.dataset.ip;
        await window.releaseHost(ip);
    } else if (action === "suspend-user") {
        const userId = btn.dataset.user;
        const alertId = btn.dataset.alert;
        await window.suspendUser(userId, `Identity lockdown for Incident #${alertId}`);
    } else if (action === "unsuspend-user") {
        const userId = btn.dataset.user;
        await window.unsuspendUser(userId);
    } else if (action === "escalate-case") {
        const alertId = btn.dataset.alert;
        const initialNote = await showPromptModal({
            title: `Eskalasi Alert #${alertId} ke Kasus Insiden`,
            message: "Masukkan catatan awal investigasi (opsional):",
            defaultValue: "Analisis awal menunjukkan anomali terkonfirmasi, eskalasi ke tier investigasi.",
            placeholder: "Catatan temuan SOC Analyst..."
        });
        if (initialNote === null) return;
        try {
            const res = await fetch(`${API_BASE}/api/cases/escalate`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    alert_id: alertId,
                    analyst: "SOC Analyst Tier-1",
                    initial_note: initialNote.trim() || undefined
                })
            });
            const data = await res.json();
            if (res.ok) {
                showToast(`Kasus ${data.id} berhasil dieskalasi! (${data.tlp})`, "success");
                await fetchAlerts();
                await fetchStats();
            } else {
                showToast(`Gagal eskalasi: ${data.detail || 'Terjadi kesalahan'}`, "error");
            }
        } catch (err) {
            showToast(`Gagal eskalasi: ${err.message}`, "error");
        }
    }
});

// ======================= STATS & METRICS =======================

async function fetchStats() {
    try {
        const res = await fetch(`${API_BASE}/api/stats`);
        if (!res.ok) return false;
        const stats = await res.json();

        if (valTotalLogs) valTotalLogs.textContent = stats.total_logs_ingested || 0;
        if (valCriticalAlerts) valCriticalAlerts.textContent = stats.alerts_by_severity?.KRITIS || 0;
        if (valHighAlerts) valHighAlerts.textContent = stats.alerts_by_severity?.TINGGI || 0;
        if (valMediumAlerts) valMediumAlerts.textContent = stats.alerts_by_severity?.MENENGAH || 0;
        if (valWhitelistCount) valWhitelistCount.textContent = stats.whitelist_count || 0;
        if (valWatchlistCount) valWatchlistCount.textContent = stats.watchlist_count || 0;
        if (valColdCount) valColdCount.textContent = stats.cold_archive_count || 0;
        if (valIsolatedCount) valIsolatedCount.textContent = stats.isolated_hosts_count || 0;
        if (valSuspendedUsersCount) valSuspendedUsersCount.textContent = stats.suspended_users_count || 0;
        if (valBlockedCount) valBlockedCount.textContent = stats.blocked_containment_count || 0;
        return true;
    } catch (err) {
        console.error("Error fetching stats:", err);
        return false;
    }
}

// ======================= RECENT INGESTION STREAM =======================

async function fetchLogs() {
    try {
        const res = await fetch(`${API_BASE}/api/logs?limit=15`);
        if (!res.ok) return;
        const logs = await res.json();
        renderLogs(logs);
    } catch (err) {
        console.error("Error fetching logs:", err);
    }
}

function renderLogs(logs) {
    if (logCountBadge) logCountBadge.textContent = `${logs.length} Recent`;

    if (!logs || logs.length === 0) {
        if (lastLogsDataHash !== "empty") {
            lastLogsDataHash = "empty";
            logTableBody.innerHTML = `
                <tr>
                    <td colspan="6" class="table-empty">No ingestion events recorded yet via POST /api/ingest</td>
                </tr>`;
        }
        return;
    }

    const currentHash = logs.map(l => `${l.timestamp}_${l.ip_address}_${l.event_type}_${l.status}`).join("|");
    if (currentHash === lastLogsDataHash) return;
    lastLogsDataHash = currentHash;

    logTableBody.innerHTML = logs.map(l => `
        <tr class="log-row">
            <td>${formatTimestamp(l.timestamp)}</td>
            <td><code style="color: #38bdf8;">${escapeHtml(l.event_type)}</code></td>
            <td><strong>${escapeHtml(l.user_id)}</strong></td>
            <td>${escapeHtml(l.ip_address)}</td>
            <td>${escapeHtml(l.location)}</td>
            <td>
                <span class="${l.status === 'success' ? 'status-badge-success' : 'status-badge-failed'}">
                    ● ${escapeHtml(l.status.toUpperCase())}
                </span>
            </td>
        </tr>
    `).join("");
}

// ======================= WHITELIST TUNING =======================

async function fetchWhitelist() {
    try {
        const res = await fetch(`${API_BASE}/api/whitelist`);
        if (!res.ok) return;
        const list = await res.json();
        renderWhitelist(list);
    } catch (err) {
        console.error("Error fetching whitelist:", err);
    }
}

function renderWhitelist(list) {
    if (!list || list.length === 0) {
        if (lastWhitelistDataHash !== "empty") {
            lastWhitelistDataHash = "empty";
            whitelistTableBody.innerHTML = `
                <tr>
                    <td colspan="3" class="table-empty">No active whitelisted IP addresses</td>
                </tr>`;
        }
        return;
    }

    const currentHash = list.map(i => `${i.ip_address}_${i.reason}`).join("|");
    if (currentHash === lastWhitelistDataHash) return;
    lastWhitelistDataHash = currentHash;

    whitelistTableBody.innerHTML = list.map(item => `
        <tr>
            <td><strong>${escapeHtml(item.ip_address)}</strong></td>
            <td>${escapeHtml(item.reason || "-")}</td>
            <td>
                <button class="btn-sm-delete" data-ip="${escapeHtml(item.ip_address)}" type="button">
                    🗑️ Remove
                </button>
            </td>
        </tr>
    `).join("");
}

if (whitelistTableBody) {
    whitelistTableBody.addEventListener("click", async (e) => {
        const btn = e.target.closest(".btn-sm-delete");
        if (!btn) return;
        const ip = btn.dataset.ip;
        await window.removeWhitelist(ip);
    });
}

// Add IP to Whitelist
if (whitelistForm) {
    whitelistForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const ipInput = document.getElementById("whitelistIp");
        const reasonInput = document.getElementById("whitelistReason");
        const ip = ipInput.value.trim();
        const reason = reasonInput.value.trim() || "Manual whitelist tuning";

        if (!IPV4_REGEX.test(ip)) {
            showToast("Format IP tidak valid! Masukkan IPv4 valid (contoh: 192.168.1.100)", "error");
            ipInput.focus();
            return;
        }

        try {
            const res = await fetch(`${API_BASE}/api/whitelist`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ ip_address: ip, reason: reason })
            });
            if (res.ok) {
                ipInput.value = "";
                reasonInput.value = "";
                showToast(`IP ${ip} added to whitelist (blind spot active)`, "success");
                fetchWhitelist();
                fetchStats();
            } else {
                const err = await res.json();
                showToast(`Failed to whitelist IP: ${JSON.stringify(err.detail || err)}`, "error");
            }
        } catch (err) {
            showToast(`Error: ${err.message}`, "error");
        }
    });
}

// Remove IP from Whitelist
window.removeWhitelist = async function(ip) {
    const confirmed = await showConfirmModal({
        title: "Remove Whitelist Entry",
        message: `Remove ${ip} from the whitelist? Correlation rules will resume monitoring telemetry from this IP address.`,
        confirmText: "Remove Whitelist",
        danger: true
    });
    if (!confirmed) return;

    try {
        const res = await fetch(`${API_BASE}/api/whitelist/${encodeURIComponent(ip)}`, {
            method: "DELETE"
        });
        if (res.ok) {
            showToast(`IP ${ip} removed from whitelist`, "success");
            fetchWhitelist();
            fetchStats();
        } else {
            const err = await res.json();
            showToast(`Failed to remove whitelist: ${JSON.stringify(err.detail || err)}`, "error");
        }
    } catch (err) {
        showToast(`Error deleting whitelist: ${err.message}`, "error");
    }
};

// ======================= SOAR ACTIVE DEFENSE =======================

async function fetchIsolatedHosts() {
    try {
        const res = await fetch(`${API_BASE}/api/soar/isolated`);
        if (!res.ok) return;
        const list = await res.json();
        isolatedIpsSet = new Set(list.map(item => item.ip_address));
        renderIsolatedHosts(list);
    } catch (err) {
        console.error("Error fetching isolated hosts:", err);
    }
}

function renderIsolatedHosts(list) {
    if (isolatedCountBadge) isolatedCountBadge.textContent = `${list ? list.length : 0} Quarantined`;

    if (!list || list.length === 0) {
        if (lastIsolatedDataHash !== "empty") {
            lastIsolatedDataHash = "empty";
            if (isolatedTableBody) {
                isolatedTableBody.innerHTML = `
                    <tr>
                        <td colspan="3" class="table-empty">No hosts currently in network quarantine</td>
                    </tr>`;
            }
        }
        return;
    }

    const currentHash = list.map(i => `${i.ip_address}_${i.reason}`).join("|");
    if (currentHash === lastIsolatedDataHash) return;
    lastIsolatedDataHash = currentHash;

    if (isolatedTableBody) {
        isolatedTableBody.innerHTML = list.map(item => `
            <tr>
                <td><strong style="color: #f472b6;">🔒 ${escapeHtml(item.ip_address)}</strong></td>
                <td><span>${escapeHtml(item.reason || "Active containment")}</span></td>
                <td>
                    <button class="btn-action-release" data-action="release-host" data-ip="${escapeHtml(item.ip_address)}" type="button">
                        🔓 Release
                    </button>
                </td>
            </tr>
        `).join("");
    }
}

if (isolatedTableBody) {
    isolatedTableBody.addEventListener("click", async (e) => {
        const btn = e.target.closest("button");
        if (!btn) return;
        const ip = btn.dataset.ip;
        await window.releaseHost(ip);
    });
}

// Fetch SOAR Action Audit Trail
async function fetchSoarAudit() {
    try {
        const res = await fetch(`${API_BASE}/api/soar/audit?limit=15`);
        if (!res.ok) return;
        const auditItems = await res.json();
        renderSoarAudit(auditItems);
    } catch (err) {
        console.error("Error fetching SOAR audit trail:", err);
    }
}

function renderSoarAudit(items) {
    if (!soarAuditList) return;

    if (!items || items.length === 0) {
        if (lastAuditDataHash !== "empty") {
            lastAuditDataHash = "empty";
            soarAuditList.innerHTML = `
                <div class="table-empty">
                    No SOAR playbook containment actions recorded
                </div>`;
        }
        return;
    }

    const currentHash = items.map(i => `${i.timestamp}_${i.ip_address}_${i.action}`).join("|");
    if (currentHash === lastAuditDataHash) return;
    lastAuditDataHash = currentHash;

    soarAuditList.innerHTML = items.map(item => `
        <div class="soar-audit-item ${item.action}">
            <div class="soar-audit-header">
                <strong>${item.action === 'ISOLATE' ? '🔒 HOST QUARANTINED' : '🔓 QUARANTINE RELEASED'}</strong>
                <span>${formatTimestamp(item.timestamp)}</span>
            </div>
            <div>
                Target: <code style="color: #ffffff;">${escapeHtml(item.ip_address)}</code>
            </div>
            <div style="color: var(--text-secondary); font-size: 0.75rem;">
                ${escapeHtml(item.reason || "-")} (${escapeHtml(item.analyst || "SOC Analyst Tier-1")})
            </div>
        </div>
    `).join("");
}

// Global Isolate Host Action
window.isolateHost = async function(ip, reason) {
    let actionReason = reason;
    if (!actionReason) {
        actionReason = await showPromptModal({
            title: "Execute SOAR Quarantine",
            message: `Enter containment justification for host ${ip}:`,
            defaultValue: "Host quarantined due to critical security alert",
            placeholder: "e.g. Inbound volumetric anomaly or brute-force"
        });
    }
    if (!actionReason) return;

    try {
        const res = await fetch(`${API_BASE}/api/soar/isolate`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                ip_address: ip,
                reason: actionReason,
                analyst: "SOC Analyst Tier-1"
            })
        });

        if (res.ok) {
            showToast(`Host ${ip} placed in network quarantine`, "success");
            fetchIsolatedHosts();
            fetchAlerts();
            fetchStats();
            fetchSoarAudit();
        } else {
            const err = await res.json();
            showToast(`Failed to isolate host: ${JSON.stringify(err.detail || err)}`, "error");
        }
    } catch (err) {
        showToast(`Error executing SOAR containment: ${err.message}`, "error");
    }
};

// Global Release Host Action
window.releaseHost = async function(ip) {
    const confirmed = await showConfirmModal({
        title: "Release Quarantine",
        message: `Lift network quarantine for host ${ip}? Inbound traffic from this address will no longer be dropped at Gatekeeper.`,
        confirmText: "Release Host",
        danger: false
    });
    if (!confirmed) return;

    try {
        const res = await fetch(`${API_BASE}/api/soar/release`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                ip_address: ip,
                analyst: "SOC Analyst Tier-1"
            })
        });

        if (res.ok) {
            showToast(`Host ${ip} quarantine lifted`, "success");
            fetchIsolatedHosts();
            fetchAlerts();
            fetchStats();
            fetchSoarAudit();
        } else {
            const err = await res.json();
            showToast(`Failed to release quarantine: ${JSON.stringify(err.detail || err)}`, "error");
        }
    } catch (err) {
        showToast(`Error releasing quarantine: ${err.message}`, "error");
    }
};

// ======================= SUSPENDED USER ACCOUNTS =======================

async function fetchSuspendedUsers() {
    try {
        const res = await fetch(`${API_BASE}/api/soar/suspended-users`);
        if (!res.ok) return;
        const list = await res.json();
        suspendedUsersSet = new Set(list.map(item => item.user_id));
        renderSuspendedUsers(list);
    } catch (err) {
        console.error("Error fetching suspended users:", err);
    }
}

function renderSuspendedUsers(list) {
    if (!suspendedUsersTableBody) return;

    if (!list || list.length === 0) {
        if (lastSuspendedDataHash !== "empty") {
            lastSuspendedDataHash = "empty";
            suspendedUsersTableBody.innerHTML = `
                <tr>
                    <td colspan="3" class="table-empty">No user accounts currently suspended</td>
                </tr>`;
        }
        return;
    }

    const currentHash = list.map(i => `${i.user_id}_${i.reason}`).join("|");
    if (currentHash === lastSuspendedDataHash) return;
    lastSuspendedDataHash = currentHash;

    suspendedUsersTableBody.innerHTML = list.map(item => `
        <tr>
            <td><strong style="color: #fca5a5;">🚫 ${escapeHtml(item.user_id)}</strong></td>
            <td><span>${escapeHtml(item.reason || "Account compromised")}</span></td>
            <td>
                <button class="btn-action-release" data-action="unsuspend-user" data-user="${escapeHtml(item.user_id)}" type="button">
                    🔓 Unsuspend
                </button>
            </td>
        </tr>
    `).join("");
}

if (suspendedUsersTableBody) {
    suspendedUsersTableBody.addEventListener("click", async (e) => {
        const btn = e.target.closest("button");
        if (!btn) return;
        const userId = btn.dataset.user;
        await window.unsuspendUser(userId);
    });
}

// Global Suspend User Action
window.suspendUser = async function(userId, reason) {
    let actionReason = reason;
    if (!actionReason) {
        actionReason = await showPromptModal({
            title: "Suspend User Account",
            message: `Enter justification for account suspension on ${userId}:`,
            defaultValue: "Compromised credentials / impossible travel anomaly",
            placeholder: "e.g. Impossible geo-velocity anomaly detected"
        });
    }
    if (!actionReason) return;

    try {
        const res = await fetch(`${API_BASE}/api/soar/suspend-user`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_id: userId,
                reason: actionReason,
                analyst: "SOC Analyst Tier-1"
            })
        });

        if (res.ok) {
            showToast(`User account ${userId} suspended`, "success");
            fetchSuspendedUsers();
            fetchAlerts();
            fetchStats();
            fetchSoarAudit();
        } else {
            const err = await res.json();
            showToast(`Failed to suspend account: ${JSON.stringify(err.detail || err)}`, "error");
        }
    } catch (err) {
        showToast(`Error executing user suspension: ${err.message}`, "error");
    }
};

// Global Unsuspend User Action
window.unsuspendUser = async function(userId) {
    const confirmed = await showConfirmModal({
        title: "Reactivate User Account",
        message: `Restore and reactivate user account ${userId}?`,
        confirmText: "Reactivate Account",
        danger: false
    });
    if (!confirmed) return;

    try {
        const res = await fetch(`${API_BASE}/api/soar/unsuspend-user`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_id: userId,
                analyst: "SOC Analyst Tier-1"
            })
        });

        if (res.ok) {
            showToast(`User account ${userId} reactivated`, "success");
            fetchSuspendedUsers();
            fetchAlerts();
            fetchStats();
            fetchSoarAudit();
        } else {
            const err = await res.json();
            showToast(`Failed to restore user: ${JSON.stringify(err.detail || err)}`, "error");
        }
    } catch (err) {
        showToast(`Error restoring user account: ${err.message}`, "error");
    }
};

// Isolate Form Submission
if (isolateForm) {
    isolateForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const ipInput = document.getElementById("isolateIp");
        const reasonInput = document.getElementById("isolateReason");
        const ip = ipInput.value.trim();
        const reason = reasonInput.value.trim() || "Manual containment via SOAR Panel";

        if (!IPV4_REGEX.test(ip)) {
            showToast("Format IP tidak valid! Masukkan IPv4 valid (contoh: 192.168.1.100)", "error");
            ipInput.focus();
            return;
        }

        await window.isolateHost(ip, reason);
        ipInput.value = "";
        reasonInput.value = "";
    });
}

// Reset SIEM
if (btnReset) {
    btnReset.addEventListener("click", async () => {
        if (btnReset.disabled) return;
        const confirmed = await showConfirmModal({
            title: "Reset SIEM State",
            message: "Reset all in-memory log ingestion buffers, correlation engine detections, and SOAR active quarantines?",
            confirmText: "Reset State",
            danger: true
        });
        if (!confirmed) return;

        try {
            btnReset.disabled = true;
            btnReset.setAttribute("aria-busy", "true");
            const res = await fetch(`${API_BASE}/api/reset`, { method: "POST" });
            if (res.ok) {
                showToast("SIEM state reset successfully", "success");
                lastAlertsDataHash = "";
                lastLogsDataHash = "";
                lastAuditDataHash = "";
                lastWhitelistDataHash = "";
                lastIsolatedDataHash = "";
                lastSuspendedDataHash = "";
                fetchAlerts();
                fetchStats();
                fetchLogs();
                fetchWhitelist();
                fetchIsolatedHosts();
                fetchSuspendedUsers();
                fetchSoarAudit();
            } else {
                showToast("Failed to reset SIEM state", "error");
            }
        } catch (err) {
            showToast(`Reset error: ${err.message}`, "error");
        } finally {
            btnReset.disabled = false;
            btnReset.removeAttribute("aria-busy");
        }
    });
}

// Browser-based Quick Scenario Execution
document.querySelectorAll(".btn-scenario").forEach(btn => {
    btn.addEventListener("click", async () => {
        const scNum = btn.getAttribute("data-scenario");
        await runScenarioFromBrowser(scNum);
    });
});

async function runScenarioFromBrowser(scNum) {
    const btn = document.querySelector(`.btn-scenario[data-scenario="${scNum}"]`);
    if (btn && btn.disabled) return;
    if (btn) {
        btn.disabled = true;
        btn.setAttribute("aria-busy", "true");
        btn.style.opacity = "0.6";
    }

    try {
        const res = await fetch(`${API_BASE}/api/simulator/replay?scenario=${scNum}`, {
            method: "POST"
        });
        const data = await res.json();

        if (btn) btn.style.opacity = "1";

        let reportMsg = `[TELEMETRY REPLAY FROM LOG FILES]\n\n`;
        reportMsg += `Scenario: ${scNum} - ${data.title || "Attack Telemetry"}\n`;
        if (data.variant) reportMsg += `Variant: ${data.variant}/3 (${data.variant_description || ""})\n`;
        reportMsg += `Source File: ${data.source_file}\n`;
        if (data.logs_processed !== undefined) reportMsg += `Logs Ingested: ${data.logs_processed}\n`;
        if (data.logs_blocked_by_soar) reportMsg += `Blocked by SOAR Gatekeeper: ${data.logs_blocked_by_soar}\n`;
        if (data.alerts_triggered !== undefined) reportMsg += `Alerts Triggered: ${data.alerts_triggered}\n`;
        if (data.message) reportMsg += `\nAnalysis / Findings:\n${data.message}`;

        if (scNum === "6" || scNum === "7" || scNum === "8") {
            await showNoticeModal({
                title: `Telemetry Replay: Scenario ${scNum}`,
                message: reportMsg
            });
        } else {
            triggerScenarioMapBarrage(scNum, data);
        showToast(`Scenario ${scNum} (${data.title || "Telemetry"}) executed: ${data.alerts_triggered || 0} alert(s) triggered`, "info");
        }
    } catch (e) {
        showToast(`Replay scenario failed: ${e.message}`, "error");
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.removeAttribute("aria-busy");
            btn.style.opacity = "1";
        }
    }

    // Refresh telemetry immediately
    setTimeout(() => {
        fetchAlerts();
        fetchStats();
        fetchLogs();
        fetchWhitelist();
        fetchIsolatedHosts();
        fetchSuspendedUsers();
        fetchSoarAudit();
    }, 250);
}

// Escape HTML utility
function escapeHtml(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Initial Call and Recurring 2s Polling
async function pollCycle() {
    if (document.hidden) return;
    const statsOk = await fetchStats();
    if (statsOk) {
        consecutivePollErrors = 0;
        setConnectionState(true);
    } else {
        consecutivePollErrors++;
        if (consecutivePollErrors >= 2) {
            setConnectionState(false);
        }
    }
    fetchAlerts();
    fetchLogs();
    fetchIsolatedHosts();
    fetchSuspendedUsers();
    fetchSoarAudit();
}

// Resume polling immediately when tab returns to foreground
document.addEventListener("visibilitychange", () => {
    if (!document.hidden) {
        pollCycle();
    }
});

pollCycle();
fetchWhitelist();

// Polling interval: 2 seconds as required by PRD
setInterval(pollCycle, 2000);


// ==========================================================================
// REAL-TIME CYBER ATTACK VECTOR MAP & TIMELAPSE SCRUBBER ENGINE
// ==========================================================================

const JAKARTA_HQ = { lat: -6.2088, lon: 106.8456, name: "Jakarta HQ [10.0.1.5]" };

const KNOWN_GEO_CTI = {
    "45.33.32.156": { lat: 32.7767, lon: -96.7970, city: "Dallas", country: "United States", flag: "🇺🇸", actor: "Mirai Botnet" },
    "194.26.29.112": { lat: -4.6796, lon: 55.4920, city: "Victoria", country: "Seychelles", flag: "🇸🇨", actor: "RedLine Bulletproof" },
    "185.220.101.45": { lat: 50.1109, lon: 8.6821, city: "Frankfurt", country: "Germany", flag: "🇩🇪", actor: "Tor Exit Relay" },
    "103.111.201.22": { lat: -6.2088, lon: 106.8456, city: "Jakarta", country: "Indonesia", flag: "🇮🇩", actor: "Telkom Gateway" },
    "194.26.29.50": { lat: 50.1109, lon: 8.6821, city: "Frankfurt", country: "Germany", flag: "🇩🇪", actor: "Tor Exit / Proxy" },
    "182.253.11.88": { lat: -7.2575, lon: 112.7521, city: "Surabaya", country: "Indonesia", flag: "🇮🇩", actor: "ISP Broadband" },
    "198.51.100.22": { lat: 32.7767, lon: -96.7970, city: "Dallas", country: "United States", flag: "🇺🇸", actor: "Commercial VPN" },
    "118.189.20.14": { lat: 1.3521, lon: 103.8198, city: "Singapore", country: "Singapore", flag: "🇸🇬", actor: "StarHub Telecom" },
    "185.220.101.99": { lat: 55.7558, lon: 37.6173, city: "Moscow", country: "Russia", flag: "🇷🇺", actor: "Tor Exit Relay" },
    "185.220.101.5": { lat: 52.3676, lon: 4.9041, city: "Amsterdam", country: "Netherlands", flag: "🇳🇱", actor: "Distributed Brute Bot" },
    "198.51.100.23": { lat: 37.7749, lon: -122.4194, city: "San Francisco", country: "United States", flag: "🇺🇸", actor: "Brute Force Node" },
    "203.0.113.15": { lat: 39.9042, lon: 116.4074, city: "Beijing", country: "China", flag: "🇨🇳", actor: "APT Scanner" },
    "192.168.1.50": { lat: -6.1500, lon: 106.8000, city: "Jakarta LAN", country: "Indonesia", flag: "🇮🇩", actor: "Insider / Infected Workstation" },
    "10.0.1.10": { lat: -6.1800, lon: 106.8200, city: "Jakarta DC", country: "Indonesia", flag: "🇮🇩", actor: "Internal Pivot Host" }
};

// Simplified Equirectangular Continents Polygons [lon, lat]
const WORLD_CONTINENTS = [
    // North America
    [ [-168, 65], [-140, 70], [-95, 70], [-60, 60], [-55, 48], [-70, 42], [-80, 25], [-97, 26], [-81, 8], [-90, 15], [-105, 20], [-120, 35], [-125, 49], [-160, 58], [-168, 65] ],
    // South America
    [ [-80, 8], [-60, 10], [-35, -5], [-38, -15], [-55, -35], [-68, -55], [-75, -50], [-72, -35], [-81, -5], [-80, 8] ],
    // Europe
    [ [-10, 36], [0, 44], [-5, 48], [5, 52], [8, 57], [15, 55], [25, 60], [30, 70], [60, 68], [60, 55], [40, 45], [28, 41], [15, 38], [-5, 36], [-10, 36] ],
    // Africa
    [ [-17, 32], [10, 37], [32, 31], [43, 12], [51, 10], [40, -5], [35, -25], [20, -35], [17, -33], [12, -15], [9, 4], [-15, 12], [-17, 32] ],
    // Asia / Eurasia
    [ [60, 55], [60, 68], [100, 75], [170, 65], [140, 50], [130, 35], [120, 30], [108, 20], [100, 15], [103, 1], [80, 10], [70, 25], [50, 25], [40, 30], [40, 45], [60, 55] ],
    // Australia
    [ [114, -22], [122, -15], [135, -12], [142, -10], [153, -28], [150, -37], [138, -35], [115, -34], [114, -22] ],
    // British Isles
    [ [-10, 50], [-2, 50], [-1, 58], [-6, 58], [-10, 50] ],
    // Japan
    [ [130, 32], [133, 34], [141, 38], [143, 44], [140, 44], [135, 36], [130, 32] ],
    // Sumatra
    [ [95, 5.5], [99, 2.5], [104, -2], [106, -5.8], [103.5, -5.5], [100, -1], [95, 5.5] ],
    // Java
    [ [105.2, -6.0], [109, -6.8], [113, -7.0], [114.5, -8.2], [114, -8.7], [108, -7.6], [105.2, -6.0] ],
    // Kalimantan (Borneo)
    [ [109, 1.2], [113, 6.8], [118, 4.5], [118.5, -3.5], [112, -4.0], [109, 1.2] ],
    // Sulawesi
    [ [119.5, 1.2], [123, 1.2], [125, 1.5], [121, -4.5], [119.5, -5.2], [119.5, 1.2] ],
    // Papua
    [ [131, -1.0], [140, -2.5], [149, -9.5], [141, -8.5], [134, -4.0], [131, -1.0] ]
];

// Fallback deterministic IP to Geo resolver
function resolveIpToGeo(ip) {
    if (!ip) return { lat: 25.0, lon: 0.0, city: "Global", country: "Internet", flag: "🌐", actor: "Threat Observable" };
    if (KNOWN_GEO_CTI[ip]) return KNOWN_GEO_CTI[ip];

    // Check if internal / private subnet
    if (ip.startsWith("10.") || ip.startsWith("192.168.") || ip.startsWith("172.16.") || ip.startsWith("127.")) {
        // Offset near Jakarta HQ to show internal datacenter lateral movement
        const hash = ip.split(".").reduce((acc, part) => (acc * 31 + parseInt(part, 10)) % 1000, 0);
        const offsetLat = ((hash % 100) - 50) * 0.01;
        const offsetLon = (((hash * 7) % 100) - 50) * 0.01;
        return {
            lat: JAKARTA_HQ.lat + offsetLat,
            lon: JAKARTA_HQ.lon + offsetLon,
            city: "Internal Subnet",
            country: "Intranet (Jakarta DC)",
            flag: "🏢",
            actor: "LAN Lateral Movement"
        };
    }

    // Public IP: Deterministic global hash distribution
    const parts = ip.split(".").map(p => parseInt(p, 10) || 0);
    const seed = (parts[0] * 16777619) ^ (parts[1] * 8191) ^ (parts[2] * 257) ^ parts[3];
    const absSeed = Math.abs(seed);

    const lat = ((absSeed % 110) - 45); // -45 to +65 lat
    const lon = (((absSeed * 13) % 320) - 160); // -160 to +160 lon

    return {
        lat: lat,
        lon: lon,
        city: `Autonomous System ${parts[0] * 200}`,
        country: "External Autonomous System",
        flag: "🌐",
        actor: "External Scanner"
    };
}

// Convert Equirectangular coordinates to Canvas X, Y
function geoToCanvas(lat, lon, width, height) {
    // lon: -180 to 180 -> 0 to width
    // lat: 85 to -60 -> 0 to height (crop polar extremes for optimal SOC aspect ratio)
    const minLat = -60;
    const maxLat = 85;
    const clampedLat = Math.max(minLat, Math.min(maxLat, lat));
    const clampedLon = Math.max(-180, Math.min(180, lon));

    const x = ((clampedLon + 180) / 360) * width;
    const y = ((maxLat - clampedLat) / (maxLat - minLat)) * height;
    return { x, y };
}

// Attack Vector Object
class AttackVectorArc {
    constructor({ id, srcIp, srcGeo, dstIp, dstGeo, severity, category, description, timestamp, threatActor }) {
        this.id = id || Math.random().toString(36).substring(2, 9);
        this.srcIp = srcIp;
        this.srcGeo = srcGeo || resolveIpToGeo(srcIp);
        this.dstIp = dstIp || "10.0.1.5";
        this.dstGeo = dstGeo || JAKARTA_HQ;
        this.severity = severity || "MEDIUM";
        this.category = category || "Cyber Incident";
        this.description = description || "Active Attack Vector";
        this.timestamp = timestamp || new Date().toISOString();
        this.threatActor = threatActor || this.srcGeo.actor || "Suspicious Host";

        this.progress = 0.0;
        this.speed = 0.007; // ~2.4s per arc at 60fps
        this.isFinished = false;
        this.ripples = [];
        this.hasImpacted = false;

        // Visual properties based on severity
        if (this.severity === "CRITICAL") {
            this.color = "#ef4444";
            this.glow = "rgba(239, 68, 68, 0.4)";
        } else if (this.severity === "HIGH") {
            this.color = "#f59e0b";
            this.glow = "rgba(245, 158, 11, 0.4)";
        } else if (this.severity === "LOW" || this.severity === "BENIGN") {
            this.color = "#10b981";
            this.glow = "rgba(16, 185, 129, 0.4)";
        } else {
            this.color = "#3b82f6";
            this.glow = "rgba(59, 130, 246, 0.4)";
        }
    }

    update() {
        if (this.progress < 1.0) {
            this.progress += this.speed;
            if (this.progress >= 1.0) {
                this.progress = 1.0;
                if (!this.hasImpacted) {
                    this.hasImpacted = true;
                    // Trigger shockwave ripples at target
                    this.ripples.push({ radius: 3, maxRadius: 28, alpha: 0.85, speed: 0.65 });
                    this.ripples.push({ radius: 0, maxRadius: 22, alpha: 0.70, speed: 0.45 });
                }
            }
        }

        // Update ripple animations
        for (let i = this.ripples.length - 1; i >= 0; i--) {
            const r = this.ripples[i];
            r.radius += r.speed;
            r.alpha -= 0.022;
            if (r.alpha <= 0 || r.radius >= r.maxRadius) {
                this.ripples.splice(i, 1);
            }
        }

        if (this.progress >= 1.0 && this.ripples.length === 0) {
            this.isFinished = true;
        }
    }
}

// Map Engine State
let attackMapCanvas = null;
let mapCtx = null;
let activeAttackArcs = [];
let historicalAttackEvents = [];
let seenAlertIds = new Set();
let isLiveMode = true;
let isTimelapsePlaying = false;
let timelapseSpeed = 1;
let timelapseCurrentIndex = 0;
let timelapsePlaybackTimer = null;
let beaconPulseRadius = 4;
let beaconPulseIncreasing = true;

// Initialize Attack Map Engine
function initAttackMapEngine() {
    attackMapCanvas = document.getElementById("attackMapCanvas");
    if (!attackMapCanvas) return;
    mapCtx = attackMapCanvas.getContext("2d");

    // Handle high DPI displays
    const dpr = window.devicePixelRatio || 1;
    const rect = attackMapCanvas.getBoundingClientRect();
    const logicalWidth = 1200;
    const logicalHeight = 420;
    attackMapCanvas.width = logicalWidth * dpr;
    attackMapCanvas.height = logicalHeight * dpr;
    mapCtx.scale(dpr, dpr);

    // Setup Timelapse UI controls
    setupTimelapseControls();

    // Start 60 FPS animation loop
    requestAnimationFrame(renderAttackMapLoop);

    // Seed initial demo vectors if no attacks yet so operator has immediate visual engagement
    seedInitialThreatTelemetry();
}

function setupTimelapseControls() {
    const btnPlayPause = document.getElementById("btnMapPlayPause");
    const btnLive = document.getElementById("btnMapLive");
    const scrubber = document.getElementById("timelapseScrubber");
    const speedButtons = document.querySelectorAll(".btn-speed");
    const modeBadge = document.getElementById("mapModeBadge");

    if (btnPlayPause) {
        btnPlayPause.addEventListener("click", () => {
            toggleTimelapsePlayPause();
        });
    }

    if (btnLive) {
        btnLive.addEventListener("click", () => {
            switchToLiveMode();
        });
    }

    if (scrubber) {
        scrubber.addEventListener("input", (e) => {
            onScrubberChange(parseInt(e.target.value, 10));
        });
    }

    speedButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            speedButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            timelapseSpeed = parseInt(btn.getAttribute("data-speed"), 10) || 1;
        });
    });
}

function switchToLiveMode() {
    isLiveMode = true;
    isTimelapsePlaying = false;
    const btnPlayPause = document.getElementById("btnMapPlayPause");
    const modeBadge = document.getElementById("mapModeBadge");
    const scrubber = document.getElementById("timelapseScrubber");
    const timeLabel = document.getElementById("timelapseTimestamp");

    if (btnPlayPause) btnPlayPause.textContent = "▶ Play";
    if (modeBadge) {
        modeBadge.textContent = "● LIVE TELEMETRY";
        modeBadge.style.color = "var(--success-green)";
        modeBadge.style.borderColor = "rgba(16, 185, 129, 0.35)";
        modeBadge.style.background = "rgba(16, 185, 129, 0.12)";
    }
    if (scrubber) scrubber.value = 100;
    if (timeLabel) timeLabel.textContent = "LIVE STREAM";
    showToast("Switched to Live Real-Time Telemetry Mode", "info");
}

function toggleTimelapsePlayPause() {
    const btnPlayPause = document.getElementById("btnMapPlayPause");
    const modeBadge = document.getElementById("mapModeBadge");
    const scrubber = document.getElementById("timelapseScrubber");

    if (isTimelapsePlaying) {
        // Pause
        isTimelapsePlaying = false;
        if (btnPlayPause) btnPlayPause.textContent = "▶ Play";
    } else {
        // Start playing
        isLiveMode = false;
        isTimelapsePlaying = true;
        if (btnPlayPause) btnPlayPause.textContent = "⏸ Pause";
        if (modeBadge) {
            modeBadge.textContent = "⏱️ TIMELAPSE REPLAY";
            modeBadge.style.color = "var(--warning-amber)";
            modeBadge.style.borderColor = "rgba(245, 158, 11, 0.35)";
            modeBadge.style.background = "rgba(245, 158, 11, 0.12)";
        }

        // If at end, loop to beginning
        if (scrubber && parseInt(scrubber.value, 10) >= 100) {
            scrubber.value = 0;
            timelapseCurrentIndex = 0;
        }
    }
}

function onScrubberChange(val) {
    isLiveMode = false;
    const modeBadge = document.getElementById("mapModeBadge");
    const timeLabel = document.getElementById("timelapseTimestamp");

    if (modeBadge) {
        modeBadge.textContent = "⏱️ TIMELAPSE REPLAY";
        modeBadge.style.color = "var(--warning-amber)";
        modeBadge.style.borderColor = "rgba(245, 158, 11, 0.35)";
        modeBadge.style.background = "rgba(245, 158, 11, 0.12)";
    }

    if (historicalAttackEvents.length === 0) return;
    const targetIdx = Math.floor((val / 100) * (historicalAttackEvents.length - 1));
    timelapseCurrentIndex = targetIdx;
    const event = historicalAttackEvents[targetIdx];

    if (event) {
        if (timeLabel) {
            const date = new Date(event.timestamp);
            timeLabel.textContent = isNaN(date.getTime()) ? event.timestamp : date.toLocaleTimeString();
        }
        fireAttackVector(event, true);
    }
}

// Fire an attack vector arc on the canvas
function fireAttackVector(eventData, isReplay = false) {
    if (!eventData || !eventData.srcIp) return;

    const arc = new AttackVectorArc(eventData);
    activeAttackArcs.push(arc);

    // Limit concurrent active arcs to prevent canvas lag
    if (activeAttackArcs.length > 15) {
        activeAttackArcs.shift();
    }

    // Save to historical events if new and not already recorded
    if (!isReplay && !historicalAttackEvents.some(e => e.id === arc.id)) {
        historicalAttackEvents.push({
            id: arc.id,
            srcIp: arc.srcIp,
            srcGeo: arc.srcGeo,
            dstIp: arc.dstIp,
            dstGeo: arc.dstGeo,
            severity: arc.severity,
            category: arc.category,
            description: arc.description,
            timestamp: arc.timestamp,
            threatActor: arc.threatActor
        });

        if (historicalAttackEvents.length > 200) {
            historicalAttackEvents.shift();
        }
    }

    // Update HUD Vector readout text
    updateHudVectorReadout(arc);

    // Update active vectors count badge
    const badge = document.getElementById("mapActiveArcsCount");
    if (badge) {
        badge.textContent = `${activeAttackArcs.length} Vector${activeAttackArcs.length === 1 ? '' : 's'}`;
    }
}

function updateHudVectorReadout(arc) {
    const hud = document.getElementById("hudVectorText");
    if (!hud) return;

    const flag = arc.srcGeo.flag || "🌐";
    const country = arc.srcGeo.country || "External";
    const city = arc.srcGeo.city || "";
    const locStr = city ? `${city}, ${country}` : country;

    hud.innerHTML = `
        <span style="color: ${arc.color}; font-weight: 700;">[IN-FLIGHT]</span>
        <span>${flag} <strong>${escapeHtml(arc.srcIp)}</strong> (${escapeHtml(locStr)})</span>
        <span style="color: var(--text-muted);">➔</span>
        <span style="color: #ffffff;">JAKARTA HQ [10.0.1.5]</span>
        <span style="color: var(--border-color);">|</span>
        <span style="color: ${arc.color}; font-weight: 600;">${escapeHtml(arc.severity)}</span>: ${escapeHtml(arc.category)}
        <span style="color: var(--text-muted);">(${escapeHtml(arc.threatActor)})</span>
    `;
}

// Initial threat seeding so operator sees live activity on start
function seedInitialThreatTelemetry() {
    const demoAttacks = [
        {
            srcIp: "194.26.29.112",
            severity: "CRITICAL",
            category: "RedLine C2 Exfiltration",
            description: "Bulletproof offshore gateway beaconing detected",
            threatActor: "RedLine / Bulletproof Inf"
        },
        {
            srcIp: "185.220.101.45",
            severity: "HIGH",
            category: "Tor Credential Stuffing",
            description: "Anonymized brute-force attack from Frankfurt Tor Exit",
            threatActor: "Tor Anonymization Network"
        },
        {
            srcIp: "45.33.32.156",
            severity: "CRITICAL",
            category: "Mirai HTTP Botnet Flood",
            description: "Volumetric L7 DDoS Cannon from Dallas Linode node",
            threatActor: "Mirai-Variant Botnet"
        }
    ];

    demoAttacks.forEach((att, idx) => {
        setTimeout(() => {
            fireAttackVector(att);
        }, idx * 1200 + 400);
    });
}

// Ingest live alerts into the attack map
function processAlertsForAttackMap(alerts) {
    if (!alerts || !Array.isArray(alerts)) return;

    alerts.forEach(alert => {
        if (!seenAlertIds.has(alert.id)) {
            seenAlertIds.add(alert.id);
            if (isLiveMode) {
                const srcIp = alert.ip_address || "194.26.29.112";
                fireAttackVector({
                    id: `alert-${alert.id}`,
                    srcIp: srcIp,
                    severity: alert.severity || "HIGH",
                    category: alert.rule_name || alert.category || "Security Alert",
                    description: alert.description || "",
                    timestamp: alert.timestamp || new Date().toISOString(),
                    threatActor: alert.details && alert.details.threat_actor ? alert.details.threat_actor : undefined
                });
            }
        }
    });
}

// Trigger immediate visual barrage when user clicks scenario simulator buttons
function triggerScenarioMapBarrage(scNum, data) {
    const scenarioMapProfiles = {
        "1": [
            { srcIp: "192.168.1.50", severity: "HIGH", category: "Brute Force Auth", threatActor: "Internal Compromised Host" }
        ],
        "2": [
            { srcIp: "45.33.32.156", severity: "CRITICAL", category: "Mirai DDoS Cannon", threatActor: "Mirai-Variant Botnet" },
            { srcIp: "194.26.29.112", severity: "CRITICAL", category: "Bulletproof Botnet Flood", threatActor: "RedLine / Offshore Inf" },
            { srcIp: "185.220.101.45", severity: "HIGH", category: "Tor Distributed Flooder", threatActor: "Tor Exit Relay" }
        ],
        "3": [
            { srcIp: "103.111.201.22", severity: "LOW", category: "Legitimate Login (Jakarta)", threatActor: "Corporate Employee" },
            { srcIp: "194.26.29.50", severity: "CRITICAL", category: "Impossible Travel Anomaly (Frankfurt)", threatActor: "Compromised VPN Credential" }
        ],
        "4": [
            { srcIp: "185.220.101.5", severity: "HIGH", category: "Distributed SSH Brute Force", threatActor: "Distributed Botnet Node" },
            { srcIp: "198.51.100.23", severity: "HIGH", category: "Distributed Auth Attack", threatActor: "US Proxy Cluster" }
        ],
        "5": [
            { srcIp: "192.168.1.50", severity: "CRITICAL", category: "OT SCADA AC Sabotage", threatActor: "HVAC Thermal Saboteur" }
        ],
        "6": [
            { srcIp: "194.26.29.112", severity: "CRITICAL", category: "Data Exfiltration to Offshore C2", threatActor: "RedLine Infostealer" }
        ],
        "7": [
            { srcIp: "10.0.1.10", severity: "HIGH", category: "Lateral Kerberoasting", threatActor: "AD Pivot Account" }
        ],
        "8": [
            { srcIp: "185.220.101.99", severity: "CRITICAL", category: "Ransomware Staging Arc", threatActor: "LockBit Affiliate" }
        ]
    };

    const attacks = scenarioMapProfiles[scNum] || [
        { srcIp: "194.26.29.112", severity: "HIGH", category: `Scenario ${scNum} Telemetry`, threatActor: "Simulated Threat" }
    ];

    attacks.forEach((att, idx) => {
        setTimeout(() => {
            fireAttackVector(att);
        }, idx * 450);
    });
}

// 60 FPS Render Loop
function renderAttackMapLoop(timestamp) {
    if (!attackMapCanvas || !mapCtx) return;

    const width = 1200;
    const height = 420;

    // 1. Clear background
    mapCtx.fillStyle = "#050608";
    mapCtx.fillRect(0, 0, width, height);

    // 2. Draw subtle latitude / longitude graticules
    mapCtx.strokeStyle = "#12151d";
    mapCtx.lineWidth = 1;
    mapCtx.setLineDash([2, 4]);

    // Longitude lines (every 30 degrees)
    for (let lon = -150; lon <= 150; lon += 30) {
        const p1 = geoToCanvas(85, lon, width, height);
        const p2 = geoToCanvas(-60, lon, width, height);
        mapCtx.beginPath();
        mapCtx.moveTo(p1.x, p1.y);
        mapCtx.lineTo(p2.x, p2.y);
        mapCtx.stroke();
    }

    // Latitude lines (every 20 degrees)
    for (let lat = -40; lat <= 80; lat += 20) {
        const p1 = geoToCanvas(lat, -180, width, height);
        const p2 = geoToCanvas(lat, 180, width, height);
        mapCtx.beginPath();
        mapCtx.moveTo(p1.x, p1.y);
        mapCtx.lineTo(p2.x, p2.y);
        mapCtx.stroke();
    }
    mapCtx.setLineDash([]); // Reset line dash

    // 3. Draw Continents Silhouettes
    mapCtx.fillStyle = "#0f131a";
    mapCtx.strokeStyle = "#1e2633";
    mapCtx.lineWidth = 1;

    WORLD_CONTINENTS.forEach(poly => {
        if (!poly || poly.length < 3) return;
        mapCtx.beginPath();
        const start = geoToCanvas(poly[0][1], poly[0][0], width, height);
        mapCtx.moveTo(start.x, start.y);
        for (let i = 1; i < poly.length; i++) {
            const pt = geoToCanvas(poly[i][1], poly[i][0], width, height);
            mapCtx.lineTo(pt.x, pt.y);
        }
        mapCtx.closePath();
        mapCtx.fill();
        mapCtx.stroke();
    });

    // 4. Draw Equator Reference Line
    const eqStart = geoToCanvas(0, -180, width, height);
    const eqEnd = geoToCanvas(0, 180, width, height);
    mapCtx.strokeStyle = "rgba(255, 255, 255, 0.04)";
    mapCtx.beginPath();
    mapCtx.moveTo(eqStart.x, eqStart.y);
    mapCtx.lineTo(eqEnd.x, eqEnd.y);
    mapCtx.stroke();

    // 5. Draw Jakarta HQ Destination Pin & Pulsing Radar Beacon
    const hqPos = geoToCanvas(JAKARTA_HQ.lat, JAKARTA_HQ.lon, width, height);

    // Pulsing Beacon
    beaconPulseRadius += beaconPulseIncreasing ? 0.15 : -0.15;
    if (beaconPulseRadius > 14) beaconPulseIncreasing = false;
    if (beaconPulseRadius < 4) beaconPulseIncreasing = true;

    // Outer beacon radar wave
    mapCtx.strokeStyle = "rgba(16, 185, 129, 0.35)";
    mapCtx.lineWidth = 1.5;
    mapCtx.beginPath();
    mapCtx.arc(hqPos.x, hqPos.y, beaconPulseRadius, 0, Math.PI * 2);
    mapCtx.stroke();

    // Inner target core
    mapCtx.fillStyle = "#10b981";
    mapCtx.beginPath();
    mapCtx.arc(hqPos.x, hqPos.y, 4, 0, Math.PI * 2);
    mapCtx.fill();

    // Target Label
    mapCtx.font = "600 11px var(--font-mono), monospace";
    mapCtx.fillStyle = "#e5e7eb";
    mapCtx.fillText("JAKARTA HQ", hqPos.x + 8, hqPos.y - 6);
    mapCtx.font = "400 9px var(--font-mono), monospace";
    mapCtx.fillStyle = "#9ca3af";
    mapCtx.fillText("[10.0.1.5]", hqPos.x + 8, hqPos.y + 6);

    // 6. Draw and Update Attack Vector Arcs
    for (let i = activeAttackArcs.length - 1; i >= 0; i--) {
        const arc = activeAttackArcs[i];
        arc.update();

        const p0 = geoToCanvas(arc.srcGeo.lat, arc.srcGeo.lon, width, height);
        const p2 = geoToCanvas(arc.dstGeo.lat, arc.dstGeo.lon, width, height);

        // Compute parabolic control point
        const midX = (p0.x + p2.x) / 2;
        const dist = Math.hypot(p2.x - p0.x, p2.y - p0.y);
        const arcHeight = Math.max(38, Math.min(140, dist * 0.38));
        const midY = Math.min(p0.y, p2.y) - arcHeight;

        // Draw Origin Pin
        mapCtx.fillStyle = arc.color;
        mapCtx.beginPath();
        mapCtx.arc(p0.x, p0.y, 3, 0, Math.PI * 2);
        mapCtx.fill();

        // Draw Origin Label (Subtle IP)
        mapCtx.font = "500 9px var(--font-mono), monospace";
        mapCtx.fillStyle = "rgba(229, 231, 235, 0.75)";
        mapCtx.fillText(arc.srcIp, p0.x + 5, p0.y + 3);

        // Draw faint guide trajectory curve
        mapCtx.strokeStyle = "rgba(255, 255, 255, 0.08)";
        mapCtx.lineWidth = 1;
        mapCtx.setLineDash([3, 4]);
        mapCtx.beginPath();
        mapCtx.moveTo(p0.x, p0.y);
        mapCtx.quadraticCurveTo(midX, midY, p2.x, p2.y);
        mapCtx.stroke();
        mapCtx.setLineDash([]); // Reset

        // Draw comet projectile along quadratic Bezier curve
        const t = Math.min(1.0, arc.progress);
        const curX = (1 - t) * (1 - t) * p0.x + 2 * (1 - t) * t * midX + t * t * p2.x;
        const curY = (1 - t) * (1 - t) * p0.y + 2 * (1 - t) * t * midY + t * t * p2.y;

        // Draw comet tail (5 trailing segments)
        const tailSegments = 6;
        for (let s = 1; s <= tailSegments; s++) {
            const tailT = Math.max(0, t - (s * 0.025));
            const tailX = (1 - tailT) * (1 - tailT) * p0.x + 2 * (1 - tailT) * tailT * midX + tailT * tailT * p2.x;
            const tailY = (1 - tailT) * (1 - tailT) * p0.y + 2 * (1 - tailT) * tailT * midY + tailT * tailT * p2.y;
            const tailAlpha = (1 - (s / tailSegments)) * 0.6;

            mapCtx.strokeStyle = arc.color;
            mapCtx.globalAlpha = tailAlpha;
            mapCtx.lineWidth = Math.max(1, 3.5 - (s * 0.5));
            mapCtx.beginPath();
            mapCtx.moveTo(curX, curY);
            mapCtx.lineTo(tailX, tailY);
            mapCtx.stroke();
        }
        mapCtx.globalAlpha = 1.0; // Reset alpha

        // Draw projectile head (bright particle)
        mapCtx.fillStyle = "#ffffff";
        mapCtx.beginPath();
        mapCtx.arc(curX, curY, 3, 0, Math.PI * 2);
        mapCtx.fill();

        // Projectile outer halo
        mapCtx.strokeStyle = arc.color;
        mapCtx.lineWidth = 1.5;
        mapCtx.beginPath();
        mapCtx.arc(curX, curY, 5, 0, Math.PI * 2);
        mapCtx.stroke();

        // Draw Impact Shockwave Ripples at Target
        arc.ripples.forEach(rip => {
            mapCtx.strokeStyle = arc.color;
            mapCtx.globalAlpha = Math.max(0, rip.alpha);
            mapCtx.lineWidth = 1.5;
            mapCtx.beginPath();
            mapCtx.arc(p2.x, p2.y, rip.radius, 0, Math.PI * 2);
            mapCtx.stroke();
        });
        mapCtx.globalAlpha = 1.0; // Reset

        // Clean up finished arcs
        if (arc.isFinished) {
            activeAttackArcs.splice(i, 1);
            const badge = document.getElementById("mapActiveArcsCount");
            if (badge) {
                badge.textContent = `${activeAttackArcs.length} Vector${activeAttackArcs.length === 1 ? '' : 's'}`;
            }
        }
    }

    // 7. Handle Timelapse Playback progression
    if (isTimelapsePlaying && historicalAttackEvents.length > 0) {
        timelapseCurrentIndex += (0.15 * timelapseSpeed);
        if (timelapseCurrentIndex >= historicalAttackEvents.length) {
            timelapseCurrentIndex = 0; // Loop or pause
        }

        const idx = Math.floor(timelapseCurrentIndex);
        const scrubber = document.getElementById("timelapseScrubber");
        const timeLabel = document.getElementById("timelapseTimestamp");

        const progressPercent = Math.floor((idx / (historicalAttackEvents.length - 1 || 1)) * 100);
        if (scrubber) scrubber.value = progressPercent;

        const event = historicalAttackEvents[idx];
        if (event && timeLabel) {
            const d = new Date(event.timestamp);
            timeLabel.textContent = isNaN(d.getTime()) ? event.timestamp : d.toLocaleTimeString();
        }

        // Fire event if just reached integer frame
        if (Math.abs(timelapseCurrentIndex - idx) < 0.16) {
            if (event && !activeAttackArcs.some(a => a.id === event.id && !a.isFinished)) {
                fireAttackVector(event, true);
            }
        }
    }

    requestAnimationFrame(renderAttackMapLoop);
}

// Hook map initialization into DOM ready
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initAttackMapEngine);
} else {
    initAttackMapEngine();
}
