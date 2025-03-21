import re
import os
import pytest
from premier_league import Transfers

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
CASSETTE_DIR = os.path.join(TEST_DIR, "transfers", "cassettes")

@pytest.mark.vcr(cassette_library_dir=CASSETTE_DIR)
def test_premier_league_integration():
    pass