// SentinelAI Next-Gen Autonomous SOC Platform Logic

(function() {
    'use strict';

    // Mock Live State
    let isStreamActive = true;
    let streamTimer = null;
    let selectedIncidentId = "INC-8802";
    let activeFilter = "all";

    const incidents = [
        {
            id: "INC-8802",
            title: "Multi-Stage Cloud Intrusion & S3 Snapshot Staging",
            severity: "critical",
            timestamp: "Just now",
            actor: "s.marcus@acme-corp.com",
            ip: "185.220.101.5",
            vector: "Cloud IAM / AWS",
            mitre: "TA0010 &bull; Exfiltration",
            confidence: "99.1%",
            status: "AUTO-CONTAINED",
            actionTaken: "Token revoked; Host isolated at Gatekeeper",
            blastRadius: "0 bytes leaked. Perimeter locked.",
            evidence: [
                { num: "01", title: "Impossible Geo-Velocity", desc: "Login Jakarta (08:12 UTC) → Tokyo (08:34 UTC)" },
                { num: "02", title: "Privilege Escalation Request", desc: "Attempted AssumeRole on arn:aws:iam::prod:role/Admin" },
                { num: "03", title: "Gatekeeper Active Intercept", desc: "Session invalidated in 1.4s; Inbound IP dropped" }
            ]
        },
        {
            id: "INC-8801",
            title: "Volumetric Layer-7 HTTP/2 Rapid-Reset Anomaly",
            severity: "critical",
            timestamp: "3m ago",
            actor: "botnet-mesh-alpha",
            ip: "45.33.32.156",
            vector: "Edge Network / Cloudflare",
            mitre: "TA0040 &bull; Impact",
            confidence: "98.7%",
            status: "AUTO-CONTAINED",
            actionTaken: "WAF Rule 901 enacted; Inbound dropped (403)",
            blastRadius: "Edge latency preserved at 18ms.",
            evidence: [
                { num: "01", title: "RST_STREAM Burst", desc: "52,000 req/sec across 14 edge POP nodes" },
                { num: "02", title: "Autonomous Rate Limiting", desc: "IP range quarantined at Edge Gatekeeper" }
            ]
        },
        {
            id: "INC-8798",
            title: "Distributed Kerberoasting & SPN Ticket Extraction",
            severity: "high",
            timestamp: "12m ago",
            actor: "d.kovacs (Compromised Dev)",
            ip: "10.0.14.92",
            vector: "Active Directory / Kerberos",
            mitre: "TA0006 &bull; Credential Access",
            confidence: "94.2%",
            status: "AUTO-CONTAINED",
            actionTaken: "Service account password cycled; Host isolated",
            blastRadius: "Single tier-2 host; Domain Controller intact.",
            evidence: [
                { num: "01", title: "High-Frequency TGS Request", desc: "48 RC4-HMAC ticket requests in 800ms" },
                { num: "02", title: "Automated Ticket Invalidation", desc: "Kerberos ticket cache flushed via SOAR" }
            ]
        },
        {
            id: "INC-8792",
            title: "Anomalous MQTT OT Command: Core Chiller Override",
            severity: "critical",
            timestamp: "45m ago",
            actor: "SCADA-GW-04",
            ip: "192.168.10.45",
            vector: "Industrial OT / MQTT",
            mitre: "TA0108 &bull; Inhibit Response Function",
            confidence: "99.8%",
            status: "AUTO-CONTAINED",
            actionTaken: "PLC controller locked to safe state; Network isolated",
            blastRadius: "Zero thermal disruption; Datacenter safe.",
            evidence: [
                { num: "01", title: "Unauthorized Setpoint Shift", desc: "Payload attempted emergency AC shutdown" },
                { num: "02", title: "Air-Gap Guard Activated", desc: "MQTT broker rejected command via Gatekeeper" }
            ]
        }
    ];

    let quarantines = [
        { ip: "185.220.101.5", reason: "Compromised Token & Geo-velocity" },
        { ip: "45.33.32.156", reason: "L7 Volumetric Rapid-Reset Flood" },
        { ip: "10.0.14.92", reason: "Kerberoasting SPN Sweep" },
        { ip: "192.168.10.45", reason: "Malicious MQTT OT Payload" },
        { ip: "198.51.100.77", reason: "Credential Stuffing on Auth Endpoint" },
        { ip: "203.0.113.89", reason: "PGAudit SQL Exfiltration Probe" },
        { ip: "194.26.29.112", reason: "Tor Exit Node Direct SSH Probe" }
    ];

    // DOM Elements
    const incidentStack = document.getElementById("incidentStack");
    const inspectorContent = document.getElementById("inspectorContent");
    const telemetryTableBody = document.getElementById("telemetryTableBody");
    const streamSearch = document.getElementById("streamSearch");
    const toggleStreamBtn = document.getElementById("toggleStreamBtn");
    const triggerSimModalBtn = document.getElementById("triggerSimModalBtn");
    const simModalOverlay = document.getElementById("simModalOverlay");
    const closeSimModalBtn = document.getElementById("closeSimModalBtn");
    const cancelSimModalBtn = document.getElementById("cancelSimModalBtn");
    const toastStack = document.getElementById("sentinelToastStack");
    const quarantineList = document.getElementById("quarantineList");
    const filterPills = document.querySelectorAll(".filter-pills .pill-btn");

    // Show Toast
    function showToast(message, type = "indigo") {
        if (!toastStack) return;
        const toast = document.createElement("div");
        toast.className = `sentinel-toast toast-${type}`;
        toast.setAttribute("role", "status");

        const textSpan = document.createElement("span");
        textSpan.textContent = message;

        const closeBtn = document.createElement("button");
        closeBtn.className = "btn-close";
        closeBtn.type = "button";
        closeBtn.innerHTML = "&times;";
        closeBtn.style.fontSize = "1.1rem";
        closeBtn.style.padding = "0 0.2rem";

        toast.appendChild(textSpan);
        toast.appendChild(closeBtn);
        toastStack.appendChild(toast);

        const dismiss = () => {
            toast.style.opacity = "0";
            toast.style.transform = "translateY(8px)";
            setTimeout(() => toast.remove(), 200);
        };

        closeBtn.addEventListener("click", dismiss);
        setTimeout(dismiss, 4500);
    }

    // Render Incident Queue
    function renderIncidents() {
        if (!incidentStack) return;

        const filtered = incidents.filter(inc => {
            if (activeFilter === "critical") return inc.severity === "critical";
            if (activeFilter === "mitigated") return inc.status === "AUTO-CONTAINED";
            return true;
        });

        incidentStack.innerHTML = filtered.map(inc => `
            <div class="incident-card ${inc.id === selectedIncidentId ? 'selected' : ''}" data-id="${inc.id}" role="button" tabindex="0">
                <div class="card-top">
                    <span class="card-severity ${inc.severity}">${inc.severity.toUpperCase()}</span>
                    <span class="card-time">${inc.timestamp}</span>
                </div>
                <div class="card-title">${escapeHtml(inc.title)}</div>
                <div class="card-meta-line">
                    <span class="mitre-badge">${inc.mitre}</span>
                    <span>${escapeHtml(inc.actor)}</span>
                </div>
                <div class="card-action-bar">
                    <span class="auto-status">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
                        ${inc.status}
                    </span>
                    <span style="font-size:0.75rem; font-family:var(--font-mono); color:#818cf8;">${inc.confidence}</span>
                </div>
            </div>
        `).join("");
    }

    // Render Selected Incident Inspector
    function renderInspector(inc) {
        if (!inspectorContent || !inc) return;

        const evidenceSteps = (inc.evidence || []).map(step => `
            <div class="evidence-step">
                <span class="step-num">${step.num}</span>
                <div class="step-body">
                    <span class="step-title">${escapeHtml(step.title)}</span>
                    <span class="step-desc">${escapeHtml(step.desc)}</span>
                </div>
            </div>
        `).join("");

        inspectorContent.innerHTML = `
            <div class="inspector-card">
                <div class="inspector-header">
                    <div class="incident-ref">${escapeHtml(inc.id)}</div>
                    <div class="confidence-badge">${inc.confidence} Neural Confidence</div>
                </div>
                <div class="inspector-summary">
                    <strong>Autonomous Triage Verdict:</strong> ${escapeHtml(inc.title)}. Target entity: <code>${escapeHtml(inc.actor)}</code> (${escapeHtml(inc.ip)}).
                </div>

                <div class="evidence-ladder">
                    ${evidenceSteps}
                </div>

                <div style="background: rgba(8,11,18,0.5); border: 1px solid var(--border-subtle); padding: 0.75rem; border-radius: 4px; font-size: 0.78rem;">
                    <div style="color: var(--text-muted); font-size: 0.75rem; font-family: var(--font-mono); margin-bottom: 0.2rem;">AUTONOMOUS PLAYBOOK RESULT:</div>
                    <div style="color: #34d399; font-weight: 600;">✓ ${escapeHtml(inc.actionTaken)}</div>
                    <div style="color: var(--text-secondary); margin-top: 0.2rem;">${escapeHtml(inc.blastRadius)}</div>
                </div>

                <div class="inspector-actions">
                    <button class="btn btn-outline btn-sm" id="btnExportReport" type="button">
                        Export Incident Brief
                    </button>
                    <button class="btn btn-emerald btn-sm" id="btnAcknowledge" type="button">
                        Confirm Triage Closed
                    </button>
                </div>
            </div>
        `;

        document.getElementById("btnExportReport")?.addEventListener("click", () => {
            showToast(`Executive incident brief for ${inc.id} compiled and exported to clipboard.`, "indigo");
        });

        document.getElementById("btnAcknowledge")?.addEventListener("click", () => {
            showToast(`Incident ${inc.id} marked verified and archived to cold storage.`, "emerald");
        });
    }

    // Render Quarantined Hosts List
    function renderQuarantines() {
        if (!quarantineList) return;
        quarantineList.innerHTML = quarantines.map((item, idx) => `
            <div class="quarantine-entry">
                <div class="quarantine-info">
                    <span class="quarantine-target">🔒 ${escapeHtml(item.ip)}</span>
                    <span class="quarantine-reason">${escapeHtml(item.reason)}</span>
                </div>
                <button class="btn-release-small" data-idx="${idx}" type="button">
                    Release
                </button>
            </div>
        `).join("");
    }

    quarantineList?.addEventListener("click", (e) => {
        const btn = e.target.closest(".btn-release-small");
        if (!btn) return;
        const idx = parseInt(btn.dataset.idx, 10);
        const removed = quarantines.splice(idx, 1)[0];
        renderQuarantines();
        const countBadge = document.getElementById("quarantinedHostsCount");
        if (countBadge) countBadge.textContent = quarantines.length;
        showToast(`Quarantine lifted for host ${removed.ip}. Traffic permitted at Gatekeeper.`, "emerald");
    });

    // Handle Incident Card Selection
    incidentStack?.addEventListener("click", (e) => {
        const card = e.target.closest(".incident-card");
        if (!card) return;
        selectedIncidentId = card.dataset.id;
        renderIncidents();
        const found = incidents.find(i => i.id === selectedIncidentId);
        if (found) renderInspector(found);
    });

    // Handle Filter Pills
    filterPills.forEach(pill => {
        pill.addEventListener("click", () => {
            filterPills.forEach(p => {
                p.classList.remove("active");
                p.setAttribute("aria-selected", "false");
            });
            pill.classList.add("active");
            pill.setAttribute("aria-selected", "true");
            activeFilter = pill.dataset.filter;
            renderIncidents();
        });
    });

    // Live Synthetic Telemetry Stream
    const sampleTelemetry = [
        { vector: "cloud", vectorName: "CloudTrail", entity: "iam:role/Admin", payload: "AuthorizeSecurityGroupIngress 0.0.0.0/0", score: "0.94", blocked: true },
        { vector: "network", vectorName: "Edge Gateway", entity: "45.33.32.156", payload: "HTTP/2 Rapid-Reset Flood (>45k rps)", score: "0.99", blocked: true },
        { vector: "identity", vectorName: "Okta Auth", entity: "user: a.reyes", payload: "Fast Token Request (Session Staged)", score: "0.12", blocked: false },
        { vector: "endpoint", vectorName: "eBPF Agent", entity: "host: k8s-worker-09", payload: "execve(/usr/bin/curl pastebin.com/payload)", score: "0.91", blocked: true },
        { vector: "cloud", vectorName: "S3 Event", entity: "s3:prod-db-dumps", payload: "GetObjectBatch request from unlisted IP", score: "0.88", blocked: true },
        { vector: "identity", vectorName: "Azure AD", entity: "user: ciso-service", payload: "MFA Token Verified via Push", score: "0.04", blocked: false }
    ];

    function addTelemetryRow(item) {
        if (!telemetryTableBody) return;
        const now = new Date();
        const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });

        const tr = document.createElement("tr");
        tr.className = "telemetry-row";
        tr.innerHTML = `
            <td>${timeStr}</td>
            <td><span class="vector-tag vector-${item.vector}">${item.vectorName}</span></td>
            <td><code>${escapeHtml(item.entity)}</code></td>
            <td>${escapeHtml(item.payload)}</td>
            <td><strong>${item.score}</strong></td>
            <td>${item.blocked ? '<span class="badge-blocked">DROPPED (403)</span>' : '<span class="badge-passed">PERMITTED</span>'}</td>
        `;

        telemetryTableBody.insertBefore(tr, telemetryTableBody.firstChild);

        // Limit to 20 rows
        while (telemetryTableBody.children.length > 20) {
            telemetryTableBody.removeChild(telemetryTableBody.lastChild);
        }
    }

    // Populate initial rows
    sampleTelemetry.forEach(t => addTelemetryRow(t));

    // Telemetry ticker
    function startTelemetryTicker() {
        if (streamTimer) clearInterval(streamTimer);
        streamTimer = setInterval(() => {
            if (!isStreamActive) return;
            const randItem = sampleTelemetry[Math.floor(Math.random() * sampleTelemetry.length)];
            addTelemetryRow(randItem);
        }, 2500);
    }
    startTelemetryTicker();

    // Toggle Stream Button
    toggleStreamBtn?.addEventListener("click", () => {
        isStreamActive = !isStreamActive;
        toggleStreamBtn.setAttribute("aria-pressed", isStreamActive ? "true" : "false");
        toggleStreamBtn.querySelector("span").textContent = isStreamActive ? "Pause Stream" : "Resume Stream";
        showToast(isStreamActive ? "Live telemetry ingestion resumed." : "Live telemetry ingestion paused.", "indigo");
    });

    // Stream Search Filter
    streamSearch?.addEventListener("input", (e) => {
        const query = e.target.value.toLowerCase().trim();
        const rows = telemetryTableBody?.querySelectorAll("tr");
        rows?.forEach(r => {
            const text = r.textContent.toLowerCase();
            r.style.display = text.includes(query) ? "" : "none";
        });
    });

    // Simulation Trigger Modal
    triggerSimModalBtn?.addEventListener("click", () => {
        if (simModalOverlay) simModalOverlay.hidden = false;
    });

    const closeSimModal = () => {
        if (simModalOverlay) simModalOverlay.hidden = true;
    };

    closeSimModalBtn?.addEventListener("click", closeSimModal);
    cancelSimModalBtn?.addEventListener("click", closeSimModal);
    simModalOverlay?.addEventListener("click", (e) => {
        if (e.target === simModalOverlay) closeSimModal();
    });

    document.querySelectorAll(".scenario-pick-card").forEach(card => {
        card.addEventListener("click", () => {
            const sc = card.dataset.scenario;
            closeSimModal();

            if (sc === "ddos") {
                addTelemetryRow({ vector: "network", vectorName: "Edge Gateway", entity: "45.33.32.156", payload: "INJECTED: Rapid-Reset HTTP/2 Anomaly", score: "0.99", blocked: true });
                showToast("Adversarial Scenario [Layer-7 Flood] injected: Gatekeeper drop rule enacted in 1.1s", "rose");
            } else if (sc === "travel") {
                addTelemetryRow({ vector: "identity", vectorName: "Okta Auth", entity: "user: j.doe@corp.net", payload: "INJECTED: Geo-velocity anomaly (Jakarta → London)", score: "0.97", blocked: true });
                showToast("Adversarial Scenario [Impossible Travel] injected: User session suspended instantly.", "rose");
            } else if (sc === "exfil") {
                addTelemetryRow({ vector: "cloud", vectorName: "S3 Event", entity: "s3://finance-vault", payload: "INJECTED: Rapid 50+ batch object download", score: "0.98", blocked: true });
                showToast("Adversarial Scenario [S3 Exfiltration] injected: IAM policy restricted, 0 bytes leaked.", "rose");
            } else if (sc === "lateral") {
                addTelemetryRow({ vector: "endpoint", vectorName: "ActiveDirectory", entity: "host: DB-CLUSTER-01", payload: "INJECTED: Distributed Kerberoasting Sweep", score: "0.95", blocked: true });
                showToast("Adversarial Scenario [Kerberoasting] injected: Ticket cache revoked automatically.", "rose");
            }
        });
    });

    // Utility escapeHtml
    function escapeHtml(str) {
        if (!str) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Initial Renders
    renderIncidents();
    const initInc = incidents.find(i => i.id === selectedIncidentId);
    if (initInc) renderInspector(initInc);
    renderQuarantines();

})();
