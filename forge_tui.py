#!/usr/bin/env python3
from __future__ import annotations
import os, shutil, subprocess, sys
from pathlib import Path
try:
    from textual.app import App, ComposeResult
    from textual.binding import Binding
    from textual.containers import Horizontal
    from textual.screen import Screen
    from textual.widgets import Button, Checkbox, Footer, Header, Input, Label, OptionList, RichLog, Static
    from textual.widgets.option_list import Option
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "textual"])
    from textual.app import App, ComposeResult
    from textual.binding import Binding
    from textual.containers import Horizontal
    from textual.screen import Screen
    from textual.widgets import Button, Checkbox, Footer, Header, Input, Label, OptionList, RichLog, Static
    from textual.widgets.option_list import Option
HERE = Path(__file__).resolve().parent
BACKEND = HERE / "setup-grok-forge.sh"
WORK = Path.home() / "GrokForge"
CSS = "Screen{background:#141414;color:#e1e1e1;} Header{background:#0c0c0c;color:#bb9af7;} Footer{background:#0c0c0c;color:#6c6c6c;} #brand{color:#bb9af7;text-style:bold;padding:1 2;} .panel{border:tall #242424;background:#111111;margin:0 2 1 2;padding:1 2;} OptionList{height:12;margin:0 2 1 2;} #log{height:1fr;margin:0 2 1 2;background:#0a0a0a;}"
def sh(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
def which(n):
    return shutil.which(n) is not None
def gh_repos():
    if not which("gh"):
        return []
    p = sh(["gh","repo","list","--limit","80","--json","nameWithOwner","--jq",".[].nameWithOwner"])
    return [x.strip() for x in p.stdout.splitlines() if x.strip()] if p.returncode==0 else []
def local_projects():
    WORK.mkdir(parents=True, exist_ok=True)
    return [c for c in sorted(WORK.iterdir()) if c.is_dir() and ((c/".git").exists() or (c/"AGENTS.md").exists())]
AGENTS="""# AGENTS.md\n## Git\n- Branche grok/<sujet> hors main.\n- Pas de force-push sur main. Pas de secrets.\n- git push -u origin HEAD\n"""
WRAP="""#!/usr/bin/env bash\nset -euo pipefail\ncd \"$(dirname \"$0\")/../..\"\nT=\"${1:-session}\"; S=\"$(date +%Y-%m-%d-%H%M)\"\nmkdir -p docs/reports\nB=\"$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo main)\"\nif [[ \"$B\" == main || \"$B\" == master ]]; then B=\"grok/$S\"; git checkout -b \"$B\"; fi\necho \"# $T\" > docs/reports/$S.md\ngit add -A\ngit diff --cached --quiet || git commit -m \"docs: $S $T\"\ngit remote get-url origin >/dev/null 2>&1 && git push -u origin HEAD || true\n"""
def prepare(root: Path):
    root.mkdir(parents=True, exist_ok=True)
    if not (root/"AGENTS.md").exists():
        (root/"AGENTS.md").write_text(AGENTS.replace("\\n","\n"))
    h=root/".grok"/"hooks"; h.mkdir(parents=True, exist_ok=True)
    w=h/"session-wrap.sh"
    if not w.exists():
        w.write_text(WRAP.replace("\\n","\n")); w.chmod(0o755)
    (root/"docs"/"reports").mkdir(parents=True, exist_ok=True)
def launch(root: Path):
    g=shutil.which("grok")
    if not g: return
    os.chdir(root); os.execvp(g,[g])
class St:
    name="High-Fortress"; parent=str(WORK); kind="4"
    windows=False; private=True; tools=True; create_gh=True
    repo=""; local=""
class Hub(Screen):
    BINDINGS=[Binding("q","app.quit","Quitter")]
    def compose(self):
        yield Header(show_clock=True)
        yield Label("Grok Forge", id="brand")
        g="Grok OK" if which("grok") else "Grok absent"
        h="gh OK" if which("gh") else "gh absent"
        yield Static(f"{g} | {h} | {WORK}", classes="panel")
        yield OptionList(Option("Forger un nouveau projet",id="new"), Option("Cloner un repo GitHub et ouvrir Grok",id="clone"), Option("Ouvrir un projet local",id="local"), Option("Quitter",id="quit"), id="menu")
        yield Footer()
    def on_option_list_option_selected(self, e):
        i=e.option_id
        if i=="new": self.app.push_screen(Form())
        elif i=="clone": self.app.push_screen(CloneP())
        elif i=="local": self.app.push_screen(LocalP())
        else: self.app.exit()
class Form(Screen):
    BINDINGS=[Binding("escape","app.pop_screen","Retour")]
    def compose(self):
        yield Header(); yield Label("Nouveau projet", id="brand")
        yield Static("Remplis puis Approuver", classes="panel")
        yield Input(St.name, id="name")
        yield Input(St.parent, id="parent")
        yield Input(St.kind, id="kind")
        yield Checkbox("Repo prive", St.private, id="priv")
        yield Checkbox("Creer GitHub + push", St.create_gh, id="gh")
        yield Checkbox("Installer outils", St.tools, id="tools")
        yield Checkbox("install.ps1", St.windows, id="win")
        yield Button("Approuver et forger", id="go"); yield Footer()
    def on_button_pressed(self, e):
        St.name=self.query_one("#name", Input).value.strip() or St.name
        St.parent=self.query_one("#parent", Input).value.strip() or St.parent
        St.kind=self.query_one("#kind", Input).value.strip() or "4"
        St.private=self.query_one("#priv", Checkbox).value
        St.create_gh=self.query_one("#gh", Checkbox).value
        St.tools=self.query_one("#tools", Checkbox).value
        St.windows=self.query_one("#win", Checkbox).value
        self.app.push_screen(RunN())
class RunN(Screen):
    BINDINGS=[Binding("g","grok","Grok")]
    def compose(self):
        yield Header(); yield Label("Forge", id="brand")
        yield RichLog(id="log"); yield Horizontal(Button("Ouvrir Grok", id="g"), Button("Menu", id="m")); yield Footer()
    def on_mount(self):
        self.run_worker(self._run, exclusive=True)
    def _env(self):
        e=os.environ.copy(); yn=lambda b: "y" if b else "n"
        e.update(FORGE_NI="1", FORGE_OVERWRITE="1", FORGE_NAME=St.name, FORGE_PARENT=St.parent, FORGE_KIND=St.kind, FORGE_PY_FW="fastapi", FORGE_NPM_FW="vite", FORGE_WINDOWS=yn(St.windows), FORGE_PRIVATE=yn(St.private), FORGE_INSTALL_TOOLS=yn(St.tools), FORGE_CREATE_GH=yn(St.create_gh), FORGE_GH_LOGIN="n", FORGE_GROK_INSPECT="n", FORGE_OPEN_GROK="n")
        return e
    def _run(self):
        log=self.query_one("#log", RichLog)
        if not BACKEND.exists():
            log.write("backend manquant"); return
        p=subprocess.Popen(["bash", str(BACKEND)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=self._env())
        for line in p.stdout: log.write(line.rstrip())
        log.write("exit %s"%p.wait())
    def on_button_pressed(self, e):
        if e.button.id=="g": launch(Path(St.parent)/St.name)
        else: self.app.switch_screen(Hub())
    def action_grok(self):
        launch(Path(St.parent)/St.name)
class CloneP(Screen):
    BINDINGS=[Binding("escape","app.pop_screen","Retour")]
    def compose(self):
        yield Header(); yield Label("Repos GitHub", id="brand")
        rs=gh_repos()
        if not rs: yield Static("Aucun repo. Connecte gh.", classes="panel")
        else: yield OptionList(*[Option(r,id=r) for r in rs], id="r")
        yield Footer()
    def on_option_list_option_selected(self, e):
        St.repo=e.option_id or ""
        if St.repo: self.app.push_screen(CloneR())
class CloneR(Screen):
    def compose(self):
        yield Header(); yield Label("Clone "+St.repo, id="brand")
        yield RichLog(id="log"); yield Horizontal(Button("Ouvrir Grok", id="g"), Button("Menu", id="m")); yield Footer()
    def on_mount(self):
        self.run_worker(self._run, exclusive=True)
    def _run(self):
        log=self.query_one("#log", RichLog)
        name=St.repo.split("/")[-1]; dest=WORK/name; WORK.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            log.write("present"); p=sh(["git","pull","--ff-only"], cwd=dest)
        else:
            p=sh(["gh","repo","clone", St.repo, str(dest)])
        log.write((p.stdout or "")+(p.stderr or ""))
        if dest.exists():
            prepare(dest); St.local=str(dest); log.write("ok "+str(dest))
    def on_button_pressed(self, e):
        if e.button.id=="g" and St.local: launch(Path(St.local))
        else: self.app.switch_screen(Hub())
class LocalP(Screen):
    BINDINGS=[Binding("escape","app.pop_screen","Retour")]
    def compose(self):
        yield Header(); yield Label("Local", id="brand")
        ps=local_projects()
        if not ps: yield Static("Vide", classes="panel")
        else: yield OptionList(*[Option(str(p),id=str(p)) for p in ps])
        yield Footer()
    def on_option_list_option_selected(self, e):
        if e.option_id:
            prepare(Path(e.option_id)); launch(Path(e.option_id))
class ForgeApp(App):
    TITLE="Grok Forge"; CSS=CSS
    def on_mount(self):
        self.push_screen(Hub())
if __name__=="__main__":
    WORK.mkdir(parents=True, exist_ok=True)
    ForgeApp().run()
