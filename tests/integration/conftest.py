import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--force-live",
        action="store_true",
        default=False,
        help="Update VCR cassettes with live data",
    )


@pytest.fixture(scope="session")
def force_live(request):
    return request.config.getoption("--force-live")


@pytest.fixture(scope="module")
def vcr_config(force_live):
    return {
        "record_mode": "all" if force_live else "once",
    }
