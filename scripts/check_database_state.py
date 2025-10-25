#!/usr/bin/env python3
"""Quick script to check database state"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.database.database_manager import DatabaseManager

db = DatabaseManager()

print("=" * 80)
print("DATABASE STATE CHECK")
print("=" * 80)

# Check resume sentences
print("\nRESUME SENTENCES:")
query = """
SELECT
    keyword_filter_status,
    truthfulness_status,
    canadian_spelling_status,
    tone_analysis_status,
    skill_analysis_status,
    COUNT(*) as count
FROM sentence_bank_resume
GROUP BY keyword_filter_status, truthfulness_status, canadian_spelling_status, tone_analysis_status, skill_analysis_status
ORDER BY count DESC;
"""
results = db.execute_query(query, ())
for row in results:
    print(f"  {row}")

# Check cover letter sentences
print("\nCOVER LETTER SENTENCES:")
query = """
SELECT
    keyword_filter_status,
    truthfulness_status,
    canadian_spelling_status,
    tone_analysis_status,
    skill_analysis_status,
    COUNT(*) as count
FROM sentence_bank_cover_letter
GROUP BY keyword_filter_status, truthfulness_status, canadian_spelling_status, tone_analysis_status, skill_analysis_status
ORDER BY count DESC;
"""
results = db.execute_query(query, ())
for row in results:
    print(f"  {row}")

# Check specific pending counts
print("\nPENDING COUNTS:")
for table in ['sentence_bank_resume', 'sentence_bank_cover_letter']:
    query = f"SELECT COUNT(*) FROM {table} WHERE keyword_filter_status = 'pending'"
    result = db.execute_query(query, ())
    print(f"  {table}: {result[0][0] if result else 0} with keyword_filter_status='pending'")

print("\n" + "=" * 80)
