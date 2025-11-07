from __future__ import annotations

from typing import Any, Dict, Optional, List, Tuple
import json


class ActionContext:
    def __init__(self, *, config, provider, agent_name: str, brain_name: Optional[str]):
        self.config = config
        self.provider = provider
        self.agent_name = agent_name
        self.brain_name = brain_name


class AgentAction:
    def name(self) -> str:
        raise NotImplementedError

    def description(self) -> str:
        raise NotImplementedError

    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
        }

    def call(self, arguments: Dict[str, Any], ctx: ActionContext) -> Any:
        raise NotImplementedError

    def as_tool_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name(),
                "description": self.description(),
                "parameters": self.parameters_schema(),
            },
        }


class WebFetchAction(AgentAction):
    def __init__(self, *, max_bytes: int = 150_000, timeout_s: float = 15.0):
        self.max_bytes = max_bytes
        self.timeout_s = timeout_s

    def name(self) -> str:
        return "web_fetch"

    def description(self) -> str:
        return "Fetch a URL over HTTP(S) and return the text content (truncated)."

    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "HTTP or HTTPS URL"},
                "headers": {"type": "object", "description": "Optional request headers"},
            },
            "required": ["url"],
        }

    def call(self, arguments: Dict[str, Any], ctx: ActionContext) -> Any:
        import httpx
        url = str(arguments.get("url"))
        headers = arguments.get("headers") or {}
        with httpx.Client(follow_redirects=True, timeout=self.timeout_s) as client:
            resp = client.get(url, headers=headers)
            resp.raise_for_status()
            content_type = resp.headers.get('content-type', '')
            text = resp.text
            if not text:
                # Try bytes decode best-effort
                try:
                    text = resp.content[: self.max_bytes].decode('utf-8', errors='replace')
                except Exception:
                    text = ""
            if len(text) > self.max_bytes:
                text = text[: self.max_bytes]
            return {
                "url": url,
                "status_code": resp.status_code,
                "content_type": content_type,
                "text": text,
            }


class ImageGenerateAction(AgentAction):
    def name(self) -> str:
        return "generate_image"

    def description(self) -> str:
        return "Generate an image from a prompt and return the image URL."

    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "prompt": {"type": "string"},
                "model": {"type": "string"},
                "size": {"type": "string", "enum": ["256x256", "512x512", "1024x1024"]},
                "quality": {"type": "string", "enum": ["standard", "hd"]},
                "style": {"type": "string", "enum": ["vivid", "natural"]},
            },
            "required": ["prompt"],
        }

    def call(self, arguments: Dict[str, Any], ctx: ActionContext) -> Any:
        # Requires OpenAI provider support
        params = {}
        for k in ("model", "size", "quality", "style"):
            if arguments.get(k) is not None:
                params[k] = arguments[k]
        res = getattr(ctx.provider, 'generate_image')(arguments["prompt"], **params)
        return res


class ImageAnalyzeUrlsAction(AgentAction):
    def name(self) -> str:
        return "analyze_image_urls"

    def description(self) -> str:
        return "Analyze one or more image URLs with a vision-capable model."

    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "prompt": {"type": "string"},
                "image_urls": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                },
                "model": {"type": "string"},
                "temperature": {"type": "number"},
                "max_tokens": {"type": "integer"},
            },
            "required": ["prompt", "image_urls"],
        }

    def call(self, arguments: Dict[str, Any], ctx: ActionContext) -> Any:
        # Provider must expose a vision method for URLs
        vision_fn = getattr(ctx.provider, 'vision_urls', None)
        if not vision_fn:
            raise RuntimeError('Provider does not support analyzing image URLs')
        params = {}
        for k in ("model", "temperature", "max_tokens"):
            if arguments.get(k) is not None:
                params[k] = arguments[k]
        return vision_fn(arguments["prompt"], arguments["image_urls"], **params)


class EmbeddingCreateAction(AgentAction):
    def name(self) -> str:
        return "create_embedding"

    def description(self) -> str:
        return "Create embeddings for text and return the embedding vector(s)."

    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "text": {"type": ["string", "array"], "description": "Text or list of texts"},
                "model": {"type": "string"},
                "dimensions": {"type": "integer"},
                "encoding_format": {"type": "string", "enum": ["float", "base64"]},
            },
            "required": ["text"],
        }

    def call(self, arguments: Dict[str, Any], ctx: ActionContext) -> Any:
        params = {}
        for k in ("model", "dimensions", "encoding_format"):
            if arguments.get(k) is not None:
                params[k] = arguments[k]
        res = getattr(ctx.provider, 'create_embedding')(arguments["text"], **params)
        return res


class BrainDocumentSearchAction(AgentAction):
    def name(self) -> str:
        return "brain_document_search"

    def description(self) -> str:
        return "Search a brain collection with a semantic query and return results."

    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "collection": {"type": "string"},
                "query": {"type": "string"},
                "limit": {"type": "integer"},
                "min_score": {"type": "number"},
            },
            "required": ["collection", "query"],
        }

    def call(self, arguments: Dict[str, Any], ctx: ActionContext) -> Any:
        if not ctx.brain_name:
            raise RuntimeError('Agent has no brain configured')
        from ffmcp.brain import ZepBrainClient, BrainInfo
        zcfg = ctx.config.get_zep_settings()
        client = ZepBrainClient(api_key=zcfg.get('api_key'), base_url=zcfg.get('base_url'), env=zcfg.get('env'))
        brain_info = BrainInfo(name=ctx.brain_name)
        res = client.document_search(
            brain=brain_info,
            collection=str(arguments["collection"]),
            query=str(arguments["query"]),
            limit=int(arguments.get("limit") or 5),
            min_score=arguments.get("min_score"),
        )
        return res


BUILTIN_ACTIONS = {
    'web_fetch': WebFetchAction,
    'generate_image': ImageGenerateAction,
    'analyze_image_urls': ImageAnalyzeUrlsAction,
    'create_embedding': EmbeddingCreateAction,
    'brain_document_search': BrainDocumentSearchAction,
}


