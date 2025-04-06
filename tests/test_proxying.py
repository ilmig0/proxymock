import time


async def test_should_proxying_by_default(
    api,
    mockserver,
    target_header,
):
    path = "/test_should_proxying_by_default"
    non_mocked_response = {"status": "non_mocked"}

    @mockserver.json_handler(f"{path}")
    def _foo(request):
        return non_mocked_response

    @mockserver.json_handler("/persist")
    def _persist(request):
        return {"status": "OK"}

    response = await api.get(
        f"{path}",
        headers=target_header,
    )

    assert response.status == 200
    assert response.json() == non_mocked_response
    assert _foo.times_called == 1

    if _persist.has_calls:
        persist_call = _persist.next_call()
    else:
        persist_call = await _persist.wait_call()

    assert persist_call["request"].json == {
        "request": {"body": "", "method": "GET", "url": f"{path}"},
        "response": {"body": non_mocked_response, "status_code": 200},
    }


async def test_persisting_should_be_in_background_proxy(
    api,
    mockserver,
    target_header,
):
    path = "/test_persisting_should_be_in_background_proxy"
    non_mocked_response = {"status": "non_mocked"}

    @mockserver.json_handler(f"{path}")
    def _foo(request):
        return non_mocked_response

    @mockserver.json_handler("/persist")
    def _persist(request):
        time.sleep(3)
        return {"status": "OK"}

    response = await api.get(
        f"{path}",
        headers=target_header,
    )

    assert response.status == 200
    assert response.json() == non_mocked_response
    assert _foo.times_called == 1

    if _persist.has_calls:
        persist_call = _persist.next_call()
    else:
        persist_call = await _persist.wait_call()

    assert persist_call["request"].json == {
        "request": {"body": "", "method": "GET", "url": f"{path}"},
        "response": {"body": non_mocked_response, "status_code": 200},
    }
