# CLAUDE.md — Josh's Linux Server PC

This file gives Claude Code full context about this machine, projects, and identity.

---

## The Human — Sir Joshua

- **Name:** Joshua (goodgrief4077-wq / kimster357) — address as **Sir**
- **Location:** Seoul, Korea (UTC+9)
- **Role:** Solo missionary + entrepreneur
- **Mission:** Kingdom Works Ministry (registered nonprofit, 2026-02-18)
- **Skill level:** Total beginner — always give step-by-step instructions
- **Financial target:** $1,500/month survival → $10,000/month by end of 2026

---

## Machine

- **OS:** Ubuntu 24.04.4 LTS
- **Hardware:** Lenovo ThinkPad 20EN0013US
- **RAM:** 46 GB | **Disk:** 915 GB
- **Role:** Always-on server (lid closed, plugged in)
- **Timezone:** Asia/Seoul (UTC+9)
- **Sudo:** Passwordless via `/etc/sudoers.d/claude-temp` — use freely

---

## The Agent System — Jeeves

**Jeeves** is Sir's primary AI executive assistant (butler character — formal, warm, loyal).
Claude Code acts as a partner to Jeeves, handing off tasks via `CLAUDE-HANDOFF.md` in jeeves-vault.

### Agent Network (from AGENTS.md + MODEL-ASSIGNMENT-STRATEGY.md)

| Agent | Model | Purpose |
|-------|-------|---------|
| **Jeeves** | Primary orchestrator | Executive CEO assistant |
| **Research Specialist** | `glm-5:cloud` | Web research & analysis |
| **Technical Specialist** | deepseek cloud | Code research & technical |
| **Deep Analysis** | `deepseek-v3.2:cloud` | Large context research |
| **Betsy** | TBD | Agent role |
| **Rocco** | TBD | Agent role |
| **Grief Channel Shepherd** | TBD | YouTube grief channel |
| **Rocky Channel Content** | TBD | YouTube rocky channel |

### OpenClaw / ZeroClaw Gateway
- **Gateway:** `0.0.0.0:3000`
- **Provider:** Ollama at `http://host.docker.internal:11434`
- **Config:** `~/jeeves-vault/zeroclaw-config.toml`
- **Workspace:** `~/.openclaw/workspace/`

---

## Key Projects (Priority Order)

1. **ADAS** — Automated Design of Agentic Systems (research + implementation)
2. **B2B SaaS** — Tools for Christian business owners (Ministry CRM)
3. **Content** — 3 YouTube channels (grief, rocky-on-the-rock, ministry)
4. **Titan-M Memory System** — Persistent AI memory (PostgreSQL, 10 phases)

---

## Titan-M Memory System

Multi-phase persistent memory system for Jeeves.

- **Database:** PostgreSQL container (`titan-postgres`), DB: `titan_memory`, user: `titan`
- **API:** `http://localhost:8080` (when running)
- **Phases:** Phase 3 complete, Phases 6-10 designed (security, ML, marketplace)
- **Code:** `~/obsidian-vault/Titan-M-Memory-System/` and `jeeves-vault/titan-m-phases/`
- **Populate script:** `~/.openclaw/workspace/scripts/populate-titan-memory.py`
- **Urgent task:** DB tables not yet initialized — needs `populate-titan-memory.py` run

### Memory Architecture (from JEEVES_MEMORY.md)
1. Conversation Memory — complete interaction history
2. Learning Patterns — what works/doesn't
3. Decision Log — all approvals and outcomes
4. Skill Development — growing capabilities
5. Mission Evolution — deepening understanding

---

## Agent Zero (AI Agent Framework)

- **URL:** http://localhost:8080
- **Container:** `docker ps --filter name=agent-zero`
- **Restart:** `docker restart agent-zero`
- **Auto-restart:** `unless-stopped` configured
- **Settings:** inside container at `/a0/usr/settings.json`
- **API base:** `http://172.17.0.1:11434` (Docker → host Ollama)

### Current Model Config
| Role | Model | Reason |
|------|-------|--------|
| Chat | `deepseek-v3.1:671b-cloud` | #1 general reasoning, 671B |
| Utility | `qwen3-coder:480b-cloud` | Coding + structured tasks |
| Browser | `kimi-k2.5:cloud` | Native multimodal + vision |

---

## Ollama

- **Version:** 0.17.6 | **Plan:** Pro ($20/month)
- **Listening:** `0.0.0.0:11434` (all interfaces — Docker can reach it)
- **Service:** `systemctl status ollama`
- **API key:** stored in `/a0/usr/.env` as `API_KEY_OLLAMA`

### Installed Models
| Model | Type | Size |
|-------|------|------|
| `deepseek-v3.1:671b-cloud` | Cloud | — |
| `qwen3-coder:480b-cloud` | Cloud | — |
| `kimi-k2.5:cloud` | Cloud | — |
| `kimi-k2-thinking:cloud` | Cloud | — |
| `qwen3.5:cloud` | Cloud | — |
| `qwen3.5:latest` | Local | 6.6 GB |

---

## GitHub

- **Account:** goodgrief4077-wq | **Email:** goodgrief4077@gmail.com
- **CLI:** `gh` installed and authenticated

### Repos
| Repo | Visibility | Purpose |
|------|-----------|---------|
| `server-config` | Public | System configs, nightly/weekly reports, CLAUDE.md |
| `jeeves-vault` | Private | Jeeves agent system, Titan-M, all memory |
| `titan-m-memory-system` | Private | Titan-M standalone |
| `jeeves-test` | Public | Testing |

### jeeves-vault Key Files
| File | Purpose |
|------|---------|
| `SOUL.md` | Jeeves identity + operating principles |
| `USER.md` | Sir Joshua profile + working preferences |
| `IDENTITY.md` | Jeeves character definition |
| `MEMORY.md` | Long-term memory (613 lines, 38 sections) |
| `AGENTS.md` | Agent workspace guide |
| `CLAUDE-HANDOFF.md` | Bidirectional task queue between Claude ↔ Jeeves |
| `MODEL-ASSIGNMENT-STRATEGY.md` | Which models do what |
| `STRATEGY-10YEAR.md` | 10-year sovereign AI roadmap |
| `MISSION_DASHBOARD.md` | Executive project status |
| `AI_SYSTEMS_ROADMAP.md` | AI systems plan |
| `BOOT.md` | Gateway startup tasks |
| `agents/` | Individual agent configs (betsy, rocco, etc.) |
| `skills/` | OpenClaw skills library |
| `titan-m-phases/` | Titan-M phase implementations |
| `memory/` | Daily memory logs (YYYY-MM-DD.md) |
| `metacog/` | Metacognitive monitoring system |

---

## Automated Agents (Cron)

| Time | Script | Purpose |
|------|--------|---------|
| 2am nightly | `~/nightly-agent/nightly_check.py` | Health: Agent Zero, memory, GitHub, battery, system |
| 3am Monday | `~/nightly-agent/weekly_research_agent.py` | Research: ArXiv, HuggingFace, DARPA → Kimi synthesis |

- **Logs:** `~/nightly-agent/logs/`
- **Reports:** pushed to `github.com/goodgrief4077-wq/server-config`

---

## System Config

### Battery (TLP)
- Stop charging: **80%** | Resume: **40%**
- Config: `/etc/tlp.conf`
- Verify: `cat /sys/class/power_supply/BAT0/charge_control_end_threshold`

### Screen
- Lock: **disabled** | Blanks after: **10 min** | Sleep: **disabled**

### Lid
- Closing lid does NOT suspend — configured in `/etc/systemd/logind.conf`

---

## Important Paths

| Path | Purpose |
|------|---------|
| `~/server-config/` | Git repo — system configs + reports |
| `~/nightly-agent/` | Automated agent scripts |
| `~/nightly-agent/logs/` | Cron logs + JSON reports |
| `~/.openclaw/workspace/` | OpenClaw/Jeeves workspace |
| `/etc/tlp.conf` | Battery thresholds |
| `/etc/systemd/logind.conf` | Lid close behavior |
| `/a0/usr/settings.json` | Agent Zero settings (in Docker) |
| `/a0/usr/.env` | Agent Zero API keys (in Docker) |

---

## Working Preferences (from USER.md + SOUL.md)

- Address Sir as **Sir** (if acting as Jeeves) or just do the work directly
- **Step-by-step** — never assume prior knowledge
- **Verify in two ways** — never declare done without testing
- **HITL** — explain and confirm sensitive/irreversible actions before running
- **No autonomous git commits** — always ask first
- **Fix small issues proactively** — flag larger ones without fixing
- No emojis unless asked
- Short, direct responses
- Research before assuming model names, APIs, versions

---

## Theological Foundation

All work serves the **Great Commission** and **Kingdom of God**.
- Kingdom Works Ministry (nonprofit) is the umbrella
- Income funds missions and gospel content
- Every technical decision should serve the mission
