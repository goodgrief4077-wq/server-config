#!/usr/bin/env python3
"""
Jeeves & OpenClaw Prometheus Exporter
Polls Agent Zero (Jeeves) and OpenClaw gateway, exposes metrics on port 9401.
"""

import json
import subprocess
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timezone
import requests

PORT = 9401
SCRAPE_INTERVAL = 30  # seconds

# ─── Metric state ────────────────────────────────────────────────────────────
metrics = {}
metrics_lock = threading.Lock()

def set_metric(name, value, labels=""):
    key = f"{name}{{{labels}}}" if labels else name
    with metrics_lock:
        metrics[key] = (name, labels, value)

# ─── Agent Zero / Jeeves collector ───────────────────────────────────────────
def collect_agent_zero():
    try:
        r = requests.get("http://127.0.0.1:8080/health", timeout=5)
        data = r.json()
        set_metric("jeeves_up", 1)
        version = data.get("gitinfo", {}).get("version", "unknown")
        error = data.get("error")
        set_metric("jeeves_healthy", 0 if error else 1)
        set_metric("jeeves_info", 1, f'version="{version}"')
    except Exception as e:
        set_metric("jeeves_up", 0)
        set_metric("jeeves_healthy", 0)

# ─── OpenClaw gateway collector ──────────────────────────────────────────────
def collect_openclaw():
    try:
        result = subprocess.run(
            ["/home/josh/.npm-global/bin/openclaw", "gateway", "call", "health"],
            capture_output=True, text=True, timeout=10,
            env={"HOME": "/home/josh", "PATH": "/home/josh/.npm-global/bin:/usr/local/bin:/usr/bin:/bin"}
        )
        # output contains the JSON after "Gateway call: health\n"
        output = result.stdout
        json_start = output.find("{")
        if json_start == -1:
            raise ValueError("No JSON in output")
        data = json.loads(output[json_start:])

        ok = 1 if data.get("ok") else 0
        set_metric("openclaw_gateway_up", ok)

        # Sessions
        sessions = data.get("sessions", {})
        session_count = sessions.get("count", 0)
        set_metric("openclaw_sessions_total", session_count)

        # Agents
        agents = data.get("agents", [])
        set_metric("openclaw_agents_total", len(agents))

        # Channels
        channels = data.get("channels", {})
        set_metric("openclaw_channels_total", len(channels))

        # Heartbeat interval
        heartbeat_s = data.get("heartbeatSeconds", 0)
        set_metric("openclaw_heartbeat_interval_seconds", heartbeat_s)

        # Per-agent session counts
        for agent in agents:
            agent_id = agent.get("agentId", "unknown")
            agent_sessions = agent.get("sessions", {}).get("count", 0)
            set_metric("openclaw_agent_sessions", agent_sessions, f'agent_id="{agent_id}"')

            # Latest session age (ms since last update)
            recent = agent.get("sessions", {}).get("recent", [])
            if recent:
                latest_age_ms = recent[0].get("age", 0)
                set_metric("openclaw_agent_last_session_age_seconds",
                           latest_age_ms / 1000, f'agent_id="{agent_id}"')

        # Timestamp
        ts_ms = data.get("ts", 0)
        set_metric("openclaw_gateway_last_seen_timestamp", ts_ms / 1000)

    except subprocess.TimeoutExpired:
        set_metric("openclaw_gateway_up", 0)
        set_metric("openclaw_sessions_total", 0)
    except Exception as e:
        set_metric("openclaw_gateway_up", 0)
        set_metric("openclaw_sessions_total", 0)

# ─── Ollama collector ─────────────────────────────────────────────────────────
def collect_ollama():
    try:
        r = requests.get("http://127.0.0.1:11434/api/tags", timeout=5)
        data = r.json()
        models = data.get("models", [])
        set_metric("ollama_up", 1)
        set_metric("ollama_models_loaded_total", len(models))
        # Count cloud vs local
        cloud = sum(1 for m in models if "cloud" in m.get("name", ""))
        local = len(models) - cloud
        set_metric("ollama_models_cloud_total", cloud)
        set_metric("ollama_models_local_total", local)
    except Exception:
        set_metric("ollama_up", 0)
        set_metric("ollama_models_loaded_total", 0)

# ─── Background scrape loop ───────────────────────────────────────────────────
def scrape_loop():
    while True:
        collect_agent_zero()
        collect_openclaw()
        collect_ollama()
        time.sleep(SCRAPE_INTERVAL)

# ─── Metric definitions (for HELP/TYPE lines) ─────────────────────────────────
METRIC_META = {
    "jeeves_up":                          ("gauge", "1 if Agent Zero (Jeeves) is reachable"),
    "jeeves_healthy":                     ("gauge", "1 if Jeeves reports no errors"),
    "jeeves_info":                        ("gauge", "Jeeves version info"),
    "openclaw_gateway_up":                ("gauge", "1 if OpenClaw gateway is responding"),
    "openclaw_sessions_total":            ("gauge", "Total OpenClaw sessions"),
    "openclaw_agents_total":              ("gauge", "Number of configured OpenClaw agents"),
    "openclaw_channels_total":            ("gauge", "Number of active OpenClaw channels"),
    "openclaw_heartbeat_interval_seconds":("gauge", "OpenClaw heartbeat interval in seconds"),
    "openclaw_agent_sessions":            ("gauge", "Session count per agent"),
    "openclaw_agent_last_session_age_seconds": ("gauge", "Seconds since last session update per agent"),
    "openclaw_gateway_last_seen_timestamp":("gauge", "Unix timestamp of last gateway health check"),
    "ollama_up":                          ("gauge", "1 if Ollama is reachable"),
    "ollama_models_loaded_total":         ("gauge", "Total models available in Ollama"),
    "ollama_models_cloud_total":          ("gauge", "Cloud models available in Ollama"),
    "ollama_models_local_total":          ("gauge", "Local models available in Ollama"),
}

# ─── HTTP handler ─────────────────────────────────────────────────────────────
class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ("/metrics", "/"):
            self.send_response(404)
            self.end_headers()
            return

        lines = []
        emitted_names = set()

        with metrics_lock:
            snapshot = dict(metrics)

        for key, (name, labels, value) in sorted(snapshot.items()):
            if name not in emitted_names:
                meta = METRIC_META.get(name, ("gauge", ""))
                lines.append(f"# HELP {name} {meta[1]}")
                lines.append(f"# TYPE {name} {meta[0]}")
                emitted_names.add(name)
            if labels:
                lines.append(f"{name}{{{labels}}} {value}")
            else:
                lines.append(f"{name} {value}")

        body = "\n".join(lines) + "\n"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; version=0.0.4")
        self.end_headers()
        self.wfile.write(body.encode())

    def log_message(self, format, *args):
        pass  # suppress access logs

# ─── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Initial scrape before serving
    collect_agent_zero()
    collect_openclaw()
    collect_ollama()

    # Start background scraper
    t = threading.Thread(target=scrape_loop, daemon=True)
    t.start()

    print(f"Jeeves exporter running on :{PORT}/metrics")
    server = HTTPServer(("0.0.0.0", PORT), MetricsHandler)
    server.serve_forever()
