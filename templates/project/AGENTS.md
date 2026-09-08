# AGENTS.md

Tu es Grok Build sur ce dépôt.

**Lis uniquement ce fichier au départ.** N’ouvre un skill que si le tableau le demande. Ne parcours pas le dépôt. Ne grep pas large. N’ouvre pas `node_modules/`, `.venv/`, `dist/`.

## Projet

- Nom : __NAME__
- Type : __KIND__
- Cadre : Grok Forge (agents routeurs, skills à la demande)

## Table de routage

| Intention | Lire (un skill) | Cibles | Ne pas ouvrir |
| --- | --- | --- | --- |
| Git, branche, commit, push | `.grok/skills/git/SKILL.md` | — | src/, tests/ |
| Installer / démarrer | `.grok/skills/session/SKILL.md` | `install.sh`, `README.md` | — |
| Code Python | `.grok/skills/python/SKILL.md` | `src/`, `tests/`, `pyproject.toml` | frontend/, node_modules |
| Code npm / frontend | `.grok/skills/npm/SKILL.md` | `package.json`, sources JS | `.venv/` |
| Scripts Linux / systemd | `.grok/skills/linux/SKILL.md` | `scripts/`, `install.sh` | — |
| Comprendre le cycle | `docs/lifecycle.md` | — | le code |
| Où est quoi | `docs/map.md` | — | le code |

Plusieurs intentions : session → git → langage.

## Invariants

- Si HEAD est `main` ou `master` : `git checkout -b grok/<sujet>`.
- Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`).
- Jamais de force-push sur `main` / `master`.
- Jamais committer `.env`, `.venv`, `node_modules`, secrets, clés.
- Push : `git push -u origin HEAD`.
- Diffs petits. Tests si le socle en a.

## Definition of done

- Changement limité aux cibles de la table.
- Note courte dans `docs/reports/` si le changement est non trivial.
- `./install.sh` reste le seul point d’entrée local.

## Interdit

- Relire tout le dépôt « pour contexte ».
- Ajouter abstractions, flags, ou docs hors demande.
- Modifier un skill que tu n’as pas ouvert via la table.
