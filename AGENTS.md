# AGENTS.md

Tu es Grok Build sur **palarchsys/grok-forge**.

**Lis uniquement ce fichier au départ.** N’ouvre un skill que si le tableau le demande. Ne parcours pas le dépôt. Ne grep pas large.

## Produit

Installateur unifié + **menu terminal** (SSH, listes numérotées). Forge des projets Grok Build : `AGENTS.md` routeur, skills à la demande, mermaid. Linux. Interactif, **aucun flag CLI**. Pas de TUI Textual.

Les **projets** vivent dans `~/GrokForge/`.  
L’**outillage** (ce dépôt) vit dans `~/.local/share/grok-forge` ou ici.

## Table de routage

| Intention | Lire (un skill) | Cibles | Ne pas ouvrir |
| --- | --- | --- | --- |
| Menu / lanceur | `.grok/skills/forge/SKILL.md` | `setup-grok-forge` | `templates/` |
| Installateur `curl \| bash` | `.grok/skills/session/SKILL.md` | `install.sh` | le menu |
| Génération de projet | `.grok/skills/forge/SKILL.md` | `setup-grok-forge.sh`, `templates/` | — |
| Cadrage posé dans un projet | `.grok/skills/session/SKILL.md` | `templates/project/` | le menu |
| Git, branche, push | `.grok/skills/git/SKILL.md` | — | src des projets |
| Comprendre le cycle | `docs/lifecycle.md` | — | le code |
| Où est quoi | `docs/map.md` | — | le code |

Plusieurs intentions : session → git → forge.

## Invariants

- Interactif, lectures clavier via `/dev/tty`, aucun paramètre CLI.
- Menu = bash simple (numéros + Entrée). Pas de textual, pas d’écran alternatif, pas de souris.
- Si le clone outils existe déjà : `git fetch` + `git reset --hard FETCH_HEAD` (clone d’outillage, pas un projet).
- Jamais de force-push sur `main` / `master`.
- Jamais committer `.env`, `.venv`, `node_modules`, secrets.
- Conventional Commits.
- Push : `git push -u origin HEAD`.
- Chaque projet forgé / cloné reçoit `AGENTS.md` routeur + `.grok/skills/*` + `docs/lifecycle.md` **sans écraser** un fichier déjà présent.
- Si tu changes le cadrage des projets : `templates/project/` **et** `templates/apply-framing.sh`. Le menu et `setup-grok-forge.sh` ne font qu’appeler ce script.

## Definition of done

- Diff limité aux cibles de la table.
- `curl | bash` + `grok-forge` restent le seul chemin utilisateur.
- Note dans `docs/reports/` si le changement n’est pas trivial.

## Interdit

- Relire tout le dépôt « pour contexte ».
- Ajouter des flags CLI, de l’auth, ou une base.
- Réintroduire une TUI (textual, curses, plein écran).
- Fusionner les skills dans un pavé unique (ça relance la facture tokens).
