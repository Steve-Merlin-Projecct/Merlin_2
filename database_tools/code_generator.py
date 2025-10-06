#!/usr/bin/env python3
"""
Database-Driven Code Generator
Automatically generates Python code from database schema changes
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Tuple
from database_schema_generator import DatabaseSchemaGenerator


class CodeGenerator:
    """
    Generates code from database schema information
    """
    
    def __init__(self):
        self.schema_generator = DatabaseSchemaGenerator()
        self.type_mappings = {
            'uuid': 'str',
            'character varying': 'str',
            'text': 'str',
            'integer': 'int',
            'double precision': 'float',
            'numeric': 'float',
            'boolean': 'bool',
            'timestamp without time zone': 'datetime',
            'date': 'date',
            'json': 'Dict[str, Any]',
            'jsonb': 'Dict[str, Any]',
            'ARRAY': 'List[str]'
        }
    
    def generate_sqlalchemy_models(self, schema_data: Dict[str, Any]) -> str:
        """
        Generate SQLAlchemy model classes from schema
        """
        models_code = f'''"""
Auto-generated SQLAlchemy Models
Generated from database schema on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Date, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, date
from typing import Dict, Any, List, Optional
import uuid

Base = declarative_base()

'''
        
        # Generate model classes
        for table in schema_data['tables']:
            table_name = table['name']
            class_name = self._to_class_name(table_name)
            columns = schema_data['columns'].get(table_name, [])
            constraints = schema_data['constraints'].get(table_name, [])
            
            models_code += f"class {class_name}(Base):\n"
            models_code += f'    __tablename__ = "{table_name}"\n\n'
            
            # Add columns
            for col in columns:
                column_def = self._generate_column_definition(col, constraints)
                models_code += f"    {column_def}\n"
            
            # Add relationships
            relationships = self._get_relationships(table_name, schema_data)
            for rel in relationships:
                models_code += f"    {rel}\n"
            
            # Add utility methods
            models_code += "\n    def to_dict(self) -> Dict[str, Any]:\n"
            models_code += "        return {\n"
            for col in columns:
                col_name = col['name']
                models_code += f'            "{col_name}": self.{col_name},\n'
            models_code += "        }\n"
            
            models_code += f"\n    def __repr__(self) -> str:\n"
            primary_key = self._get_primary_key(constraints)
            if primary_key:
                models_code += f'        return f"<{class_name}({{self.{primary_key}}})>"\n'
            else:
                models_code += f'        return f"<{class_name}>"\n'
            
            models_code += "\n\n"
        
        return models_code
    
    def generate_pydantic_schemas(self, schema_data: Dict[str, Any]) -> str:
        """
        Generate Pydantic schemas for API validation
        """
        schemas_code = f'''"""
Auto-generated Pydantic Schemas
Generated from database schema on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, date
from typing import Dict, Any, List, Optional
from uuid import UUID

'''
        
        # Generate schemas for each table
        for table in schema_data['tables']:
            table_name = table['name']
            class_name = self._to_class_name(table_name)
            columns = schema_data['columns'].get(table_name, [])
            
            # Base schema (for creation)
            schemas_code += f"class {class_name}Base(BaseModel):\n"
            schemas_code += "    model_config = ConfigDict(from_attributes=True)\n\n"
            
            for col in columns:
                if col['name'] in ['id', 'created_at', 'updated_at']:
                    continue  # Skip auto-generated fields in base schema
                
                field_def = self._generate_pydantic_field(col)
                schemas_code += f"    {field_def}\n"
            
            schemas_code += "\n\n"
            
            # Create schema (inherits from base)
            schemas_code += f"class {class_name}Create({class_name}Base):\n"
            schemas_code += "    pass\n\n\n"
            
            # Update schema (all fields optional)
            schemas_code += f"class {class_name}Update(BaseModel):\n"
            schemas_code += "    model_config = ConfigDict(from_attributes=True)\n\n"
            
            for col in columns:
                if col['name'] in ['id', 'created_at']:
                    continue  # Skip immutable fields
                
                field_def = self._generate_pydantic_field(col, optional=True)
                schemas_code += f"    {field_def}\n"
            
            schemas_code += "\n\n"
            
            # Response schema (includes all fields)
            schemas_code += f"class {class_name}Response({class_name}Base):\n"
            
            for col in columns:
                if col['name'] in [c['name'] for c in columns if not col['name'] in ['id', 'created_at', 'updated_at']]:
                    continue  # Already in base
                
                field_def = self._generate_pydantic_field(col)
                schemas_code += f"    {field_def}\n"
            
            schemas_code += "\n\n"
        
        return schemas_code
    
    def generate_crud_operations(self, schema_data: Dict[str, Any]) -> str:
        """
        Generate CRUD operations for each table
        """
        crud_code = f'''"""
Auto-generated CRUD Operations
Generated from database schema on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

# Import models and schemas (adjust import paths as needed)
# from .models import *
# from .schemas import *

'''
        
        # Generate CRUD class for each table
        for table in schema_data['tables']:
            table_name = table['name']
            class_name = self._to_class_name(table_name)
            columns = schema_data['columns'].get(table_name, [])
            constraints = schema_data['constraints'].get(table_name, [])
            primary_key = self._get_primary_key(constraints)
            
            crud_code += f"class {class_name}CRUD:\n"
            crud_code += f'    """\n'
            crud_code += f'    CRUD operations for {table_name} table\n'
            crud_code += f'    """\n\n'
            
            # Create method
            crud_code += f"    @staticmethod\n"
            crud_code += f"    def create(db: Session, obj_data: Dict[str, Any]) -> {class_name}:\n"
            crud_code += f'        """\n'
            crud_code += f'        Create a new {table_name} record\n'
            crud_code += f'        """\n'
            crud_code += f"        db_obj = {class_name}(**obj_data)\n"
            crud_code += f"        db.add(db_obj)\n"
            crud_code += f"        db.commit()\n"
            crud_code += f"        db.refresh(db_obj)\n"
            crud_code += f"        return db_obj\n\n"
            
            # Get by ID method
            if primary_key:
                crud_code += f"    @staticmethod\n"
                crud_code += f"    def get_by_id(db: Session, {primary_key}: UUID) -> Optional[{class_name}]:\n"
                crud_code += f'        """\n'
                crud_code += f'        Get {table_name} by ID\n'
                crud_code += f'        """\n'
                crud_code += f"        return db.query({class_name}).filter({class_name}.{primary_key} == {primary_key}).first()\n\n"
            
            # Get all method
            crud_code += f"    @staticmethod\n"
            crud_code += f"    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[{class_name}]:\n"
            crud_code += f'        """\n'
            crud_code += f'        Get all {table_name} records with pagination\n'
            crud_code += f'        """\n'
            crud_code += f"        return db.query({class_name}).offset(skip).limit(limit).all()\n\n"
            
            # Update method
            if primary_key:
                crud_code += f"    @staticmethod\n"
                crud_code += f"    def update(db: Session, {primary_key}: UUID, update_data: Dict[str, Any]) -> Optional[{class_name}]:\n"
                crud_code += f'        """\n'
                crud_code += f'        Update {table_name} record\n'
                crud_code += f'        """\n'
                crud_code += f"        db_obj = db.query({class_name}).filter({class_name}.{primary_key} == {primary_key}).first()\n"
                crud_code += f"        if db_obj:\n"
                crud_code += f"            for field, value in update_data.items():\n"
                crud_code += f"                if hasattr(db_obj, field):\n"
                crud_code += f"                    setattr(db_obj, field, value)\n"
                crud_code += f"            db.commit()\n"
                crud_code += f"            db.refresh(db_obj)\n"
                crud_code += f"        return db_obj\n\n"
            
            # Delete method
            if primary_key:
                crud_code += f"    @staticmethod\n"
                crud_code += f"    def delete(db: Session, {primary_key}: UUID) -> bool:\n"
                crud_code += f'        """\n'
                crud_code += f'        Delete {table_name} record\n'
                crud_code += f'        """\n'
                crud_code += f"        db_obj = db.query({class_name}).filter({class_name}.{primary_key} == {primary_key}).first()\n"
                crud_code += f"        if db_obj:\n"
                crud_code += f"            db.delete(db_obj)\n"
                crud_code += f"            db.commit()\n"
                crud_code += f"            return True\n"
                crud_code += f"        return False\n\n"
            
            # Custom query methods based on table purpose
            custom_methods = self._generate_custom_methods(table_name, class_name, columns)
            crud_code += custom_methods
            
            crud_code += "\n\n"
        
        return crud_code
    
    def generate_api_routes(self, schema_data: Dict[str, Any]) -> str:
        """
        Generate FastAPI/Flask routes for each table
        """
        routes_code = f'''"""
Auto-generated API Routes
Generated from database schema on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from uuid import UUID
import uuid

# Import database session and CRUD operations (adjust imports as needed)
# from .database import get_db_session
# from .crud import *
# from .schemas import *

'''
        
        # Generate routes for each table
        for table in schema_data['tables']:
            table_name = table['name']
            class_name = self._to_class_name(table_name)
            constraints = schema_data['constraints'].get(table_name, [])
            primary_key = self._get_primary_key(constraints)
            
            blueprint_name = table_name.replace('_', '-')
            
            routes_code += f"# {class_name} Routes\n"
            routes_code += f"{table_name}_bp = Blueprint('{table_name}', __name__, url_prefix='/api/{blueprint_name}')\n\n"
            
            # GET all records
            routes_code += f"@{table_name}_bp.route('/', methods=['GET'])\n"
            routes_code += f"def get_{table_name}_list():\n"
            routes_code += f'    """\n'
            routes_code += f'    Get all {table_name} records\n'
            routes_code += f'    """\n'
            routes_code += f"    try:\n"
            routes_code += f"        skip = request.args.get('skip', 0, type=int)\n"
            routes_code += f"        limit = request.args.get('limit', 100, type=int)\n"
            routes_code += f"        \n"
            routes_code += f"        with get_db_session() as db:\n"
            routes_code += f"            records = {class_name}CRUD.get_all(db, skip=skip, limit=limit)\n"
            routes_code += f"            return jsonify([record.to_dict() for record in records])\n"
            routes_code += f"    except Exception as e:\n"
            routes_code += f"        return jsonify({{'error': str(e)}}), 500\n\n"
            
            # GET single record
            if primary_key:
                routes_code += f"@{table_name}_bp.route('/<uuid:{primary_key}>', methods=['GET'])\n"
                routes_code += f"def get_{table_name}_by_id({primary_key}):\n"
                routes_code += f'    """\n'
                routes_code += f'    Get {table_name} by ID\n'
                routes_code += f'    """\n'
                routes_code += f"    try:\n"
                routes_code += f"        with get_db_session() as db:\n"
                routes_code += f"            record = {class_name}CRUD.get_by_id(db, {primary_key})\n"
                routes_code += f"            if record:\n"
                routes_code += f"                return jsonify(record.to_dict())\n"
                routes_code += f"            return jsonify({{'error': 'Record not found'}}), 404\n"
                routes_code += f"    except Exception as e:\n"
                routes_code += f"        return jsonify({{'error': str(e)}}), 500\n\n"
            
            # POST create record
            routes_code += f"@{table_name}_bp.route('/', methods=['POST'])\n"
            routes_code += f"def create_{table_name}():\n"
            routes_code += f'    """\n'
            routes_code += f'    Create new {table_name} record\n'
            routes_code += f'    """\n'
            routes_code += f"    try:\n"
            routes_code += f"        data = request.get_json()\n"
            routes_code += f"        if not data:\n"
            routes_code += f"            return jsonify({{'error': 'No data provided'}}), 400\n"
            routes_code += f"        \n"
            routes_code += f"        with get_db_session() as db:\n"
            routes_code += f"            record = {class_name}CRUD.create(db, data)\n"
            routes_code += f"            return jsonify(record.to_dict()), 201\n"
            routes_code += f"    except Exception as e:\n"
            routes_code += f"        return jsonify({{'error': str(e)}}), 500\n\n"
            
            # PUT update record
            if primary_key:
                routes_code += f"@{table_name}_bp.route('/<uuid:{primary_key}>', methods=['PUT'])\n"
                routes_code += f"def update_{table_name}({primary_key}):\n"
                routes_code += f'    """\n'
                routes_code += f'    Update {table_name} record\n'
                routes_code += f'    """\n'
                routes_code += f"    try:\n"
                routes_code += f"        data = request.get_json()\n"
                routes_code += f"        if not data:\n"
                routes_code += f"            return jsonify({{'error': 'No data provided'}}), 400\n"
                routes_code += f"        \n"
                routes_code += f"        with get_db_session() as db:\n"
                routes_code += f"            record = {class_name}CRUD.update(db, {primary_key}, data)\n"
                routes_code += f"            if record:\n"
                routes_code += f"                return jsonify(record.to_dict())\n"
                routes_code += f"            return jsonify({{'error': 'Record not found'}}), 404\n"
                routes_code += f"    except Exception as e:\n"
                routes_code += f"        return jsonify({{'error': str(e)}}), 500\n\n"
            
            # DELETE record
            if primary_key:
                routes_code += f"@{table_name}_bp.route('/<uuid:{primary_key}>', methods=['DELETE'])\n"
                routes_code += f"def delete_{table_name}({primary_key}):\n"
                routes_code += f'    """\n'
                routes_code += f'    Delete {table_name} record\n'
                routes_code += f'    """\n'
                routes_code += f"    try:\n"
                routes_code += f"        with get_db_session() as db:\n"
                routes_code += f"            success = {class_name}CRUD.delete(db, {primary_key})\n"
                routes_code += f"            if success:\n"
                routes_code += f"                return jsonify({{'message': 'Record deleted successfully'}})\n"
                routes_code += f"            return jsonify({{'error': 'Record not found'}}), 404\n"
                routes_code += f"    except Exception as e:\n"
                routes_code += f"        return jsonify({{'error': str(e)}}), 500\n\n"
            
            routes_code += "\n"
        
        return routes_code
    
    def generate_migration_script(self, old_schema: Dict[str, Any], new_schema: Dict[str, Any]) -> str:
        """
        Generate database migration script from schema changes
        """
        migration_code = f'''"""
Database Migration Script
Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

from sqlalchemy import text
from sqlalchemy.orm import Session

def migrate_database(db: Session):
    """
    Apply database schema changes
    """
    migration_statements = []
    
'''
        
        # Detect schema changes
        old_tables = {table['name']: table for table in old_schema.get('tables', [])}
        new_tables = {table['name']: table for table in new_schema.get('tables', [])}
        
        # New tables
        for table_name in new_tables:
            if table_name not in old_tables:
                migration_code += f"    # Create new table: {table_name}\n"
                migration_code += f"    migration_statements.append(\"\"\"\n"
                migration_code += self._generate_create_table_sql(table_name, new_schema)
                migration_code += f"    \"\"\")\n\n"
        
        # Dropped tables
        for table_name in old_tables:
            if table_name not in new_tables:
                migration_code += f"    # Drop table: {table_name}\n"
                migration_code += f"    migration_statements.append(\"DROP TABLE IF EXISTS {table_name} CASCADE;\")\n\n"
        
        # Modified tables
        for table_name in new_tables:
            if table_name in old_tables:
                column_changes = self._detect_column_changes(table_name, old_schema, new_schema)
                for change in column_changes:
                    migration_code += f"    # {change['description']}\n"
                    migration_code += f"    migration_statements.append(\"\"\"{change['sql']}\"\"\")\n\n"
        
        migration_code += '''
    # Execute migrations
    for statement in migration_statements:
        try:
            db.execute(text(statement))
            print(f"Executed: {statement[:50]}...")
        except Exception as e:
            print(f"Error executing migration: {e}")
            print(f"Statement: {statement}")
            raise
    
    db.commit()
    print("Migration completed successfully!")

'''
        
        return migration_code
    
    def _to_class_name(self, table_name: str) -> str:
        """Convert table name to class name"""
        return ''.join(word.capitalize() for word in table_name.split('_'))
    
    def _generate_column_definition(self, col: Dict[str, Any], constraints: List[Dict[str, Any]]) -> str:
        """Generate SQLAlchemy column definition"""
        col_name = col['name']
        data_type = col['data_type']
        
        # Map PostgreSQL types to SQLAlchemy types
        if data_type == 'uuid':
            sqlalchemy_type = 'UUID(as_uuid=True)'
        elif data_type.startswith('character varying'):
            length = col.get('max_length', 255)
            sqlalchemy_type = f'String({length})'
        elif data_type == 'text':
            sqlalchemy_type = 'Text'
        elif data_type == 'integer':
            sqlalchemy_type = 'Integer'
        elif data_type == 'double precision':
            sqlalchemy_type = 'Float'
        elif data_type == 'numeric':
            sqlalchemy_type = 'Float'
        elif data_type == 'boolean':
            sqlalchemy_type = 'Boolean'
        elif data_type == 'timestamp without time zone':
            sqlalchemy_type = 'DateTime'
        elif data_type == 'date':
            sqlalchemy_type = 'Date'
        elif data_type in ['json', 'jsonb']:
            sqlalchemy_type = 'JSON'
        elif data_type == 'ARRAY':
            sqlalchemy_type = 'ARRAY(String)'
        else:
            sqlalchemy_type = 'String'
        
        # Build column definition
        col_def = f"{col_name} = Column({sqlalchemy_type}"
        
        # Add constraints
        col_constraints = [c for c in constraints if c['column'] == col_name]
        for constraint in col_constraints:
            if constraint['type'] == 'PRIMARY KEY':
                col_def += ", primary_key=True"
            elif constraint['type'] == 'FOREIGN KEY':
                foreign_table = constraint['foreign_table']
                foreign_column = constraint['foreign_column']
                col_def += f", ForeignKey('{foreign_table}.{foreign_column}')"
            elif constraint['type'] == 'UNIQUE':
                col_def += ", unique=True"
        
        if not col['nullable']:
            col_def += ", nullable=False"
        
        if col['default']:
            default_val = col['default']
            if 'gen_random_uuid()' in str(default_val):
                col_def += ", default=uuid.uuid4"
            elif 'CURRENT_TIMESTAMP' in str(default_val):
                col_def += ", default=datetime.utcnow"
        
        col_def += ")"
        
        return col_def
    
    def _generate_pydantic_field(self, col: Dict[str, Any], optional: bool = False) -> str:
        """Generate Pydantic field definition"""
        col_name = col['name']
        python_type = self.type_mappings.get(col['data_type'], 'str')
        
        if optional or col['nullable']:
            python_type = f"Optional[{python_type}]"
            default = " = None"
        else:
            default = ""
        
        return f"{col_name}: {python_type}{default}"
    
    def _get_primary_key(self, constraints: List[Dict[str, Any]]) -> str:
        """Get primary key column name"""
        for constraint in constraints:
            if constraint['type'] == 'PRIMARY KEY':
                return constraint['column']
        return None
    
    def _get_relationships(self, table_name: str, schema_data: Dict[str, Any]) -> List[str]:
        """Generate SQLAlchemy relationships"""
        relationships = []
        constraints = schema_data['constraints'].get(table_name, [])
        
        # Foreign key relationships (many-to-one)
        for constraint in constraints:
            if constraint['type'] == 'FOREIGN KEY' and constraint['foreign_table']:
                foreign_table = constraint['foreign_table']
                foreign_class = self._to_class_name(foreign_table)
                rel_name = foreign_table.replace('_', '')
                relationships.append(f"{rel_name} = relationship('{foreign_class}', back_populates='{table_name}')")
        
        return relationships
    
    def _generate_custom_methods(self, table_name: str, class_name: str, columns: List[Dict[str, Any]]) -> str:
        """Generate custom CRUD methods based on table purpose"""
        custom_methods = ""
        
        # Generate search methods for text fields
        text_columns = [col for col in columns if col['data_type'] in ['text', 'character varying']]
        if text_columns:
            custom_methods += f"    @staticmethod\n"
            custom_methods += f"    def search(db: Session, query: str, limit: int = 50) -> List[{class_name}]:\n"
            custom_methods += f'        """\n'
            custom_methods += f'        Search {table_name} records by text content\n'
            custom_methods += f'        """\n'
            
            search_conditions = []
            for col in text_columns[:3]:  # Limit to first 3 text columns
                search_conditions.append(f"{class_name}.{col['name']}.ilike(f'%{{query}}%')")
            
            if search_conditions:
                custom_methods += f"        return db.query({class_name}).filter(\n"
                custom_methods += "            db.or_(\n"
                for condition in search_conditions:
                    custom_methods += f"                {condition},\n"
                custom_methods += "            )\n"
                custom_methods += "        ).limit(limit).all()\n\n"
        
        # Generate status-based methods if status column exists
        status_columns = [col for col in columns if 'status' in col['name']]
        if status_columns:
            status_col = status_columns[0]['name']
            custom_methods += f"    @staticmethod\n"
            custom_methods += f"    def get_by_status(db: Session, status: str) -> List[{class_name}]:\n"
            custom_methods += f'        """\n'
            custom_methods += f'        Get {table_name} records by status\n'
            custom_methods += f'        """\n'
            custom_methods += f"        return db.query({class_name}).filter({class_name}.{status_col} == status).all()\n\n"
        
        return custom_methods
    
    def _generate_create_table_sql(self, table_name: str, schema_data: Dict[str, Any]) -> str:
        """Generate CREATE TABLE SQL statement"""
        columns = schema_data['columns'].get(table_name, [])
        constraints = schema_data['constraints'].get(table_name, [])
        
        sql = f"CREATE TABLE {table_name} (\n"
        
        # Add columns
        column_defs = []
        for col in columns:
            col_def = f"    {col['name']} {col['data_type']}"
            if col['max_length']:
                col_def += f"({col['max_length']})"
            if not col['nullable']:
                col_def += " NOT NULL"
            if col['default']:
                col_def += f" DEFAULT {col['default']}"
            column_defs.append(col_def)
        
        sql += ",\n".join(column_defs)
        
        # Add constraints
        constraint_defs = []
        for constraint in constraints:
            if constraint['type'] == 'PRIMARY KEY':
                constraint_defs.append(f"    PRIMARY KEY ({constraint['column']})")
            elif constraint['type'] == 'FOREIGN KEY':
                constraint_defs.append(
                    f"    FOREIGN KEY ({constraint['column']}) "
                    f"REFERENCES {constraint['foreign_table']}({constraint['foreign_column']})"
                )
        
        if constraint_defs:
            sql += ",\n" + ",\n".join(constraint_defs)
        
        sql += "\n);"
        
        return sql
    
    def _detect_column_changes(self, table_name: str, old_schema: Dict[str, Any], new_schema: Dict[str, Any]) -> List[Dict[str, str]]:
        """Detect column changes between schemas"""
        changes = []
        
        old_columns = {col['name']: col for col in old_schema['columns'].get(table_name, [])}
        new_columns = {col['name']: col for col in new_schema['columns'].get(table_name, [])}
        
        # New columns
        for col_name in new_columns:
            if col_name not in old_columns:
                col = new_columns[col_name]
                changes.append({
                    'description': f"Add column {col_name} to {table_name}",
                    'sql': f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col['data_type']};"
                })
        
        # Dropped columns
        for col_name in old_columns:
            if col_name not in new_columns:
                changes.append({
                    'description': f"Drop column {col_name} from {table_name}",
                    'sql': f"ALTER TABLE {table_name} DROP COLUMN {col_name};"
                })
        
        return changes
    
    def save_generated_code(self, output_dir: str = "generated"):
        """
        Generate and save all code files
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Extract schema information
        schema_data = self.schema_generator.extract_schema_information()
        
        # Generate and save models
        models_code = self.generate_sqlalchemy_models(schema_data)
        with open(f"{output_dir}/models.py", "w") as f:
            f.write(models_code)
        
        # Generate and save schemas
        schemas_code = self.generate_pydantic_schemas(schema_data)
        with open(f"{output_dir}/schemas.py", "w") as f:
            f.write(schemas_code)
        
        # Generate and save CRUD operations
        crud_code = self.generate_crud_operations(schema_data)
        with open(f"{output_dir}/crud.py", "w") as f:
            f.write(crud_code)
        
        # Generate and save API routes
        routes_code = self.generate_api_routes(schema_data)
        with open(f"{output_dir}/routes.py", "w") as f:
            f.write(routes_code)
        
        print(f"Code generated in {output_dir}/")
        print(f"- models.py (SQLAlchemy models)")
        print(f"- schemas.py (Pydantic schemas)")
        print(f"- crud.py (CRUD operations)")
        print(f"- routes.py (API routes)")


def main():
    """
    Command-line interface for code generation
    """
    generator = CodeGenerator()
    generator.save_generated_code()


if __name__ == "__main__":
    main()