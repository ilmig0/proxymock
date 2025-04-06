# Proxy mock server PoC
 - Based on FastAPI
 - Proxy server by default
 - Mocks responses if need by rules
 - Send traffic history into persistent server by `/persist` path

## Prerequisits
 - Available persistent server for history (or mock ex. https://app.beeceptor.com rule for `/persist`)
 - The persistent server base url should be setted to PERSIST_SERVER_URL env variable

## How to run
 - Install packages:
```shell
    pip install -r requirements.txt
```
 - Run tests: 
 ```shell
    make test
 ```
 - Run server:
```shell
    make run
```

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
