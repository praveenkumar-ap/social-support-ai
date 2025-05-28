"""
Observability hooks: provide tracing and logging decorators for instrumenting functions.
"""

import logging
import functools
from typing import Callable, Any, Coroutine

# Hypothetical tracing client (e.g., LangSmith)
try:
    from langsmith import TraceClient
    trace_client = TraceClient()
except ImportError:
    trace_client = None

logger = logging.getLogger(__name__)

def trace(operation_name: str):
    """
    Decorator to trace function execution with start/end logs and optional external tracing.
    
    :param operation_name: name of the operation for tracing
    """
    def decorator(func: Callable[..., Coroutine[Any, Any, Any]]):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            logger.info(f"🔍 Trace start: {operation_name}")
            span = None
            if trace_client:
                try:
                    span = trace_client.start_span(operation_name)
                except Exception:
                    logger.warning("Failed to start external trace span", exc_info=True)
            try:
                result = await func(*args, **kwargs)
                logger.info(f"✅ Trace end: {operation_name}")
                if span:
                    span.finish(status="ok")
                return result
            except Exception as e:
                logger.exception(f"❌ Trace error: {operation_name}")
                if span:
                    span.finish(status="error", error=e)
                raise
        return wrapper
    return decorator