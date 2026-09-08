---
name: forge
description: >
  Outillage Grok Forge (install.sh, TUI, génération de projet, cadrage AGENTS).
  Triggers: forge, TUI, install.sh, setup-grok-forge, templates, cadrage, mermaid.
---

# Forge (ce dépôt)

1. Relire `AGENTS.md` (déjà fait si tu es ici).
2. Ouvrir **un** fichier :

| Sujet | Fichier |
| --- | --- |
| Menu TUI | `forge_tui.py` |
| Bootstrap machine | `install.sh` |
| Socle d’un projet | `setup-grok-forge.sh` |
| Cadrage posé dans les projets | `templates/apply-framing.sh` + `templates/project/` |

3. S’arrêter.

Si tu changes un skill git/session/python/npm/linux **des projets**, édite `templates/project/` (c’est la copie poussée dans `~/GrokForge/...`). Les skills à la racine `.grok/skills/` sont pour **ce** dépôt.

Ne pas fusionner les skills. Ne pas ajouter de flags CLI.
