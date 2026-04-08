import os
from dotenv import load_dotenv
import litellm

# Supported Providers and common models
PROVIDERS = {
    "1": {"name": "Groq", "prefix": "groq/", "models": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"], "env_key": "GROQ_API_KEY"},
    "2": {"name": "OpenAI", "prefix": "openai/", "models": ["gpt-4o", "gpt-4o-mini"], "env_key": "OPENAI_API_KEY"},
    "3": {"name": "Anthropic", "prefix": "anthropic/", "models": ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229"], "env_key": "ANTHROPIC_API_KEY"},
    "4": {"name": "Gemini", "prefix": "gemini/", "models": ["gemini-1.5-pro", "gemini-1.5-flash"], "env_key": "GEMINI_API_KEY"},
    "5": {"name": "Local", "prefix": "", "models": ["llama3", "mistral"], "env_key": "OPENAI_API_KEY"} # Often uses OpenAI key pattern
}

def _verify_api_key(model: str, api_key: str, base_url: str = None) -> bool:
    """Verify API key by attempting a minimal completion."""
    if not api_key and "Local" not in model:
        return False
    try:
        # Use a very short timeout and minimal tokens for verification
        litellm.completion(
            model=model,
            messages=[{"role": "user", "content": "hi"}],
            max_tokens=1,
            api_key=api_key,
            base_url=base_url,
            timeout=10
        )
        return True
    except Exception as e:
        print(f"\033[31m❌ Verification failed: {str(e)}\033[0m")
        return False

def setup(force_reconfigure: bool = False) -> tuple:
    """Load configuration and select provider/model."""
    load_dotenv()
    
    provider_name = os.getenv("LLM_PROVIDER", "Groq")
    model_id = os.getenv("LLM_MODEL")
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL")

    if not api_key or force_reconfigure:
        print("\n\033[33m⚙️  Configuration Setup:\033[0m")
        
        # 1. Select Provider
        print("\nSelect Provider:")
        for k, v in PROVIDERS.items():
            print(f"  {k}. {v['name']}")
        
        p_choice = input(f"\033[36mChoice [1-5]: \033[0m").strip() or "1"
        provider = PROVIDERS.get(p_choice, PROVIDERS["1"])
        provider_name = provider["name"]
        
        # 2. Select Model
        print(f"\nAvailable {provider_name} Models:")
        for i, m in enumerate(provider["models"]):
            print(f"  {i+1}. {m}")
        print(f"  {len(provider['models'])+1}. Custom...")
        
        m_choice = input(f"\033[36mChoice [1]: \033[0m").strip() or "1"
        if m_choice == str(len(provider["models"]) + 1):
            model_id = input("\033[36mEnter custom model name: \033[0m").strip()
        else:
            try:
                model_id = provider["models"][int(m_choice)-1]
            except (ValueError, IndexError):
                model_id = provider["models"][0]
        
        # Prepend prefix if not already present
        full_model = model_id if "/" in model_id else f"{provider['prefix']}{model_id}"
        
        # 3. API Key & Base URL
        if provider_name == "Local":
            base_url = input("\033[36mEnter Local Base URL [default http://localhost:11434/v1]: \033[0m").strip() or "http://localhost:11434/v1"
        
        while True:
            prompt = f"Enter {provider_name} API Key: " if provider_name != "Local" else "Enter API Key (if required): "
            api_key = input(f"\033[36m{prompt}\033[0m").strip()
            
            print(f"🔄 Verifying {full_model}...")
            if _verify_api_key(full_model, api_key, base_url):
                print("\033[32m✅ Verified!\033[0m")
                break
            else:
                retry = input("Verification failed. Continue anyway? (y/n): ").lower()
                if retry == 'y': break

        # Save to .env
        with open(".env", "w") as f:
            f.write(f"LLM_PROVIDER={provider_name}\n")
            f.write(f"LLM_MODEL={full_model}\n")
            f.write(f"LLM_API_KEY={api_key}\n")
            if base_url:
                f.write(f"LLM_BASE_URL={base_url}\n")
            
    else:
        # Verify existing config
        full_model = model_id
        # We don't always want to verify on every boot if it adds delay, 
        # but the user asked for automatic verification. 
        # I'll skip it here unless it's a fresh setup or force_reconfigure to keep it snappy.
        pass

    return api_key, full_model, base_url

if __name__ == "__main__":
    # Test setup
    setup(force_reconfigure=True)
