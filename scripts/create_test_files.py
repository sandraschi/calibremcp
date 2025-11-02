"""
Create minimal test book files (EPUB, PDF, CBZ) for testing.

Creates very small but valid files that can be committed to GitHub.
"""
from pathlib import Path
import zipfile
import struct

TEST_LIBRARY_DIR = Path(__file__).parent.parent / "tests" / "fixtures" / "test_library"


def create_minimal_epub(output_path: Path, title: str = "Test Book", author: str = "Test Author"):
    """Create a minimal valid EPUB file."""
    # EPUB is just a ZIP file with specific structure
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as epub:
        # mimetype (must be first, uncompressed)
        epub.writestr('mimetype', 'application/epub+zip', compress_type=zipfile.ZIP_STORED)
        
        # META-INF/container.xml (required)
        epub.writestr('META-INF/container.xml', '''<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>''')
        
        # OEBPS/content.opf (package file)
        epub.writestr('OEBPS/content.opf', f'''<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="bookid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title>{title}</dc:title>
    <dc:creator>{author}</dc:creator>
    <dc:identifier id="bookid">test-book-id</dc:identifier>
  </metadata>
  <manifest>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
    <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine toc="ncx">
    <itemref idref="chapter1"/>
  </spine>
</package>''')
        
        # OEBPS/toc.ncx (table of contents)
        epub.writestr('OEBPS/toc.ncx', f'''<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="test-book-id"/>
  </head>
  <docTitle><text>{title}</text></docTitle>
  <navMap>
    <navPoint id="nav1" playOrder="1">
      <navLabel><text>Chapter 1</text></navLabel>
      <content src="OEBPS/chapter1.xhtml"/>
    </navPoint>
  </navMap>
</ncx>''')
        
        # OEBPS/chapter1.xhtml (content)
        epub.writestr('OEBPS/chapter1.xhtml', f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>Chapter 1</title>
</head>
<body>
  <h1>{title}</h1>
  <p>This is a minimal test EPUB file for automated testing.</p>
  <p>It contains just enough content to be a valid EPUB file.</p>
</body>
</html>''')


def create_minimal_pdf(output_path: Path, title: str = "Test Book"):
    """Create a minimal valid PDF file."""
    # Minimal PDF structure (just enough to be valid)
    pdf_content = b'''%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
/Resources <<
/Font <<
/F1 5 0 R
>>
>>
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(''' + title.encode('utf-8') + b''') Tj
ET
endstream
endobj
5 0 obj
<<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000317 00000 n 
0000000424 00000 n 
trailer
<<
/Size 6
/Root 1 0 R
>>
startxref
515
%%EOF'''
    
    output_path.write_bytes(pdf_content)


def create_minimal_cbz(output_path: Path, title: str = "Test Comic"):
    """Create a minimal valid CBZ file (ZIP of images)."""
    # CBZ is just a ZIP file with images
    # Create a minimal 1x1 pixel PNG
    # PNG signature + minimal IHDR chunk + IEND
    png_data = (
        b'\x89PNG\r\n\x1a\n'  # PNG signature
        b'\x00\x00\x00\r'  # IHDR chunk length
        b'IHDR'  # Chunk type
        b'\x00\x00\x00\x01'  # Width: 1 pixel
        b'\x00\x00\x00\x01'  # Height: 1 pixel
        b'\x08\x02'  # Bit depth: 8, Color type: RGB
        b'\x00\x00\x00'  # Compression, filter, interlace
        b'\x00\x00\x00\n'  # CRC (simplified)
        b'\x9a\x9c\x18\x00'  # CRC value
        b'\x00\x00\x00\x00'  # IEND chunk length
        b'IEND'  # Chunk type
        b'\xaeB`\x82'  # IEND CRC
    )
    
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as cbz:
        # Add a cover page
        cbz.writestr('00000.png', png_data)
        # Add a content page
        cbz.writestr('00001.png', png_data)


def create_test_files():
    """Create all test files for the test library."""
    print("Creating test book files...\n")
    
    # Book 1: A Study in Scarlet (EPUB + PDF)
    book1_dir = TEST_LIBRARY_DIR / "Arthur Conan Doyle" / "A Study in Scarlet (1)"
    book1_dir.mkdir(parents=True, exist_ok=True)
    
    epub1 = book1_dir / "1.epub"
    create_minimal_epub(epub1, "A Study in Scarlet", "Arthur Conan Doyle")
    print(f"✓ Created: {epub1.name} ({epub1.stat().st_size} bytes)")
    
    pdf1 = book1_dir / "1.pdf"
    create_minimal_pdf(pdf1, "A Study in Scarlet")
    print(f"✓ Created: {pdf1.name} ({pdf1.stat().st_size} bytes)")
    
    # Book 2: The Sign of the Four (EPUB)
    book2_dir = TEST_LIBRARY_DIR / "Arthur Conan Doyle" / "The Sign of the Four (2)"
    book2_dir.mkdir(parents=True, exist_ok=True)
    
    epub2 = book2_dir / "2.epub"
    create_minimal_epub(epub2, "The Sign of the Four", "Arthur Conan Doyle")
    print(f"✓ Created: {epub2.name} ({epub2.stat().st_size} bytes)")
    
    # Book 3: Pride and Prejudice (EPUB)
    book3_dir = TEST_LIBRARY_DIR / "Jane Austen" / "Pride and Prejudice (3)"
    book3_dir.mkdir(parents=True, exist_ok=True)
    
    epub3 = book3_dir / "3.epub"
    create_minimal_epub(epub3, "Pride and Prejudice", "Jane Austen")
    print(f"✓ Created: {epub3.name} ({epub3.stat().st_size} bytes)")
    
    # Book 4: Tom Sawyer (EPUB + CBZ for comic/manga test)
    book4_dir = TEST_LIBRARY_DIR / "Mark Twain" / "The Adventures of Tom Sawyer (4)"
    book4_dir.mkdir(parents=True, exist_ok=True)
    
    epub4 = book4_dir / "4.epub"
    create_minimal_epub(epub4, "The Adventures of Tom Sawyer", "Mark Twain")
    print(f"✓ Created: {epub4.name} ({epub4.stat().st_size} bytes)")
    
    # Add a CBZ file (comic format) - we'll need to update the database to include this
    cbz4 = book4_dir / "4.cbz"
    create_minimal_cbz(cbz4, "The Adventures of Tom Sawyer")
    print(f"✓ Created: {cbz4.name} ({cbz4.stat().st_size} bytes)")
    
    total_size = sum(f.stat().st_size for f in [epub1, pdf1, epub2, epub3, epub4, cbz4])
    print(f"\n✓ Created {6} test files")
    print(f"  Total size: {total_size / 1024:.1f} KB")
    print(f"\nAll test files ready in: {TEST_LIBRARY_DIR}")


if __name__ == "__main__":
    create_test_files()

