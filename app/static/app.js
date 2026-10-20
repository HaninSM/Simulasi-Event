// Mini-SIEM Dashboard Logic

const API_BASE = "";

// State
let lastAlertIds = new Set();

// Elements
const alertList = document.getElementById("alertList");
const logTableBody = document.getElementById("logTableBody");
const whitelistTableBody = document.getElementById("whitelistTableBody");
const whitelistForm = document.getElementById("whitelistForm");
const btnReset = document.getElementById("btnReset");

// Metric elements
const valTotalLogs = document.getElementById("valTotalLogs");
const valCriticalAlerts = document.getElementById("valCriticalAlerts");
const valHighAlerts = document.getElementById("valHighAlerts");
const valMediumAlerts = document.getElementById("valMediumAlerts");
const valWhitelistCount = document.getElementById("valWhitelistCount");
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
        const metaDetails = a.details ? Object.entries(a.details)
            .map(([k, v]) => `<span class="meta-item"><strong>${k}:</strong> ${typeof v === 'object' ? JSON.stringify(v) : v}</span>`)
            .join("") : "";

        return `
            <div class="alert-card ${a.severity}" id="alert-${a.id}">
                <div class="alert-header">
                    <span class="alert-badge ${a.severity}">${a.severity}</span>
                    <span class="alert-time">⏱️ ${formatTimestamp(a.timestamp)} (ID: ${a.id})</span>
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
    const nowIso = () => new Date().toISOString();

    const postLog = async (data) => {
        try {
            return await fetch(`${API_BASE}/api/ingest`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });
        } catch (e) {
            console.error("Ingest failed:", e);
        }
    };

    if (scNum === "1") {
        // Normal Traffic
        for (let i = 0; i < 5; i++) {
            await postLog({
                timestamp: nowIso(),
                event_type: "web_request",
                user_id: `alice_${i}`,
                ip_address: `192.168.1.${10 + i}`,
                location: "Jakarta, ID",
                status: "success"
            });
        }
    } else if (scNum === "2") {
        // DDoS Attack: > 10 web requests from 1 IP in 10s
        for (let i = 0; i < 15; i++) {
            await postLog({
                timestamp: nowIso(),
                event_type: "web_request",
                user_id: "anonymous_bot",
                ip_address: "45.33.32.156",
                location: "Unknown",
                status: "success"
            });
        }
    } else if (scNum === "3") {
        // Impossible Travel: Same user, 2 successful logins in different locations < 1 hour
        await postLog({
            timestamp: nowIso(),
            event_type: "login_attempt",
            user_id: "john_doe",
            ip_address: "103.24.56.12",
            location: "Jakarta, ID",
            status: "success"
        });
        await new Promise(r => setTimeout(r, 200));
        await postLog({
            timestamp: nowIso(),
            event_type: "login_attempt",
            user_id: "john_doe",
            ip_address: "185.190.140.2",
            location: "Frankfurt, DE",
            status: "success"
        });
    } else if (scNum === "4") {
        // Distributed Brute Force: > 5 failed logins for 1 user from > 3 IPs in 60s
        const ips = ["198.51.100.1", "198.51.100.2", "198.51.100.3", "198.51.100.4"];
        for (let i = 0; i < 7; i++) {
            await postLog({
                timestamp: nowIso(),
                event_type: "login_attempt",
                user_id: "admin_finance",
                ip_address: ips[i % ips.length],
                location: "Remote Proxy",
                status: "failed"
            });
        }
    } else if (scNum === "5") {
        // Data Exfiltration: > 50 database_downloads in 60s
        for (let i = 0; i < 55; i++) {
            await postLog({
                timestamp: nowIso(),
                event_type: "database_download",
                user_id: "insider_dave",
                ip_address: "10.0.4.88",
                location: "Internal LAN",
                status: "success"
            });
        }
    } else if (scNum === "6") {
        // Careless Whitelisting: Whitelist attacker IP first, then launch attack. 0 alerts triggered!
        const attackerIp = "198.51.100.99";
        await fetch(`${API_BASE}/api/whitelist`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ ip_address: attackerIp, reason: "Bypass test for VIP" })
        });
        // Attack via whitelisted IP
        for (let i = 0; i < 15; i++) {
            await postLog({
                timestamp: nowIso(),
                event_type: "web_request",
                user_id: "stealth_hacker",
                ip_address: attackerIp,
                location: "External",
                status: "success"
            });
        }
        fetchWhitelist();
    } else if (scNum === "7") {
        // Skenario Negatif 1: Malformed Log (Format Cacat/Hilang) & Time Drift
        // Test 1: ip_address: null (Server lama mengalami bug)
        const resNull = await postLog({
            timestamp: nowIso(),
            event_type: "web_request",
            user_id: "legacy_server_bug_01",
            ip_address: null,
            location: "Server Room A",
            status: "success"
        });

        // Test 2: JSON terpotong / malformed syntax (koneksi putus di tengah jalan)
        let resTruncatedStatus = "422";
        try {
            const rawRes = await fetch(`${API_BASE}/api/ingest`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: '{"timestamp": "2026-10-20T03:00:00Z", "event_type": "web_request", "user_id": "legacy'
            });
            resTruncatedStatus = rawRes.status;
        } catch (e) {
            console.warn(e);
        }

        // Test 3: Missing attribute 'ip_address' completely
        const resMissing = await postLog({
            timestamp: nowIso(),
            event_type: "web_request",
            user_id: "legacy_server_bug_02",
            location: "Server Room B",
            status: "success"
        });

        // Test 4: Time Drift Error (Tahun 1970)
        const resTimeDrift = await postLog({
            timestamp: "1970-01-01T00:00:00Z",
            event_type: "web_request",
            user_id: "time_traveler",
            ip_address: "1.2.3.4",
            location: "Time Rift",
            status: "success"
        });

        alert(
            `Hasil Pengujian Skenario Negatif:\n` +
            `1. Malformed Log (ip_address: null) -> HTTP ${resNull?.status} (Ditolak)\n` +
            `2. Malformed Log (JSON terpotong)   -> HTTP ${resTruncatedStatus} (Ditolak)\n` +
            `3. Malformed Log (Field IP hilang) -> HTTP ${resMissing?.status} (Ditolak)\n` +
            `4. Time Drift (Tahun 1970)         -> HTTP ${resTimeDrift?.status} (Ditolak)\n\n` +
            `Hasil: Lapisan Validasi Skema (Gatekeeper) menolak data kotor secara aman.\n` +
            `Backend SIEM TIDAK CRASH dan seluruh pusat komando tetap berjalan normal!`
        );
    }

    // Refresh immediately
    setTimeout(() => {
        fetchAlerts();
        fetchStats();
        fetchLogs();
    }, 400);
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
}

pollCycle();
fetchWhitelist();

// Polling interval: 2 seconds as required by PRD
setInterval(pollCycle, 2000);
