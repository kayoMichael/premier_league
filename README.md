# Premier League Data Scraping Package

A comprehensive Python package for exporting Premier League data. This package provides various modules to retrieve league standings, player statistics (goals and assists), transfer data, and machine learning datasets through the PLPredictor.
Table of Contents

    Features
    Installation
    Quick Start
        Importing the Package
        Using the RankingTable
        Using the PlayerSeasonLeaders
        Using the Transfers Module
        Using the PLPredictor
        Running the API Server
    API Endpoints
    Contributing
    License

Features

    Ranking Table: Scrape and export Premier League standings as CSV, JSON, or PDF.
    Player Season Leaders: Retrieve top goal scorers or assist leaders for a given season.
    Transfers: Extract transfer data (in/out/both) for any Premier League team.
    PLPredictor: Update and export datasets for machine learning purposes.
    Flask API: Run a RESTful API server with endpoints for standings, player stats, and transfers.
    AWS Lambda Support: Deploy your scrapers as serverless functions.

Installation

Install the package via pip:

pip install premier_league

Or install from source:

git clone https://github.com/yourusername/premier_league.git
cd premier_league
pip install -e .

Quick Start
Importing the Package

The package provides several modules which can be imported directly:

from premier_league import (
    RankingTable,
    PlayerSeasonLeaders,
    Transfers,
    PLPredictor,
    run_server,
)

Using the RankingTable

Retrieve and export the league standings:

# Initialize for the 2023-2024 season
ranking = RankingTable(target_season="2023-2024")

# Get the current ranking list (list of lists)
ranking_data = ranking.get_ranking_list()
print(ranking_data)

# Export ranking table to CSV
ranking.get_ranking_csv("premier_league_standings", header="Premier League 2023-2024")

# Export ranking table to JSON
ranking.get_ranking_json("premier_league_standings", header="Premier League 2023-2024")

# Export ranking table to PDF
ranking.get_ranking_pdf("premier_league_standings")

Using the PlayerSeasonLeaders

Retrieve and export top goal scorers or assist leaders:

# For top goal scorers:
scorers = PlayerSeasonLeaders(stat_type="G", target_season="2023-2024")
top_scorers = scorers.get_top_stats_list(limit=10)
print(top_scorers)

# Export goal scorers data to CSV
scorers.get_top_stats_csv("top_goal_scorers", header="Top Goalscorers 2023-2024", limit=10)

# Export goal scorers data to JSON
scorers.get_top_stats_json("top_goal_scorers", header="Top Goalscorers 2023-2024", limit=10)

# Export goal scorers data to PDF (top 20 by default)
scorers.get_top_stats_pdf("top_goal_scorers", path="files")

Using the Transfers Module

Extract transfer data for a specific team:

# Initialize Transfers for a given season (optional)
transfers = Transfers(target_season="2023-2024")

# List all teams available in the season
teams = transfers.get_all_current_teams()
print("Teams:", teams)

# Print transfer table for a specific team (e.g., Arsenal)
transfers.print_transfer_table("Arsenal")

# Alternatively, export transfer data to CSV:
transfers.transfer_csv("Arsenal", "arsenal_transfers", transfer_type="both")

# Or export transfer data to JSON:
transfers.transfer_json("Arsenal", "arsenal_transfers", transfer_type="both")

Using the PLPredictor

Update your dataset and export it for further analysis or machine learning:

# Initialize the PLPredictor
predictor = PLPredictor()

# Update the dataset with new match data
predictor.update_data_set()

# Create a CSV dataset for analysis or training
predictor.create_dataset("ml_dataset.csv")

Running the API Server

Run a Flask-based API server (useful for development or deployment):

from premier_league import run_server

if __name__ == '__main__':
    # Run the API on localhost at port 5000 with debug mode enabled
    run_server(host="0.0.0.0", port=5000, debug=True)

The API provides endpoints for:

    Player Stats (goals/assists) with file export options.
    League Standings with export to CSV/JSON/PDF.
    Transfers Data with options to filter incoming/outgoing transfers.

For more details on the API endpoints, please refer to the API Documentation section.
API Endpoints

The package includes a Flask API as well as AWS Lambda handlers. Here’s a brief overview:

    /players/goals & /players/assists: Retrieve top player stats in JSON.
    /players/goals/csv_file & /players/assists/csv_file: Export player stats as CSV.
    /players/goals/json_file & /players/assists/json_file: Export player stats as JSON.
    /ranking: Retrieve detailed league standings.
    /ranking/csv_file, /ranking/json_file, /ranking/pdf_file: Export standings in various formats.
    /transfers/in, /transfers/out: Retrieve transfer data for a team.
    /transfers/csv_file, /transfers/json_file: Export transfers data.

For complete API documentation, refer to the inline docs in the source code or the API Docs (if provided).
Contributing

Contributions are welcome! Please follow these steps:

    Fork the repository.
    Create a new branch for your feature or bug fix.
    Commit your changes with clear commit messages.
    Submit a pull request with a detailed description of your changes.

Please ensure that your code follows the PEP 8 style guide.
License

This project is licensed under the MIT License.

Feel free to reach out with any questions or suggestions.

Happy scraping!