# Pydantic V2 Migration Guide (SOTA 2026)

This document describes the patterns and requirements for Pydantic models in the CalibreMCP project following the April 2026 Industrialization phase.

## Pattern Overview

CalibreMCP has migrated entirely to **Pydantic V2**. The legacy V1 `@validator` decorators are deprecated and must not be used in new code.

### 1. Field Validators

Instead of `@validator`, use `@field_validator`. 

> [!IMPORTANT]
> All validators must be `classmethod` and follow the V2 signature.

```python
from pydantic import BaseModel, field_validator, ValidationInfo
from typing import ClassVar

class MyModel(BaseModel):
    name: str

    @field_validator("name", mode="after")
    @classmethod
    def validate_name(cls, v: str, info: ValidationInfo) -> str:
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()
```

### 2. Model Configuration

Use the `model_config` attribute instead of the inner `Config` class.

```python
class MyModel(BaseModel):
    model_config = {
        "str_strip_whitespace": True,
        "populate_by_name": True,
    }
```

### 3. Migrating Legacy Code

When migrating legacy V1 models:
1. Replace `@validator('field')` with `@field_validator('field', mode='after')`.
2. Add `@classmethod` to the method if it was missing.
3. Add `info: ValidationInfo` to the arguments (or `**kwargs` if preferred, but `ValidationInfo` is SOTA).
4. Update `cls` usage if the validator was an instance method (though V1 also preferred classmethods).

## Rationale

- **Performance**: Pydantic V2 (Rust core) is significantly faster.
- **Type Safety**: Improved type hinting and validation logic.
- **SOTA Compliance**: Aligning with the 2026 Fleet standards for agentic MCP servers.

## Implementation Notes

References:
- [Pydantic V2 Migration Guide](https://docs.pydantic.dev/latest/migration/)
- `src/calibre_mcp/models/book.py` (Reference implementation)
- `src/calibre_mcp/models/identifier.py`
