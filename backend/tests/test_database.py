from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, normalize_database_url
from app.models.department import Department


def test_database_url_quotes_special_password_without_losing_normalization():
    from sqlalchemy.engine import make_url

    raw = normalize_database_url("postgres://user:p@ss!word@db.example:5432/app")
    parsed = make_url(raw)
    assert parsed.drivername == "postgresql+psycopg2"
    assert parsed.password == "p@ss!word"
    encoded = normalize_database_url("postgresql://user:p%40ss@db.example:5432/app")
    assert make_url(encoded).password == "p@ss"


def test_alembic_migrations_apply_to_fresh_sqlite_database(tmp_path):
    database_path = tmp_path / "migration.sqlite"
    config = Config(str(Path(__file__).parents[1] / "alembic.ini"))
    config.attributes["test_database_url"] = f"sqlite:///{database_path.as_posix()}"
    command.upgrade(config, "head")
    engine = create_engine(f"sqlite:///{database_path.as_posix()}")
    assert "approvals" in __import__("sqlalchemy").inspect(engine).get_table_names()
    engine.dispose()


def test_seeded_model_rows_round_trip(tmp_path):
    engine = create_engine(f"sqlite:///{(tmp_path / 'seed.sqlite').as_posix()}")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    row = Department(id="dept-test", name="Test Regulatory Department", website="https://example.gov")
    session.add(row)
    session.commit()
    loaded = session.query(Department).filter_by(id="dept-test").one()
    assert loaded.name == "Test Regulatory Department"
    assert loaded.website == "https://example.gov"
    session.close()
    engine.dispose()
