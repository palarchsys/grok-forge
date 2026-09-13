#!/usr/bin/env python3
"""Menu GrokNight : forger, cloner, ouvrir. Le cadrage AGENTS est dans templates/.

Souris volontairement coupee : GNOME Terminal + mode 1003 envoie des
sequences SGR `CSI < 35 ; x ; y M` (mouvement). Si elles ne sont pas
parsees, elles s'affichent en clair dans le Header et saturent stdin —
plus aucune touche n'arrive au menu.

Workers Textual 2+ : une fonction sync sans thread=True leve
WorkerError ("non-async function as an async worker"). Les taches
longues (forge, clone) sont donc async, le sous-processus tourne
via asyncio sans bloquer le rendu.
"""
from __future__ import annotations
import asyncio, atexit, os, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VENV_PY = HERE / ".venv" / "bin" / "python"
# DECSET mouse : 1000 clic, 1002 drag, 1003 tout mouvement, 1006 SGR, 1015 urxvt
_MOUSE_OFF = "\033[?1003l\033[?1002l\033[?1000l\033[?1006l\033[?1015l\033[?1005l"


def _mouse_off() -> None:
    try:
        fd = os.open("/dev/tty", os.O_WRONLY)
        os.write(fd, _MOUSE_OFF.encode())
        os.close(fd)
    except OSError:
        try:
            sys.stdout.write(_MOUSE_OFF)
            sys.stdout.flush()
        except Exception:
            pass


def _bind_tty() -> None:
    """curl|bash laisse stdin sur le pipe : le TUI doit lire /dev/tty."""
    if sys.stdin.isatty() and sys.stdout.isatty():
        return
    try:
        fd = os.open("/dev/tty", os.O_RDWR)
    except OSError:
        print("Lance grok-forge dans un terminal (GNOME, kitty, foot…).", file=sys.stderr)
        sys.exit(1)
    if not sys.stdin.isatty():
        os.dup2(fd, 0)
    if not sys.stdout.isatty():
        os.dup2(fd, 1)
    if not sys.stderr.isatty():
        os.dup2(fd, 2)
    if fd not in (0, 1, 2):
        os.close(fd)


def _ensure_textual() -> None:
    """Ubuntu PEP 668 : jamais pip --user sur le Python systeme. Venv local."""
    try:
        import textual  # noqa: F401
        return
    except ImportError:
        pass
    venv_dir = HERE / ".venv"
    if not VENV_PY.exists():
        uv = shutil.which("uv")
        if uv:
            subprocess.check_call([uv, "venv", str(venv_dir)])
            subprocess.check_call([uv, "pip", "install", "--python", str(VENV_PY), "textual"])
        else:
            subprocess.check_call([sys.executable, "-m", "venv", str(venv_dir)])
            subprocess.check_call([str(venv_dir / "bin" / "pip"), "install", "-U", "pip", "textual"])
    else:
        subprocess.check_call([str(venv_dir / "bin" / "pip"), "install", "textual"])
    os.execv(str(VENV_PY), [str(VENV_PY), str(Path(__file__).resolve()), *sys.argv[1:]])


_bind_tty()
_mouse_off()
atexit.register(_mouse_off)
_ensure_textual()

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import (
    Button,
    Checkbox,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    OptionList,
    RichLog,
    Static,
)
from textual.widgets.option_list import Option

BACKEND = HERE / "setup-grok-forge.sh"
FRAME = HERE / "templates" / "apply-framing.sh"
WORK = Path.home() / "GrokForge"
CSS = """
Screen { background: #141414; color: #e1e1e1; }
Header { background: #0c0c0c; color: #bb9af7; }
Footer { background: #0c0c0c; color: #6c6c6c; }
#brand { color: #bb9af7; text-style: bold; padding: 1 2 0 2; }
.panel { border: tall #242424; background: #111111; margin: 0 2 1 2; padding: 0 2; color: #8a8a8a; }
#hint { color: #8a8a8a; padding: 0 2 1 2; }
#hub-row { height: 1fr; margin: 0 2 1 2; }
#menu { width: 3fr; height: 1fr; background: #111111; border: tall #242424; }
#menu:focus { border: tall #7aa2f7; }
ListView > ListItem {
    background: #161616;
    padding: 1 2;
    height: 5;
    margin: 0 1 1 1;
    border-left: wide #2a2a2a;
}
ListView > ListItem.-highlight {
    background: #1a2333;
    border-left: wide #7aa2f7;
}
.card-title { color: #e1e1e1; text-style: bold; }
.card-blurb { color: #8a8a8a; }
#hub-detail { width: 2fr; height: 1fr; border: tall #242424; background: #111111; padding: 1 2; margin-left: 1; }
#detail-kicker { color: #7aa2f7; text-style: bold; }
#detail-title { color: #e1e1e1; text-style: bold; padding-top: 1; }
#detail-body { color: #a0a0a0; padding-top: 1; }
#detail-help { color: #6c6c6c; padding-top: 2; }
.field-label { color: #8a8a8a; padding: 0 2; }
Input { margin: 0 2 1 2; }
Checkbox { margin: 0 2; }
Button { margin: 1 2; }
OptionList { height: 1fr; margin: 0 2 1 2; background: #111111; }
OptionList:focus { border: tall #7aa2f7; }
#kind-list { height: 12; margin: 0 2 1 2; }
#log { height: 1fr; margin: 0 2 1 2; background: #0a0a0a; }
"""

KIND_LABELS = {
    "1": "Python CLI — outil, scripts, paquet",
    "2": "API Python — FastAPI par defaut",
    "3": "npm / Vite — app Node, frontend",
    "4": "Fullstack — backend Python + frontend npm",
    "5": "Linux — scripts et units systemd",
}


def sh(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)


def which(n):
    return shutil.which(n) is not None


def gh_repos():
    if not which("gh"):
        return []
    p = sh(["gh", "repo", "list", "--limit", "80", "--json", "nameWithOwner", "--jq", ".[].nameWithOwner"])
    return [x.strip() for x in p.stdout.splitlines() if x.strip()] if p.returncode == 0 else []


def local_projects():
    WORK.mkdir(parents=True, exist_ok=True)
    return [c for c in sorted(WORK.iterdir()) if c.is_dir() and ((c / ".git").exists() or (c / "AGENTS.md").exists())]


WRAP = """#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
T="${1:-session}"; S="$(date +%Y-%m-%d-%H%M)"
mkdir -p docs/reports
B="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo main)"
if [[ "$B" == main || "$B" == master ]]; then B="grok/$S"; git checkout -b "$B"; fi
echo "# $T" > docs/reports/$S.md
git add -A
git diff --cached --quiet || git commit -m "docs: $S $T"
git remote get-url origin >/dev/null 2>&1 && git push -u origin HEAD || true
"""


def prepare(root: Path, name: str | None = None, kind: str = "imported"):
    """Pose le cadrage s'il manque. N'ecrase jamais un AGENTS.md existant."""
    root.mkdir(parents=True, exist_ok=True)
    if FRAME.exists():
        sh(["bash", str(FRAME), str(root), name or root.name, kind])
    h = root / ".grok" / "hooks"
    h.mkdir(parents=True, exist_ok=True)
    w = h / "session-wrap.sh"
    if not w.exists():
        w.write_text(WRAP)
        w.chmod(0o755)
    (root / "docs" / "reports").mkdir(parents=True, exist_ok=True)


def launch(root: Path):
    _mouse_off()
    g = shutil.which("grok")
    if not g:
        for c in (Path.home() / ".local" / "bin" / "grok", Path.home() / ".grok" / "bin" / "grok"):
            if c.is_file():
                g = str(c)
                break
    if not g:
        return
    os.chdir(root)
    os.execvp(g, [g])


def _focus_menu(screen: Screen, wid: str = "#menu") -> None:
    try:
        menu = screen.query_one(wid)
        menu.focus()
        if isinstance(menu, ListView):
            if len(menu.children):
                menu.index = 0
        elif isinstance(menu, OptionList) and menu.option_count:
            menu.highlighted = 0
    except Exception:
        pass


class St:
    name = "High-Fortress"
    parent = str(WORK)
    kind = "4"
    windows = False
    private = True
    tools = True
    create_gh = True
    repo = ""
    local = ""


class Card(ListItem):
    """Ligne de menu : raccourci + titre + une ligne d'accroche."""

    def __init__(self, key: str, title: str, blurb: str, action_id: str, detail: str) -> None:
        self.key = key
        self.card_title = title
        self.blurb = blurb
        self.action_id = action_id
        self.detail = detail
        super().__init__(
            Static(f"{key}   {title}", classes="card-title"),
            Static(blurb, classes="card-blurb"),
            id="card-" + action_id,
        )


HUB = (
    (
        "1",
        "Forger un nouveau projet",
        "Python, npm ou fullstack — rien n'est ecrit avant ton OK.",
        "new",
        "Cree un depot vierge dans ~/GrokForge.\n\n"
        "Tu choisis le nom, le type (CLI Python, API FastAPI, npm/Vite, fullstack, systemd), "
        "la visibilite GitHub, puis tu approuves le plan (Ctrl+S).\n\n"
        "Pose AGENTS.md (routeur) + skills + mermaid. Un cadrage deja present n'est jamais ecrase.\n\n"
        "Ensuite : ouvrir Grok dans le projet.",
    ),
    (
        "2",
        "Cloner un repo GitHub",
        "Tes depots → ~/GrokForge → cadrage si manquant → Grok.",
        "clone",
        "Liste les repos de ton compte (gh). Clone, ou git pull --ff-only s'il est deja local.\n\n"
        "Si AGENTS.md manque, le cadrage est pose sans toucher tes fichiers.\n\n"
        "Puis tu ouvres Grok dans ce dossier — origin est deja le bon remote.",
    ),
    (
        "3",
        "Ouvrir un projet local",
        "Reprendre un dossier deja present dans ~/GrokForge.",
        "local",
        "Parcourt ~/GrokForge (dossiers git ou AGENTS.md).\n\n"
        "Complete le cadrage seulement s'il manque, puis lance Grok Build dans ce repertoire.",
    ),
    (
        "Q",
        "Quitter",
        "Fermer le menu. Tes projets restent en place.",
        "quit",
        "Quitte Grok Forge. Rien n'est detruit.\n\nRelance plus tard : grok-forge",
    ),
)


def _hub_cards() -> list[Card]:
    """Widgets neufs a chaque ecran : un ListItem n'a qu'un parent."""
    return [Card(*row) for row in HUB]


class Hub(Screen):
    BINDINGS = [
        Binding("q", "app.quit", "Quitter"),
        Binding("1", "go_new", "Forger"),
        Binding("2", "go_clone", "Cloner"),
        Binding("3", "go_local", "Local"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Label("Grok Forge", id="brand")
        g = "Grok OK" if which("grok") else "Grok absent"
        h = "gh OK" if which("gh") else "gh absent"
        yield Static(f"{g}   ·   {h}   ·   {WORK}", classes="panel")
        cards = _hub_cards()
        first = cards[0]
        yield Horizontal(
            ListView(*cards, id="menu"),
            Vertical(
                Static("Apercu", id="detail-kicker"),
                Static(first.card_title, id="detail-title"),
                Static(first.detail, id="detail-body"),
                Static("Fleches pour parcourir.  Entree pour ouvrir.  1 / 2 / 3 / Q", id="detail-help"),
                id="hub-detail",
            ),
            id="hub-row",
        )
        yield Footer()

    def on_mount(self):
        _focus_menu(self)
        try:
            item = self.query_one("#menu", ListView).highlighted_child
            if isinstance(item, Card):
                self._preview(item)
        except Exception:
            pass

    def _preview(self, card: Card | None):
        if card is None:
            return
        try:
            self.query_one("#detail-kicker", Static).update("Option  " + card.key)
            self.query_one("#detail-title", Static).update(card.card_title)
            self.query_one("#detail-body", Static).update(card.detail)
        except Exception:
            pass

    def _open(self, action_id: str | None):
        if action_id == "new":
            self.app.push_screen(Form())
        elif action_id == "clone":
            self.app.push_screen(CloneP())
        elif action_id == "local":
            self.app.push_screen(LocalP())
        elif action_id == "quit":
            self.app.exit()

    def on_list_view_highlighted(self, event: ListView.Highlighted):
        item = event.item
        if isinstance(item, Card):
            self._preview(item)

    def on_list_view_selected(self, event: ListView.Selected):
        item = event.item
        if isinstance(item, Card):
            self._open(item.action_id)

    def action_go_new(self):
        self.app.push_screen(Form())

    def action_go_clone(self):
        self.app.push_screen(CloneP())

    def action_go_local(self):
        self.app.push_screen(LocalP())


class Form(Screen):
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Retour"),
        Binding("ctrl+s", "submit", "Forger"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Nouveau projet", id="brand")
        yield Static("Tab pour circuler. Ctrl+S ou le bouton pour approuver le plan.", classes="panel")
        yield Static("Nom du projet  (dossier cree sous le parent)", classes="field-label")
        yield Input(St.name, id="name")
        yield Static("Dossier parent", classes="field-label")
        yield Input(St.parent, id="parent")
        yield Static(
            "Type   1 Python CLI   2 API FastAPI   3 npm/Vite   4 fullstack   5 systemd",
            classes="field-label",
        )
        yield OptionList(
            Option("1  Python CLI\nOutil, scripts, paquet", id="1"),
            Option("2  API Python\nFastAPI par defaut", id="2"),
            Option("3  npm / Vite\nApp Node, frontend", id="3"),
            Option("4  Fullstack\nBackend Python + frontend npm", id="4"),
            Option("5  Linux system\nScripts et units systemd", id="5"),
            id="kind-list",
        )
        yield Checkbox("Repo prive", St.private, id="priv")
        yield Checkbox("Creer le depot GitHub et pousser le bootstrap", St.create_gh, id="gh")
        yield Checkbox("Installer les outils (venv / npm) pendant la forge", St.tools, id="tools")
        yield Checkbox("Ajouter install.ps1 (Windows)", St.windows, id="win")
        yield Button("Approuver et forger", id="go")
        yield Footer()

    def on_mount(self):
        try:
            kinds = self.query_one("#kind-list", OptionList)
            kinds.highlighted = max(0, int(St.kind) - 1)
        except Exception:
            pass
        try:
            self.query_one("#name", Input).focus()
        except Exception:
            pass

    def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted):
        if event.option_list.id == "kind-list" and event.option_id:
            St.kind = event.option_id

    def on_option_list_option_selected(self, event: OptionList.OptionSelected):
        # Entree sur le type : on retient, on ne lance pas encore la forge.
        if event.option_list.id == "kind-list" and event.option_id:
            St.kind = event.option_id

    def _go(self):
        St.name = self.query_one("#name", Input).value.strip() or St.name
        St.parent = self.query_one("#parent", Input).value.strip() or St.parent
        try:
            k = self.query_one("#kind-list", OptionList)
            if k.highlighted is not None:
                opt = k.get_option_at_index(k.highlighted)
                if opt.id:
                    St.kind = opt.id
        except Exception:
            pass
        St.kind = St.kind if St.kind in KIND_LABELS else "4"
        St.private = self.query_one("#priv", Checkbox).value
        St.create_gh = self.query_one("#gh", Checkbox).value
        St.tools = self.query_one("#tools", Checkbox).value
        St.windows = self.query_one("#win", Checkbox).value
        self.app.push_screen(RunN())

    def on_button_pressed(self, e):
        if e.button.id == "go":
            self._go()

    def action_submit(self):
        self._go()


class RunN(Screen):
    BINDINGS = [Binding("g", "grok", "Grok"), Binding("escape", "menu", "Menu")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Forge  ·  " + St.name, id="brand")
        yield Static(
            f"{KIND_LABELS.get(St.kind, St.kind)}   ·   {Path(St.parent) / St.name}",
            classes="panel",
        )
        yield RichLog(id="log")
        yield Horizontal(Button("Ouvrir Grok", id="g"), Button("Menu", id="m"))
        yield Footer()

    def on_mount(self):
        # async worker (Textual 2+) : _run est une coroutine
        self.run_worker(self._run, exclusive=True)

    def _env(self):
        e = os.environ.copy()
        yn = lambda b: "y" if b else "n"
        e.update(
            FORGE_NI="1",
            FORGE_OVERWRITE="1",
            FORGE_NAME=St.name,
            FORGE_PARENT=St.parent,
            FORGE_KIND=St.kind,
            FORGE_PY_FW="fastapi",
            FORGE_NPM_FW="vite",
            FORGE_WINDOWS=yn(St.windows),
            FORGE_PRIVATE=yn(St.private),
            FORGE_INSTALL_TOOLS=yn(St.tools),
            FORGE_CREATE_GH=yn(St.create_gh),
            FORGE_GH_LOGIN="n",
            FORGE_GROK_INSPECT="n",
            FORGE_OPEN_GROK="n",
        )
        return e

    async def _run(self):
        log = self.query_one("#log", RichLog)
        if not BACKEND.exists():
            log.write("backend manquant")
            return
        log.write("forge de " + St.name + " …")
        try:
            p = await asyncio.create_subprocess_exec(
                "bash",
                str(BACKEND),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                env=self._env(),
            )
        except OSError as err:
            log.write(str(err))
            return
        assert p.stdout is not None
        while True:
            line = await p.stdout.readline()
            if not line:
                break
            log.write(line.decode(errors="replace").rstrip())
        log.write("exit %s" % await p.wait())

    def on_button_pressed(self, e):
        if e.button.id == "g":
            launch(Path(St.parent) / St.name)
        else:
            self.app.switch_screen(Hub())

    def action_grok(self):
        launch(Path(St.parent) / St.name)

    def action_menu(self):
        self.app.switch_screen(Hub())


class CloneP(Screen):
    BINDINGS = [Binding("escape", "app.pop_screen", "Retour")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Cloner un repo GitHub", id="brand")
        yield Static(
            "Tes depots (gh). Entree : clone ou pull vers ~/GrokForge, cadrage si manquant, puis Grok.",
            id="hint",
        )
        rs = gh_repos()
        if not rs:
            yield Static("Aucun repo visible. Connecte GitHub : gh auth login", classes="panel")
        else:
            opts = []
            for r in rs:
                name = r.split("/")[-1]
                opts.append(Option(f"{name}\n{r}", id=r))
            yield OptionList(*opts, id="menu")
        yield Footer()

    def on_mount(self):
        _focus_menu(self)

    def on_option_list_option_selected(self, e):
        St.repo = e.option_id or ""
        if St.repo:
            self.app.push_screen(CloneR())


class CloneR(Screen):
    BINDINGS = [Binding("g", "grok", "Grok"), Binding("escape", "menu", "Menu")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Clone  ·  " + St.repo, id="brand")
        yield RichLog(id="log")
        yield Horizontal(Button("Ouvrir Grok", id="g"), Button("Menu", id="m"))
        yield Footer()

    def on_mount(self):
        self.run_worker(self._run, exclusive=True)

    async def _run(self):
        log = self.query_one("#log", RichLog)
        name = St.repo.split("/")[-1]
        dest = WORK / name
        WORK.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            log.write("deja present — pull si origin a avance")
            p = await asyncio.to_thread(sh, ["git", "pull", "--ff-only"], dest)
        else:
            log.write("clone de " + St.repo)
            p = await asyncio.to_thread(sh, ["gh", "repo", "clone", St.repo, str(dest)])
        out = ((p.stdout or "") + (p.stderr or "")).strip()
        if out:
            log.write(out)
        if dest.exists():
            await asyncio.to_thread(prepare, dest, name, "imported")
            St.local = str(dest)
            log.write("pret  " + str(dest))
        else:
            log.write("echec du clone")

    def on_button_pressed(self, e):
        if e.button.id == "g" and St.local:
            launch(Path(St.local))
        else:
            self.app.switch_screen(Hub())

    def action_grok(self):
        if St.local:
            launch(Path(St.local))

    def action_menu(self):
        self.app.switch_screen(Hub())


class LocalP(Screen):
    BINDINGS = [Binding("escape", "app.pop_screen", "Retour")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Projet local", id="brand")
        yield Static("Dossiers deja dans ~/GrokForge. Entree : cadrage si besoin, puis Grok.", id="hint")
        ps = local_projects()
        if not ps:
            yield Static("Aucun projet pour l'instant. Forge-en un, ou clone un repo.", classes="panel")
        else:
            yield OptionList(
                *[Option(f"{p.name}\n{p}", id=str(p)) for p in ps],
                id="menu",
            )
        yield Footer()

    def on_mount(self):
        _focus_menu(self)

    def on_option_list_option_selected(self, e):
        if e.option_id:
            prepare(Path(e.option_id), name=Path(e.option_id).name, kind="imported")
            launch(Path(e.option_id))


class ForgeApp(App):
    TITLE = "Grok Forge"
    CSS = CSS
    ENABLE_COMMAND_PALETTE = False

    def on_mount(self):
        self.push_screen(Hub())

    def on_unmount(self):
        _mouse_off()


def _run() -> None:
    _mouse_off()
    WORK.mkdir(parents=True, exist_ok=True)
    app = ForgeApp()
    try:
        app.run(mouse=False)
    except TypeError:
        app.run()
    finally:
        _mouse_off()


if __name__ == "__main__":
    _run()
