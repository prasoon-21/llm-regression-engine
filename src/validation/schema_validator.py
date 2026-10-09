"""Schema conformance validation layer using Pydantic and Instructor principles."""
import json
import logging
from typing import Any, Dict, List, Optional, Tuple, Type
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)


class SchemaValidationResult(BaseModel):
    is_valid: bool
    errors: List[str] = []
    parsed_data: Optional[Dict[str, Any]] = None


class CustomerSupportIntentSchema(BaseModel):
    intent: str
    confidence: float
    action: str
    response: str


class InvoiceExtractionSchema(BaseModel):
    invoice_id: str
    vendor: str
    amount: float
    currency: str
    due_date: str


SCHEMA_REGISTRY: Dict[str, Type[BaseModel]] = {
    "customer_support_intent_router": CustomerSupportIntentSchema,
    "structured_invoice_extractor": InvoiceExtractionSchema,
}


def validate_schema_conformance(
    target_name: str,
    output_data: Any,
    custom_model: Optional[Type[BaseModel]] = None
) -> SchemaValidationResult:
    """
    Validate LLM output against strict Pydantic schemas.
    Accepts raw strings (JSON) or pre-parsed dicts.
    """
    model_class = custom_model or SCHEMA_REGISTRY.get(target_name)

    # If no strict schema registered for this generic task, check if it's valid JSON
    if not model_class:
        if isinstance(output_data, dict):
            return SchemaValidationResult(is_valid=True, parsed_data=output_data)
        if isinstance(output_data, str):
            try:
                parsed = json.loads(output_data)
                return SchemaValidationResult(is_valid=True, parsed_data=parsed if isinstance(parsed, dict) else {"raw": parsed})
            except Exception:
                # Text output is acceptable if no schema registered
                return SchemaValidationResult(is_valid=True, parsed_data={"text": output_data})

    # Prepare dict
    data_dict = output_data
    if isinstance(output_data, str):
        try:
            data_dict = json.loads(output_data)
        except json.JSONDecodeError as e:
            return SchemaValidationResult(
                is_valid=False,
                errors=[f"Output is not valid JSON: {str(e)}"]
            )

    if not isinstance(data_dict, dict):
        return SchemaValidationResult(
            is_valid=False,
            errors=[f"Expected dictionary payload but received {type(data_dict).__name__}"]
        )

    try:
        validated = model_class.model_validate(data_dict)
        return SchemaValidationResult(
            is_valid=True,
            parsed_data=validated.model_dump()
        )
    except ValidationError as ve:
        error_messages = [
            f"Field '{'.'.join(str(loc) for loc in err['loc'])}': {err['msg']}"
            for err in ve.errors()
        ]
        return SchemaValidationResult(
            is_valid=False,
            errors=error_messages
        )
