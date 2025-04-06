import time


async def test_mocked_by_rule(
    api,
    mockserver,
    target_header,
):
    non_mocked_response = {"status": "non_mocked"}
    mocked_response = {"status": "non_mocked"}

    @mockserver.json_handler("/foo")
    def _foo(request):
        return non_mocked_response

    @mockserver.json_handler("/log")
    def _log(request):
        return "OK"

    set_rule = await api.post(
        "/rule",
        json={
            "path": "foo",
            "response": mocked_response,
        },
    )

    response = await api.get(
        "/foo",
        headers=target_header,
    )

    assert _foo.times_called == 0
    assert response.status == 200
    assert response.json() == mocked_response

    log_call = await _log.wait_call()
    assert log_call["request"].json == {
        "request": {"body": "", "method": "GET", "url": "/foo"},
        "response": {"body": mocked_response, "status_code": 200},
    }


async def test_request_logging_should_be_in_background(
    api,
    mockserver,
    target_header,
):
    non_mocked_response = {"status": "non_mocked"}
    mocked_response = {"status": "non_mocked"}

    @mockserver.json_handler("/foo")
    def _foo(request):
        return non_mocked_response

    @mockserver.json_handler("/log")
    def _log(request):
        time.sleep(3)
        return "OK"

    set_rule = await api.post(
        "/rule",
        json={
            "path": "foo",
            "response": mocked_response,
        },
    )

    response = await api.get(
        "/foo",
        headers=target_header,
    )

    assert _foo.times_called == 0
    assert response.status == 200
    assert response.json() == mocked_response

    assert _log.times_called == 0
    log_call = await _log.wait_call()
    assert log_call["request"].json == {
        "request": {"body": "", "method": "GET", "url": "/foo"},
        "response": {"body": mocked_response, "status_code": 200},
    }
