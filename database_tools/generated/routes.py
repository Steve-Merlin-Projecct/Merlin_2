"""
Auto-generated API Routes
Generated from database schema on 2025-09-12 13:08:25
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

# AnalyzedJobs Routes
analyzed_jobs_bp = Blueprint('analyzed_jobs', __name__, url_prefix='/api/analyzed-jobs')

@analyzed_jobs_bp.route('/', methods=['GET'])
def get_analyzed_jobs_list():
    """
    Get all analyzed_jobs records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = AnalyzedJobsCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analyzed_jobs_bp.route('/<uuid:id>', methods=['GET'])
def get_analyzed_jobs_by_id(id):
    """
    Get analyzed_jobs by ID
    """
    try:
        with get_db_session() as db:
            record = AnalyzedJobsCRUD.get_by_id(db, id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analyzed_jobs_bp.route('/', methods=['POST'])
def create_analyzed_jobs():
    """
    Create new analyzed_jobs record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = AnalyzedJobsCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analyzed_jobs_bp.route('/<uuid:id>', methods=['PUT'])
def update_analyzed_jobs(id):
    """
    Update analyzed_jobs record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = AnalyzedJobsCRUD.update(db, id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analyzed_jobs_bp.route('/<uuid:id>', methods=['DELETE'])
def delete_analyzed_jobs(id):
    """
    Delete analyzed_jobs record
    """
    try:
        with get_db_session() as db:
            success = AnalyzedJobsCRUD.delete(db, id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ApplicationDocuments Routes
application_documents_bp = Blueprint('application_documents', __name__, url_prefix='/api/application-documents')

@application_documents_bp.route('/', methods=['GET'])
def get_application_documents_list():
    """
    Get all application_documents records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = ApplicationDocumentsCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@application_documents_bp.route('/<uuid:document_id>', methods=['GET'])
def get_application_documents_by_id(document_id):
    """
    Get application_documents by ID
    """
    try:
        with get_db_session() as db:
            record = ApplicationDocumentsCRUD.get_by_id(db, document_id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@application_documents_bp.route('/', methods=['POST'])
def create_application_documents():
    """
    Create new application_documents record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = ApplicationDocumentsCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@application_documents_bp.route('/<uuid:document_id>', methods=['PUT'])
def update_application_documents(document_id):
    """
    Update application_documents record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = ApplicationDocumentsCRUD.update(db, document_id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@application_documents_bp.route('/<uuid:document_id>', methods=['DELETE'])
def delete_application_documents(document_id):
    """
    Delete application_documents record
    """
    try:
        with get_db_session() as db:
            success = ApplicationDocumentsCRUD.delete(db, document_id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ApplicationSettings Routes
application_settings_bp = Blueprint('application_settings', __name__, url_prefix='/api/application-settings')

@application_settings_bp.route('/', methods=['GET'])
def get_application_settings_list():
    """
    Get all application_settings records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = ApplicationSettingsCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@application_settings_bp.route('/<uuid:setting_key>', methods=['GET'])
def get_application_settings_by_id(setting_key):
    """
    Get application_settings by ID
    """
    try:
        with get_db_session() as db:
            record = ApplicationSettingsCRUD.get_by_id(db, setting_key)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@application_settings_bp.route('/', methods=['POST'])
def create_application_settings():
    """
    Create new application_settings record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = ApplicationSettingsCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@application_settings_bp.route('/<uuid:setting_key>', methods=['PUT'])
def update_application_settings(setting_key):
    """
    Update application_settings record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = ApplicationSettingsCRUD.update(db, setting_key, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@application_settings_bp.route('/<uuid:setting_key>', methods=['DELETE'])
def delete_application_settings(setting_key):
    """
    Delete application_settings record
    """
    try:
        with get_db_session() as db:
            success = ApplicationSettingsCRUD.delete(db, setting_key)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# CanadianSpellings Routes
canadian_spellings_bp = Blueprint('canadian_spellings', __name__, url_prefix='/api/canadian-spellings')

@canadian_spellings_bp.route('/', methods=['GET'])
def get_canadian_spellings_list():
    """
    Get all canadian_spellings records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = CanadianSpellingsCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@canadian_spellings_bp.route('/<uuid:id>', methods=['GET'])
def get_canadian_spellings_by_id(id):
    """
    Get canadian_spellings by ID
    """
    try:
        with get_db_session() as db:
            record = CanadianSpellingsCRUD.get_by_id(db, id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@canadian_spellings_bp.route('/', methods=['POST'])
def create_canadian_spellings():
    """
    Create new canadian_spellings record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = CanadianSpellingsCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@canadian_spellings_bp.route('/<uuid:id>', methods=['PUT'])
def update_canadian_spellings(id):
    """
    Update canadian_spellings record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = CanadianSpellingsCRUD.update(db, id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@canadian_spellings_bp.route('/<uuid:id>', methods=['DELETE'])
def delete_canadian_spellings(id):
    """
    Delete canadian_spellings record
    """
    try:
        with get_db_session() as db:
            success = CanadianSpellingsCRUD.delete(db, id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# CleanedJobScrapeSources Routes
cleaned_job_scrape_sources_bp = Blueprint('cleaned_job_scrape_sources', __name__, url_prefix='/api/cleaned-job-scrape-sources')

@cleaned_job_scrape_sources_bp.route('/', methods=['GET'])
def get_cleaned_job_scrape_sources_list():
    """
    Get all cleaned_job_scrape_sources records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = CleanedJobScrapeSourcesCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cleaned_job_scrape_sources_bp.route('/<uuid:source_id>', methods=['GET'])
def get_cleaned_job_scrape_sources_by_id(source_id):
    """
    Get cleaned_job_scrape_sources by ID
    """
    try:
        with get_db_session() as db:
            record = CleanedJobScrapeSourcesCRUD.get_by_id(db, source_id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cleaned_job_scrape_sources_bp.route('/', methods=['POST'])
def create_cleaned_job_scrape_sources():
    """
    Create new cleaned_job_scrape_sources record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = CleanedJobScrapeSourcesCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cleaned_job_scrape_sources_bp.route('/<uuid:source_id>', methods=['PUT'])
def update_cleaned_job_scrape_sources(source_id):
    """
    Update cleaned_job_scrape_sources record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = CleanedJobScrapeSourcesCRUD.update(db, source_id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cleaned_job_scrape_sources_bp.route('/<uuid:source_id>', methods=['DELETE'])
def delete_cleaned_job_scrape_sources(source_id):
    """
    Delete cleaned_job_scrape_sources record
    """
    try:
        with get_db_session() as db:
            success = CleanedJobScrapeSourcesCRUD.delete(db, source_id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# CleanedJobScrapes Routes
cleaned_job_scrapes_bp = Blueprint('cleaned_job_scrapes', __name__, url_prefix='/api/cleaned-job-scrapes')

@cleaned_job_scrapes_bp.route('/', methods=['GET'])
def get_cleaned_job_scrapes_list():
    """
    Get all cleaned_job_scrapes records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = CleanedJobScrapesCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cleaned_job_scrapes_bp.route('/<uuid:cleaned_job_id>', methods=['GET'])
def get_cleaned_job_scrapes_by_id(cleaned_job_id):
    """
    Get cleaned_job_scrapes by ID
    """
    try:
        with get_db_session() as db:
            record = CleanedJobScrapesCRUD.get_by_id(db, cleaned_job_id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cleaned_job_scrapes_bp.route('/', methods=['POST'])
def create_cleaned_job_scrapes():
    """
    Create new cleaned_job_scrapes record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = CleanedJobScrapesCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cleaned_job_scrapes_bp.route('/<uuid:cleaned_job_id>', methods=['PUT'])
def update_cleaned_job_scrapes(cleaned_job_id):
    """
    Update cleaned_job_scrapes record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = CleanedJobScrapesCRUD.update(db, cleaned_job_id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cleaned_job_scrapes_bp.route('/<uuid:cleaned_job_id>', methods=['DELETE'])
def delete_cleaned_job_scrapes(cleaned_job_id):
    """
    Delete cleaned_job_scrapes record
    """
    try:
        with get_db_session() as db:
            success = CleanedJobScrapesCRUD.delete(db, cleaned_job_id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Companies Routes
companies_bp = Blueprint('companies', __name__, url_prefix='/api/companies')

@companies_bp.route('/', methods=['GET'])
def get_companies_list():
    """
    Get all companies records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = CompaniesCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@companies_bp.route('/<uuid:id>', methods=['GET'])
def get_companies_by_id(id):
    """
    Get companies by ID
    """
    try:
        with get_db_session() as db:
            record = CompaniesCRUD.get_by_id(db, id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@companies_bp.route('/', methods=['POST'])
def create_companies():
    """
    Create new companies record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = CompaniesCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@companies_bp.route('/<uuid:id>', methods=['PUT'])
def update_companies(id):
    """
    Update companies record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = CompaniesCRUD.update(db, id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@companies_bp.route('/<uuid:id>', methods=['DELETE'])
def delete_companies(id):
    """
    Delete companies record
    """
    try:
        with get_db_session() as db:
            success = CompaniesCRUD.delete(db, id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ConsistencyValidationLogs Routes
consistency_validation_logs_bp = Blueprint('consistency_validation_logs', __name__, url_prefix='/api/consistency-validation-logs')

@consistency_validation_logs_bp.route('/', methods=['GET'])
def get_consistency_validation_logs_list():
    """
    Get all consistency_validation_logs records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = ConsistencyValidationLogsCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@consistency_validation_logs_bp.route('/<uuid:id>', methods=['GET'])
def get_consistency_validation_logs_by_id(id):
    """
    Get consistency_validation_logs by ID
    """
    try:
        with get_db_session() as db:
            record = ConsistencyValidationLogsCRUD.get_by_id(db, id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@consistency_validation_logs_bp.route('/', methods=['POST'])
def create_consistency_validation_logs():
    """
    Create new consistency_validation_logs record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = ConsistencyValidationLogsCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@consistency_validation_logs_bp.route('/<uuid:id>', methods=['PUT'])
def update_consistency_validation_logs(id):
    """
    Update consistency_validation_logs record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = ConsistencyValidationLogsCRUD.update(db, id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@consistency_validation_logs_bp.route('/<uuid:id>', methods=['DELETE'])
def delete_consistency_validation_logs(id):
    """
    Delete consistency_validation_logs record
    """
    try:
        with get_db_session() as db:
            success = ConsistencyValidationLogsCRUD.delete(db, id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# DataCorrections Routes
data_corrections_bp = Blueprint('data_corrections', __name__, url_prefix='/api/data-corrections')

@data_corrections_bp.route('/', methods=['GET'])
def get_data_corrections_list():
    """
    Get all data_corrections records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = DataCorrectionsCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@data_corrections_bp.route('/<uuid:id>', methods=['GET'])
def get_data_corrections_by_id(id):
    """
    Get data_corrections by ID
    """
    try:
        with get_db_session() as db:
            record = DataCorrectionsCRUD.get_by_id(db, id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@data_corrections_bp.route('/', methods=['POST'])
def create_data_corrections():
    """
    Create new data_corrections record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = DataCorrectionsCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@data_corrections_bp.route('/<uuid:id>', methods=['PUT'])
def update_data_corrections(id):
    """
    Update data_corrections record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = DataCorrectionsCRUD.update(db, id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@data_corrections_bp.route('/<uuid:id>', methods=['DELETE'])
def delete_data_corrections(id):
    """
    Delete data_corrections record
    """
    try:
        with get_db_session() as db:
            success = DataCorrectionsCRUD.delete(db, id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# DocumentJobs Routes
document_jobs_bp = Blueprint('document_jobs', __name__, url_prefix='/api/document-jobs')

@document_jobs_bp.route('/', methods=['GET'])
def get_document_jobs_list():
    """
    Get all document_jobs records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = DocumentJobsCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@document_jobs_bp.route('/<uuid:job_id>', methods=['GET'])
def get_document_jobs_by_id(job_id):
    """
    Get document_jobs by ID
    """
    try:
        with get_db_session() as db:
            record = DocumentJobsCRUD.get_by_id(db, job_id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@document_jobs_bp.route('/', methods=['POST'])
def create_document_jobs():
    """
    Create new document_jobs record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = DocumentJobsCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@document_jobs_bp.route('/<uuid:job_id>', methods=['PUT'])
def update_document_jobs(job_id):
    """
    Update document_jobs record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = DocumentJobsCRUD.update(db, job_id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@document_jobs_bp.route('/<uuid:job_id>', methods=['DELETE'])
def delete_document_jobs(job_id):
    """
    Delete document_jobs record
    """
    try:
        with get_db_session() as db:
            success = DocumentJobsCRUD.delete(db, job_id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# DocumentSentences Routes
document_sentences_bp = Blueprint('document_sentences', __name__, url_prefix='/api/document-sentences')

@document_sentences_bp.route('/', methods=['GET'])
def get_document_sentences_list():
    """
    Get all document_sentences records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = DocumentSentencesCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@document_sentences_bp.route('/<uuid:sentence_id>', methods=['GET'])
def get_document_sentences_by_id(sentence_id):
    """
    Get document_sentences by ID
    """
    try:
        with get_db_session() as db:
            record = DocumentSentencesCRUD.get_by_id(db, sentence_id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@document_sentences_bp.route('/', methods=['POST'])
def create_document_sentences():
    """
    Create new document_sentences record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = DocumentSentencesCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@document_sentences_bp.route('/<uuid:sentence_id>', methods=['PUT'])
def update_document_sentences(sentence_id):
    """
    Update document_sentences record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = DocumentSentencesCRUD.update(db, sentence_id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@document_sentences_bp.route('/<uuid:sentence_id>', methods=['DELETE'])
def delete_document_sentences(sentence_id):
    """
    Delete document_sentences record
    """
    try:
        with get_db_session() as db:
            success = DocumentSentencesCRUD.delete(db, sentence_id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# DocumentTemplateMetadata Routes
document_template_metadata_bp = Blueprint('document_template_metadata', __name__, url_prefix='/api/document-template-metadata')

@document_template_metadata_bp.route('/', methods=['GET'])
def get_document_template_metadata_list():
    """
    Get all document_template_metadata records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = DocumentTemplateMetadataCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@document_template_metadata_bp.route('/<uuid:id>', methods=['GET'])
def get_document_template_metadata_by_id(id):
    """
    Get document_template_metadata by ID
    """
    try:
        with get_db_session() as db:
            record = DocumentTemplateMetadataCRUD.get_by_id(db, id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@document_template_metadata_bp.route('/', methods=['POST'])
def create_document_template_metadata():
    """
    Create new document_template_metadata record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = DocumentTemplateMetadataCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@document_template_metadata_bp.route('/<uuid:id>', methods=['PUT'])
def update_document_template_metadata(id):
    """
    Update document_template_metadata record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = DocumentTemplateMetadataCRUD.update(db, id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@document_template_metadata_bp.route('/<uuid:id>', methods=['DELETE'])
def delete_document_template_metadata(id):
    """
    Delete document_template_metadata record
    """
    try:
        with get_db_session() as db:
            success = DocumentTemplateMetadataCRUD.delete(db, id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# DocumentToneAnalysis Routes
document_tone_analysis_bp = Blueprint('document_tone_analysis', __name__, url_prefix='/api/document-tone-analysis')

@document_tone_analysis_bp.route('/', methods=['GET'])
def get_document_tone_analysis_list():
    """
    Get all document_tone_analysis records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = DocumentToneAnalysisCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@document_tone_analysis_bp.route('/<uuid:id>', methods=['GET'])
def get_document_tone_analysis_by_id(id):
    """
    Get document_tone_analysis by ID
    """
    try:
        with get_db_session() as db:
            record = DocumentToneAnalysisCRUD.get_by_id(db, id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@document_tone_analysis_bp.route('/', methods=['POST'])
def create_document_tone_analysis():
    """
    Create new document_tone_analysis record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = DocumentToneAnalysisCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@document_tone_analysis_bp.route('/<uuid:id>', methods=['PUT'])
def update_document_tone_analysis(id):
    """
    Update document_tone_analysis record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = DocumentToneAnalysisCRUD.update(db, id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@document_tone_analysis_bp.route('/<uuid:id>', methods=['DELETE'])
def delete_document_tone_analysis(id):
    """
    Delete document_tone_analysis record
    """
    try:
        with get_db_session() as db:
            success = DocumentToneAnalysisCRUD.delete(db, id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ErrorLog Routes
error_log_bp = Blueprint('error_log', __name__, url_prefix='/api/error-log')

@error_log_bp.route('/', methods=['GET'])
def get_error_log_list():
    """
    Get all error_log records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = ErrorLogCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@error_log_bp.route('/<uuid:id>', methods=['GET'])
def get_error_log_by_id(id):
    """
    Get error_log by ID
    """
    try:
        with get_db_session() as db:
            record = ErrorLogCRUD.get_by_id(db, id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@error_log_bp.route('/', methods=['POST'])
def create_error_log():
    """
    Create new error_log record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = ErrorLogCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@error_log_bp.route('/<uuid:id>', methods=['PUT'])
def update_error_log(id):
    """
    Update error_log record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = ErrorLogCRUD.update(db, id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@error_log_bp.route('/<uuid:id>', methods=['DELETE'])
def delete_error_log(id):
    """
    Delete error_log record
    """
    try:
        with get_db_session() as db:
            success = ErrorLogCRUD.delete(db, id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# FailureLogs Routes
failure_logs_bp = Blueprint('failure_logs', __name__, url_prefix='/api/failure-logs')

@failure_logs_bp.route('/', methods=['GET'])
def get_failure_logs_list():
    """
    Get all failure_logs records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = FailureLogsCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@failure_logs_bp.route('/<uuid:id>', methods=['GET'])
def get_failure_logs_by_id(id):
    """
    Get failure_logs by ID
    """
    try:
        with get_db_session() as db:
            record = FailureLogsCRUD.get_by_id(db, id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@failure_logs_bp.route('/', methods=['POST'])
def create_failure_logs():
    """
    Create new failure_logs record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = FailureLogsCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@failure_logs_bp.route('/<uuid:id>', methods=['PUT'])
def update_failure_logs(id):
    """
    Update failure_logs record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = FailureLogsCRUD.update(db, id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@failure_logs_bp.route('/<uuid:id>', methods=['DELETE'])
def delete_failure_logs(id):
    """
    Delete failure_logs record
    """
    try:
        with get_db_session() as db:
            success = FailureLogsCRUD.delete(db, id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# JobAnalysisQueue Routes
job_analysis_queue_bp = Blueprint('job_analysis_queue', __name__, url_prefix='/api/job-analysis-queue')

@job_analysis_queue_bp.route('/', methods=['GET'])
def get_job_analysis_queue_list():
    """
    Get all job_analysis_queue records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = JobAnalysisQueueCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_analysis_queue_bp.route('/<uuid:id>', methods=['GET'])
def get_job_analysis_queue_by_id(id):
    """
    Get job_analysis_queue by ID
    """
    try:
        with get_db_session() as db:
            record = JobAnalysisQueueCRUD.get_by_id(db, id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_analysis_queue_bp.route('/', methods=['POST'])
def create_job_analysis_queue():
    """
    Create new job_analysis_queue record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = JobAnalysisQueueCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_analysis_queue_bp.route('/<uuid:id>', methods=['PUT'])
def update_job_analysis_queue(id):
    """
    Update job_analysis_queue record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = JobAnalysisQueueCRUD.update(db, id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_analysis_queue_bp.route('/<uuid:id>', methods=['DELETE'])
def delete_job_analysis_queue(id):
    """
    Delete job_analysis_queue record
    """
    try:
        with get_db_session() as db:
            success = JobAnalysisQueueCRUD.delete(db, id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# JobApplicationTracking Routes
job_application_tracking_bp = Blueprint('job_application_tracking', __name__, url_prefix='/api/job-application-tracking')

@job_application_tracking_bp.route('/', methods=['GET'])
def get_job_application_tracking_list():
    """
    Get all job_application_tracking records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = JobApplicationTrackingCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_application_tracking_bp.route('/<uuid:tracking_id>', methods=['GET'])
def get_job_application_tracking_by_id(tracking_id):
    """
    Get job_application_tracking by ID
    """
    try:
        with get_db_session() as db:
            record = JobApplicationTrackingCRUD.get_by_id(db, tracking_id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_application_tracking_bp.route('/', methods=['POST'])
def create_job_application_tracking():
    """
    Create new job_application_tracking record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = JobApplicationTrackingCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_application_tracking_bp.route('/<uuid:tracking_id>', methods=['PUT'])
def update_job_application_tracking(tracking_id):
    """
    Update job_application_tracking record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = JobApplicationTrackingCRUD.update(db, tracking_id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_application_tracking_bp.route('/<uuid:tracking_id>', methods=['DELETE'])
def delete_job_application_tracking(tracking_id):
    """
    Delete job_application_tracking record
    """
    try:
        with get_db_session() as db:
            success = JobApplicationTrackingCRUD.delete(db, tracking_id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# JobApplications Routes
job_applications_bp = Blueprint('job_applications', __name__, url_prefix='/api/job-applications')

@job_applications_bp.route('/', methods=['GET'])
def get_job_applications_list():
    """
    Get all job_applications records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = JobApplicationsCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_applications_bp.route('/<uuid:id>', methods=['GET'])
def get_job_applications_by_id(id):
    """
    Get job_applications by ID
    """
    try:
        with get_db_session() as db:
            record = JobApplicationsCRUD.get_by_id(db, id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_applications_bp.route('/', methods=['POST'])
def create_job_applications():
    """
    Create new job_applications record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = JobApplicationsCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_applications_bp.route('/<uuid:id>', methods=['PUT'])
def update_job_applications(id):
    """
    Update job_applications record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = JobApplicationsCRUD.update(db, id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_applications_bp.route('/<uuid:id>', methods=['DELETE'])
def delete_job_applications(id):
    """
    Delete job_applications record
    """
    try:
        with get_db_session() as db:
            success = JobApplicationsCRUD.delete(db, id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# JobAtsKeywords Routes
job_ats_keywords_bp = Blueprint('job_ats_keywords', __name__, url_prefix='/api/job-ats-keywords')

@job_ats_keywords_bp.route('/', methods=['GET'])
def get_job_ats_keywords_list():
    """
    Get all job_ats_keywords records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = JobAtsKeywordsCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_ats_keywords_bp.route('/<uuid:id>', methods=['GET'])
def get_job_ats_keywords_by_id(id):
    """
    Get job_ats_keywords by ID
    """
    try:
        with get_db_session() as db:
            record = JobAtsKeywordsCRUD.get_by_id(db, id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_ats_keywords_bp.route('/', methods=['POST'])
def create_job_ats_keywords():
    """
    Create new job_ats_keywords record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = JobAtsKeywordsCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_ats_keywords_bp.route('/<uuid:id>', methods=['PUT'])
def update_job_ats_keywords(id):
    """
    Update job_ats_keywords record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = JobAtsKeywordsCRUD.update(db, id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_ats_keywords_bp.route('/<uuid:id>', methods=['DELETE'])
def delete_job_ats_keywords(id):
    """
    Delete job_ats_keywords record
    """
    try:
        with get_db_session() as db:
            success = JobAtsKeywordsCRUD.delete(db, id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# JobBenefits Routes
job_benefits_bp = Blueprint('job_benefits', __name__, url_prefix='/api/job-benefits')

@job_benefits_bp.route('/', methods=['GET'])
def get_job_benefits_list():
    """
    Get all job_benefits records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = JobBenefitsCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_benefits_bp.route('/<uuid:benefit_id>', methods=['GET'])
def get_job_benefits_by_id(benefit_id):
    """
    Get job_benefits by ID
    """
    try:
        with get_db_session() as db:
            record = JobBenefitsCRUD.get_by_id(db, benefit_id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_benefits_bp.route('/', methods=['POST'])
def create_job_benefits():
    """
    Create new job_benefits record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = JobBenefitsCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_benefits_bp.route('/<uuid:benefit_id>', methods=['PUT'])
def update_job_benefits(benefit_id):
    """
    Update job_benefits record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = JobBenefitsCRUD.update(db, benefit_id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_benefits_bp.route('/<uuid:benefit_id>', methods=['DELETE'])
def delete_job_benefits(benefit_id):
    """
    Delete job_benefits record
    """
    try:
        with get_db_session() as db:
            success = JobBenefitsCRUD.delete(db, benefit_id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# JobCertifications Routes
job_certifications_bp = Blueprint('job_certifications', __name__, url_prefix='/api/job-certifications')

@job_certifications_bp.route('/', methods=['GET'])
def get_job_certifications_list():
    """
    Get all job_certifications records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = JobCertificationsCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_certifications_bp.route('/<uuid:id>', methods=['GET'])
def get_job_certifications_by_id(id):
    """
    Get job_certifications by ID
    """
    try:
        with get_db_session() as db:
            record = JobCertificationsCRUD.get_by_id(db, id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_certifications_bp.route('/', methods=['POST'])
def create_job_certifications():
    """
    Create new job_certifications record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = JobCertificationsCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_certifications_bp.route('/<uuid:id>', methods=['PUT'])
def update_job_certifications(id):
    """
    Update job_certifications record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = JobCertificationsCRUD.update(db, id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_certifications_bp.route('/<uuid:id>', methods=['DELETE'])
def delete_job_certifications(id):
    """
    Delete job_certifications record
    """
    try:
        with get_db_session() as db:
            success = JobCertificationsCRUD.delete(db, id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# JobEducationRequirements Routes
job_education_requirements_bp = Blueprint('job_education_requirements', __name__, url_prefix='/api/job-education-requirements')

@job_education_requirements_bp.route('/', methods=['GET'])
def get_job_education_requirements_list():
    """
    Get all job_education_requirements records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = JobEducationRequirementsCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_education_requirements_bp.route('/<uuid:id>', methods=['GET'])
def get_job_education_requirements_by_id(id):
    """
    Get job_education_requirements by ID
    """
    try:
        with get_db_session() as db:
            record = JobEducationRequirementsCRUD.get_by_id(db, id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_education_requirements_bp.route('/', methods=['POST'])
def create_job_education_requirements():
    """
    Create new job_education_requirements record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = JobEducationRequirementsCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_education_requirements_bp.route('/<uuid:id>', methods=['PUT'])
def update_job_education_requirements(id):
    """
    Update job_education_requirements record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = JobEducationRequirementsCRUD.update(db, id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_education_requirements_bp.route('/<uuid:id>', methods=['DELETE'])
def delete_job_education_requirements(id):
    """
    Delete job_education_requirements record
    """
    try:
        with get_db_session() as db:
            success = JobEducationRequirementsCRUD.delete(db, id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# JobLogs Routes
job_logs_bp = Blueprint('job_logs', __name__, url_prefix='/api/job-logs')

@job_logs_bp.route('/', methods=['GET'])
def get_job_logs_list():
    """
    Get all job_logs records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = JobLogsCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_logs_bp.route('/<uuid:log_id>', methods=['GET'])
def get_job_logs_by_id(log_id):
    """
    Get job_logs by ID
    """
    try:
        with get_db_session() as db:
            record = JobLogsCRUD.get_by_id(db, log_id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_logs_bp.route('/', methods=['POST'])
def create_job_logs():
    """
    Create new job_logs record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = JobLogsCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_logs_bp.route('/<uuid:log_id>', methods=['PUT'])
def update_job_logs(log_id):
    """
    Update job_logs record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = JobLogsCRUD.update(db, log_id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_logs_bp.route('/<uuid:log_id>', methods=['DELETE'])
def delete_job_logs(log_id):
    """
    Delete job_logs record
    """
    try:
        with get_db_session() as db:
            success = JobLogsCRUD.delete(db, log_id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# JobPlatformsFound Routes
job_platforms_found_bp = Blueprint('job_platforms_found', __name__, url_prefix='/api/job-platforms-found')

@job_platforms_found_bp.route('/', methods=['GET'])
def get_job_platforms_found_list():
    """
    Get all job_platforms_found records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = JobPlatformsFoundCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_platforms_found_bp.route('/<uuid:platform_id>', methods=['GET'])
def get_job_platforms_found_by_id(platform_id):
    """
    Get job_platforms_found by ID
    """
    try:
        with get_db_session() as db:
            record = JobPlatformsFoundCRUD.get_by_id(db, platform_id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_platforms_found_bp.route('/', methods=['POST'])
def create_job_platforms_found():
    """
    Create new job_platforms_found record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = JobPlatformsFoundCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_platforms_found_bp.route('/<uuid:platform_id>', methods=['PUT'])
def update_job_platforms_found(platform_id):
    """
    Update job_platforms_found record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = JobPlatformsFoundCRUD.update(db, platform_id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_platforms_found_bp.route('/<uuid:platform_id>', methods=['DELETE'])
def delete_job_platforms_found(platform_id):
    """
    Delete job_platforms_found record
    """
    try:
        with get_db_session() as db:
            success = JobPlatformsFoundCRUD.delete(db, platform_id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# JobRedFlagsDetails Routes
job_red_flags_details_bp = Blueprint('job_red_flags_details', __name__, url_prefix='/api/job-red-flags-details')

@job_red_flags_details_bp.route('/', methods=['GET'])
def get_job_red_flags_details_list():
    """
    Get all job_red_flags_details records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = JobRedFlagsDetailsCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_red_flags_details_bp.route('/<uuid:id>', methods=['GET'])
def get_job_red_flags_details_by_id(id):
    """
    Get job_red_flags_details by ID
    """
    try:
        with get_db_session() as db:
            record = JobRedFlagsDetailsCRUD.get_by_id(db, id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_red_flags_details_bp.route('/', methods=['POST'])
def create_job_red_flags_details():
    """
    Create new job_red_flags_details record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = JobRedFlagsDetailsCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_red_flags_details_bp.route('/<uuid:id>', methods=['PUT'])
def update_job_red_flags_details(id):
    """
    Update job_red_flags_details record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = JobRedFlagsDetailsCRUD.update(db, id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_red_flags_details_bp.route('/<uuid:id>', methods=['DELETE'])
def delete_job_red_flags_details(id):
    """
    Delete job_red_flags_details record
    """
    try:
        with get_db_session() as db:
            success = JobRedFlagsDetailsCRUD.delete(db, id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# JobRequiredDocuments Routes
job_required_documents_bp = Blueprint('job_required_documents', __name__, url_prefix='/api/job-required-documents')

@job_required_documents_bp.route('/', methods=['GET'])
def get_job_required_documents_list():
    """
    Get all job_required_documents records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = JobRequiredDocumentsCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_required_documents_bp.route('/<uuid:id>', methods=['GET'])
def get_job_required_documents_by_id(id):
    """
    Get job_required_documents by ID
    """
    try:
        with get_db_session() as db:
            record = JobRequiredDocumentsCRUD.get_by_id(db, id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_required_documents_bp.route('/', methods=['POST'])
def create_job_required_documents():
    """
    Create new job_required_documents record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = JobRequiredDocumentsCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_required_documents_bp.route('/<uuid:id>', methods=['PUT'])
def update_job_required_documents(id):
    """
    Update job_required_documents record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = JobRequiredDocumentsCRUD.update(db, id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_required_documents_bp.route('/<uuid:id>', methods=['DELETE'])
def delete_job_required_documents(id):
    """
    Delete job_required_documents record
    """
    try:
        with get_db_session() as db:
            success = JobRequiredDocumentsCRUD.delete(db, id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# JobRequiredSkills Routes
job_required_skills_bp = Blueprint('job_required_skills', __name__, url_prefix='/api/job-required-skills')

@job_required_skills_bp.route('/', methods=['GET'])
def get_job_required_skills_list():
    """
    Get all job_required_skills records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = JobRequiredSkillsCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_required_skills_bp.route('/<uuid:skill_id>', methods=['GET'])
def get_job_required_skills_by_id(skill_id):
    """
    Get job_required_skills by ID
    """
    try:
        with get_db_session() as db:
            record = JobRequiredSkillsCRUD.get_by_id(db, skill_id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_required_skills_bp.route('/', methods=['POST'])
def create_job_required_skills():
    """
    Create new job_required_skills record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = JobRequiredSkillsCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_required_skills_bp.route('/<uuid:skill_id>', methods=['PUT'])
def update_job_required_skills(skill_id):
    """
    Update job_required_skills record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = JobRequiredSkillsCRUD.update(db, skill_id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_required_skills_bp.route('/<uuid:skill_id>', methods=['DELETE'])
def delete_job_required_skills(skill_id):
    """
    Delete job_required_skills record
    """
    try:
        with get_db_session() as db:
            success = JobRequiredSkillsCRUD.delete(db, skill_id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# JobSkills Routes
job_skills_bp = Blueprint('job_skills', __name__, url_prefix='/api/job-skills')

@job_skills_bp.route('/', methods=['GET'])
def get_job_skills_list():
    """
    Get all job_skills records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = JobSkillsCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_skills_bp.route('/<uuid:skill_id>', methods=['GET'])
def get_job_skills_by_id(skill_id):
    """
    Get job_skills by ID
    """
    try:
        with get_db_session() as db:
            record = JobSkillsCRUD.get_by_id(db, skill_id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_skills_bp.route('/', methods=['POST'])
def create_job_skills():
    """
    Create new job_skills record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = JobSkillsCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_skills_bp.route('/<uuid:skill_id>', methods=['PUT'])
def update_job_skills(skill_id):
    """
    Update job_skills record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = JobSkillsCRUD.update(db, skill_id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_skills_bp.route('/<uuid:skill_id>', methods=['DELETE'])
def delete_job_skills(skill_id):
    """
    Delete job_skills record
    """
    try:
        with get_db_session() as db:
            success = JobSkillsCRUD.delete(db, skill_id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# JobStressIndicators Routes
job_stress_indicators_bp = Blueprint('job_stress_indicators', __name__, url_prefix='/api/job-stress-indicators')

@job_stress_indicators_bp.route('/', methods=['GET'])
def get_job_stress_indicators_list():
    """
    Get all job_stress_indicators records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = JobStressIndicatorsCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_stress_indicators_bp.route('/<uuid:id>', methods=['GET'])
def get_job_stress_indicators_by_id(id):
    """
    Get job_stress_indicators by ID
    """
    try:
        with get_db_session() as db:
            record = JobStressIndicatorsCRUD.get_by_id(db, id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_stress_indicators_bp.route('/', methods=['POST'])
def create_job_stress_indicators():
    """
    Create new job_stress_indicators record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = JobStressIndicatorsCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_stress_indicators_bp.route('/<uuid:id>', methods=['PUT'])
def update_job_stress_indicators(id):
    """
    Update job_stress_indicators record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = JobStressIndicatorsCRUD.update(db, id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_stress_indicators_bp.route('/<uuid:id>', methods=['DELETE'])
def delete_job_stress_indicators(id):
    """
    Delete job_stress_indicators record
    """
    try:
        with get_db_session() as db:
            success = JobStressIndicatorsCRUD.delete(db, id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Jobs Routes
jobs_bp = Blueprint('jobs', __name__, url_prefix='/api/jobs')

@jobs_bp.route('/', methods=['GET'])
def get_jobs_list():
    """
    Get all jobs records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = JobsCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@jobs_bp.route('/<uuid:id>', methods=['GET'])
def get_jobs_by_id(id):
    """
    Get jobs by ID
    """
    try:
        with get_db_session() as db:
            record = JobsCRUD.get_by_id(db, id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@jobs_bp.route('/', methods=['POST'])
def create_jobs():
    """
    Create new jobs record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = JobsCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@jobs_bp.route('/<uuid:id>', methods=['PUT'])
def update_jobs(id):
    """
    Update jobs record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = JobsCRUD.update(db, id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@jobs_bp.route('/<uuid:id>', methods=['DELETE'])
def delete_jobs(id):
    """
    Delete jobs record
    """
    try:
        with get_db_session() as db:
            success = JobsCRUD.delete(db, id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# KeywordFilters Routes
keyword_filters_bp = Blueprint('keyword_filters', __name__, url_prefix='/api/keyword-filters')

@keyword_filters_bp.route('/', methods=['GET'])
def get_keyword_filters_list():
    """
    Get all keyword_filters records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = KeywordFiltersCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@keyword_filters_bp.route('/<uuid:id>', methods=['GET'])
def get_keyword_filters_by_id(id):
    """
    Get keyword_filters by ID
    """
    try:
        with get_db_session() as db:
            record = KeywordFiltersCRUD.get_by_id(db, id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@keyword_filters_bp.route('/', methods=['POST'])
def create_keyword_filters():
    """
    Create new keyword_filters record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = KeywordFiltersCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@keyword_filters_bp.route('/<uuid:id>', methods=['PUT'])
def update_keyword_filters(id):
    """
    Update keyword_filters record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = KeywordFiltersCRUD.update(db, id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@keyword_filters_bp.route('/<uuid:id>', methods=['DELETE'])
def delete_keyword_filters(id):
    """
    Delete keyword_filters record
    """
    try:
        with get_db_session() as db:
            success = KeywordFiltersCRUD.delete(db, id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# LinkClicks Routes
link_clicks_bp = Blueprint('link_clicks', __name__, url_prefix='/api/link-clicks')

@link_clicks_bp.route('/', methods=['GET'])
def get_link_clicks_list():
    """
    Get all link_clicks records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = LinkClicksCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@link_clicks_bp.route('/<uuid:click_id>', methods=['GET'])
def get_link_clicks_by_id(click_id):
    """
    Get link_clicks by ID
    """
    try:
        with get_db_session() as db:
            record = LinkClicksCRUD.get_by_id(db, click_id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@link_clicks_bp.route('/', methods=['POST'])
def create_link_clicks():
    """
    Create new link_clicks record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = LinkClicksCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@link_clicks_bp.route('/<uuid:click_id>', methods=['PUT'])
def update_link_clicks(click_id):
    """
    Update link_clicks record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = LinkClicksCRUD.update(db, click_id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@link_clicks_bp.route('/<uuid:click_id>', methods=['DELETE'])
def delete_link_clicks(click_id):
    """
    Delete link_clicks record
    """
    try:
        with get_db_session() as db:
            success = LinkClicksCRUD.delete(db, click_id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# LinkTracking Routes
link_tracking_bp = Blueprint('link_tracking', __name__, url_prefix='/api/link-tracking')

@link_tracking_bp.route('/', methods=['GET'])
def get_link_tracking_list():
    """
    Get all link_tracking records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = LinkTrackingCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@link_tracking_bp.route('/<uuid:tracking_id>', methods=['GET'])
def get_link_tracking_by_id(tracking_id):
    """
    Get link_tracking by ID
    """
    try:
        with get_db_session() as db:
            record = LinkTrackingCRUD.get_by_id(db, tracking_id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@link_tracking_bp.route('/', methods=['POST'])
def create_link_tracking():
    """
    Create new link_tracking record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = LinkTrackingCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@link_tracking_bp.route('/<uuid:tracking_id>', methods=['PUT'])
def update_link_tracking(tracking_id):
    """
    Update link_tracking record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = LinkTrackingCRUD.update(db, tracking_id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@link_tracking_bp.route('/<uuid:tracking_id>', methods=['DELETE'])
def delete_link_tracking(tracking_id):
    """
    Delete link_tracking record
    """
    try:
        with get_db_session() as db:
            success = LinkTrackingCRUD.delete(db, tracking_id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# PerformanceMetrics Routes
performance_metrics_bp = Blueprint('performance_metrics', __name__, url_prefix='/api/performance-metrics')

@performance_metrics_bp.route('/', methods=['GET'])
def get_performance_metrics_list():
    """
    Get all performance_metrics records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = PerformanceMetricsCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@performance_metrics_bp.route('/<uuid:id>', methods=['GET'])
def get_performance_metrics_by_id(id):
    """
    Get performance_metrics by ID
    """
    try:
        with get_db_session() as db:
            record = PerformanceMetricsCRUD.get_by_id(db, id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@performance_metrics_bp.route('/', methods=['POST'])
def create_performance_metrics():
    """
    Create new performance_metrics record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = PerformanceMetricsCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@performance_metrics_bp.route('/<uuid:id>', methods=['PUT'])
def update_performance_metrics(id):
    """
    Update performance_metrics record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = PerformanceMetricsCRUD.update(db, id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@performance_metrics_bp.route('/<uuid:id>', methods=['DELETE'])
def delete_performance_metrics(id):
    """
    Delete performance_metrics record
    """
    try:
        with get_db_session() as db:
            success = PerformanceMetricsCRUD.delete(db, id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# PreAnalyzedJobs Routes
pre_analyzed_jobs_bp = Blueprint('pre_analyzed_jobs', __name__, url_prefix='/api/pre-analyzed-jobs')

@pre_analyzed_jobs_bp.route('/', methods=['GET'])
def get_pre_analyzed_jobs_list():
    """
    Get all pre_analyzed_jobs records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = PreAnalyzedJobsCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pre_analyzed_jobs_bp.route('/<uuid:id>', methods=['GET'])
def get_pre_analyzed_jobs_by_id(id):
    """
    Get pre_analyzed_jobs by ID
    """
    try:
        with get_db_session() as db:
            record = PreAnalyzedJobsCRUD.get_by_id(db, id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pre_analyzed_jobs_bp.route('/', methods=['POST'])
def create_pre_analyzed_jobs():
    """
    Create new pre_analyzed_jobs record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = PreAnalyzedJobsCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pre_analyzed_jobs_bp.route('/<uuid:id>', methods=['PUT'])
def update_pre_analyzed_jobs(id):
    """
    Update pre_analyzed_jobs record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = PreAnalyzedJobsCRUD.update(db, id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pre_analyzed_jobs_bp.route('/<uuid:id>', methods=['DELETE'])
def delete_pre_analyzed_jobs(id):
    """
    Delete pre_analyzed_jobs record
    """
    try:
        with get_db_session() as db:
            success = PreAnalyzedJobsCRUD.delete(db, id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# RawJobScrapes Routes
raw_job_scrapes_bp = Blueprint('raw_job_scrapes', __name__, url_prefix='/api/raw-job-scrapes')

@raw_job_scrapes_bp.route('/', methods=['GET'])
def get_raw_job_scrapes_list():
    """
    Get all raw_job_scrapes records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = RawJobScrapesCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@raw_job_scrapes_bp.route('/<uuid:scrape_id>', methods=['GET'])
def get_raw_job_scrapes_by_id(scrape_id):
    """
    Get raw_job_scrapes by ID
    """
    try:
        with get_db_session() as db:
            record = RawJobScrapesCRUD.get_by_id(db, scrape_id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@raw_job_scrapes_bp.route('/', methods=['POST'])
def create_raw_job_scrapes():
    """
    Create new raw_job_scrapes record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = RawJobScrapesCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@raw_job_scrapes_bp.route('/<uuid:scrape_id>', methods=['PUT'])
def update_raw_job_scrapes(scrape_id):
    """
    Update raw_job_scrapes record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = RawJobScrapesCRUD.update(db, scrape_id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@raw_job_scrapes_bp.route('/<uuid:scrape_id>', methods=['DELETE'])
def delete_raw_job_scrapes(scrape_id):
    """
    Delete raw_job_scrapes record
    """
    try:
        with get_db_session() as db:
            success = RawJobScrapesCRUD.delete(db, scrape_id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# RecoveryStatistics Routes
recovery_statistics_bp = Blueprint('recovery_statistics', __name__, url_prefix='/api/recovery-statistics')

@recovery_statistics_bp.route('/', methods=['GET'])
def get_recovery_statistics_list():
    """
    Get all recovery_statistics records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = RecoveryStatisticsCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recovery_statistics_bp.route('/<uuid:id>', methods=['GET'])
def get_recovery_statistics_by_id(id):
    """
    Get recovery_statistics by ID
    """
    try:
        with get_db_session() as db:
            record = RecoveryStatisticsCRUD.get_by_id(db, id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recovery_statistics_bp.route('/', methods=['POST'])
def create_recovery_statistics():
    """
    Create new recovery_statistics record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = RecoveryStatisticsCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recovery_statistics_bp.route('/<uuid:id>', methods=['PUT'])
def update_recovery_statistics(id):
    """
    Update recovery_statistics record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = RecoveryStatisticsCRUD.update(db, id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recovery_statistics_bp.route('/<uuid:id>', methods=['DELETE'])
def delete_recovery_statistics(id):
    """
    Delete recovery_statistics record
    """
    try:
        with get_db_session() as db:
            success = RecoveryStatisticsCRUD.delete(db, id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# SecurityTestTable Routes
security_test_table_bp = Blueprint('security_test_table', __name__, url_prefix='/api/security-test-table')

@security_test_table_bp.route('/', methods=['GET'])
def get_security_test_table_list():
    """
    Get all security_test_table records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = SecurityTestTableCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@security_test_table_bp.route('/', methods=['POST'])
def create_security_test_table():
    """
    Create new security_test_table record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = SecurityTestTableCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# SentenceBankCoverLetter Routes
sentence_bank_cover_letter_bp = Blueprint('sentence_bank_cover_letter', __name__, url_prefix='/api/sentence-bank-cover-letter')

@sentence_bank_cover_letter_bp.route('/', methods=['GET'])
def get_sentence_bank_cover_letter_list():
    """
    Get all sentence_bank_cover_letter records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = SentenceBankCoverLetterCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sentence_bank_cover_letter_bp.route('/<uuid:id>', methods=['GET'])
def get_sentence_bank_cover_letter_by_id(id):
    """
    Get sentence_bank_cover_letter by ID
    """
    try:
        with get_db_session() as db:
            record = SentenceBankCoverLetterCRUD.get_by_id(db, id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sentence_bank_cover_letter_bp.route('/', methods=['POST'])
def create_sentence_bank_cover_letter():
    """
    Create new sentence_bank_cover_letter record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = SentenceBankCoverLetterCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sentence_bank_cover_letter_bp.route('/<uuid:id>', methods=['PUT'])
def update_sentence_bank_cover_letter(id):
    """
    Update sentence_bank_cover_letter record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = SentenceBankCoverLetterCRUD.update(db, id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sentence_bank_cover_letter_bp.route('/<uuid:id>', methods=['DELETE'])
def delete_sentence_bank_cover_letter(id):
    """
    Delete sentence_bank_cover_letter record
    """
    try:
        with get_db_session() as db:
            success = SentenceBankCoverLetterCRUD.delete(db, id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# SentenceBankResume Routes
sentence_bank_resume_bp = Blueprint('sentence_bank_resume', __name__, url_prefix='/api/sentence-bank-resume')

@sentence_bank_resume_bp.route('/', methods=['GET'])
def get_sentence_bank_resume_list():
    """
    Get all sentence_bank_resume records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = SentenceBankResumeCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sentence_bank_resume_bp.route('/<uuid:id>', methods=['GET'])
def get_sentence_bank_resume_by_id(id):
    """
    Get sentence_bank_resume by ID
    """
    try:
        with get_db_session() as db:
            record = SentenceBankResumeCRUD.get_by_id(db, id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sentence_bank_resume_bp.route('/', methods=['POST'])
def create_sentence_bank_resume():
    """
    Create new sentence_bank_resume record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = SentenceBankResumeCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sentence_bank_resume_bp.route('/<uuid:id>', methods=['PUT'])
def update_sentence_bank_resume(id):
    """
    Update sentence_bank_resume record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = SentenceBankResumeCRUD.update(db, id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sentence_bank_resume_bp.route('/<uuid:id>', methods=['DELETE'])
def delete_sentence_bank_resume(id):
    """
    Delete sentence_bank_resume record
    """
    try:
        with get_db_session() as db:
            success = SentenceBankResumeCRUD.delete(db, id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# UserCandidateInfo Routes
user_candidate_info_bp = Blueprint('user_candidate_info', __name__, url_prefix='/api/user-candidate-info')

@user_candidate_info_bp.route('/', methods=['GET'])
def get_user_candidate_info_list():
    """
    Get all user_candidate_info records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = UserCandidateInfoCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_candidate_info_bp.route('/<uuid:id>', methods=['GET'])
def get_user_candidate_info_by_id(id):
    """
    Get user_candidate_info by ID
    """
    try:
        with get_db_session() as db:
            record = UserCandidateInfoCRUD.get_by_id(db, id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_candidate_info_bp.route('/', methods=['POST'])
def create_user_candidate_info():
    """
    Create new user_candidate_info record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = UserCandidateInfoCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_candidate_info_bp.route('/<uuid:id>', methods=['PUT'])
def update_user_candidate_info(id):
    """
    Update user_candidate_info record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = UserCandidateInfoCRUD.update(db, id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_candidate_info_bp.route('/<uuid:id>', methods=['DELETE'])
def delete_user_candidate_info(id):
    """
    Delete user_candidate_info record
    """
    try:
        with get_db_session() as db:
            success = UserCandidateInfoCRUD.delete(db, id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# UserJobPreferences Routes
user_job_preferences_bp = Blueprint('user_job_preferences', __name__, url_prefix='/api/user-job-preferences')

@user_job_preferences_bp.route('/', methods=['GET'])
def get_user_job_preferences_list():
    """
    Get all user_job_preferences records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = UserJobPreferencesCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_job_preferences_bp.route('/<uuid:id>', methods=['GET'])
def get_user_job_preferences_by_id(id):
    """
    Get user_job_preferences by ID
    """
    try:
        with get_db_session() as db:
            record = UserJobPreferencesCRUD.get_by_id(db, id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_job_preferences_bp.route('/', methods=['POST'])
def create_user_job_preferences():
    """
    Create new user_job_preferences record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = UserJobPreferencesCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_job_preferences_bp.route('/<uuid:id>', methods=['PUT'])
def update_user_job_preferences(id):
    """
    Update user_job_preferences record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = UserJobPreferencesCRUD.update(db, id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_job_preferences_bp.route('/<uuid:id>', methods=['DELETE'])
def delete_user_job_preferences(id):
    """
    Delete user_job_preferences record
    """
    try:
        with get_db_session() as db:
            success = UserJobPreferencesCRUD.delete(db, id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# UserPreferencePackages Routes
user_preference_packages_bp = Blueprint('user_preference_packages', __name__, url_prefix='/api/user-preference-packages')

@user_preference_packages_bp.route('/', methods=['GET'])
def get_user_preference_packages_list():
    """
    Get all user_preference_packages records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = UserPreferencePackagesCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_preference_packages_bp.route('/<uuid:package_id>', methods=['GET'])
def get_user_preference_packages_by_id(package_id):
    """
    Get user_preference_packages by ID
    """
    try:
        with get_db_session() as db:
            record = UserPreferencePackagesCRUD.get_by_id(db, package_id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_preference_packages_bp.route('/', methods=['POST'])
def create_user_preference_packages():
    """
    Create new user_preference_packages record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = UserPreferencePackagesCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_preference_packages_bp.route('/<uuid:package_id>', methods=['PUT'])
def update_user_preference_packages(package_id):
    """
    Update user_preference_packages record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = UserPreferencePackagesCRUD.update(db, package_id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_preference_packages_bp.route('/<uuid:package_id>', methods=['DELETE'])
def delete_user_preference_packages(package_id):
    """
    Delete user_preference_packages record
    """
    try:
        with get_db_session() as db:
            success = UserPreferencePackagesCRUD.delete(db, package_id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# UserPreferredIndustries Routes
user_preferred_industries_bp = Blueprint('user_preferred_industries', __name__, url_prefix='/api/user-preferred-industries')

@user_preferred_industries_bp.route('/', methods=['GET'])
def get_user_preferred_industries_list():
    """
    Get all user_preferred_industries records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = UserPreferredIndustriesCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_preferred_industries_bp.route('/<uuid:preference_id>', methods=['GET'])
def get_user_preferred_industries_by_id(preference_id):
    """
    Get user_preferred_industries by ID
    """
    try:
        with get_db_session() as db:
            record = UserPreferredIndustriesCRUD.get_by_id(db, preference_id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_preferred_industries_bp.route('/', methods=['POST'])
def create_user_preferred_industries():
    """
    Create new user_preferred_industries record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = UserPreferredIndustriesCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_preferred_industries_bp.route('/<uuid:preference_id>', methods=['PUT'])
def update_user_preferred_industries(preference_id):
    """
    Update user_preferred_industries record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = UserPreferredIndustriesCRUD.update(db, preference_id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_preferred_industries_bp.route('/<uuid:preference_id>', methods=['DELETE'])
def delete_user_preferred_industries(preference_id):
    """
    Delete user_preferred_industries record
    """
    try:
        with get_db_session() as db:
            success = UserPreferredIndustriesCRUD.delete(db, preference_id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# WorkExperiences Routes
work_experiences_bp = Blueprint('work_experiences', __name__, url_prefix='/api/work-experiences')

@work_experiences_bp.route('/', methods=['GET'])
def get_work_experiences_list():
    """
    Get all work_experiences records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = WorkExperiencesCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@work_experiences_bp.route('/<uuid:id>', methods=['GET'])
def get_work_experiences_by_id(id):
    """
    Get work_experiences by ID
    """
    try:
        with get_db_session() as db:
            record = WorkExperiencesCRUD.get_by_id(db, id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@work_experiences_bp.route('/', methods=['POST'])
def create_work_experiences():
    """
    Create new work_experiences record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = WorkExperiencesCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@work_experiences_bp.route('/<uuid:id>', methods=['PUT'])
def update_work_experiences(id):
    """
    Update work_experiences record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = WorkExperiencesCRUD.update(db, id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@work_experiences_bp.route('/<uuid:id>', methods=['DELETE'])
def delete_work_experiences(id):
    """
    Delete work_experiences record
    """
    try:
        with get_db_session() as db:
            success = WorkExperiencesCRUD.delete(db, id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# WorkflowCheckpoints Routes
workflow_checkpoints_bp = Blueprint('workflow_checkpoints', __name__, url_prefix='/api/workflow-checkpoints')

@workflow_checkpoints_bp.route('/', methods=['GET'])
def get_workflow_checkpoints_list():
    """
    Get all workflow_checkpoints records
    """
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        with get_db_session() as db:
            records = WorkflowCheckpointsCRUD.get_all(db, skip=skip, limit=limit)
            return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workflow_checkpoints_bp.route('/<uuid:id>', methods=['GET'])
def get_workflow_checkpoints_by_id(id):
    """
    Get workflow_checkpoints by ID
    """
    try:
        with get_db_session() as db:
            record = WorkflowCheckpointsCRUD.get_by_id(db, id)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workflow_checkpoints_bp.route('/', methods=['POST'])
def create_workflow_checkpoints():
    """
    Create new workflow_checkpoints record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = WorkflowCheckpointsCRUD.create(db, data)
            return jsonify(record.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workflow_checkpoints_bp.route('/<uuid:id>', methods=['PUT'])
def update_workflow_checkpoints(id):
    """
    Update workflow_checkpoints record
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        with get_db_session() as db:
            record = WorkflowCheckpointsCRUD.update(db, id, data)
            if record:
                return jsonify(record.to_dict())
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workflow_checkpoints_bp.route('/<uuid:id>', methods=['DELETE'])
def delete_workflow_checkpoints(id):
    """
    Delete workflow_checkpoints record
    """
    try:
        with get_db_session() as db:
            success = WorkflowCheckpointsCRUD.delete(db, id)
            if success:
                return jsonify({'message': 'Record deleted successfully'})
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


