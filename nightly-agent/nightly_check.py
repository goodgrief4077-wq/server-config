#!/usr/bin/env python3
"""
Nightly Agent — runs at 2am
Checks: Agent Zero health, memory, GitHub repos, sends test message
"""

import json
import os
import subprocess
import time
import requests
from datetime import datetime

AGENT_ZERO_URL = "http://localhost:8080"
LOG_DIR = os.path.expanduser("~/nightly-agent/logs")
os.makedirs(LOG_DIR, exist_ok=True)

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")

def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip()

# ─────────────────────────────────────────────
# 1. Agent Zero health check
# ─────────────────────────────────────────────
def check_agent_zero_health():
    log("Checking Agent Zero health...")
    try:
        r = requests.get(f"{AGENT_ZERO_URL}/health", timeout=10)
        data = r.json()
        version = data.get("gitinfo", {}).get("version", "unknown")
        error = data.get("error")
        log(f"  Agent Zero: {version} — {'OK' if not error else 'ERROR: ' + error}")
        return {"status": "ok" if not error else "error", "version": version, "error": error}
    except Exception as e:
        log(f"  Agent Zero unreachable: {e}")
        return {"status": "unreachable", "error": str(e)}

# ─────────────────────────────────────────────
# 2. Memory check
# ─────────────────────────────────────────────
def check_memory():
    log("Checking Agent Zero memory...")
    memory_path = os.path.expanduser("~/.local/share/docker/volumes")
    results = {}

    # Check memory files inside container
    files_to_check = [
        "/a0/usr/memory/default/index.faiss",
        "/a0/usr/memory/default/knowledge_import.json",
        "/a0/usr/memory/default/embedding.json",
    ]
    for f in files_to_check:
        out, _ = run(f"docker exec agent-zero stat -c '%s %n' {f} 2>/dev/null")
        if out:
            size, name = out.split(" ", 1)
            fname = os.path.basename(name)
            results[fname] = f"{int(size):,} bytes"
            log(f"  {fname}: {int(size):,} bytes")
        else:
            log(f"  {os.path.basename(f)}: missing")
            results[os.path.basename(f)] = "missing"

    # Check knowledge import entries
    out, _ = run("docker exec agent-zero cat /a0/usr/memory/default/knowledge_import.json 2>/dev/null")
    if out:
        try:
            data = json.loads(out)
            count = len(data) if isinstance(data, list) else len(data.keys())
            log(f"  knowledge entries: {count}")
            results["knowledge_entries"] = count
        except:
            results["knowledge_entries"] = "parse error"

    return results

# ─────────────────────────────────────────────
# 3. GitHub check
# ─────────────────────────────────────────────
def check_github():
    log("Checking GitHub repos...")
    results = {}

    out, err = run("gh repo list --limit 10 --json name,updatedAt,isPrivate 2>/dev/null")
    if out:
        repos = json.loads(out)
        for repo in repos:
            name = repo["name"]
            updated = repo["updatedAt"][:10]
            private = "private" if repo["isPrivate"] else "public"
            log(f"  {name} ({private}) — last updated: {updated}")
            results[name] = {"updated": updated, "visibility": private}
    else:
        log(f"  GitHub CLI error: {err}")
        results["error"] = err

    # Check titan-m-memory-system repo details
    out, err = run("gh repo view goodgrief4077-wq/titan-m-memory-system --json name,updatedAt,description 2>/dev/null")
    if out:
        titan = json.loads(out)
        log(f"  titan-m-memory-system: last updated {titan.get('updatedAt','?')[:10]}")
        results["titan-m-memory-system"] = titan
    else:
        log(f"  titan-m-memory-system: {err}")

    # Check for uncommitted changes in server-config
    out, _ = run("cd ~/server-config && git status --short 2>/dev/null")
    if out:
        log(f"  server-config has uncommitted changes:\n{out}")
        results["server-config-dirty"] = out
    else:
        log("  server-config: clean")

    return results

# ─────────────────────────────────────────────
# 4. Send test message to Agent Zero
# ─────────────────────────────────────────────
def test_agent_zero():
    log("Sending test message to Agent Zero...")
    sess = requests.Session()

    try:
        # Step 1: get CSRF token + runtime_id
        r = sess.get(
            f"{AGENT_ZERO_URL}/csrf_token",
            headers={"Origin": AGENT_ZERO_URL},
            timeout=10
        )
        data = r.json()
        if not data.get("ok"):
            raise Exception(f"CSRF denied: {data.get('error')}")
        csrf_token = data["token"]
        runtime_id = data["runtime_id"]

        # Step 2: set CSRF cookie so subsequent requests are authenticated
        sess.cookies.set(f"csrf_token_{runtime_id}", csrf_token)
        headers = {
            "Origin": AGENT_ZERO_URL,
            "X-CSRF-Token": csrf_token,
            "Content-Type": "application/json",
        }

        # Step 3: create chat context
        r = sess.post(f"{AGENT_ZERO_URL}/chat_create", headers=headers, json={}, timeout=10)
        ctxid = r.json().get("ctxid", "")
        if not ctxid:
            raise Exception(f"No context ID returned: {r.text[:100]}")
        log(f"  Context created: {ctxid[:8]}...")

        # Step 4: send test message
        test_msg = "Nightly health check. Reply with: OK and the current time."
        r = sess.post(
            f"{AGENT_ZERO_URL}/message_async",
            headers=headers,
            json={"text": test_msg, "context": ctxid},
            timeout=15
        )
        log(f"  Message sent — status: {r.status_code}")

        # Step 5: wait then check container logs for response
        time.sleep(20)
        out, _ = run(f"docker logs agent-zero --tail 5 2>/dev/null")
        log(f"  Agent log tail: {out[:100]}")

        return {"status": "sent", "ctxid": ctxid, "http_status": r.status_code}

    except Exception as e:
        log(f"  Test failed: {e}")
        return {"status": "failed", "error": str(e)}

# ─────────────────────────────────────────────
# 5. Docker & system status
# ─────────────────────────────────────────────
def check_system():
    log("Checking system...")
    results = {}

    # Docker container status
    out, _ = run("docker ps --filter name=agent-zero --format '{{.Status}}'")
    results["agent_zero_container"] = out or "not running"
    log(f"  Container: {out or 'not running'}")

    # Battery
    out, _ = run("cat /sys/class/power_supply/BAT0/capacity 2>/dev/null")
    thresh_start, _ = run("cat /sys/class/power_supply/BAT0/charge_control_start_threshold 2>/dev/null")
    thresh_stop, _ = run("cat /sys/class/power_supply/BAT0/charge_control_end_threshold 2>/dev/null")
    if out:
        results["battery"] = f"{out}% (thresholds: {thresh_start}-{thresh_stop}%)"
        log(f"  Battery: {out}% (thresholds: {thresh_start}-{thresh_stop}%)")

    # Disk usage
    out, _ = run("df -h / | tail -1 | awk '{print $3\"/\"$2\" used (\"$5\")\"}'")
    results["disk"] = out
    log(f"  Disk: {out}")

    # Memory
    out, _ = run("free -h | grep Mem | awk '{print $3\"/\"$2\" used\"}'")
    results["ram"] = out
    log(f"  RAM: {out}")

    # Ollama models
    out, _ = run("ollama list 2>/dev/null | tail -n +2 | awk '{print $1}'")
    results["ollama_models"] = out.splitlines()
    log(f"  Ollama models: {', '.join(out.splitlines())}")

    return results

# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
def main():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    log(f"=== Nightly Agent starting: {timestamp} ===")

    report = {
        "timestamp": timestamp,
        "agent_zero": check_agent_zero_health(),
        "memory": check_memory(),
        "github": check_github(),
        "agent_test": test_agent_zero(),
        "system": check_system(),
    }

    # Save report
    report_path = os.path.join(LOG_DIR, f"report_{timestamp}.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    log(f"Report saved: {report_path}")

    # Push report to GitHub
    out, err = run(f"""
        cd ~/server-config && \
        mkdir -p nightly-reports && \
        cp {report_path} nightly-reports/ && \
        git add nightly-reports/ && \
        git diff --cached --quiet || git commit -m "Nightly report {timestamp}" && \
        git push
    """)
    if err and "nothing to commit" not in err:
        log(f"  GitHub push: {err}")
    else:
        log(f"  Report pushed to GitHub")

    log("=== Done ===")

if __name__ == "__main__":
    main()
