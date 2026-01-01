#!/usr/bin/env bash
set -euo pipefail

SESSION_NAME="${1:-ai-coding}"

if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "Attaching to existing session: $SESSION_NAME"
    exec tmux attach-session -t "$SESSION_NAME"
else
    echo "Creating new session: $SESSION_NAME"
    exec tmux new-session -s "$SESSION_NAME"
fi
