import pytest

from premier_league.api.app import create_app
from premier_league.api.config.config import ServerConfig


@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    test_config = ServerConfig(
        HOST="localhost",
        PORT=5000,
        DEBUG=True,
        SECRET_KEY="test-key",
        CORS_ORIGINS=["*"],
        JSON_SORT_KEYS=False,
        RATE_LIMIT=100,
        CACHE_TYPE="null",
        CACHE_DEFAULT_TIMEOUT=0,
        LOG_LEVEL="ERROR",
    )

    app, _ = create_app(test_config)
    yield app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()


@pytest.fixture
def mock_player_goals_data():
    """Sample player data for testing."""
    return [
        {
            "Club": "Paris Saint-Germain",
            "Country": "France",
            "Goals": "34",
            "In Play Goals+Penalty": "(27+7)",
            "Name": "Kylian Mbappé",
        },
        {
            "Club": "Olympique Marseille",
            "Country": "Gabon",
            "Goals": "25",
            "In Play Goals+Penalty": "(17+8)",
            "Name": "Pierre-Emerick Aubameyang",
        },
        {
            "Club": "Lille OSC",
            "Country": "Canada",
            "Goals": "24",
            "In Play Goals+Penalty": "(19+5)",
            "Name": "Jonathan David",
        },
        {
            "Club": "Olympique Lyonnais",
            "Country": "France",
            "Goals": "21",
            "In Play Goals+Penalty": "(19+2)",
            "Name": "Alexandre Lacazette",
        },
    ]


@pytest.fixture
def mock_player_assists_data():
    """Sample player assist data for testing."""
    return [
        {
            "Assists": "8",
            "Club": "Olympique Marseille",
            "Country": "Gabon",
            "Name": "Pierre-Emerick Aubameyang",
        },
        {
            "Assists": "8",
            "Club": "Stade Brestois 29",
            "Country": "France",
            "Name": "Romain Del Castillo",
        },
        {
            "Assists": "8",
            "Club": "Paris Saint-Germain",
            "Country": "France",
            "Name": "Ousmane Dembélé",
        },
    ]


@pytest.fixture
def mock_ranking_data():
    """Sample ranking data for testing."""
    return [
        {
            "D": "10",
            "GA": "33",
            "GD": "+48",
            "GF": "81",
            "L": "2",
            "Pld": "34",
            "Pos": "1",
            "Pts": "76",
            "Team": "Paris Saint-Germain",
            "W": "22",
        },
        {
            "D": "49",
            "GA": "7",
            "GD": "Lens",
            "GF": "−6",
            "L": "55",
            "Pld": "5",
            "Pos": "34",
            "Pts": "34",
            "Team": "16",
            "W": "13",
        },
        {
            "D": "10",
            "GA": "60",
            "GD": "−34",
            "GF": "26",
            "L": "19",
            "Pld": "34",
            "Pos": "18",
            "Team": "Clermont",
            "W": "5",
        },
    ]


@pytest.fixture
def mock_ranking_data_list():
    """Sample ranking data list for testing."""
    return [
        ["Pos", "Team", "Pld", "W", "D", "L", "GF", "GA", "GD", "Pts"],
        ["1", "Paris Saint-Germain", "34", "22", "10", "2", "81", "33", "+48", "76"],
        ["2", "Monaco", "34", "20", "7", "7", "68", "42", "+26", "3"],
    ]


@pytest.fixture
def mock_transfer_data():
    """Sample transfer data for testing."""
    return [
        {
            "Club": "São Paulo FC",
            "Date": "01/24",
            "Name": "Lucas Beraldo",
            "Position": "DF",
        },
        {
            "Club": "Eintracht Frankfurt",
            "Date": "09/23",
            "Name": "Randal Kolo Muani",
            "Position": "FW",
        },
        {
            "Club": "Olympique Lyonnais",
            "Date": "08/23",
            "Name": "Bradley Barcola",
            "Position": "FW",
        },
        {
            "Club": "FC Barcelona",
            "Date": "08/23",
            "Name": "Ousmane Dembélé",
            "Position": "FW",
        },
    ]


@pytest.fixture
def mock_transfers_list():
    return [
        ["Date", "Name", "Position", "Club"],
        ["01/24", "Lucas Beraldo", "DF", "São Paulo FC"],
        ["09/23", "Randal Kolo Muani", "FW", "Eintracht Frankfurt"],
        ["08/23", "Bradley Barcola", "FW", "Olympique Lyonnais"],
        ["08/23", "Ousmane Dembélé", "FW", "FC Barcelona"],
    ]


@pytest.fixture
def mock_teams_data():
    """Sample teams data for testing."""
    return ["Arsenal FC", "Olympique Marseille", "Lille OSC", "Olympique Lyonnais"]


@pytest.fixture
def create_temp_file(tmp_path):
    """Returns a function to create a temporary file dynamically."""

    def _create_temp_file(filename: str, data: str):
        temp = tmp_path / filename
        temp.write_text(data)
        return str(temp)

    return _create_temp_file
