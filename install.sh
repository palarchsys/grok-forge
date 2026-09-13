#!/usr/bin/env bash
# Installateur unifie Grok Forge + Grok Build. Aucun parametre.
# curl -fsSL https://raw.githubusercontent.com/palarchsys/grok-forge/main/install.sh | bash
set -euo pipefail
TTY="/dev/tty"
[[ -e "$TTY" ]] || TTY="/dev/stdin"
ask() {
  local p="$1" d="${2:-}" r
  if [[ -n "$d" ]]; then printf '%s [%s] : ' "$p" "$d" >"$TTY"; else printf '%s : ' "$p" >"$TTY"; fi
  read -r r <"$TTY" || true
  printf '%s' "${r:-$d}"
}
yesno() {
  local p="$1" d="${2:-y}" r
  printf '%s [%s] : ' "$p" "$d" >"$TTY"
  read -r r <"$TTY" || true
  r="${r:-$d}"
  [[ "$r" =~ ^[yYoO1]$ ]]
}
say(){ printf '→ %s\n' "$*"; }
ok(){ printf '✔ %s\n' "$*"; }
die(){ printf '✖ %s\n' "$*" >&2; exit 1; }

FORGE_HOME="${HOME}/.local/share/grok-forge"
FORGE_BIN="${HOME}/.local/bin"
FORGE_WORK="${HOME}/GrokForge"
FORGE_REF="main"
FORGE_REPO_DEFAULT="https://github.com/palarchsys/grok-forge.git"
export PATH="${FORGE_BIN}:${HOME}/.local/bin:${HOME}/.grok/bin:${HOME}/.cargo/bin:${PATH}"

cat <<EOF

  Grok Forge — installateur unifie
  Grok Build + forge + clone de tes repos

EOF

if [[ -f /etc/os-release ]]; then . /etc/os-release; say "OS ${ID:-?} ${VERSION_ID:-?}"; fi

apt_need() {
  command -v apt-get >/dev/null 2>&1 || return 0
  local miss=() p
  for p in "$@"; do dpkg -s "$p" >/dev/null 2>&1 || miss+=("$p"); done
  ((${#miss[@]})) || return 0
  say "Paquets : ${miss[*]}"
  if yesno "Installer avec apt ?" y; then
    if [[ "${EUID:-1}" -eq 0 ]]; then
      apt-get update -y && DEBIAN_FRONTEND=noninteractive apt-get install -y "${miss[@]}"
    else
      sudo apt-get update -y && sudo DEBIAN_FRONTEND=noninteractive apt-get install -y "${miss[@]}"
    fi
  fi
}
apt_need git curl ca-certificates build-essential python3 python3-venv python3-pip python3-full unzip jq

if ! command -v gh >/dev/null 2>&1; then
  if yesno "Installer GitHub CLI ?" y; then
    sudo mkdir -p -m 755 /etc/apt/keyrings
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg >/dev/null
    sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list >/dev/null
    sudo apt-get update -y && sudo apt-get install -y gh
  fi
fi
if command -v gh >/dev/null 2>&1 && ! gh auth status >/dev/null 2>&1; then
  if yesno "Connecter GitHub maintenant ?" y; then
    gh auth login || true
    gh auth setup-git || true
  fi
fi

if command -v grok >/dev/null 2>&1; then
  ok "Grok Build deja installe"
else
  if yesno "Installer Grok Build ?" y; then
    curl -fsSL https://x.ai/cli/install.sh | bash
    export PATH="${HOME}/.local/bin:${HOME}/.grok/bin:${PATH}"
    if command -v grok >/dev/null; then
      ok "Grok Build installe — on continue grok-forge"
    else
      say "Grok Build : ouvre un nouveau terminal si la commande grok est introuvable."
    fi
  fi
fi

if ! command -v uv >/dev/null 2>&1; then
  yesno "Installer uv (Python) ?" y && curl -LsSf https://astral.sh/uv/install.sh | sh && export PATH="${HOME}/.local/bin:${PATH}"
fi
if ! command -v node >/dev/null 2>&1; then
  if yesno "Installer Node LTS (fnm) ?" y; then
    curl -fsSL https://fnm.vercel.app/install | bash
    export PATH="${HOME}/.local/share/fnm:${PATH}"
    if [[ -x "${HOME}/.local/share/fnm/fnm" ]]; then
      eval "$("${HOME}/.local/share/fnm/fnm" env --shell bash)" || true
      "${HOME}/.local/share/fnm/fnm" install --lts || true
    fi
  fi
fi

mkdir -p "$FORGE_HOME" "$FORGE_BIN" "$FORGE_WORK"
SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-}")" 2>/dev/null && pwd || true)"
if [[ -n "${SELF_DIR}" && -f "${SELF_DIR}/setup-grok-forge.sh" && -f "${SELF_DIR}/forge_tui.py" ]]; then
  FORGE_HOME="$SELF_DIR"
  ok "Forge locale $FORGE_HOME"
else
  if [[ -d "$FORGE_HOME/.git" ]]; then
    say "Mise a jour de l'outillage"
    git -C "$FORGE_HOME" pull --ff-only || true
  else
    REPO="${FORGE_REPO:-$FORGE_REPO_DEFAULT}"
    say "Telechargement de l'outillage Grok Forge"
    git clone --depth 1 --branch "$FORGE_REF" "$REPO" "$FORGE_HOME" \
      || git clone --depth 1 "$REPO" "$FORGE_HOME" \
      || die "clone outillage impossible. Verifie le reseau."
  fi
fi
[[ -f "$FORGE_HOME/setup-grok-forge.sh" ]] || die "setup-grok-forge.sh absent"
chmod +x "$FORGE_HOME"/setup-grok-forge.sh "$FORGE_HOME"/install.sh "$FORGE_HOME"/forge_tui.py 2>/dev/null || true
[[ -f "$FORGE_HOME/setup-grok-forge" ]] && chmod +x "$FORGE_HOME/setup-grok-forge"

ensure_tui() {
  local py="$FORGE_HOME/.venv/bin/python"
  if [[ -x "$py" ]] && "$py" -c "import textual" >/dev/null 2>&1; then
    return 0
  fi
  say "Environnement du menu (venv, pas le Python systeme)"
  if command -v uv >/dev/null 2>&1; then
    uv venv "$FORGE_HOME/.venv"
    uv pip install --python "$py" textual
  else
    python3 -m venv "$FORGE_HOME/.venv"
    "$FORGE_HOME/.venv/bin/pip" install -U pip textual
  fi
  "$FORGE_HOME/.venv/bin/python" -c "import textual" >/dev/null 2>&1 \
    || die "textual introuvable. Installe python3-venv et relance."
}
ensure_tui
FORGE_PY="$FORGE_HOME/.venv/bin/python"

cat > "$FORGE_BIN/grok-forge" <<EOF
#!/usr/bin/env bash
set -euo pipefail
export PATH="\$HOME/.local/bin:\$HOME/.grok/bin:\$PATH"
FORGE_HOME="$FORGE_HOME"
# Mise a jour silencieuse si origin/main a avance
if [[ -d "\$FORGE_HOME/.git" && -z "\${FORGE_NO_UPDATE:-}" ]]; then
  git -C "\$FORGE_HOME" fetch --quiet --depth 1 origin main 2>/dev/null || true
  LOCAL=\$(git -C "\$FORGE_HOME" rev-parse HEAD 2>/dev/null || true)
  REMOTE=\$(git -C "\$FORGE_HOME" rev-parse FETCH_HEAD 2>/dev/null || true)
  if [[ -n "\$LOCAL" && -n "\$REMOTE" && "\$LOCAL" != "\$REMOTE" ]]; then
    git -C "\$FORGE_HOME" pull --ff-only --quiet origin main 2>/dev/null || true
  fi
fi
PY="\$FORGE_HOME/.venv/bin/python"
if [[ ! -x "\$PY" ]]; then PY=python3; fi
# Coupe un tracking souris laisse par une session precedente (SGR 1003)
printf '\\033[?1003l\\033[?1002l\\033[?1000l\\033[?1006l\\033[?1015l' >/dev/tty 2>/dev/null || true
# stdin = vrai TTY (evite le pipe de curl | bash)
if [[ -e /dev/tty ]]; then
  exec </dev/tty "\$PY" "\$FORGE_HOME/forge_tui.py"
else
  exec "\$PY" "\$FORGE_HOME/forge_tui.py"
fi
EOF
chmod +x "$FORGE_BIN/grok-forge"
if [[ -f "${HOME}/.bashrc" ]] && ! grep -q 'HOME/.local/bin' "${HOME}/.bashrc" 2>/dev/null; then
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> "${HOME}/.bashrc"
fi
export PATH="${FORGE_BIN}:$PATH"
ok "Commande : grok-forge"

if [[ -e /dev/tty ]]; then
  if yesno "Ouvrir le menu (forger / cloner / grok) ?" y; then
    # stdin etait le pipe curl : on bascule sur le vrai terminal
    exec </dev/tty "$FORGE_PY" "$FORGE_HOME/forge_tui.py"
  fi
fi
say "Plus tard : grok-forge"
ok "Installation terminee."
