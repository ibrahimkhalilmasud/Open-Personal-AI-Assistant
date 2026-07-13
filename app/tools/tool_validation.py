from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class ValidationError:
    code: str
    message: str


@dataclass(slots=True)
class ValidationResult:
    valid: bool
    errors: list[ValidationError]


def _matches_type(expected_type: str, value: Any) -> bool:
    checks: dict[str, type[Any] | tuple[type[Any], ...]] = {
        "string": str,
        "number": (int, float),
        "integer": int,
        "boolean": bool,
        "object": dict,
        "array": list,
    }
    check = checks.get(expected_type)
    if check is None:
        return True
    return isinstance(value, check)


def validate_schema(payload: dict[str, Any], schema: dict[str, Any]) -> ValidationResult:
    errors: list[ValidationError] = []
    required = schema.get("required", [])
    properties = schema.get("properties", {})

    for key in required:
        if key not in payload:
            errors.append(ValidationError("MISSING_PARAMETER", f"Missing required parameter: {key}"))

    for key, value in payload.items():
        definition = properties.get(key, {})
        expected_type = definition.get("type")
        if expected_type and not _matches_type(str(expected_type), value):
            errors.append(
                ValidationError(
                    "INVALID_PARAMETER_TYPE",
                    f"Invalid type for '{key}'. Expected {expected_type}.",
                )
            )

    for key, definition in properties.items():
        if not definition.get("must_exist"):
            continue
        if key not in payload:
            continue
        candidate = payload.get(key)
        if isinstance(candidate, str) and not Path(candidate).exists():
            errors.append(ValidationError("FILE_NOT_FOUND", f"File not found: {candidate}"))

    return ValidationResult(valid=not errors, errors=errors)


def validate_runtime_availability(requirements: list[str]) -> ValidationResult:
    errors: list[ValidationError] = []
    for requirement in requirements:
        try:
            __import__(requirement)
        except Exception:
            errors.append(ValidationError("RUNTIME_UNAVAILABLE", f"Runtime dependency unavailable: {requirement}"))
    return ValidationResult(valid=not errors, errors=errors)
