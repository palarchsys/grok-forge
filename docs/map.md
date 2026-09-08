# Carte — palarchsys/grok-forge

Ne pas lire le dépôt : cette table suffit.

| Chemin | Rôle | Quand l’ouvrir |
| --- | --- | --- |
| `AGENTS.md` | Routeur | Toujours, et seulement ça au départ |
| `install.sh` | Bootstrap machine + clone outils | Install / session |
| `forge_tui.py` | Menu GrokNight | TUI |
| `setup-grok-forge.sh` | Génère un projet dans `~/GrokForge` | Nouveau projet |
| `setup-grok-forge` | Wrapper lanceur | Rare |
| `templates/apply-framing.sh` | Pose le cadrage sans écraser | Cadrage projets |
| `templates/project/` | AGENTS + skills + mermaid copiés | Cadrage projets |
| `.grok/skills/git/SKILL.md` | Git | Branche / commit / push |
| `.grok/skills/session/SKILL.md` | Session | Install, démarrage |
| `.grok/skills/forge/SKILL.md` | Ce dépôt | TUI / génération |
| `.grok/skills/forge-session/SKILL.md` | Clôture | Fin de session |
| `docs/lifecycle.md` | Mermaid | Comprendre le flux |
| `docs/reports/` | Rapports | Fin non triviale |
