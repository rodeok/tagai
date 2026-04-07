import os, subprocess, json
from .git_tools import GIT_TOOLS, execute_git_tool

def load_ignore_patterns(path=".agentignore") -> list[str]:
    defaults = ["node_modules", ".git", "__pycache__", ".env",
                "dist", "build", ".next", "venv"]
    if not os.path.exists(path):
        return defaults
    with open(path) as f:
        lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]
    return defaults + lines

IGNORE_PATTERNS = load_ignore_patterns()

def is_ignored(path: str) -> bool:
    parts = path.replace("\\", "/").split("/")
    return any(pat in parts for pat in IGNORE_PATTERNS)

# ── filesystem tool schemas ───────────────────────────────────────────
FS_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file (creates or overwrites)",
            "parameters": {
                "type": "object",
                "properties": {
                    "path":    {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "bash",
            "description": "Run a shell command",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string"}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "List directory contents, respecting .agentignore",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "default": "."}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_files",
            "description": "Search for a pattern in files using grep",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern":   {"type": "string"},
                    "path":      {"type": "string", "default": "."},
                    "file_glob": {"type": "string", "default": "*"}
                },
                "required": ["pattern"]
            }
        }
    },
]

# Combine both tool lists — agent sees everything
TOOLS = FS_TOOLS + GIT_TOOLS


def execute_tool(name: str, args: dict, ask_permission) -> str:
    # Route git tools
    if name.startswith("git_"):
        return execute_git_tool(name, args, ask_permission)

    # Filesystem tools
    try:
        if name == "read_file":
            path = args["path"]
            if not os.path.exists(path):
                 return f"❌ File not found: {path}"
            with open(path, encoding="utf-8", errors="replace") as f:
                return f.read()

        elif name == "write_file":
            path, content = args["path"], args["content"]
            if not ask_permission("write_file", f"Write to '{path}'?"):
                return "⛔ Skipped by user."
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"✅ Written to {path}"

        elif name == "bash":
            cmd = args["command"]
            if not ask_permission("bash", f"Run: `{cmd}`?"):
                return "⛔ Skipped by user."
            # Set shell to True for multiple commands or piping
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            return (r.stdout + r.stderr)[:4000] or "(no output)"

        elif name == "list_dir":
            p = args.get("path", ".")
            if not os.path.exists(p):
                 return f"❌ Directory not found: {p}"
            entries = [e for e in os.listdir(p) if not is_ignored(os.path.join(p, e))]
            return "\n".join(sorted(entries)) or "(empty)"

        elif name == "search_files":
            pattern   = args["pattern"]
            spath     = args.get("path", ".")
            file_glob = args.get("file_glob", "*")
            
            # Using grep if available, otherwise fallback (for Windows compatibility we might want a pure python fallback but user specifically asked for grep)
            # On windows, grep might not be available, but we'll try it.
            excl = " ".join(f"--exclude-dir='{p}'" for p in IGNORE_PATTERNS)
            cmd  = f'grep -rn --include="{file_glob}" {excl} "{pattern}" "{spath}"'
            
            try:
                r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
                return r.stdout.strip()[:3000] or f"No matches for '{pattern}'"
            except FileNotFoundError:
                return "❌ 'grep' command not found. Please ensure it's in your PATH."

    except Exception as e:
        return f"❌ {name} error: {str(e)}"
