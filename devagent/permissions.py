import sys

def ask_permission(tool_name: str, details: str) -> bool:
    """Prompt user for permission before running a tool. Use ANSI colors."""
    print(f"\n\033[33m🔧 DevAgent wants to use '{tool_name}':\033[0m")
    print(f"   \033[36m{details}\033[0m")
    
    try:
        ans = input("\033[35mAllow? (y/N): \033[0m").lower().strip()
        return ans == "y"
    except (KeyboardInterrupt, EOFError):
        print("\n⛔ Operation cancelled.")
        return False
