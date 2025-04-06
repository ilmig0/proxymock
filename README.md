### Proxy mock server PoC
 - Based on FastAPI
 - Requests proxying by default
 - Mocks responses by created path rule
 - Send traffic history to persisting server by `/persist` path

## Prerequisits
 - Server for persist traffic history (or mock ex. https://app.beeceptor.com with rule for `/persist` path)
 - Persist server base url setted to PERSIST_SERVER_URL env variable

## How to run
 - Install packages `pip install -r requirements.txt`
 - Run tests: `make test`
 - Run server: `make run`

## How to add/delete rules
 - add:
 ```shell
    curl --location '<base_url>/rule' \
    --header 'Content-Type: application/json' \
    --data '{
        "path": "<path>:string",
        "response": "<response>:json"
    }'
 ```
 - delete:
 ```shell
    curl --location --request DELETE '<base_url>/rule' \
    --header 'Content-Type: application/json' \
    --data '{
        "path": "<path>:string"
    }'
 ```