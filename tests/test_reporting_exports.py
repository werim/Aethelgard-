import src.reporting as reporting


def test_reporting_exports_do_not_expose_metric_or_readiness_fields() -> None:
    exported_names = set(reporting.__all__)
    forbidden_exports = {
        "alpha",
        "balance",
        "drawdown",
        "equity",
        "expectancy",
        "loss",
        "pnl",
        "profit",
        "profitability",
        "readiness",
        "returns",
        "sharpe",
        "win_rate",
    }

    assert forbidden_exports.isdisjoint(exported_names)


def test_reporting_exports_keep_guarded_metric_boundary_visible() -> None:
    exported_names = set(reporting.__all__)

    assert "evaluate_metric_publication_eligibility" in exported_names
    assert "guarded_performance_report_payload" in exported_names
    assert "guarded_performance_report_json" in exported_names
    assert "metric_publication_eligibility_json" in exported_names
