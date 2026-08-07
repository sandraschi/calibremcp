"""PyInstaller runtime hook: patch opentelemetry for missing entry points in frozen exe."""

import os

# Skip propagator loading (entry_points not available in frozen exe)
os.environ.setdefault("OTEL_PROPAGATORS", "none")
os.environ.setdefault("OTEL_PYTHON_CONTEXT", "contextvars_context")

import opentelemetry.context

_orig = opentelemetry.context._load_runtime_context


def _patched():
    try:
        return _orig()
    except StopIteration:
        from opentelemetry.context import contextvars_context

        return contextvars_context.ContextVarsRuntimeContext()


opentelemetry.context._load_runtime_context = _patched
try:
    opentelemetry.context._RUNTIME_CONTEXT = _patched()
except Exception:
    pass
