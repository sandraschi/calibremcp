"""Regression tests: series/comments shape tolerance + max_results cap.

Bug 1: two Book mappings coexist (db.models.Book.series is a list,
models/book.py::Book.series is a scalar property). Every formatter assumed
one shape and crashed on the other with
TypeError: 'Series' object is not subscriptable (by_author path).

Bug 2: full-text search fetched up to 10000 IDs with snippets and timed out.
get_all() now takes max_results (default 20) and stops early; empty results
say "No matching books found" instead of timing out.
"""

import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from calibre_mcp.db.database import close_database, init_database
from calibre_mcp.db.models import first_comment, first_series


def _series(id, name):
    return SimpleNamespace(id=id, name=name)


def test_first_series_list_shape():
    book = SimpleNamespace(series=[_series(3, "Dune"), _series(9, "Other")])
    assert first_series(book).name == "Dune"


def test_first_series_scalar_shape():
    book = SimpleNamespace(series=_series(7, "Fell"))
    assert first_series(book).id == 7


def test_first_series_empty_shapes():
    assert first_series(SimpleNamespace(series=[])) is None
    assert first_series(SimpleNamespace(series=None)) is None
    assert first_series(SimpleNamespace()) is None


def test_first_comment_both_shapes():
    assert first_comment(SimpleNamespace(comments=[SimpleNamespace(text="hi")])).text == "hi"
    assert first_comment(SimpleNamespace(comments=SimpleNamespace(text="yo"))).text == "yo"
    assert first_comment(SimpleNamespace(comments=[])) is None
    assert first_comment(SimpleNamespace(comments=None)) is None


def _fixture_db():
    db_path = Path(__file__).parent / "fixtures" / "test_library" / "metadata.db"
    assert db_path.exists(), "fixture test_library/metadata.db missing"
    init_database(str(db_path), echo=False)
    return db_path


def _stub_book(series):
    return SimpleNamespace(
        id=1,
        title="T",
        sort="T",
        timestamp=None,
        pubdate=None,
        series_index=1.0,
        author_sort="A",
        path="p",
        has_cover=0,
        uuid=None,
        last_modified=None,
        identifiers=[],
        authors=[],
        tags=[],
        series=series,
        ratings=[],
        publishers=[],
    )


def test_to_response_scalar_series_shape():
    from calibre_mcp.services.book_service import book_service

    out = book_service._to_response(_stub_book(_series(7, "Fell")))
    assert out["series"] == {"id": 7, "name": "Fell"}


def test_to_response_list_series_shape():
    from calibre_mcp.services.book_service import book_service

    out = book_service._to_response(_stub_book([_series(3, "Dune")]))
    assert out["series"] == {"id": 3, "name": "Dune"}
    out_none = book_service._to_response(_stub_book(None))
    assert out_none["series"] is None


def test_max_results_caps_fetch():
    _fixture_db()
    try:
        from calibre_mcp.services.book_service import book_service

        result = book_service.get_all(search="e", max_results=3, limit=50)
        assert len(result["items"]) <= 3
    finally:
        close_database()


def test_empty_search_says_no_matching_books():
    _fixture_db()
    try:
        from calibre_mcp.services.book_service import book_service

        result = book_service.get_all(search="zzz-no-such-book-xyz-123", max_results=20)
        assert result["total"] == 0
        assert result.get("message", "").startswith("No matching books found")
    finally:
        close_database()
