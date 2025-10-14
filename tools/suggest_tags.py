#!/usr/bin/env python3
"""
Tag Suggestion Script

Purpose: Extract keywords from content for auto-tagging
Usage: python tools/suggest_tags.py <file_path> [--yaml]
"""

import sys
import re
from pathlib import Path
from typing import List, Dict, Set
from collections import Counter
import math

try:
    import click
    HAS_CLICK = True
except ImportError:
    import argparse
    HAS_CLICK = False


class TagSuggester:
    """Suggests tags based on content analysis"""

    # Common stop words to exclude
    STOP_WORDS = {
        'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
        'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
        'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
        'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their',
        'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go',
        'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know',
        'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could',
        'them', 'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come',
        'its', 'over', 'think', 'also', 'back', 'after', 'use', 'two', 'how',
        'our', 'work', 'first', 'well', 'way', 'even', 'new', 'want', 'because',
        'any', 'these', 'give', 'day', 'most', 'us', 'is', 'was', 'are', 'been',
        'has', 'had', 'were', 'did', 'being', 'having', 'does', 'may', 'might',
        'must', 'should', 'could', 'would', 'shall', 'will', 'can'
    }

    # Technical keywords to boost
    TECH_KEYWORDS = {
        'api', 'database', 'authentication', 'authorization', 'security',
        'encryption', 'configuration', 'deployment', 'testing', 'documentation',
        'integration', 'migration', 'schema', 'workflow', 'architecture',
        'postgresql', 'python', 'flask', 'docker', 'github', 'git',
        'oauth', 'rest', 'endpoint', 'validation', 'error', 'logging'
    }

    def __init__(self, file_path: Path):
        """
        Initialize tag suggester

        Args:
            file_path: Path to markdown file
        """
        self.file_path = Path(file_path)

    def suggest(self, num_tags: int = 7, min_score: float = 1.0) -> List[str]:
        """
        Suggest tags for the document

        Args:
            num_tags: Maximum number of tags to suggest
            min_score: Minimum relevance score (0-10)

        Returns:
            List of suggested tags
        """
        # Read content
        try:
            content = self.file_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            return []

        # Remove frontmatter
        content = self._remove_frontmatter(content)

        # Remove code blocks (they can skew results)
        content = self._remove_code_blocks(content)

        # Extract words
        words = self._extract_words(content)

        # Calculate TF-IDF-like scores
        scores = self._calculate_scores(words)

        # Filter and sort
        candidates = [
            (word, score) for word, score in scores.items()
            if score >= min_score
        ]
        candidates.sort(key=lambda x: x[1], reverse=True)

        # Return top N
        return [word for word, score in candidates[:num_tags]]

    def _remove_frontmatter(self, content: str) -> str:
        """Remove YAML frontmatter"""
        if content.startswith('---\n'):
            parts = content.split('---\n', 2)
            if len(parts) >= 3:
                return parts[2]
        return content

    def _remove_code_blocks(self, content: str) -> str:
        """Remove code blocks"""
        # Remove fenced code blocks
        content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)

        # Remove inline code
        content = re.sub(r'`[^`]+`', '', content)

        return content

    def _extract_words(self, content: str) -> List[str]:
        """Extract words from content"""
        # Convert to lowercase
        content = content.lower()

        # Extract words (alphanumeric + underscores/hyphens)
        words = re.findall(r'\b[a-z0-9_-]+\b', content)

        # Filter out stop words and very short words
        words = [
            w for w in words
            if len(w) >= 3 and w not in self.STOP_WORDS
        ]

        return words

    def _calculate_scores(self, words: List[str]) -> Dict[str, float]:
        """Calculate relevance scores for words"""
        # Count word frequencies
        word_counts = Counter(words)

        # Calculate term frequency scores
        total_words = len(words)
        tf_scores = {}

        for word, count in word_counts.items():
            # Term frequency
            tf = count / total_words

            # Boost technical keywords
            boost = 2.0 if word in self.TECH_KEYWORDS else 1.0

            # Favor compound words (with underscores or hyphens)
            if '_' in word or '-' in word:
                boost *= 1.5

            # Penalize very common words
            if count > total_words * 0.1:  # Appears in >10% of text
                boost *= 0.5

            # Calculate score (scaled to 0-10)
            score = (tf * 100 * boost)
            tf_scores[word] = score

        return tf_scores


# CLI Implementation
if HAS_CLICK:
    @click.command()
    @click.argument('file_path', type=click.Path(exists=True))
    @click.option('--num-tags', '-n', default=7, type=int, help='Number of tags to suggest (default: 7)')
    @click.option('--min-score', '-m', default=1.0, type=float, help='Minimum relevance score (default: 1.0)')
    @click.option('--yaml', 'yaml_output', is_flag=True, help='Output as YAML array')
    def main(file_path: str, num_tags: int, min_score: float, yaml_output: bool):
        """Suggest tags for a markdown document"""

        suggester = TagSuggester(Path(file_path))
        tags = suggester.suggest(num_tags=num_tags, min_score=min_score)

        if not tags:
            print("No tags suggested (file may be empty or contain only common words)")
            sys.exit(1)

        if yaml_output:
            # Format as YAML array
            tags_str = ', '.join(f'"{tag}"' for tag in tags)
            print(f"tags: [{tags_str}]")
        else:
            print(f"Suggested tags for {file_path}:")
            for i, tag in enumerate(tags, 1):
                print(f"  {i}. {tag}")

        sys.exit(0)

else:
    def main():
        parser = argparse.ArgumentParser(description='Suggest tags for markdown document')
        parser.add_argument('file_path', help='Path to markdown file')
        parser.add_argument('--num-tags', '-n', type=int, default=7, help='Number of tags')
        parser.add_argument('--min-score', '-m', type=float, default=1.0, help='Minimum score')
        parser.add_argument('--yaml', action='store_true', help='Output as YAML')

        args = parser.parse_args()

        suggester = TagSuggester(Path(args.file_path))
        tags = suggester.suggest(num_tags=args.num_tags, min_score=args.min_score)

        if not tags:
            print("No tags suggested")
            sys.exit(1)

        if args.yaml:
            tags_str = ', '.join(f'"{tag}"' for tag in tags)
            print(f"tags: [{tags_str}]")
        else:
            print(f"Suggested tags for {args.file_path}:")
            for i, tag in enumerate(tags, 1):
                print(f"  {i}. {tag}")

        sys.exit(0)


if __name__ == '__main__':
    main()
