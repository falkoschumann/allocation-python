import pathlib
import time

import pytest
import requests
import sqlalchemy
import sqlalchemy.exc
import sqlalchemy.orm

from allocation import config
from allocation.adapters.orm import metadata, start_mappers


@pytest.fixture
def in_memory_db():
    engine = sqlalchemy.create_engine("sqlite:///:memory:", echo=True)
    metadata.create_all(engine)
    return engine


@pytest.fixture
def session_factory(in_memory_db):
    start_mappers()
    yield sqlalchemy.orm.sessionmaker(bind=in_memory_db)
    sqlalchemy.orm.clear_mappers()


@pytest.fixture
def session(session_factory):
    return session_factory()


def wait_for_postgres_to_come_up(engine):
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            return engine.connect()
        except sqlalchemy.exc.OperationalError:
            time.sleep(0.5)
    pytest.fail("Postgres never came up")


def wait_for_webapp_to_come_up():
    deadline = time.time() + 10
    url = config.get_api_url()
    while time.time() < deadline:
        try:
            return requests.get(url)
        except requests.ConnectionError:
            time.sleep(0.5)
    pytest.fail("API never came up")


@pytest.fixture(scope="session")
def postgres_db():
    engine = sqlalchemy.create_engine(config.get_postgres_uri(), echo=True)
    wait_for_postgres_to_come_up(engine)
    metadata.create_all(engine)
    return engine


@pytest.fixture
def postgres_session_factory(postgres_db):
    start_mappers()
    yield sqlalchemy.orm.sessionmaker(bind=postgres_db)
    sqlalchemy.orm.clear_mappers()


@pytest.fixture
def postgres_session(postgres_db):
    postgres_session_factory()


@pytest.fixture()
def restart_api():
    (pathlib.Path(
        __file__
    ).parent / "../src/allocation/entrypoints/flask_app.py").touch()
    time.sleep(0.5)
    wait_for_webapp_to_come_up()
