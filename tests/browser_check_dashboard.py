"""Optional local Chromium checks; run separately from the Pytest unit suite."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.dashboard_pages import PAGES


def main():
    from playwright.sync_api import sync_playwright

    parser = argparse.ArgumentParser()
    parser.add_argument("--browser", default="/usr/bin/chromium")
    parser.add_argument("--url", default="http://127.0.0.1:8501")
    args = parser.parse_args()
    output = Path("work/dashboard-browser")
    output.mkdir(parents=True, exist_ok=True)
    profiles = [("desktop", 1440, 1000, False), ("tablet_landscape", 1280, 800, True),
                ("android_portrait", 800, 1280, True)]
    headings = ["Real estate, with evidence", "Land market records", "Muscat brokerage registrations",
                "Compare places within a period", "Coverage is part of the result", "Every chart has a lineage"]
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=args.browser,
                                              args=["--no-sandbox"], headless=True)
        for profile, width, height, touch in profiles:
            context = browser.new_context(viewport={"width": width, "height": height}, has_touch=touch,
                user_agent=("Mozilla/5.0 (Linux; Android 13; Tablet) AppleWebKit/537.36 "
                            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36") if touch else None)
            page = context.new_page()
            errors = []
            page.on("pageerror", lambda err: errors.append(str(err)))
            page.goto(args.url, wait_until="domcontentloaded")
            page.get_by_text("Real estate, with evidence", exact=True).wait_for(timeout=60000)
            page.get_by_text("Reviewed EDA 168665c92a8a2ff91598", exact=False).wait_for(timeout=60000)
            page.locator('[data-test-script-state="notRunning"]').wait_for(timeout=60000)
            page.get_by_role("button", name="Stop", exact=True).wait_for(state="hidden", timeout=60000)
            for index, (name, label) in enumerate(PAGES.items()):
                if not page.get_by_text(label, exact=True).is_visible():
                    control = page.locator('[data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapsedControl"]')
                    control.first.click()
                page.get_by_text(label, exact=True).click()
                page.get_by_role("heading", name=headings[index], exact=True).wait_for(timeout=60000)
                # The rendered page footer follows the final page output, so wait for
                # Streamlit to finish its rerun before inspecting chart/error elements.
                page.locator('[data-testid="stStatusWidget"]').wait_for(state="hidden", timeout=60000)
                page.get_by_text("Reviewed EDA 168665c92a8a2ff91598", exact=False).wait_for(timeout=60000)
                page.get_by_role("button", name="Stop", exact=True).wait_for(state="hidden", timeout=60000)
                page.locator('[data-test-script-state="notRunning"]').wait_for(timeout=60000)
                page.wait_for_function("document.querySelectorAll('[data-stale=\"true\"]').length === 0", timeout=60000)
                assert page.locator('[data-testid="stException"]').count() == 0, (profile, name)
                assert page.locator('[data-testid="stAlertContainer"] [data-testid="stMarkdownContainer"]').filter(has_text="Data integrity check failed").count() == 0
                assert not errors, errors
                overflow = page.evaluate("document.documentElement.scrollWidth > window.innerWidth + 2")
                assert not overflow, (profile, name, "page-level horizontal overflow")
                main_overflow = page.locator('[data-testid="stMain"]').evaluate("e=>e.scrollWidth > e.clientWidth + 2")
                assert not main_overflow, (profile, name, "main content horizontal overflow")
                if name != "Sources and Methodology":
                    assert page.locator('[data-testid="stPlotlyChart"]').count() > 0, (profile, name)
                    chart = page.locator('[data-testid="stPlotlyChart"]').first
                    chart.locator('svg.main-svg').first.wait_for(timeout=60000)
                    chart.scroll_into_view_if_needed()
                    chart.screenshot(path=str(output / f"{profile}_{index+1}_chart.png"))
                page.locator('[data-testid="stMain"]').evaluate("e=>e.scrollTop=0")
                page.screenshot(path=str(output / f"{profile}_{index+1}.png"), full_page=True)
                print(f"PASS {profile} {width}x{height}: {name}", flush=True)
            context.close()
        browser.close()


if __name__ == "__main__":
    main()
