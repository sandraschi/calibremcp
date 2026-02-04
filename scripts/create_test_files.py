"""
Create minimal test book files (EPUB, PDF, CBZ) for testing.

Creates very small but valid files that can be committed to GitHub.
"""

import zipfile
from pathlib import Path

TEST_LIBRARY_DIR = Path(__file__).parent.parent / "tests" / "fixtures" / "test_library"


def create_minimal_epub(
    output_path: Path, title: str = "Test Book", author: str = "Test Author", num_pages: int = 5
):
    """Create a minimal valid EPUB file with specified number of pages."""
    # EPUB is just a ZIP file with specific structure
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as epub:
        # mimetype (must be first, uncompressed)
        epub.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)

        # META-INF/container.xml (required)
        epub.writestr(
            "META-INF/container.xml",
            """<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>""",
        )

        # Generate manifest and spine items for all pages
        manifest_items = '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>'
        spine_items = ""
        nav_points = ""

        for i in range(1, num_pages + 1):
            manifest_items += f'\n    <item id="page{i}" href="page{i}.xhtml" media-type="application/xhtml+xml"/>'
            spine_items += f'\n    <itemref idref="page{i}"/>'
            nav_points += f"""
    <navPoint id="nav{i}" playOrder="{i}">
      <navLabel><text>Page {i}</text></navLabel>
      <content src="OEBPS/page{i}.xhtml"/>
    </navPoint>"""

        # OEBPS/content.opf (package file)
        epub.writestr(
            "OEBPS/content.opf",
            f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="bookid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title>{title}</dc:title>
    <dc:creator>{author}</dc:creator>
    <dc:identifier id="bookid">test-book-id</dc:identifier>
  </metadata>
  <manifest>
    {manifest_items}
  </manifest>
  <spine toc="ncx">
    {spine_items}
  </spine>
</package>""",
        )

        # OEBPS/toc.ncx (table of contents)
        epub.writestr(
            "OEBPS/toc.ncx",
            f"""<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="test-book-id"/>
  </head>
  <docTitle><text>{title}</text></docTitle>
  <navMap>
    {nav_points}
  </navMap>
</ncx>""",
        )

        # Create 5 pages of content
        for i in range(1, num_pages + 1):
            epub.writestr(
                f"OEBPS/page{i}.xhtml",
                f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>Page {i}</title>
</head>
<body>
  <h1>{title}</h1>
  <h2>Page {i} of {num_pages}</h2>
  <p>This is page {i} of a minimal test EPUB file for automated testing.</p>
  <p>It contains just enough content to be a valid EPUB file with multiple pages.</p>
  <p>Each page has unique content to test page navigation and viewing functionality.</p>
</body>
</html>""",
            )


def create_minimal_pdf(output_path: Path, title: str = "Test Book", num_pages: int = 5):
    """Create a minimal valid PDF file with specified number of pages."""
    # Simplified PDF structure - build incrementally
    parts = []
    obj_num = 1
    offsets = {}

    # Catalog (obj 1)
    catalog_obj = f"""{obj_num} 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj"""
    offsets[obj_num] = len(b"%PDF-1.4\n")
    parts.append(catalog_obj.encode("utf-8"))
    obj_num += 1

    # Pages object (obj 2)
    # We'll update this after creating all page objects
    pages_obj_num = obj_num
    obj_num += 1

    # Font object (obj 3)
    font_obj_num = obj_num
    font_obj = f"""{font_obj_num} 0 obj
<<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
endobj"""
    parts.append(font_obj.encode("utf-8"))
    obj_num += 1

    # Create pages (each page needs 2 objects: page + content)
    page_obj_nums = []
    for page_num in range(1, num_pages + 1):
        page_obj_num = obj_num
        content_obj_num = obj_num + 1
        page_obj_nums.append(page_obj_num)
        obj_num += 2

        # Content stream
        page_text = f"Page {page_num} of {num_pages} - {title}"
        content_text = f"BT\n/F1 12 Tf\n100 700 Td\n({page_text}) Tj\nET"
        content_obj = f"""{content_obj_num} 0 obj
<<
/Length {len(content_text)}
>>
stream
{content_text}
endstream
endobj"""
        parts.append(content_obj.encode("utf-8"))

        # Page object
        page_obj = f"""{page_obj_num} 0 obj
<<
/Type /Page
/Parent {pages_obj_num} 0 R
/MediaBox [0 0 612 792]
/Contents {content_obj_num} 0 R
/Resources <<
/Font <<
/F1 {font_obj_num} 0 R
>>
>>
>>
endobj"""
        parts.append(page_obj.encode("utf-8"))

    # Now create Pages object with all page references
    kids_list = " ".join([f"{num} 0 R" for num in page_obj_nums])
    pages_obj = f"""{pages_obj_num} 0 obj
<<
/Type /Pages
/Kids [{kids_list}]
/Count {num_pages}
>>
endobj"""
    parts.insert(1, pages_obj.encode("utf-8"))  # Insert after catalog

    # Build PDF
    pdf_header = b"%PDF-1.4\n"
    body = b"\n".join(parts)

    # Calculate xref offsets
    xref_start = len(pdf_header) + len(body) + 1
    xref_entries = [b"0000000000 65535 f "]
    current_offset = len(pdf_header)

    for part in parts:
        xref_entries.append(f"{current_offset:010d} 00000 n ".encode())
        current_offset += len(part) + 1  # +1 for newline

    xref_table = b"xref\n0 " + str(len(xref_entries)).encode() + b"\n" + b"\n".join(xref_entries)

    # Trailer
    trailer = f"""trailer
<<
/Size {len(xref_entries)}
/Root 1 0 R
>>
startxref
{xref_start}
%%EOF"""

    pdf_content = pdf_header + body + b"\n" + xref_table + b"\n" + trailer.encode("utf-8")
    output_path.write_bytes(pdf_content)


def create_minimal_cbz(output_path: Path, title: str = "Test Comic", num_pages: int = 5):
    """Create a minimal valid CBZ file (ZIP of images) with specified number of pages."""

    # CBZ is just a ZIP file with images
    # Create a minimal 100x100 pixel PNG (small but visible)
    # PNG signature + minimal IHDR chunk + IEND
    def create_png_image():
        return (
            b"\x89PNG\r\n\x1a\n"  # PNG signature
            b"\x00\x00\x00\r"  # IHDR chunk length
            b"IHDR"  # Chunk type
            b"\x00\x00\x00d"  # Width: 100 pixels
            b"\x00\x00\x00d"  # Height: 100 pixels
            b"\x08\x02"  # Bit depth: 8, Color type: RGB
            b"\x00\x00\x00"  # Compression, filter, interlace
            b"\x00\x00\x00\n"  # CRC (simplified)
            b"\x9a\x9c\x18\x00"  # CRC value
            b"\x00\x00\x00\x00"  # IEND chunk length
            b"IEND"  # Chunk type
            b"\xaeB`\x82"  # IEND CRC
        )

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as cbz:
        # Add pages (numbered 00000, 00001, etc.)
        for page_num in range(num_pages):
            page_filename = f"{page_num:05d}.png"
            cbz.writestr(page_filename, create_png_image())


def create_test_files():
    """Create all test files for the test library."""
    print("Creating test book files...\n")

    # Book 1: A Study in Scarlet (EPUB + PDF)
    book1_dir = TEST_LIBRARY_DIR / "Arthur Conan Doyle" / "A Study in Scarlet (1)"
    book1_dir.mkdir(parents=True, exist_ok=True)

    epub1 = book1_dir / "1.epub"
    create_minimal_epub(epub1, "A Study in Scarlet", "Arthur Conan Doyle", num_pages=5)
    print(f"[OK] Created: {epub1.name} ({epub1.stat().st_size} bytes, 5 pages)")

    pdf1 = book1_dir / "1.pdf"
    create_minimal_pdf(pdf1, "A Study in Scarlet", num_pages=5)
    print(f"[OK] Created: {pdf1.name} ({pdf1.stat().st_size} bytes, 5 pages)")

    # Book 2: The Sign of the Four (EPUB)
    book2_dir = TEST_LIBRARY_DIR / "Arthur Conan Doyle" / "The Sign of the Four (2)"
    book2_dir.mkdir(parents=True, exist_ok=True)

    epub2 = book2_dir / "2.epub"
    create_minimal_epub(epub2, "The Sign of the Four", "Arthur Conan Doyle", num_pages=5)
    print(f"[OK] Created: {epub2.name} ({epub2.stat().st_size} bytes, 5 pages)")

    # Book 3: Pride and Prejudice (EPUB)
    book3_dir = TEST_LIBRARY_DIR / "Jane Austen" / "Pride and Prejudice (3)"
    book3_dir.mkdir(parents=True, exist_ok=True)

    epub3 = book3_dir / "3.epub"
    create_minimal_epub(epub3, "Pride and Prejudice", "Jane Austen", num_pages=5)
    print(f"[OK] Created: {epub3.name} ({epub3.stat().st_size} bytes, 5 pages)")

    # Book 4: Tom Sawyer (EPUB + CBZ for comic/manga test)
    book4_dir = TEST_LIBRARY_DIR / "Mark Twain" / "The Adventures of Tom Sawyer (4)"
    book4_dir.mkdir(parents=True, exist_ok=True)

    epub4 = book4_dir / "4.epub"
    create_minimal_epub(epub4, "The Adventures of Tom Sawyer", "Mark Twain", num_pages=5)
    print(f"[OK] Created: {epub4.name} ({epub4.stat().st_size} bytes, 5 pages)")

    # Add a CBZ file (comic format) with 5 pages
    cbz4 = book4_dir / "4.cbz"
    create_minimal_cbz(cbz4, "The Adventures of Tom Sawyer", num_pages=5)
    print(f"[OK] Created: {cbz4.name} ({cbz4.stat().st_size} bytes, 5 pages)")

    total_size = sum(f.stat().st_size for f in [epub1, pdf1, epub2, epub3, epub4, cbz4])
    print(f"\n[OK] Created {6} test files")
    print(f"  Total size: {total_size / 1024:.1f} KB")
    print(f"\nAll test files ready in: {TEST_LIBRARY_DIR}")


if __name__ == "__main__":
    create_test_files()
