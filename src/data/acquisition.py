"""Read-only public historical-kline acquisition and immutable artifact evidence.

This boundary can read public Binance Futures kline data only. It contains no
credential support, order endpoint, signal logic, or execution capability.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Protocol, cast
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from src.data.klines import (
    DatasetProvenance,
    DataValidationError,
    ValidatedKlineDataset,
    validate_historical_klines,
)

PUBLIC_KLINES_URL = "https://fapi.binance.com/fapi/v1/klines"
SOURCE_NAME = "BINANCE_FUTURES_PUBLIC_REST"
_FIXED_INTERVALS_MS = {
    "1m": 60_000,
    "3m": 180_000,
    "5m": 300_000,
    "15m": 900_000,
    "30m": 1_800_000,
    "1h": 3_600_000,
    "2h": 7_200_000,
    "4h": 14_400_000,
    "6h": 21_600_000,
    "8h": 28_800_000,
    "12h": 43_200_000,
    "1d": 86_400_000,
}
_SYMBOL_PATTERN = re.compile(r"^[A-Z0-9]{5,20}$")


class AcquisitionError(DataValidationError):
    """Raised when a read-only acquisition cannot establish usable evidence."""


class ArtifactIntegrityError(DataValidationError):
    """Raised when an immutable artifact is missing, stale, or altered."""


@dataclass(frozen=True)
class HistoricalKlineRequest:
    """Validated fixed-interval public historical acquisition selector."""

    symbol: str
    timeframe: str
    start_time_ms: int
    end_time_ms: int
    page_limit: int = 1000

    @property
    def interval_ms(self) -> int:
        """Return the validated fixed interval in milliseconds."""

        try:
            return _FIXED_INTERVALS_MS[self.timeframe]
        except KeyError as exc:
            raise AcquisitionError(
                "Unsupported fixed Binance kline timeframe."
            ) from exc

    def validate(self) -> None:
        """Reject ambiguous, unsafe, or non-deterministic acquisition requests."""

        if (
            not _SYMBOL_PATTERN.fullmatch(self.symbol)
            or self.symbol != self.symbol.upper()
        ):
            raise AcquisitionError(
                "Symbol must be uppercase alphanumeric Binance notation."
            )
        interval_ms = self.interval_ms
        if self.start_time_ms < 0 or self.end_time_ms <= self.start_time_ms:
            raise AcquisitionError("Request time range must be positive and non-empty.")
        if self.start_time_ms % interval_ms or self.end_time_ms % interval_ms:
            raise AcquisitionError(
                "Request boundaries must align to timeframe intervals."
            )
        if not 1 <= self.page_limit <= 1500:
            raise AcquisitionError("page_limit must be between 1 and 1500.")

    def provenance_parameters(self) -> dict[str, str]:
        """Canonical selector persisted as provenance for readback checks."""

        return {
            "endpoint": PUBLIC_KLINES_URL,
            "symbol": self.symbol,
            "interval": self.timeframe,
            "startTime": str(self.start_time_ms),
            "endTimeExclusive": str(self.end_time_ms),
            "limit": str(self.page_limit),
        }


@dataclass(frozen=True)
class AcquisitionPolicy:
    """Bounded network behavior constraints."""

    max_pages: int = 1000
    max_retries: int = 2
    retry_backoff_seconds: float = 0.25
    request_timeout_seconds: float = 10.0

    def validate(self) -> None:
        if self.max_pages < 1 or self.max_retries < 0:
            raise AcquisitionError(
                "Acquisition limits must be non-negative and bounded."
            )
        if self.retry_backoff_seconds < 0 or self.request_timeout_seconds <= 0:
            raise AcquisitionError("Network timing policy is invalid.")


@dataclass(frozen=True)
class FetchResponse:
    """One transport response captured for deterministic acquisition handling."""

    status_code: int
    payload: object
    headers: Mapping[str, str]


class KlineTransport(Protocol):
    """Injected read-only transport contract used for tests and public fetches."""

    def fetch(self, params: Mapping[str, str], timeout_seconds: float) -> FetchResponse:
        """Retrieve one public kline page without credentials or state mutation."""


class PublicBinanceFuturesTransport:
    """Credential-free GET transport for the public Binance Futures kline endpoint."""

    def fetch(self, params: Mapping[str, str], timeout_seconds: float) -> FetchResponse:
        query = urlencode(dict(params))
        request = Request(
            f"{PUBLIC_KLINES_URL}?{query}",
            method="GET",
            headers={
                "Accept": "application/json",
                "User-Agent": "aethelgard-research/0.3",
            },
        )
        try:
            with urlopen(request, timeout=timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
                headers = {key: value for key, value in response.headers.items()}
                return FetchResponse(response.status, payload, headers)
        except HTTPError as exc:
            try:
                payload = json.loads(exc.read().decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                payload = None
            return FetchResponse(exc.code, payload, dict(exc.headers.items()))
        except URLError as exc:
            raise AcquisitionError(
                "Public kline request failed without response evidence."
            ) from exc


@dataclass(frozen=True)
class AcquisitionDiagnostics:
    """Measured request behavior, not market authenticity or completeness proof."""

    pages_fetched: int
    attempts: int
    retries: int
    response_status_codes: tuple[int, ...]


@dataclass(frozen=True)
class PersistedArtifact:
    """Paths and checksums for one immutable locally written acquisition artifact."""

    data_path: Path
    metadata_path: Path
    artifact_sha256: str
    dataset_sha256: str
    metadata_sha256: str


@dataclass(frozen=True)
class AcquisitionResult:
    """Validated acquired rows plus persisted evidence and diagnostics."""

    dataset: ValidatedKlineDataset
    diagnostics: AcquisitionDiagnostics
    artifact: PersistedArtifact


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _iso_utc(moment: datetime) -> str:
    if moment.tzinfo is None or moment.utcoffset() != UTC.utcoffset(None):
        raise AcquisitionError("Acquisition clock must supply a UTC datetime.")
    return moment.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _rows_payload(payload: object) -> list[list[object]]:
    if not isinstance(payload, list):
        raise AcquisitionError("Public kline response payload must be a row list.")
    rows: list[list[object]] = []
    for raw_row in payload:
        if not isinstance(raw_row, list):
            raise AcquisitionError("Public kline response contains a non-row value.")
        rows.append(cast(list[object], raw_row))
    return rows


def _bounded_retry_delay(
    headers: Mapping[str, str], policy: AcquisitionPolicy
) -> float:
    raw = headers.get("Retry-After")
    if raw is None:
        return policy.retry_backoff_seconds
    try:
        stated = float(raw)
    except ValueError:
        return policy.retry_backoff_seconds
    return max(0.0, min(stated, 60.0))


def _page_params(request: HistoricalKlineRequest, cursor: int) -> dict[str, str]:
    return {
        "symbol": request.symbol,
        "interval": request.timeframe,
        "startTime": str(cursor),
        "endTime": str(request.end_time_ms - 1),
        "limit": str(request.page_limit),
    }


def acquire_historical_klines(
    request: HistoricalKlineRequest,
    *,
    output_directory: Path,
    transport: KlineTransport | None = None,
    policy: AcquisitionPolicy | None = None,
    clock: Callable[[], datetime] = _utc_now,
    sleeper: Callable[[float], None] = time.sleep,
) -> AcquisitionResult:
    """Acquire complete fixed-range public klines and persist immutable evidence.

    This proves local validation of captured public-response content and request
    behavior only. It does not establish exchange authenticity or trading fitness.
    """

    request.validate()
    active_policy = policy or AcquisitionPolicy()
    active_policy.validate()
    reader = transport or PublicBinanceFuturesTransport()
    raw_rows: list[list[object]] = []
    cursor = request.start_time_ms
    attempts = 0
    retries = 0
    pages = 0
    statuses: list[int] = []

    while cursor < request.end_time_ms:
        if pages >= active_policy.max_pages:
            raise AcquisitionError("Acquisition exceeded bounded page limit.")
        attempt_for_page = 0
        while True:
            response = reader.fetch(
                _page_params(request, cursor), active_policy.request_timeout_seconds
            )
            attempts += 1
            statuses.append(response.status_code)
            if response.status_code == 200:
                break
            if response.status_code not in {429, 500, 502, 503, 504}:
                raise AcquisitionError(
                    "Public kline request returned a non-retryable status."
                )
            if attempt_for_page >= active_policy.max_retries:
                raise AcquisitionError(
                    "Public kline request exhausted bounded retries."
                )
            sleeper(_bounded_retry_delay(response.headers, active_policy))
            retries += 1
            attempt_for_page += 1

        page_rows = _rows_payload(response.payload)
        if not page_rows:
            raise AcquisitionError(
                "Public kline response ended before the requested range."
            )
        raw_rows.extend(page_rows)
        pages += 1
        try:
            next_cursor = int(str(page_rows[-1][0])) + request.interval_ms
        except (IndexError, ValueError) as exc:
            raise AcquisitionError(
                "Public kline page lacks a valid cursor timestamp."
            ) from exc
        if next_cursor <= cursor:
            raise AcquisitionError("Public kline pagination did not advance.")
        cursor = next_cursor

    fetched_at = _iso_utc(clock())
    provenance = DatasetProvenance(
        source=SOURCE_NAME,
        symbol=request.symbol,
        timeframe=request.timeframe,
        fetched_at_utc=fetched_at,
        request_parameters=request.provenance_parameters(),
    )
    dataset = validate_historical_klines(
        raw_rows, provenance=provenance, interval_ms=request.interval_ms
    )
    if dataset.rows[0].open_time_ms != request.start_time_ms:
        raise AcquisitionError(
            "Acquired dataset does not begin at the requested boundary."
        )
    if dataset.rows[-1].open_time_ms + request.interval_ms != request.end_time_ms:
        raise AcquisitionError(
            "Acquired dataset does not end at the requested boundary."
        )
    diagnostics = AcquisitionDiagnostics(
        pages_fetched=pages,
        attempts=attempts,
        retries=retries,
        response_status_codes=tuple(statuses),
    )
    artifact = persist_immutable_dataset(dataset, output_directory, diagnostics)
    return AcquisitionResult(
        dataset=dataset, diagnostics=diagnostics, artifact=artifact
    )


def _dataset_payload(dataset: ValidatedKlineDataset) -> dict[str, object]:
    return {
        "schema_version": dataset.provenance.schema_version,
        "evidence_classification": dataset.evidence_classification,
        "provenance": {
            "source": dataset.provenance.source,
            "symbol": dataset.provenance.symbol,
            "timeframe": dataset.provenance.timeframe,
            "fetched_at_utc": dataset.provenance.fetched_at_utc,
            "request_parameters": dict(
                sorted(dataset.provenance.request_parameters.items())
            ),
        },
        "interval_ms": dataset.interval_ms,
        "dataset_sha256": dataset.dataset_sha256,
        "rows": [row.canonical_record() for row in dataset.rows],
    }


def persist_immutable_dataset(
    dataset: ValidatedKlineDataset,
    output_directory: Path,
    diagnostics: AcquisitionDiagnostics,
) -> PersistedArtifact:
    """Write raw validated content and checksum metadata without overwrite paths."""

    output_directory.mkdir(parents=True, exist_ok=True)
    payload_bytes = json.dumps(
        _dataset_payload(dataset), sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    artifact_sha256 = hashlib.sha256(payload_bytes).hexdigest()
    data_path = output_directory / f"{artifact_sha256}.json"
    metadata_path = output_directory / f"{artifact_sha256}.metadata.json"
    metadata = {
        "artifact_sha256": artifact_sha256,
        "dataset_sha256": dataset.dataset_sha256,
        "data_filename": data_path.name,
        "evidence_classification": "MEASURED",
        "claim_limit": "LOCAL_CAPTURE_INTEGRITY_ONLY",
        "fetch_metadata": {
            "pages_fetched": diagnostics.pages_fetched,
            "attempts": diagnostics.attempts,
            "retries": diagnostics.retries,
            "response_status_codes": list(diagnostics.response_status_codes),
        },
    }
    metadata_bytes = json.dumps(metadata, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
    metadata_sha256 = hashlib.sha256(metadata_bytes).hexdigest()
    for path, content in ((data_path, payload_bytes), (metadata_path, metadata_bytes)):
        try:
            with path.open("xb") as stream:
                stream.write(content)
        except FileExistsError:
            if path.read_bytes() != content:
                raise ArtifactIntegrityError(
                    "Immutable artifact path contains altered bytes."
                ) from None
    return PersistedArtifact(
        data_path,
        metadata_path,
        artifact_sha256,
        dataset.dataset_sha256,
        metadata_sha256,
    )


def load_immutable_dataset(
    artifact: PersistedArtifact,
    *,
    now: datetime,
    max_age: timedelta,
) -> ValidatedKlineDataset:
    """Verify checksums, selector consistency, and acquisition evidence freshness."""

    if max_age <= timedelta(0):
        raise ArtifactIntegrityError("max_age must be positive.")
    try:
        payload_bytes = artifact.data_path.read_bytes()
        metadata_bytes = artifact.metadata_path.read_bytes()
        metadata = json.loads(metadata_bytes.decode("utf-8"))
        payload = json.loads(payload_bytes.decode("utf-8"))
    except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ArtifactIntegrityError(
            "Immutable artifact evidence is missing or unreadable."
        ) from exc
    if hashlib.sha256(payload_bytes).hexdigest() != artifact.artifact_sha256:
        raise ArtifactIntegrityError("Immutable artifact checksum mismatch.")
    if hashlib.sha256(metadata_bytes).hexdigest() != artifact.metadata_sha256:
        raise ArtifactIntegrityError("Immutable metadata checksum mismatch.")
    if (
        not isinstance(metadata, dict)
        or metadata.get("artifact_sha256") != artifact.artifact_sha256
    ):
        raise ArtifactIntegrityError("Immutable metadata checksum reference mismatch.")
    if (
        not isinstance(payload, dict)
        or payload.get("dataset_sha256") != artifact.dataset_sha256
    ):
        raise ArtifactIntegrityError("Immutable dataset checksum reference mismatch.")
    provenance_raw = payload.get("provenance")
    rows_raw = payload.get("rows")
    if not isinstance(provenance_raw, dict) or not isinstance(rows_raw, list):
        raise ArtifactIntegrityError(
            "Immutable artifact payload has invalid structure."
        )
    params = provenance_raw.get("request_parameters")
    if not isinstance(params, dict) or not all(
        isinstance(key, str) and isinstance(value, str) for key, value in params.items()
    ):
        raise ArtifactIntegrityError(
            "Immutable artifact provenance parameters are invalid."
        )
    provenance = DatasetProvenance(
        source=str(provenance_raw.get("source", "")),
        symbol=str(provenance_raw.get("symbol", "")),
        timeframe=str(provenance_raw.get("timeframe", "")),
        fetched_at_utc=str(provenance_raw.get("fetched_at_utc", "")),
        request_parameters=cast(dict[str, str], params),
        schema_version=int(payload.get("schema_version", 0)),
    )
    if provenance.source != SOURCE_NAME or params.get("endpoint") != PUBLIC_KLINES_URL:
        raise ArtifactIntegrityError(
            "Immutable artifact source is not the public acquisition boundary."
        )
    dataset = validate_historical_klines(
        cast(list[list[object]], rows_raw),
        provenance=provenance,
        interval_ms=int(payload.get("interval_ms", 0)),
    )
    if dataset.dataset_sha256 != artifact.dataset_sha256:
        raise ArtifactIntegrityError(
            "Immutable artifact dataset validation hash mismatch."
        )
    if now.tzinfo is None or now.utcoffset() != UTC.utcoffset(None):
        raise ArtifactIntegrityError("Freshness comparison requires a UTC datetime.")
    fetched_at = datetime.fromisoformat(
        provenance.fetched_at_utc.replace("Z", "+00:00")
    )
    if now - fetched_at > max_age or fetched_at > now + timedelta(seconds=5):
        raise ArtifactIntegrityError(
            "Immutable acquisition evidence is stale or future-dated."
        )
    return dataset
