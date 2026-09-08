#!/usr/bin/env bash
# Pose le cadrage AGENTS (routeur + skills + mermaid) SANS écraser.
# Usage : apply-framing.sh DEST [NAME] [KIND]
set -euo pipefail
DEST="${1:?destination}"
NAME="${2:-projet}"
KIND="${3:-imported}"
NAME="${NAME//\//-}"
HERE="$(cd "$(dirname "$0")" && pwd)"
SRC="$HERE/project"

mkdir -p "$DEST/.grok/skills" "$DEST/docs/reports"

put() {
  local rel="$1"
  local from="$SRC/$rel"
  local to="$DEST/$rel"
  [[ -f "$from" ]] || return 0
  [[ -f "$to" ]] && return 0
  mkdir -p "$(dirname "$to")"
  sed -e "s/__NAME__/${NAME}/g" -e "s/__KIND__/${KIND}/g" "$from" > "$to"
}

put "AGENTS.md"
put "docs/lifecycle.md"
put "docs/map.md"
put ".grok/skills/git/SKILL.md"
put ".grok/skills/session/SKILL.md"
put ".grok/skills/python/SKILL.md"
put ".grok/skills/npm/SKILL.md"
put ".grok/skills/linux/SKILL.md"
