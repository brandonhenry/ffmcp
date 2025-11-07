"""Zep Brain integration: unified wrapper over Zep Cloud / Zep Python SDKs.

This module provides a high-level API used by the CLI `brain` command to:
- manage named brains (CLI-level namespace)
- add/get/search/clear chat memory (per session)
- create/list collections and add/search/delete documents
- access lowest-level graph APIs when available

It autodetects the available Zep SDK:
- Preferred: zep_cloud (Zep Cloud)
- Fallback: zep_python (self-hosted Zep)
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple


class ZepSDKNotInstalledError(RuntimeError):
    pass


@dataclass
class BrainInfo:
    name: str
    default_session_id: Optional[str] = None


class ZepBrainClient:
    """Facade over Zep SDK with CLI-friendly helpers.

    A Brain is a CLI concept that namespaces session and collection identifiers.
    By default, the brain name is used as the session id and as a namespace
    prefix for collections (e.g., "brain::collection").
    """

    def __init__(self, *, api_key: Optional[str], base_url: Optional[str] = None, env: Optional[str] = None):
        self.api_key = api_key or os.getenv('ZEP_API_KEY') or os.getenv('ZEP_CLOUD_API_KEY')
        self.base_url = base_url or os.getenv('ZEP_BASE_URL')
        self.env = (env or os.getenv('ZEP_ENV') or 'cloud').lower()
        self._sdk = None  # "cloud" | "python"
        self._client = None
        self._types: Dict[str, Any] = {}
        self._ensure_client()

    # ---------------- Internal ----------------
    def _ensure_client(self) -> None:
        if self._client is not None:
            return
        last_err: Optional[Exception] = None

        # Try Zep Cloud SDK first
        try:
            from zep_cloud.client import Zep as CloudZep  # type: ignore
            from zep_cloud.types import Message as CloudMessage  # type: ignore
            self._client = CloudZep(api_key=self.api_key) if self.base_url is None else CloudZep(api_key=self.api_key, base_url=self.base_url)
            self._sdk = 'cloud'
            self._types['Message'] = CloudMessage
            return
        except Exception as e:  # noqa: BLE001
            last_err = e

        # Fallback to self-hosted Zep python SDK
        try:
            from zep_python import ZepClient as ZepPythonClient  # type: ignore
            from zep_python.memory import Message as PyMessage  # type: ignore
            self._client = ZepPythonClient(base_url=self.base_url or 'http://localhost:8000', api_key=self.api_key)
            self._sdk = 'python'
            self._types['Message'] = PyMessage
            return
        except Exception as e:  # noqa: BLE001
            last_err = e

        msg = "Zep SDK not installed. Install zep-cloud (preferred) or zep-python."
        raise ZepSDKNotInstalledError(f"{msg} Last error: {last_err}")

    # ---------------- Helpers ----------------
    @staticmethod
    def _ns_collection(brain: str, collection: str) -> str:
        if '::' in collection:
            return collection
        return f"{brain}::{collection}"

    @staticmethod
    def _resolve_session_id(brain: BrainInfo, session_id: Optional[str]) -> str:
        if session_id:
            return session_id
        return brain.default_session_id or brain.name

    # ---------------- Memory ----------------
    def memory_add_messages(
        self,
        *,
        brain: BrainInfo,
        session_id: Optional[str],
        messages: Iterable[Dict[str, Any]],
    ) -> Dict[str, Any]:
        sid = self._resolve_session_id(brain, session_id)
        msg_type = self._types['Message']
        to_msgs = []
        for m in messages:
            # Support common fields: role (speaker name), role_type (user/assistant/system), content
            role = m.get('role') or m.get('name') or 'user'
            role_type = m.get('role_type') or m.get('type') or m.get('role_type'.upper()) or 'user'
            content = m.get('content') or m.get('text')
            if content is None:
                continue
            to_msgs.append(msg_type(role=role, role_type=role_type, content=content))

        if not to_msgs:
            return {"ok": False, "error": "no messages provided"}

        if self._sdk == 'cloud':
            result = self._client.memory.add(session_id=sid, messages=to_msgs)
            return {"ok": True, "result": result}
        # zep_python
        result = self._client.add_memory(session_id=sid, messages=[{"role": m.role, "role_type": m.role_type, "content": m.content} for m in to_msgs])
        return {"ok": True, "result": result}

    def memory_get(self, *, brain: BrainInfo, session_id: Optional[str]) -> Dict[str, Any]:
        sid = self._resolve_session_id(brain, session_id)
        if self._sdk == 'cloud':
            mem = self._client.memory.get(session_id=sid)
            return {"ok": True, "result": mem}
        mem = self._client.get_memory(session_id=sid)
        return {"ok": True, "result": mem}

    def memory_search(
        self,
        *,
        brain: BrainInfo,
        session_id: Optional[str],
        query: str,
        limit: Optional[int] = None,
        min_score: Optional[float] = None,
    ) -> Dict[str, Any]:
        sid = self._resolve_session_id(brain, session_id)
        limit = limit or 5
        if self._sdk == 'cloud':
            results = self._client.memory.search(session_id=sid, text=query, limit=limit, min_score=min_score)
            return {"ok": True, "result": results}
        results = self._client.search_memory(session_id=sid, text=query, limit=limit, min_score=min_score)
        return {"ok": True, "result": results}

    def memory_clear(self, *, brain: BrainInfo, session_id: Optional[str]) -> Dict[str, Any]:
        sid = self._resolve_session_id(brain, session_id)
        if self._sdk == 'cloud':
            res = self._client.memory.delete(session_id=sid)
            return {"ok": True, "result": res}
        res = self._client.delete_memory(session_id=sid)
        return {"ok": True, "result": res}

    # ---------------- Collections / Documents ----------------
    def collection_create(
        self,
        *,
        brain: BrainInfo,
        name: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        full_name = self._ns_collection(brain.name, name)
        if self._sdk == 'cloud':
            res = self._client.collections.add(name=full_name, description=description, metadata=metadata)
            return {"ok": True, "result": res}
        res = self._client.add_collection(name=full_name, description=description, metadata=metadata)
        return {"ok": True, "result": res}

    def collection_list(self, *, brain: BrainInfo) -> Dict[str, Any]:
        if self._sdk == 'cloud':
            res = self._client.collections.list()
            # Filter to this brain namespace
            items = [c for c in res if isinstance(c, dict) and str(c.get('name', '')).startswith(f"{brain.name}::")]
            return {"ok": True, "result": items}
        res = self._client.list_collections()
        items = [c for c in res if isinstance(c, dict) and str(c.get('name', '')).startswith(f"{brain.name}::")]
        return {"ok": True, "result": items}

    def document_add(
        self,
        *,
        brain: BrainInfo,
        collection: str,
        document_id: Optional[str],
        text: Optional[str],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        full_collection = self._ns_collection(brain.name, collection)
        if text is None:
            return {"ok": False, "error": "text is required"}
        if self._sdk == 'cloud':
            res = self._client.collections.documents.add(
                collection=full_collection,
                documents=[{"id": document_id, "text": text, "metadata": metadata or {}}],
            )
            return {"ok": True, "result": res}
        res = self._client.add_document(
            collection=full_collection,
            document={"id": document_id, "text": text, "metadata": metadata or {}},
        )
        return {"ok": True, "result": res}

    def document_search(
        self,
        *,
        brain: BrainInfo,
        collection: str,
        query: str,
        limit: Optional[int] = None,
        min_score: Optional[float] = None,
    ) -> Dict[str, Any]:
        full_collection = self._ns_collection(brain.name, collection)
        limit = limit or 5
        if self._sdk == 'cloud':
            res = self._client.collections.search(collection=full_collection, text=query, limit=limit, min_score=min_score)
            return {"ok": True, "result": res}
        res = self._client.search_documents(collection=full_collection, text=query, limit=limit, min_score=min_score)
        return {"ok": True, "result": res}

    def document_delete(
        self,
        *,
        brain: BrainInfo,
        collection: str,
        document_id: str,
    ) -> Dict[str, Any]:
        full_collection = self._ns_collection(brain.name, collection)
        if self._sdk == 'cloud':
            res = self._client.collections.documents.delete(collection=full_collection, document_id=document_id)
            return {"ok": True, "result": res}
        res = self._client.delete_document(collection=full_collection, document_id=document_id)
        return {"ok": True, "result": res}

    # ---------------- Graph (low-level) ----------------
    def graph_add(self, *, user_id: str, data_type: str, data: Any) -> Dict[str, Any]:
        if self._sdk != 'cloud':
            return {"ok": False, "error": "graph API available in zep-cloud SDK only"}
        # Accept data as dict or JSON string
        payload = data
        if isinstance(data, str):
            try:
                payload = json.loads(data)
            except Exception:
                payload = data
        res = self._client.graph.add(user_id=user_id, type=data_type, data=payload)
        return {"ok": True, "result": res}

    def graph_get(self, *, user_id: str) -> Dict[str, Any]:
        if self._sdk != 'cloud':
            return {"ok": False, "error": "graph API available in zep-cloud SDK only"}
        res = self._client.graph.get(user_id=user_id)
        return {"ok": True, "result": res}


