import pytest

import sys
import pathlib

import logging

logging.basicConfig(
    format="%(asctime)s:%(name)s:%(process)d:%(lineno)d " "%(levelname)s %(message)s"
)
logger = logging.getLogger("tests")

pytest_plugins = [
    "testsuite.pytest_plugin",
]


@pytest.fixture(scope="session")
def service_port():
    return 8088


@pytest.fixture(scope="session")
def service_baseurl(service_port):
    return f"http://127.0.0.1:{service_port}/"


@pytest.fixture(scope="session")
def service_root():
    return pathlib.Path(__file__).parent.parent


@pytest.fixture(scope="session")
async def service_scope(
    create_daemon_scope,
    service_baseurl,
    service_port,
    service_root,
    mockserver_info,
):
    app_path = str(service_root.joinpath("src", "fastapi", "app.py"))
    async with create_daemon_scope(
        args=[
            sys.executable,
            app_path,
            "--port",
            str(service_port),
        ],
        ping_url=service_baseurl + "ping",
        env={
            "SEND_LOG_URL": mockserver_info.base_url.rstrip("/"),
        },
    ) as scope:
        yield scope


@pytest.fixture(scope="session")
def target_header(mockserver_info):
    return {"x-target-host": mockserver_info.base_url.rstrip("/")}


@pytest.fixture
async def service(
    ensure_daemon_started,
    service_scope,
):
    await ensure_daemon_started(service_scope)


@pytest.fixture
async def api(
    create_service_client,
    service_baseurl,
    service,
):
    return create_service_client(service_baseurl)
