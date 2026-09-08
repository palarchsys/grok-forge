# Git

Procédure git seulement. Ne pas ouvrir le code applicatif.

## Branche

Si HEAD est `main` ou `master` :

```bash
git checkout -b grok/<sujet-court>
```

Ne pas committer sur main « pour aller plus vite ».

## Commit

- Conventional Commits.
- Un sujet = un commit si possible.
- Jamais `--amend` d’un commit déjà poussé.
- Jamais `--force` / `--force-with-lease` sur `main` / `master`.

## Ne pas versionner

`.env`, `.venv/`, `node_modules/`, `__pycache__/`, secrets, clés, dumps.

## Push

```bash
git push -u origin HEAD
```

Pas de PR automatique. Rapport : `docs/reports/`.
