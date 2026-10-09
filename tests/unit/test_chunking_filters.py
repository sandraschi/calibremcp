"""Chunk RAG env filters (format exclusion, max text size)."""

import pytest

from calibre_mcp.rag.chunking import (
    _exclude_formats_from_env,
    _max_book_text_chars_from_env,
)


def test_exclude_default_is_pdf_when_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CALIBRE_RAG_CHUNK_EXCLUDE_FORMATS", raising=False)
    assert _exclude_formats_from_env() == {"PDF"}


def test_exclude_empty_string_means_no_exclusion(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CALIBRE_RAG_CHUNK_EXCLUDE_FORMATS", "")
    assert _exclude_formats_from_env() == set()


def test_exclude_list(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CALIBRE_RAG_CHUNK_EXCLUDE_FORMATS", "PDF, EPUB")
    assert _exclude_formats_from_env() == {"PDF", "EPUB"}


def test_max_book_text_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CALIBRE_RAG_MAX_BOOK_TEXT_CHARS", raising=False)
    assert _max_book_text_chars_from_env() is None


def test_max_book_text_positive(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CALIBRE_RAG_MAX_BOOK_TEXT_CHARS", "5000000")
    assert _max_book_text_chars_from_env() == 5_000_000


def test_max_book_text_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CALIBRE_RAG_MAX_BOOK_TEXT_CHARS", "x")
    assert _max_book_text_chars_from_env() is None
