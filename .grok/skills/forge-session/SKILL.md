---
name: forge-session
description: Clôturer une session Grok Build dans une forge (rapport, install.sh à jour, push branche grok/*).
---

# forge-session

À la fin d’une session qui a modifié des fichiers :

1. Vérifier que `install.sh` reflète tout nouveau prérequis. L’éditer si besoin.
2. Lancer les tests ciblés, ou documenter l’impossibilité.
3. Exécuter `.grok/hooks/session-wrap.sh "<titre court>"` s’il existe (projets). Sinon : branche `grok/<sujet>`, commit, `git push -u origin HEAD`.
4. Ne jamais force-push `main`. Ne jamais committer `.env`, `.venv`, `node_modules`.
5. Note courte dans `docs/reports/` si non trivial.

Git détaillé : `.grok/skills/git/SKILL.md`.
