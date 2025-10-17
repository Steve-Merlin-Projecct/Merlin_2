#!/usr/bin/env python3
"""
Metrics Collection Script

Purpose: Gather quantitative metrics about documentation and codebase
Usage: python tools/collect_metrics.py [--json] [--report]
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

try:
    import click
    HAS_CLICK = True
except ImportError:
    import argparse
    HAS_CLICK = False


@dataclass
class DocumentationMetrics:
    """Aggregated documentation metrics"""
    total_docs: int
    total_code_files: int
    docs_with_metadata: int
    metadata_coverage_pct: float
    broken_links_count: int
    stale_docs_count: int  # >90 days
    archive_candidates: int  # >180 days
    root_violations: int
    avg_doc_age_days: float
    docs_by_component: Dict[str, int]
    docs_by_type: Dict[str, int]
    docs_by_status: Dict[str, int]
    undocumented_modules: List[str]
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class MetricsCollector:
    """Collects documentation and codebase metrics"""

    def __init__(self, project_root: Path = None):
        """
        Initialize metrics collector

        Args:
            project_root: Project root directory (default: auto-detect)
        """
        if project_root is None:
            self.project_root = self._find_project_root()
        else:
            self.project_root = Path(project_root).resolve()

        self.skip_dirs = ['node_modules', '.git', 'venv', 'project_venv', '__pycache__', 'archived_files']

    def _find_project_root(self) -> Path:
        """Find project root by looking for .git or CLAUDE.md"""
        current = Path.cwd()

        while current != current.parent:
            if (current / '.git').exists() or (current / 'CLAUDE.md').exists():
                return current
            current = current.parent

        return Path.cwd()

    def collect(self) -> DocumentationMetrics:
        """
        Collect all metrics

        Returns:
            DocumentationMetrics object
        """
        # Find all markdown and Python files
        md_files = self._find_files('*.md')
        py_files = self._find_files('*.py')

        # Count metrics
        total_docs = len(md_files)
        total_code_files = len(py_files)

        # Metadata analysis
        docs_with_metadata = self._count_docs_with_metadata(md_files)
        metadata_coverage_pct = (docs_with_metadata / total_docs * 100) if total_docs > 0 else 0.0

        # Link analysis (simplified - would use validate_links.py for full analysis)
        broken_links_count = 0  # Placeholder

        # Age analysis
        stale_docs = self._find_stale_docs(md_files, days=90)
        archive_candidates = self._find_stale_docs(md_files, days=180)
        avg_age = self._calculate_avg_age(md_files)

        # Root violations
        root_violations = self._count_root_violations()

        # Group by component, type, status
        docs_by_component = self._group_by_component(md_files)
        docs_by_type = self._group_by_type(md_files)
        docs_by_status = self._group_by_status(md_files)

        # Find undocumented modules
        undocumented = self._find_undocumented_modules(md_files)

        return DocumentationMetrics(
            total_docs=total_docs,
            total_code_files=total_code_files,
            docs_with_metadata=docs_with_metadata,
            metadata_coverage_pct=round(metadata_coverage_pct, 2),
            broken_links_count=broken_links_count,
            stale_docs_count=len(stale_docs),
            archive_candidates=len(archive_candidates),
            root_violations=root_violations,
            avg_doc_age_days=round(avg_age, 1),
            docs_by_component=docs_by_component,
            docs_by_type=docs_by_type,
            docs_by_status=docs_by_status,
            undocumented_modules=undocumented,
            timestamp=datetime.now().isoformat()
        )

    def _find_files(self, pattern: str) -> List[Path]:
        """Find all files matching pattern, excluding skip_dirs"""
        all_files = list(self.project_root.rglob(pattern))

        return [
            f for f in all_files
            if not any(skip_dir in f.parts for skip_dir in self.skip_dirs)
        ]

    def _count_docs_with_metadata(self, md_files: List[Path]) -> int:
        """Count markdown files with YAML frontmatter"""
        count = 0

        for md_file in md_files:
            try:
                content = md_file.read_text(encoding='utf-8')
                if content.startswith('---\n'):
                    count += 1
            except Exception:
                continue

        return count

    def _find_stale_docs(self, md_files: List[Path], days: int) -> List[Path]:
        """Find documents not modified in N days"""
        cutoff = datetime.now() - timedelta(days=days)
        cutoff_timestamp = cutoff.timestamp()

        stale = []

        for md_file in md_files:
            try:
                mtime = md_file.stat().st_mtime
                if mtime < cutoff_timestamp:
                    stale.append(md_file)
            except Exception:
                continue

        return stale

    def _calculate_avg_age(self, md_files: List[Path]) -> float:
        """Calculate average age of documents in days"""
        if not md_files:
            return 0.0

        total_age = 0.0
        count = 0
        now = datetime.now().timestamp()

        for md_file in md_files:
            try:
                mtime = md_file.stat().st_mtime
                age_seconds = now - mtime
                age_days = age_seconds / 86400  # Convert to days
                total_age += age_days
                count += 1
            except Exception:
                continue

        return total_age / count if count > 0 else 0.0

    def _count_root_violations(self) -> int:
        """Count files in root directory that shouldn't be there"""
        allowed_files = {
            'README.md', 'CLAUDE.md', 'CHANGELOG.md', 'app_modular.py',
            'main.py', 'requirements.txt', 'pyproject.toml', 'VERSION',
            'docker-compose.yml', '.env', '.env.example', '.gitignore',
            'Makefile', 'claude.md', 'PURPOSE.md'
        }

        violations = 0

        root_files = [f for f in self.project_root.iterdir() if f.is_file()]

        for file_path in root_files:
            # Skip hidden files
            if file_path.name.startswith('.'):
                continue

            if file_path.name not in allowed_files:
                violations += 1

        return violations

    def _group_by_component(self, md_files: List[Path]) -> Dict[str, int]:
        """Group documents by component (from metadata or path)"""
        components: Dict[str, int] = {}

        for md_file in md_files:
            component = self._extract_component(md_file)
            if component:
                components[component] = components.get(component, 0) + 1

        return dict(sorted(components.items()))

    def _group_by_type(self, md_files: List[Path]) -> Dict[str, int]:
        """Group documents by type (from metadata)"""
        types: Dict[str, int] = {}

        for md_file in md_files:
            doc_type = self._extract_metadata_field(md_file, 'type')
            if doc_type:
                types[doc_type] = types.get(doc_type, 0) + 1
            else:
                types['unknown'] = types.get('unknown', 0) + 1

        return dict(sorted(types.items()))

    def _group_by_status(self, md_files: List[Path]) -> Dict[str, int]:
        """Group documents by status (from metadata)"""
        statuses: Dict[str, int] = {}

        for md_file in md_files:
            status = self._extract_metadata_field(md_file, 'status')
            if status:
                statuses[status] = statuses.get(status, 0) + 1
            else:
                statuses['unknown'] = statuses.get('unknown', 0) + 1

        return dict(sorted(statuses.items()))

    def _extract_component(self, md_file: Path) -> str:
        """Extract component from metadata or infer from path"""
        # Try metadata first
        component = self._extract_metadata_field(md_file, 'component')
        if component:
            return component

        # Infer from path
        parts = md_file.parts

        # Check for modules directory
        if 'modules' in parts:
            idx = parts.index('modules')
            if len(parts) > idx + 1:
                return parts[idx + 1]

        # Check for component_docs
        if 'component_docs' in parts:
            idx = parts.index('component_docs')
            if len(parts) > idx + 1:
                return parts[idx + 1]

        # Check for common keywords
        path_str = str(md_file).lower()
        component_keywords = [
            'database', 'email', 'scraping', 'ai_analysis',
            'document_generation', 'storage', 'security',
            'integration', 'authentication', 'analytics'
        ]

        for keyword in component_keywords:
            if keyword in path_str:
                return keyword

        return 'general'

    def _extract_metadata_field(self, md_file: Path, field: str) -> str:
        """Extract a field from YAML frontmatter"""
        try:
            content = md_file.read_text(encoding='utf-8')

            # Check for frontmatter
            if not content.startswith('---\n'):
                return ''

            # Extract frontmatter
            parts = content.split('---\n', 2)
            if len(parts) < 3:
                return ''

            frontmatter = parts[1]

            # Simple field extraction (not full YAML parsing for performance)
            pattern = rf'^{field}:\s*(.+)$'
            import re
            match = re.search(pattern, frontmatter, re.MULTILINE)

            if match:
                value = match.group(1).strip()
                # Remove quotes if present
                value = value.strip('"\'')
                return value

        except Exception:
            pass

        return ''

    def _find_undocumented_modules(self, md_files: List[Path]) -> List[str]:
        """Find modules without documentation"""
        # Find all module directories
        modules_dir = self.project_root / 'modules'

        if not modules_dir.exists():
            return []

        module_dirs = [d for d in modules_dir.iterdir() if d.is_dir() and not d.name.startswith('_')]

        # Check which modules have documentation
        undocumented = []

        for module_dir in module_dirs:
            module_name = module_dir.name

            # Check if any doc references this module
            has_docs = any(
                module_name in str(md_file).lower()
                for md_file in md_files
            )

            if not has_docs:
                undocumented.append(module_name)

        return sorted(undocumented)


def format_human_readable(metrics: DocumentationMetrics) -> str:
    """Format metrics for human-readable output"""
    output = []

    output.append("=" * 60)
    output.append("DOCUMENTATION METRICS REPORT")
    output.append("=" * 60)
    output.append(f"Generated: {metrics.timestamp}")
    output.append("")

    output.append("OVERVIEW")
    output.append("-" * 60)
    output.append(f"Total Documentation Files:  {metrics.total_docs}")
    output.append(f"Total Code Files (Python):  {metrics.total_code_files}")
    output.append(f"Docs with Metadata:         {metrics.docs_with_metadata} ({metrics.metadata_coverage_pct}%)")
    output.append(f"Average Document Age:       {metrics.avg_doc_age_days} days")
    output.append("")

    output.append("HEALTH INDICATORS")
    output.append("-" * 60)
    output.append(f"Metadata Coverage:          {metrics.metadata_coverage_pct}%")
    output.append(f"Stale Docs (>90 days):      {metrics.stale_docs_count}")
    output.append(f"Archive Candidates (>180):  {metrics.archive_candidates}")
    output.append(f"Root Directory Violations:  {metrics.root_violations}")
    output.append(f"Broken Links:               {metrics.broken_links_count}")
    output.append("")

    if metrics.docs_by_component:
        output.append("DOCUMENTATION BY COMPONENT")
        output.append("-" * 60)
        for component, count in metrics.docs_by_component.items():
            output.append(f"  {component:30s} {count:3d} docs")
        output.append("")

    if metrics.docs_by_type:
        output.append("DOCUMENTATION BY TYPE")
        output.append("-" * 60)
        for doc_type, count in metrics.docs_by_type.items():
            output.append(f"  {doc_type:30s} {count:3d} docs")
        output.append("")

    if metrics.docs_by_status:
        output.append("DOCUMENTATION BY STATUS")
        output.append("-" * 60)
        for status, count in metrics.docs_by_status.items():
            output.append(f"  {status:30s} {count:3d} docs")
        output.append("")

    if metrics.undocumented_modules:
        output.append("UNDOCUMENTED MODULES")
        output.append("-" * 60)
        for module in metrics.undocumented_modules:
            output.append(f"  - modules/{module}")
        output.append("")

    output.append("=" * 60)

    return "\n".join(output)


# CLI Implementation
if HAS_CLICK:
    @click.command()
    @click.option('--json', 'json_output', is_flag=True, help='Output as JSON')
    @click.option('--report', is_flag=True, help='Generate full report (default is human-readable)')
    @click.option('--project-root', type=click.Path(exists=True), help='Project root directory')
    def main(json_output: bool, report: bool, project_root: Optional[str]):
        """Collect documentation and codebase metrics"""

        root = Path(project_root) if project_root else None

        collector = MetricsCollector(root)
        metrics = collector.collect()

        if json_output:
            print(json.dumps(metrics.to_dict(), indent=2))
        else:
            print(format_human_readable(metrics))

        sys.exit(0)

else:
    def main():
        parser = argparse.ArgumentParser(description='Collect documentation metrics')
        parser.add_argument('--json', action='store_true', help='Output as JSON')
        parser.add_argument('--report', action='store_true', help='Generate full report')
        parser.add_argument('--project-root', help='Project root directory')

        args = parser.parse_args()

        root = Path(args.project_root) if args.project_root else None

        collector = MetricsCollector(root)
        metrics = collector.collect()

        if args.json:
            print(json.dumps(metrics.to_dict(), indent=2))
        else:
            print(format_human_readable(metrics))

        sys.exit(0)


if __name__ == '__main__':
    main()
