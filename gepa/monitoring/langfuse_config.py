from __future__ import annotations


def configure_langfuse(public_key: str, secret_key: str):
    if not public_key or not secret_key:
        return None
    try:
        from langfuse.callback import CallbackHandler
        return CallbackHandler(
            public_key=public_key,
            secret_key=secret_key,
        )
    except Exception:
        return None
