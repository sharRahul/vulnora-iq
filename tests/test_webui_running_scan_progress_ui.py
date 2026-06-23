from __future__ import annotations

from pathlib import Path

INDEX = Path("webui/static/index.html")
APP = Path("webui/static/app.js")
BASE_CSS = Path("webui/static/styles.css")
SCAN_PROGRESS_CSS = Path("webui/static/scan-progress.css")
UI_POLISH_CSS = Path("webui/static/ui-polish.css")


def test_running_scan_progress_panel_is_present() -> None:
    html = INDEX.read_text(encoding="utf-8")

    for expected in (
        "active-scan-card",
        "active-scan-title",
        "active-scan-detail",
        "active-scan-percent",
        "progress-bar",
        "active-scan-target",
        "active-scan-profile",
        "active-scan-stage",
        "active-scan-updated",
        "active-scan-message",
    ):
        assert expected in html

    assert "/static/scan-progress.css" in html


def test_full_webui_filter_controls_are_present() -> None:
    html = INDEX.read_text(encoding="utf-8")

    for expected in (
        "catalog-search",
        "catalog-category-filter",
        "catalog-mode-filter",
        "catalog-count",
        "run-readiness",
        "readiness-target",
        "readiness-profile",
        "readiness-modules",
        "readiness-authorisation",
        "top-risks-list",
        "copy-summary",
        "finding-severity-filter",
        "finding-policy-filter",
        "findings-count",
        "history-summary",
        "history-search",
        "history-status-filter",
        "grouped-artifacts",
        "/static/ui-polish.css",
    ):
        assert expected in html


def test_running_scan_progress_javascript_updates_live_details() -> None:
    script = APP.read_text(encoding="utf-8")

    for expected in (
        "function renderActiveScan",
        "function updateActiveScanFromJob",
        "active-scan-card",
        "active-scan-target",
        "active-scan-profile",
        "active-scan-stage",
        "active-scan-updated",
        "active-scan-message",
        "progress-bar",
        "Scan completed. Dashboard and report outputs are ready.",
    ):
        assert expected in script


def test_full_webui_javascript_filters_and_dashboard_actions_exist() -> None:
    script = APP.read_text(encoding="utf-8")

    for expected in (
        "function renderCatalogFilters",
        "function filteredProfileEntries",
        "function renderRunReadiness",
        "function renderHistorySummary",
        "function filteredJobs",
        "function renderJobHistory",
        "function findingPolicyStatus",
        "function filteredFindings",
        "function renderTopRisks",
        "function dashboardSummaryText",
        "function copyDashboardSummary",
        "catalogSearch",
        "historyStatus",
        "findingSeverity",
        "findingPolicy",
    ):
        assert expected in script


def test_sophisticated_muted_light_theme_palette_is_present() -> None:
    css = BASE_CSS.read_text(encoding="utf-8")

    for expected in (
        "#F8F9FA",
        "#E8DFE0",
        "#8A9EA7",
        "#8D9B6A",
        "#DAB692",
        "#2A2F35",
        "#1E2229",
        "--critical: #6E1F25",
        "color-scheme: light",
    ):
        assert expected in css


def test_running_scan_progress_css_is_responsive_and_accessible() -> None:
    css = SCAN_PROGRESS_CSS.read_text(encoding="utf-8")

    for expected in (
        ".active-scan-card",
        ".scan-visual",
        ".progress-bar-shell",
        ".scan-stage-grid",
        "@media (max-width: 1100px)",
        "@media (max-width: 760px)",
        "@media (max-width: 520px)",
        "@media (prefers-reduced-motion: reduce)",
        "@keyframes scan-pulse",
        "@keyframes progress-shimmer",
    ):
        assert expected in css


def test_full_webui_responsive_polish_css_exists() -> None:
    css = UI_POLISH_CSS.read_text(encoding="utf-8")

    for expected in (
        ".toolbar",
        ".run-readiness",
        ".readiness-grid",
        ".dashboard-section-header",
        ".top-risks-panel",
        ".enhanced-finding",
        ".finding-meta",
        ".grouped-artifacts",
        ".history-summary",
        "@media (max-width: 1180px)",
        "@media (max-width: 820px)",
        "@media (max-width: 620px)",
    ):
        assert expected in css
