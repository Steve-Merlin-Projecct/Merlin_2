#!/usr/bin/env python3
"""
Document Catalog Builder

Purpose: Build searchable SQLite database of all documentation
Usage: python tools/build_index.py [--incremental] [--rebuild]
"""

import sys
import sqlite3
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import hashlib

try:
    import click
    HAS_CLICK = True
except ImportError:
    import argparse
    HAS_CLICK = False


class DocumentCatalog:
    """SQLite-based document catalog"""

    SCHEMA_VERSION = 1

    # SQL schema
    SCHEMA_SQL = """
    CREATE TABLE IF NOT EXISTS documents (
        id TEXT PRIMARY KEY,
        file_path TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        type TEXT,
        component TEXT,
        status TEXT,
        tags TEXT,  -- JSON array as string
        content_summary TEXT,
        word_count INTEGER,
        last_modified INTEGER,  -- Unix timestamp
        created INTEGER,  -- Unix timestamp
        file_hash TEXT,  -- MD5 hash for change detection
        indexed_at INTEGER  -- Unix timestamp
    );

    CREATE INDEX IF NOT EXISTS idx_component ON documents(component);
    CREATE INDEX IF NOT EXISTS idx_type ON documents(type);
    CREATE INDEX IF NOT EXISTS idx_status ON documents(status);
    CREATE INDEX IF NOT EXISTS idx_file_path ON documents(file_path);

    CREATE TABLE IF NOT EXISTS metadata (
        key TEXT PRIMARY KEY,
        value TEXT
    );
    """

    def __init__(self, db_path: Path = None, project_root: Path = None):
        """
        Initialize document catalog

        Args:
            db_path: Path to SQLite database (default: tools/librarian_catalog.db)
            project_root: Project root directory
        """
        if project_root is None:
            self.project_root = self._find_project_root()
        else:
            self.project_root = Path(project_root).resolve()

        if db_path is None:
            self.db_path = self.project_root / 'tools' / 'librarian_catalog.db'
        else:
            self.db_path = Path(db_path)

        self.conn: Optional[sqlite3.Connection] = None
        self.skip_dirs = ['node_modules', '.git', 'venv', 'project_venv', '__pycache__', 'archived_files']

    def _find_project_root(self) -> Path:
        """Find project root by looking for .git or CLAUDE.md"""
        current = Path.cwd()

        while current != current.parent:
            if (current / '.git').exists() or (current / 'CLAUDE.md').exists():
                return current
            current = current.parent

        return Path.cwd()

    def connect(self) -> None:
        """Connect to database and initialize schema"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def close(self) -> None:
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def _init_schema(self) -> None:
        """Initialize database schema"""
        if not self.conn:
            raise RuntimeError("Not connected to database")

        self.conn.executescript(self.SCHEMA_SQL)

        # Store schema version
        self.conn.execute(
            "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
            ('schema_version', str(self.SCHEMA_VERSION))
        )
        self.conn.commit()

    def rebuild(self) -> Tuple[int, int]:
        """
        Rebuild entire catalog from scratch

        Returns:
            Tuple of (indexed_count, error_count)
        """
        print("Rebuilding catalog from scratch...")

        # Clear existing data
        if self.conn:
            self.conn.execute("DELETE FROM documents")
            self.conn.commit()

        # Find all markdown files
        md_files = self._find_markdown_files()

        print(f"Found {len(md_files)} markdown files to index")

        indexed_count = 0
        error_count = 0

        for md_file in md_files:
            try:
                self._index_document(md_file)
                indexed_count += 1

                if indexed_count % 50 == 0:
                    print(f"  Indexed {indexed_count} documents...")

            except Exception as e:
                error_count += 1
                print(f"  Error indexing {md_file}: {e}")

        self.conn.commit()

        print(f"\nCompleted: {indexed_count} indexed, {error_count} errors")

        return indexed_count, error_count

    def incremental_update(self) -> Tuple[int, int, int]:
        """
        Update only changed/new files

        Returns:
            Tuple of (new_count, updated_count, error_count)
        """
        print("Performing incremental update...")

        md_files = self._find_markdown_files()

        new_count = 0
        updated_count = 0
        error_count = 0

        for md_file in md_files:
            try:
                if self._needs_reindex(md_file):
                    was_new = self._is_new_document(md_file)
                    self._index_document(md_file)

                    if was_new:
                        new_count += 1
                    else:
                        updated_count += 1

                    if (new_count + updated_count) % 50 == 0:
                        print(f"  Processed {new_count + updated_count} documents...")

            except Exception as e:
                error_count += 1
                print(f"  Error indexing {md_file}: {e}")

        self.conn.commit()

        print(f"\nCompleted: {new_count} new, {updated_count} updated, {error_count} errors")

        return new_count, updated_count, error_count

    def _find_markdown_files(self) -> List[Path]:
        """Find all markdown files in project"""
        md_files = list(self.project_root.rglob('*.md'))

        # Filter out skip directories
        return [
            f for f in md_files
            if not any(skip_dir in f.parts for skip_dir in self.skip_dirs)
        ]

    def _needs_reindex(self, file_path: Path) -> bool:
        """Check if file needs to be reindexed"""
        rel_path = str(file_path.relative_to(self.project_root))

        # Check if file exists in catalog
        cursor = self.conn.execute(
            "SELECT file_hash, last_modified FROM documents WHERE file_path = ?",
            (rel_path,)
        )
        row = cursor.fetchone()

        if not row:
            return True  # New file

        # Check if file has changed
        current_hash = self._compute_file_hash(file_path)
        current_mtime = int(file_path.stat().st_mtime)

        return current_hash != row['file_hash'] or current_mtime != row['last_modified']

    def _is_new_document(self, file_path: Path) -> bool:
        """Check if document is new (not in catalog)"""
        rel_path = str(file_path.relative_to(self.project_root))

        cursor = self.conn.execute(
            "SELECT 1 FROM documents WHERE file_path = ? LIMIT 1",
            (rel_path,)
        )
        return cursor.fetchone() is None

    def _index_document(self, file_path: Path) -> None:
        """Index a single document"""
        rel_path = str(file_path.relative_to(self.project_root))

        # Read file content
        content = file_path.read_text(encoding='utf-8')

        # Extract metadata
        metadata = self._extract_metadata(content)

        # Generate summary
        summary = self._generate_summary(content)

        # Count words
        word_count = self._count_words(content)

        # Get file stats
        stat = file_path.stat()
        last_modified = int(stat.st_mtime)

        # Compute file hash
        file_hash = self._compute_file_hash(file_path)

        # Generate document ID (hash of file path)
        doc_id = hashlib.md5(rel_path.encode()).hexdigest()

        # Insert or replace document
        self.conn.execute(
            """
            INSERT OR REPLACE INTO documents (
                id, file_path, title, type, component, status, tags,
                content_summary, word_count, last_modified, created,
                file_hash, indexed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                doc_id,
                rel_path,
                metadata.get('title', file_path.stem),
                metadata.get('type'),
                metadata.get('component'),
                metadata.get('status'),
                str(metadata.get('tags', [])),  # Store as string
                summary,
                word_count,
                last_modified,
                metadata.get('created'),
                file_hash,
                int(datetime.now().timestamp())
            )
        )

    def _extract_metadata(self, content: str) -> Dict[str, str]:
        """Extract YAML frontmatter metadata"""
        metadata = {}

        # Check for frontmatter
        if not content.startswith('---\n'):
            return metadata

        # Extract frontmatter
        parts = content.split('---\n', 2)
        if len(parts) < 3:
            return metadata

        frontmatter = parts[1]

        # Simple field extraction (faster than full YAML parsing)
        patterns = {
            'title': r'^title:\s*["\']?(.+?)["\']?\s*$',
            'type': r'^type:\s*(\S+)',
            'component': r'^component:\s*(\S+)',
            'status': r'^status:\s*(\S+)',
            'created': r'^created:\s*(.+?)\s*$',
            'updated': r'^updated:\s*(.+?)\s*$',
        }

        for field, pattern in patterns.items():
            match = re.search(pattern, frontmatter, re.MULTILINE)
            if match:
                value = match.group(1).strip().strip('"\'')
                metadata[field] = value

        # Extract tags (list)
        tags_match = re.search(r'^tags:\s*\[(.*?)\]', frontmatter, re.MULTILINE)
        if tags_match:
            tags_str = tags_match.group(1)
            tags = [t.strip().strip('"\'') for t in tags_str.split(',')]
            metadata['tags'] = [t for t in tags if t]

        return metadata

    def _generate_summary(self, content: str) -> str:
        """Generate summary from first paragraph"""
        # Remove frontmatter
        if content.startswith('---\n'):
            parts = content.split('---\n', 2)
            if len(parts) >= 3:
                content = parts[2]

        # Remove markdown formatting
        content = re.sub(r'#+\s+', '', content)  # Remove headers
        content = re.sub(r'\*\*(.+?)\*\*', r'\1', content)  # Remove bold
        content = re.sub(r'\*(.+?)\*', r'\1', content)  # Remove italic
        content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)  # Remove links
        content = re.sub(r'`([^`]+)`', r'\1', content)  # Remove inline code

        # Get first paragraph
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

        if not paragraphs:
            return ''

        first_para = paragraphs[0]

        # Limit length
        max_length = 200
        if len(first_para) > max_length:
            first_para = first_para[:max_length].rsplit(' ', 1)[0] + '...'

        return first_para

    def _count_words(self, content: str) -> int:
        """Count words in content (excluding code blocks)"""
        # Remove code blocks
        content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)

        # Remove frontmatter
        if content.startswith('---\n'):
            parts = content.split('---\n', 2)
            if len(parts) >= 3:
                content = parts[2]

        # Count words
        words = re.findall(r'\b\w+\b', content)
        return len(words)

    def _compute_file_hash(self, file_path: Path) -> str:
        """Compute MD5 hash of file content"""
        content = file_path.read_bytes()
        return hashlib.md5(content).hexdigest()

    def get_stats(self) -> Dict[str, int]:
        """Get catalog statistics"""
        if not self.conn:
            raise RuntimeError("Not connected to database")

        stats = {}

        cursor = self.conn.execute("SELECT COUNT(*) as count FROM documents")
        stats['total_documents'] = cursor.fetchone()['count']

        cursor = self.conn.execute("SELECT COUNT(DISTINCT component) as count FROM documents WHERE component IS NOT NULL")
        stats['unique_components'] = cursor.fetchone()['count']

        cursor = self.conn.execute("SELECT COUNT(DISTINCT type) as count FROM documents WHERE type IS NOT NULL")
        stats['unique_types'] = cursor.fetchone()['count']

        return stats


# CLI Implementation
if HAS_CLICK:
    @click.command()
    @click.option('--incremental', is_flag=True, help='Update only changed files (default)')
    @click.option('--rebuild', is_flag=True, help='Rebuild entire catalog from scratch')
    @click.option('--db-path', type=click.Path(), help='Database file path')
    @click.option('--project-root', type=click.Path(exists=True), help='Project root directory')
    def main(incremental: bool, rebuild: bool, db_path: Optional[str], project_root: Optional[str]):
        """Build searchable catalog of documentation"""

        root = Path(project_root) if project_root else None
        db = Path(db_path) if db_path else None

        catalog = DocumentCatalog(db, root)

        try:
            catalog.connect()

            if rebuild:
                indexed, errors = catalog.rebuild()
            else:
                new, updated, errors = catalog.incremental_update()

            # Print stats
            stats = catalog.get_stats()
            print("\nCatalog Statistics:")
            print(f"  Total documents: {stats['total_documents']}")
            print(f"  Unique components: {stats['unique_components']}")
            print(f"  Unique types: {stats['unique_types']}")
            print(f"\nDatabase: {catalog.db_path}")

        finally:
            catalog.close()

        sys.exit(0 if errors == 0 else 1)

else:
    def main():
        parser = argparse.ArgumentParser(description='Build document catalog')
        parser.add_argument('--incremental', action='store_true', help='Incremental update')
        parser.add_argument('--rebuild', action='store_true', help='Rebuild from scratch')
        parser.add_argument('--db-path', help='Database file path')
        parser.add_argument('--project-root', help='Project root directory')

        args = parser.parse_args()

        root = Path(args.project_root) if args.project_root else None
        db = Path(args.db_path) if args.db_path else None

        catalog = DocumentCatalog(db, root)

        try:
            catalog.connect()

            if args.rebuild:
                indexed, errors = catalog.rebuild()
            else:
                new, updated, errors = catalog.incremental_update()

            stats = catalog.get_stats()
            print("\nCatalog Statistics:")
            print(f"  Total documents: {stats['total_documents']}")
            print(f"  Unique components: {stats['unique_components']}")
            print(f"  Unique types: {stats['unique_types']}")
            print(f"\nDatabase: {catalog.db_path}")

        finally:
            catalog.close()

        sys.exit(0)


if __name__ == '__main__':
    main()
