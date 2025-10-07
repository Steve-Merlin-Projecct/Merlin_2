#!/usr/bin/env python3
"""
Database Schema Automation System
Monitors database changes and automatically updates documentation and code
"""

import os
import json
import hashlib
import argparse
from datetime import datetime
from pathlib import Path
from database_schema_generator import DatabaseSchemaGenerator
from code_generator import CodeGenerator


class SchemaAutomation:
    """
    Automated schema documentation and code generation system
    """
    
    def __init__(self, config_path: str = "database_tools/schema_config.json"):
        self.config_path = config_path
        self.config = self.load_config()
        self.schema_generator = DatabaseSchemaGenerator()
        self.code_generator = CodeGenerator()
        self.schema_hash_file = "database_tools/.schema_hash"
        
    def load_config(self) -> dict:
        """Load automation configuration"""
        default_config = {
            "documentation": {
                "enabled": True,
                "output_dir": "docs",
                "formats": ["markdown", "json"]
            },
            "code_generation": {
                "enabled": True,
                "output_dir": "generated",
                "generate_models": True,
                "generate_schemas": True,
                "generate_crud": True,
                "generate_routes": True,
                "generate_migrations": True
            },
            "monitoring": {
                "check_interval_minutes": 60,
                "auto_commit": False,
                "notify_on_changes": True
            },
            "git_integration": {
                "enabled": False,
                "auto_commit": False,
                "commit_message_template": "Auto-update: Database schema changes detected on {date}"
            }
        }
        
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                user_config = json.load(f)
                # Merge with defaults
                return {**default_config, **user_config}
        else:
            # Create default config file
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def get_schema_hash(self) -> str:
        """Generate hash of current database schema"""
        schema_data = self.schema_generator.extract_schema_information()
        
        # Create consistent string representation for hashing
        schema_str = json.dumps(schema_data, sort_keys=True, default=str)
        return hashlib.sha256(schema_str.encode()).hexdigest()
    
    def load_previous_hash(self) -> str:
        """Load previously stored schema hash"""
        if os.path.exists(self.schema_hash_file):
            with open(self.schema_hash_file, 'r') as f:
                return f.read().strip()
        return ""
    
    def save_current_hash(self, schema_hash: str):
        """Save current schema hash"""
        os.makedirs(os.path.dirname(self.schema_hash_file), exist_ok=True)
        with open(self.schema_hash_file, 'w') as f:
            f.write(schema_hash)
    
    def detect_schema_changes(self) -> bool:
        """Check if database schema has changed"""
        current_hash = self.get_schema_hash()
        previous_hash = self.load_previous_hash()
        
        if current_hash != previous_hash:
            print(f"Schema changes detected!")
            print(f"Previous hash: {previous_hash[:16]}...")
            print(f"Current hash:  {current_hash[:16]}...")
            return True
        
        return False
    
    def update_documentation(self):
        """Update schema documentation"""
        if not self.config["documentation"]["enabled"]:
            return
        
        print("Updating database schema documentation...")
        
        output_dir = self.config["documentation"]["output_dir"]
        formats = self.config["documentation"]["formats"]
        
        # Generate documentation
        schema_data = self.schema_generator.extract_schema_information()
        
        if "markdown" in formats:
            markdown_doc = self.schema_generator.generate_markdown_documentation(schema_data)
            os.makedirs(output_dir, exist_ok=True)
            with open(f"{output_dir}/database_schema.md", "w") as f:
                f.write(markdown_doc)
            print(f"✓ Updated {output_dir}/database_schema.md")
        
        if "json" in formats:
            json_schema = self.schema_generator.generate_json_schema(schema_data)
            os.makedirs(output_dir, exist_ok=True)
            with open(f"{output_dir}/database_schema.json", "w") as f:
                f.write(json_schema)
            print(f"✓ Updated {output_dir}/database_schema.json")
        
        # Save raw schema data for migration generation
        with open(f"{output_dir}/schema_raw_data.json", "w") as f:
            json.dump(schema_data, f, indent=2, default=str)
        print(f"✓ Updated {output_dir}/schema_raw_data.json")
    
    def generate_code(self):
        """Generate code from schema"""
        if not self.config["code_generation"]["enabled"]:
            return
        
        print("Generating code from database schema...")
        
        output_dir = self.config["code_generation"]["output_dir"]
        os.makedirs(output_dir, exist_ok=True)
        
        schema_data = self.schema_generator.extract_schema_information()
        
        if self.config["code_generation"]["generate_models"]:
            models_code = self.code_generator.generate_sqlalchemy_models(schema_data)
            with open(f"{output_dir}/models.py", "w") as f:
                f.write(models_code)
            print(f"✓ Generated {output_dir}/models.py")
        
        if self.config["code_generation"]["generate_schemas"]:
            schemas_code = self.code_generator.generate_pydantic_schemas(schema_data)
            with open(f"{output_dir}/schemas.py", "w") as f:
                f.write(schemas_code)
            print(f"✓ Generated {output_dir}/schemas.py")
        
        if self.config["code_generation"]["generate_crud"]:
            crud_code = self.code_generator.generate_crud_operations(schema_data)
            with open(f"{output_dir}/crud.py", "w") as f:
                f.write(crud_code)
            print(f"✓ Generated {output_dir}/crud.py")
        
        if self.config["code_generation"]["generate_routes"]:
            routes_code = self.code_generator.generate_api_routes(schema_data)
            with open(f"{output_dir}/routes.py", "w") as f:
                f.write(routes_code)
            print(f"✓ Generated {output_dir}/routes.py")
        
        if self.config["code_generation"]["generate_migrations"]:
            # Check if we have previous schema data for migration generation
            prev_schema_file = f"{self.config['documentation']['output_dir']}/schema_raw_data_previous.json"
            if os.path.exists(prev_schema_file):
                with open(prev_schema_file, 'r') as f:
                    old_schema = json.load(f)
                
                migration_code = self.code_generator.generate_migration_script(old_schema, schema_data)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                migration_file = f"{output_dir}/migration_{timestamp}.py"
                with open(migration_file, "w") as f:
                    f.write(migration_code)
                print(f"✓ Generated {migration_file}")
        
        # Save current schema as previous for next migration
        prev_schema_file = f"{self.config['documentation']['output_dir']}/schema_raw_data_previous.json"
        with open(prev_schema_file, "w") as f:
            json.dump(schema_data, f, indent=2, default=str)
    
    def git_commit_changes(self):
        """Commit changes to git if enabled"""
        if not self.config["git_integration"]["enabled"] or not self.config["git_integration"]["auto_commit"]:
            return
        
        try:
            import subprocess
            
            # Add all generated files
            subprocess.run(["git", "add", "docs/", "generated/"], check=True)
            
            # Create commit message
            commit_message = self.config["git_integration"]["commit_message_template"].format(
                date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            
            # Commit changes
            result = subprocess.run(["git", "commit", "-m", commit_message], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✓ Committed changes to git: {commit_message}")
            else:
                print(f"Git commit failed: {result.stderr}")
                
        except subprocess.CalledProcessError as e:
            print(f"Git operation failed: {e}")
        except ImportError:
            print("Git integration requires subprocess module")
    
    def run_full_update(self, force: bool = False):
        """Run complete schema update process"""
        print(f"Database Schema Automation - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        if force or self.detect_schema_changes():
            # Update documentation
            self.update_documentation()
            
            # Generate code
            self.generate_code()

            # Save current schema hash
            current_hash = self.get_schema_hash()
            self.save_current_hash(current_hash)
            
            # Commit to git if enabled
            self.git_commit_changes()
            
            print("\n✅ Schema automation completed successfully!")
            
            if self.config["monitoring"]["notify_on_changes"]:
                self.send_notification("Database schema changes detected and processed")
        else:
            print("No schema changes detected.")
    
    def send_notification(self, message: str):
        """Send notification about schema changes"""
        print(f"📧 Notification: {message}")
        # Here you could integrate with Slack, email, Discord, etc.
    
    def monitor_continuous(self):
        """Continuously monitor for schema changes"""
        import time
        
        interval = self.config["monitoring"]["check_interval_minutes"] * 60
        print(f"Starting continuous monitoring (checking every {self.config['monitoring']['check_interval_minutes']} minutes)...")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                self.run_full_update()
                print(f"Next check in {self.config['monitoring']['check_interval_minutes']} minutes...\n")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")


def main():
    """Command-line interface for schema automation"""
    parser = argparse.ArgumentParser(description="Database Schema Automation System")
    parser.add_argument("--check", action="store_true", 
                       help="Check for schema changes and update if needed")
    parser.add_argument("--force", action="store_true", 
                       help="Force update documentation and code regardless of changes")
    parser.add_argument("--monitor", action="store_true", 
                       help="Continuously monitor for schema changes")
    parser.add_argument("--config", default="tools/schema_config.json",
                       help="Path to configuration file")
    
    args = parser.parse_args()
    
    automation = SchemaAutomation(args.config)
    
    if args.monitor:
        automation.monitor_continuous()
    elif args.check:
        # Return exit code 0 if no changes, 1 if changes detected
        has_changes = automation.detect_schema_changes()
        if has_changes:
            print("Schema changes detected")
            exit(1)
        else:
            print("No schema changes detected")
            exit(0)
    elif args.force:
        automation.run_full_update(force=True)
    else:
        # Default: check for changes and update if needed
        automation.run_full_update()


if __name__ == "__main__":
    main()