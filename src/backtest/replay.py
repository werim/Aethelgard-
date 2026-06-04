"""Deterministic candle replay boundary for validated research datasets.

This module replays already supplied candle rows in timestamp order and records
validation metadata. It does not generate signals, simulate trades, calculate
PnL, or approve PAPER/LIVE runtime use.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal, InvalidOperation
from hashlib import sha256
from json import dumps
from re import fullmatch
from typing import Any


class CandleReplayError(ValueError):
    """Raised when candle replay input fails closed validation."""


@dataclass(frozen=True)
class CandleReplayRow:
    """One normalized candle row supplied by an already validated dataset."""

    symbol: str
    timeframe: str
    open_time: str
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal

    def payload(self) -> dict[str, str]:
        """Return a deterministic JSON-compatible row payload."""

        return {
            "close": _decimal_text(self.close),
            "high": _decimal_text(self.high),
            "low": _decimal_text(self.low),
            "open": _decimal_text(self.open),
            "open_time": self.open_time,
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "volume": _decimal_text(self.volume),
        }


@dataclass(frozen=True)
class CandleReplayMetadata:
    """Auditable metadata for a deterministic candle replay dataset."""

    dataset_fingerprint: str
    symbol: str
    timeframe: str
    start_ts: str
    end_ts: str
    row_count: int
    missing_interval_count: int
    duplicate_count: int
    validation_status: str
    deterministic_hash: str

    def payload(self) -> dict[str, int | str]:
        """Return deterministic metadata payload."""

        return {
            "dataset_fingerprint": self.dataset_fingerprint,
            "deterministic_hash": self.deterministic_hash,
            "duplicate_count": self.duplicate_count,
            "end_ts": self.end_ts,
            "missing_interval_count": self.missing_interval_count,
            "row_count": self.row_count,
            "start_ts": self.start_ts,
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "validation_status": self.validation_status,
        }


@dataclass(frozen=True)
class CandleReplay:
    """Validated replay rows plus metadata and diagnostic errors."""

    rows: tuple[CandleReplayRow, ...]
    metadata: CandleReplayMetadata
    errors: tuple[str, ...] = ()

    def iter_rows(self) -> tuple[CandleReplayRow, ...]:
        """Return rows in the original strictly increasing timestamp order."""

        if self.metadata.validation_status != "VALID":
            raise CandleReplayError("cannot replay invalid candle data")
        return self.rows


def build_candle_replay(
    rows: Iterable[Mapping[str, Any]],
    *,
    symbol: str | None = None,
    timeframe: str | None = None,
    allow_read_only_diagnostics: bool = False,
) -> CandleReplay:
    """Validate and package deterministic replay rows.

    Invalid input fails closed by default. When read-only diagnostics are
    explicitly enabled, invalid metadata is returned without approving replay.
    """

    normalized: list[CandleReplayRow] = []
    errors: list[str] = []
    duplicate_count = 0
    missing_interval_count = 0
    previous_open: datetime | None = None
    seen_open_times: set[str] = set()
    expected_delta: timedelta | None = None
    expected_symbol = symbol.strip() if symbol else None
    expected_timeframe = timeframe.strip() if timeframe else None

    for index, raw in enumerate(rows):
        try:
            row = _normalize_row(
                raw,
                index=index,
                expected_symbol=expected_symbol,
                expected_timeframe=expected_timeframe,
            )
        except CandleReplayError as exc:
            errors.append(str(exc))
            continue

        opened_at = _parse_utc_timestamp("open_time", row.open_time)
        if expected_delta is None:
            expected_delta = _timeframe_delta(row.timeframe)
        elif expected_delta != _timeframe_delta(row.timeframe):
            errors.append(f"row {index}: timeframe interval changed")

        if row.open_time in seen_open_times:
            duplicate_count += 1
            errors.append(f"row {index}: duplicate candle open_time")
        seen_open_times.add(row.open_time)

        if previous_open is not None:
            if opened_at <= previous_open:
                errors.append(f"row {index}: open_time is not strictly increasing")
            elif expected_delta is not None:
                missing = int((opened_at - previous_open) / expected_delta) - 1
                if missing > 0:
                    missing_interval_count += missing
                    errors.append(
                        f"row {index}: {missing} missing candle interval(s)"
                    )
        previous_open = opened_at
        normalized.append(row)

    if not normalized:
        errors.append("at least one candle row is required")

    status = "VALID" if not errors else "INVALID"
    metadata = _metadata_for(
        rows=tuple(normalized),
        duplicate_count=duplicate_count,
        missing_interval_count=missing_interval_count,
        validation_status=status,
        fallback_symbol=expected_symbol or "UNAVAILABLE",
        fallback_timeframe=expected_timeframe or "UNAVAILABLE",
    )
    replay = CandleReplay(
        rows=tuple(normalized),
        metadata=metadata,
        errors=tuple(errors),
    )
    if errors and not allow_read_only_diagnostics:
        raise CandleReplayError("; ".join(errors))
    return replay


def candle_replay_metadata_json(metadata: CandleReplayMetadata) -> str:
    """Serialize replay metadata deterministically."""

    return dumps(metadata.payload(), sort_keys=True, separators=(",", ":"))


def candle_replay_rows_json(rows: Iterable[CandleReplayRow]) -> str:
    """Serialize replay rows deterministically."""

    return dumps(
        [row.payload() for row in rows],
        sort_keys=True,
        separators=(",", ":"),
    )


def _metadata_for(
    *,
    rows: tuple[CandleReplayRow, ...],
    duplicate_count: int,
    missing_interval_count: int,
    validation_status: str,
    fallback_symbol: str,
    fallback_timeframe: str,
) -> CandleReplayMetadata:
    row_payload = candle_replay_rows_json(rows)
    dataset_fingerprint = sha256(row_payload.encode("utf-8")).hexdigest()
    symbol = rows[0].symbol if rows else fallback_symbol
    timeframe = rows[0].timeframe if rows else fallback_timeframe
    start_ts = rows[0].open_time if rows else "UNAVAILABLE"
    end_ts = rows[-1].open_time if rows else "UNAVAILABLE"
    base_payload = {
        "dataset_fingerprint": dataset_fingerprint,
        "duplicate_count": duplicate_count,
        "end_ts": end_ts,
        "missing_interval_count": missing_interval_count,
        "row_count": len(rows),
        "start_ts": start_ts,
        "symbol": symbol,
        "timeframe": timeframe,
        "validation_status": validation_status,
    }
    deterministic_hash = sha256(
        dumps(base_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return CandleReplayMetadata(
        dataset_fingerprint=dataset_fingerprint,
        symbol=symbol,
        timeframe=timeframe,
        start_ts=start_ts,
        end_ts=end_ts,
        row_count=len(rows),
        missing_interval_count=missing_interval_count,
        duplicate_count=duplicate_count,
        validation_status=validation_status,
        deterministic_hash=deterministic_hash,
    )


def _normalize_row(
    row: Mapping[str, Any],
    *,
    index: int,
    expected_symbol: str | None,
    expected_timeframe: str | None,
) -> CandleReplayRow:
    symbol = _required_text(row, "symbol", index)
    timeframe = _required_text(row, "timeframe", index)
    open_time = _required_text(row, "open_time", index)
    _parse_utc_timestamp("open_time", open_time)
    if expected_symbol is not None and symbol != expected_symbol:
        raise CandleReplayError(f"row {index}: symbol mismatch")
    if expected_timeframe is not None and timeframe != expected_timeframe:
        raise CandleReplayError(f"row {index}: timeframe mismatch")
    _timeframe_delta(timeframe)
    opened = _decimal(row, "open", index)
    high = _decimal(row, "high", index)
    low = _decimal(row, "low", index)
    close = _decimal(row, "close", index)
    volume = _decimal(row, "volume", index)
    for name, value in (
        ("open", opened),
        ("high", high),
        ("low", low),
        ("close", close),
    ):
        if value <= 0:
            raise CandleReplayError(f"row {index}: {name} must be positive")
    if volume < 0:
        raise CandleReplayError(f"row {index}: volume cannot be negative")
    if high < max(opened, close) or low > min(opened, close) or high < low:
        raise CandleReplayError(f"row {index}: malformed OHLC bounds")
    return CandleReplayRow(
        symbol=symbol,
        timeframe=timeframe,
        open_time=open_time,
        open=opened,
        high=high,
        low=low,
        close=close,
        volume=volume,
    )


def _required_text(row: Mapping[str, Any], name: str, index: int) -> str:
    value = row.get(name)
    if not isinstance(value, str) or not value.strip():
        raise CandleReplayError(f"row {index}: {name} is required")
    return value.strip()


def _decimal(row: Mapping[str, Any], name: str, index: int) -> Decimal:
    value = row.get(name)
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise CandleReplayError(f"row {index}: {name} must be numeric") from exc
    if not parsed.is_finite():
        raise CandleReplayError(f"row {index}: {name} must be finite")
    return parsed


def _parse_utc_timestamp(name: str, value: str) -> datetime:
    if not value.endswith("Z"):
        raise CandleReplayError(f"{name} must be UTC and end with 'Z'")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise CandleReplayError(f"{name} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo != UTC:
        raise CandleReplayError(f"{name} must use UTC timezone")
    return parsed


def _timeframe_delta(timeframe: str) -> timedelta:
    match = fullmatch(r"([1-9][0-9]*)([mhd])", timeframe)
    if match is None:
        raise CandleReplayError("timeframe must use positive m/h/d notation")
    amount = int(match.group(1))
    unit = match.group(2)
    if unit == "m":
        return timedelta(minutes=amount)
    if unit == "h":
        return timedelta(hours=amount)
    return timedelta(days=amount)


def _decimal_text(value: Decimal) -> str:
    return format(value.normalize(), "f")
