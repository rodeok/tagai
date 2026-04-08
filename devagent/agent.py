import os
import json
import litellm
from .tools import TOOLS, execute_tool
from .prompts import SYSTEM_PROMPT
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown

console = Console()

# Global state
session_tokens = {"input": 0, "output": 0}
config = {
    "api_key": None,
    "model": None,
    "base_url": None
}

def init(api_key, model, base_url=None):
    """Initialise LLM config."""
    global config
    config["api_key"] = api_key
    config["model"] = model
    config["base_url"] = base_url
    
    # Optional: silence litellm logging if too verbose
    litellm.set_verbose = False

def run_agent(user_input, history, ask_permission):
    """Process a natural language request through the agent loop."""
    global session_tokens
    
    # Add user message to history
    history.append({"role": "user", "content": user_input})
    
    while True:
        # 1. Get response from LLM via LiteLLM
        response = litellm.completion(
            model=config["model"],
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
            tools=TOOLS,
            tool_choice="auto",
            stream=True,
            api_key=config["api_key"],
            base_url=config["base_url"]
        )
        
        full_content = ""
        tool_calls = []
        
        # 2. Live Streaming Output
        with Live(console=console, refresh_per_second=4) as live:
            for chunk in response:
                # Update usage if provided
                usage = getattr(chunk, 'usage', None)
                if usage:
                    session_tokens["input"] += getattr(usage, 'prompt_tokens', 0)
                    session_tokens["output"] += getattr(usage, 'completion_tokens', 0)

                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                
                # Content stream
                if delta.content:
                    full_content += delta.content
                    live.update(Markdown(full_content))
                
                # Tool calls stream
                if delta.tool_calls:
                    for tc_delta in delta.tool_calls:
                        if len(tool_calls) <= tc_delta.index:
                            tool_calls.append({"id": "", "type": "function", "function": {"name": "", "arguments": ""}})
                        
                        tc = tool_calls[tc_delta.index]
                        if tc_delta.id: tc["id"] += tc_delta.id
                        if tc_delta.function.name: tc["function"]["name"] += tc_delta.function.name
                        if tc_delta.function.arguments: tc["function"]["arguments"] += tc_delta.function.arguments

        # 3. Handle Completion
        if full_content:
             history.append({"role": "assistant", "content": full_content})
        
        # 4. Handle Tool Calls
        if tool_calls:
            # Need to add assistant message with tool calls to history
            history.append({
                "role": "assistant",
                "content": full_content or None,
                "tool_calls": tool_calls
            })
            
            for tc in tool_calls:
                name = tc["function"]["name"]
                try:
                    args = json.loads(tc["function"]["arguments"])
                except json.JSONDecodeError:
                    args = {}
                
                # Execute tool
                result = execute_tool(name, args, ask_permission)
                
                # Feed result back
                history.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "name": name,
                    "content": str(result)
                })
            
            # Continue the loop for the next assistant turn
            continue
        
        # No more tool calls, exit loop
        break

def build_and_heal(task, entry_point, history, ask_permission, max_heal_iterations=10):
    """Iteratively build and fix a file until it runs without errors or max iterations reached."""
    from .self_heal import check_for_errors
    
    # Initial instruction
    prompt = f"Building '{entry_point}':\n{task}\n\nPlan the code and then write it to the file using write_file tool."
    run_agent(prompt, history, ask_permission)
    
    for i in range(max_heal_iterations):
        console.print(f"\n\033[33m🩺 Self-Healing Iteration {i+1} of {max_heal_iterations}...\033[0m")
        
        # Check for errors in the entry point
        has_error, error_msg = check_for_errors(entry_point)
        
        if not has_error:
            console.print("\033[32m🛡️  No errors detected. Build successful.\033[0m")
            break
        
        console.print(f"\033[31m💥 Error detected:\033[0m\n{error_msg}")
        
        # Ask agent to fix the error
        fix_prompt = f"I detected an error when running '{entry_point}':\n\n{error_msg}\n\nPlease analyze and fix this error. Use write_file to update the code."
        run_agent(fix_prompt, history, ask_permission)
    
    return history
