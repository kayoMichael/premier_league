from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from .models.base import Base
from .models.league import League


def init_db(db_path: str = "sqlite:///premier_league/data/premier_league.db") -> Session:
    """
    Initialize the database and return a session.

    Args:
        db_path: SQLite database URL. Defaults to 'premier_league.db' in current directory.

    Returns:
        SQLAlchemy session object
    """
    engine = create_engine(db_path)

    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    seed_initial_data(SessionLocal())

    return SessionLocal()


def seed_initial_data(session: Session):
    """
    Seed initial League data into the database

    Args:
        session: SQLAlchemy session object

    """

    all_current_league_names = [league[0] for league in session.query(League.name).all()]

    for potential_league in ["Premier League", "La Liga", "Serie A", "Fußball-Bundesliga", "Ligue 1", "EFL Championship"]:
        if potential_league not in all_current_league_names:
            if potential_league == "EFL Championship":
                session.add(League(name=potential_league, up_to_date_season="2018-2019", up_to_date_match_week=1))
            else:
                session.add(League(name=potential_league, up_to_date_season="2017-2018", up_to_date_match_week=1))

    try:
        if session.dirty or session.new:
            session.commit()
    except Exception as e:
        session.rollback()
        raise Exception(f"Error seeding database: {str(e)}")
