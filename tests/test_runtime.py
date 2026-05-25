import json
import logging
from io import StringIO

from src.logging_config import configure_logging
from src.runtime import configure_determinism, initialize_runtime


def test_runtime_context_emits_limited_determinism_claim() -> None:
    context = initialize_runtime()
    record = context.audit_record()
    assert record["settings"]["mode"] == "PAPER_ONLY"
    assert record["metadata"]["requested_random_seed"] == 42
    assert (
        record["metadata"]["determinism_scope"] == "PYTHON_RANDOM_SEED_DECLARATION_ONLY"
    )


def test_deterministic_seed_repeats_python_random_values() -> None:
    configure_determinism(17)
    first = __import__("random").random()
    configure_determinism(17)
    second = __import__("random").random()
    assert first == second


def test_json_logging_contains_safety_context() -> None:
    stream = StringIO()
    configure_logging("INFO", stream=stream)
    logging.getLogger("test").info(
        "safe bootstrap",
        extra={
            "event": "bootstrap",
            "mode": "PAPER_ONLY",
            "readiness": "RESEARCH_ONLY",
        },
    )
    payload = json.loads(stream.getvalue())
    assert payload["message"] == "safe bootstrap"
    assert payload["mode"] == "PAPER_ONLY"
    assert payload["readiness"] == "RESEARCH_ONLY"
