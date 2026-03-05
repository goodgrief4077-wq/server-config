#!/bin/bash
# Obsidian Vault Auto-Backup to GitHub
# Runs on cron — pushes any changes in the vault

VAULT="/home/josh/Documents/Obsidian Vault"
LOG="/home/josh/nightly-agent/logs/obsidian-backup.log"
DATE=$(date '+%Y-%m-%d %H:%M KST')

cd "$VAULT" || exit 1

# Check if there are any changes
if git status --short | grep -q .; then
    git add -A
    git commit -m "Vault backup $DATE" >> "$LOG" 2>&1
    git push >> "$LOG" 2>&1
    echo "[$DATE] Pushed vault changes" >> "$LOG"
else
    echo "[$DATE] No changes" >> "$LOG"
fi
