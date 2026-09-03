---
name: forge-session
description: Clôturer une session Grok Build dans une forge (rapport, install.sh à jour, push branche grok/*).
---

# forge-session

À la fin d'une session qui a modifié des fichiers :

1. Vérifier que `install.sh` reflète tout nouveau prérequis. L'éditer si besoin.
2. Lancer les tests ciblés (`make test`) ou documenter l'impossibilité.
3. Exécuter `.grok/hooks/session-wrap.sh "<titre court>"`.
4. Ne jamais force-push `main`. Ne jamais committer `.env`, `.venv`, `node_modules`.
