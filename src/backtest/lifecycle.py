"""Conservative research-only trade lifecycle simulation boundary.

This module validates caller-supplied lifecycle observations against an already
validated candle replay. It does not generate entries, place orders, model fills,
calculate PnL, optimize parameters, or approve PAPER/LIVE runtime use.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from hashlib import sha256
from json import dumps
from typing import Any

from src.backtest.replay import CandleReplay, CandleReplayError


class TradeLifecycleSimulationError(ValueError):
    """Raised when lifecycle simulation input fails closed validation."""


class LifecycleEventType(StrEnum):
    """Caller-supplied lifecycle observation types."""

    ENTRY_OBSERVED = "ENTRY_OBSERVED"
    EXIT_OBSERVED = "EXIT_OBSERVED"
    ENTRY_REJECTED = "ENTRY_REJECTED"
    TIMEOUT_OBSERVED = "TIMEOUT_OBSERVED"


class LifecycleState(StrEnum):
    """Conservative lifecycle states derived from caller evidence only."""

    WAITING_ENTRY = "WAITING_ENTRY"
    POSITION_OBSERVED_OPEN = "POSITION_OBSERVED_OPEN"
    POSITION_OBSERVED_CLOSED = "POSITION_OBSERVED_CLOSED"
    ENTRY_REJECTED = "ENTRY_REJECTED"
    TIMED_OUT = "TIMED_OUT"
    INVALID = "INVALID"


TERMINAL_STATES: frozenset[LifecycleState] = frozenset(
    {
        LifecycleState.POSITION_OBSERVED_CLOSED,
        LifecycleState.ENTRY_REJECTED,
        LifecycleState.TIMED_OUT,
    }
)


@dataclass(frozen=True)
class LifecycleObservation:
    """One normalized caller-supplied lifecycle observation."""

    event_type: LifecycleEventType
    event_time: str
    price: Decimal | None = None
    note: str | None = None

    def payload(self) -> dict[str, str | None]:
        """Return deterministic JSON-compatible observation payload."""

        return {
            "event_time": self.event_time,
            "event_type": self.event_type.value,
            "note": self.note,
            "price": _decimal_text(self.price) if self.price is not None else None,
        }


@dataclass(frozen=True)
class LifecycleTransition:
    """One deterministic lifecycle transition produced from observations."""

    sequence: int
    event_type: LifecycleEventType
    event_time: str
    candle_open_time: str
    from_state: LifecycleState
    to_state: LifecycleState
    evidence: str

    def payload(self) -> dict[str, int | str]:
        """Return deterministic JSON-compatible transition payload."""

        return {
            "candle_open_time": self.candle_open_time,
            "event_time": self.event_time,
            "event_type": self.event_type.value,
            "evidence": self.evidence,
            "from_state": self.from_state.value,
            "sequence": self.sequence,
            "to_state": self.to_state.value,
        }


@dataclass(frozen=True)
class LifecycleSimulationMetadata:
    """Auditable metadata for a lifecycle simulation boundary."""

    trade_id: str
    dataset_fingerprint: str
    event_count: int
    transition_count: int
    start_state: str
    terminal_state: str
    validation_status: str
    deterministic_hash: str

    def payload(self) -> dict[str, int | str]:
        """Return deterministic metadata payload."""

        return {
            "dataset_fingerprint": self.dataset_fingerprint,
            "deterministic_hash": self.deterministic_hash,
            "event_count": self.event_count,
            "start_state": self.start_state,
            "terminal_state": self.terminal_state,
            "trade_id": self.trade_id,
            "transition_count": self.transition_count,
            "validation_status": self.validation_status,
        }


@dataclass(frozen=True)
class TradeLifecycleSimulation:
    """Validated lifecycle transitions plus metadata and diagnostic errors."""

    metadata: LifecycleSimulationMetadata
    observations: tuple[LifecycleObservation, ...]
    transitions: tuple[LifecycleTransition, ...]
    errors: tuple[str, ...] = ()

    def iter_transitions(self) -> tuple[LifecycleTransition, ...]:
        """Return transitions only when lifecycle input was valid."""

        if self.metadata.validation_status != "VALID":
            raise TradeLifecycleSimulationError(
                "cannot iterate invalid lifecycle simulation"
            )
        return self.transitions


def build_trade_lifecycle_simulation(
    replay: CandleReplay,
    observations: Iterable[Mapping[str, Any]],
    *,
    trade_id: str,
    allow_read_only_diagnostics: bool = False,
) -> TradeLifecycleSimulation:
    """Build a deterministic lifecycle simulation from caller observations.

    The replay must already be valid. Observations are checked against replayed
    candle open times and transition rules. Invalid input fails closed by default.
    """

    if not trade_id.strip():
        raise TradeLifecycleSimulationError("trade_id is required")
    try:
        replay_rows = replay.iter_rows()
    except CandleReplayError as exc:
        raise TradeLifecycleSimulationError(
            "valid candle replay is required before lifecycle simulation"
        ) from exc
    candle_times = {row.open_time for row in replay_rows}
    normalized: list[LifecycleObservation] = []
    transitions: list[LifecycleTransition] = []
    errors: list[str] = []
    previous_event_at: datetime | None = None
    state = LifecycleState.WAITING_ENTRY

    for index, raw in enumerate(observations):
        try:
            observation = _normalize_observation(raw, index=index)
        except TradeLifecycleSimulationError as exc:
            errors.append(str(exc))
            continue
        event_at = _parse_utc_timestamp("event_time", observation.event_time)
        if previous_event_at is not None and event_at <= previous_event_at:
            errors.append(f"observation {index}: event_time is not increasing")
        previous_event_at = event_at
        if observation.event_time not in candle_times:
            errors.append(f"observation {index}: event_time has no replay candle")
        next_state = _transition_state(
            current=state,
            event_type=observation.event_type,
            index=index,
            errors=errors,
        )
        transitions.append(
            LifecycleTransition(
                sequence=len(transitions),
                event_type=observation.event_type,
                event_time=observation.event_time,
                candle_open_time=observation.event_time,
                from_state=state,
                to_state=next_state,
                evidence="CALLER_SUPPLIED_OBSERVATION",
            )
        )
        state = next_state
        normalized.append(observation)

    if not normalized:
        errors.append("at least one lifecycle observation is required")
    if state not in TERMINAL_STATES and state is not LifecycleState.INVALID:
        errors.append("lifecycle simulation must end in a terminal state")
    if errors:
        state = LifecycleState.INVALID
    metadata = _metadata_for(
        trade_id=trade_id.strip(),
        dataset_fingerprint=replay.metadata.dataset_fingerprint,
        observations=tuple(normalized),
        transitions=tuple(transitions),
        terminal_state=state,
        validation_status="VALID" if not errors else "INVALID",
    )
    simulation = TradeLifecycleSimulation(
        metadata=metadata,
        observations=tuple(normalized),
        transitions=tuple(transitions),
        errors=tuple(errors),
    )
    if errors and not allow_read_only_diagnostics:
        raise TradeLifecycleSimulationError("; ".join(errors))
    return simulation


def lifecycle_metadata_json(metadata: LifecycleSimulationMetadata) -> str:
    """Serialize lifecycle metadata deterministically."""

    return dumps(metadata.payload(), sort_keys=True, separators=(",", ":"))


def lifecycle_transitions_json(
    transitions: Iterable[LifecycleTransition],
) -> str:
    """Serialize lifecycle transitions deterministically."""

    return dumps(
        [transition.payload() for transition in transitions],
        sort_keys=True,
        separators=(",", ":"),
    )


def _transition_state(
    *,
    current: LifecycleState,
    event_type: LifecycleEventType,
    index: int,
    errors: list[str],
) -> LifecycleState:
    if current in TERMINAL_STATES:
        errors.append(f"observation {index}: event after terminal state")
        return LifecycleState.INVALID
    if current is LifecycleState.WAITING_ENTRY:
        if event_type is LifecycleEventType.ENTRY_OBSERVED:
            return LifecycleState.POSITION_OBSERVED_OPEN
        if event_type is LifecycleEventType.ENTRY_REJECTED:
            return LifecycleState.ENTRY_REJECTED
        errors.append(f"observation {index}: terminal event without observed entry")
        return LifecycleState.INVALID
    if current is LifecycleState.POSITION_OBSERVED_OPEN:
        if event_type is LifecycleEventType.EXIT_OBSERVED:
            return LifecycleState.POSITION_OBSERVED_CLOSED
        if event_type is LifecycleEventType.TIMEOUT_OBSERVED:
            return LifecycleState.TIMED_OUT
        errors.append(f"observation {index}: duplicate or invalid entry observation")
        return LifecycleState.INVALID
    errors.append(f"observation {index}: invalid lifecycle state")
    return LifecycleState.INVALID


def _metadata_for(
    *,
    trade_id: str,
    dataset_fingerprint: str,
    observations: tuple[LifecycleObservation, ...],
    transitions: tuple[LifecycleTransition, ...],
    terminal_state: LifecycleState,
    validation_status: str,
) -> LifecycleSimulationMetadata:
    base_payload = {
        "dataset_fingerprint": dataset_fingerprint,
        "event_count": len(observations),
        "observations": [observation.payload() for observation in observations],
        "start_state": LifecycleState.WAITING_ENTRY.value,
        "terminal_state": terminal_state.value,
        "trade_id": trade_id,
        "transition_count": len(transitions),
        "transitions": [transition.payload() for transition in transitions],
        "validation_status": validation_status,
    }
    deterministic_hash = sha256(
        dumps(base_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return LifecycleSimulationMetadata(
        trade_id=trade_id,
        dataset_fingerprint=dataset_fingerprint,
        event_count=len(observations),
        transition_count=len(transitions),
        start_state=LifecycleState.WAITING_ENTRY.value,
        terminal_state=terminal_state.value,
        validation_status=validation_status,
        deterministic_hash=deterministic_hash,
    )


def _normalize_observation(
    row: Mapping[str, Any],
    *,
    index: int,
) -> LifecycleObservation:
    event_type_text = _required_text(row, "event_type", index)
    try:
        event_type = LifecycleEventType(event_type_text)
    except ValueError as exc:
        raise TradeLifecycleSimulationError(
            f"observation {index}: unsupported event_type"
        ) from exc
    event_time = _required_text(row, "event_time", index)
    _parse_utc_timestamp("event_time", event_time)
    price = _optional_decimal(row, "price", index)
    if price is not None and price <= 0:
        raise TradeLifecycleSimulationError(
            f"observation {index}: price must be positive when supplied"
        )
    note_value = row.get("note")
    if note_value is not None and not isinstance(note_value, str):
        raise TradeLifecycleSimulationError(f"observation {index}: note must be text")
    if isinstance(note_value, str) and note_value.strip():
        note = note_value.strip()
    else:
        note = None
    return LifecycleObservation(
        event_type=event_type,
        event_time=event_time,
        price=price,
        note=note,
    )


def _required_text(row: Mapping[str, Any], name: str, index: int) -> str:
    value = row.get(name)
    if not isinstance(value, str) or not value.strip():
        raise TradeLifecycleSimulationError(f"observation {index}: {name} is required")
    return value.strip()


def _optional_decimal(
    row: Mapping[str, Any],
    name: str,
    index: int,
) -> Decimal | None:
    value = row.get(name)
    if value is None:
        return None
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise TradeLifecycleSimulationError(
            f"observation {index}: {name} must be numeric"
        ) from exc
    if not parsed.is_finite():
        raise TradeLifecycleSimulationError(
            f"observation {index}: {name} must be finite"
        )
    return parsed


def _parse_utc_timestamp(name: str, value: str) -> datetime:
    if not value.endswith("Z"):
        raise TradeLifecycleSimulationError(f"{name} must be UTC and end with 'Z'")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise TradeLifecycleSimulationError(
            f"{name} must be an ISO-8601 timestamp"
        ) from exc
    if parsed.tzinfo != UTC:
        raise TradeLifecycleSimulationError(f"{name} must use UTC timezone")
    return parsed


def _decimal_text(value: Decimal) -> str:
    return format(value.normalize(), "f")
