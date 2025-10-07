import os
import logging
import uuid
from datetime import datetime, timedelta

# Dynamic import of python-docx - only install when needed
try:
    # Import python-docx directly since it should be available
    from docx import Document

    logging.info("python-docx loaded successfully for document generation")
except ImportError as e:
    logging.warning(f"python-docx not available: {e}")

    # Create dummy classes for non-document workflows
    class Document:
        def __init__(self, *args, **kwargs):
            raise ImportError("python-docx not available - document generation disabled")


from modules.storage import ReplitStorageCompatibilityClient as Client
from .template_engine import TemplateEngine


class DocumentGenerator:
    """
    Handles Word document generation using template-based system

    This class integrates with the template library system to generate professional
    documents by loading template files and replacing variable placeholders with
    actual data from JSON input. Maintains all original formatting while enabling
    dynamic content generation.

    Key Features:
    - Template-based document generation preserving formatting
    - JSON input processing for dynamic content
    - Professional document metadata and properties
    - Cloud storage integration with local fallback
    - Support for multiple document types (resume, cover letter, etc.)
    """

    def __init__(self):
        """
        Initialize the document generator with template engine and storage

        Sets up:
        - Template engine for processing template files
        - Storage directories for generated documents
        - Cloud storage client for document persistence
        - Logging configuration for debugging
        """
        self.storage_dir = os.path.join(os.getcwd(), "storage")
        self.template_engine = TemplateEngine()

        # Initialize storage client (local filesystem by default)
        try:
            self.storage_client = Client()
            logging.info("Connected to storage backend (local filesystem)")
        except Exception as e:
            logging.error(f"Failed to initialize storage: {str(e)}")
            self.storage_client = None

        # Initialize CSV content mapper for dynamic content mapping
        from modules.content.document_generation.csv_content_mapper import CSVContentMapper

        self.csv_mapper = CSVContentMapper()

    def generate_document_with_csv_mapping(
        self, data, document_type="resume", template_name=None, csv_mapping_path=None
    ):
        """
        Generate a Word document using CSV-mapped template system

        This method uses CSV content mapping to dynamically transform templates
        with variable substitution, static text changes, and content removal
        based on the CSV mapping specifications.

        Args:
            data (dict): JSON data containing document information and variables
            document_type (str): Type of document ('resume', 'coverletter', etc.)
            template_name (str): Optional specific template name to use
            csv_mapping_path (str): Path to CSV mapping file

        Returns:
            dict: File information including path, filename, size, and generation stats
        """
        try:
            # Load CSV mapping if provided
            if csv_mapping_path and os.path.exists(csv_mapping_path):
                mapping = self.csv_mapper.load_mapping_from_csv(csv_mapping_path)

                # Resolve variables from content data
                resolved_variables = self.csv_mapper.resolve_variables_from_content(mapping, data)

                # Apply CSV mapping to template
                template_path = self.get_template_path(document_type, template_name)
                mapped_template_path = self.csv_mapper.apply_mapping_to_template(template_path, mapping, data)

                # Use the mapped template with resolved variables
                template_data = {**data, **resolved_variables}

                # Generate document using mapped template
                result = self.template_engine.generate_document(template_path=mapped_template_path, data=template_data)

                logging.info(f"Generated document using CSV mapping: {len(resolved_variables)} variables resolved")

            else:
                # Fallback to standard generation
                result = self.generate_document(data, document_type, template_name)

            return result

        except Exception as e:
            logging.error(f"CSV-mapped document generation failed: {e}")
            # Fallback to standard generation
            return self.generate_document(data, document_type, template_name)

    def generate_document(self, data, document_type="resume", template_name=None):
        """
        Generate a Word document using template-based system

        This method processes JSON data through the template engine to create
        professional documents with proper formatting and metadata.

        Args:
            data (dict): JSON data containing document information and variables
            document_type (str): Type of document ('resume', 'coverletter', etc.)
            template_name (str): Optional specific template name to use

        Returns:
            dict: File information including path, filename, size, and generation stats
        """
        try:
            # Determine template path based on document type and template name
            template_path = self.get_template_path(document_type, template_name)

            # Prepare document metadata from data
            document_metadata = self.prepare_document_metadata(data, document_type)

            # Merge user data with document metadata for template processing
            template_data = {**data, **document_metadata}

            # Generate document using template engine
            result = self.template_engine.generate_document(template_path=template_path, data=template_data)

            # Get the generated document path
            generated_path = result["output_path"]

            # Upload to object storage if available
            file_info = self.upload_to_storage(generated_path)

            # Update result with storage information
            result.update(
                {
                    "file_path": file_info.get("file_path", generated_path),
                    "filename": file_info.get("filename", os.path.basename(generated_path)),
                    "storage_type": file_info.get("storage_type", "local"),
                    "template_used": template_path,
                    "document_type": document_type,
                    "generation_method": "template_based",
                }
            )

            return result

        except Exception as e:
            logging.error(f"Error generating document: {str(e)}")
            raise

    def get_template_path(self, document_type, template_name=None):
        """
        Determine the template path based on document type and optional template name

        Args:
            document_type (str): Type of document ('resume', 'coverletter', etc.)
            template_name (str): Optional specific template name

        Returns:
            str: Path to the template file
        """
        template_dir = os.path.join("content_template_library", f"{document_type}s")

        if template_name:
            # Use specific template if provided
            template_path = os.path.join(template_dir, template_name)
            if not template_name.endswith(".docx"):
                template_path += ".docx"
        else:
            # Use default template for document type
            if document_type == "resume":
                # Use existing template file
                template_path = "content_template_library/jinja_templates/resume/Accessible-MCS-Resume-Template-Bullet-Points_1751349781656_jinja_template_20250718_021104.docx"
            elif document_type == "coverletter":
                template_path = os.path.join(template_dir, "default_coverletter_template.docx")
            else:
                raise ValueError(f"Unknown document type: {document_type}")

        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template not found: {template_path}")

        return template_path

    def prepare_document_metadata(self, data, document_type):
        """
        Prepare document metadata for professional document properties

        Args:
            data (dict): User data containing personal information
            document_type (str): Type of document being generated

        Returns:
            dict: Metadata dictionary for document properties
        """
        # Extract names for author field
        first_name = data.get("first_name", data.get("personal", {}).get("first_name", ""))
        last_name = data.get("last_name", data.get("personal", {}).get("last_name", ""))
        full_name = f"{first_name} {last_name}".strip()

        # Determine document title
        if document_type == "resume":
            title = f"{full_name} Resume" if full_name else "Professional Resume"
            subject = "Professional Resume"
            keywords = "Resume, Professional, Job Application, Career"
        elif document_type == "coverletter":
            title = f"{full_name} Cover Letter" if full_name else "Professional Cover Letter"
            subject = "Professional Cover Letter"
            keywords = "Cover Letter, Professional, Job Application, Career"
        else:
            title = f"{full_name} Professional Document" if full_name else "Professional Document"
            subject = "Professional Document"
            keywords = "Professional, Document, Career"

        return {
            "title": title,
            "author": full_name or "Steve Glen",
            "subject": subject,
            "keywords": keywords,
            "comments": f"Generated on {datetime.now().strftime('%Y-%m-%d')} for professional use",
            "category": "Job Application",
            "language": "en-CA",
            "version": "1.0",
            "revision": 1,
        }

    def upload_to_storage(self, file_path):
        """
        Upload generated document to object storage with local fallback

        Args:
            file_path (str): Path to the generated document

        Returns:
            dict: Storage information including path, filename, and storage type
        """
        filename = os.path.basename(file_path)

        if self.storage_client:
            try:
                # Upload to Replit Object Storage
                with open(file_path, "rb") as file:
                    file_content = file.read()

                # Use documents/ prefix for organization
                object_key = f"documents/{filename}"

                # Upload to storage
                self.storage_client.upload(object_key, file_content)

                logging.info(f"Document uploaded to object storage: {object_key}")

                return {
                    "file_path": object_key,
                    "filename": filename,
                    "storage_type": "cloud",
                    "local_path": file_path,
                    "file_size": len(file_content),
                }

            except Exception as e:
                logging.error(f"Failed to upload to object storage: {str(e)}")
                # Fall back to local storage
                pass

        # Local storage fallback
        return {
            "file_path": file_path,
            "filename": filename,
            "storage_type": "local",
            "file_size": os.path.getsize(file_path),
        }

    def cleanup_old_files(self, max_age_hours=24):
        """
        Clean up old generated files

        Args:
            max_age_hours (int): Maximum age of files to keep in hours
        """
        try:
            if os.path.exists(self.storage_dir):
                current_time = datetime.now()
                for filename in os.listdir(self.storage_dir):
                    file_path = os.path.join(self.storage_dir, filename)
                    if os.path.isfile(file_path):
                        file_age = current_time - datetime.fromtimestamp(os.path.getctime(file_path))
                        if file_age.total_seconds() > max_age_hours * 3600:
                            os.remove(file_path)
                            logging.info(f"Cleaned up old file: {filename}")
        except Exception as e:
            logging.error(f"Error during cleanup: {str(e)}")
