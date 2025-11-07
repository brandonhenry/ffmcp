from __future__ import annotations

from typing import Any, Dict, List, Optional
import json

from ffmcp.providers import get_provider
from ffmcp.agents.actions import AgentAction, BUILTIN_ACTIONS, ActionContext


class Agent:
    def __init__(
        self,
        *,
        config,
        name: str,
        provider: str,
        model: str,
        instructions: Optional[str] = None,
        brain: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        actions_config: Optional[Dict[str, Any]] = None,
    ):
        self.config = config
        self.name = name
        self.provider_name = provider
        self.model = model
        self.instructions = instructions or ''
        self.brain = brain
        self.properties = dict(properties or {})
        self._actions: Dict[str, AgentAction] = {}
        self._provider = get_provider(provider, config)
        self._load_actions(actions_config or {})

    # ---------------- Actions ----------------
    def _load_actions(self, actions_config: Dict[str, Any]):
        for action_name, cfg in actions_config.items():
            cls = BUILTIN_ACTIONS.get(action_name)
            if not cls:
                continue
            if isinstance(cfg, dict):
                # Pass through simple kwargs for constructor if accepted
                try:
                    action = cls(**cfg)
                except TypeError:
                    action = cls()
            else:
                action = cls()
            self._actions[action_name] = action

    def register_action(self, name: str, action: AgentAction):
        self._actions[name] = action

    def unregister_action(self, name: str):
        if name in self._actions:
            del self._actions[name]

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        return [act.as_tool_definition() for act in self._actions.values()]

    # ---------------- Run ----------------
    def run(self, *, input_text: str, images: Optional[List[str]] = None, extra_messages: Optional[List[Dict[str, Any]]] = None) -> str:
        # Build messages
        messages: List[Dict[str, Any]] = []
        # Optional memory context from brain
        if self.brain:
            try:
                from ffmcp.brain import ZepBrainClient, BrainInfo
                zcfg = self.config.get_zep_settings()
                client = ZepBrainClient(api_key=zcfg.get('api_key'), base_url=zcfg.get('base_url'), env=zcfg.get('env'))
                brain_info = BrainInfo(name=self.brain)
                mem = client.memory_get(brain=brain_info, session_id=None)
                mem_text = json.dumps(mem.get('result'), default=str)
                if len(mem_text) > 50000:
                    mem_text = mem_text[:50000]
                messages.append({"role": "system", "content": f"Memory context (read-only): {mem_text}"})
            except Exception:
                # If memory unavailable, continue without failing
                pass
        if self.instructions:
            messages.append({"role": "system", "content": self.instructions})

        # Optional: include image content upfront if provided
        if images:
            # If provider supports direct vision with file paths, use a one-shot call and return
            vision_fn = getattr(self._provider, 'vision', None)
            if vision_fn:
                return vision_fn(input_text, images, model=self.model)

        messages.append({"role": "user", "content": input_text})
        if extra_messages:
            messages.extend(extra_messages)

        tools = self.get_tool_definitions() if self._actions else None
        # If there are tools and provider is OpenAI, run tool-calling loop
        if tools and getattr(self._provider, 'chat_with_tools', None):
            return self._run_with_tools(messages, tools)

        # Fallback: plain chat
        return self._provider.chat(messages, model=self.model)

    def _run_with_tools(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]], *, max_rounds: int = 5) -> str:
        rounds = 0
        content_final: Optional[str] = None
        while rounds < max_rounds:
            rounds += 1
            result = self._provider.chat_with_tools(messages, tools, model=self.model)
            content_final = result.get('content')
            tool_calls = result.get('tool_calls') or []
            if not tool_calls:
                break

            # Append assistant tool calls message so the model sees its own calls
            assistant_msg = {
                "role": "assistant",
                "content": content_final or None,
                "tool_calls": [
                    {
                        "id": tc["id"],
                        "type": tc.get("type") or "function",
                        "function": {
                            "name": tc["function"]["name"],
                            "arguments": json.dumps(tc["function"]["arguments"], ensure_ascii=False),
                        },
                    }
                    for tc in tool_calls
                ],
            }
            messages.append(assistant_msg)

            # Execute tools
            for tc in tool_calls:
                func_name = tc['function']['name']
                args = tc['function'].get('arguments') or {}
                action = self._actions.get(func_name)
                if not action:
                    tool_content = json.dumps({"error": f"unknown action: {func_name}"})
                else:
                    ctx = ActionContext(config=self.config, provider=self._provider, agent_name=self.name, brain_name=self.brain)
                    try:
                        result_obj = action.call(args, ctx)
                        tool_content = json.dumps(result_obj, ensure_ascii=False)
                    except Exception as e:
                        tool_content = json.dumps({"error": str(e)})

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc['id'],
                        "name": func_name,
                        "content": tool_content,
                    }
                )

            # Continue loop; model will see tool results
        return content_final or ""


