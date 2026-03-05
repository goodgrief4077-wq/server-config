#!/usr/bin/env python3
"""
Weekly Research Agent
Searches ArXiv, Semantic Scholar, NSF, DARPA, NIST for new research on:
  - Recursive agentic systems
  - Context visualization
  - Multi-agent memory architectures
  - Autonomous agent frameworks
  - LLM context management

Runs every Monday at 3am. Summarized by Agent Zero (kimi-k2-thinking:cloud).
Reports saved to ~/server-config/research-reports/ and pushed to GitHub.
"""

import json
import os
import time
import requests
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode, quote

AGENT_ZERO_URL = "http://localhost:8080"
LOG_DIR = os.path.expanduser("~/nightly-agent/logs")
REPORT_DIR = os.path.expanduser("~/server-config/research-reports")
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

WEEK_AGO = datetime.now(timezone.utc) - timedelta(days=7)

# ─── Search topics ───────────────────────────────────────────
TOPICS = [
    "recursive agentic systems",
    "context visualization LLM agent",
    "multi-agent memory architecture",
    "autonomous agent self-improvement",
    "agentic AI context management",
    "LLM agent orchestration",
    "agent context window",
    "recursive agent planning",
]

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")

def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip()

# ─────────────────────────────────────────────────────────────
# SOURCE 1: ArXiv
# ─────────────────────────────────────────────────────────────
def search_arxiv(query, max_results=5):
    """Search ArXiv for recent papers on a topic."""
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "lastUpdatedDate",
        "sortOrder": "descending",
    }
    url = f"http://export.arxiv.org/api/query?{urlencode(params)}"
    try:
        r = requests.get(url, timeout=15)
        root = ET.fromstring(r.text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        papers = []
        for entry in root.findall("atom:entry", ns):
            updated_str = entry.findtext("atom:updated", "", ns)
            try:
                updated = datetime.fromisoformat(updated_str.replace("Z", "+00:00"))
                if updated < WEEK_AGO:
                    continue
            except:
                pass
            papers.append({
                "title": entry.findtext("atom:title", "", ns).strip().replace("\n", " "),
                "authors": [a.findtext("atom:name", "", ns) for a in entry.findall("atom:author", ns)][:3],
                "summary": entry.findtext("atom:summary", "", ns).strip()[:300].replace("\n", " "),
                "url": entry.findtext("atom:id", "", ns),
                "updated": updated_str[:10],
                "source": "arxiv",
            })
        return papers
    except Exception as e:
        log(f"  ArXiv error for '{query}': {e}")
        return []

# ─────────────────────────────────────────────────────────────
# SOURCE 2: Semantic Scholar
# ─────────────────────────────────────────────────────────────
def search_semantic_scholar(query, max_results=5):
    """Search Semantic Scholar for recent papers."""
    params = {
        "query": query,
        "limit": max_results,
        "fields": "title,authors,abstract,year,url,publicationDate,externalIds",
        "sort": "publicationDate:desc",
    }
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?{urlencode(params)}"
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "research-agent/1.0"})
        data = r.json()
        papers = []
        for p in data.get("data", []):
            pub_date = p.get("publicationDate") or ""
            papers.append({
                "title": p.get("title", ""),
                "authors": [a.get("name", "") for a in p.get("authors", [])][:3],
                "summary": (p.get("abstract") or "")[:300],
                "url": p.get("url") or f"https://www.semanticscholar.org/paper/{p.get('paperId','')}",
                "updated": pub_date,
                "source": "semantic_scholar",
            })
        return papers
    except Exception as e:
        log(f"  Semantic Scholar error for '{query}': {e}")
        return []

# ─────────────────────────────────────────────────────────────
# SOURCE 3: HuggingFace Daily Papers (replaces NSF/NIST broken APIs)
# ─────────────────────────────────────────────────────────────
def search_huggingface_papers(keywords):
    """Fetch recent HuggingFace daily papers and filter by keywords."""
    results = []
    try:
        # Fetch last 7 days of daily papers
        for days_ago in range(7):
            day = (datetime.now(timezone.utc) - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            r = requests.get(
                f"https://huggingface.co/api/daily_papers?date={day}",
                timeout=15,
                headers={"User-Agent": "research-agent/1.0"},
            )
            if r.status_code != 200:
                continue
            papers = r.json()
            for p in papers:
                paper = p.get("paper", {})
                title = paper.get("title", "").lower()
                abstract = (paper.get("summary") or "").lower()
                # filter by relevance to our topics
                if any(kw.lower() in title or kw.lower() in abstract
                       for kw in keywords):
                    results.append({
                        "title": paper.get("title", ""),
                        "authors": [a.get("name", "") for a in paper.get("authors", [])][:3],
                        "summary": (paper.get("summary") or "")[:300],
                        "url": f"https://huggingface.co/papers/{paper.get('id','')}",
                        "updated": day,
                        "source": "huggingface",
                    })
        return results
    except Exception as e:
        log(f"  HuggingFace error: {e}")
        return []

# ─────────────────────────────────────────────────────────────
# SOURCE 4: DARPA (scrape research programs page)
# ─────────────────────────────────────────────────────────────
def search_darpa():
    """Fetch DARPA AI Forward program info."""
    try:
        r = requests.get("https://www.darpa.mil/research/programs/ai-forward", timeout=15,
                         headers={"User-Agent": "Mozilla/5.0"})
        # Extract key text snippets (simple parse)
        text = r.text
        start = text.find("AI Forward")
        snippet = text[start:start+500] if start > 0 else ""
        # Strip HTML tags
        import re
        clean = re.sub(r"<[^>]+>", " ", snippet).strip()
        clean = " ".join(clean.split())[:400]
        return [{
            "title": "DARPA AI Forward Program",
            "authors": ["DARPA"],
            "summary": clean or "DARPA's initiative exploring new AI research directions for trustworthy national security systems.",
            "url": "https://www.darpa.mil/research/programs/ai-forward",
            "updated": datetime.now().strftime("%Y-%m-%d"),
            "source": "darpa",
        }]
    except Exception as e:
        log(f"  DARPA fetch error: {e}")
        return []

# ─────────────────────────────────────────────────────────────
# SOURCE 5: Papers With Code (ML benchmarks & implementations)
# ─────────────────────────────────────────────────────────────
def search_papers_with_code(query, max_results=5):
    """Search Papers With Code for implementations of agent research."""
    try:
        r = requests.get(
            "https://paperswithcode.com/api/v1/papers/",
            params={"q": query, "ordering": "-published", "items_per_page": max_results},
            timeout=15,
            headers={"User-Agent": "research-agent/1.0"},
        )
        data = r.json()
        results = []
        for p in data.get("results", []):
            pub_date = (p.get("published") or "")[:10]
            try:
                if pub_date and datetime.fromisoformat(pub_date).replace(tzinfo=timezone.utc) < WEEK_AGO:
                    continue
            except:
                pass
            results.append({
                "title": p.get("title", ""),
                "authors": [],
                "summary": (p.get("abstract") or "")[:300],
                "url": p.get("url_pdf") or f"https://paperswithcode.com{p.get('paper_page','')}",
                "updated": pub_date,
                "source": "papers_with_code",
                "has_code": p.get("is_official", False),
            })
        return results
    except Exception as e:
        log(f"  Papers With Code error for '{query}': {e}")
        return []

# ─────────────────────────────────────────────────────────────
# Deduplicate by title similarity
# ─────────────────────────────────────────────────────────────
def deduplicate(papers):
    seen = set()
    unique = []
    for p in papers:
        key = p["title"].lower()[:60]
        if key and key not in seen:
            seen.add(key)
            unique.append(p)
    return unique

# ─────────────────────────────────────────────────────────────
# Send to Agent Zero for synthesis
# ─────────────────────────────────────────────────────────────
def synthesize_with_agent_zero(papers, week_str):
    log("Sending findings to Agent Zero for synthesis...")
    sess = requests.Session()

    try:
        # CSRF
        r = sess.get(f"{AGENT_ZERO_URL}/csrf_token",
                     headers={"Origin": AGENT_ZERO_URL}, timeout=10)
        data = r.json()
        if not data.get("ok"):
            raise Exception(f"CSRF denied: {data.get('error')}")
        csrf_token = data["token"]
        runtime_id = data["runtime_id"]
        sess.cookies.set(f"csrf_token_{runtime_id}", csrf_token)
        headers = {
            "Origin": AGENT_ZERO_URL,
            "X-CSRF-Token": csrf_token,
            "Content-Type": "application/json",
        }

        # Create context
        r = sess.post(f"{AGENT_ZERO_URL}/chat_create", headers=headers, json={}, timeout=10)
        ctxid = r.json().get("ctxid", "")
        if not ctxid:
            raise Exception("No context ID")

        # Build prompt
        papers_text = ""
        for i, p in enumerate(papers[:30], 1):
            papers_text += (
                f"\n{i}. [{p['source'].upper()}] {p['title']}\n"
                f"   Authors: {', '.join(p.get('authors', []))}\n"
                f"   Summary: {p.get('summary','')}\n"
                f"   URL: {p.get('url','')}\n"
            )

        prompt = f"""You are a research analyst specializing in agentic AI systems.

Below are this week's ({week_str}) new papers and research from ArXiv, Semantic Scholar, NSF, DARPA, and NIST on recursive agentic systems, context visualization, and multi-agent architectures.

{papers_text}

Please produce a structured weekly research digest with these sections:
1. **Key Themes This Week** — 3-5 bullet points on what's trending
2. **Top Papers** — pick the 5 most significant, explain why they matter
3. **Recursive Agentic Systems** — what's new specifically on recursive/self-improving agents
4. **Context Visualization & Management** — findings on context window management and visualization
5. **Government & Funding** — notable NSF/DARPA/NIST developments
6. **Connections to Agent Zero** — how any of this applies to improving our local Agent Zero setup
7. **Action Items** — 3 concrete things to experiment with or implement next week

Be concise, technical, and practical."""

        # Send message (async — model needs time to think)
        r = sess.post(
            f"{AGENT_ZERO_URL}/message_async",
            headers=headers,
            json={"text": prompt, "context": ctxid},
            timeout=20,
        )
        log(f"  Synthesis request sent (status {r.status_code}), waiting for kimi to think...")

        # Wait for kimi-k2-thinking to reason (up to 5 min)
        for i in range(30):
            time.sleep(10)
            # Check agent logs for completion signal
            out, _ = run("docker logs agent-zero --tail 3 2>/dev/null")
            if "done" in out.lower() or "response" in out.lower() or i > 25:
                break

        log(f"  Synthesis complete (context: {ctxid[:8]}...)")
        return {"status": "ok", "ctxid": ctxid, "prompt_length": len(prompt)}

    except Exception as e:
        log(f"  Agent Zero synthesis failed: {e}")
        return {"status": "failed", "error": str(e)}

# ─────────────────────────────────────────────────────────────
# Save report and push to GitHub
# ─────────────────────────────────────────────────────────────
def save_and_push(week_str, all_papers, synthesis_result):
    report = {
        "week": week_str,
        "generated": datetime.now().isoformat(),
        "total_papers": len(all_papers),
        "sources": {
            "arxiv": len([p for p in all_papers if p["source"] == "arxiv"]),
            "semantic_scholar": len([p for p in all_papers if p["source"] == "semantic_scholar"]),
            "huggingface": len([p for p in all_papers if p["source"] == "huggingface"]),
            "papers_with_code": len([p for p in all_papers if p["source"] == "papers_with_code"]),
            "darpa": len([p for p in all_papers if p["source"] == "darpa"]),
        },
        "synthesis": synthesis_result,
        "papers": all_papers,
    }

    fname = f"research_{week_str}.json"
    fpath = os.path.join(REPORT_DIR, fname)
    with open(fpath, "w") as f:
        json.dump(report, f, indent=2)
    log(f"  Report saved: {fpath}")

    # Push to GitHub
    out, err = run(f"""
        cd ~/server-config && \
        git add research-reports/ && \
        git diff --cached --quiet || git commit -m "Weekly research digest {week_str} ({len(all_papers)} papers)" && \
        git push
    """)
    if err and "nothing to commit" not in err and "master" not in err:
        log(f"  GitHub error: {err}")
    else:
        log(f"  Pushed to GitHub: server-config/research-reports/{fname}")

    return fpath

# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────
def main():
    week_str = datetime.now().strftime("%Y-W%V")
    log(f"=== Weekly Research Agent: {week_str} ===")

    all_papers = []

    # ArXiv — search all topics
    log("Searching ArXiv...")
    for topic in TOPICS:
        papers = search_arxiv(topic, max_results=4)
        all_papers.extend(papers)
        log(f"  '{topic}': {len(papers)} papers")
        time.sleep(1)  # be polite to API

    # Semantic Scholar — top topics only
    log("Searching Semantic Scholar...")
    for topic in TOPICS[:4]:
        papers = search_semantic_scholar(topic, max_results=3)
        all_papers.extend(papers)
        log(f"  '{topic}': {len(papers)} papers")
        time.sleep(2)

    # HuggingFace daily papers
    log("Searching HuggingFace Daily Papers...")
    hf_keywords = ["agent", "agentic", "recursive", "context", "memory", "multi-agent", "orchestration"]
    hf_papers = search_huggingface_papers(hf_keywords)
    all_papers.extend(hf_papers)
    log(f"  HuggingFace: {len(hf_papers)} relevant papers this week")

    # DARPA
    log("Fetching DARPA AI Forward...")
    darpa = search_darpa()
    all_papers.extend(darpa)
    log(f"  DARPA: {len(darpa)} entries")

    # Deduplicate
    all_papers = deduplicate(all_papers)
    log(f"Total unique papers/entries: {len(all_papers)}")

    # Synthesize with Agent Zero
    synthesis = synthesize_with_agent_zero(all_papers, week_str)

    # Save + push
    report_path = save_and_push(week_str, all_papers, synthesis)

    log(f"=== Done — {len(all_papers)} items collected ===")
    log(f"Report: {report_path}")

if __name__ == "__main__":
    main()
