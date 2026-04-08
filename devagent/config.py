import os
from dotenv import load_dotenv
from groq import Groq

# Models available on Groq Cloud
GROQ_MODELS = [
    {"id": "openai/gpt-oss-120b", "label": "openai/gpt-oss-120b"},
    {"id": "llama-3.1-8b-instant", "label": "llama-3.1-8b-instant"},
    {"id": "llama-3.3-70b-versatile", "label": "llama-3.3-70b-versatile"},
    {"id": "qwen/qwen3-32b", "label": "qwen/qwen3-32b"}
]

def _verify_api_key(api_key: str) -> bool:
    """Verify if the Groq API key is valid by attempting to list models."""
    if not api_key:
        return False
    try:
        client = Groq(api_key=api_key)
        client.models.list()
        return True
    except Exception:
        return False

def setup(force_reconfigure: bool = False) -> tuple:
    """Load API key and select model. Prompt user if missing or forced."""
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    model_id = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    # Verify existing key if not forcing reconfigure
    if api_key and not force_reconfigure:
        if not _verify_api_key(api_key):
             print("\033[33m⚠️  Stored API key is invalid. Forcing reconfiguration...\033[0m")
             force_reconfigure = True

    if not api_key or force_reconfigure:
        print("\n\033[33m⚙️  Configuration Setup:\033[0m")
        
        # Loop until a valid key is provided
        while True:
            api_key = input("\033[36mEnter your GROQ_API_KEY: \033[0m").strip()
            if _verify_api_key(api_key):
                with open(".env", "a") as f:
                    f.write(f"\nGROQ_API_KEY={api_key}\n")
                print("\033[32m✅ API Key verified.\033[0m")
                break
            else:
                print("\033[31m❌ Key verification failed. Please check your key and try again.\033[0m")
        
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
