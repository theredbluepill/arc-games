"""Lightweight LLM stand-ins for local benchmark / CI runs (no Model Proxy)."""


class ReplayMockLLM:
    """Returns one character per ``prompt`` call from ``digits``, then ``fallback``."""

    def __init__(self, digits: str, fallback: str = "1") -> None:
        self._it = iter(digits)
        self._fallback = fallback

    def prompt(self, text: str) -> str:
        try:
            return next(self._it)
        except StopIteration:
            return self._fallback


class ConstantMockLLM:
    """Always returns the same response string."""

    def __init__(self, response: str) -> None:
        self._response = response

    def prompt(self, text: str) -> str:
        return self._response
