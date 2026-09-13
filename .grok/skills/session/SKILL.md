# Session

Point d’entrée unique de l’outillage : `install.sh` (machine) puis `grok-forge` (menu).

## Démarrage

```bash
curl -fsSL https://raw.githubusercontent.com/palarchsys/grok-forge/main/install.sh | bash
```

Les fois suivantes : `grok-forge`. Ne pas inventer une autre séquence.

`install.sh` est idempotent : outils déjà là → skip ; clone déjà là → `git fetch` + `reset --hard FETCH_HEAD` (outillage seulement).

## Pendant

1. Table de routage dans `AGENTS.md` → un skill.
2. Modifier uniquement les cibles.
3. Commit + push selon `.grok/skills/git/SKILL.md`.

## Fin

`.grok/skills/forge-session/SKILL.md` si la session a modifié des fichiers.
