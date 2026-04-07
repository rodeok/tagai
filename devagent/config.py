import os
from dotenv import load_dotenv

# Models available on Groq Cloud
GROQ_MODELS = [
    {"id": "openai/gpt-oss-120b", "label": "openai/gpt-oss-120b"},
    {"id": "llama-3.1-8b-instant", "label": "llama-3.1-8b-instant"},
    {"id": "llama-3.3-70b-versatile", "label": "llama-3.3-70b-versatile"},
    {"id": "qwen/qwen3-32b", "label": "qwen/qwen3-32b"}
]

def setup(force_reconfigure: bool = False) -> tuple:
    """Load API key and select model. Prompt user if missing or forced."""
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    model_id = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    if not api_key or force_reconfigure:
        print("\n\033[33m⚙️  Configuration Setup:\033[0m")
        if not api_key:
            api_key = input("\033[36mEnter your GROQ_API_KEY: \033[0m").strip()
            # Update .env
            with open(".env", "a") as f:
                f.write(f"\nGROQ_API_KEY={api_key}\n")
        
        print("\n\033[33mAvailable Groq Models:\033[0m")
        for i, m in enumerate(GROQ_MODELS):
            print(f"  {i+1}. {m['label']} (\033[32m{m['id']}\033[0m)")
        
        try:
            choice = int(input(f"\033[36mSelect model [default 1]: \033[0m") or "1")
            model_id = GROQ_MODELS[choice-1]["id"]
            # Update .env
            with open(".env", "a") as f:
                 f.write(f"GROQ_MODEL={model_id}\n")
        except (ValueError, IndexError):
            model_id = GROQ_MODELS[0]["id"]
            
    return api_key, model_id
