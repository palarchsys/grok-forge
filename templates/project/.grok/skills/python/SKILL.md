# Python

Stack : Python ≥ 3.12, `pyproject.toml`, paquets sous `src/`.

| Fichier | Rôle |
| --- | --- |
| `pyproject.toml` | deps, outil |
| `src/` | code |
| `tests/` | pytest |

Ne pas toucher `frontend/` ni `package.json` (skill npm).

L’environnement est créé par `./install.sh`. Ensuite :

```bash
.venv/bin/python -m pytest
```

Pas de `sudo`, pas de `pip install` global.
