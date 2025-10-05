"""CLI output validation using JSON Schema."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    import jsonschema
    from jsonschema import Draft7Validator
except ImportError:
    jsonschema = None  # type: ignore
    Draft7Validator = None  # type: ignore


class ValidationError(Exception):
    """Raised when CLI output validation fails."""


def get_schema_path(version: str = "v1") -> Path:
    """Get path to CLI schema file."""
    schema_dir = Path(__file__).parent.parent.parent / "schemas" / "cli" / version
    return schema_dir / "cli-schema.json"


def load_schema(version: str = "v1") -> dict[str, Any]:
    """Load CLI schema from file."""
    schema_path = get_schema_path(version)
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    
    with open(schema_path) as f:
        return json.load(f)


def validate_cli_output(output: dict[str, Any], version: str = "v1") -> None:
    """
    Validate CLI output against JSON schema.
    
    Args:
        output: Dictionary to validate
        version: Schema version to use (default: "v1")
        
    Raises:
        ValidationError: If validation fails
        ImportError: If jsonschema package not available
    """
    if jsonschema is None:
        raise ImportError(
            "jsonschema package required for validation. "
            "Install with: pip install jsonschema"
        )
    
    schema = load_schema(version)
    
    try:
        validator = Draft7Validator(schema)
        validator.validate(output)
    except jsonschema.ValidationError as e:
        raise ValidationError(f"CLI output validation failed: {e.message}") from e
    except jsonschema.SchemaError as e:
        raise ValidationError(f"Invalid schema: {e.message}") from e


def validate_cli_output_string(output_json: str, version: str = "v1") -> None:
    """
    Validate CLI output JSON string against schema.
    
    Args:
        output_json: JSON string to validate
        version: Schema version to use (default: "v1")
        
    Raises:
        ValidationError: If validation fails
        json.JSONDecodeError: If JSON is malformed
    """
    try:
        output = json.loads(output_json)
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON: {e}") from e
    
    validate_cli_output(output, version)


def get_validation_examples() -> dict[str, dict[str, Any]]:
    """Get example valid outputs for each CLI command."""
    return {
        "n_two_prop": {"n1": 388, "n2": 388},
        "n_one_sample_prop": {"n": 123},
        "n_mean": {"n1": 64, "n2": 64},
        "n_one_sample_mean": {"n": 34},
        "n_paired": {"n": 34},
        "n_anova": {"n_total": 120},
        "alpha_adjust": {"alpha": 0.004166666666666667},
        "bh_thresholds": {"thresholds": [0.004166, 0.008333, 0.0125]},
    }