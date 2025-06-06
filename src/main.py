import os
import fire
import httpx
import json
import logging

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, Response
from starlette.background import BackgroundTask

logging.basicConfig(
    format="%(asctime)s:%(name)s:%(process)d:%(lineno)d " "%(levelname)s %(message)s"
)
logger = logging.getLogger("app")

app = FastAPI()

RULES = {
    "proxy/session": {"status": "mocked"},
}

TARGET_HOST_HEADER = "x-target-host"

PERSIST_SERVER_URL = os.getenv("PERSIST_SERVER_URL")


async def proxy_request(request: Request, target_url: str):
    logger.info(f"Target url: {target_url}")
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=target_url,
            headers={
                key: value for key, value in request.headers.items() if key != "host"
            },
            content=await request.body(),
            params=request.query_params,
        )
        return StreamingResponse(
            response.iter_bytes(),
            status_code=response.status_code,
            headers=response.headers,
        )


async def persist(
    request_url,
    request_method,
    request_body,
    response_code,
    response_body,
):
    if "/rule" in request_url or "/ping" in request_url:
        return

    async with httpx.AsyncClient() as client:
        _ = await client.request(
            method="POST",
            url=PERSIST_SERVER_URL + "/persist",
            content=json.dumps(
                {
                    "request": {
                        "url": request_url,
                        "method": request_method,
                        "body": request_body,
                    },
                    "response": {
                        "status_code": response_code,
                        "body": json.loads(response_body),
                    },
                }
            ),
        )


@app.middleware("http")
async def log_requests_and_responses(request: Request, call_next):
    request_body = await request.body()
    request_body = request_body.decode()
    logger.info(f"Request: {request.method} {request.url} Body: {request_body}")

    response: Response = await call_next(request)
    response_body = b""
    async for chunk in response.body_iterator:
        response_body += chunk

    response_body = response_body.decode()
    logger.info(f"Response: {response.status_code} Body: {response_body}")

    return Response(
        content=response_body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type,
        background=BackgroundTask(
            persist,
            request_url=request.url.path,
            request_method=request.method,
            request_body=request_body,
            response_code=response.status_code,
            response_body=response_body,
        ),
    )


@app.api_route("/ping", methods=["GET"])
async def ping_handler(request: Request):
    return {"status": "OK"}


@app.api_route("/rule", methods=["POST"])
async def rule_create_handler(request: Request):
    rule = await request.json()
    RULES.update({rule["path"]: rule["response"]})
    return {"status": "OK"}


@app.api_route("/rule", methods=["DELETE"])
async def rule_delete_handler(request: Request):
    rule = await request.json()
    if rule["path"] in RULES:
        del RULES[rule["path"]]
    return {"status": "OK"}


@app.api_route(
    "/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
)
async def route_handler(request: Request, full_path: str):
    if full_path in RULES:
        return RULES[full_path]
    else:
        target_server = request.headers.get(TARGET_HOST_HEADER)
        target_url = f"{target_server}/{full_path}"
        return await proxy_request(request, target_url)


def serve(port):
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    fire.Fire(serve)
