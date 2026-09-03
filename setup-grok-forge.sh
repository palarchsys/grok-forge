#!/usr/bin/env bash
set -euo pipefail
ask(){ local p="$1" d="${2:-}" k="${3:-}" r
  if [[ "${FORGE_NI:-0}" == "1" && -n "$k" && -n "${!k:-}" ]]; then printf '%s' "${!k}"; return; fi
  if [[ -n "$d" ]]; then read -r -p "$p [$d] : " r || true; printf '%s' "${r:-$d}"
  else read -r -p "$p : " r || true; printf '%s' "$r"; fi
}
yesno(){ local p="$1" d="${2:-y}" k="${3:-}" r
  if [[ "${FORGE_NI:-0}" == "1" && -n "$k" ]]; then r="${!k:-$d}"; [[ "$r" =~ ^[yYoO1]$ ]]; return; fi
  read -r -p "$p [$d] : " r || true; r="${r:-$d}"; [[ "$r" =~ ^[yYoO1]$ ]]
}
ok(){ printf '✔ %s\n' "$*"; }
NAME="$(ask "Nom" "High-Fortress" FORGE_NAME)"; NAME="${NAME// /-}"
PARENT="$(ask "Parent" "${HOME}/GrokForge" FORGE_PARENT)"
ROOT="${PARENT}/${NAME}"
KIND="$(ask "Type 1-5" "4" FORGE_KIND)"
WANT_PY=0; WANT_NPM=0
case "$KIND" in
  1) KINDN=python-cli; WANT_PY=1 ;;
  2) KINDN=python-web; WANT_PY=1 ;;
  3) KINDN=npm-web; WANT_NPM=1 ;;
  5) KINDN=linux-system; WANT_PY=1 ;;
  *) KINDN=fullstack; WANT_PY=1; WANT_NPM=1 ;;
esac
yesno "Repo prive ?" y FORGE_PRIVATE && VIS=private || VIS=public
yesno "Creer GitHub + push ?" y FORGE_CREATE_GH && CREATE_GH=1 || CREATE_GH=0
yesno "install.ps1 Windows ?" n FORGE_WINDOWS && WIN=1 || WIN=0
mkdir -p "$ROOT"/{docs/reports,.grok/hooks}
cd "$ROOT"
[[ -d .git ]] || git init -b main >/dev/null
PKG="$(printf '%s' "$NAME" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '_' | sed 's/_$//')"
[[ -n "$PKG" ]] || PKG=app
cat > .gitignore <<'EOF'
.venv/
node_modules/
.env
__pycache__/
.grok/sessions/
EOF
cat > AGENTS.md <<EOF
# AGENTS.md — ${NAME}
Projet **${KINDN}**. Plan Mode si plus d un fichier.
Git: branche grok/<sujet>, Conventional Commits, pas de force-push sur main.
Pas de secrets. Mettre a jour install.sh avec tout nouveau prerequis.
EOF
cat > README.md <<EOF
# ${NAME}
chmod +x install.sh && ./install.sh
EOF
echo '# cp .env.example .env' > .env.example
{
printf '%s\n' '#!/usr/bin/env bash' 'set -euo pipefail' 'cd "$(dirname "$0")"'
printf '%s\n' 'if command -v apt-get >/dev/null; then'
printf '%s\n' '  M=()'
printf '%s\n' '  for p in git curl python3 python3-venv python3-pip; do dpkg -s "$p" >/dev/null 2>&1 || M+=("$p"); done'
printf '%s\n' '  ((${#M[@]})) && sudo apt-get update -y && sudo apt-get install -y "${M[@]}"'
printf '%s\n' 'fi'
if [[ "$WANT_PY" -eq 1 ]]; then
printf '%s\n' 'if command -v uv >/dev/null; then uv venv && uv pip install -e ".[dev]" || true'
printf '%s\n' 'else python3 -m venv .venv && .venv/bin/pip install -U pip && .venv/bin/pip install -e ".[dev]" || true; fi'
fi
if [[ "$WANT_NPM" -eq 1 ]]; then
printf '%s\n' 'command -v npm >/dev/null && { [[ -f package-lock.json ]] && npm ci || npm install; } || true'
fi
printf '%s\n' '[[ -f .env ]] || cp .env.example .env' 'echo OK'
} > install.sh
chmod +x install.sh
[[ "$WIN" -eq 1 ]] && printf '%s\n' '$ErrorActionPreference="Stop"' 'Write-Host OK' > install.ps1
if [[ "$WANT_PY" -eq 1 ]]; then
  mkdir -p "src/${PKG}" tests
  cat > pyproject.toml <<EOF
[project]
name = "${PKG}"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = []
[project.optional-dependencies]
dev = ["pytest>=8", "ruff>=0.6"]
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"
[tool.setuptools.packages.find]
where = ["src"]
EOF
  echo "__version__ = '0.1.0'" > "src/${PKG}/__init__.py"
  echo "def test_ok(): assert True" > tests/test_smoke.py
fi
if [[ "$WANT_NPM" -eq 1 ]]; then
  mkdir -p src
  printf '%s\n' "{\"name\":\"${NAME}\",\"version\":\"0.1.0\",\"private\":true,\"scripts\":{\"dev\":\"node src/index.js\",\"test\":\"node --test\"}}" > package.json
  echo "console.log('${NAME}')" > src/index.js
fi
cat > .grok/hooks/session-wrap.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
TITLE="${1:-session}"; STAMP="$(date +%Y-%m-%d-%H%M)"
SLUG="$(printf '%s' "$TITLE" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed 's/-$//')"
mkdir -p docs/reports
B="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo main)"
if [[ "$B" == "main" || "$B" == "master" ]]; then B="grok/${SLUG}-${STAMP}"; git checkout -b "$B"; fi
[[ -f "docs/reports/${STAMP}-${SLUG}.md" ]] || echo "# $TITLE" > "docs/reports/${STAMP}-${SLUG}.md"
git add -A
git diff --cached --quiet || git commit -m "docs: rapport ${STAMP} — ${TITLE}"
git remote get-url origin >/dev/null 2>&1 && git push -u origin HEAD || true
EOF
chmod +x .grok/hooks/session-wrap.sh
if [[ "$WANT_PY" -eq 1 ]]; then
  if command -v uv >/dev/null; then uv venv && uv pip install -e ".[dev]" || true
  else python3 -m venv .venv && .venv/bin/pip install -U pip && .venv/bin/pip install -e ".[dev]" || true
  fi
fi
[[ "$WANT_NPM" -eq 1 ]] && command -v npm >/dev/null && npm install || true
git add -A
if ! git rev-parse HEAD >/dev/null 2>&1; then git commit -m "chore: bootstrap ${NAME} (${KINDN})" || true
elif ! git diff --cached --quiet; then git commit -m "chore: bootstrap ${NAME} (${KINDN})" || true
fi
if ! git remote get-url origin >/dev/null 2>&1; then
  if [[ "$CREATE_GH" -eq 1 ]] && command -v gh >/dev/null && gh auth status >/dev/null 2>&1; then
    gh repo create "$NAME" --source=. --remote=origin --"$VIS" --push || true
  fi
else
  git push -u origin HEAD || true
fi
ok "$ROOT"
