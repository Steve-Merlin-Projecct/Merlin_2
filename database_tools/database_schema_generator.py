#!/usr/bin/env python3
"""
Database Schema Documentation Generator
Automatically generates comprehensive database documentation from PostgreSQL information_schema
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any
import sys
sys.path.append('..')
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.database.database_client import DatabaseClient
from sqlalchemy import text


class DatabaseSchemaGenerator:
    """
    Generates comprehensive database schema documentation
    """
    
    def __init__(self):
        self.db_client = DatabaseClient()
        self.schema_data = {}
        
    def extract_schema_information(self) -> Dict[str, Any]:
        """
        Extract complete schema information from PostgreSQL information_schema
        """
        with self.db_client.get_session() as session:
            # Get all tables
            tables_query = text("""
                SELECT table_name
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """)
            tables_result = session.execute(tables_query)
            tables = [{'name': row[0], 'comment': None} for row in tables_result]
            
            # Get detailed column information
            columns_query = text("""
                SELECT 
                    t.table_name,
                    c.column_name,
                    c.data_type,
                    c.character_maximum_length,
                    c.numeric_precision,
                    c.numeric_scale,
                    c.is_nullable,
                    c.column_default,
                    c.ordinal_position
                FROM information_schema.tables t
                JOIN information_schema.columns c ON t.table_name = c.table_name
                WHERE t.table_schema = 'public' 
                AND c.table_schema = 'public'
                ORDER BY t.table_name, c.ordinal_position
            """)
            columns_result = session.execute(columns_query)
            
            # Organize columns by table
            table_columns = {}
            for row in columns_result:
                table_name = row[0]
                if table_name not in table_columns:
                    table_columns[table_name] = []
                table_columns[table_name].append({
                    'name': row[1],
                    'data_type': row[2],
                    'max_length': row[3],
                    'precision': row[4],
                    'scale': row[5],
                    'nullable': row[6] == 'YES',
                    'default': row[7],
                    'position': row[8],
                    'comment': None
                })
            
            # Get constraints (primary keys, foreign keys, unique, check)
            constraints_query = text("""
                SELECT 
                    tc.table_name,
                    tc.constraint_name,
                    tc.constraint_type,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints tc
                LEFT JOIN information_schema.key_column_usage kcu 
                    ON tc.constraint_name = kcu.constraint_name
                LEFT JOIN information_schema.constraint_column_usage ccu 
                    ON tc.constraint_name = ccu.constraint_name
                WHERE tc.table_schema = 'public'
                ORDER BY tc.table_name, tc.constraint_type, kcu.ordinal_position
            """)
            constraints_result = session.execute(constraints_query)
            
            # Organize constraints by table
            table_constraints = {}
            for row in constraints_result:
                table_name = row[0]
                if table_name not in table_constraints:
                    table_constraints[table_name] = []
                table_constraints[table_name].append({
                    'name': row[1],
                    'type': row[2],
                    'column': row[3],
                    'foreign_table': row[4],
                    'foreign_column': row[5]
                })
            
            # Get indexes
            indexes_query = text("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    indexdef
                FROM pg_indexes 
                WHERE schemaname = 'public'
                ORDER BY tablename, indexname
            """)
            indexes_result = session.execute(indexes_query)
            
            # Organize indexes by table
            table_indexes = {}
            for row in indexes_result:
                table_name = row[1]
                if table_name not in table_indexes:
                    table_indexes[table_name] = []
                table_indexes[table_name].append({
                    'name': row[2],
                    'definition': row[3]
                })
        
        return {
            'tables': tables,
            'columns': table_columns,
            'constraints': table_constraints,
            'indexes': table_indexes,
            'generated_at': datetime.now().isoformat(),
            'database_name': os.environ.get('PGDATABASE', 'unknown')
        }
    
    def generate_markdown_documentation(self, schema_data: Dict[str, Any]) -> str:
        """
        Generate comprehensive Markdown documentation from schema data
        """
        doc = f"""# Database Schema Documentation
**Automated Job Application System**

*Last Updated: {datetime.now().strftime('%B %d, %Y')}*  
*Auto-generated from PostgreSQL information_schema*

## Overview

This database supports a comprehensive automated job application system that scrapes job postings, analyzes them with AI, manages user preferences, and tracks applications with sophisticated document generation and tone analysis.

### Architecture Summary
- **Primary Tables**: {len(schema_data['tables'])} tables with UUID primary keys
- **Database**: {schema_data['database_name']}
- **Generated**: {schema_data['generated_at']}

---

## Table Summary

| Table Name | Purpose | Key Relationships |
|------------|---------|-------------------|
"""
        
        # Add table summary
        for table in schema_data['tables']:
            table_name = table['name']
            constraints = schema_data['constraints'].get(table_name, [])
            foreign_keys = [c for c in constraints if c['type'] == 'FOREIGN KEY']
            fk_summary = ', '.join([f"{c['column']} → {c['foreign_table']}" for c in foreign_keys if c['foreign_table']])
            if not fk_summary:
                fk_summary = "Standalone"
            
            purpose = self._get_table_purpose(table_name)
            doc += f"| {table_name} | {purpose} | {fk_summary} |\n"
        
        doc += "\n---\n\n## Detailed Table Specifications\n\n"
        
        # Add detailed table documentation
        for table in schema_data['tables']:
            table_name = table['name']
            columns = schema_data['columns'].get(table_name, [])
            constraints = schema_data['constraints'].get(table_name, [])
            indexes = schema_data['indexes'].get(table_name, [])
            
            doc += f"### {table_name}\n"
            doc += f"**{self._get_table_purpose(table_name)}**\n\n"
            
            # Column specifications
            doc += "| Column | Type | Constraints | Description |\n"
            doc += "|--------|------|-------------|-------------|\n"
            
            for col in columns:
                # Build type string
                type_str = col['data_type']
                if col['max_length']:
                    type_str += f"({col['max_length']})"
                elif col['precision'] and col['scale']:
                    type_str += f"({col['precision']},{col['scale']})"
                elif col['precision']:
                    type_str += f"({col['precision']})"
                
                # Build constraints string
                constraints_str = []
                if not col['nullable']:
                    constraints_str.append("NOT NULL")
                if col['default']:
                    default_clean = str(col['default']).replace('::character varying', '').replace('::timestamp without time zone', '')
                    if len(default_clean) > 30:
                        default_clean = default_clean[:27] + "..."
                    constraints_str.append(f"DEFAULT {default_clean}")
                
                # Add constraint information
                col_constraints = [c for c in constraints if c['column'] == col['name']]
                for constraint in col_constraints:
                    if constraint['type'] == 'PRIMARY KEY':
                        constraints_str.append("PK")
                    elif constraint['type'] == 'FOREIGN KEY' and constraint['foreign_table']:
                        constraints_str.append(f"FK → {constraint['foreign_table']}({constraint['foreign_column']})")
                    elif constraint['type'] == 'UNIQUE':
                        constraints_str.append("UNIQUE")
                
                constraints_text = ', '.join(constraints_str) if constraints_str else ""
                description = self._get_column_description(table_name, col['name'])
                
                doc += f"| {col['name']} | {type_str} | {constraints_text} | {description} |\n"
            
            # Business rules
            business_rules = self._get_business_rules(table_name)
            if business_rules:
                doc += f"\n**Business Rules:**\n{business_rules}\n"
            
            doc += "\n"
        
        doc += self._generate_relationships_section(schema_data)
        doc += self._generate_indexes_section(schema_data)
        doc += self._generate_sample_data_section()
        
        return doc
    
    def _get_table_purpose(self, table_name: str) -> str:
        """Get descriptive purpose for each table"""
        purposes = {
            'jobs': 'Primary entity for job postings',
            'companies': 'Company information and metadata',
            'job_applications': 'Application tracking and status management',
            'user_job_preferences': 'User criteria and preference packages',
            'raw_job_scrapes': 'Raw scraped data before processing',
            'cleaned_job_scrapes': 'Processed and deduplicated job data',
            'document_jobs': 'Document generation tracking',
            'sentence_bank_resume': 'Resume content sentence bank',
            'sentence_bank_cover_letter': 'Cover letter content sentence bank',
            'document_tone_analysis': 'Document tone analysis results',
            'link_tracking': 'Hyperlink click tracking',
            'application_settings': 'System configuration and settings',
            'job_logs': 'System audit trail and debugging'
        }
        return purposes.get(table_name, 'Database table')
    
    def _get_column_description(self, table_name: str, column_name: str) -> str:
        """Get descriptive text for columns"""
        descriptions = {
            'id': 'Unique identifier',
            'created_at': 'Record creation timestamp',
            'updated_at': 'Last modification timestamp',
            'job_id': 'Associated job reference',
            'company_id': 'Associated company reference',
            'user_id': 'User identifier',
            'application_id': 'Associated application reference'
        }
        
        # Table-specific descriptions
        if table_name == 'jobs':
            job_descriptions = {
                'job_title': 'Position title',
                'salary_low': 'Minimum salary (in cents)',
                'salary_high': 'Maximum salary (in cents)',
                'eligibility_flag': 'Meets user criteria',
                'priority_score': 'AI-calculated priority (0.0-10.0)'
            }
            descriptions.update(job_descriptions)
        
        return descriptions.get(column_name, '')
    
    def _get_business_rules(self, table_name: str) -> str:
        """Get business rules for tables"""
        rules = {
            'jobs': '- Salary amounts stored in cents for precision\n- Priority score ranges 0.0-10.0, higher = better match\n- Application status: \'not_applied\', \'pending\', \'submitted\', \'responded\', \'rejected\'',
            'job_applications': '- Application status: \'submitted\', \'pending\', \'responded\', \'rejected\', \'hired\'\n- Tone scores range 0.0-1.0, lower = more coherent',
            'user_job_preferences': '- Salary amounts in cents for precision\n- Multiple preference packages per user supported\n- Contextual conditions stored as JSON for flexibility'
        }
        return rules.get(table_name, '')
    
    def _generate_relationships_section(self, schema_data: Dict[str, Any]) -> str:
        """Generate relationships documentation"""
        doc = "## Table Relationships\n\n```\n"
        
        # Add main relationships
        doc += "companies (1) ──→ (∞) jobs ──→ (∞) job_applications\n"
        doc += "                     │              │\n"
        doc += "                     ├─→ (∞) document_tone_analysis\n"
        doc += "                     ├─→ (∞) link_tracking\n"
        doc += "                     └─→ (1) user_job_preferences\n"
        doc += "                     \n"
        doc += "raw_job_scrapes ──→ cleaned_job_scrapes (processing pipeline)\n"
        doc += "```\n\n"
        
        return doc
    
    def _generate_indexes_section(self, schema_data: Dict[str, Any]) -> str:
        """Generate indexes documentation"""
        doc = "## Indexes and Performance\n\n"
        
        doc += "### Existing Indexes\n"
        for table_name, indexes in schema_data['indexes'].items():
            if indexes:
                doc += f"\n**{table_name}:**\n"
                for index in indexes:
                    doc += f"- `{index['name']}`\n"
        
        doc += "\n### Recommended Performance Indexes\n"
        doc += "```sql\n"
        doc += "-- Performance indexes (not auto-created)\n"
        doc += "CREATE INDEX idx_jobs_company_eligibility ON jobs(company_id, eligibility_flag);\n"
        doc += "CREATE INDEX idx_jobs_created_priority ON jobs(created_at DESC, priority_score DESC);\n"
        doc += "CREATE INDEX idx_applications_status_date ON job_applications(application_status, application_date DESC);\n"
        doc += "CREATE INDEX idx_raw_scrapes_website_timestamp ON raw_job_scrapes(source_website, scrape_timestamp DESC);\n"
        doc += "CREATE INDEX idx_cleaned_scrapes_title_company ON cleaned_job_scrapes(job_title, company_name);\n"
        doc += "CREATE INDEX idx_preferences_active_user ON user_job_preferences(is_active, user_id);\n"
        doc += "```\n\n"
        
        return doc
    
    def _generate_sample_data_section(self) -> str:
        """Generate sample data examples"""
        doc = "## Sample Data Examples\n\n"
        
        doc += "### Example Job Record\n"
        doc += "```sql\n"
        doc += "INSERT INTO jobs (job_title, company_id, salary_low, salary_high, location, eligibility_flag) \n"
        doc += "VALUES ('Marketing Manager', '123e4567-e89b-12d3-a456-426614174000', 6500000, 8500000, 'Edmonton, AB', true);\n"
        doc += "```\n\n"
        
        doc += "### Example User Preferences\n"
        doc += "```sql\n"
        doc += "INSERT INTO user_job_preferences (salary_minimum, salary_maximum, preferred_city, work_arrangement) \n"
        doc += "VALUES (6500000, 8500000, 'Edmonton', 'hybrid');\n"
        doc += "```\n\n"
        
        return doc
    
    def generate_json_schema(self, schema_data: Dict[str, Any]) -> str:
        """
        Generate JSON schema for API documentation and validation
        """
        json_schema = {
            "database": schema_data['database_name'],
            "generated_at": schema_data['generated_at'],
            "tables": {}
        }
        
        for table in schema_data['tables']:
            table_name = table['name']
            columns = schema_data['columns'].get(table_name, [])
            constraints = schema_data['constraints'].get(table_name, [])
            
            table_schema = {
                "description": self._get_table_purpose(table_name),
                "columns": {},
                "primary_key": [],
                "foreign_keys": [],
                "indexes": []
            }
            
            # Add columns
            for col in columns:
                table_schema["columns"][col['name']] = {
                    "type": col['data_type'],
                    "nullable": col['nullable'],
                    "default": col['default'],
                    "max_length": col['max_length'],
                    "description": self._get_column_description(table_name, col['name'])
                }
            
            # Add constraints
            for constraint in constraints:
                if constraint['type'] == 'PRIMARY KEY':
                    table_schema["primary_key"].append(constraint['column'])
                elif constraint['type'] == 'FOREIGN KEY':
                    table_schema["foreign_keys"].append({
                        "column": constraint['column'],
                        "references": f"{constraint['foreign_table']}.{constraint['foreign_column']}"
                    })
            
            json_schema["tables"][table_name] = table_schema
        
        return json.dumps(json_schema, indent=2)
    
    def save_documentation(self, output_dir: str = "docs"):
        """
        Generate and save all documentation formats
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Extract schema information
        schema_data = self.extract_schema_information()
        
        # Generate Markdown documentation
        markdown_doc = self.generate_markdown_documentation(schema_data)
        with open(f"{output_dir}/database_schema.md", "w") as f:
            f.write(markdown_doc)
        
        # Generate JSON schema
        json_schema = self.generate_json_schema(schema_data)
        with open(f"{output_dir}/database_schema.json", "w") as f:
            f.write(json_schema)
        
        # Save raw schema data
        with open(f"{output_dir}/schema_raw_data.json", "w") as f:
            json.dump(schema_data, f, indent=2, default=str)
        
        print(f"Documentation generated in {output_dir}/")
        print(f"- database_schema.md (Comprehensive documentation)")
        print(f"- database_schema.json (JSON schema for APIs)")
        print(f"- schema_raw_data.json (Raw extracted data)")


def main():
    """
    Command-line interface for schema documentation generation
    """
    generator = DatabaseSchemaGenerator()
    generator.save_documentation()


if __name__ == "__main__":
    main()