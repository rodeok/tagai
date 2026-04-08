import os
import json
from groq import Groq
from .tools import TOOLS, execute_tool
from .prompts import SYSTEM_PROMPT
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown

console = Console()

# Global state for session tokens
session_tokens = {"input": 0, "output": 0}
client = None
model = None

def init(api_key, model_id):
    """Initialise Groq client and model."""
    global client, model
    client = Groq(api_key=api_key)
    model = model_id

def run_agent(user_input, history, ask_permission):
    """Process a natural language request through the agent loop."""
    global session_tokens
    
    # Add user message to history
    history.append({"role": "user", "content": user_input})
    
    while True:
        # 1. First Pass - Get response from Groq
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
            tools=TOOLS,
            tool_choice="auto",
            stream=True
        )
        
        full_content = ""
        tool_calls = []
        
        # 2. Live Streaming Output
        with Live(console=console, refresh_per_second=4) as live:
            for chunk in response:
                # Update usage if provided (Groq provides usage in x_groq or usage field)
                usage = getattr(chunk, 'x_groq', None) or getattr(chunk, 'usage', None)
                if usage and getattr(usage, 'usage', None):
                    u = usage.usage
                    session_tokens["input"] += u.prompt_tokens
                    session_tokens["output"] += u.completion_tokens
                elif usage and hasattr(usage, 'prompt_tokens'):
                    u = usage
                    session_tokens["input"] += u.prompt_tokens
                    session_tokens["output"] += u.completion_tokens

                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                
                # Content stream
                if delta.content:
                    full_content += delta.content
                    live.update(Markdown(full_content))
                
                # Tool calls stream (OpenAI format)
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
