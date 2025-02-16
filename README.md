# Premier League Data Tool

### Python Package
premier_league Package scraps data from various sites to provide useful information about the Premier League.

## Deployments
There are several ways to utilize the package as an API via Flask, or AWS Lambda. The configuration are in both the /app and /lambda_function directories. 
## Running the Flask API


### Locally
```
from premier_league import run_server

run_server()
```

## Deploying to AWS Lambda (Serverless Framework)
Assuming A Valid AWS Account is Configured

### Required IAM Role
- s3:PutObject
- s3:GetObject

```commandline
npm install -g serverless
npm install -g serverless-python-requirements
python -m premier_league.lamdba_functions.deploy --aws-profile ${aws profile} --region ${region}
```



## Features

📊 [Match Statistics](#matchstatistics)

📊 [Ranking Table](#rankingtable)

📊 [Player Leaders](#playerseasonleaders)

📊 [Transfers](#transfers)

📊 [Flask API Docs](#flask-api-docs)

# MatchStatistics

`MatchStatistics` is a class for retrieving and analyzing detailed match-level statistics in the form of ML datasets from Premier League games and other top European leagues. It provides access to extensive game data including team performance metrics, player statistics, and match events for ML Training or Analysis

## Data Structure

The data is stored in a SQLite database that is automatically initialized in the user's local directory upon first use. The database schema includes:

### Core Tables
- **League**: Stores league information and update status
- **Team**: Contains team details and league associations
- **Game**: Records match details and scores
- **GameStats**: Stores detailed match statistics

### Database Initialization

```python
from premier_league import MatchStatistics

# Initialize with default database
stats = MatchStatistics()

# The database is automatically initialized on first use
# Default location: user's data directory/premier_league_sqlite/premier_league.db
```

## Usage

```python
from premier_league import MatchStatistics

# Initialize match statistics
stats = MatchStatistics()

# Get specific team's match history
arsenal_games = stats.get_team_games("Arsenal")

# Get games for a specific season and match week
season_games = stats.get_games_by_season("2023-2024", match_week=5)

# Get recent games before a specific date
from datetime import datetime
recent_games = stats.get_games_before_date(
    date=datetime(2024, 2, 1),
    limit=10,
    team="Manchester City"
)
```

## Core Features

### Team Statistics Retrieval

#### `get_team_games(team_name: str) -> List[dict]`
Retrieves complete match history for a specific team.
```python
stats = MatchStatistics()
arsenal_games = stats.get_team_games("Arsenal")
```

#### `get_games_by_season(season: str, match_week: int) -> List[dict]`
Retrieves all games for a specific season and match week.
```python
games = stats.get_games_by_season("2023-2024", match_week=15)
```

### Time-Based Queries

#### `get_games_before_date(date: datetime, limit: int = 10, team: Optional[str] = None) -> List[dict]`
Retrieves games before a specific date with optional team filter.
```python
recent_games = stats.get_games_before_date(
    date=datetime(2024, 2, 1),
    limit=5
)
```

#### `get_game_stats_before_date(date: datetime, limit: int = 10, team: Optional[str] = None) -> List[dict]`
Retrieves detailed game statistics before a specific date.
```python
recent_stats = stats.get_game_stats_before_date(
    date=datetime(2024, 2, 1),
    team="Liverpool"
)
```

### Data Management

#### `update_data_set()`
Updates the database with the latest available match data.
```python
stats = MatchStatistics()
stats.update_data_set()
```

#### `create_dataset(output_path: str)`
Exports the entire match statistics database to a CSV file.
```python
stats.create_dataset("premier_league_stats.csv")
```

## Data Format

### Game Statistics Fields

Each game statistics record includes detailed metrics broken down by position groups (FW, MF, DF):

#### Attacking Metrics
- Expected Goals (xG)
- Expected Assisted Goals (xAG)
- Shots (Total and On Target)
- Shot Creating Actions
- Goal Creating Actions

#### Passing Metrics
- Passes Completed
- Pass Completion Percentage
- Key Passes
- Progressive Passes
- Passes into Final Third
- Passes into Penalty Area

#### Defensive Metrics
- Tackles Won
- Blocks
- Interceptions
- Clearances
- Errors Leading to Goal

#### Possession Metrics
- Possession Rate
- Touches
- Take-ons (Attempted and Successful)
- Carries
- Carrying Distance
- Ball Control Metrics

#### Miscellaneous
- Fouls (Committed and Drawn)
- Aerial Duels (Won and Lost)
- Cards (Yellow and Red)
- Goalkeeper Statistics

### Sample Game Statistics Output
```python
{
    "xG": 2.3,
    "shots_total_FW": 8,
    "shots_on_target_FW": 4,
    "passes_completed_MF": 245,
    "tackles_won_DF": 12,
    "possession_rate": 58,
    # ... many more statistics
}
```

## Database Initialization Details

The database is automatically initialized using `init_db()` which:

1. Creates a user-specific data directory
2. Installs a pre-configured SQLite database
3. Seeds initial league data
4. Sets up all required tables and relationships

```python
def init_db(
    db_filename: str = "premier_league.db",
    db_directory: str = "premier_league_sqlite"
) -> Session:
    """
    Initialize the database and seed initial data
    """
    # Creates user data directory
    data_dir = appdirs.user_data_dir(db_directory)
    
    # Sets up database if not exists
    db_path = os.path.join(data_dir, db_filename)
    if not os.path.exists(db_path):
        # Initialize from SQL dump
        conn = sqlite3.connect(db_path)
        sql_path = files("premier_league").joinpath("data/premier_league.sql")
        conn.executescript(sql_file.read())
        
    # Create SQLAlchemy session
    engine = create_engine(f"sqlite:///{db_path}")
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    # Seed initial league data
    seed_initial_data(session)
    return session
```

### Supported Leagues
The database is seeded with these leagues by default:
- Premier League
- La Liga
- Serie A
- Bundesliga
- Ligue 1
- EFL Championship

## Notes

- The database is automatically updated to include the latest available match data
- All statistics are sourced from official match reports
- Position groups (FW, MF, DF) are determined by primary player positions
- The database maintains complete match history since the 2017-2018 season
- Updates are rate-limited to respect data source restrictions
- Error handling includes automatic rollback of failed database operations


# RankingTable

`RankingTable` Fetches ranking data for a given premier league season and league.

## Usage

```python
from premier_league import RankingTable

# Initialize the ranking table for the current season
ranking = RankingTable()

# Or specify a target season
ranking = RankingTable(target_season="1995-1996")
```

## Core Features


#### `get_ranking_list() -> list`
Retrieves the current Premier League ranking data in list format.
- **Returns:** List containing the processed ranking data.
- **Example:**
  ```python
  from premier_league import RankingTable
  ranking = RankingTable().get_ranking_list()
  ```

### Export Methods

#### `get_ranking_csv(file_name: str, header: str = None) -> None`
Exports the ranking data to a CSV file.
- **Parameters:**
  - `file_name` (str): Name of the output file (without extension)
  - `header` (str, optional): Header to include in the CSV file
- **Example:**
  ```python
  from premier_league import RankingTable
  ranking = RankingTable()
  ranking.get_ranking_csv("premier_league_rankings", "Season 2023-24")
  ```

#### `get_prem_ranking_json(file_name: str, header: str = None) -> None`
Exports the ranking data to a JSON file.
- **Parameters:**
  - `file_name` (str): Name of the output file (without extension)
  - `header` (str, optional): Header to use as the parent key in the JSON structure
- **Example:**
  ```python
  from premier_league import RankingTable
  ranking = RankingTable(league="Serie A")
  ranking.get_ranking_json("premier_league_rankings", "PL_Rankings")
  ```

#### `get_prem_ranking_pdf(file_name: str) -> None`
Generates a formatted PDF file containing the Premier League ranking table.
- **Parameters:**
  - `file_name` (str): Name of the output file (without extension)
- **Features:**
  - Color-coded rows for European qualification spots
  - Relegation zone highlighting
  - Centered title with season information
- **Example:**
  ```python
  from premier_league import RankingTable
  ranking = RankingTable()
  ranking.get_ranking_pdf("premier_league_standings")
  ```

## Data Format

The ranking data is structured as a list of lists, where each inner list contains:
1. Position
2. Team name
3. Matches played
4. Wins
5. Draws
6. Losses
7. Goals for
8. Goals against
9. Goal difference
10. Points

Example: 
```python
[
    ["Position", "Team", "MP", "W", "D", "L", "GF", "GA", "GD", "Points"],
    ["1", "Manchester City", "38", "32", "4", "2", "102", "31", "71", "100"],
    # ... more entries
]
```

## Notes

- The PDF generation includes color coding:
  - Green shades for European qualification spots
  - Red for relegation zones
  - Gray for header row
- European qualification rules are handled differently for seasons before and after 2019-20
- The class automatically handles special cases like the 1994-95 season when 4 teams were relegated


# PlayerSeasonLeaders

`PlayerSeasonLeaders` is a specialized scraper for retrieving and processing Premier League player statistics, focusing on either goals or assists for a specific season.


## Usage

```python
from premier_league import PlayerSeasonLeaders

# Initialize for current season's top scorers
scorers = PlayerSeasonLeaders(stat_type='G')

# Initialize for current season's top assisters
assists = PlayerSeasonLeaders(stat_type='A')

# For a specific season's data
scorers_2022 = PlayerSeasonLeaders(stat_type='G', target_season='2022-23')
```

## Core Features

#### `get_top_stats_list(limit: int = None) -> list`
Returns processed list of top players and their statistics.
- `limit`: Optional number of players to return (defaults to 100)
```python
# Get top 10 scorers
scorers = PlayerSeasonLeaders(stat_type='G')
top_10 = scorers.get_top_stats_list(limit=10)
```

#### `get_top_stats_csv(file_name: str, header: str = None, limit: int = None)`
Exports statistics to CSV format.
```python
scorers = PlayerSeasonLeaders(stat_type='G')
scorers.get_top_stats_csv("top_scorers", header="2023-24 Season", limit=20)
```

#### `get_top_stats_json(file_name: str, header: str = None, limit: int = None)`
Exports statistics to JSON format.
```python
scorers = PlayerSeasonLeaders(stat_type='A')
scorers.get_top_stats_json("top_scorers", header="PL_Scorers", limit=20)
```

#### `get_top_stats_pdf(file_name: str)`
Creates formatted PDF of top 20 players.
```python
scorers = PlayerSeasonLeaders(stat_type='A')
scorers.get_top_stats_pdf("premier_league_top_scorers")
```

## Data Format

### Goals Statistics Format
List of lists with the following columns:
1. Name
2. Country
3. Club
4. Goals
5. Goals Breakdown (In Play Goals + Penalties)

Example:
```python
[
    ["Name", "Country", "Club", "Goals", "In Play Goals+Penalty"],
    ["Erling Haaland", "Norway", "Manchester City", "36", "30+6"],
    # ... more entries
]
```

### Assists Statistics Format
List of lists with the following columns:
1. Name
2. Country
3. Club
4. Assists

Example:
```python
[
    ["Name", "Country", "Club", "Assists"],
    ["Kevin De Bruyne", "Belgium", "Manchester City", "16"],
    # ... more entries
]
```

## Notes

- PDF export includes:
  - Gray header row
  - Gold highlighting for the top scorer/assister
  - Limited to top 20 players
  - A3 page size for better readability
- Data is scraped from worldfootball.net
- Default limit for data retrieval is 100 entries
- All export methods support optional headers and limits (except PDF which is fixed at top 20)


# Transfers

`Transfers` is a specialized scraper for retrieving and processing Premier League transfer data for teams in a specific season. It provides methods to fetch, display, and export both incoming and outgoing transfers.

## Usage

```python
from premier_league import Transfers

# Initialize for current season
transfers = Transfers()

# Initialize for specific season and league
transfers_2022 = Transfers(target_season="2022-23", league="La Liga")

# Print transfer table for a specific team
transfers.print_transfer_table("Arsenal")

# Get list of all teams in the specified season for referencing.
all_teams = transfers.get_all_current_teams()
```

## Core Features

#### `transfer_in_table(team: str) -> list[list[str]]`
Get incoming transfers for a specific team.
```python
arsenal_ins = transfers.transfer_in_table("Arsenal FC")
```

#### `transfer_out_table(team: str) -> list[list[str]]`
Get outgoing transfers for a specific team.
```python
arsenal_outs = transfers.transfer_out_table("Arsenal FC")
```

#### `print_transfer_table(team: str) -> None`
Display formatted transfer tables (both in and out) for a team.
```python
transfers.print_transfer_table("Manchester United")
```

#### `get_all_current_teams() -> list[str]`
Get list of all teams in the current season.
```python
teams = transfers.get_all_current_teams()
```

#### `transfer_csv(team: str, file_name: str, transfer_type: Literal["in", "out", "both"] = "both")`
Export transfer data to CSV format.
```python
# Export all transfers
transfers.transfer_csv("Chelsea", "chelsea_transfers")

# Export only incoming transfers
transfers.transfer_csv("Chelsea", "chelsea_incoming", transfer_type="in")

# Export only outgoing transfers
transfers.transfer_csv("Chelsea", "chelsea_outgoing", transfer_type="out")
```

#### `transfer_json(team: str, file_name: str, transfer_type: Literal["in", "out", "both"] = "both")`
Export transfer data to JSON format.
```python
# Export all transfers
transfers.transfer_json("Liverpool", "liverpool_transfers")

# Export specific transfer type (in, out)
transfers.transfer_json("Liverpool", "liverpool_ins", transfer_type="in")
```

## Data Format

### Transfer Data Structure
Each transfer record contains the following columns:
1. Date (format: "DD/MM")
2. Name (player name)
3. Position
4. Club (previous/new club)

Example Data Structure:
```python
{
    "arsenal in transfers": [
        # Incoming transfers
        [
            ["Date", "Name", "Position", "Club"],
            ["01/07", "Kai Havertz", "MF", "Chelsea FC"],
            # ... more entries
        ]
    ],
    "arsenal out transfers": [
        [
            ["Date", "Name", "Position", "Club"],
            ["30/06", "Granit Xhaka", "MF", "Bayer Leverkusen"],
            # ... more entries
        ]
    ],
    # ... more teams
}
```

## Notes

- Team names are case-insensitive but must match the official team name
- Raises `TeamNotFoundError` if specified team isn't found in the season
- Data is scraped from worldfootball.net
- Transfer dates are in DD/MM format
- The `print_transfer_table` method uses PrettyTable for formatted console output
- Export methods support three modes:
  - "both": Exports both incoming and outgoing transfers (default)
  - "in": Exports only incoming transfers
  - "out": Exports only outgoing transfers
- Team names are stored in lowercase internally
- The class automatically handles clubs with special characters or extended names
- Transfer windows covered:
  - Summer transfer window
  - Winter transfer window
- Position abbreviations follow standard football notation (MF, FW, DF, GK)


# Flask API Docs

# Premier League Players API Documentation

## Table of Contents
- [🔍 Overview](#-overview)
- [📊 Endpoints](#-endpoints)
  - [Get Top Scorers](#get-top-scorers)
  - [Get Top Assists](#get-top-assists)
  - [Export Scorers CSV](#export-scorers-csv)
  - [Export Assists CSV](#export-assists-csv)
  - [Export Scorers JSON](#export-scorers-json)
  - [Export Assists JSON](#export-assists-json)
- [🔧 Common Parameters](#-common-parameters)
- [❌ Error Handling](#-error-handling)
- [📝 Examples](#-examples)

## 🔍 Overview
[Back to top](#premier-league-data-tool)

This API provides access to Premier League player statistics, including goals and assists data. It supports both direct data retrieval and file exports in CSV and JSON formats.

## 📊 Endpoints

### Get Top Scorers

```http
GET /players/goals
```

Retrieve a list of top goalscorers in JSON format.

#### Query Parameters
- `season` (optional): Season identifier (e.g., "2023-2024")
- `limit` (optional): Maximum number of players to return

#### Response
```json
{
  "data": [
    {
      "name": "Erling Haaland",
      "country": "Norway",
      "club": "Manchester City",
      "goals": "36",
      "goals_breakdown": "30+6"
    }
  ]
}
```

### Get Top Assists

```http
GET /players/assists
```

Retrieve a list of top assist providers in JSON format.

#### Query Parameters
- `season` (optional): Season identifier (e.g., "2023-2024")
- `limit` (optional): Maximum number of players to return

#### Response
```json
{
  "data": [
    {
      "name": "Kevin De Bruyne",
      "country": "Belgium",
      "club": "Manchester City",
      "assists": "16"
    }
  ]
}
```

### Export Scorers CSV

```http
GET /players/goals/csv_file
```

Download top goalscorers data as a CSV file.

#### Query Parameters
- `season` (optional): Season identifier (e.g., "2023-2024")
- `filename` (required): Name for the exported file (without extension)
- `header` (optional): Custom header for the CSV file
- `limit` (optional): Maximum number of players to return
- `league` (optional): League name (defaults to "Premier League")

### Export Assists CSV

```http
GET /players/assists/csv_file
```

Download top assist providers data as a CSV file.

#### Query Parameters
- `season` (optional): Season identifier (e.g., "2023-2024")
- `filename` (required): Name for the exported file (without extension)
- `header` (optional): Custom header for the CSV file
- `limit` (optional): Maximum number of players to return
- `league` (optional): League name (defaults to "Premier League")

### Export Scorers JSON

```http
GET /players/goals/json_file
```

Download top goalscorers data as a JSON file.

#### Query Parameters
- `season` (optional): Season identifier (e.g., "2023-2024")
- `filename` (required): Name for the exported file (without extension)
- `header` (optional): Custom metadata for the JSON file
- `limit` (optional): Maximum number of players to return
- `league` (optional): League name (defaults to "Premier League")

### Export Assists JSON

```http
GET /players/assists/json_file
```

Download top assist providers data as a JSON file.

#### Query Parameters
- `season` (optional): Season identifier (e.g., "2023-2024")
- `filename` (required): Name for the exported file (without extension)
- `header` (optional): Custom metadata for the JSON file
- `limit` (optional): Maximum number of players to return
- `league` (optional): League name (defaults to "Premier League")

## 🔧 Common Parameters

| Parameter | Type    | Required | Description                         | Example       |
|-----------|---------|----------|-------------------------------------|---------------|
| season    | string  | No       | Premier League season identifier    | "2023-2024"   |
| limit     | integer | No       | Maximum number of results to return | 10            |
| filename  | string  | Yes*     | Output filename for file exports    | "top_scorers" |
| header    | string  | No       | Custom header/metadata for exports  | "PL Stats"    |
| league    | string  | Yes*     | Target League (defalts to PL)       | "Bundesliga"  |

\* Required only for file export endpoints

## ❌ Error Handling

The API returns standard HTTP status codes:

| Status Code | Description                                          |
|------------|------------------------------------------------------|
| 200        | Success                                              |
| 400        | Bad Request (invalid parameters)                     |
| 500        | Internal Server Error                                |

Common error responses:
```json
{
  "error": "Limit must be a number"
}
```
```json
{
  "error": "Missing filename parameter"
}
```

## 📝 Examples

### Get Top 5 Scorers for 2023-2024
```http
GET /players/goals?season=2023-2024&limit=5
```

### Export Top 10 Assists to CSV
```http
GET /players/assists/csv_file?limit=10&filename=top_assists&header=Premier League Assists
```

### Export All Scorers to JSON
```http
GET /players/goals/json_file?filename=goalscorers&header=Goal Statistics
```

### Using cURL

```bash
# Get top scorers
curl "http://api.example.com/players/goals?limit=5"

# Download assists CSV
curl -O "http://api.example.com/players/assists/csv_file?filename=assists&limit=10"
```
# Premier League Rankings API Documentation

## Table of Contents
- [🔍 Overview](#-overview-ranking)
- [📊 Endpoints](#-endpoints-ranking)
  - [Get Standings](#get-standings)
  - [Get Simple Table](#get-simple-table)
  - [Export CSV](#export-csv)
  - [Export JSON](#export-json)
  - [Export PDF](#export-pdf)
- [🔧 Common Parameters](#-common-query-parameters)
- [❌ Error Handling](#-error-codes)
- [📝 Examples](#-example)

## 🔍 Overview Ranking

This API provides access to Premier League standings and team rankings. It supports both detailed and simplified table views, along with multiple export formats including CSV, JSON, and PDF.

## 📊 Endpoints /Ranking

### Get Standings

```http
GET /ranking
```

Retrieve detailed Premier League standings with comprehensive team statistics.

#### Query Parameters
- `season` (optional): Season identifier (e.g., "2023-2024")
- `header` (optional): Include additional metadata in response

#### Response
```json
{
  "data": {
    "season": "2023-2024",
    "standings": [
      {
        "position": 1,
        "team": "Arsenal",
        "played": 38,
        "won": 25,
        "drawn": 8,
        "lost": 5,
        "goals_for": 88,
        "goals_against": 43,
        "goal_difference": 45,
        "points": 83
      }
    ]
  }
}
```

### Get Simple Table

```http
GET /ranking/table
```

Retrieve a simplified version of the league standings.

#### Query Parameters
- `season` (optional): Season identifier (e.g., "2023-2024")

#### Response
```json
{
  "data": [
    ["Pos", "Team", "P", "W", "D", "L", "GF", "GA", "GD", "Pts"],
    [1, "Arsenal", 38, 25, 8, 5, 88, 43, 45, 83]
  ]
}
```

### Export CSV

```http
GET /ranking/csv_file
```

Download Premier League standings as a CSV file.

#### Query Parameters
- `season` (optional): Season identifier (e.g., "2023-2024")
- `filename` (required): Name for the exported file (without extension)

### Export JSON

```http
GET /ranking/json_file
```

Download Premier League standings as a JSON file.

#### Query Parameters
- `season` (optional): Season identifier (e.g., "2023-2024")
- `filename` (required): Name for the exported file (without extension)

### Export PDF

```http
GET /ranking/pdf_file
```

Download Premier League standings as a formatted PDF file.

#### Query Parameters
- `season` (optional): Season identifier (e.g., "2023-2024")
- `filename` (required): Name for the exported file (without extension)

## 🔧 Common Query Parameters

| Parameter | Type   | Required | Description                      | Example       |
|-----------|--------|----------|----------------------------------|---------------|
| season    | string | No       | Premier League season identifier | "2023-2024"   |
| filename  | string | Yes*     | Output filename for file exports | "standings"   |
| header    | string | No       | Custom metadata for response     | "PL Rankings" |

\* Required only for file export endpoints

## ❌ Error Codes

The API returns standard HTTP status codes:

| Status Code | Description                  |
|------------|------------------------------|
| 200        | Success                      |
| 400        | Bad Request                  |
| 500        | Internal Server Error        |

Common error response:
```json
{
  "error": "Missing filename parameter"
}
```

## 📝 Example

### Get Current Season Standings
```http
GET /ranking
```

### Get Specific Season's Simple Table
```http
GET /ranking/table?season=2023-2024
```

### Export Standings to Different Formats
```http
# CSV Export
GET /ranking/csv_file?filename=premier_league_standings&season=2023-2024

# JSON Export
GET /ranking/json_file?filename=pl_rankings&season=2023-2024

# PDF Export
GET /ranking/pdf_file?filename=standings_report&season=2023-2024
```

### Using cURL

```bash
# Get full standings
curl "http://api.example.com/ranking"

# Download PDF report
curl -O "http://api.example.com/ranking/pdf_file?filename=standings"

# Get simplified table for specific season
curl "http://api.example.com/ranking/table?season=2023-2024"
```

### Data Format Details

#### Full Standings Response Fields
- `position`: Current league position
- `team`: Team name
- `played`: Games played
- `won`: Games won
- `drawn`: Games drawn
- `lost`: Games lost
- `goals_for`: Goals scored
- `goals_against`: Goals conceded
- `goal_difference`: Goal difference (GF - GA)
- `points`: Total points


# Premier League Transfers API Documentation

## Table of Contents
- [🔍 Overview](#-overview-transfers)
- [📊 Endpoints](#-endpoints-transfers)
  - [Get All Teams](#get-all-teams)
  - [Get Incoming Transfers](#get-incoming-transfers)
  - [Get Outgoing Transfers](#get-outgoing-transfers)
  - [Export Transfers CSV](#export-transfers-csv)
  - [Export Transfers JSON](#export-transfers-json)
- [🔧 Common Parameters](#-common-api-parameters)
- [❌ Error Handling](#-error-code)
- [📝 Examples](#-sample)

## 🔍 Overview Transfers

This API provides access to Premier League transfer data, allowing you to retrieve information about player transfers for specific teams. It supports both incoming and outgoing transfers and offers multiple export formats.

## 📊 Endpoints /Transfers

### Get All Teams

```http
GET /all_teams
```

Retrieve a list of all teams in the Premier League for a given season.

#### Query Parameters
- `season` (optional): Season identifier (e.g., "2023-2024")

#### Response
```json
{
  "data": [
    "Arsenal",
    "Aston Villa",
    "Brighton",
    "Burnley",
    ...
  ]
}
```

### Get Incoming Transfers

```http
GET /transfers/in
```

Retrieve all incoming transfers for a specific team.

#### Query Parameters
- `season` (optional): Season identifier (e.g., "2023-2024")
- `team` (required): Team name

#### Response
```json
{
  "data": [
    {
      "date": "01/07",
      "name": "Kai Havertz",
      "position": "MF",
      "previous_club": "Chelsea"
    }
  ]
}
```

### Get Outgoing Transfers

```http
GET /transfers/out
```

Retrieve all outgoing transfers for a specific team.

#### Query Parameters
- `season` (optional): Season identifier (e.g., "2023-2024")
- `team` (required): Team name

#### Response
```json
{
  "data": [
    {
      "date": "30/06",
      "name": "Granit Xhaka",
      "position": "MF",
      "new_club": "Bayer Leverkusen"
    }
  ]
}
```

### Export Transfers CSV

```http
GET /transfers/csv_file
```

Download transfer data as a CSV file.

#### Query Parameters
- `season` (optional): Season identifier (e.g., "2023-2024")
- `team` (required): Team name
- `filename` (required): Name for the exported file (without extension)
- `transfer_type` (optional): Type of transfers to include:
  - `"in"`: Only incoming transfers
  - `"out"`: Only outgoing transfers
  - `"both"`: Both incoming and outgoing transfers (default)
- `league` (optional): League name (defaults to "Premier League")

### Export Transfers JSON

```http
GET /transfers/json_file
```

Download transfer data as a JSON file.

#### Query Parameters
- `season` (optional): Season identifier (e.g., "2023-2024")
- `team` (required): Team name
- `filename` (required): Name for the exported file (without extension)
- `transfer_type` (optional): Type of transfers to include:
  - `"in"`: Only incoming transfers
  - `"out"`: Only outgoing transfers
  - `"both"`: Both incoming and outgoing transfers (default)
- `league` (optional): League name (defaults to "Premier League")

## 🔧 Common API Parameters

| Parameter     | Type   | Required | Description                      | Example     |
|---------------|--------|----------|----------------------------------|-------------|
| season        | string | No       | Premier League season identifier | "2023-2024" |
| team          | string | Yes*     | Team name                        | "Arsenal"   |
| filename      | string | Yes**    | Output filename for file exports | "transfers" |
| transfer_type | string | No       | Type of transfers to include     | "both"      |
| league        | string | Yes*     | Target league (Defaults to PL)   | "Serie A"   |

\* Required for all transfer-related endpoints except `/all_teams`  
\** Required only for file export endpoints

## ❌ Error Code

The API returns standard HTTP status codes:

| Status Code | Description                                   |
|------------|-----------------------------------------------|
| 200        | Success                                       |
| 400        | Bad Request (missing or invalid parameters)   |
| 500        | Internal Server Error                         |

Common error responses:
```json
{
  "error": "Missing team parameter"
}
```
```json
{
  "error": "Missing filename parameter"
}
```
```json
{
  "error": "Invalid type parameter"
}
```

## 📝 Sample

### Get All Teams for Current Season
```http
GET /all_teams
```

### Get Arsenal's Incoming Transfers
```http
GET /transfers/in?team=Arsenal
```

### Export Complete Transfer History
```http
GET /transfers/csv_file?team=Manchester%20United&filename=united_transfers&transfer_type=both
```

### Using cURL

```bash
# Get all teams
curl "http://api.example.com/all_teams"

# Get incoming transfers
curl "http://api.example.com/transfers/in?team=Chelsea"

# Download transfer data
curl -O "http://api.example.com/transfers/json_file?team=Liverpool&filename=liverpool_transfers"
```

### Data Format Details

#### Transfer Record Fields
- `date`: Transfer date (DD/MM format)
- `name`: Player name
- `position`: Player position (e.g., MF, FW, DF, GK)
- `previous_club`/`new_club`: Club involved in the transfer

#### File Export Features
- CSV exports include headers
- JSON exports are properly formatted
- Filenames are sanitized for security
- Support for splitting incoming/outgoing transfers
