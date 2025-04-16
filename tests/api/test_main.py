import pytest
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from one_shot_api.api.main import app

# Constants for HTTP status codes
HTTP_STATUS_OK = 200
HTTP_STATUS_INTERNAL_ERROR = 500
ERROR_MESSAGE = "Test error"

client = TestClient(app)


def test_root() -> None:
    response = client.get("/")
    assert response.status_code == HTTP_STATUS_OK
    assert response.json() == {
        "message": "Welcome to the One-Shot RPG Story Generator API.\nCreate a one-shot!",
        "version": "0.1.0",
    }


def test_health_check() -> None:
    response = client.get("/health")
    assert response.status_code == HTTP_STATUS_OK
    assert "status" in response.json()
    assert response.json()["status"] == "healthy"


def test_generic_exception_handler() -> None:
    # Create a test endpoint that raises an exception
    @app.get("/test-error")
    async def test_error() -> None:
        raise ValueError(ERROR_MESSAGE)

    # Test the endpoint
    with pytest.raises(ValueError) as exc_info:
        client.get("/test-error", headers={"Accept": "application/json"})

    assert str(exc_info.value) == ERROR_MESSAGE


def test_cors_headers() -> None:
    # Test CORS headers are present
    response = client.options(
        "/",
        headers={
            "Origin": "http://testserver",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert response.status_code == HTTP_STATUS_OK
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "http://testserver"
    assert "access-control-allow-methods" in response.headers
    assert "GET" in response.headers["access-control-allow-methods"]
    assert "access-control-allow-headers" in response.headers
    assert "content-type" in response.headers["access-control-allow-headers"].lower()


def test_error_handling() -> None:
    # Create a test app with an error endpoint
    test_app = FastAPI()

    @test_app.exception_handler(Exception)  # type: ignore[misc]
    async def generic_exception_handler(_, exc: Exception):
        return JSONResponse(
            status_code=HTTP_STATUS_INTERNAL_ERROR,
            content={"detail": str(exc)},
        )

    # Add exception middleware
    from starlette.middleware.exceptions import ExceptionMiddleware

    test_app.add_middleware(ExceptionMiddleware, handlers=test_app.exception_handlers)

    @test_app.get("/test-error")
    async def test_error() -> None:
        raise ValueError(ERROR_MESSAGE)

    # Test the endpoint
    test_client = TestClient(test_app)
    response = test_client.get("/test-error")
    assert response.status_code == HTTP_STATUS_INTERNAL_ERROR
    assert ERROR_MESSAGE in response.json()["detail"]


def test_cors_middleware() -> None:
    response = client.get(
        "/",
        headers={
            "Origin": "http://testserver",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == HTTP_STATUS_OK
    assert "access-control-allow-origin" in response.headers
    assert (
        response.headers["access-control-allow-origin"] == "*"
    )  # CORS is configured to allow all origins
