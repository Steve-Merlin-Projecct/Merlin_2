#!/usr/bin/env python3
"""
Database Schema HTML Generator
Automatically generates the database schema HTML template based on actual database structure.
"""

import os
import sys
import json
import psycopg2
from typing import Dict, List, Any
from datetime import datetime

class DatabaseSchemaHTMLGenerator:
    def __init__(self):
        self.db_url = os.environ.get('DATABASE_URL')
        if not self.db_url:
            raise ValueError("DATABASE_URL environment variable is required")
        
        # Table categorization for the HTML visualization
        self.table_categories = {
            'core_workflow': [
                'companies', 'jobs', 'job_applications', 'user_job_preferences',
                'user_job_preference_packages', 'cleaned_job_scrapes', 'raw_job_scrapes'
            ],
            'content_analysis': [
                'sentence_bank_resume', 'sentence_bank_cover_letter', 'job_analysis',
                'ai_analysis_batches', 'ai_usage_tracking'
            ],
            'tracking_monitoring': [
                'link_tracking', 'document_jobs', 'job_logs', 'application_settings'
            ]
        }
        
        # Color themes for different table categories
        self.category_colors = {
            'core_workflow': '#0066cc',
            'content_analysis': '#28a745',
            'tracking_monitoring': '#ffc107'
        }

    def get_database_schema(self) -> Dict[str, Any]:
        """Fetch complete database schema from PostgreSQL information_schema"""
        conn = psycopg2.connect(self.db_url)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        schema = {}
        
        for table in tables:
            # Get columns for each table
            cursor.execute("""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    character_maximum_length,
                    numeric_precision,
                    numeric_scale,
                    ordinal_position
                FROM information_schema.columns 
                WHERE table_name = %s 
                ORDER BY ordinal_position
            """, (table,))
            
            columns = []
            for col in cursor.fetchall():
                col_info = {
                    'name': col[0],
                    'type': col[1],
                    'nullable': col[2] == 'YES',
                    'default': col[3],
                    'max_length': col[4],
                    'precision': col[5],
                    'scale': col[6],
                    'position': col[7]
                }
                columns.append(col_info)
            
            # Get primary keys
            cursor.execute("""
                SELECT column_name
                FROM information_schema.key_column_usage
                WHERE table_name = %s
                AND constraint_name IN (
                    SELECT constraint_name
                    FROM information_schema.table_constraints
                    WHERE table_name = %s
                    AND constraint_type = 'PRIMARY KEY'
                )
            """, (table, table))
            
            primary_keys = [row[0] for row in cursor.fetchall()]
            
            # Get foreign keys
            cursor.execute("""
                SELECT 
                    kcu.column_name,
                    ccu.table_name AS foreign_table,
                    ccu.column_name AS foreign_column
                FROM information_schema.key_column_usage kcu
                JOIN information_schema.constraint_column_usage ccu
                    ON kcu.constraint_name = ccu.constraint_name
                WHERE kcu.table_name = %s
                AND kcu.constraint_name IN (
                    SELECT constraint_name
                    FROM information_schema.table_constraints
                    WHERE table_name = %s
                    AND constraint_type = 'FOREIGN KEY'
                )
            """, (table, table))
            
            foreign_keys = {}
            for fk in cursor.fetchall():
                foreign_keys[fk[0]] = {'table': fk[1], 'column': fk[2]}
            
            schema[table] = {
                'columns': columns,
                'primary_keys': primary_keys,
                'foreign_keys': foreign_keys
            }
        
        conn.close()
        return schema

    def format_column_type(self, column: Dict[str, Any]) -> str:
        """Format column type for display"""
        col_type = column['type'].upper()
        
        # Handle specific type formatting
        if col_type == 'CHARACTER VARYING':
            if column['max_length']:
                return f"VARCHAR({column['max_length']})"
            return "VARCHAR"
        elif col_type == 'TIMESTAMP WITHOUT TIME ZONE':
            return "TIMESTAMP"
        elif col_type == 'DOUBLE PRECISION':
            return "DECIMAL"
        elif col_type == 'USER-DEFINED':
            return "UUID"
        elif 'ARRAY' in col_type:
            return "ARRAY"
        
        return col_type

    def get_table_category(self, table_name: str) -> str:
        """Determine which category a table belongs to"""
        for category, tables in self.table_categories.items():
            if table_name in tables:
                return category
        return 'core_workflow'  # Default category

    def generate_table_html(self, table_name: str, table_info: Dict[str, Any]) -> str:
        """Generate HTML for a single table"""
        category = self.get_table_category(table_name)
        
        html = f'''            <div class="table-box">
                <div class="table-header">{table_name}</div>'''
        
        # Add columns
        for column in table_info['columns']:
            field_class = "field-name"
            if column['name'] in table_info['primary_keys']:
                field_class += " primary-key"
            elif column['name'] in table_info['foreign_keys']:
                field_class += " foreign-key"
            
            type_display = self.format_column_type(column)
            if column['name'] in table_info['primary_keys']:
                type_display += " (PK)"
            elif column['name'] in table_info['foreign_keys']:
                type_display += " (FK)"
            
            html += f'''
                <div class="table-field">
                    <span class="{field_class}">{column['name']}</span>
                    <span class="field-type">{type_display}</span>
                </div>'''
        
        html += '''
            </div>'''
        
        return html

    def generate_relationship_notes(self, schema: Dict[str, Any]) -> str:
        """Generate relationship notes for each category"""
        relationships = []
        
        for table_name, table_info in schema.items():
            for col_name, fk_info in table_info['foreign_keys'].items():
                relationships.append(f"{fk_info['table']}.{fk_info['column']} → {table_name}.{col_name}")
        
        if relationships:
            return f"<strong>Relationships:</strong> {' | '.join(relationships[:3])}"
        return ""

    def generate_complete_html(self, schema: Dict[str, Any]) -> str:
        """Generate the complete HTML template"""
        
        # Categorize tables
        categorized_tables = {
            'core_workflow': [],
            'content_analysis': [],
            'tracking_monitoring': []
        }
        
        for table_name, table_info in schema.items():
            category = self.get_table_category(table_name)
            categorized_tables[category].append((table_name, table_info))
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Database Schema - Job Application System</title>
    <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="/static/css/unified-theme.css" rel="stylesheet">
    <style>
        /* Unified light theme */
        body {{
            background: #f8f9fa !important;
        }}
        
        .schema-container {{
            background: #b8b8b8;
            border: 1px solid rgba(0, 0, 0, 0.1);
            border-radius: 8px;
            padding: 2rem;
            margin: 1rem 0;
            min-height: 600px;
            color: #1a1a1a;
        }}
        
        .table-box {{
            background: rgba(255, 255, 255, 0.9);
            border: 2px solid rgba(0, 0, 0, 0.2);
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem;
            position: relative;
            transition: all 0.3s ease;
            width: 280px;
            display: inline-block;
            vertical-align: top;
            color: #1a1a1a;
        }}
        
        .table-box:hover {{
            border-color: #0066cc;
            transform: scale(1.02);
            z-index: 10;
        }}
        
        .table-header {{
            background: #0066cc;
            color: white;
            padding: 0.75rem;
            margin: -1rem -1rem 1rem -1rem;
            border-radius: 6px 6px 0 0;
            font-weight: bold;
            text-align: center;
        }}
        
        .table-field {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.25rem 0;
            border-bottom: 1px solid var(--bs-gray-700);
            font-size: 0.85rem;
        }}
        
        .table-field:last-child {{
            border-bottom: none;
        }}
        
        .field-name {{
            font-weight: 500;
        }}
        
        .field-type {{
            color: var(--bs-info);
            font-size: 0.75rem;
        }}
        
        .primary-key {{
            color: var(--bs-warning);
        }}
        
        .foreign-key {{
            color: var(--bs-success);
        }}
        
        .relationship-line {{
            position: absolute;
            background: var(--bs-success);
            height: 2px;
            z-index: 1;
        }}
        
        .relationship-arrow {{
            position: absolute;
            width: 0;
            height: 0;
            border-left: 8px solid var(--bs-success);
            border-top: 4px solid transparent;
            border-bottom: 4px solid transparent;
            z-index: 2;
        }}
        
        .schema-section {{
            margin: 2rem 0;
        }}
        
        .schema-section h3 {{
            color: #1a1a1a;
            border-bottom: 2px solid #0066cc;
            padding-bottom: 0.5rem;
            margin-bottom: 1rem;
        }}
        
        .relationship-note {{
            background: rgba(255, 255, 255, 0.8);
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem;
            font-size: 0.9rem;
            border-left: 4px solid var(--bs-success);
        }}
        
        .legend {{
            background: rgba(255, 255, 255, 0.9);
            padding: 1.5rem;
            border-radius: 8px;
            margin: 1rem 0;
            border: 1px solid rgba(0, 0, 0, 0.1);
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            margin: 0.5rem 0;
        }}
        
        .legend-icon {{
            width: 16px;
            height: 16px;
            border-radius: 3px;
            margin-right: 0.5rem;
        }}
        
        .core-tables .table-header {{
            background: #0066cc;
        }}
        
        .content-tables .table-header {{
            background: #28a745;
        }}
        
        .tracking-tables .table-header {{
            background: #ffc107;
            color: #1a1a1a;
        }}
        
        .auto-generated-note {{
            background: rgba(255, 193, 7, 0.1);
            border: 1px solid #ffc107;
            border-radius: 4px;
            padding: 0.75rem;
            margin: 1rem 0;
            font-size: 0.9rem;
            color: #856404;
        }}
    </style>
</head>
<body>
    <!-- Shared Navigation -->
    {{% include 'shared_navigation.html' %}}
    
    <div class="container mt-4">
        <div class="row">
            <div class="col-12">
                <div class="enhanced-card">
                    <div class="card-header">
                        <h1 class="mb-0">
                            <i class="fas fa-database me-2"></i>
                            Database Schema Visualization
                        </h1>
                    </div>
                    <div class="card-body">
                        <div class="auto-generated-note">
                            <i class="fas fa-robot me-2"></i>
                            <strong>Auto-generated:</strong> This schema was automatically generated from the live database on {timestamp}. 
                            Run <code>python tools/schema_html_generator.py</code> to update.
                        </div>
                        
                        <div class="schema-container">
                            <div class="text-center mb-4">
                                <h2>Job Application System Database Schema</h2>
                                <p class="text-muted">Interactive visualization of all database tables and relationships</p>
                            </div>
                            
                            <!-- Legend -->
                            <div class="legend">
                                <h4>Legend</h4>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="legend-item">
                                            <div class="legend-icon" style="background: var(--bs-warning);"></div>
                                            <span>Primary Key</span>
                                        </div>
                                        <div class="legend-item">
                                            <div class="legend-icon" style="background: var(--bs-success);"></div>
                                            <span>Foreign Key</span>
                                        </div>
                                        <div class="legend-item">
                                            <div class="legend-icon" style="background: var(--bs-info);"></div>
                                            <span>Data Type</span>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="legend-item">
                                            <div class="legend-icon" style="background: #0066cc;"></div>
                                            <span>Core Workflow Tables</span>
                                        </div>
                                        <div class="legend-item">
                                            <div class="legend-icon" style="background: #28a745;"></div>
                                            <span>Content & Analysis Tables</span>
                                        </div>
                                        <div class="legend-item">
                                            <div class="legend-icon" style="background: #ffc107;"></div>
                                            <span>Tracking & Monitoring Tables</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Core Workflow Tables -->
                            <div class="schema-section core-tables">
                                <h3 class="mb-3">
                                    <i class="fas fa-cogs me-2"></i>
                                    Core Workflow Tables
                                </h3>
                                
'''

        # Add core workflow tables
        for table_name, table_info in categorized_tables['core_workflow']:
            html_template += self.generate_table_html(table_name, table_info)

        html_template += '''
                                <div class="relationship-note">
                                    ''' + self.generate_relationship_notes(dict(categorized_tables['core_workflow'])) + '''
                                </div>
                            </div>

                            <!-- Content & Analysis Tables -->
                            <div class="schema-section content-tables">
                                <h3 class="mb-3">
                                    <i class="fas fa-file-alt me-2"></i>
                                    Content & Analysis Tables
                                </h3>
                                
'''

        # Add content & analysis tables
        for table_name, table_info in categorized_tables['content_analysis']:
            html_template += self.generate_table_html(table_name, table_info)

        html_template += '''
                                <div class="relationship-note">
                                    ''' + self.generate_relationship_notes(dict(categorized_tables['content_analysis'])) + '''
                                </div>
                            </div>

                            <!-- Tracking & Monitoring Tables -->
                            <div class="schema-section tracking-tables">
                                <h3 class="mb-3">
                                    <i class="fas fa-chart-line me-2"></i>
                                    Tracking & Monitoring Tables
                                </h3>
                                
'''

        # Add tracking & monitoring tables
        for table_name, table_info in categorized_tables['tracking_monitoring']:
            html_template += self.generate_table_html(table_name, table_info)

        html_template += '''
                                <div class="relationship-note">
                                    ''' + self.generate_relationship_notes(dict(categorized_tables['tracking_monitoring'])) + '''
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Add hover effects and interactions
        document.querySelectorAll('.table-box').forEach(box => {
            box.addEventListener('mouseenter', function() {
                this.style.transform = 'scale(1.02)';
                this.style.zIndex = '10';
            });
            
            box.addEventListener('mouseleave', function() {
                this.style.transform = 'scale(1)';
                this.style.zIndex = '1';
            });
        });
    </script>
</body>
</html>'''

        return html_template

    def update_schema_html(self, output_path: str = None):
        """Main method to update the schema HTML file"""
        if output_path is None:
            output_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'database_schema.html')
        
        print("Fetching database schema...")
        schema = self.get_database_schema()
        
        print(f"Found {len(schema)} tables in database")
        for table_name in sorted(schema.keys()):
            column_count = len(schema[table_name]['columns'])
            print(f"  - {table_name}: {column_count} columns")
        
        print("Generating HTML template...")
        html_content = self.generate_complete_html(schema)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✓ Database schema HTML updated: {output_path}")
        print(f"✓ Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Main function for command-line usage"""
    try:
        generator = DatabaseSchemaHTMLGenerator()
        generator.update_schema_html()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()