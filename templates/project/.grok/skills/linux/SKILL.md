# Linux

Scripts et unités systemd. Ubuntu-like, bash `set -euo pipefail`.

`scripts/`, `install.sh`. Pas de secret en dur. `.env.example` documente les variables.

Idempotent : relancer `./install.sh` ne casse pas un état déjà bon.
