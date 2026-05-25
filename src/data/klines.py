"""Validated historical Binance Futures kline ingestion boundary.

This module validates user-supplied or separately fetched historical kline rows.
It performs no network requests, persistence, signal generation, or execution.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation


class DataValidationError(ValueError):
    """Raised when historical market data cannot be trusted for research use."""


@dataclass(frozen=True)
class DatasetProvenance:
    """Declared origin and retrieval metadata accompanying raw historical rows."""

    source: str
    symbol: str
    timeframe: str
    fetched_at_utc: str
    request_parameters: Mapping[str, str]
    schema_version: int = 1

    def validate(self) -> None:
        """Fail closed when required provenance metadata is missing or ambiguous."""

        for label, value in (
            ("source", self.source),
            ("symbol", self.symbol),
            ("timeframe", self.timeframe),
        ):
            if not value.strip():
                raise DataValidationError(f"Provenance field '{label}' is required.")
        if self.schema_version < 1:
            raise DataValidationError("Provenance schema_version must be positive.")
        try:
            fetched_at = datetime.fromisoformat(
                self.fetched_at_utc.replace("Z", "+00:00")
            )
        except ValueError as exc:
            raise DataValidationError(
                "Provenance fetched_at_utc must be an ISO-8601 timestamp."
            ) from exc
        if fetched_at.tzinfo is None or fetched_at.utcoffset() != UTC.utcoffset(None):
            raise DataValidationError("Provenance fetched_at_utc must use UTC.")


@dataclass(frozen=True)
class Kline:
    """Normalized representation of one Binance kline row."""

    open_time_ms: int
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    close_price: Decimal
    volume: Decimal
    close_time_ms: int
    quote_asset_volume: Decimal
    trade_count: int
    taker_buy_base_volume: Decimal
    taker_buy_quote_volume: Decimal
    ignored_value: str

    def canonical_record(self) -> list[str | int]:
        """Return a stable serialization form for reproducible dataset hashing."""

        return [
            self.open_time_ms,
            str(self.open_price),
            str(self.high_price),
            str(self.low_price),
            str(self.close_price),
            str(self.volume),
            self.close_time_ms,
            str(self.quote_asset_volume),
            self.trade_count,
            str(self.taker_buy_base_volume),
            str(self.taker_buy_quote_volume),
            self.ignored_value,
        ]


@dataclass(frozen=True)
class ValidatedKlineDataset:
    """Historical rows accepted after local integrity validation only."""

    provenance: DatasetProvenance
    interval_ms: int
    rows: tuple[Kline, ...]
    dataset_sha256: str
    evidence_classification: str = "MEASURED"

    @property
    def row_count(self) -> int:
        """Number of locally validated historical records."""

        return len(self.rows)


def _decimal(value: object, field_name: str) -> Decimal:
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise DataValidationError(f"Invalid decimal value for '{field_name}'.") from exc
    if not parsed.is_finite():
        raise DataValidationError(f"Non-finite value for '{field_name}' is prohibited.")
    return parsed


def _integer(value: object, field_name: str) -> int:
    try:
        rendered = str(value)
        if rendered.strip() != rendered or any(
            mark in rendered for mark in (".", "e", "E")
        ):
            raise ValueError
        return int(rendered)
    except (TypeError, ValueError) as exc:
        raise DataValidationError(f"Invalid integer value for '{field_name}'.") from exc


def _parse_row(raw_row: Sequence[object]) -> Kline:
    if len(raw_row) != 12:
        raise DataValidationError(
            "Each Binance kline row must contain exactly 12 fields."
        )
    row = Kline(
        open_time_ms=_integer(raw_row[0], "open_time_ms"),
        open_price=_decimal(raw_row[1], "open_price"),
        high_price=_decimal(raw_row[2], "high_price"),
        low_price=_decimal(raw_row[3], "low_price"),
        close_price=_decimal(raw_row[4], "close_price"),
        volume=_decimal(raw_row[5], "volume"),
        close_time_ms=_integer(raw_row[6], "close_time_ms"),
        quote_asset_volume=_decimal(raw_row[7], "quote_asset_volume"),
        trade_count=_integer(raw_row[8], "trade_count"),
        taker_buy_base_volume=_decimal(raw_row[9], "taker_buy_base_volume"),
        taker_buy_quote_volume=_decimal(raw_row[10], "taker_buy_quote_volume"),
        ignored_value=str(raw_row[11]),
    )
    if row.open_time_ms < 0 or row.close_time_ms < 0:
        raise DataValidationError("Kline timestamps must be non-negative milliseconds.")
    if row.high_price < row.low_price:
        raise DataValidationError("Kline high_price cannot be below low_price.")
    if not row.low_price <= row.open_price <= row.high_price:
        raise DataValidationError("Kline open_price is outside its high-low range.")
    if not row.low_price <= row.close_price <= row.high_price:
        raise DataValidationError("Kline close_price is outside its high-low range.")
    if any(
        amount < 0
        for amount in (
            row.volume,
            row.quote_asset_volume,
            row.taker_buy_base_volume,
            row.taker_buy_quote_volume,
        )
    ):
        raise DataValidationError("Kline volume fields cannot be negative.")
    if row.trade_count < 0:
        raise DataValidationError("Kline trade_count cannot be negative.")
    return row


def validate_historical_klines(
    raw_rows: Sequence[Sequence[object]],
    *,
    provenance: DatasetProvenance,
    interval_ms: int,
) -> ValidatedKlineDataset:
    """Validate fixed-interval historical klines and produce a content hash.

    The result proves only local structural and continuity validation of the supplied
    rows. It does not prove exchange authenticity, data completeness outside the
    supplied time range, liquidity, fill quality, or trading performance.
    """

    provenance.validate()
    if interval_ms <= 0:
        raise DataValidationError("interval_ms must be positive.")
    if not raw_rows:
        raise DataValidationError("Historical kline dataset must not be empty.")

    rows = tuple(_parse_row(raw_row) for raw_row in raw_rows)
    for index, row in enumerate(rows):
        if row.open_time_ms % interval_ms != 0:
            raise DataValidationError("Kline open_time_ms is not interval aligned.")
        if row.close_time_ms != row.open_time_ms + interval_ms - 1:
            raise DataValidationError(
                "Kline close_time_ms does not match its interval."
            )
        if index == 0:
            continue
        prior = rows[index - 1]
        if row.open_time_ms == prior.open_time_ms:
            raise DataValidationError("Duplicate kline open timestamp detected.")
        if row.open_time_ms < prior.open_time_ms:
            raise DataValidationError("Kline timestamps must be strictly increasing.")
        if row.open_time_ms != prior.open_time_ms + interval_ms:
            raise DataValidationError(
                "Missing candle gap detected in historical dataset."
            )

    hash_payload = {
        "schema_version": provenance.schema_version,
        "source": provenance.source,
        "symbol": provenance.symbol,
        "timeframe": provenance.timeframe,
        "request_parameters": dict(sorted(provenance.request_parameters.items())),
        "interval_ms": interval_ms,
        "rows": [row.canonical_record() for row in rows],
    }
    encoded = json.dumps(hash_payload, sort_keys=True, separators=(",", ":")).encode()
    return ValidatedKlineDataset(
        provenance=provenance,
        interval_ms=interval_ms,
        rows=rows,
        dataset_sha256=hashlib.sha256(encoded).hexdigest(),
    )
