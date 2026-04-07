import subprocess
import os

# ── helper ──────────────────────────────────────────────────────────
def _git(cmd: str, cwd: str = ".") -> dict:
    result = subprocess.run(
        f"git {cmd}", shell=True, cwd=cwd,
        capture_output=True, text=True
    )
    return {
        "success": result.returncode == 0,
        "stdout":  result.stdout.strip(),
        "stderr":  result.stderr.strip(),
        "code":    result.returncode,
    }

def _out(r: dict) -> str:
    if r["success"]:
        return r["stdout"] or "✅ Done"
    return f"❌ {r['stderr'] or r['stdout']}"


# ── tool schemas ─────────────────────────────────────────────────────
GIT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "git_init",
            "description": "Initialise a new git repo in a directory",
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
            "name": "git_status",
            "description": "Show working tree status",
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
            "name": "git_add",
            "description": "Stage files. Use '.' to stage everything.",
            "parameters": {
                "type": "object",
                "properties": {
                    "files": {"type": "string", "description": "Files to stage, e.g. '.' or 'src/main.py'"},
                    "path":  {"type": "string", "default": "."}
                },
                "required": ["files"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_commit",
            "description": "Commit staged changes with a message",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "path":    {"type": "string", "default": "."}
                },
                "required": ["message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_log",
            "description": "Show recent commit history",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 10},
                    "path":  {"type": "string", "default": "."}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_diff",
            "description": "Show unstaged or staged diffs",
            "parameters": {
                "type": "object",
                "properties": {
                    "staged": {"type": "boolean", "default": False, "description": "If true, show staged diff"},
                    "file":   {"type": "string", "description": "Specific file to diff (optional)"},
                    "path":   {"type": "string", "default": "."}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_branch",
            "description": "List, create, or delete branches",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["list", "create", "delete", "current"],
                        "default": "list"
                    },
                    "name": {"type": "string", "description": "Branch name (for create/delete)"},
                    "path": {"type": "string", "default": "."}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_checkout",
            "description": "Switch to a branch or create and switch",
            "parameters": {
                "type": "object",
                "properties": {
                    "branch":    {"type": "string"},
                    "create_if_missing": {"type": "boolean", "default": False},
                    "path":      {"type": "string", "default": "."}
                },
                "required": ["branch"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_merge",
            "description": "Merge a branch into the current branch",
            "parameters": {
                "type": "object",
                "properties": {
                    "branch": {"type": "string"},
                    "path":   {"type": "string", "default": "."}
                },
                "required": ["branch"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_stash",
            "description": "Stash or pop uncommitted changes",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["push", "pop", "list", "drop"],
                        "default": "push"
                    },
                    "message": {"type": "string", "description": "Stash message (for push)"},
                    "path":    {"type": "string", "default": "."}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_reset",
            "description": "Reset HEAD to a previous commit or unstage files",
            "parameters": {
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "enum": ["soft", "mixed", "hard"],
                        "default": "mixed"
                    },
                    "target": {"type": "string", "default": "HEAD~1",
                               "description": "Commit hash or HEAD~N"},
                    "path":   {"type": "string", "default": "."}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_remote",
            "description": "List, add or remove remotes",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["list", "add", "remove"],
                        "default": "list"
                    },
                    "name": {"type": "string", "description": "Remote name e.g. origin"},
                    "url":  {"type": "string", "description": "Remote URL"},
                    "path": {"type": "string", "default": "."}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_push",
            "description": "Push commits to a remote",
            "parameters": {
                "type": "object",
                "properties": {
                    "remote":     {"type": "string", "default": "origin"},
                    "branch":     {"type": "string", "default": ""},
                    "force":      {"type": "boolean", "default": False},
                    "set_upstream": {"type": "boolean", "default": False},
                    "path":       {"type": "string", "default": "."}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_pull",
            "description": "Pull latest changes from a remote",
            "parameters": {
                "type": "object",
                "properties": {
                    "remote": {"type": "string", "default": "origin"},
                    "branch": {"type": "string", "default": ""},
                    "path":   {"type": "string", "default": "."}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_clone",
            "description": "Clone a remote repository",
            "parameters": {
                "type": "object",
                "properties": {
                    "url":       {"type": "string"},
                    "dest":      {"type": "string", "description": "Local folder name (optional)"},
                    "depth":     {"type": "integer", "description": "Shallow clone depth (optional)"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_tag",
            "description": "List, create, or delete tags",
            "parameters": {
                "type": "object",
                "properties": {
                    "action":  {"type": "string", "enum": ["list", "create", "delete"], "default": "list"},
                    "name":    {"type": "string"},
                    "message": {"type": "string", "description": "Annotated tag message"},
                    "path":    {"type": "string", "default": "."}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_show",
            "description": "Show details of a specific commit",
            "parameters": {
                "type": "object",
                "properties": {
                    "ref":  {"type": "string", "default": "HEAD"},
                    "path": {"type": "string", "default": "."}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_blame",
            "description": "Show who last modified each line of a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string"},
                    "path": {"type": "string", "default": "."}
                },
                "required": ["file"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_config",
            "description": "Get or set git config values (user.name, user.email, etc.)",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["get", "set"], "default": "get"},
                    "key":    {"type": "string", "description": "e.g. user.name"},
                    "value":  {"type": "string", "description": "Value to set"},
                    "global": {"type": "boolean", "default": False}
                },
                "required": ["key"]
            }
        }
    },
]


# ── executor ─────────────────────────────────────────────────────────
def execute_git_tool(name: str, args: dict, ask_permission) -> str:
    path = args.get("path", ".")

    # Destructive ops need permission
    DESTRUCTIVE = {"git_reset", "git_push", "git_merge", "git_clone"}
    if name in DESTRUCTIVE:
        if not ask_permission(name, f"{name} with args {args}"):
            return "⛔ Skipped by user."

    if name == "git_init":
        return _out(_git(f"init {path}"))

    elif name == "git_status":
        return _out(_git("status", cwd=path))

    elif name == "git_add":
        return _out(_git(f"add {args['files']}", cwd=path))

    elif name == "git_commit":
        msg = args["message"].replace('"', '\\"')
        return _out(_git(f'commit -m "{msg}"', cwd=path))

    elif name == "git_log":
        limit = args.get("limit", 10)
        r = _git(f"log --oneline --decorate --graph -n {limit}", cwd=path)
        return _out(r)

    elif name == "git_diff":
        staged = args.get("staged", False)
        file_  = args.get("file", "")
        flag   = "--cached" if staged else ""
        return _out(_git(f"diff {flag} {file_}".strip(), cwd=path))

    elif name == "git_branch":
        action = args.get("action", "list")
        bname  = args.get("name", "")
        if action == "list":
            return _out(_git("branch -a", cwd=path))
        elif action == "create":
            return _out(_git(f"branch {bname}", cwd=path))
        elif action == "delete":
            return _out(_git(f"branch -d {bname}", cwd=path))
        elif action == "current":
            return _out(_git("rev-parse --abbrev-ref HEAD", cwd=path))

    elif name == "git_checkout":
        branch = args["branch"]
        create = args.get("create_if_missing", False)
        flag   = "-B" if create else ""
        return _out(_git(f"checkout {flag} {branch}".strip(), cwd=path))

    elif name == "git_merge":
        return _out(_git(f"merge {args['branch']}", cwd=path))

    elif name == "git_stash":
        action  = args.get("action", "push")
        message = args.get("message", "")
        if action == "push":
            flag = f'-m "{message}"' if message else ""
            return _out(_git(f"stash push {flag}".strip(), cwd=path))
        elif action == "pop":
            return _out(_git("stash pop", cwd=path))
        elif action == "list":
            return _out(_git("stash list", cwd=path))
        elif action == "drop":
            return _out(_git("stash drop", cwd=path))

    elif name == "git_reset":
        mode   = args.get("mode", "mixed")
        target = args.get("target", "HEAD~1")
        return _out(_git(f"reset --{mode} {target}", cwd=path))

    elif name == "git_remote":
        action = args.get("action", "list")
        rname  = args.get("name", "")
        url    = args.get("url", "")
        if action == "list":
            return _out(_git("remote -v", cwd=path))
        elif action == "add":
            return _out(_git(f"remote add {rname} {url}", cwd=path))
        elif action == "remove":
            return _out(_git(f"remote remove {rname}", cwd=path))

    elif name == "git_push":
        remote = args.get("remote", "origin")
        branch = args.get("branch", "")
        force  = "--force" if args.get("force") else ""
        ups    = "-u" if args.get("set_upstream") else ""
        return _out(_git(f"push {ups} {force} {remote} {branch}".strip(), cwd=path))

    elif name == "git_pull":
        remote = args.get("remote", "origin")
        branch = args.get("branch", "")
        return _out(_git(f"pull {remote} {branch}".strip(), cwd=path))

    elif name == "git_clone":
        url   = args["url"]
        dest  = args.get("dest", "")
        depth = f"--depth {args['depth']}" if args.get("depth") else ""
        return _out(_git(f"clone {depth} {url} {dest}".strip(), cwd="."))

    elif name == "git_tag":
        action = args.get("action", "list")
        tname  = args.get("name", "")
        msg    = args.get("message", "")
        if action == "list":
            return _out(_git("tag --list", cwd=path))
        elif action == "create":
            flag = f'-a {tname} -m "{msg}"' if msg else tname
            return _out(_git(f"tag {flag}", cwd=path))
        elif action == "delete":
            return _out(_git(f"tag -d {tname}", cwd=path))

    elif name == "git_show":
        ref = args.get("ref", "HEAD")
        return _out(_git(f"show --stat {ref}", cwd=path))

    elif name == "git_blame":
        return _out(_git(f"blame {args['file']}", cwd=path))

    elif name == "git_config":
        action = args.get("action", "get")
        key    = args["key"]
        value  = args.get("value", "")
        scope  = "--global" if args.get("global") else ""
        if action == "get":
            return _out(_git(f"config {scope} {key}".strip(), cwd=path))
        elif action == "set":
            return _out(_git(f'config {scope} {key} "{value}"'.strip(), cwd=path))

    return f"❌ Unknown git tool: {name}"
