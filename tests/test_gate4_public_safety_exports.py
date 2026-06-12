PUBLIC_EXPORT_MODULES = (
    "src.backtest",
    "src.data",
    "src.execution",
    "src.reporting",
)

UNSAFE_PUBLIC_EXPORT_NAMES = {
    "create_live_order",
    "enable_live_mode",
    "enable_live_trading",
    "live_order",
    "live_runtime",
    "live_trading_enabled",
    "place_live_order",
    "submit_live_order",
}

UNSAFE_PUBLIC_EXPORT_FRAGMENTS = (
    "live_order",
    "live_trading",
    "live_runtime",
)


def exported_names(module_name: str) -> set[str]:
    module = __import__(module_name, fromlist=["__all__"])
    return {name.lower() for name in module.__all__}


def test_gate4_public_exports_do_not_expose_live_order_helpers() -> None:
    for module_name in PUBLIC_EXPORT_MODULES:
        exports = exported_names(module_name)
        assert UNSAFE_PUBLIC_EXPORT_NAMES.isdisjoint(exports), module_name


def test_gate4_public_exports_do_not_expose_live_order_fragments() -> None:
    for module_name in PUBLIC_EXPORT_MODULES:
        exports = exported_names(module_name)
        for exported_name in exports:
            for unsafe_fragment in UNSAFE_PUBLIC_EXPORT_FRAGMENTS:
                assert unsafe_fragment not in exported_name, (
                    module_name,
                    exported_name,
                    unsafe_fragment,
                )
