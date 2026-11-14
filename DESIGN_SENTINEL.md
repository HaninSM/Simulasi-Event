# SentinelAI Design System & UX Architecture

> **Surface Mode**: Operate (Next-Gen Autonomous SOC Interactive Web App & Command Console)  
> **Visual Identity**: Deep Obsidian & Quantum Indigo/Emerald  
> **Target Audience**: Tier-3 SOC Analysts, CISOs, Threat Hunters, and Autonomous Incident Responders.

---

## 1. Visual Foundation & Color Strategy

The design follows a **Committed Dark-Room Operation** palette tailored for 24/7 mission-critical security environments. It rejects generic bright neons and clashing halos in favor of velvety obsidian elevations and purposeful status lighting.

### Color Tokens

| Token Name | Value | Purpose & Contrast Ratio |
|---|---|---|
| `--bg-void` | `#080b12` | Root background; simulates infinite dark space |
| `--bg-surface` | `#0f1523` | First-level panels and workbench columns |
| `--bg-elevated` | `#151d30` | Hover states and interactive toolbars |
| `--bg-card` | `#182238` | Incident cards, kill-chain stages, inspection boxes |
| `--border-subtle` | `#1e2d48` | Crisp structural separation |
| `--border-strong` | `#2e4368` | Active focus rings and highlighted cards |
| `--text-primary` | `#f8fafc` | Main headings and telemetry values (15.8:1) |
| `--text-secondary` | `#cbd5e1` | Card summaries, labels, and entity names (11.2:1) |
| `--text-muted` | `#94a3b8` | Metadata, timestamps, and secondary captions (7.1:1 - WCAG AA Pass) |
| `--quantum-indigo` | `#6366f1` / `#4338ca` | AI Core, Neural Correlation, Machine Learning Confidence |
| `--quantum-emerald` | `#10b981` / `#047857` | Active Containment, Zero-Loss Verdicts, Gatekeeper Defense |
| `--alert-rose` | `#f43f5e` / `#be123c` | Critical Inbound Exploits, Active Breach Campaigns |
| `--alert-amber` | `#f59e0b` / `#b45309` | High Severity, Suspicious Geo-velocity, TGS Sweeps |

---

## 2. Typography Hierarchy

A dual-typeface system balancing futuristic authority with technical data legibility:
- **Display & Interface**: `Sora` (Geometric, assertive, highly legible at small sizes).
- **Data & Telemetry**: `Fira Code` (Tabular numerals, monospaced entity IDs, IP addresses, MITRE codes).

### Type Scale Steps (1.25× Ratio)
- `h1 / Brand`: `1.25rem` (20px) / `1.5rem` (24px), font-weight: 800.
- `h2 / Panel Title`: `1.15rem` (18.4px), font-weight: 700.
- `h3 / Modal & Card Title`: `0.9rem` (14.4px), font-weight: 700.
- `Body & Controls`: `0.82rem` (13.1px), line-height: 1.5.
- `Micro-Badges & Meta`: `0.75rem` (12px), font-weight: 600–700 (strictly strictly above the 11px accessibility floor).

---

## 3. Core Component Anatomy

### 1. Header Navigation & Health Ribbon
- **Brand Mark**: Authored geometric SVG hex-shield with two-tone linear gradient (`#4338ca` to `#047857`).
- **Engine Status Pill**: Non-pulsing static green indicator dot (`--quantum-emerald`) displaying active model name and inference latency (`42ms p99`).
- **Controls**: Stream toggle (pause/resume with accessible `aria-pressed`), Simulation launcher, and route switcher.

### 2. Autonomous Triage Queue
- High-density stacked cards displaying:
  - Severity badge (`CRITICAL` rose, `HIGH` amber).
  - Timecode and Mitre ATT&CK stage pill (`TA0010 • Exfiltration`).
  - Target entity (`s.marcus@acme-corp.com`, IP, vector).
  - Autonomous resolution state (`✓ AUTO-CONTAINED`).
  - Selection state with crisp indigo accent border (`#818cf8`).

### 3. MITRE ATT&CK Kill-Chain Matrix
- 4-stage horizontal operational matrix:
  1. **Reconnaissance (TA0043)**: Port sweep and scanning telemetry.
  2. **Initial Access (TA0001)**: Credential spraying and Okta anomalies.
  3. **Lateral Movement (TA0008)**: WMI remote exec and Kerberoasting.
  4. **Exfiltration (TA0010)**: S3 database snapshot staging.
- Stage nodes feature subtle tinted badges with entity and MITRE technique IDs.

### 4. AI Reasoning & Decision Inspector
- Provides complete explainability for autonomous AI actions:
  - **Verdict Summary**: Why the model flagged the campaign.
  - **Evidence Ladder**: Sequential 3-step proof chain (Geo-velocity → Privilege escalation → Intercept).
  - **Blast Radius Report**: Quantified impact verification (e.g. `0 bytes leaked`).
  - **Action Controls**: One-click brief export and incident closure verification.

### 5. Multi-Vector Telemetry Table
- Real-time ingestion stream connecting CloudTrail, Edge Gateway, Okta, and eBPF Agent.
- Search input with instant DOM filtering.
- Status badges: `DROPPED (403)` in soft rose vs `PERMITTED` in muted gray.

### 6. Simulation Trigger Modal & Toast Stack
- Modal dialog for launching live adversarial scenarios (`Layer-7 Rapid-Reset Flood`, `Impossible Geo-velocity`, `S3 Exfiltration Sweep`, `Kerberoasting`).
- Non-blocking toast notifications positioned at bottom-right with progress animations and explicit dismiss controls.

### 7. Dual-Mode Incident Stream & UI/UX Pro Max Architecture
- **Segmented View Switcher**: High-precision dark toggle (`#080808` recessed container, `#1c1c1c` active surface, subtle border stroke) switching between:
  - *Chronological Node Stream*: Connecting vertical spine line with timestamped nodes.
  - *Highest Severity Priority Matrix*: Deterministic triage ranking (`RANK #1, #2...`), severity tier banners (`tier-kritis`, `tier-tinggi`, `tier-menengah`), and interactive severity filter chips (*All, KRITIS, TINGGI, MENENGAH*).
- **Anti-Cache & Visual Reliability**: Asset versioning query parameter (`?v=2.4.2`), universal button CSS reset, and FastAPI anti-cache middleware response headers ensuring consistent dark-room command center aesthetic across all client environments.

---

## 4. Craft Floor Compliance Checklist

- [x] **Zero Detector Antipatterns**: 0 errors, 0 warnings on `impeccable detect`.
- [x] **WCAG AA Contrast**: All body text ≥ 4.5:1, headings ≥ 3:1.
- [x] **Accessibility Floor**: Zero functional text below 12px (`0.75rem`).
- [x] **No Slop**: No gradient text, no clashing border-accent on rounded corners, no zero-offset neon glow halos.
- [x] **Stateful UX**: Search filtering, active tab selection, live ticker pausing, and modal escape hatches.
- [x] **Reduced Motion**: Complete `@media (prefers-reduced-motion: reduce)` block disabling non-essential transitions.
