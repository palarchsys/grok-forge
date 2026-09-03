# Grok Forge

Installateur unifié et menu TUI pour travailler avec [Grok Build](https://x.ai/build) : installer les outils, forger un nouveau projet, ou cloner un dépôt déjà présent sur ton compte GitHub, puis laisser Grok coder et pousser proprement.

Cible : **Ubuntu / Linux**, stacks **Python**, **npm**, ou les deux. Interface plein écran inspirée du thème **GrokNight** de Grok Build.

Repo public : [palarchsys/grok-forge](https://github.com/palarchsys/grok-forge)

---

## Installation (une ligne)

Dans un terminal Linux :

```bash
curl -fsSL https://raw.githubusercontent.com/palarchsys/grok-forge/main/install.sh | bash
```

Le script est **interactif** (il lit le clavier même via `curl | bash`). Il ne demande **aucun flag**.

Il va, dans l’ordre, si ce n’est pas déjà fait :

1. Installer les paquets de base (`git`, `curl`, `python3`, compilateur, etc.)
2. Installer **GitHub CLI** (`gh`) et proposer `gh auth login`
3. Installer **Grok Build** (`curl -fsSL https://x.ai/cli/install.sh | bash`)
4. Proposer **uv** (Python) et **Node LTS** via fnm
5. Cloner / mettre à jour cet outillage dans `~/.local/share/grok-forge`
6. Créer la commande `grok-forge` dans `~/.local/bin`

À la fin : *ouvrir le menu maintenant ?* → oui.

Les fois suivantes :

```bash
grok-forge
```

Grok Build seul, une fois installé :

```bash
grok --version
```

---

## Menu principal

| Choix | Effet |
| --- | --- |
| **Forger un nouveau projet** | Assistant (nom, type, options) → **plan à approuver** → création des fichiers, venv / npm, `install.sh` du projet, repo GitHub créé ou branché, push initial |
| **Cloner un repo de mon GitHub** | Liste tes dépôts (`gh repo list`) → clone dans `~/GrokForge/<nom>` → pose `AGENTS.md` + hook de session s’ils manquent → ouvrir Grok dans ce dossier |
| **Ouvrir un projet local** | Liste ce qui est déjà dans `~/GrokForge` → prépare les fichiers agent si besoin → lance `grok` |

Rien n’est écrit tant que tu n’as pas **approuvé le plan** (nouveau projet).

---

## Types de projet

1. `python-cli` — outil / service Python  
2. `python-web` — API (FastAPI par défaut)  
3. `npm-web` — app Node  
4. `fullstack` — backend Python + frontend npm  
5. `linux-system` — scripts et units systemd  

Selon le type, la forge génère notamment :

- `AGENTS.md` (contrat pour Grok Build)
- `install.sh` (réinstall depuis un clone Linux)
- `install.ps1` seulement si tu as coché Windows
- `pyproject.toml`, `src/`, `tests/`, `.venv` (uv de préférence)
- `package.json` (à la racine ou `frontend/`)
- `.gitignore`, `.grokignore`, `.env.example`
- `.github/workflows/ci.yml`
- `deploy/systemd/` si pertinent
- `.grok/hooks/session-wrap.sh`

Les **projets** vivent dans `~/GrokForge/`.  
L’**outillage** (ce dépôt) vit dans `~/.local/share/grok-forge`.

---

## Git : créer, cloner, pousser

### Nouveau projet

- Si `gh` est connecté et que tu as accepté « créer le repo » : `gh repo create` + `git push -u origin main` pour le bootstrap.
- Ensuite le travail agent se fait sur `grok/<sujet>`, pas un force-push sur `main`.

### Repo déjà existant sur ton compte

Menu → cloner → choisir dans la liste → `gh repo clone` dans `~/GrokForge`.  
Le remote `origin` est déjà le bon. Grok ouvre **dans** ce dossier.

### Fin de session

```bash
cd ~/GrokForge/ton-projet
.grok/hooks/session-wrap.sh "titre court"
```

Le hook :

- écrit un rapport dans `docs/reports/`
- crée une branche `grok/…` si tu étais sur `main`
- commit conventionnel
- `git push -u origin HEAD`

Jamais de `--force` sur `main`. Jamais de `.env`, `.venv`, `node_modules` dans git.

---

## Relancer un projet depuis Git (machine neuve)

Sur le **projet** forgé, pas sur grok-forge :

```bash
git clone https://github.com/palarchsys/TON-PROJET.git
cd TON-PROJET
chmod +x install.sh
./install.sh
```

`install.sh` du projet installe les paquets manquants, recrée le venv Python et/ou `npm ci`.

---

## Fichiers de ce dépôt

| Fichier | Rôle |
| --- | --- |
| `install.sh` | Bootstrap unifié (Grok Build + forge), interactif |
| `setup-grok-forge` | Lanceur TUI (`textual`) |
| `setup-grok-forge.sh` | Backend : génération du projet, git, GitHub |
| `forge_tui.py` | Menu GrokNight (nouveau / clone / local) |
| `.grok/skills/forge-session/SKILL.md` | Skill de clôture de session pour Grok Build |

---

## Prérequis

- Linux (Ubuntu 26.04 visé, Debian-like accepté)
- Compte [xAI / SuperGrok](https://x.ai) pour Grok Build
- Compte GitHub + `gh auth login` pour lister / créer / pousser tes repos
- Terminal vrai (TTY) pour la TUI

Aucun secret n’est stocké dans ce dépôt. L’auth GitHub passe par `gh` sur ta machine. L’auth Grok Build passe par le login officiel du CLI.

---

## Dépannage

**`grok-forge` introuvable**  
```bash
export PATH="$HOME/.local/bin:$PATH"
# ou rouvre le terminal après install (le script ajoute la ligne dans ~/.bashrc)
```

**`grok` introuvable**  
Relance `grok-forge` ou :

```bash
curl -fsSL https://x.ai/cli/install.sh | bash
```

**La TUI ne s’ouvre pas après `curl | bash`**  
C’est normal si le pipe n’a pas de TTY propre. Tape simplement `grok-forge`.

**`gh repo list` vide**  
```bash
gh auth login
gh auth setup-git
```

**textual manquant**  
Le lanceur fait `pip install --user textual` tout seul. Fallback :  
`bash ~/.local/share/grok-forge/setup-grok-forge.sh`

---

## Licence

MIT. Grok Build reste le produit d’xAI ; ce dépôt n’est que l’outillage de forge autour.
