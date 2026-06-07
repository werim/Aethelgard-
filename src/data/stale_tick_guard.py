"""Research-only stale tick guard for market-data quality checks.

The guard rejects stale, impossible, weakly confirmed, or peer-inconsistent ticks
before downstream research code consumes them. It does not create signals, model
fills, run a PAPER loop, or prove execution readiness.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from statistics import median
from time import monotonic, time


class StaleTickReason(StrEnum):
    """Canonical validation reasons emitted by the stale tick guard."""

    PASS = "STALE_TICK_GATE_PASS"
    INVALID_SYMBOL = "INVALID_SYMBOL"
    PRICE_OUT_OF_BOUNDS = "PRICE_OUT_OF_BOUNDS"
    LOCAL_TICK_TOO_OLD = "LOCAL_TICK_TOO_OLD"
    EXCHANGE_TS_IN_FUTURE = "EXCHANGE_TS_IN_FUTURE"
    MISSING_WARMUP_REFERENCE = "MISSING_WARMUP_REFERENCE"
    WARMUP_DELTA_TOO_LARGE = "STALE_TICK_REJECTED_WARMUP_DELTA"
    INSUFFICIENT_PEER_CONFIRMATION = "INSUFFICIENT_PEER_CONFIRMATION"
    PEER_DELTA_TOO_LARGE = "STALE_TICK_REJECTED_PEER_DELTA"
    DUPLICATE_TICK = "DUPLICATE_TICK"


@dataclass(frozen=True)
class MarketTick:
    """A single observed market-data tick from one source connection.

    `exchange_timestamp`, when present, is expected to use wall-clock seconds.
    `observed_monotonic` is intentionally separate for local receive-age checks.
    """

    symbol: str
    price: float
    observed_monotonic: float
    source_id: str
    sequence_id: str | None = None
    exchange_timestamp: float | None = None

    def identity(self) -> tuple[str, str, str | None]:
        """Return the duplicate-detection identity for this tick."""

        return (self.symbol, self.source_id, self.sequence_id)


@dataclass(frozen=True)
class StaleTickGuardConfig:
    """Fail-closed stale tick guard configuration."""

    min_price: float = 0.0
    max_price: float = 1_000_000.0
    max_tick_age_seconds: float = 1.0
    max_exchange_future_skew_seconds: float = 0.5
    max_delta_from_warmup_bps: float = 1200.0
    max_delta_from_peer_median_bps: float = 600.0
    min_peer_confirmations: int = 2
    peer_window_seconds: float = 0.5
    reject_duplicate_sequence_ids: bool = True
    duplicate_cache_size: int = 4096
    require_warmup_reference: bool = True
    require_peer_confirmation: bool = True

    def validate(self) -> None:
        """Reject unsafe or contradictory configuration values."""

        if self.min_price < 0:
            raise ValueError("min_price cannot be negative.")
        if self.max_price <= self.min_price:
            raise ValueError("max_price must be greater than min_price.")
        if self.max_tick_age_seconds <= 0:
            raise ValueError("max_tick_age_seconds must be positive.")
        if self.max_exchange_future_skew_seconds < 0:
            raise ValueError("max_exchange_future_skew_seconds cannot be negative.")
        if self.max_delta_from_warmup_bps <= 0:
            raise ValueError("max_delta_from_warmup_bps must be positive.")
        if self.max_delta_from_peer_median_bps <= 0:
            raise ValueError("max_delta_from_peer_median_bps must be positive.")
        if self.min_peer_confirmations < 0:
            raise ValueError("min_peer_confirmations cannot be negative.")
        if self.peer_window_seconds <= 0:
            raise ValueError("peer_window_seconds must be positive.")
        if self.duplicate_cache_size <= 0:
            raise ValueError("duplicate_cache_size must be positive.")


@dataclass(frozen=True)
class StaleTickDecision:
    """Auditable decision for one observed tick."""

    passed: bool
    reason: StaleTickReason
    tick: MarketTick
    decided_at: float
    diagnostics: dict[str, float | int | str | None] = field(default_factory=dict)

    def to_audit_record(self) -> dict[str, object]:
        """Render a JSON-compatible audit record."""

        return {
            "passed": self.passed,
            "reason": self.reason.value,
            "decided_at": self.decided_at,
            "tick": asdict(self.tick),
            "diagnostics": dict(self.diagnostics),
        }


class TickBuffer:
    """Bounded in-memory buffer used for peer confirmation checks."""

    def __init__(self, maxlen: int = 10_000) -> None:
        if maxlen <= 0:
            raise ValueError("maxlen must be positive.")
        self._ticks: deque[MarketTick] = deque(maxlen=maxlen)

    def add(self, tick: MarketTick) -> None:
        """Add a tick to the bounded buffer."""

        self._ticks.append(tick)

    def recent(
        self,
        *,
        symbol: str,
        center_monotonic: float,
        window_seconds: float,
    ) -> list[MarketTick]:
        """Return ticks for the same symbol around the target receive time."""

        lower = center_monotonic - window_seconds
        upper = center_monotonic + window_seconds
        return [
            tick
            for tick in self._ticks
            if tick.symbol == symbol and lower <= tick.observed_monotonic <= upper
        ]


def relative_delta_bps(value: float, reference: float) -> float:
    """Return absolute relative drift in basis points."""

    if reference <= 0:
        raise ValueError("reference must be positive.")
    return abs(value - reference) / reference * 10_000.0


class StaleTickGuard:
    """Fail-closed market-data tick guard for research ingestion boundaries."""

    def __init__(
        self,
        config: StaleTickGuardConfig | None = None,
        buffer: TickBuffer | None = None,
    ) -> None:
        self.config = config or StaleTickGuardConfig()
        self.config.validate()
        self.buffer = buffer or TickBuffer()
        self.audit_log: list[StaleTickDecision] = []
        self._seen: deque[tuple[str, str, str | None]] = deque(
            maxlen=self.config.duplicate_cache_size
        )
        self._seen_set: set[tuple[str, str, str | None]] = set()

    def validate_tick(
        self,
        tick: MarketTick,
        *,
        warmup_reference_price: float | None,
        now_monotonic: float | None = None,
        wall_clock_now: float | None = None,
        add_to_buffer: bool = True,
    ) -> StaleTickDecision:
        """Validate and audit one tick before downstream research use."""

        decided_at = time() if wall_clock_now is None else wall_clock_now
        observed_now = monotonic() if now_monotonic is None else now_monotonic
        decision = self._validate_inner(
            tick=tick,
            warmup_reference_price=warmup_reference_price,
            now_monotonic=observed_now,
            decided_at=decided_at,
        )
        self.audit_log.append(decision)
        if add_to_buffer:
            self.buffer.add(tick)
        return decision

    def _validate_inner(
        self,
        *,
        tick: MarketTick,
        warmup_reference_price: float | None,
        now_monotonic: float,
        decided_at: float,
    ) -> StaleTickDecision:
        if not tick.symbol.strip():
            return self._reject(tick, StaleTickReason.INVALID_SYMBOL, decided_at, {})

        if tick.price <= self.config.min_price or tick.price > self.config.max_price:
            return self._reject(
                tick,
                StaleTickReason.PRICE_OUT_OF_BOUNDS,
                decided_at,
                {
                    "price": tick.price,
                    "min_price": self.config.min_price,
                    "max_price": self.config.max_price,
                },
            )

        if self.config.reject_duplicate_sequence_ids and tick.sequence_id is not None:
            identity = tick.identity()
            if identity in self._seen_set:
                return self._reject(
                    tick,
                    StaleTickReason.DUPLICATE_TICK,
                    decided_at,
                    {},
                )
            self._remember_identity(identity)

        age_seconds = now_monotonic - tick.observed_monotonic
        if age_seconds > self.config.max_tick_age_seconds:
            return self._reject(
                tick,
                StaleTickReason.LOCAL_TICK_TOO_OLD,
                decided_at,
                {
                    "age_seconds": age_seconds,
                    "max_tick_age_seconds": self.config.max_tick_age_seconds,
                },
            )

        if (
            tick.exchange_timestamp is not None
            and tick.exchange_timestamp
            > decided_at + self.config.max_exchange_future_skew_seconds
        ):
            return self._reject(
                tick,
                StaleTickReason.EXCHANGE_TS_IN_FUTURE,
                decided_at,
                {
                    "exchange_timestamp": tick.exchange_timestamp,
                    "decided_at": decided_at,
                    "max_exchange_future_skew_seconds": (
                        self.config.max_exchange_future_skew_seconds
                    ),
                },
            )

        if warmup_reference_price is None:
            if self.config.require_warmup_reference:
                return self._reject(
                    tick,
                    StaleTickReason.MISSING_WARMUP_REFERENCE,
                    decided_at,
                    {},
                )
        else:
            warmup_delta_bps = relative_delta_bps(tick.price, warmup_reference_price)
            if warmup_delta_bps > self.config.max_delta_from_warmup_bps:
                return self._reject(
                    tick,
                    StaleTickReason.WARMUP_DELTA_TOO_LARGE,
                    decided_at,
                    {
                        "warmup_reference_price": warmup_reference_price,
                        "warmup_delta_bps": warmup_delta_bps,
                        "max_delta_from_warmup_bps": (
                            self.config.max_delta_from_warmup_bps
                        ),
                    },
                )

        peers = self._peer_ticks(tick)
        if (
            self.config.require_peer_confirmation
            and len(peers) < self.config.min_peer_confirmations
        ):
            return self._reject(
                tick,
                StaleTickReason.INSUFFICIENT_PEER_CONFIRMATION,
                decided_at,
                {
                    "peer_count": len(peers),
                    "min_peer_confirmations": self.config.min_peer_confirmations,
                },
            )

        if peers:
            peer_median = float(median(peer.price for peer in peers))
            peer_delta_bps = relative_delta_bps(tick.price, peer_median)
            if peer_delta_bps > self.config.max_delta_from_peer_median_bps:
                return self._reject(
                    tick,
                    StaleTickReason.PEER_DELTA_TOO_LARGE,
                    decided_at,
                    {
                        "peer_median": peer_median,
                        "peer_delta_bps": peer_delta_bps,
                        "max_delta_from_peer_median_bps": (
                            self.config.max_delta_from_peer_median_bps
                        ),
                        "peer_count": len(peers),
                    },
                )

        return StaleTickDecision(
            passed=True,
            reason=StaleTickReason.PASS,
            tick=tick,
            decided_at=decided_at,
            diagnostics={
                "peer_count": len(peers),
                "warmup_reference_price": warmup_reference_price,
            },
        )

    def _peer_ticks(self, tick: MarketTick) -> list[MarketTick]:
        raw_peers = self.buffer.recent(
            symbol=tick.symbol,
            center_monotonic=tick.observed_monotonic,
            window_seconds=self.config.peer_window_seconds,
        )
        return [
            peer
            for peer in raw_peers
            if peer.source_id != tick.source_id
            and (tick.sequence_id is None or peer.sequence_id != tick.sequence_id)
        ]

    def _remember_identity(self, identity: tuple[str, str, str | None]) -> None:
        if len(self._seen) == self._seen.maxlen and self._seen:
            oldest = self._seen.popleft()
            self._seen_set.discard(oldest)
        self._seen.append(identity)
        self._seen_set.add(identity)

    @staticmethod
    def _reject(
        tick: MarketTick,
        reason: StaleTickReason,
        decided_at: float,
        diagnostics: dict[str, float | int | str | None],
    ) -> StaleTickDecision:
        return StaleTickDecision(
            passed=False,
            reason=reason,
            tick=tick,
            decided_at=decided_at,
            diagnostics=diagnostics,
        )


def select_first_valid_tick(
    ticks: Iterable[MarketTick],
    *,
    guard: StaleTickGuard,
    warmup_reference_prices: dict[str, float],
    now_monotonic: float | None = None,
) -> StaleTickDecision | None:
    """Return the first validated tick rather than the first arriving tick."""

    for tick in ticks:
        decision = guard.validate_tick(
            tick,
            warmup_reference_price=warmup_reference_prices.get(tick.symbol),
            now_monotonic=now_monotonic,
        )
        if decision.passed:
            return decision
    return None
