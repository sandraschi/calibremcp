"""Tests for metadata RAG text normalization and env-driven limits."""

import pytest

from calibre_mcp.rag import text_utils


def test_strip_html_for_embedding_basic() -> None:
    assert text_utils.strip_html_for_embedding("") == ""
    assert text_utils.strip_html_for_embedding("plain") == "plain"
    assert text_utils.strip_html_for_embedding("<p>Hello &amp; world</p>") == "Hello & world"


def test_get_comment_max_chars_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CALIBRE_METADATA_COMMENT_MAX_CHARS", raising=False)
    assert text_utils.get_comment_max_chars() == 20 * 1024


def test_get_comment_max_chars_custom(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CALIBRE_METADATA_COMMENT_MAX_CHARS", "500000")
    assert text_utils.get_comment_max_chars() == 500_000


def test_get_comment_max_chars_clamp_high(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CALIBRE_METADATA_COMMENT_MAX_CHARS", str(10**9))
    assert text_utils.get_comment_max_chars() == 16_777_216


def test_get_comment_max_chars_invalid_falls_back(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CALIBRE_METADATA_COMMENT_MAX_CHARS", "not-a-number")
    assert text_utils.get_comment_max_chars() == 20 * 1024


def test_get_comment_max_chars_non_positive_falls_back(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CALIBRE_METADATA_COMMENT_MAX_CHARS", "0")
    assert text_utils.get_comment_max_chars() == 20 * 1024


def test_should_strip_html_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CALIBRE_METADATA_STRIP_HTML", raising=False)
    assert text_utils.should_strip_html_metadata() is True
    monkeypatch.setenv("CALIBRE_METADATA_STRIP_HTML", "0")
    assert text_utils.should_strip_html_metadata() is False
    monkeypatch.setenv("CALIBRE_METADATA_STRIP_HTML", "false")
    assert text_utils.should_strip_html_metadata() is False
