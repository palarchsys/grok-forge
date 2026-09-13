# Carte — palarchsys/grok-forge

Ne pas lire le dépôt : cette table suffit.

| Chemin | Rôle | Quand l’ouvrir |
| --- | --- | --- |
| `AGENTS.md` | Routeur | Toujours, et seulement ça au départ |
| `install.sh` | Bootstrap machine + clone outils | Install / session |
| `setup-grok-forge` | Menu terminal (SSH) | Menu / lanceur |
| `setup-grok-forge.sh` | Génère un projet dans `~/GrokForge` | Nouveau projet |
| `forge_tui.py` | Shim vers le menu bash | Ancien lanceur seulement |
| `templates/apply-framing.sh` | Pose le cadrage sans écraser | Cadrage projets |
| `templates/project/` | AGENTS + skills + mermaid copiés | Cadrage projets |
| `.grok/skills/git/SKILL.md` | Git | Branche / commit / push |
| `.grok/skills/session/SKILL.md` | Session | Install, démarrage |
| `.grok/skills/forge/SKILL.md` | Ce dépôt | Menu / génération |
| `.grok/skills/forge-session/SKILL.md` | Clôture | Fin de session |
| `docs/lifecycle.md` | Mermaid | Comprendre le flux |
| `docs/reports/` | Rapports | Fin non triviale |
