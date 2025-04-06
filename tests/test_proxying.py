async def test_json_handler(
    api,
    mockserver,
    target_header,
    handle_log,
):
    @mockserver.json_handler("/foo")
    def _handler(request):
        return {"msg": "hello"}

    response = await api.get(
        "/foo",
        headers=target_header,
    )
    assert response.status == 200
    data = response.json()

    assert data == {"msg": "hello"}
    call = await handle_log.wait_call()
    assert call["request"].json == {
        "request": {"body": "", "method": "GET", "url": "/foo"},
        "response": {"body": '{"msg": "hello"}', "status_code": 200},
    }


async def test_json_handler2(
    api,
    mockserver,
    target_header,
    handle_log,
):
    @mockserver.json_handler("/foo")
    def _handler(request):
        return {"msg": "hello"}

    response = await api.get(
        "/foo",
        headers=target_header,
    )
    assert response.status == 200
    data = response.json()

    assert data == {"msg": "hello"}
    call = await handle_log.wait_call()
    assert call["request"].json == {
        "request": {"body": "", "method": "GET", "url": "/foo"},
        "response": {"body": '{"msg": "hello"}', "status_code": 200},
    }
