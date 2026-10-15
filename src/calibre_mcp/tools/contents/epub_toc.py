"""EPUB table-of-contents extraction (stdlib only).

Reads NCX (EPUB 2) or nav (EPUB 3) navmaps and returns contained works with
nesting depth. Group headers (entries that contain other entries) are flagged
so UIs can render Delphi-style "The Novels / The Novellas" structure.
Falls back to spine filenames when no navmap exists (weak signal, marked).
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Any

_NCX_NS = {"n": "http://www.daisy.org/z3986/2005/ncx/"}
_OPF_NS = {"o": "http://www.idpf.org/2007/opf"}
_CONT_NS = {"c": "urn:oasis:names:tc:opendocument:xmlns:container"}


def _clean(text: str | None) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()


def _parse_ncx(z: zipfile.ZipFile, ncx_path: str) -> list[dict[str, Any]]:
    nx = ET.fromstring(z.read(ncx_path))
    parent = {c: p for p in nx.iter() for c in p}
    points = nx.findall(".//n:navPoint", _NCX_NS)
    works: list[dict[str, Any]] = []
    for p in points:
        depth = 1
        q = p
        while parent.get(q) is not None and parent[q].tag.endswith("navPoint"):
            depth += 1
            q = parent[q]
        label_el = p.find("n:navLabel/n:text", _NCX_NS)
        content_el = p.find("n:content", _NCX_NS)
        src = (content_el.get("src", "") if content_el is not None else "").split("#")[0]
        works.append(
            {
                "title": _clean(label_el.text if label_el is not None else ""),
                "href": src,
                "depth": depth,
                "is_group": False,  # fixed up below (points with children)
            }
        )
    # group = has children
    for w, p in zip(works, points, strict=False):
        w["is_group"] = any(True for _ in p.findall("n:navPoint", _NCX_NS))
    return [w for w in works if w["title"]]


def _parse_nav(z: zipfile.ZipFile, nav_path: str) -> list[dict[str, Any]]:
    from html.parser import HTMLParser

    raw = z.read(nav_path).decode("utf-8", errors="replace")

    class NavParser(HTMLParser):
        def __init__(self) -> None:
            super().__init__()
            self.in_nav = False
            self.depth = 0
            self.works: list[dict[str, Any]] = []
            self._href = ""
            self._text = ""
            self._in_a = False
            self._stack: list[int] = []

        def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
            d = dict(attrs)
            if tag == "nav":
                epub_type = (d.get("epub:type") or "") + (d.get("type") or "")
                if "toc" in epub_type or not self.in_nav:
                    # first nav is usually the toc; nested nav unlikely
                    if not self.works:
                        self.in_nav = True
            if not self.in_nav:
                return
            if tag == "ol":
                self.depth += 1
            if tag == "a":
                self._href = (d.get("href") or "").split("#")[0]
                self._text = ""
                self._in_a = True
                self._stack.append(len(self.works))

        def handle_data(self, data: str) -> None:
            if self.in_nav and self._in_a:
                self._text += data

        def handle_endtag(self, tag: str) -> None:
            if not self.in_nav:
                return
            if tag == "a" and self._in_a:
                self._in_a = False
                title = _clean(self._text)
                if title:
                    self.works.append(
                        {"title": title, "href": self._href, "depth": max(self.depth, 1), "is_group": False}
                    )
            if tag == "ol":
                self.depth = max(0, self.depth - 1)
            if tag == "nav" and not self._stack:
                pass

    p = NavParser()
    p.feed(raw)
    # groups: entries whose href is a prefix-container or that repeat as section heads —
    # conservative: only flag depth transitions (a depth-1 entry followed by depth-2 runs)
    works = p.works
    for i, w in enumerate(works):
        nxt = works[i + 1]["depth"] if i + 1 < len(works) else 0
        if w["depth"] == 1 and nxt == 2:
            w["is_group"] = True
    return works


def _spine_fallback(z: zipfile.ZipFile, opf_path: str) -> list[dict[str, Any]]:
    opf = ET.fromstring(z.read(opf_path))
    opf_dir = "/".join(opf_path.split("/")[:-1])
    manifest = {}
    for item in opf.findall("o:manifest/o:item", _OPF_NS):
        href = item.get("href", "")
        if opf_dir:
            href = f"{opf_dir}/{href}"
        manifest[item.get("id")] = href
    spine = opf.find("o:spine", _OPF_NS)
    works = []
    if spine is not None:
        for ref in spine.findall("o:itemref", _OPF_NS):
            href = manifest.get(ref.get("idref", ""), "")
            if href.lower().endswith((".xhtml", ".html", ".htm", ".xml")):
                name = Path(href).stem.replace("_", " ").replace("-", " ").strip()
                works.append({"title": name or href, "href": href, "depth": 0, "is_group": False})
    return works


def parse_epub_toc(epub_path: str | Path) -> dict[str, Any]:
    """Parse an EPUB's navmap. Never raises — errors come back in the dict."""
    try:
        z = zipfile.ZipFile(str(epub_path))
    except Exception as e:
        return {"ok": False, "error": f"cannot open epub: {e}", "works": [], "source": "none"}
    try:
        names = z.namelist()
        try:
            container = ET.fromstring(z.read("META-INF/container.xml"))
            rootfile = container.find("c:rootfiles/c:rootfile", _CONT_NS)
            opf_path = rootfile.get("full-path") if rootfile is not None else None
        except Exception:
            opf_path = None
        if not opf_path:
            opfs = [n for n in names if n.lower().endswith(".opf")]
            opf_path = opfs[0] if opfs else None
        if not opf_path:
            return {"ok": False, "error": "no OPF found", "works": [], "source": "none"}

        opf = ET.fromstring(z.read(opf_path))
        opf_dir = "/".join(opf_path.split("/")[:-1])
        manifest = {}
        for item in opf.findall("o:manifest/o:item", _OPF_NS):
            href = item.get("href", "")
            if opf_dir and not href.startswith(("http:", "https:")):
                href = f"{opf_dir}/{href}"
            manifest[item.get("id")] = (href, item.get("media-type", ""))

        ncx = [h for (h, mt) in manifest.values() if h.endswith(".ncx") or (mt or "").endswith("ncx")]
        if ncx and ncx[0] in names:
            works = _parse_ncx(z, ncx[0])
            # drop group-only headers from work counts? No — report all, flag groups.
            return {"ok": True, "source": "ncx", "works": works}

        navs = [h for (h, mt) in manifest.values() if h in names and h.lower().endswith((".xhtml", ".html", ".htm"))]
        # prefer files with 'nav' or 'toc' in the name
        navs.sort(key=lambda h: (0 if "nav" in h.lower() or "toc" in h.lower() else 1, h))
        for nav in navs[:3]:
            try:
                works = _parse_nav(z, nav)
            except Exception:
                continue
            if len(works) >= 5:
                return {"ok": True, "source": "nav", "works": works}

        works = _spine_fallback(z, opf_path)
        return {"ok": True, "source": "spine", "works": works, "weak": True}
    except Exception as e:
        return {"ok": False, "error": f"toc parse failed: {e}", "works": [], "source": "none"}
    finally:
        try:
            z.close()
        except Exception:
            pass


TITLE_PATTERNS = (
    "complete works",
    "collected works",
    "complete novels",
    "complete stories",
    "complete short stories",
    "omnibus",
    "ultimate collection",
    "collected stories",
    "entire works",
)

TAG_PATTERNS = (
    "complete works",
    "collected works",
    "delphi classics",
    "omnibus",
)


def looks_like_collection(title: str, tags: list[str] | None) -> bool:
    """Metadata-only heuristic (no file reads)."""
    t = (title or "").lower()
    if any(p in t for p in TITLE_PATTERNS):
        return True
    for tag in tags or []:
        if (tag or "").lower() in TAG_PATTERNS:
            return True
    return False
