#!/usr/bin/env python3
"""
Document Catalog Query Tool

Purpose: Search document catalog with filters
Usage: python tools/query_catalog.py --keywords "database" --component email
"""

import sys
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple

try:
    import click
    HAS_CLICK = True
except ImportError:
    import argparse
    HAS_CLICK = False


class CatalogQuery:
    """Query interface for document catalog"""

    def __init__(self, db_path: Path = None, project_root: Path = None):
        """
        Initialize catalog query

        Args:
            db_path: Path to SQLite database
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

    def _find_project_root(self) -> Path:
        """Find project root"""
        current = Path.cwd()

        while current != current.parent:
            if (current / '.git').exists() or (current / 'CLAUDE.md').exists():
                return current
            current = current.parent

        return Path.cwd()

    def connect(self) -> None:
        """Connect to database"""
        if not self.db_path.exists():
            raise FileNotFoundError(
                f"Catalog database not found: {self.db_path}\n"
                f"Run 'python tools/build_index.py' to create it."
            )

        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row

    def close(self) -> None:
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def search(
        self,
        keywords: Optional[str] = None,
        component: Optional[str] = None,
        doc_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Search catalog with filters

        Args:
            keywords: Keywords to search in title and summary
            component: Filter by component
            doc_type: Filter by document type
            status: Filter by status
            limit: Maximum number of results

        Returns:
            List of matching documents
        """
        if not self.conn:
            raise RuntimeError("Not connected to database")

        # Build query
        query = "SELECT * FROM documents WHERE 1=1"
        params = []

        # Add filters
        if keywords:
            # Search in title and content_summary
            query += " AND (title LIKE ? OR content_summary LIKE ?)"
            pattern = f"%{keywords}%"
            params.extend([pattern, pattern])

        if component:
            query += " AND component = ?"
            params.append(component)

        if doc_type:
            query += " AND type = ?"
            params.append(doc_type)

        if status:
            query += " AND status = ?"
            params.append(status)

        # Order by last modified (most recent first)
        query += " ORDER BY last_modified DESC"

        # Add limit
        query += " LIMIT ?"
        params.append(limit)

        # Execute query
        cursor = self.conn.execute(query, params)
        rows = cursor.fetchall()

        # Convert to dictionaries
        results = []
        for row in rows:
            results.append(dict(row))

        return results

    def get_all_components(self) -> List[str]:
        """Get list of all components"""
        if not self.conn:
            raise RuntimeError("Not connected to database")

        cursor = self.conn.execute(
            "SELECT DISTINCT component FROM documents WHERE component IS NOT NULL ORDER BY component"
        )
        return [row[0] for row in cursor.fetchall()]

    def get_all_types(self) -> List[str]:
        """Get list of all document types"""
        if not self.conn:
            raise RuntimeError("Not connected to database")

        cursor = self.conn.execute(
            "SELECT DISTINCT type FROM documents WHERE type IS NOT NULL ORDER BY type"
        )
        return [row[0] for row in cursor.fetchall()]

    def get_all_statuses(self) -> List[str]:
        """Get list of all statuses"""
        if not self.conn:
            raise RuntimeError("Not connected to database")

        cursor = self.conn.execute(
            "SELECT DISTINCT status FROM documents WHERE status IS NOT NULL ORDER BY status"
        )
        return [row[0] for row in cursor.fetchall()]


def format_results(results: List[Dict], show_summary: bool = True) -> str:
    """Format search results for display"""
    if not results:
        return "No documents found matching criteria."

    output = []
    output.append(f"Found {len(results)} documents:\n")

    for i, doc in enumerate(results, 1):
        output.append(f"{i}. {doc['file_path']}")

        metadata_parts = []
        if doc.get('type'):
            metadata_parts.append(f"Type: {doc['type']}")
        if doc.get('component'):
            metadata_parts.append(f"Component: {doc['component']}")
        if doc.get('status'):
            metadata_parts.append(f"Status: {doc['status']}")

        if metadata_parts:
            output.append(f"   {' | '.join(metadata_parts)}")

        if show_summary and doc.get('content_summary'):
            summary = doc['content_summary']
            if len(summary) > 150:
                summary = summary[:150] + '...'
            output.append(f"   Summary: {summary}")

        output.append("")  # Blank line

    return "\n".join(output)


# CLI Implementation
if HAS_CLICK:
    @click.command()
    @click.option('--keywords', '-k', help='Keywords to search')
    @click.option('--component', '-c', help='Filter by component')
    @click.option('--type', '-t', 'doc_type', help='Filter by document type')
    @click.option('--status', '-s', help='Filter by status')
    @click.option('--limit', '-l', default=10, type=int, help='Maximum results (default: 10)')
    @click.option('--json', 'json_output', is_flag=True, help='Output as JSON')
    @click.option('--no-summary', is_flag=True, help='Hide content summaries')
    @click.option('--list-components', is_flag=True, help='List all components')
    @click.option('--list-types', is_flag=True, help='List all types')
    @click.option('--list-statuses', is_flag=True, help='List all statuses')
    @click.option('--db-path', type=click.Path(), help='Database file path')
    @click.option('--project-root', type=click.Path(exists=True), help='Project root directory')
    def main(
        keywords: Optional[str],
        component: Optional[str],
        doc_type: Optional[str],
        status: Optional[str],
        limit: int,
        json_output: bool,
        no_summary: bool,
        list_components: bool,
        list_types: bool,
        list_statuses: bool,
        db_path: Optional[str],
        project_root: Optional[str]
    ):
        """Query document catalog"""

        root = Path(project_root) if project_root else None
        db = Path(db_path) if db_path else None

        query = CatalogQuery(db, root)

        try:
            query.connect()

            # Handle list operations
            if list_components:
                components = query.get_all_components()
                print("Available components:")
                for comp in components:
                    print(f"  - {comp}")
                sys.exit(0)

            if list_types:
                types = query.get_all_types()
                print("Available document types:")
                for t in types:
                    print(f"  - {t}")
                sys.exit(0)

            if list_statuses:
                statuses = query.get_all_statuses()
                print("Available statuses:")
                for s in statuses:
                    print(f"  - {s}")
                sys.exit(0)

            # Perform search
            results = query.search(
                keywords=keywords,
                component=component,
                doc_type=doc_type,
                status=status,
                limit=limit
            )

            if json_output:
                print(json.dumps(results, indent=2))
            else:
                print(format_results(results, show_summary=not no_summary))

        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

        finally:
            query.close()

        sys.exit(0)

else:
    def main():
        parser = argparse.ArgumentParser(description='Query document catalog')
        parser.add_argument('--keywords', '-k', help='Keywords to search')
        parser.add_argument('--component', '-c', help='Filter by component')
        parser.add_argument('--type', '-t', dest='doc_type', help='Filter by type')
        parser.add_argument('--status', '-s', help='Filter by status')
        parser.add_argument('--limit', '-l', type=int, default=10, help='Maximum results')
        parser.add_argument('--json', action='store_true', help='Output as JSON')
        parser.add_argument('--no-summary', action='store_true', help='Hide summaries')
        parser.add_argument('--list-components', action='store_true', help='List all components')
        parser.add_argument('--list-types', action='store_true', help='List all types')
        parser.add_argument('--list-statuses', action='store_true', help='List all statuses')
        parser.add_argument('--db-path', help='Database file path')
        parser.add_argument('--project-root', help='Project root directory')

        args = parser.parse_args()

        root = Path(args.project_root) if args.project_root else None
        db = Path(args.db_path) if args.db_path else None

        query = CatalogQuery(db, root)

        try:
            query.connect()

            if args.list_components:
                components = query.get_all_components()
                print("Available components:")
                for comp in components:
                    print(f"  - {comp}")
                sys.exit(0)

            if args.list_types:
                types = query.get_all_types()
                print("Available document types:")
                for t in types:
                    print(f"  - {t}")
                sys.exit(0)

            if args.list_statuses:
                statuses = query.get_all_statuses()
                print("Available statuses:")
                for s in statuses:
                    print(f"  - {s}")
                sys.exit(0)

            results = query.search(
                keywords=args.keywords,
                component=args.component,
                doc_type=args.doc_type,
                status=args.status,
                limit=args.limit
            )

            if args.json:
                print(json.dumps(results, indent=2))
            else:
                print(format_results(results, show_summary=not args.no_summary))

        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

        finally:
            query.close()

        sys.exit(0)


if __name__ == '__main__':
    main()
