#!/usr/bin/env python3
"""Quick script to check sentence bank status"""

import sys
sys.path.append('/workspace')

from modules.database.database_manager import DatabaseManager

db = DatabaseManager()

# Check resume sentences
print("=== RESUME SENTENCES ===")
resume_query = """
SELECT COUNT(*) as total, keyword_filter_status, truthfulness_status
FROM sentence_bank_resume
GROUP BY keyword_filter_status, truthfulness_status
"""

results = db.execute_query(resume_query, ())
print(f"Type of results: {type(results)}")
print(f"Results: {results}")

if results:
    for row in results:
        print(f"Row: {row}")
        # Try to access by index
        try:
            print(f"Count: {row[0]}, Keyword: {row[1]}, Truthfulness: {row[2]}")
        except:
            # Try dict access
            print(f"Dict keys: {row.keys() if hasattr(row, 'keys') else 'no keys'}")
            if hasattr(row, 'items'):
                for k, v in row.items():
                    print(f"  {k}: {v}")

# Simple count
count_query = "SELECT COUNT(*) FROM sentence_bank_resume"
count_result = db.execute_query(count_query, ())
print(f"\nTotal resume sentences: {count_result}")

# Check one row
sample_query = "SELECT id, content_text, keyword_filter_status, truthfulness_status FROM sentence_bank_resume LIMIT 1"
sample_result = db.execute_query(sample_query, ())
print(f"\nSample row: {sample_result}")
