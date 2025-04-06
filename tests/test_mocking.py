import time


async def test_should_mocked_by_rule(
    api,
    mockserver,
    target_header,
):
    path = "/test_should_mocked_by_rule"
    non_mocked_response = {"status": "non_mocked"}
    mocked_response = {"status": "mocked"}

    @mockserver.json_handler(path)
    def _foo(request):
        return non_mocked_response

    @mockserver.json_handler("/persist")
    def _persist(request):
        return {"status": "OK"}

    set_rule = await api.post(
        "/rule",
        json={
            "path": path.lstrip("/"),
            "response": mocked_response,
        },
    )

    assert set_rule.json() == {"status": "OK"}

    response = await api.get(
        f"{path}",
        headers=target_header,
    )

    assert response.status == 200
    assert response.json() == mocked_response
    assert _foo.times_called == 0

    if _persist.has_calls:
        persist_call = _persist.next_call()
    else:
        persist_call = await _persist.wait_call()

    assert persist_call["request"].json == {
        "request": {"body": "", "method": "GET", "url": path},
        "response": {"body": mocked_response, "status_code": 200},
    }


async def test_persisting_should_be_in_background_mocked(
    api,
    mockserver,
    target_header,
):
    path = "/test_persisting_should_be_in_background_mocked"
    non_mocked_response = {"status": "non_mocked"}
    mocked_response = {"status": "mocked"}

    @mockserver.json_handler(path)
    def _foo(request):
        return non_mocked_response

    @mockserver.json_handler("/persist")
    def _persist(request):
        time.sleep(3)
        return {"status": "OK"}

    set_rule = await api.post(
        "/rule",
        json={
            "path": path.lstrip("/"),
            "response": mocked_response,
        },
    )

    assert set_rule.json() == {"status": "OK"}

    response = await api.get(
        f"{path}",
        headers=target_header,
    )

    assert response.status == 200
    assert response.json() == mocked_response
    assert _foo.times_called == 0

    if _persist.has_calls:
        persist_call = _persist.next_call()
    else:
        persist_call = await _persist.wait_call()

    assert persist_call["request"].json == {
        "request": {"body": "", "method": "GET", "url": path},
        "response": {"body": mocked_response, "status_code": 200},
    }
