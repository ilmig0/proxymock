run:
	uvicorn src.main:app --host 0.0.0.0 --port 8080
test:
	python3 -m pytest . --log-cli-level=DEBUG --capture=tee-sys
