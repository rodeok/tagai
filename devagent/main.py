import sys
from . import agent
from .config import setup
from .permissions import ask_permission
from .tools.git_tools import _git   # direct passthrough for raw git commands

BANNER = """
╔══════════════════════════════════════════════════════╗
║  🤖  TagAI · Multi-LLM · Self-Healing · Git         ║
║  Commands:                                           ║
║    exit | tokens | clear | config | help             ║
║    build <file>   — build + auto-heal until clean    ║
║    git <cmd>      — run any git command directly     ║
╚══════════════════════════════════════════════════════╝
"""

HELP = """
Commands:
  exit            quit (shows token summary)
  tokens          session token usage
  clear           reset conversation history
  config          change provider/model/key
  help            this message

  build <file>    agent writes + self-heals the file
                  e.g.  build app.py

  git <cmd>       pass any git command straight through
                  e.g.  git log --oneline
                        git status
                        git push origin main

Natural language also works — just describe what you want:
  "initialise a git repo, add all files and make an initial commit"
  "create a feature/auth branch and switch to it"
  "show me the diff of the last commit"
"""


def main():
    print(BANNER)

    api_key, model_id, base_url = setup()
    agent.init(api_key, model_id, base_url)

    history = []
    print(f"✅ Ready — \033[32m{model_id}\033[0m\n")

    while True:
        try:
            user_input = input("\033[36mYou:\033[0m ").strip()
        except (KeyboardInterrupt, EOFError):
            _token_summary()
            print("\nBye! 👋")
            sys.exit(0)

        if not user_input:
            continue

        parts = user_input.split()
        cmd   = parts[0].lower()

        if cmd == "exit":
            _token_summary(); print("Bye! 👋"); break

        if cmd == "tokens":
            _token_summary(); continue

        if cmd == "clear":
            history = []; print("🗑️  History cleared."); continue

        if cmd == "help":
            print(HELP); continue

        if cmd == "config":
            api_key, model_id, base_url = setup(force_reconfigure=True)
            agent.init(api_key, model_id, base_url)
            history = []
            print(f"✅ Switched to \033[32m{model_id}\033[0m  (history cleared)\n")
            continue

        # ── direct git passthrough ───────────────────────────────────
        if cmd == "git":
            raw_cmd = " ".join(parts[1:])
            if not raw_cmd:
                print("Usage: git <command>  e.g.  git status")
                continue
            r = _git(raw_cmd, cwd=".")
            output = r["stdout"] or r["stderr"]
            color  = "\033[32m" if r["success"] else "\033[31m"
            print(f"{color}{output}\033[0m")
            continue

        # ── build + self-heal ────────────────────────────────────────
        if cmd == "build":
            if len(parts) < 2:
                print("Usage: build <file>  e.g.  build app.py")
                continue
            entry_point = parts[1]
            print(f"\nDescribe what '{entry_point}' should do:")
            try:
                task = input("\033[33mTask:\033[0m ").strip()
            except (KeyboardInterrupt, EOFError):
                continue
            if not task:
                print("No task provided.")
                continue
            history = agent.build_and_heal(
                task=task,
                entry_point=entry_point,
                history=history,
                ask_permission=ask_permission,
                max_heal_iterations=10,
            )
            print(f"\n{'─'*52}")
            _token_summary()
            continue

        # ── normal agent turn (natural language) ─────────────────────
        try:
             agent.run_agent(user_input, history, ask_permission)
        except Exception as e:
             print(f"\033[31mError running agent: {str(e)}\033[0m")
             
        print(f"\n{'─'*52}")
        _token_summary()


def _token_summary():
    t = agent.session_tokens
    print(f"📊 Tokens — in: {t['input']:,}  out: {t['output']:,}  "
          f"total: {t['input'] + t['output']:,}")


if __name__ == "__main__":
    main()
