#!/usr/bin/env python3
"""
API Documentation Generator

This script generates comprehensive API documentation from Flask application
routes and docstrings. Creates both individual endpoint documentation and
an OpenAPI/Swagger specification.
"""

import os
import sys
import json
import yaml
import inspect
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import importlib.util


class APIDocumentationGenerator:
    def __init__(self, app_module_path: str = "main.py"):
        """Initialize the API documentation generator."""
        self.app_module_path = app_module_path
        self.output_dir = Path("docs/api/endpoints")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.api_spec = {
            "openapi": "3.0.3",
            "info": {
                "title": "Automated Job Application System API",
                "version": "1.0.0",
                "description": "REST API for the Automated Job Application System",
                "contact": {
                    "name": "Development Team",
                    "url": "https://github.com/your-repo"
                }
            },
            "servers": [
                {"url": "https://your-app.replit.app/api/v1", "description": "Production"},
                {"url": "https://staging-app.replit.app/api/v1", "description": "Staging"}
            ],
            "paths": {},
            "components": {
                "securitySchemes": {
                    "ApiKeyAuth": {
                        "type": "apiKey",
                        "in": "header",
                        "name": "X-API-Key"
                    }
                },
                "schemas": {}
            },
            "security": [{"ApiKeyAuth": []}]
        }

    def load_flask_app(self):
        """Load the Flask application to inspect routes."""
        try:
            # Add current directory to path
            sys.path.insert(0, os.getcwd())
            
            # Import the main module
            spec = importlib.util.spec_from_file_location("main", self.app_module_path)
            if spec is None or spec.loader is None:
                print(f"Could not create spec for {self.app_module_path}")
                return None
            main_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(main_module)
            
            # Try to get the Flask app instance
            if hasattr(main_module, 'app'):
                return main_module.app
            else:
                print("No 'app' attribute found in main module")
                return None
                
        except Exception as e:
            print(f"Error loading Flask app: {e}")
            return None

    def extract_route_info(self, app) -> List[Dict]:
        """Extract information about all routes from the Flask app."""
        routes = []
        
        for rule in app.url_map.iter_rules():
            if rule.endpoint == 'static':
                continue
                
            route_info = {
                'endpoint': rule.endpoint,
                'url': str(rule.rule),
                'methods': list(rule.methods - {'HEAD', 'OPTIONS'}),
                'function': app.view_functions.get(rule.endpoint),
                'docstring': None,
                'module': None
            }
            
            # Get function information
            if route_info['function']:
                route_info['docstring'] = inspect.getdoc(route_info['function'])
                module = inspect.getmodule(route_info['function'])
                route_info['module'] = module.__name__ if module else 'unknown'
            
            routes.append(route_info)
            
        return routes

    def parse_docstring(self, docstring: str) -> Dict[str, Any]:
        """Parse structured information from function docstrings."""
        if not docstring:
            return {}
            
        lines = docstring.strip().split('\n')
        parsed = {
            'summary': '',
            'description': '',
            'parameters': [],
            'responses': {},
            'examples': []
        }
        
        current_section = 'description'
        current_content = []
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('Parameters:'):
                if current_content:
                    parsed[current_section] = '\n'.join(current_content).strip()
                    current_content = []
                current_section = 'parameters'
            elif line.startswith('Returns:'):
                if current_content:
                    parsed[current_section] = '\n'.join(current_content).strip()
                    current_content = []
                current_section = 'returns'
            elif line.startswith('Example:'):
                if current_content:
                    parsed[current_section] = '\n'.join(current_content).strip()
                    current_content = []
                current_section = 'examples'
            else:
                current_content.append(line)
        
        # Handle the last section
        if current_content:
            parsed[current_section] = '\n'.join(current_content).strip()
        
        # Extract summary from first line of description
        if parsed['description']:
            desc_lines = parsed['description'].split('\n')
            parsed['summary'] = desc_lines[0]
            if len(desc_lines) > 1:
                parsed['description'] = '\n'.join(desc_lines[1:]).strip()
        
        return parsed

    def generate_endpoint_docs(self, routes: List[Dict]):
        """Generate individual endpoint documentation files."""
        # Group routes by module/category
        route_groups = {}
        for route in routes:
            module = route['module'] or 'unknown'
            if module not in route_groups:
                route_groups[module] = []
            route_groups[module].append(route)
        
        for module, module_routes in route_groups.items():
            filename = f"{module.replace('.', '_')}_endpoints.md"
            filepath = self.output_dir / filename
            
            with open(filepath, 'w') as f:
                f.write(f"# {module.title()} API Endpoints\n\n")
                f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                for route in module_routes:
                    self.write_endpoint_doc(f, route)
                    
        print(f"Generated endpoint documentation in {self.output_dir}")

    def write_endpoint_doc(self, f, route: Dict):
        """Write documentation for a single endpoint."""
        parsed_doc = self.parse_docstring(route['docstring'])
        
        # Endpoint title
        f.write(f"## {route['endpoint']}\n\n")
        
        # Basic info
        for method in route['methods']:
            f.write(f"**{method}** `{route['url']}`\n\n")
        
        # Summary and description
        if parsed_doc.get('summary'):
            f.write(f"**Summary:** {parsed_doc['summary']}\n\n")
            
        if parsed_doc.get('description'):
            f.write(f"{parsed_doc['description']}\n\n")
        
        # Parameters
        if parsed_doc.get('parameters'):
            f.write("### Parameters\n\n")
            f.write(f"{parsed_doc['parameters']}\n\n")
        
        # Examples
        if parsed_doc.get('examples'):
            f.write("### Examples\n\n")
            f.write("```bash\n")
            f.write(f"{parsed_doc['examples']}\n")
            f.write("```\n\n")
        
        # Response
        if parsed_doc.get('returns'):
            f.write("### Response\n\n")
            f.write(f"{parsed_doc['returns']}\n\n")
        
        f.write("---\n\n")

    def generate_openapi_spec(self, routes: List[Dict]):
        """Generate OpenAPI/Swagger specification."""
        for route in routes:
            path = route['url']
            
            # Convert Flask route parameters to OpenAPI format
            path = path.replace('<', '{').replace('>', '}')
            
            if path not in self.api_spec['paths']:
                self.api_spec['paths'][path] = {}
            
            for method in route['methods']:
                method_lower = method.lower()
                parsed_doc = self.parse_docstring(route['docstring'])
                
                operation = {
                    "summary": parsed_doc.get('summary', route['endpoint']),
                    "description": parsed_doc.get('description', ''),
                    "operationId": route['endpoint'],
                    "tags": [self.get_tag_from_endpoint(route['endpoint'])],
                    "security": [{"ApiKeyAuth": []}],
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"}
                                }
                            }
                        },
                        "400": {"description": "Bad request"},
                        "401": {"description": "Unauthorized"},
                        "404": {"description": "Not found"},
                        "500": {"description": "Internal server error"}
                    }
                }
                
                # Add parameters if URL has path parameters
                if '{' in path:
                    operation['parameters'] = self.extract_path_parameters(path)
                
                self.api_spec['paths'][path][method_lower] = operation

    def get_tag_from_endpoint(self, endpoint: str) -> str:
        """Extract a tag name from endpoint."""
        if '.' in endpoint:
            return endpoint.split('.')[0]
        return 'general'

    def extract_path_parameters(self, path: str) -> List[Dict]:
        """Extract path parameters from URL."""
        import re
        parameters = []
        
        for match in re.finditer(r'{([^}]+)}', path):
            param_name = match.group(1)
            parameters.append({
                "name": param_name,
                "in": "path",
                "required": True,
                "schema": {"type": "string"},
                "description": f"The {param_name} identifier"
            })
            
        return parameters

    def save_openapi_spec(self, filename: str = "docs/api/openapi.yaml"):
        """Save the OpenAPI specification to a file."""
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filename, 'w') as f:
            yaml.dump(self.api_spec, f, default_flow_style=False, sort_keys=False)
            
        print(f"OpenAPI specification saved to {filename}")

    def generate_api_index(self, routes: List[Dict]):
        """Generate an API index file."""
        index_path = Path("docs/api/api_index.md")
        
        with open(index_path, 'w') as f:
            f.write("# API Endpoint Index\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Group by tags
            tagged_routes = {}
            for route in routes:
                tag = self.get_tag_from_endpoint(route['endpoint'])
                if tag not in tagged_routes:
                    tagged_routes[tag] = []
                tagged_routes[tag].append(route)
            
            for tag, tag_routes in sorted(tagged_routes.items()):
                f.write(f"## {tag.title()}\n\n")
                
                for route in sorted(tag_routes, key=lambda r: r['endpoint']):
                    methods = ', '.join(route['methods'])
                    f.write(f"- **{route['endpoint']}** `{methods} {route['url']}`\n")
                    
                    if route['docstring']:
                        summary = route['docstring'].split('\n')[0]
                        f.write(f"  {summary}\n")
                    f.write("\n")
        
        print(f"API index generated at {index_path}")

    def run(self):
        """Run the complete API documentation generation process."""
        print("Starting API documentation generation...")
        
        # Load Flask app
        app = self.load_flask_app()
        if not app:
            print("Failed to load Flask application")
            return
        
        # Extract route information
        routes = self.extract_route_info(app)
        print(f"Found {len(routes)} routes")
        
        # Generate documentation
        self.generate_endpoint_docs(routes)
        self.generate_openapi_spec(routes)
        self.save_openapi_spec()
        self.generate_api_index(routes)
        
        print("API documentation generation complete!")


def main():
    """Main entry point."""
    generator = APIDocumentationGenerator()
    generator.run()


if __name__ == "__main__":
    main()