import json
import os
import shutil
import subprocess
import sys
import time
from collections.abc import Iterator
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

import pytest
from playwright.sync_api import Browser, Page, Route, sync_playwright

from models import Person
from people_service import read_people

PROJECT_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = PROJECT_DIR / "frontend"
FRONTEND_URL = "http://127.0.0.1:5174"
API_URL = "http://127.0.0.1:8001"
CSV_PEOPLE = list(read_people().values())
SECOND_PERSON = CSV_PEOPLE[1]


def _wait_for_url(url: str, process: subprocess.Popen[bytes], name: str) -> None:
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        if process.poll() is not None:
            pytest.fail(f"{name} exited before becoming available.")
        try:
            with urlopen(url, timeout=1):
                if process.poll() is None:
                    return
                pytest.fail(f"{name} exited while becoming available.")
        except (OSError, URLError):
            time.sleep(0.25)
    pytest.fail(f"Timed out waiting for {name}.")


def _stop_process(process: subprocess.Popen[bytes]) -> None:
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


def _start_vite(port: int, api_base_url: str | None = None) -> subprocess.Popen[bytes]:
    node = shutil.which("node")
    if node is None:
        pytest.fail("Node.js is required to run the frontend browser tests.")

    environment = os.environ.copy()
    if api_base_url is not None:
        environment["VITE_API_BASE_URL"] = api_base_url

    return subprocess.Popen(
        [
            node,
            "node_modules/vite/bin/vite.js",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--strictPort",
        ],
        cwd=FRONTEND_DIR,
        env=environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )


@pytest.fixture(scope="module")
def frontend_server() -> Iterator[str]:
    process = _start_vite(5174, API_URL)
    try:
        _wait_for_url(FRONTEND_URL, process, "Vite")
        yield FRONTEND_URL
    finally:
        _stop_process(process)


@pytest.fixture(scope="module")
def cors_api_server() -> Iterator[None]:
    api_process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8001",
            "--log-level",
            "warning",
        ],
        cwd=PROJECT_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )
    try:
        _wait_for_url("http://127.0.0.1:8001/docs", api_process, "FastAPI")
        yield
    finally:
        _stop_process(api_process)


@pytest.fixture(scope="module")
def chromium_browser(frontend_server: str) -> Iterator[Browser]:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        yield browser
        browser.close()


@pytest.fixture
def page(frontend_server: str, chromium_browser: Browser) -> Iterator[Page]:
    browser_page = chromium_browser.new_page()
    browser_page.goto(frontend_server)
    yield browser_page
    browser_page.close()


def _fulfill_json(route: Route, status: int, body: object) -> None:
    route.fulfill(
        status=status,
        content_type="application/json",
        body=json.dumps(body),
    )


def _mock_person(page: Page, person: Person) -> None:
    page.route(
        f"{API_URL}/people/*",
        lambda route: _fulfill_json(route, 200, person.__dict__),
    )


def test_ui_01_initial_page_shows_lookup_form_without_results_or_errors(
    page: Page,
) -> None:
    api_requests: list[str] = []
    page.on(
        "request",
        lambda request: api_requests.append(request.url)
        if request.url.startswith(f"{API_URL}/")
        else None,
    )

    assert page.title() == "People Directory"
    assert page.get_by_role(
        "heading", name="Find a person", exact=True
    ).is_visible()
    assert page.get_by_role("spinbutton", name="Person ID").is_visible()
    assert page.get_by_role("button", name="Search").is_visible()
    assert page.get_by_role("alert").count() == 0
    assert page.locator(".person-results").count() == 0
    assert api_requests == []


def test_ui_02_find_existing_person(page: Page) -> None:
    _mock_person(page, SECOND_PERSON)
    page.get_by_role("spinbutton", name="Person ID").fill(str(SECOND_PERSON.id))
    page.get_by_role("button", name="Search").click()

    assert page.get_by_label("Name").inner_text() == SECOND_PERSON.name
    assert page.get_by_label("Country").inner_text() == SECOND_PERSON.country


def test_ui_03_replace_previous_result(page: Page) -> None:
    first_person, second_person = CSV_PEOPLE[:2]
    people_by_id = {person.id: person for person in (first_person, second_person)}

    def handle_person(route: Route) -> None:
        person_id = int(route.request.url.rsplit("/", 1)[-1])
        _fulfill_json(route, 200, people_by_id[person_id].__dict__)

    page.route(f"{API_URL}/people/*", handle_person)
    person_id = page.get_by_role("spinbutton", name="Person ID")
    search = page.get_by_role("button", name="Search")

    person_id.fill(str(first_person.id))
    search.click()
    assert page.get_by_label("Name").inner_text() == first_person.name

    person_id.fill(str(second_person.id))
    search.click()
    assert page.get_by_label("Name").inner_text() == second_person.name
    assert page.get_by_label("Country").inner_text() == second_person.country


def test_ui_04_unknown_id_clears_previous_result(page: Page) -> None:
    missing_id = max(person.id for person in CSV_PEOPLE) + 999

    def handle_person(route: Route) -> None:
        requested_id = int(route.request.url.rsplit("/", 1)[-1])
        if requested_id == SECOND_PERSON.id:
            _fulfill_json(route, 200, SECOND_PERSON.__dict__)
        else:
            _fulfill_json(
                route,
                404,
                {"detail": f"No person found with ID {requested_id}"},
            )

    page.route(f"{API_URL}/people/*", handle_person)
    person_id = page.get_by_role("spinbutton", name="Person ID")
    search = page.get_by_role("button", name="Search")

    person_id.fill(str(SECOND_PERSON.id))
    search.click()
    assert page.get_by_label("Name").inner_text() == SECOND_PERSON.name

    person_id.fill(str(missing_id))
    search.click()
    assert f"No person found with ID {missing_id}" in page.get_by_role(
        "alert"
    ).inner_text()
    assert page.locator(".person-results").count() == 0


def test_ui_05_empty_input_is_blocked_by_browser_validation(page: Page) -> None:
    api_requests: list[str] = []
    page.on(
        "request",
        lambda request: api_requests.append(request.url)
        if request.url.startswith(f"{API_URL}/")
        else None,
    )
    person_id = page.get_by_role("spinbutton", name="Person ID")
    person_id.fill("")
    page.get_by_role("button", name="Search").click()

    assert person_id.evaluate("(input) => input.validity.valueMissing")
    assert api_requests == []
    assert page.get_by_role("alert").count() == 0


@pytest.mark.parametrize("invalid_id", ["0", "-1", "1.5"])
def test_ui_06_invalid_numeric_input_is_blocked(
    page: Page,
    invalid_id: str,
) -> None:
    api_requests: list[str] = []
    page.on(
        "request",
        lambda request: api_requests.append(request.url)
        if request.url.startswith(f"{API_URL}/")
        else None,
    )
    person_id = page.get_by_role("spinbutton", name="Person ID")
    person_id.fill(invalid_id)
    page.get_by_role("button", name="Search").click()

    assert not person_id.evaluate("(input) => input.validity.valid")
    assert api_requests == []


def test_ui_07_loading_state_disables_search_until_result(page: Page) -> None:
    page.add_init_script(
        """
        window.fetch = () => new Promise((resolve) => {
          window.resolvePersonLookup = () => resolve(new Response(
            JSON.stringify({ id: 2, name: 'Maria', country: 'Portugal' }),
            { status: 200, headers: { 'Content-Type': 'application/json' } }
          ));
        });
        """
    )
    page.reload()
    page.get_by_role("spinbutton", name="Person ID").fill("2")
    page.get_by_role("button", name="Search").click()

    page.get_by_text("Looking up person…").wait_for()
    searching_button = page.get_by_role("button", name="Searching…")
    assert searching_button.is_disabled()
    page.wait_for_function("() => typeof window.resolvePersonLookup === 'function'")
    page.evaluate("() => window.resolvePersonLookup()")

    assert page.get_by_label("Name").inner_text() == "Maria"
    assert page.get_by_label("Country").inner_text() == "Portugal"
    assert page.get_by_role("button", name="Search").is_enabled()


def test_ui_08_api_unavailable_shows_connection_error(page: Page) -> None:
    page.route(f"{API_URL}/people/*", lambda route: route.abort())
    page.get_by_role("spinbutton", name="Person ID").fill(str(SECOND_PERSON.id))
    page.get_by_role("button", name="Search").click()

    assert "Could not connect to the API" in page.get_by_role("alert").inner_text()


def test_ui_09_api_server_error_is_reported(page: Page) -> None:
    page.route(
        f"{API_URL}/people/*",
        lambda route: _fulfill_json(route, 500, {"detail": "Server error"}),
    )
    page.get_by_role("spinbutton", name="Person ID").fill(str(SECOND_PERSON.id))
    page.get_by_role("button", name="Search").click()

    assert "server returned an error (500)" in page.get_by_role("alert").inner_text()
    assert page.get_by_text("PERSON FOUND").count() == 0


def test_ui_10_keyboard_accessible_lookup_and_live_announcements(page: Page) -> None:
    _mock_person(page, SECOND_PERSON)
    person_id = page.get_by_role("spinbutton", name="Person ID")

    page.keyboard.press("Tab")
    assert person_id.evaluate("(input) => document.activeElement === input")
    page.keyboard.type(str(SECOND_PERSON.id))
    page.keyboard.press("Enter")

    assert page.get_by_label("Name").inner_text() == SECOND_PERSON.name
    assert page.get_by_label("Country").inner_text() == SECOND_PERSON.country
    assert page.locator(".result-area").get_attribute("aria-live") == "polite"


def test_ui_11_responsive_layout_at_mobile_viewport(page: Page) -> None:
    page.set_viewport_size({"width": 375, "height": 812})
    person_id = page.get_by_role("spinbutton", name="Person ID")
    search = page.get_by_role("button", name="Search")
    input_box = person_id.bounding_box()
    button_box = search.bounding_box()

    assert input_box is not None
    assert button_box is not None
    assert button_box["y"] >= input_box["y"] + input_box["height"]
    assert page.evaluate(
        "() => document.documentElement.scrollWidth <= window.innerWidth"
    )
    assert person_id.is_visible()
    assert search.is_visible()


def test_ui_12_local_api_cors_allows_lookup_from_frontend_origin(
    page: Page,
    cors_api_server: None,
) -> None:
    page.get_by_role("spinbutton", name="Person ID").fill(str(SECOND_PERSON.id))
    with page.expect_response(f"{API_URL}/people/{SECOND_PERSON.id}") as response:
        page.get_by_role("button", name="Search").click()

    assert page.get_by_label("Name").inner_text() == SECOND_PERSON.name
    assert page.get_by_label("Country").inner_text() == SECOND_PERSON.country
    assert response.value.headers["access-control-allow-origin"] == (
        "http://127.0.0.1:5174"
    )
