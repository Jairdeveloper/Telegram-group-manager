import types

import httpx

from app.tools.builtins import (
    search_handler,
    weather_handler,
    http_get_handler,
    database_handler,
)


class FakeResponse:
    def __init__(self, json_data=None, text="OK", status_code=200):
        self._json = json_data or {}
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        return None

    def json(self):
        return self._json


def test_search_handler_uses_duckduckgo(monkeypatch):
    monkeypatch.setenv("SEARCH_API_URL", "https://api.duckduckgo.com/")
    monkeypatch.setenv("SEARCH_PROVIDER", "duckduckgo")

    def fake_get(*args, **kwargs):
        return FakeResponse(json_data={"AbstractText": "resultado de prueba"})

    monkeypatch.setattr(httpx, "get", fake_get)
    result = search_handler("openai")
    assert "resultado de prueba" in result


def test_weather_handler(monkeypatch):
    monkeypatch.setenv("WEATHER_API_KEY", "test-key")
    monkeypatch.setenv("WEATHER_API_URL", "https://api.openweathermap.org/data/2.5/weather")

    def fake_get(*args, **kwargs):
        return FakeResponse(
            json_data={"main": {"temp": 25}, "weather": [{"description": "cielo claro"}]}
        )

    monkeypatch.setattr(httpx, "get", fake_get)
    result = weather_handler("Madrid")
    assert "Weather for Madrid" in result


def test_http_get_handler_allowlist(monkeypatch):
    monkeypatch.setenv("HTTP_ALLOWED_HOSTS", "example.com")

    def fake_get(*args, **kwargs):
        return FakeResponse(text="payload")

    monkeypatch.setattr(httpx, "get", fake_get)
    result = http_get_handler("http://example.com/data")
    assert "HTTP 200" in result


def test_database_handler_select(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/db")

    class FakeResult:
        def keys(self):
            return ["col"]

        def fetchmany(self, limit):
            return [("value",)]

    class FakeConn:
        def execute(self, *args, **kwargs):
            return FakeResult()

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    class FakeEngine:
        def connect(self):
            return FakeConn()

    def fake_create_engine(*args, **kwargs):
        return FakeEngine()

    import sqlalchemy

    monkeypatch.setattr(sqlalchemy, "create_engine", fake_create_engine)
    result = database_handler("select 'value' as col")
    assert "col" in result
    assert "value" in result
