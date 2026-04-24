"""Tests for Gemini client retry behavior."""

from types import SimpleNamespace

from weave.ai.client import call_gemini


class _DummyModels:
    def __init__(self, responses):
        self._responses = iter(responses)

    def generate_content(self, **_kwargs):
        response = next(self._responses)
        if isinstance(response, Exception):
            raise response
        return response


class _DummyClient:
    def __init__(self, responses):
        self.models = _DummyModels(responses)


def test_call_gemini_waits_longer_for_503(monkeypatch):
    sleep_calls = []
    monkeypatch.setattr("weave.ai.client.time.sleep", sleep_calls.append)

    client = _DummyClient(
        [
            Exception("503 UNAVAILABLE. {'status': 'UNAVAILABLE'}"),
            SimpleNamespace(text="ok"),
        ]
    )

    result = call_gemini(
        client,
        contents=["hello"],
        system_instruction="test",
        model="gemini-2.5-flash",
        max_retries=3,
        retry_base_delay=2,
        unavailable_retry_delay=30,
    )

    assert result == "ok"
    assert sleep_calls == [32]


def test_call_gemini_uses_exponential_delay_for_non_503(monkeypatch):
    sleep_calls = []
    monkeypatch.setattr("weave.ai.client.time.sleep", sleep_calls.append)

    client = _DummyClient(
        [
            Exception("500 INTERNAL"),
            Exception("500 INTERNAL"),
            SimpleNamespace(text="ok"),
        ]
    )

    result = call_gemini(
        client,
        contents=["hello"],
        system_instruction="test",
        model="gemini-2.5-flash",
        max_retries=3,
        retry_base_delay=2,
        unavailable_retry_delay=30,
    )

    assert result == "ok"
    assert sleep_calls == [2, 6]
