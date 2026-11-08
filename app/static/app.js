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

// ======================= NON-BLOCKING MODAL & TOAST SYSTEM =======================

function closeModal(result = null) {
    if (modalOverlay) {
        modalOverlay.hidden = true;
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

function showConfirmModal({ title = "Confirm Action", message = "", confirmText = "Confirm", cancelText = "Cancel", danger = false }) {
    return new Promise((resolve) => {
        activeModalResolve = resolve;
        if (!modalOverlay) return resolve(false);

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
    } catch (err) {
        console.error("Error fetching alerts:", err);
    }
}

function renderAlerts(alerts) {
    if (alertCountBadge) alertCountBadge.textContent = `${alerts.length} Total`;

    if (!alerts || alerts.length === 0) {
        if (lastAlertsDataHash !== "empty") {
            lastAlertsDataHash = "empty";
            alertList.innerHTML = `
                <div class="empty-state">
                    Awaiting security incident detection.<br>
                    Trigger an attack scenario from the Simulator tab to evaluate detection rules.
                </div>`;
        }
        return;
    }

    const currentHash = alerts.map(a => `${a.id}_${a.severity}_${a.status}_${isolatedIpsSet.has(a.ip_address)}_${suspendedUsersSet.has(a.user_id)}`).join("|");
    if (currentHash === lastAlertsDataHash) {
        return; // No DOM mutation needed, prevents selection wipe and repaint
    }
    lastAlertsDataHash = currentHash;

    const fragment = document.createDocumentFragment();

    alerts.forEach(a => {
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
                <div class="alert-cti" style="margin-top: 0.55rem; padding: 0.45rem 0.65rem; background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-left: 3px solid ${verdictColor}; border-radius: 4px; font-size: 0.75rem;">
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

        card.innerHTML = `
            <div class="alert-header">
                <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
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

        fragment.appendChild(card);
    });

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
        if (!res.ok) return;
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
    } catch (err) {
        console.error("Error fetching stats:", err);
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
        await window.isolateHost(ip, reason);
        ipInput.value = "";
        reasonInput.value = "";
    });
}

// Reset SIEM
if (btnReset) {
    btnReset.addEventListener("click", async () => {
        const confirmed = await showConfirmModal({
            title: "Reset SIEM State",
            message: "Reset all in-memory log ingestion buffers, correlation engine detections, and SOAR active quarantines?",
            confirmText: "Reset State",
            danger: true
        });
        if (!confirmed) return;

        try {
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
            }
        } catch (err) {
            showToast(`Reset error: ${err.message}`, "error");
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
    try {
        const btn = document.querySelector(`.btn-scenario[data-scenario="${scNum}"]`);
        if (btn) btn.style.opacity = "0.6";

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
            showToast(`Scenario ${scNum} (${data.title || "Telemetry"}) executed: ${data.alerts_triggered || 0} alert(s) triggered`, "info");
        }
    } catch (e) {
        showToast(`Replay scenario failed: ${e.message}`, "error");
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
function pollCycle() {
    fetchAlerts();
    fetchStats();
    fetchLogs();
    fetchIsolatedHosts();
    fetchSuspendedUsers();
    fetchSoarAudit();
}

pollCycle();
fetchWhitelist();

// Polling interval: 2 seconds as required by PRD
setInterval(pollCycle, 2000);
