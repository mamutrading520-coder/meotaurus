"""Document management tool service.

This module owns the manage_documents tool implementation.

Temporary compatibility note:
some ownership/state helpers still live in src.tool_implementations because
create/update/edit/suggest document use the same helpers. A later phase can
move those helpers into this package too.
"""

from typing import Dict, Optional

from src.tool_implementations import (
    MAX_READ_CHARS,
    _get_owned_document,
    _most_recent_owned_document,
    _owned_document_query,
    _parse_tool_args,
    logger,
    set_active_document,
)


def _get_active_document_id():
    from src import tool_implementations as tool_impl

    return tool_impl._active_document_id


async def do_manage_documents(content: str, owner: Optional[str] = None) -> Dict:
    """Manage documents: list, read/view/open, delete, tidy.

    Output format mirrors `manage_session`: list rows include a
    clickable `[Title](#document-<id>)` anchor + relative timestamps
    so the user can click straight from chat to open the editor.
    """
    from core.database import SessionLocal, Document
    from datetime import datetime, timezone

    try:
        args = _parse_tool_args(content)
    except ValueError:
        return {"error": "Invalid JSON arguments", "exit_code": 1}

    action = args.get("action", "list")
    db = SessionLocal()

    def _rel(ts):
        if not ts:
            return 'never'
        try:
            now = datetime.now(timezone.utc) if ts.tzinfo is not None else datetime.utcnow()
            diff = (now - ts).total_seconds()
        except Exception:
            return 'unknown'
        if diff < 60: return 'just now'
        if diff < 3600: return f'{int(diff / 60)}m ago'
        if diff < 86400: return f'{int(diff / 3600)}h ago'
        if diff < 86400 * 7: return f'{int(diff / 86400)}d ago'
        return ts.strftime('%Y-%m-%d')

    try:
        if action == "list":
            q = db.query(Document).filter(Document.is_active == True)
            q = _owned_document_query(q, Document, owner)
            if args.get("search"):
                q = q.filter(Document.title.ilike(f"%{args['search']}%"))
            if args.get("language"):
                q = q.filter(Document.language == args["language"])
            docs = q.order_by(Document.updated_at.desc()).limit(args.get("limit", 50)).all()
            if not docs:
                msg = "No documents found" + (f" matching '{args['search']}'" if args.get("search") else "") + "."
                return {"response": msg, "documents": [], "exit_code": 0}
            lines = []
            items = []
            for i, d in enumerate(docs):
                size = len(d.current_content or "")
                lang = d.language or "text"
                ts = getattr(d, 'updated_at', None) or getattr(d, 'created_at', None)
                marker = " ← most recent" if i == 0 else ""
                lines.append(
                    f"- [{d.title}](#document-{d.id}) — {lang}, {size} chars, updated {_rel(ts)}{marker}"
                )
                items.append({"id": d.id, "title": d.title, "language": lang, "size": size})
            header = f"Found {len(docs)} document(s), sorted most-recent first. Click a title to open:"
            return {
                "response": header + "\n" + "\n".join(lines),
                "documents": items,
                "exit_code": 0,
            }

        elif action in ("read", "view", "open", "get"):
            doc_id = args.get("document_id") or args.get("id") or args.get("uid")
            if not doc_id:
                return {"error": "Need document_id (use action=list to find one)", "exit_code": 1}
            doc = _get_owned_document(db, Document, doc_id, owner, active_only=True)
            if not doc:
                return {"error": f"Document '{doc_id}' not found", "exit_code": 1}
            body = doc.current_content or ""
            preview_limit = int(args.get("limit", MAX_READ_CHARS))
            truncated = len(body) > preview_limit
            preview = body[:preview_limit] + (f"\n... (truncated, {len(body)} chars total)" if truncated else "")
            anchor = f"[{doc.title}](#document-{doc.id})"
            return {
                "response": f"{anchor} — click to open in editor.\n\n```{doc.language or ''}\n{preview}\n```",
                "document": {
                    "id": doc.id,
                    "title": doc.title,
                    "language": doc.language,
                    "size": len(body),
                    "content": preview,
                    "truncated": truncated,
                },
                "exit_code": 0,
            }

        elif action == "delete":
            doc_id = args.get("document_id") or args.get("id") or args.get("uid") or _get_active_document_id()
            doc = None
            if doc_id:
                doc = _get_owned_document(db, Document, doc_id, owner)
            if not doc:
                # Fallback: most recently updated doc (likely what the user means)
                doc = _most_recent_owned_document(db, Document, owner, active_only=True)
            if not doc:
                return {"error": "No document to delete", "exit_code": 1}
            title = doc.title
            doc.is_active = False
            db.commit()
            if _get_active_document_id() == doc.id:
                set_active_document(None)
            return {"response": f"Deleted document '{title}'", "exit_code": 0}

        elif action == "tidy":
            from src.document_actions import run_document_tidy
            result = await run_document_tidy(owner or "")
            return {"response": result, "exit_code": 0}

        else:
            return {"error": f"Unknown action: {action}", "exit_code": 1}
    except Exception as e:
        logger.error(f"manage_documents error: {e}")
        return {"error": str(e), "exit_code": 1}
    finally:
        db.close()
