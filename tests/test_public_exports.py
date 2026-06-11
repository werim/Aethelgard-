PUBLIC_EXPORT_MODULES = (
    "src.backtest",
    "src.data",
    "src.execution",
    "src.reporting",
)

FORBIDDEN_DIRECT_EXPORTS = {
    "alpha",
    "drawdown",
    "expectancy",
    "live",
    "order",
    "optimizer",
    "pnl",
    "position",
    "profit",
    "profitability",
    "readiness",
    "returns",
    "sharpe",
    "trade",
    "win_rate",
}


def test_public_exports_are_declared_attributes() -> None:
    for module_name in PUBLIC_EXPORT_MODULES:
        module = __import__(module_name, fromlist=["__all__"])

        for exported_name in module.__all__:
            assert hasattr(module, exported_name), (module_name, exported_name)


def test_public_exports_do_not_expose_unsafe_direct_names() -> None:
    for module_name in PUBLIC_EXPORT_MODULES:
        module = __import__(module_name, fromlist=["__all__"])
        normalized_exports = {exported_name.lower() for exported_name in module.__all__}

        assert FORBIDDEN_DIRECT_EXPORTS.isdisjoint(normalized_exports), module_name
