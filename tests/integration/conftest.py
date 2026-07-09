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
        # Store/replay response bodies decompressed so cassette playback does not
        # depend on the client's Content-Encoding handling. Without this, gzip
        # cassettes recorded under urllib3 1.x fail to decode under urllib3 2.x.
        "decode_compressed_response": True,
    }
