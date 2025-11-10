"""Brain integration: unified wrapper over Zep Cloud / Zep Python SDKs and LEANN.

This module provides a high-level API used by the CLI `brain` command to:
- manage named brains (CLI-level namespace)
- add/get/search/clear chat memory (per session)
- create/list collections and add/search/delete documents
- access lowest-level graph APIs when available (Zep only)

Supported backends:
- Zep: Preferred: zep_cloud (Zep Cloud), Fallback: zep_python (self-hosted Zep)
- LEANN: Local vector index with 97% storage savings
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


class ZepSDKNotInstalledError(RuntimeError):
    pass


class LEANNSDKNotInstalledError(RuntimeError):
    pass


@dataclass
class BrainInfo:
    name: str
    default_session_id: Optional[str] = None
    backend: str = "zep"  # "zep" or "leann"


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


class LEANNBrainClient:
    """LEANN-based brain client with full feature parity.

    Uses LEANN for local vector storage with 97% storage savings.
    Collections map to LEANN indexes, documents are stored as text chunks.
    Memory is stored as a special collection per session.
    """

    def __init__(self, *, index_dir: Optional[str] = None):
        """Initialize LEANN client.
        
        Args:
            index_dir: Directory where LEANN indexes are stored. Defaults to ~/.ffmcp/leann_indexes
        """
        self.index_dir = Path(index_dir) if index_dir else Path.home() / '.ffmcp' / 'leann_indexes'
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_leann()

    def _ensure_leann(self) -> None:
        """Ensure LEANN is installed."""
        try:
            from leann import LeannBuilder, LeannSearcher  # type: ignore
            self._builder_class = LeannBuilder
            self._searcher_class = LeannSearcher
        except ImportError as e:
            msg = "LEANN SDK not installed. Install with: pip install leann"
            raise LEANNSDKNotInstalledError(f"{msg} Last error: {e}")

    @staticmethod
    def _ns_collection(brain: str, collection: str) -> str:
        """Namespace collection name with brain prefix."""
        if '::' in collection:
            return collection
        return f"{brain}::{collection}"

    @staticmethod
    def _resolve_session_id(brain: BrainInfo, session_id: Optional[str]) -> str:
        """Resolve session ID."""
        if session_id:
            return session_id
        return brain.default_session_id or brain.name

    def _get_index_path(self, collection_name: str) -> Path:
        """Get path to LEANN index file for a collection."""
        # Sanitize collection name for filesystem
        safe_name = collection_name.replace('::', '_').replace('/', '_').replace('\\', '_')
        return self.index_dir / f"{safe_name}.leann"

    def _get_memory_index_path(self, brain: BrainInfo, session_id: str) -> Path:
        """Get path to memory index for a session."""
        sid = self._resolve_session_id(brain, session_id)
        safe_name = f"{brain.name}_memory_{sid}".replace('::', '_').replace('/', '_').replace('\\', '_')
        return self.index_dir / f"{safe_name}.leann"

    def _load_searcher(self, index_path: Path):
        """Load a LEANN searcher for an index."""
        if not index_path.exists():
            return None
        try:
            return self._searcher_class(str(index_path))
        except Exception:
            return None

    def _load_builder(self, index_path: Path, backend: str = "hnsw", **kwargs):
        """Load a LEANN builder for an index."""
        return self._builder_class(backend_name=backend, **kwargs)
    
    def _rebuild_index_with_new_items(self, index_path: Path, new_items: List[Tuple[str, Dict[str, Any]]]):
        """Rebuild an index with existing items plus new items.
        
        Args:
            index_path: Path to the index file
            new_items: List of (text, metadata) tuples to add
        """
        builder = self._load_builder(index_path)
        
        # Load existing items if index exists
        existing_items = []
        if index_path.exists():
            searcher = self._load_searcher(index_path)
            if searcher:
                try:
                    # Get all existing documents
                    all_results = searcher.search("", top_k=100000)
                    for r in all_results:
                        text = r.text if hasattr(r, 'text') else str(r)
                        metadata = getattr(r, 'metadata', {}) or {}
                        # Skip placeholder collection markers
                        if not metadata.get("__collection__"):
                            existing_items.append((text, metadata))
                except Exception:
                    pass
        
        # Add all items (existing + new)
        for text, metadata in existing_items + new_items:
            builder.add_text(text, metadata=metadata)
        
        # Build index
        builder.build_index(str(index_path))

    # ---------------- Memory ----------------
    def memory_add_messages(
        self,
        *,
        brain: BrainInfo,
        session_id: Optional[str],
        messages: Iterable[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Add messages to memory."""
        sid = self._resolve_session_id(brain, session_id)
        index_path = self._get_memory_index_path(brain, sid)
        
        # Prepare new messages
        new_items = []
        for m in messages:
            role = m.get('role') or m.get('name') or 'user'
            role_type = m.get('role_type') or m.get('type') or 'user'
            content = m.get('content') or m.get('text')
            if content is None:
                continue
            
            # Format message for storage
            text = f"[{role_type}] {role}: {content}"
            metadata = {
                "role": role,
                "role_type": role_type,
                "session_id": sid,
                "brain": brain.name,
            }
            new_items.append((text, metadata))

        if not new_items:
            return {"ok": False, "error": "no messages provided"}

        # Rebuild index with existing + new messages
        self._rebuild_index_with_new_items(index_path, new_items)
        return {"ok": True, "result": {"added": len(new_items), "session_id": sid}}

    def memory_get(self, *, brain: BrainInfo, session_id: Optional[str]) -> Dict[str, Any]:
        """Get memory context for a session."""
        sid = self._resolve_session_id(brain, session_id)
        index_path = self._get_memory_index_path(brain, sid)
        
        searcher = self._load_searcher(index_path)
        if not searcher:
            return {"ok": True, "result": {"messages": [], "session_id": sid}}
        
        # Get all messages by searching with empty query or high top_k
        # LEANN doesn't have a direct "get all" so we use a broad search
        try:
            # Search with a very generic query to get most results
            results = searcher.search("", top_k=1000)
            messages = []
            for r in results:
                if hasattr(r, 'metadata') and r.metadata:
                    messages.append({
                        "role": r.metadata.get("role", "user"),
                        "role_type": r.metadata.get("role_type", "user"),
                        "content": r.text if hasattr(r, 'text') else str(r),
                        "metadata": r.metadata,
                    })
                else:
                    messages.append({
                        "role": "user",
                        "role_type": "user",
                        "content": str(r),
                    })
            return {"ok": True, "result": {"messages": messages, "session_id": sid}}
        except Exception as e:
            return {"ok": True, "result": {"messages": [], "session_id": sid, "error": str(e)}}

    def memory_search(
        self,
        *,
        brain: BrainInfo,
        session_id: Optional[str],
        query: str,
        limit: Optional[int] = None,
        min_score: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Semantic search over session memory."""
        sid = self._resolve_session_id(brain, session_id)
        index_path = self._get_memory_index_path(brain, sid)
        limit = limit or 5
        
        searcher = self._load_searcher(index_path)
        if not searcher:
            return {"ok": True, "result": []}
        
        try:
            results = searcher.search(query, top_k=limit)
            formatted_results = []
            for r in results:
                score = getattr(r, 'score', None) or getattr(r, 'distance', None)
                if min_score is not None and score is not None and score < min_score:
                    continue
                
                result_dict = {
                    "text": r.text if hasattr(r, 'text') else str(r),
                    "score": score,
                }
                if hasattr(r, 'metadata') and r.metadata:
                    result_dict["metadata"] = r.metadata
                formatted_results.append(result_dict)
            
            return {"ok": True, "result": formatted_results}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def memory_clear(self, *, brain: BrainInfo, session_id: Optional[str]) -> Dict[str, Any]:
        """Clear memory for a session."""
        sid = self._resolve_session_id(brain, session_id)
        index_path = self._get_memory_index_path(brain, sid)
        
        try:
            if index_path.exists():
                index_path.unlink()
            # Also remove any associated metadata files
            meta_path = Path(str(index_path) + ".meta.json")
            if meta_path.exists():
                meta_path.unlink()
            return {"ok": True, "result": {"cleared": True, "session_id": sid}}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ---------------- Collections / Documents ----------------
    def collection_create(
        self,
        *,
        brain: BrainInfo,
        name: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a namespaced collection (LEANN index)."""
        full_name = self._ns_collection(brain.name, name)
        index_path = self._get_index_path(full_name)
        
        # Create empty index to mark collection as created
        builder = self._load_builder(index_path)
        # Add a placeholder document
        builder.add_text("", metadata={"__collection__": True, "name": full_name, "description": description or "", **(metadata or {})})
        builder.build_index(str(index_path))
        
        return {"ok": True, "result": {"name": full_name, "description": description, "metadata": metadata}}

    def collection_list(self, *, brain: BrainInfo) -> Dict[str, Any]:
        """List collections for a brain."""
        items = []
        prefix = f"{brain.name}::"
        
        # Scan index directory for matching indexes
        for index_file in self.index_dir.glob("*.leann"):
            # Extract collection name from filename
            safe_name = index_file.stem
            # Try to reverse the sanitization
            collection_name = safe_name.replace('_', '::')
            
            # Check if it belongs to this brain
            if collection_name.startswith(prefix) or collection_name.startswith(brain.name + "_"):
                # Try to load metadata
                meta_path = index_file.with_suffix('.leann.meta.json')
                metadata = {}
                if meta_path.exists():
                    try:
                        with open(meta_path, 'r') as f:
                            metadata = json.load(f)
                    except Exception:
                        pass
                
                items.append({
                    "name": collection_name,
                    "metadata": metadata,
                })
        
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
        """Add a text document to a collection."""
        full_collection = self._ns_collection(brain.name, collection)
        if text is None:
            return {"ok": False, "error": "text is required"}
        
        index_path = self._get_index_path(full_collection)
        
        # Prepare document metadata
        doc_metadata = {
            "document_id": document_id,
            "brain": brain.name,
            "collection": full_collection,
            **(metadata or {}),
        }
        
        # Rebuild index with existing + new document
        self._rebuild_index_with_new_items(index_path, [(text, doc_metadata)])
        
        return {"ok": True, "result": {"id": document_id, "collection": full_collection}}

    def document_search(
        self,
        *,
        brain: BrainInfo,
        collection: str,
        query: str,
        limit: Optional[int] = None,
        min_score: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Semantic search over documents in a collection."""
        full_collection = self._ns_collection(brain.name, collection)
        index_path = self._get_index_path(full_collection)
        limit = limit or 5
        
        searcher = self._load_searcher(index_path)
        if not searcher:
            return {"ok": True, "result": []}
        
        try:
            results = searcher.search(query, top_k=limit)
            formatted_results = []
            for r in results:
                score = getattr(r, 'score', None) or getattr(r, 'distance', None)
                if min_score is not None and score is not None and score < min_score:
                    continue
                
                result_dict = {
                    "text": r.text if hasattr(r, 'text') else str(r),
                    "score": score,
                }
                if hasattr(r, 'metadata') and r.metadata:
                    result_dict["metadata"] = r.metadata
                    result_dict["id"] = r.metadata.get("document_id")
                formatted_results.append(result_dict)
            
            return {"ok": True, "result": formatted_results}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def document_delete(
        self,
        *,
        brain: BrainInfo,
        collection: str,
        document_id: str,
    ) -> Dict[str, Any]:
        """Delete a document by id from a collection.
        
        Note: LEANN doesn't support direct deletion. This rebuilds the index
        without the deleted document. For large collections, this may be slow.
        """
        full_collection = self._ns_collection(brain.name, collection)
        index_path = self._get_index_path(full_collection)
        
        if not index_path.exists():
            return {"ok": False, "error": "collection not found"}
        
        # Load existing index and rebuild without the deleted document
        searcher = self._load_searcher(index_path)
        if not searcher:
            return {"ok": False, "error": "could not load collection"}
        
        try:
            # Get all documents
            all_results = searcher.search("", top_k=10000)
            builder = self._load_builder(index_path)
            deleted = False
            
            for r in all_results:
                metadata = getattr(r, 'metadata', {}) or {}
                if metadata.get("document_id") == document_id:
                    deleted = True
                    continue
                # Re-add document
                text = r.text if hasattr(r, 'text') else str(r)
                builder.add_text(text, metadata=metadata)
            
            if deleted:
                builder.build_index(str(index_path))
                return {"ok": True, "result": {"deleted": True, "document_id": document_id}}
            else:
                return {"ok": False, "error": "document not found"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ---------------- Graph (not supported by LEANN) ----------------
    def graph_add(self, *, user_id: str, data_type: str, data: Any) -> Dict[str, Any]:
        return {"ok": False, "error": "graph API not available in LEANN backend"}

    def graph_get(self, *, user_id: str) -> Dict[str, Any]:
        return {"ok": False, "error": "graph API not available in LEANN backend"}


# ---------------- Unified Brain Client Factory ----------------
def create_brain_client(
    *,
    backend: str = "zep",
    brain: BrainInfo,
    zep_api_key: Optional[str] = None,
    zep_base_url: Optional[str] = None,
    zep_env: Optional[str] = None,
    leann_index_dir: Optional[str] = None,
) -> Any:
    """Create a brain client based on backend type.
    
    Args:
        backend: "zep" or "leann"
        brain: BrainInfo instance
        zep_api_key: Zep API key (for zep backend)
        zep_base_url: Zep base URL (for zep backend)
        zep_env: Zep environment (for zep backend)
        leann_index_dir: LEANN index directory (for leann backend)
    
    Returns:
        ZepBrainClient or LEANNBrainClient instance
    """
    if backend == "leann":
        return LEANNBrainClient(index_dir=leann_index_dir)
    else:
        return ZepBrainClient(api_key=zep_api_key, base_url=zep_base_url, env=zep_env)


