// Mini-SIEM Dashboard Logic

const API_BASE = "";

// State
let lastAlertIds = new Set();
let isolatedIpsSet = new Set();
let suspendedUsersSet = new Set();

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

// 1. Fetch Alerts (Runs every 2 seconds as required by PRD)
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
    alertCountBadge.textContent = `${alerts.length} Total`;

    if (!alerts || alerts.length === 0) {
        alertList.innerHTML = `
            <div class="empty-state">
                Menunggu deteksi insiden keamanan...<br>
                Gunakan Simulator di sebelah kanan untuk memicu skenario serangan.
            </div>`;
        return;
    }

    alertList.innerHTML = alerts.map(a => {
        const isCritical = a.severity === "KRITIS";
        const isHostContained = a.ip_address && isolatedIpsSet.has(a.ip_address);
        const isUserSuspended = a.user_id && suspendedUsersSet.has(a.user_id);
        const isContained = a.status === "CONTAINED" || isHostContained || isUserSuspended;

        const metaDetails = a.details ? Object.entries(a.details)
            .map(([k, v]) => `<span class="meta-item"><strong>${k}:</strong> ${typeof v === 'object' ? JSON.stringify(v) : v}</span>`)
            .join("") : "";

        let soarHostButton = "";
        if (a.ip_address) {
            if (isHostContained) {
                soarHostButton = `
                    <button class="btn-action-release" onclick="releaseHost('${escapeHtml(a.ip_address)}')">
                        🔓 Release Host
                    </button>
                `;
            } else {
                soarHostButton = `
                    <button class="btn-action-isolate" onclick="isolateHost('${escapeHtml(a.ip_address)}', 'Containment for alert ${a.id}')">
                        🔒 Isolate Host
                    </button>
                `;
            }
        }

        let soarUserButton = "";
        if (a.user_id) {
            if (isUserSuspended) {
                soarUserButton = `
                    <button class="btn-action-release" onclick="unsuspendUser('${escapeHtml(a.user_id)}')">
                        🔓 Unsuspend User
                    </button>
                `;
            } else {
                soarUserButton = `
                    <button class="btn-action-suspend" onclick="suspendUser('${escapeHtml(a.user_id)}', 'Identity lockdown for alert ${a.id}')">
                        🚫 Suspend User
                    </button>
                `;
            }
        }

        return `
            <div class="alert-card ${a.severity} ${isContained ? 'CONTAINED' : ''}" id="alert-${a.id}">
                <div class="alert-header">
                    <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                        <span class="alert-badge ${a.severity}">${a.severity}</span>
                        ${isHostContained ? `<span class="badge-contained">🔒 HOST ISOLATED</span>` : ""}
                        ${isUserSuspended ? `<span class="badge-contained" style="border-color:#ef4444; color:#f87171;">🚫 USER SUSPENDED</span>` : ""}
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.4rem; flex-wrap: wrap;">
                        <span class="alert-time">⏱️ ${formatTimestamp(a.timestamp)} (ID: ${a.id})</span>
                        ${soarHostButton}
                        ${soarUserButton}
                    </div>
                </div>
                <div class="alert-rule">${escapeHtml(a.rule_name)}</div>
                <div class="alert-desc">${escapeHtml(a.description)}</div>
                ${metaDetails ? `<div class="alert-meta">${metaDetails}</div>` : ""}
            </div>
        `;
    }).join("");
}

// 2. Fetch Stats & Metrics
async function fetchStats() {
    try {
        const res = await fetch(`${API_BASE}/api/stats`);
        if (!res.ok) return;
        const stats = await res.json();

        valTotalLogs.textContent = stats.total_logs_ingested;
        valCriticalAlerts.textContent = stats.alerts_by_severity.KRITIS || 0;
        valHighAlerts.textContent = stats.alerts_by_severity.TINGGI || 0;
        valMediumAlerts.textContent = stats.alerts_by_severity.MENENGAH || 0;
        valWhitelistCount.textContent = stats.whitelist_count || 0;
        if (valWatchlistCount) valWatchlistCount.textContent = stats.watchlist_count || 0;
        if (valColdCount) valColdCount.textContent = stats.cold_archive_count || 0;
        if (valIsolatedCount) valIsolatedCount.textContent = stats.isolated_hosts_count || 0;
        if (valSuspendedUsersCount) valSuspendedUsersCount.textContent = stats.suspended_users_count || 0;
        if (valBlockedCount) valBlockedCount.textContent = stats.blocked_containment_count || 0;
    } catch (err) {
        console.error("Error fetching stats:", err);
    }
}



// 3. Fetch Recent Ingestion Logs
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
    logCountBadge.textContent = `${logs.length} Recent`;

    if (!logs || logs.length === 0) {
        logTableBody.innerHTML = `
            <tr>
                <td colspan="6" class="empty-state">Belum ada log yang masuk via POST /api/ingest</td>
            </tr>`;
        return;
    }

    logTableBody.innerHTML = logs.map(l => `
        <tr class="log-row">
            <td>${formatTimestamp(l.timestamp)}</td>
            <td><code style="color:var(--accent-cyan);">${escapeHtml(l.event_type)}</code></td>
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

// 4. Fetch Whitelist
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
        whitelistTableBody.innerHTML = `
            <tr>
                <td colspan="3" style="text-align: center; color: var(--text-muted);">Tidak ada IP yang di-whitelist</td>
            </tr>`;
        return;
    }

    whitelistTableBody.innerHTML = list.map(item => `
        <tr>
            <td><strong>${escapeHtml(item.ip_address)}</strong></td>
            <td>${escapeHtml(item.reason || "-")}</td>
            <td>
                <button class="btn-sm-delete" onclick="removeWhitelist('${escapeHtml(item.ip_address)}')">
                    🗑️ Hapus
                </button>
            </td>
        </tr>
    `).join("");
}

// Add IP to Whitelist
whitelistForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const ip = document.getElementById("whitelistIp").value.trim();
    const reason = document.getElementById("whitelistReason").value.trim();

    try {
        const res = await fetch(`${API_BASE}/api/whitelist`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ ip_address: ip, reason: reason })
        });
        if (res.ok) {
            document.getElementById("whitelistIp").value = "";
            document.getElementById("whitelistReason").value = "";
            fetchWhitelist();
            fetchStats();
        } else {
            const err = await res.json();
            alert(`Gagal menambah whitelist: ${JSON.stringify(err.detail || err)}`);
        }
    } catch (err) {
        alert(`Error: ${err.message}`);
    }
});

// Remove IP from Whitelist
window.removeWhitelist = async function(ip) {
    if (!confirm(`Hapus ${ip} dari whitelist?`)) return;
    try {
        const res = await fetch(`${API_BASE}/api/whitelist/${encodeURIComponent(ip)}`, {
            method: "DELETE"
        });
        if (res.ok) {
            fetchWhitelist();
            fetchStats();
        }
    } catch (err) {
        alert(`Error deleting whitelist: ${err.message}`);
    }
};

// ---------------- SOAR ACTIVE DEFENSE (CONTAINMENT) ----------------

// Fetch Quarantined / Isolated Hosts
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
        if (isolatedTableBody) {
            isolatedTableBody.innerHTML = `
                <tr>
                    <td colspan="3" style="text-align: center; color: var(--text-muted);">Tidak ada host dalam karantina</td>
                </tr>`;
        }
        return;
    }

    if (isolatedTableBody) {
        isolatedTableBody.innerHTML = list.map(item => `
            <tr>
                <td><strong style="color: #ec4899;">🔒 ${escapeHtml(item.ip_address)}</strong></td>
                <td><span style="font-size: 0.72rem;">${escapeHtml(item.reason || "Manual containment")}</span></td>
                <td>
                    <button class="btn-action-release" onclick="releaseHost('${escapeHtml(item.ip_address)}')">
                        🔓 Release
                    </button>
                </td>
            </tr>
        `).join("");
    }
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
        soarAuditList.innerHTML = `
            <div style="font-size: 0.75rem; color: var(--text-muted); text-align: center; padding: 0.5rem;">
                Belum ada aksi penindakan SOAR
            </div>`;
        return;
    }

    soarAuditList.innerHTML = items.map(item => `
        <div class="soar-audit-item ${item.action}">
            <div class="soar-audit-header">
                <strong>${item.action === 'ISOLATE' ? '🔒 HOST QUARANTINED' : '🔓 QUARANTINE RELEASED'}</strong>
                <span>${formatTimestamp(item.timestamp)}</span>
            </div>
            <div>
                Target: <code style="color: #fff;">${escapeHtml(item.ip_address)}</code>
            </div>
            <div style="color: var(--text-secondary); font-size: 0.7rem;">
                ${escapeHtml(item.reason || "-")} (${escapeHtml(item.analyst || "SOC Analyst")})
            </div>
        </div>
    `).join("");
}

// Global Isolate Host Action
window.isolateHost = async function(ip, reason) {
    const actionReason = reason || prompt(`Alasan penindakan isolasi host ${ip}:`, "Host quarantined due to critical security alert");
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
            fetchIsolatedHosts();
            fetchAlerts();
            fetchStats();
            fetchSoarAudit();
        } else {
            const err = await res.json();
            alert(`Gagal mengisolasi host: ${JSON.stringify(err.detail || err)}`);
        }
    } catch (err) {
        alert(`Error executing SOAR containment: ${err.message}`);
    }
};

// Global Release Host Action
window.releaseHost = async function(ip) {
    if (!confirm(`Lepas karantina jaringan untuk host ${ip}?`)) return;

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
            fetchIsolatedHosts();
            fetchAlerts();
            fetchStats();
            fetchSoarAudit();
        } else {
            const err = await res.json();
            alert(`Gagal melepas karantina: ${JSON.stringify(err.detail || err)}`);
        }
    } catch (err) {
        alert(`Error releasing quarantine: ${err.message}`);
    }
};

// Fetch Suspended Users
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
        suspendedUsersTableBody.innerHTML = `
            <tr>
                <td colspan="3" style="text-align: center; color: var(--text-muted);">Tidak ada akun user yang dibekukan</td>
            </tr>`;
        return;
    }

    suspendedUsersTableBody.innerHTML = list.map(item => `
        <tr>
            <td><strong style="color: #f87171;">🚫 ${escapeHtml(item.user_id)}</strong></td>
            <td><span style="font-size: 0.72rem;">${escapeHtml(item.reason || "Account compromised")}</span></td>
            <td>
                <button class="btn-action-release" onclick="unsuspendUser('${escapeHtml(item.user_id)}')">
                    🔓 Unsuspend
                </button>
            </td>
        </tr>
    `).join("");
}

// Global Suspend User Action
window.suspendUser = async function(userId, reason) {
    const actionReason = reason || prompt(`Alasan pembekuan akun ${userId}:`, "Compromised credentials / impossible travel anomaly");
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
            fetchSuspendedUsers();
            fetchAlerts();
            fetchStats();
            fetchSoarAudit();
        } else {
            const err = await res.json();
            alert(`Gagal membekukan akun user: ${JSON.stringify(err.detail || err)}`);
        }
    } catch (err) {
        alert(`Error executing user suspension: ${err.message}`);
    }
};

// Global Unsuspend User Action
window.unsuspendUser = async function(userId) {
    if (!confirm(`Pulihkan dan aktifkan kembali akun user ${userId}?`)) return;

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
            fetchSuspendedUsers();
            fetchAlerts();
            fetchStats();
            fetchSoarAudit();
        } else {
            const err = await res.json();
            alert(`Gagal memulihkan akun user: ${JSON.stringify(err.detail || err)}`);
        }
    } catch (err) {
        alert(`Error restoring user account: ${err.message}`);
    }
};


// Isolate Form Submission
if (isolateForm) {
    isolateForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const ip = document.getElementById("isolateIp").value.trim();
        const reason = document.getElementById("isolateReason").value.trim() || "Manual containment via SOAR Panel";
        await window.isolateHost(ip, reason);
        document.getElementById("isolateIp").value = "";
        document.getElementById("isolateReason").value = "";
    });
}


// Reset SIEM
btnReset.addEventListener("click", async () => {
    if (!confirm("Reset database dan state korelasi SIEM?")) return;
    try {
        const res = await fetch(`${API_BASE}/api/reset`, { method: "POST" });
        if (res.ok) {
            fetchAlerts();
            fetchStats();
            fetchLogs();
            fetchWhitelist();
            fetchIsolatedHosts();
            fetchSuspendedUsers();
            fetchSoarAudit();
        }
    } catch (err) {
        alert(`Reset error: ${err.message}`);
    }
});

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

        let alertMsg = `[LOG REPLAY DARI BERKAS FISIK]\n`;
        alertMsg += `Skenario: ${scNum} - ${data.title || "Attack Telemetry"}\n`;
        if (data.variant) alertMsg += `Varian: ${data.variant}/3 (${data.variant_description || ""})\n`;
        alertMsg += `Berkas Sumber: ${data.source_file}\n`;
        if (data.logs_processed !== undefined) alertMsg += `Jumlah Log Diproses: ${data.logs_processed}\n`;
        if (data.logs_blocked_by_soar) alertMsg += `Log Diblokir SOAR (Karantina/Suspensi): ${data.logs_blocked_by_soar}\n`;
        if (data.alerts_triggered !== undefined) alertMsg += `Alarm Dipicu: ${data.alerts_triggered}\n`;
        if (data.message) alertMsg += `\nKeterangan:\n${data.message}`;

        if (scNum === "6" || scNum === "7" || scNum === "8") {
            alert(alertMsg);
        } else {
            console.log(alertMsg);
        }
    } catch (e) {
        console.error("Replay scenario failed:", e);
    }

    // Refresh immediately
    setTimeout(() => {
        fetchAlerts();
        fetchStats();
        fetchLogs();
        fetchWhitelist();
        fetchIsolatedHosts();
        fetchSuspendedUsers();
        fetchSoarAudit();
    }, 300);
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
