import time

import pytest
import uvicorn

from multiprocessing.context import Process
from application.settings import get_settings

settings = get_settings()

settings.READ_DATABASE_URL = (
    "postgresql://postgres:postgres@localhost/digital_land_test"
)
settings.WRITE_DATABASE_URL = (
    "postgresql://postgres:postgres@localhost/digital_land_test"
)

from application.app import create_app  # noqa: E402

app = create_app()

HOST = "0.0.0.0"
PORT = 9000
BASE_URL = f"http://{HOST}:{PORT}"


def run_server():
    uvicorn.run(app, host=HOST, port=PORT)


@pytest.fixture(scope="session")
def server_process():
    proc = Process(target=run_server, args=(), daemon=True)
    proc.start()
    time.sleep(10)
    yield proc
    proc.kill()


def test_download_data_for_dataset(
    server_process, page, add_base_entities_to_database_yield_reset
):
    page.goto(BASE_URL)

    # Navigate to the Brownfield site dataset page.
    page.get_by_role("link", name="Datasets", exact=True).click()
    page.get_by_role("link", name="Geography").click()
    page.get_by_role("link", name="Brownfield site").click()

    # Check that the "CSV" download link is correct.
    csv_href = page.get_by_role("link", name="CSV", exact=True).first.get_attribute(
        "href"
    )

    assert "brownfield-site" in csv_href
    assert ".csv" in csv_href

    # Check that the "JSON" download link is correct.
    json_href = page.get_by_role("link", name="JSON", exact=True).first.get_attribute(
        "href"
    )

    assert "brownfield-site" in json_href
    assert ".json" in json_href

    # Check that the "GeoJSON" download link is correct.
    geojson_href = page.get_by_role(
        "link", name="GeoJSON", exact=True
    ).first.get_attribute("href")

    assert "brownfield-site" in geojson_href
    assert ".geojson" in geojson_href