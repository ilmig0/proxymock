import pytest

import sys
import pathlib

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
    """Path to example service root."""
    return pathlib.Path(__file__).parent.parent


@pytest.fixture(scope="session")
async def service_scope(
    create_daemon_scope,
    service_baseurl,
    service_root,
):
    app_path = str(service_root.joinpath("src", "fastapi", "app.py"))
    print(sys.executable, app_path)
    async with create_daemon_scope(
        args=[
            sys.executable,
            app_path,
        ],
        ping_url=service_baseurl + "ping",
    ) as scope:
        yield scope


@pytest.fixture
def handle_log(mockserver):
    @mockserver.json_handler("/log")
    def log_handler(request):
        print("logged", request.json)
        return {"msg": "hello"}

    return log_handler


@pytest.fixture
async def service(
    ensure_daemon_started,
    service_scope,
    handle_log,
):
    await ensure_daemon_started(service_scope)


@pytest.fixture
async def api(
    create_service_client,
    service_baseurl,
    service,
):
    return create_service_client(service_baseurl)


@pytest.fixture
def target_header(mockserver):
    return {"x-target-host": mockserver.base_url.rstrip("/")}
