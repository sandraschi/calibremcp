# Comic OCR Strategy for CBZ Archives

**Date**: 2025-10-30  
**Status**: Strategy Document  
**Library**: Calibre Comics Library (207 CBZ files)  
**Goal**: Make scanned comics searchable through OCR

---

## Understanding CBZ Archives

### What are CBZ Files?

**CBZ = Comic Book ZIP**
- **Format**: Standard ZIP archive containing images
- **Extension**: `.cbz` (can be renamed to `.zip`)
- **Contents**: JPEG/JPG, PNG images representing comic pages
- **Reading Direction**: Typically left-to-right (Western comics) or right-to-left (Manga)

### Library Structure

```
L:\Multimedia Files\Written Word\Calibre-Bibliothek Comics\
├── Alan Moore\
│   └── Batman_ The Killing Joke Deluxe (56)\
│       └── Batman_ The Killing Joke Deluxe - Alan Moore.cbz  [65 pages]
├── [...]
└── 207 total CBZ files
```

**Sample Comic**: Batman: The Killing Joke  
- **Pages**: 65 images  
- **Structure**: Sequential numbered images  
- **Format**: JPG files in ZIP archive

---

## OCR Strategy

### **Option 1: Extract → OCR → Rebuild** ⭐ **RECOMMENDED**

**Workflow:**
1. **Extract**: Unzip CBZ to temporary directory
2. **OCR**: Process all images through FineReader
3. **Store**: Save OCR text to database/metadata
4. **Rebuild**: Create new CBZ with searchable text embedded
5. **Index**: Make text searchable in Calibre library

**Pros:**
- ✅ Preserves original comic structure
- ✅ OCR text stored as metadata (not in images)
- ✅ Fast search through indexed text
- ✅ No image quality degradation
- ✅ Works with existing comic readers

**Cons:**
- ⚠️ Processing time (65 pages × 30 seconds ≈ 32 minutes)
- ⚠️ Temporary storage needed during extraction

**Implementation:**
```python
async def ocr_comic_cbz(cbz_path: Path) -> Dict[str, Any]:
    """
    OCR a CBZ comic archive.
    
    Args:
        cbz_path: Path to CBZ file
        
    Returns:
        OCR results with searchable text per page
    """
    # 1. Extract CBZ to temp directory
    temp_dir = tempfile.TemporaryDirectory()
    zipfile.ZipFile(cbz_path).extractall(temp_dir.name)
    
    # 2. Get list of page images
    pages = sorted(Path(temp_dir.name).glob("*.jpg"))
    
    # 3. Process each page through OCR
    finereader = FineReaderCLI()
    ocr_results = []
    
    for page_num, page_img in enumerate(pages, 1):
        logger.info(f"OCR page {page_num}/{len(pages)}")
        
        # OCR single page
        result = await finereader.process_document(
            page_img,
            output_path=None,  # We don't need PDF output
            language="multilingual"  # Comics can have multiple languages
        )
        
        # Extract text from OCR result
        text = await extract_text_from_ocr_result(result)
        
        ocr_results.append({
            "page": page_num,
            "text": text,
            "confidence": result["confidence"]
        })
    
    # 4. Store OCR text in Calibre metadata
    await store_comic_ocr_metadata(cbz_path, ocr_results)
    
    # 5. Clean up
    temp_dir.cleanup()
    
    return {
        "success": True,
        "total_pages": len(pages),
        "ocr_results": ocr_results,
        "average_confidence": sum(r["confidence"] for r in ocr_results) / len(ocr_results)
    }
```

### **Option 2: Stream OCR (No Extraction)**

**Workflow:**
1. **Open**: Zipfile.open() to read images directly from archive
2. **Process**: OCR images from memory stream
3. **Store**: Save OCR text to database

**Pros:**
- ✅ No temporary extraction needed
- ✅ Lower disk I/O
- ✅ Faster overall

**Cons:**
- ⚠️ More complex implementation
- ⚠️ Memory usage for large archives

**Implementation:**
```python
async def ocr_comic_cbz_streaming(cbz_path: Path) -> Dict[str, Any]:
    """OCR CBZ without extracting to disk."""
    with zipfile.ZipFile(cbz_path, 'r') as zip_file:
        # Get list of pages
        pages = sorted([
            f for f in zip_file.namelist() 
            if f.lower().endswith(('.jpg', '.jpeg', '.png'))
        ])
        
        ocr_results = []
        finereader = FineReaderCLI()
        
        for page_num, page_name in enumerate(pages, 1):
            # Read page from archive
            with zip_file.open(page_name) as page_data:
                # Write to temp file for FineReader (it needs file path)
                temp_page = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
                temp_page.write(page_data.read())
                temp_page.close()
                
                # OCR
                result = await finereader.process_document(
                    temp_page.name,
                    language="multilingual"
                )
                
                ocr_results.append({
                    "page": page_num,
                    "text": await extract_text_from_ocr_result(result),
                    "confidence": result["confidence"]
                })
                
                # Clean up temp file
                os.unlink(temp_page.name)
    
    # Store OCR metadata
    await store_comic_ocr_metadata(cbz_path, ocr_results)
    
    return {
        "success": True,
        "total_pages": len(pages),
        "ocr_results": ocr_results
    }
```

### **Option 3: Hybrid Approach**

**Workflow:**
1. **Check**: If OCR already exists, skip
2. **Batch**: Process multiple comics together
3. **Cache**: Store OCR results for quick access
4. **Progressive**: OCR on-demand when comic is accessed

**Pros:**
- ✅ Efficient for large libraries
- ✅ On-demand processing
- ✅ Caching reduces redundant work

**Implementation:**
```python
async def ocr_comic_on_demand(cbz_path: Path, force: bool = False) -> Dict[str, Any]:
    """OCR comic only if needed."""
    # Check if OCR already exists
    ocr_db_path = cbz_path.with_suffix('.cbz.ocr.json')
    
    if not force and ocr_db_path.exists():
        logger.info(f"OCR cache exists for {cbz_path.name}")
        return json.loads(ocr_db_path.read_text())
    
    # Perform OCR
    result = await ocr_comic_cbz(cbz_path)
    
    # Cache result
    ocr_db_path.write_text(json.dumps(result, indent=2))
    
    return result
```

---

## Storage Strategy

### Where to Store OCR Text?

**Option A: Calibre Comments Field** ✅ **BEST**
```python
# Store in Calibre book metadata
book.comments += f"\n\n=== OCR Text ===\n{full_text}"
```

**Option B: Separate Metadata File**
```python
# Store alongside CBZ
comic.cbz → comic.cbz.ocr.json
{
    "pages": [
        {"page": 1, "text": "...", "confidence": 0.95},
        {"page": 2, "text": "...", "confidence": 0.92}
    ]
}
```

**Option C: Database Table** (Most Flexible)
```python
# Custom table in Calibre database
CREATE TABLE comic_ocr (
    book_id INTEGER PRIMARY KEY,
    page_number INTEGER,
    ocr_text TEXT,
    confidence REAL,
    processed_date TIMESTAMP
)
```

---

## Search Strategy

### **Full-Text Search Over OCR Text**

Once OCR text is stored, enable search:

```python
async def search_comics_by_text(query: str) -> List[Dict]:
    """Search across all comic OCR text."""
    results = []
    
    # Search through all OCR metadata
    for comic in all_comics:
        ocr_data = await get_comic_ocr_metadata(comic)
        
        if query.lower() in ocr_data['full_text'].lower():
            results.append({
                "title": comic.title,
                "matches": find_matching_pages(query, ocr_data['pages']),
                "confidence": ocr_data['average_confidence']
            })
    
    return sorted(results, key=lambda x: x['confidence'], reverse=True)
```

---

## Implementation Priority

### Phase 1: Core OCR for Comics (2-3 hours)
- [ ] Extract CBZ files to temp directory
- [ ] Process images through FineReader
- [ ] Store OCR text in Calibre comments
- [ ] Test with single comic

### Phase 2: Search Integration (1-2 hours)
- [ ] Full-text search over OCR text
- [ ] Page-level search with matches
- [ ] Confidence-based ranking

### Phase 3: Batch Processing (1-2 hours)
- [ ] Process all 207 comics
- [ ] Progress reporting
- [ ] Error handling for failed comics

### Phase 4: Optimization (2-3 hours)
- [ ] Streaming OCR (no extraction)
- [ ] Caching OCR results
- [ ] On-demand OCR

**Total**: ~6-10 hours focused development

---

## Usage Examples

### Basic OCR
```python
# OCR single comic
result = await calibre_ocr(
    operation="process",
    source="L:\\Multimedia Files\\Written Word\\Calibre-Bibliothek Comics\\Alan Moore\\Batman_ The Killing Joke Deluxe (56)\\Batman_ The Killing Joke Deluxe - Alan Moore.cbz",
    language="multilingual"
)
```

### Batch OCR
```python
# OCR all comics in library
result = await calibre_ocr(
    operation="batch_process",
    source="L:\\Multimedia Files\\Written Word\\Calibre-Bibliothek Comics",
    language="multilingual"
)
```

### Search Comics
```python
# Search comics by text
results = await search_books(
    text="Joker",
    filter="format:CBZ"
)
```

---

## CBR Support (Future)

**CBR = Comic Book RAR**
- Requires `rarfile` Python library
- Can extract with `unrar` command-line tool
- Same OCR strategy once extracted
- **Status**: Deferred (focus on CBZ first)

---

## Success Metrics

- ✅ OCR processing success rate > 95%
- ✅ Average processing time < 30 seconds per page
- ✅ Search returns relevant comics
- ✅ Page-level matches displayed
- ✅ Confidence scores > 85%

---

## Questions to Answer

1. **OCR all comics upfront or on-demand?**
   - **Recommendation**: Hybrid (on-demand with caching)
   
2. **Where to store OCR text?**
   - **Recommendation**: Calibre comments + separate metadata file for search index
   
3. **Process images or extracted pages?**
   - **Recommendation**: Extract first for simplicity, optimize later
   
4. **Multi-language support?**
   - **Recommendation**: "multilingual" for comics (bubbles in different languages)
   
5. **Rebuild CBZ or keep original?**
   - **Recommendation**: Keep original, store OCR separately (no quality loss)

---

## Conclusion

CBZ comics are ZIP archives with image pages. OCR strategy:
1. **Extract** CBZ to temporary directory
2. **Process** all images through FineReader
3. **Store** OCR text in searchable format
4. **Make** comics searchable by dialogue/bubbles

This enables searching comic libraries for quotes, character names, or story elements! 📚🦇

