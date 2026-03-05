# HEARTBEAT.md — System Status (updated 2026-03-06)

On heartbeat: check if anything needs attention. If not, reply HEARTBEAT_OK.
Do NOT run diagnostics, do NOT interrogate your own setup. Just check the list below.

## Current Infrastructure — VERIFIED WORKING

| Service | URL / Port | Status |
|---------|-----------|--------|
| Agent Zero (Jeeves) | http://localhost:8080 | Running |
| OpenClaw Gateway | ws://127.0.0.1:18789 | Running (systemd) |
| Ollama | http://localhost:11434 | Running (6 models) |
| Titan-M API | http://localhost:8000 | Running |
| Titan-M PostgreSQL | localhost:5432 | Healthy |
| Titan-M WebSocket | http://localhost:8001 | Running |
| Grafana (monitoring) | http://localhost:3000 | Running |
| Prometheus | http://localhost:9090 | Running |
| cAdvisor | http://localhost:8081 | Running |

## Ollama Models (Ollama Pro — resets Fridays 6pm KST)

- deepseek-v3.1:671b-cloud (chat — primary)
- qwen3-coder:480b-cloud (utility/coding)
- kimi-k2.5:cloud (browser/vision)
- kimi-k2-thinking:cloud (deep research)
- qwen3.5:cloud (fast tasks)
- qwen3.5:latest (local fallback)

**IMPORTANT: Use Ollama models only. Anthropic API is NOT authorized.**

## Key Paths

- Jeeves vault: ~/jeeves-vault/
- Titan-M code: ~/titan-m-memory-system/
- Server config: ~/server-config/
- Nightly agent: ~/nightly-agent/
- OpenClaw workspace: ~/.openclaw/workspace/

## Cron Jobs

- 2am nightly: ~/nightly-agent/nightly_check.py (health check → GitHub)
- 3am Monday: ~/nightly-agent/weekly_research_agent.py (ArXiv research → GitHub)

## Known Issues

- titan-api Docker healthcheck shows "unhealthy" — this is because the healthcheck
  hits /api/v1/system/status which requires auth. The API itself IS healthy at
  /api/v1/system/health. Ignore the Docker health status.
- titan-websocket shows unhealthy — separate issue, non-critical.

## CLAUDE-HANDOFF.md

Check ~/jeeves-vault/CLAUDE-HANDOFF.md for any pending tasks from Claude Code.
