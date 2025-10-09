#!/usr/bin/env python3
"""
Librarian Index Generator: Create searchable documentation index

Generates JSON and HTML indexes of all documentation with metadata-driven
navigation, search, and filtering capabilities.

Author: Claude Sonnet 4.5
Created: 2025-10-09
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))

from librarian_common import (
    extract_frontmatter,
    find_markdown_files,
    extract_markdown_links,
    logger
)


def generate_index(root_dir='.'):
    """Generate complete documentation index."""

    files = find_markdown_files(root_dir)

    index = {
        'generated': datetime.now().isoformat(),
        'version': '1.0.0',
        'total_files': len(files),
        'statistics': {
            'by_type': defaultdict(int),
            'by_status': defaultdict(int),
            'with_metadata': 0,
            'without_metadata': 0
        },
        'categories': defaultdict(list),
        'tags': defaultdict(list),
        'files': []
    }

    # Process each file
    for file_path in files:
        metadata = extract_frontmatter(file_path)

        file_info = {
            'path': file_path,
            'metadata': metadata if metadata else {},
            'has_metadata': metadata is not None
        }

        if metadata:
            index['statistics']['with_metadata'] += 1

            # Count by type
            if 'type' in metadata:
                index['statistics']['by_type'][metadata['type']] += 1
                index['categories'][metadata['type']].append(file_path)

            # Count by status
            if 'status' in metadata:
                index['statistics']['by_status'][metadata['status']] += 1

            # Index by tags
            if 'tags' in metadata and isinstance(metadata['tags'], list):
                for tag in metadata['tags']:
                    index['tags'][tag].append(file_path)

            # Add references
            links = extract_markdown_links(file_path)
            file_info['references'] = [url for _, url in links if not url.startswith('http')]
        else:
            index['statistics']['without_metadata'] += 1

        index['files'].append(file_info)

    # Convert defaultdicts to regular dicts
    index['categories'] = dict(index['categories'])
    index['tags'] = dict(index['tags'])
    index['statistics']['by_type'] = dict(index['statistics']['by_type'])
    index['statistics']['by_status'] = dict(index['statistics']['by_status'])

    return index


def save_json_index(index, output_path):
    """Save index as JSON."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(index, f, indent=2)

    logger.info(f"JSON index saved to {output_path}")


def generate_html_index(index, output_path):
    """Generate HTML documentation map."""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Documentation Index</title>
    <style>
        body {{ font-family: system-ui, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
        .stat-card {{ background: #f8f9fa; padding: 15px; border-radius: 6px; border-left: 4px solid #007bff; }}
        .stat-card h3 {{ margin: 0 0 10px 0; font-size: 14px; color: #666; }}
        .stat-card .value {{ font-size: 32px; font-weight: bold; color: #007bff; }}
        .search {{ margin: 20px 0; }}
        .search input {{ width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 6px; font-size: 16px; }}
        .filters {{ margin: 20px 0; display: flex; gap: 10px; flex-wrap: wrap; }}
        .filter-btn {{ padding: 8px 16px; border: 2px solid #ddd; background: white; border-radius: 6px; cursor: pointer; }}
        .filter-btn.active {{ background: #007bff; color: white; border-color: #007bff; }}
        .file-list {{ margin: 20px 0; }}
        .file-item {{ padding: 15px; margin: 10px 0; background: #f8f9fa; border-radius: 6px; border-left: 4px solid #28a745; }}
        .file-item.hidden {{ display: none; }}
        .file-path {{ font-weight: bold; color: #333; margin-bottom: 8px; }}
        .file-meta {{ font-size: 14px; color: #666; }}
        .file-meta span {{ margin-right: 15px; padding: 4px 8px; background: white; border-radius: 4px; }}
        .tag {{ display: inline-block; padding: 4px 8px; margin: 2px; background: #e7f3ff; color: #007bff; border-radius: 4px; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 Documentation Index</h1>

        <div class="stats">
            <div class="stat-card">
                <h3>Total Files</h3>
                <div class="value">{index['total_files']}</div>
            </div>
            <div class="stat-card">
                <h3>With Metadata</h3>
                <div class="value">{index['statistics']['with_metadata']}</div>
            </div>
            <div class="stat-card">
                <h3>Coverage</h3>
                <div class="value">{int(index['statistics']['with_metadata']/index['total_files']*100)}%</div>
            </div>
            <div class="stat-card">
                <h3>Generated</h3>
                <div class="value" style="font-size: 16px;">{datetime.fromisoformat(index['generated']).strftime('%Y-%m-%d')}</div>
            </div>
        </div>

        <div class="search">
            <input type="text" id="searchInput" placeholder="Search documentation..." onkeyup="searchFiles()">
        </div>

        <div class="filters">
            <button class="filter-btn active" onclick="filterType('all')">All</button>
"""

    # Add type filters
    for doc_type in sorted(index['statistics']['by_type'].keys()):
        count = index['statistics']['by_type'][doc_type]
        html += f'            <button class="filter-btn" onclick="filterType(\'{doc_type}\')">{doc_type.title()} ({count})</button>\n'

    html += """        </div>

        <div class="file-list" id="fileList">
"""

    # Add file entries
    for file_info in sorted(index['files'], key=lambda x: x.get('metadata', {}).get('title', x['path'])):
        metadata = file_info.get('metadata', {})
        path = file_info['path']

        title = metadata.get('title', Path(path).stem.replace('-', ' ').title())
        doc_type = metadata.get('type', 'unknown')
        status = metadata.get('status', 'unknown')
        tags = metadata.get('tags', [])

        html += f"""            <div class="file-item" data-type="{doc_type}" data-status="{status}">
                <div class="file-path">{title}</div>
                <div class="file-meta">
                    <span>📄 {doc_type}</span>
                    <span>🔖 {status}</span>
"""

        if tags:
            html += '                    <span>'
            for tag in tags[:5]:  # Show first 5 tags
                html += f'<span class="tag">{tag}</span>'
            html += '</span>\n'

        html += f"""                    <span>📁 {path}</span>
                </div>
            </div>
"""

    html += """        </div>
    </div>

    <script>
        let currentFilter = 'all';

        function searchFiles() {
            const input = document.getElementById('searchInput');
            const filter = input.value.toLowerCase();
            const items = document.querySelectorAll('.file-item');

            items.forEach(item => {
                const text = item.textContent.toLowerCase();
                const matchesSearch = text.includes(filter);
                const matchesFilter = currentFilter === 'all' || item.dataset.type === currentFilter;

                item.style.display = (matchesSearch && matchesFilter) ? 'block' : 'none';
            });
        }

        function filterType(type) {
            currentFilter = type;

            // Update button states
            document.querySelectorAll('.filter-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');

            searchFiles();
        }
    </script>
</body>
</html>
"""

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        f.write(html)

    logger.info(f"HTML index saved to {output_path}")


def main():
    print("Generating documentation index...")

    # Generate index
    index = generate_index('.')

    # Save JSON
    json_path = 'docs/indexes/documentation-index.json'
    save_json_index(index, json_path)

    # Generate HTML
    html_path = 'docs/indexes/documentation-map.html'
    generate_html_index(index, html_path)

    print(f"\n✓ Index generation complete!")
    print(f"  - JSON: {json_path}")
    print(f"  - HTML: {html_path}")
    print(f"  - Total files: {index['total_files']}")
    print(f"  - With metadata: {index['statistics']['with_metadata']} ({int(index['statistics']['with_metadata']/index['total_files']*100)}%)")


if __name__ == '__main__':
    main()
