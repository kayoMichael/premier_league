import os
import sqlite3
from importlib.resources import files

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .models.league import League


def init_db(db_filename: str, db_directory: str) -> Session:
    """
    Initialize the database and seed initial data
    Args:
        db_filename: Name of the database file
        db_directory: Name of the directory where the database file is stored
    Returns:
        SQLAlchemy session object
    """
    if db_directory is None or db_filename is None:
        raise ValueError("db_filename and db_directory must not be None Value")

    data_dir = os.path.join(os.getcwd(), db_directory)
    os.makedirs(data_dir, exist_ok=True)

    db_path = os.path.join(data_dir, db_filename)

    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        sql_path = files("premier_league").joinpath("data/premier_league.sql")
        with sql_path.open("r") as sql_file:
            conn.executescript(sql_file.read())
        conn.close()

    engine = create_engine(f"sqlite:///{db_path}")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    seed_initial_data(session)
    return session


def seed_initial_data(session: Session):
    """
    Seed initial League data into the database

    Args:
        session: SQLAlchemy session object
    """

    all_current_league_names = [
        league[0] for league in session.query(League.name).all()
    ]

    for potential_league in [
        "Premier League",
        "La Liga",
        "Serie A",
        "Fußball-Bundesliga",
        "Ligue 1",
        "EFL Championship",
    ]:
        if potential_league not in all_current_league_names:
            if potential_league == "EFL Championship":
                session.add(
                    League(
                        name=potential_league,
                        up_to_date_season="2018-2019",
                        up_to_date_match_week=1,
                    )
                )
            else:
                session.add(
                    League(
                        name=potential_league,
                        up_to_date_season="2017-2018",
                        up_to_date_match_week=1,
                    )
                )

    try:
        if session.dirty or session.new:
            session.commit()
    except Exception as e:
        session.rollback()
        raise Exception(f"Error seeding database: {str(e)}")
