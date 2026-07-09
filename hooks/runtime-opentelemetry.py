"""PyInstaller runtime hook: patch opentelemetry context to handle missing entry points."""
import opentelemetry.context

_orig = opentelemetry.context._load_runtime_context

def _patched():
    try:
        return _orig()
    except StopIteration:
        from opentelemetry.context import contextvars_context
        return contextvars_context.ContextVarsRuntimeContext()

opentelemetry.context._load_runtime_context = _patched
# Also patch the module-level context instance
try:
    opentelemetry.context._RUNTIME_CONTEXT = _patched()
except Exception:
    pass
