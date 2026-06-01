from src.data.stale_tick_guard import (
    MarketTick,
    StaleTickGuard,
    StaleTickGuardConfig,
    StaleTickReason,
    TickBuffer,
    relative_delta_bps,
    select_first_valid_tick,
)


def make_guard() -> StaleTickGuard:
    config = StaleTickGuardConfig(
        max_tick_age_seconds=1.0,
        max_delta_from_warmup_bps=1200.0,
        max_delta_from_peer_median_bps=600.0,
        min_peer_confirmations=2,
        peer_window_seconds=0.5,
    )
    return StaleTickGuard(config)


def seed_peers(
    guard: StaleTickGuard,
    *,
    symbol: str = "BTCUSDT",
    observed_monotonic: float = 100.0,
    prices: tuple[float, ...] = (50_100.0, 50_200.0),
) -> None:
    for idx, price in enumerate(prices):
        guard.buffer.add(
            MarketTick(
                symbol=symbol,
                price=price,
                observed_monotonic=observed_monotonic,
                source_id=f"peer-{idx}",
                sequence_id=f"peer-{idx}",
            )
        )


def test_passes_with_warmup_and_peer_confirmation() -> None:
    guard = make_guard()
    seed_peers(guard)
    tick = MarketTick("BTCUSDT", 50_150.0, 100.0, "fast-1", "x1")
    decision = guard.validate_tick(
        tick,
        warmup_reference_price=50_000.0,
        now_monotonic=100.2,
        wall_clock_now=1_700_000_000.0,
    )
    assert decision.passed is True
    assert decision.reason == StaleTickReason.PASS
    assert decision.to_audit_record()["reason"] == "STALE_TICK_GATE_PASS"


def test_rejects_invalid_symbol() -> None:
    guard = make_guard()
    seed_peers(guard, symbol="")
    tick = MarketTick("", 50_150.0, 100.0, "fast-1", "x1")
    decision = guard.validate_tick(
        tick, warmup_reference_price=50_000.0, now_monotonic=100.1
    )
    assert decision.passed is False
    assert decision.reason == StaleTickReason.INVALID_SYMBOL


def test_rejects_price_out_of_bounds() -> None:
    guard = make_guard()
    seed_peers(guard)
    tick = MarketTick("BTCUSDT", 0.0, 100.0, "fast-1", "x1")
    decision = guard.validate_tick(
        tick, warmup_reference_price=50_000.0, now_monotonic=100.1
    )
    assert decision.passed is False
    assert decision.reason == StaleTickReason.PRICE_OUT_OF_BOUNDS


def test_rejects_old_local_tick() -> None:
    guard = make_guard()
    seed_peers(guard)
    tick = MarketTick("BTCUSDT", 50_100.0, 98.0, "fast-1", "x1")
    decision = guard.validate_tick(
        tick, warmup_reference_price=50_000.0, now_monotonic=100.1
    )
    assert decision.passed is False
    assert decision.reason == StaleTickReason.LOCAL_TICK_TOO_OLD


def test_rejects_exchange_timestamp_in_future() -> None:
    guard = make_guard()
    seed_peers(guard)
    tick = MarketTick(
        "BTCUSDT",
        50_100.0,
        100.0,
        "fast-1",
        "x1",
        exchange_timestamp=1_700_000_000.7,
    )
    decision = guard.validate_tick(
        tick,
        warmup_reference_price=50_000.0,
        now_monotonic=100.1,
        wall_clock_now=1_700_000_000.0,
    )
    assert decision.passed is False
    assert decision.reason == StaleTickReason.EXCHANGE_TS_IN_FUTURE


def test_rejects_missing_warmup_reference_fail_closed() -> None:
    guard = make_guard()
    seed_peers(guard)
    tick = MarketTick("BTCUSDT", 50_100.0, 100.0, "fast-1", "x1")
    decision = guard.validate_tick(
        tick, warmup_reference_price=None, now_monotonic=100.1
    )
    assert decision.passed is False
    assert decision.reason == StaleTickReason.MISSING_WARMUP_REFERENCE


def test_rejects_warmup_delta() -> None:
    guard = make_guard()
    seed_peers(guard, prices=(60_100.0, 60_200.0))
    tick = MarketTick("BTCUSDT", 60_150.0, 100.0, "fast-1", "x1")
    decision = guard.validate_tick(
        tick, warmup_reference_price=50_000.0, now_monotonic=100.1
    )
    assert decision.passed is False
    assert decision.reason == StaleTickReason.WARMUP_DELTA_TOO_LARGE


def test_rejects_insufficient_peer_confirmation() -> None:
    guard = make_guard()
    guard.buffer.add(MarketTick("BTCUSDT", 50_100.0, 100.0, "peer-1", "p1"))
    tick = MarketTick("BTCUSDT", 50_150.0, 100.0, "fast-1", "x1")
    decision = guard.validate_tick(
        tick, warmup_reference_price=50_000.0, now_monotonic=100.1
    )
    assert decision.passed is False
    assert decision.reason == StaleTickReason.INSUFFICIENT_PEER_CONFIRMATION


def test_rejects_peer_delta() -> None:
    guard = make_guard()
    seed_peers(guard, prices=(50_000.0, 50_100.0))
    tick = MarketTick("BTCUSDT", 54_000.0, 100.0, "fast-1", "x1")
    decision = guard.validate_tick(
        tick, warmup_reference_price=54_000.0, now_monotonic=100.1
    )
    assert decision.passed is False
    assert decision.reason == StaleTickReason.PEER_DELTA_TOO_LARGE


def test_rejects_duplicate_sequence_id() -> None:
    guard = make_guard()
    seed_peers(guard)
    tick = MarketTick("BTCUSDT", 50_150.0, 100.0, "fast-1", "x1")
    first = guard.validate_tick(
        tick, warmup_reference_price=50_000.0, now_monotonic=100.1
    )
    second = guard.validate_tick(
        tick, warmup_reference_price=50_000.0, now_monotonic=100.1
    )
    assert first.passed is True
    assert second.passed is False
    assert second.reason == StaleTickReason.DUPLICATE_TICK


def test_select_first_valid_tick_skips_bad_then_accepts_good() -> None:
    guard = make_guard()
    seed_peers(guard)
    bad = MarketTick("BTCUSDT", 80_000.0, 100.0, "fast-bad", "bad")
    good = MarketTick("BTCUSDT", 50_150.0, 100.0, "fast-good", "good")
    decision = select_first_valid_tick(
        [bad, good],
        guard=guard,
        warmup_reference_prices={"BTCUSDT": 50_000.0},
        now_monotonic=100.1,
    )
    assert decision is not None
    assert decision.tick.source_id == "fast-good"
    assert len(guard.audit_log) == 2


def test_config_validation_rejects_unsafe_values() -> None:
    config = StaleTickGuardConfig(max_tick_age_seconds=0.0)
    try:
        config.validate()
    except ValueError as exc:
        assert "max_tick_age_seconds" in str(exc)
    else:  # pragma: no cover - defensive branch
        raise AssertionError("unsafe config should fail closed")


def test_tick_buffer_requires_positive_length() -> None:
    try:
        TickBuffer(maxlen=0)
    except ValueError as exc:
        assert "maxlen" in str(exc)
    else:  # pragma: no cover - defensive branch
        raise AssertionError("zero-length buffers should fail closed")


def test_relative_delta_requires_positive_reference() -> None:
    try:
        relative_delta_bps(1.0, 0.0)
    except ValueError as exc:
        assert "reference" in str(exc)
    else:  # pragma: no cover - defensive branch
        raise AssertionError("zero reference should fail closed")
