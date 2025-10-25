"""Extended library operations for CalibreMCP."""
from typing import Dict, List
import os
import shutil
import re
import zipfile
from datetime import datetime
from collections import defaultdict

from fastmcp import MCPTool
from pydantic import BaseModel, Field

# Models
class LibraryStats(BaseModel):
    """Detailed library statistics."""
    total_books: int = 0
    total_authors: int = 0
    total_series: int = 0
    total_tags: int = 0
    total_file_size: int = 0  # in bytes
    formats: Dict[str, int] = Field(default_factory=dict)
    languages: Dict[str, int] = Field(default_factory=dict)
    publishers: Dict[str, int] = Field(default_factory=dict)
    publication_years: Dict[int, int] = Field(default_factory=dict)
    ratings: Dict[int, int] = Field(default_factory=dict)
    added_dates: Dict[str, int] = Field(default_factory=dict)
    tag_cloud: Dict[str, int] = Field(default_factory=dict)

class BookDuplicates(BaseModel):
    """Information about duplicate books."""
    book_id: str
    title: str
    authors: List[str]
    formats: List[str]
    file_paths: List[str]
    file_sizes: List[int]
    is_duplicate: bool = True
    duplicate_group: int

class LibraryBackupConfig(BaseModel):
    """Configuration for library backup operations."""
    backup_dir: str
    max_backups: int = 5
    compress: bool = True
    include_metadata: bool = True
    include_books: bool = True
    include_covers: bool = True

# Main tool
class ExtendedLibraryOperations(MCPTool):
    """Extended library operations for CalibreMCP."""
    
    name = "extended_library_ops"
    description = "Extended library operations including maintenance, cleanup, and analysis"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._backup_configs = {}
    
    # Library Analysis
    async def analyze_library(self, library_path: str) -> Dict:
        """Generate detailed statistics about the library."""
        from calibre_plugins.calibremcp.storage.local import LocalStorage
        
        storage = LocalStorage(library_path)
        books = await storage.get_all_books()
        
        stats = LibraryStats()
        stats.total_books = len(books)
        
        authors = set()
        series = set()
        tags = set()
        
        for book in books:
            # Count formats
            for fmt in book.get('formats', []):
                stats.formats[fmt.lower()] = stats.formats.get(fmt.lower(), 0) + 1
            
            # Count languages
            lang = book.get('language', 'Unknown')
            stats.languages[lang] = stats.languages.get(lang, 0) + 1
            
            # Count publishers
            publisher = book.get('publisher', 'Unknown')
            if publisher:
                stats.publishers[publisher] = stats.publishers.get(publisher, 0) + 1
            
            # Count publication years
            pub_year = book.get('pubdate', '')
            if pub_year and isinstance(pub_year, str) and pub_year.isdigit():
                year = int(pub_year)
                stats.publication_years[year] = stats.publication_years.get(year, 0) + 1
            
            # Count ratings
            rating = book.get('rating', 0)
            if rating and isinstance(rating, (int, float)) and 1 <= rating <= 5:
                stats.ratings[int(rating)] = stats.ratings.get(int(rating), 0) + 1
            
            # Count added dates
            added = book.get('timestamp', '')
            if added and isinstance(added, str) and 'T' in added:
                date_str = added.split('T')[0]
                stats.added_dates[date_str] = stats.added_dates.get(date_str, 0) + 1
            
            # Collect unique values
            if 'authors' in book and book['authors']:
                authors.update(book['authors'])
            
            if 'series' in book and book['series']:
                series.add(book['series'])
            
            if 'tags' in book and book['tags']:
                for tag in book['tags']:
                    tags.add(tag)
                    stats.tag_cloud[tag] = stats.tag_cloud.get(tag, 0) + 1
            
            # Calculate total file size
            if 'files' in book and book['files']:
                for file_info in book['files'].values():
                    stats.total_file_size += file_info.get('size', 0)
        
        # Set unique counts
        stats.total_authors = len(authors)
        stats.total_series = len(series)
        stats.total_tags = len(tags)
        
        # Sort tag cloud by count (descending)
        stats.tag_cloud = dict(sorted(
            stats.tag_cloud.items(), 
            key=lambda x: x[1], 
            reverse=True
        ))
        
        return {"success": True, "stats": stats.dict()}
    
    # Duplicate Detection
    async def find_duplicates(self, 
                            library_path: str, 
                            check_fields: List[str] = ['title', 'authors'],
                            min_similarity: float = 0.9) -> Dict:
        """Find duplicate books in the library."""
        from calibre_plugins.calibremcp.storage.local import LocalStorage
        
        storage = LocalStorage(library_path)
        books = await storage.get_all_books()
        
        # Group books by normalized title and authors
        groups = defaultdict(list)
        
        for book in books:
            if not book.get('id'):
                continue
                
            key_parts = []
            
            if 'title' in check_fields:
                title = book.get('title', '').lower().strip()
                title = re.sub(r'\s*\([^)]*\)\s*', ' ', title)
                title = re.sub(r'\s*\[[^]]*\]\s*', ' ', title)
                title = re.sub(r'\s+', ' ', title).strip()
                key_parts.append(title)
            
            if 'authors' in check_fields and book.get('authors'):
                authors = ', '.join(sorted(a.lower().strip() for a in book['authors']))
                key_parts.append(authors)
            
            if 'isbn' in check_fields and book.get('identifiers', {}).get('isbn'):
                isbn = book['identifiers']['isbn']
                isbn = re.sub(r'[^0-9Xx]', '', isbn.upper())
                if isbn:
                    key_parts.append(f"isbn:{isbn}")
            
            if not key_parts:
                continue
                
            key = '|'.join(key_parts)
            groups[key].append(book)
        
        # Find groups with potential duplicates
        duplicate_groups = []
        group_id = 0
        
        for key, book_group in groups.items():
            if len(book_group) < 2:
                continue
                
            similar_books = []
            
            for i, book1 in enumerate(book_group):
                if not book1.get('id'):
                    continue
                
                current_group = [book1]
                
                for book2 in book_group[i+1:]:
                    if not book2.get('id'):
                        continue
                    
                    similarity = self._calculate_book_similarity(book1, book2, check_fields)
                    
                    if similarity >= min_similarity:
                        current_group.append(book2)
                
                if len(current_group) > 1:
                    group_id += 1
                    
                    for book in current_group:
                        formats = []
                        file_paths = []
                        file_sizes = []
                        
                        if 'files' in book and book['files']:
                            for fmt, file_info in book['files'].items():
                                formats.append(fmt)
                                file_paths.append(file_info.get('path', ''))
                                file_sizes.append(file_info.get('size', 0))
                        
                        added_date = None
                        if 'timestamp' in book and book['timestamp']:
                            try:
                                added_date = datetime.fromisoformat(book['timestamp'].replace('Z', '+00:00'))
                            except (ValueError, AttributeError):
                                pass
                        
                        similar_books.append({
                            'book_id': book['id'],
                            'title': book.get('title', 'Unknown Title'),
                            'authors': book.get('authors', []),
                            'formats': formats,
                            'file_paths': file_paths,
                            'file_sizes': file_sizes,
                            'added_date': added_date.isoformat() if added_date else None,
                            'is_duplicate': True,
                            'duplicate_group': group_id
                        })
            
            if similar_books:
                duplicate_groups.extend(similar_books)
        
        return {
            "success": True,
            "duplicates": duplicate_groups,
            "total_duplicates": len(duplicate_groups),
            "duplicate_groups": group_id
        }
    
    def _calculate_book_similarity(self, book1: Dict, book2: Dict, check_fields: List[str]) -> float:
        """Calculate similarity between two books (0.0 to 1.0)."""
        from difflib import SequenceMatcher
        
        if not book1 or not book2:
            return 0.0
        
        scores = []
        
        if 'title' in check_fields:
            title1 = book1.get('title', '').lower()
            title2 = book2.get('title', '').lower()
            title_sim = SequenceMatcher(None, title1, title2).ratio()
            scores.append(('title', title_sim))
        
        if 'authors' in check_fields:
            authors1 = set(a.lower() for a in book1.get('authors', []))
            authors2 = set(a.lower() for a in book2.get('authors', []))
            
            if authors1 and authors2:
                intersection = len(authors1 & authors2)
                union = len(authors1 | authors2)
                author_sim = intersection / union if union > 0 else 0.0
                scores.append(('authors', author_sim))
        
        if 'isbn' in check_fields:
            isbn1 = book1.get('identifiers', {}).get('isbn', '')
            isbn2 = book2.get('identifiers', {}).get('isbn', '')
            
            if isbn1 and isbn2:
                isbn1 = re.sub(r'[^0-9Xx]', '', isbn1.upper())
                isbn2 = re.sub(r'[^0-9Xx]', '', isbn2.upper())
                
                if len(isbn1) == 10 and len(isbn2) == 13:
                    isbn1 = '978' + isbn1[:-1] + self._calculate_isbn13_check_digit('978' + isbn1[:-1])
                elif len(isbn1) == 13 and len(isbn2) == 10:
                    isbn2 = '978' + isbn2[:-1] + self._calculate_isbn13_check_digit('978' + isbn2[:-1])
                
                isbn_sim = 1.0 if isbn1 == isbn2 else 0.0
                scores.append(('isbn', isbn_sim))
        
        if not scores:
            return 0.0
        
        weights = {
            'title': 0.5,
            'authors': 0.4,
            'isbn': 0.9
        }
        
        total_weight = 0.0
        weighted_sum = 0.0
        
        for field, score in scores:
            weight = weights.get(field, 0.1)
            weighted_sum += score * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _calculate_isbn13_check_digit(self, isbn: str) -> str:
        """Calculate the check digit for an ISBN-13."""
        if len(isbn) != 12:
            return ''
        
        total = 0
        for i, c in enumerate(isbn):
            digit = int(c)
            total += digit * (1 if i % 2 == 0 else 3)
        
        check_digit = (10 - (total % 10)) % 10
        return str(check_digit)
    
    # Library Backup
    async def backup_library(self, 
                           library_path: str, 
                           backup_dir: str,
                           max_backups: int = 5,
                           compress: bool = True) -> Dict:
        """Create a backup of the library."""
        if not os.path.isdir(library_path):
            return {"error": f"Library directory not found: {library_path}", "success": False}
        
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"calibre_backup_{timestamp}"
        backup_path = os.path.join(backup_dir, backup_name)
        
        try:
            if compress:
                backup_path += '.zip'
                with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    # Add metadata.db
                    metadata_db = os.path.join(library_path, 'metadata.db')
                    if os.path.exists(metadata_db):
                        zipf.write(metadata_db, os.path.join(backup_name, 'metadata.db'))
                    
                    # Add books
                    books_dir = os.path.join(library_path, 'books')
                    if os.path.isdir(books_dir):
                        for root, _, files in os.walk(books_dir):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.join(backup_name, 'books', os.path.relpath(file_path, books_dir))
                                zipf.write(file_path, arcname)
                    
                    # Add covers
                    covers_dir = os.path.join(library_path, 'covers')
                    if os.path.isdir(covers_dir):
                        for root, _, files in os.walk(covers_dir):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.join(backup_name, 'covers', os.path.relpath(file_path, covers_dir))
                                zipf.write(file_path, arcname)
            else:
                backup_path = os.path.join(backup_path, os.path.basename(library_path))
                
                def copy_dir(src, dst):
                    if not os.path.isdir(src):
                        return
                    
                    os.makedirs(dst, exist_ok=True)
                    for item in os.listdir(src):
                        s = os.path.join(src, item)
                        d = os.path.join(dst, item)
                        
                        if os.path.isdir(s):
                            copy_dir(s, d)
                        else:
                            shutil.copy2(s, d)
                
                # Copy metadata.db
                metadata_db = os.path.join(library_path, 'metadata.db')
                if os.path.exists(metadata_db):
                    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                    shutil.copy2(metadata_db, os.path.join(backup_path, 'metadata.db'))
                
                # Copy books and covers
                copy_dir(os.path.join(library_path, 'books'), os.path.join(backup_path, 'books'))
                copy_dir(os.path.join(library_path, 'covers'), os.path.join(backup_path, 'covers'))
            
            # Clean up old backups
            if max_backups > 0:
                self._cleanup_old_backups(backup_dir, max_backups)
            
            return {
                "success": True,
                "backup_path": backup_path,
                "backup_size": os.path.getsize(backup_path) if os.path.exists(backup_path) else 0,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "error": f"Backup failed: {str(e)}",
                "success": False
            }
    
    def _cleanup_old_backups(self, backup_dir: str, max_backups: int):
        """Remove old backups, keeping only the most recent max_backups."""
        try:
            backups = []
            
            for item in os.listdir(backup_dir):
                path = os.path.join(backup_dir, item)
                if os.path.isdir(path) or item.endswith('.zip'):
                    backups.append((os.path.getmtime(path), path))
            
            backups.sort()
            
            for _, path in backups[:-max_backups]:
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                except Exception as e:
                    self.logger.warning(f"Failed to remove old backup {path}: {str(e)}")
                    
        except Exception as e:
            self.logger.warning(f"Error cleaning up old backups: {str(e)}")
    
    # Library Repair
    async def repair_library(self, library_path: str) -> Dict:
        """Repair common library issues."""
        results = {
            "success": True,
            "operations": [],
            "errors": [],
            "warnings": [],
            "fixed": 0
        }
        
        try:
            # Check and repair metadata.db
            try:
                result = await self._repair_metadata_db(library_path)
                results['operations'].append({"operation": "check_metadata_db", "result": result})
                
                if result.get('repaired', False):
                    results['fixed'] += 1
                
                if 'error' in result:
                    results['errors'].append(f"Metadata DB check failed: {result['error']}")
                    results['success'] = False
                
            except Exception as e:
                error_msg = f"Error checking metadata.db: {str(e)}"
                results['errors'].append(error_msg)
                results['operations'].append({"operation": "check_metadata_db", "error": error_msg})
                results['success'] = False
            
            # Check for orphaned files
            try:
                result = await self._find_orphaned_files(library_path)
                results['operations'].append({"operation": "check_orphaned_files", "result": result})
                
                if result.get('orphaned_files', []):
                    results['warnings'].append(f"Found {len(result['orphaned_files'])} orphaned files")
            except Exception as e:
                error_msg = f"Error checking for orphaned files: {str(e)}"
                results['errors'].append(error_msg)
                results['operations'].append({"operation": "check_orphaned_files", "error": error_msg})
                results['success'] = False
            
            return results
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Library repair failed: {str(e)}",
                "operations": results.get('operations', [])
            }
    
    async def _repair_metadata_db(self, library_path: str) -> Dict:
        """Check and repair the metadata database."""
        import sqlite3
        
        metadata_db = os.path.join(library_path, 'metadata.db')
        if not os.path.exists(metadata_db):
            return {"error": "metadata.db not found", "repaired": False}
        
        backup_db = f"{metadata_db}.backup"
        
        try:
            # Create a backup of the database
            shutil.copy2(metadata_db, backup_db)
            
            # Connect to the database and run integrity check
            conn = sqlite3.connect(metadata_db)
            cursor = conn.cursor()
            
            # Check integrity
            cursor.execute("PRAGMA integrity_check")
            integrity_result = cursor.fetchone()[0]
            
            if integrity_result != "ok":
                cursor.execute("PRAGMA quick_check")
                quick_check = cursor.fetchone()[0]
                
                if quick_check != "ok":
                    cursor.close()
                    conn.close()
                    
                    # Try to recover using backup
                    self.logger.warning("Database integrity check failed, attempting recovery...")
                    
                    try:
                        # Close any open connections
                        try:
                            cursor.close()
                            conn.close()
                        except:
                            pass
                        
                        # Remove the corrupted database
                        os.remove(metadata_db)
                        
                        # Restore from backup
                        shutil.copy2(backup_db, metadata_db)
                        
                        # Reconnect to the restored database
                        conn = sqlite3.connect(metadata_db)
                        cursor = conn.cursor()
                        
                        # Run VACUUM to rebuild the database file
                        cursor.execute("VACUUM")
                        conn.commit()
                        
                        return {
                            "repaired": True,
                            "message": "Database recovered from backup",
                            "integrity_check": integrity_result,
                            "quick_check": quick_check
                        }
                        
                    except Exception as e:
                        return {
                            "error": f"Database recovery failed: {str(e)}",
                            "repaired": False,
                            "integrity_check": integrity_result,
                            "quick_check": quick_check
                        }
            
            # If we get here, the database is either OK or we've recovered it
            cursor.close()
            conn.close()
            
            # Remove the backup if everything is OK
            try:
                os.remove(backup_db)
            except:
                pass
            
            return {
                "repaired": integrity_result != "ok",
                "integrity_check": integrity_result,
                "message": "Database integrity verified" if integrity_result == "ok" else "Database may have issues"
            }
            
        except Exception as e:
            # Restore from backup if possible
            if os.path.exists(backup_db):
                try:
                    shutil.copy2(backup_db, metadata_db)
                except:
                    pass
            
            return {
                "error": f"Error checking database: {str(e)}",
                "repaired": False
            }
    
    async def _find_orphaned_files(self, library_path: str) -> Dict:
        """Find files in the library that are not referenced in the database."""
        from calibre_plugins.calibremcp.storage.local import LocalStorage
        
        storage = LocalStorage(library_path)
        books = await storage.get_all_books()
        
        # Get all referenced files from the database
        referenced_files = set()
        
        for book in books:
            if 'files' in book:
                for file_info in book['files'].values():
                    if 'path' in file_info:
                        referenced_files.add(os.path.normpath(file_info['path']))
        
        # Scan the library directory for files
        orphaned = []
        
        books_dir = os.path.join(library_path, 'books')
        if os.path.isdir(books_dir):
            for root, _, files in os.walk(books_dir):
                for file in files:
                    file_path = os.path.normpath(os.path.join(root, file))
                    rel_path = os.path.relpath(file_path, library_path)
                    
                    if file_path not in referenced_files and not file.startswith('.'):
                        orphaned.append({
                            "path": file_path,
                            "relative_path": rel_path,
                            "size": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                            "modified": os.path.getmtime(file_path) if os.path.exists(file_path) else 0
                        })
        
        return {
            "orphaned_files": orphaned,
            "total_orphaned": len(orphaned),
            "total_referenced": len(referenced_files)
        }
