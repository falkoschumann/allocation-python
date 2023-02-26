import pathlib
import shutil
import subprocess
import time

import pytest
import redis
import requests
import sqlalchemy
import sqlalchemy.exc
import sqlalchemy.orm
import tenacity

from allocation import config
from allocation.adapters.orm import metadata, start_mappers

pytest.register_assert_rewrite("tests.e2e.api_client")


@pytest.fixture
def in_memory_db():
    engine = sqlalchemy.create_engine("sqlite:///:memory:", echo=True)
    metadata.create_all(engine)
    return engine


@pytest.fixture
def sqlite_session_factory(in_memory_db):
    yield sqlalchemy.orm.sessionmaker(bind=in_memory_db)


@pytest.fixture
def mappers():
    start_mappers()
    yield
    sqlalchemy.orm.clear_mappers()


@tenacity.retry(stop=tenacity.stop_after_delay(10))
def wait_for_postgres_to_come_up(engine):
    return engine.connect()


@tenacity.retry(stop=tenacity.stop_after_delay(10))
def wait_for_webapp_to_come_up():
    return requests.get(config.get_api_url())


@tenacity.retry(stop=tenacity.stop_after_delay(10))
def wait_for_redis_to_come_up():
    r = redis.Redis(**config.get_redis_host_and_port())
    return r.ping()


@pytest.fixture(scope="session")
def postgres_db():
    engine = sqlalchemy.create_engine(config.get_postgres_uri(), echo=True)
    wait_for_postgres_to_come_up(engine)
    metadata.create_all(engine)
    return engine


@pytest.fixture
def postgres_session_factory(postgres_db):
    yield sqlalchemy.orm.sessionmaker(bind=postgres_db)


@pytest.fixture
def postgres_session(postgres_db):
    postgres_session_factory()


@pytest.fixture()
def restart_api():
    (
        pathlib.Path(__file__).parent / "../src/allocation/entrypoints/flask_app.py"
    ).touch()
    time.sleep(0.5)
    wait_for_webapp_to_come_up()


@pytest.fixture
def restart_redis_pubsub():
    wait_for_redis_to_come_up()
    if not shutil.which("docker-compose"):
        print("skipping restart, assumes running in container")
        return
    subprocess.run(
        ["docker-compose", "restart", "-t", "0", "redis_pubsub"],
        check=True,
    )
