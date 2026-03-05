# CLAUDE.md — Josh's Linux Server PC

This file gives Claude Code context about this machine and ongoing projects.

## Machine

- **OS**: Ubuntu 24.04.4 LTS
- **Hardware**: Lenovo ThinkPad 20EN0013US
- **RAM**: 46 GB
- **Disk**: 915 GB (38 GB used)
- **Role**: Always-on server (lid closed, plugged in)
- **Timezone**: Asia/Seoul (UTC+9)

## Sudo Access

Claude has passwordless sudo via `/etc/sudoers.d/claude-temp`. Use it freely for system tasks.

## Key Services

### Agent Zero (AI Agent Framework)
- **URL**: http://localhost:8080
- **Container**: `docker ps --filter name=agent-zero`
- **Config**: `/home/josh/server-config/` (pushed to GitHub)
- **Models**:
  - Chat: `deepseek-v3.1:671b-cloud` (main reasoning)
  - Utility: `qwen3-coder:480b-cloud` (memory/summarization)
  - Browser: `kimi-k2.5:cloud` (vision/web tasks)
- **Restart**: `docker restart agent-zero`
- **Settings file**: inside container at `/a0/usr/settings.json`
- **API base**: `http://172.17.0.1:11434` (Docker → host Ollama)

### Ollama
- **Version**: 0.17.6
- **Plan**: Pro ($20/month) — cloud models enabled
- **Listening**: `0.0.0.0:11434` (all interfaces)
- **Service**: `systemctl status ollama`
- **Installed cloud models**:
  - `deepseek-v3.1:671b-cloud`
  - `qwen3-coder:480b-cloud`
  - `kimi-k2.5:cloud`
  - `kimi-k2-thinking:cloud`
  - `qwen3.5:cloud`
  - `qwen3.5:latest` (local, 6.6 GB)

### Battery (TLP)
- **Stop charging at**: 80%
- **Resume charging at**: 40%
- **Config**: `/etc/tlp.conf`
- **Verify**: `cat /sys/class/power_supply/BAT0/charge_control_start_threshold`

### Screen
- **Lock**: disabled
- **Blanks after**: 10 minutes (no password to wake)
- **Sleep**: disabled

## GitHub

- **Account**: goodgrief4077-wq
- **Email**: goodgrief4077@gmail.com
- **CLI**: `gh` is installed and authenticated
- **Repos**:
  - `server-config` (public) — system configs + nightly/weekly reports
  - `jeeves-vault` (private)
  - `titan-m-memory-system` (private)
  - `jeeves-test` (public)

## Automated Agents (Cron)

| Time | Script | Purpose |
|------|--------|---------|
| 2am nightly | `~/nightly-agent/nightly_check.py` | Health check Agent Zero, memory, GitHub, battery |
| 3am Monday | `~/nightly-agent/weekly_research_agent.py` | Research agentic AI papers from ArXiv, HuggingFace, DARPA |

- Logs: `~/nightly-agent/logs/`
- Reports pushed to: `github.com/goodgrief4077-wq/server-config`

## Preferences

- No emojis unless asked
- Short, direct responses
- Always run commands directly — sudo is available
- Research before making assumptions on model names, APIs, versions
- When installing packages, use `sudo apt install -y`
- Docker containers should always have `--restart=unless-stopped`

## Important Paths

| Path | Purpose |
|------|---------|
| `~/server-config/` | Git repo with all system configs |
| `~/nightly-agent/` | Automated agent scripts |
| `~/nightly-agent/logs/` | Cron logs and JSON reports |
| `/etc/tlp.conf` | Battery charge thresholds |
| `/etc/systemd/logind.conf` | Lid close behavior |
| `/a0/usr/settings.json` | Agent Zero settings (inside Docker) |
| `/a0/usr/.env` | Agent Zero API keys (inside Docker) |
