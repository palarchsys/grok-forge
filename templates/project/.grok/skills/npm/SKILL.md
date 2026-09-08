# npm

JS/TS du projet. Fullstack : le frontend est sous `frontend/` s’il existe.

| Fichier | Rôle |
| --- | --- |
| `package.json` ou `frontend/package.json` | scripts, deps |
| `src/` ou `frontend/src/` | code |

Ne pas toucher `.venv/` ni `pyproject.toml` (skill python).

`./install.sh` fait `npm install` si un `package.json` est à la racine. Scripts : ceux du package, rien d’inventé.
