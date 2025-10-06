#!/usr/bin/env python3
"""
Database Schema Automation Enforcement
Ensures automated tools are used instead of manual changes
"""

import os
import sys
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Optional

class AutomationEnforcement:
    """
    Enforces use of automated database tools instead of manual changes
    """
    
    def __init__(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.hash_file = os.path.join(self.base_path, '.schema_hash')
        self.enforcement_log = os.path.join(self.base_path, 'enforcement.log')
        
    def check_schema_changes(self) -> Dict[str, any]:
        """
        Check if schema has changed and enforcement is needed
        Returns dict with change status and required actions
        """
        try:
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            from database_tools.database_schema_generator import DatabaseSchemaGenerator
            
            # Get current schema
            generator = DatabaseSchemaGenerator()
            current_schema = generator.extract_schema_information()
            current_hash = self._generate_schema_hash(current_schema)
            
            # Load stored hash
            stored_hash = self._load_stored_hash()
            
            result = {
                'schema_changed': current_hash != stored_hash,
                'current_hash': current_hash,
                'stored_hash': stored_hash,
                'timestamp': datetime.now().isoformat(),
                'required_actions': []
            }
            
            if result['schema_changed']:
                result['required_actions'] = [
                    'Update HTML visualization',
                    'Generate documentation',
                    'Update generated code',
                    'Commit changes to version control'
                ]
                
                # Log the change
                self._log_schema_change(result)
            
            return result
            
        except Exception as e:
            return {
                'error': str(e),
                'schema_changed': False,
                'timestamp': datetime.now().isoformat()
            }
    
    def enforce_automation_workflow(self) -> Dict[str, any]:
        """
        Enforce the automated workflow for schema changes
        Returns status of enforcement actions
        """
        check_result = self.check_schema_changes()
        
        if check_result.get('error'):
            return {
                'success': False,
                'error': check_result['error'],
                'message': 'Failed to check schema changes'
            }
        
        if not check_result['schema_changed']:
            return {
                'success': True,
                'message': 'No schema changes detected - automation not required',
                'actions_taken': []
            }
        
        # Schema has changed - enforce automation
        actions_taken = []
        
        try:
            # 1. Update HTML visualization
            from database_tools.schema_html_generator import SchemaHTMLGenerator
            html_generator = SchemaHTMLGenerator()
            html_generator.generate_html()
            actions_taken.append('Updated HTML visualization')
            
            # 2. Generate documentation
            from database_tools.database_schema_generator import DatabaseSchemaGenerator
            schema_generator = DatabaseSchemaGenerator()
            schema_generator.generate_all_documentation()
            actions_taken.append('Generated documentation')
            
            # 3. Update generated code
            from database_tools.code_generator import CodeGenerator
            code_generator = CodeGenerator()
            code_generator.save_generated_code()
            actions_taken.append('Updated generated code')
            
            # 4. Update stored hash
            self._save_schema_hash(check_result['current_hash'])
            actions_taken.append('Updated schema hash')
            
            # Log successful enforcement
            self._log_enforcement_success(actions_taken)
            
            return {
                'success': True,
                'message': 'Schema changes detected and automated workflow enforced',
                'actions_taken': actions_taken,
                'schema_hash': check_result['current_hash']
            }
            
        except Exception as e:
            self._log_enforcement_error(str(e))
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to enforce automation workflow',
                'actions_taken': actions_taken
            }
    
    def create_enforcement_reminder(self) -> str:
        """
        Create a reminder file for developers about using automation
        """
        reminder_content = """
# DATABASE SCHEMA AUTOMATION REMINDER

## IMPORTANT: Use Automated Tools Only

When making database schema changes, ALWAYS use the automated tools:

### Required Workflow:
1. Make schema changes to PostgreSQL database
2. Run: python database_tools/update_schema.py
3. Commit generated files to version control

### Automated Tools:
- `python database_tools/update_schema.py` - Manual update
- `python database_tools/schema_automation.py --check` - Check changes
- `python database_tools/schema_automation.py --force` - Force update
- `./update_database_schema.sh` - Shell wrapper

### DO NOT:
- Manually edit frontend_templates/database_schema.html
- Manually edit database_tools/docs/ files
- Manually edit database_tools/generated/ files
- Skip running automation after schema changes

### WHY:
- Ensures documentation accuracy
- Prevents inconsistencies
- Maintains code generation synchronization
- Preserves change detection system

For questions, see docs/SCHEMA_AUTOMATION.md
"""
        
        reminder_file = os.path.join(self.base_path, 'AUTOMATION_REMINDER.md')
        with open(reminder_file, 'w') as f:
            f.write(reminder_content.strip())
        
        return reminder_file
    
    def _generate_schema_hash(self, schema_data: Dict) -> str:
        """Generate SHA-256 hash of schema data"""
        schema_str = json.dumps(schema_data, sort_keys=True)
        return hashlib.sha256(schema_str.encode()).hexdigest()
    
    def _load_stored_hash(self) -> Optional[str]:
        """Load stored schema hash"""
        if not os.path.exists(self.hash_file):
            return None
        
        with open(self.hash_file, 'r') as f:
            return f.read().strip()
    
    def _save_schema_hash(self, hash_value: str):
        """Save schema hash to file"""
        with open(self.hash_file, 'w') as f:
            f.write(hash_value)
    
    def _log_schema_change(self, change_info: Dict):
        """Log schema change detection"""
        log_entry = {
            'timestamp': change_info['timestamp'],
            'event': 'schema_change_detected',
            'current_hash': change_info['current_hash'],
            'stored_hash': change_info['stored_hash'],
            'required_actions': change_info['required_actions']
        }
        self._write_log(log_entry)
    
    def _log_enforcement_success(self, actions_taken: List[str]):
        """Log successful enforcement"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event': 'automation_enforced',
            'actions_taken': actions_taken,
            'status': 'success'
        }
        self._write_log(log_entry)
    
    def _log_enforcement_error(self, error: str):
        """Log enforcement error"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event': 'automation_enforcement_error',
            'error': error,
            'status': 'failed'
        }
        self._write_log(log_entry)
    
    def _write_log(self, log_entry: Dict):
        """Write log entry to file"""
        with open(self.enforcement_log, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

def main():
    """Command line interface for enforcement"""
    enforcement = AutomationEnforcement()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == '--check':
            result = enforcement.check_schema_changes()
            print(json.dumps(result, indent=2))
        elif command == '--enforce':
            result = enforcement.enforce_automation_workflow()
            print(json.dumps(result, indent=2))
        elif command == '--create-reminder':
            reminder_file = enforcement.create_enforcement_reminder()
            print(f"Created reminder file: {reminder_file}")
        else:
            print("Usage: python enforce_automation.py [--check|--enforce|--create-reminder]")
    else:
        # Default: check and enforce if needed
        result = enforcement.enforce_automation_workflow()
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()