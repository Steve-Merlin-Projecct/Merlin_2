"""
Auto-generated CRUD Operations
Generated from database schema on 2025-10-24 02:33:15
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

# Import models and schemas (adjust import paths as needed)
# from .models import *
# from .schemas import *

class AnalyzedJobsCRUD:
    """
    CRUD operations for analyzed_jobs table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> AnalyzedJobs:
        """
        Create a new analyzed_jobs record
        """
        db_obj = AnalyzedJobs(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, id: UUID) -> Optional[AnalyzedJobs]:
        """
        Get analyzed_jobs by ID
        """
        return db.query(AnalyzedJobs).filter(AnalyzedJobs.id == id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[AnalyzedJobs]:
        """
        Get all analyzed_jobs records with pagination
        """
        return db.query(AnalyzedJobs).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, id: UUID, update_data: Dict[str, Any]) -> Optional[AnalyzedJobs]:
        """
        Update analyzed_jobs record
        """
        db_obj = db.query(AnalyzedJobs).filter(AnalyzedJobs.id == id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, id: UUID) -> bool:
        """
        Delete analyzed_jobs record
        """
        db_obj = db.query(AnalyzedJobs).filter(AnalyzedJobs.id == id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[AnalyzedJobs]:
        """
        Search analyzed_jobs records by text content
        """
        return db.query(AnalyzedJobs).filter(
            db.or_(
                AnalyzedJobs.job_title.ilike(f'%{query}%'),
                AnalyzedJobs.job_description.ilike(f'%{query}%'),
                AnalyzedJobs.job_number.ilike(f'%{query}%'),
            )
        ).limit(limit).all()

    @staticmethod
    def get_by_status(db: Session, status: str) -> List[AnalyzedJobs]:
        """
        Get analyzed_jobs records by status
        """
        return db.query(AnalyzedJobs).filter(AnalyzedJobs.application_status == status).all()



class ApifyApplicationSubmissionsCRUD:
    """
    CRUD operations for apify_application_submissions table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> ApifyApplicationSubmissions:
        """
        Create a new apify_application_submissions record
        """
        db_obj = ApifyApplicationSubmissions(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, submission_id: UUID) -> Optional[ApifyApplicationSubmissions]:
        """
        Get apify_application_submissions by ID
        """
        return db.query(ApifyApplicationSubmissions).filter(ApifyApplicationSubmissions.submission_id == submission_id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[ApifyApplicationSubmissions]:
        """
        Get all apify_application_submissions records with pagination
        """
        return db.query(ApifyApplicationSubmissions).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, submission_id: UUID, update_data: Dict[str, Any]) -> Optional[ApifyApplicationSubmissions]:
        """
        Update apify_application_submissions record
        """
        db_obj = db.query(ApifyApplicationSubmissions).filter(ApifyApplicationSubmissions.submission_id == submission_id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, submission_id: UUID) -> bool:
        """
        Delete apify_application_submissions record
        """
        db_obj = db.query(ApifyApplicationSubmissions).filter(ApifyApplicationSubmissions.submission_id == submission_id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[ApifyApplicationSubmissions]:
        """
        Search apify_application_submissions records by text content
        """
        return db.query(ApifyApplicationSubmissions).filter(
            db.or_(
                ApifyApplicationSubmissions.application_id.ilike(f'%{query}%'),
                ApifyApplicationSubmissions.job_id.ilike(f'%{query}%'),
                ApifyApplicationSubmissions.actor_run_id.ilike(f'%{query}%'),
            )
        ).limit(limit).all()

    @staticmethod
    def get_by_status(db: Session, status: str) -> List[ApifyApplicationSubmissions]:
        """
        Get apify_application_submissions records by status
        """
        return db.query(ApifyApplicationSubmissions).filter(ApifyApplicationSubmissions.status == status).all()



class ApplicationDocumentsCRUD:
    """
    CRUD operations for application_documents table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> ApplicationDocuments:
        """
        Create a new application_documents record
        """
        db_obj = ApplicationDocuments(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, document_id: UUID) -> Optional[ApplicationDocuments]:
        """
        Get application_documents by ID
        """
        return db.query(ApplicationDocuments).filter(ApplicationDocuments.document_id == document_id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[ApplicationDocuments]:
        """
        Get all application_documents records with pagination
        """
        return db.query(ApplicationDocuments).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, document_id: UUID, update_data: Dict[str, Any]) -> Optional[ApplicationDocuments]:
        """
        Update application_documents record
        """
        db_obj = db.query(ApplicationDocuments).filter(ApplicationDocuments.document_id == document_id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, document_id: UUID) -> bool:
        """
        Delete application_documents record
        """
        db_obj = db.query(ApplicationDocuments).filter(ApplicationDocuments.document_id == document_id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[ApplicationDocuments]:
        """
        Search application_documents records by text content
        """
        return db.query(ApplicationDocuments).filter(
            db.or_(
                ApplicationDocuments.document_type.ilike(f'%{query}%'),
                ApplicationDocuments.document_name.ilike(f'%{query}%'),
                ApplicationDocuments.file_path.ilike(f'%{query}%'),
            )
        ).limit(limit).all()



class ApplicationSettingsCRUD:
    """
    CRUD operations for application_settings table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> ApplicationSettings:
        """
        Create a new application_settings record
        """
        db_obj = ApplicationSettings(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, setting_key: UUID) -> Optional[ApplicationSettings]:
        """
        Get application_settings by ID
        """
        return db.query(ApplicationSettings).filter(ApplicationSettings.setting_key == setting_key).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[ApplicationSettings]:
        """
        Get all application_settings records with pagination
        """
        return db.query(ApplicationSettings).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, setting_key: UUID, update_data: Dict[str, Any]) -> Optional[ApplicationSettings]:
        """
        Update application_settings record
        """
        db_obj = db.query(ApplicationSettings).filter(ApplicationSettings.setting_key == setting_key).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, setting_key: UUID) -> bool:
        """
        Delete application_settings record
        """
        db_obj = db.query(ApplicationSettings).filter(ApplicationSettings.setting_key == setting_key).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[ApplicationSettings]:
        """
        Search application_settings records by text content
        """
        return db.query(ApplicationSettings).filter(
            db.or_(
                ApplicationSettings.setting_key.ilike(f'%{query}%'),
                ApplicationSettings.setting_value.ilike(f'%{query}%'),
                ApplicationSettings.setting_type.ilike(f'%{query}%'),
            )
        ).limit(limit).all()



class CanadianSpellingsCRUD:
    """
    CRUD operations for canadian_spellings table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> CanadianSpellings:
        """
        Create a new canadian_spellings record
        """
        db_obj = CanadianSpellings(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, id: UUID) -> Optional[CanadianSpellings]:
        """
        Get canadian_spellings by ID
        """
        return db.query(CanadianSpellings).filter(CanadianSpellings.id == id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[CanadianSpellings]:
        """
        Get all canadian_spellings records with pagination
        """
        return db.query(CanadianSpellings).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, id: UUID, update_data: Dict[str, Any]) -> Optional[CanadianSpellings]:
        """
        Update canadian_spellings record
        """
        db_obj = db.query(CanadianSpellings).filter(CanadianSpellings.id == id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, id: UUID) -> bool:
        """
        Delete canadian_spellings record
        """
        db_obj = db.query(CanadianSpellings).filter(CanadianSpellings.id == id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[CanadianSpellings]:
        """
        Search canadian_spellings records by text content
        """
        return db.query(CanadianSpellings).filter(
            db.or_(
                CanadianSpellings.american_spelling.ilike(f'%{query}%'),
                CanadianSpellings.canadian_spelling.ilike(f'%{query}%'),
                CanadianSpellings.status.ilike(f'%{query}%'),
            )
        ).limit(limit).all()

    @staticmethod
    def get_by_status(db: Session, status: str) -> List[CanadianSpellings]:
        """
        Get canadian_spellings records by status
        """
        return db.query(CanadianSpellings).filter(CanadianSpellings.status == status).all()



class CleanedJobScrapeSourcesCRUD:
    """
    CRUD operations for cleaned_job_scrape_sources table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> CleanedJobScrapeSources:
        """
        Create a new cleaned_job_scrape_sources record
        """
        db_obj = CleanedJobScrapeSources(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, source_id: UUID) -> Optional[CleanedJobScrapeSources]:
        """
        Get cleaned_job_scrape_sources by ID
        """
        return db.query(CleanedJobScrapeSources).filter(CleanedJobScrapeSources.source_id == source_id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[CleanedJobScrapeSources]:
        """
        Get all cleaned_job_scrape_sources records with pagination
        """
        return db.query(CleanedJobScrapeSources).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, source_id: UUID, update_data: Dict[str, Any]) -> Optional[CleanedJobScrapeSources]:
        """
        Update cleaned_job_scrape_sources record
        """
        db_obj = db.query(CleanedJobScrapeSources).filter(CleanedJobScrapeSources.source_id == source_id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, source_id: UUID) -> bool:
        """
        Delete cleaned_job_scrape_sources record
        """
        db_obj = db.query(CleanedJobScrapeSources).filter(CleanedJobScrapeSources.source_id == source_id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False



class CleanedJobScrapesCRUD:
    """
    CRUD operations for cleaned_job_scrapes table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> CleanedJobScrapes:
        """
        Create a new cleaned_job_scrapes record
        """
        db_obj = CleanedJobScrapes(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, cleaned_job_id: UUID) -> Optional[CleanedJobScrapes]:
        """
        Get cleaned_job_scrapes by ID
        """
        return db.query(CleanedJobScrapes).filter(CleanedJobScrapes.cleaned_job_id == cleaned_job_id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[CleanedJobScrapes]:
        """
        Get all cleaned_job_scrapes records with pagination
        """
        return db.query(CleanedJobScrapes).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, cleaned_job_id: UUID, update_data: Dict[str, Any]) -> Optional[CleanedJobScrapes]:
        """
        Update cleaned_job_scrapes record
        """
        db_obj = db.query(CleanedJobScrapes).filter(CleanedJobScrapes.cleaned_job_id == cleaned_job_id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, cleaned_job_id: UUID) -> bool:
        """
        Delete cleaned_job_scrapes record
        """
        db_obj = db.query(CleanedJobScrapes).filter(CleanedJobScrapes.cleaned_job_id == cleaned_job_id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[CleanedJobScrapes]:
        """
        Search cleaned_job_scrapes records by text content
        """
        return db.query(CleanedJobScrapes).filter(
            db.or_(
                CleanedJobScrapes.job_title.ilike(f'%{query}%'),
                CleanedJobScrapes.company_name.ilike(f'%{query}%'),
                CleanedJobScrapes.location_city.ilike(f'%{query}%'),
            )
        ).limit(limit).all()



class CompaniesCRUD:
    """
    CRUD operations for companies table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> Companies:
        """
        Create a new companies record
        """
        db_obj = Companies(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, id: UUID) -> Optional[Companies]:
        """
        Get companies by ID
        """
        return db.query(Companies).filter(Companies.id == id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Companies]:
        """
        Get all companies records with pagination
        """
        return db.query(Companies).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, id: UUID, update_data: Dict[str, Any]) -> Optional[Companies]:
        """
        Update companies record
        """
        db_obj = db.query(Companies).filter(Companies.id == id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, id: UUID) -> bool:
        """
        Delete companies record
        """
        db_obj = db.query(Companies).filter(Companies.id == id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[Companies]:
        """
        Search companies records by text content
        """
        return db.query(Companies).filter(
            db.or_(
                Companies.name.ilike(f'%{query}%'),
                Companies.domain.ilike(f'%{query}%'),
                Companies.industry.ilike(f'%{query}%'),
            )
        ).limit(limit).all()



class ConsistencyValidationLogsCRUD:
    """
    CRUD operations for consistency_validation_logs table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> ConsistencyValidationLogs:
        """
        Create a new consistency_validation_logs record
        """
        db_obj = ConsistencyValidationLogs(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, id: UUID) -> Optional[ConsistencyValidationLogs]:
        """
        Get consistency_validation_logs by ID
        """
        return db.query(ConsistencyValidationLogs).filter(ConsistencyValidationLogs.id == id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[ConsistencyValidationLogs]:
        """
        Get all consistency_validation_logs records with pagination
        """
        return db.query(ConsistencyValidationLogs).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, id: UUID, update_data: Dict[str, Any]) -> Optional[ConsistencyValidationLogs]:
        """
        Update consistency_validation_logs record
        """
        db_obj = db.query(ConsistencyValidationLogs).filter(ConsistencyValidationLogs.id == id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, id: UUID) -> bool:
        """
        Delete consistency_validation_logs record
        """
        db_obj = db.query(ConsistencyValidationLogs).filter(ConsistencyValidationLogs.id == id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[ConsistencyValidationLogs]:
        """
        Search consistency_validation_logs records by text content
        """
        return db.query(ConsistencyValidationLogs).filter(
            db.or_(
                ConsistencyValidationLogs.issue_type.ilike(f'%{query}%'),
                ConsistencyValidationLogs.severity.ilike(f'%{query}%'),
                ConsistencyValidationLogs.description.ilike(f'%{query}%'),
            )
        ).limit(limit).all()



class DashboardMetricsDailyCRUD:
    """
    CRUD operations for dashboard_metrics_daily table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> DashboardMetricsDaily:
        """
        Create a new dashboard_metrics_daily record
        """
        db_obj = DashboardMetricsDaily(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, id: UUID) -> Optional[DashboardMetricsDaily]:
        """
        Get dashboard_metrics_daily by ID
        """
        return db.query(DashboardMetricsDaily).filter(DashboardMetricsDaily.id == id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[DashboardMetricsDaily]:
        """
        Get all dashboard_metrics_daily records with pagination
        """
        return db.query(DashboardMetricsDaily).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, id: UUID, update_data: Dict[str, Any]) -> Optional[DashboardMetricsDaily]:
        """
        Update dashboard_metrics_daily record
        """
        db_obj = db.query(DashboardMetricsDaily).filter(DashboardMetricsDaily.id == id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, id: UUID) -> bool:
        """
        Delete dashboard_metrics_daily record
        """
        db_obj = db.query(DashboardMetricsDaily).filter(DashboardMetricsDaily.id == id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[DashboardMetricsDaily]:
        """
        Search dashboard_metrics_daily records by text content
        """
        return db.query(DashboardMetricsDaily).filter(
            db.or_(
                DashboardMetricsDaily.ai_model_used.ilike(f'%{query}%'),
                DashboardMetricsDaily.pipeline_bottleneck.ilike(f'%{query}%'),
            )
        ).limit(limit).all()



class DashboardMetricsHourlyCRUD:
    """
    CRUD operations for dashboard_metrics_hourly table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> DashboardMetricsHourly:
        """
        Create a new dashboard_metrics_hourly record
        """
        db_obj = DashboardMetricsHourly(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, id: UUID) -> Optional[DashboardMetricsHourly]:
        """
        Get dashboard_metrics_hourly by ID
        """
        return db.query(DashboardMetricsHourly).filter(DashboardMetricsHourly.id == id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[DashboardMetricsHourly]:
        """
        Get all dashboard_metrics_hourly records with pagination
        """
        return db.query(DashboardMetricsHourly).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, id: UUID, update_data: Dict[str, Any]) -> Optional[DashboardMetricsHourly]:
        """
        Update dashboard_metrics_hourly record
        """
        db_obj = db.query(DashboardMetricsHourly).filter(DashboardMetricsHourly.id == id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, id: UUID) -> bool:
        """
        Delete dashboard_metrics_hourly record
        """
        db_obj = db.query(DashboardMetricsHourly).filter(DashboardMetricsHourly.id == id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[DashboardMetricsHourly]:
        """
        Search dashboard_metrics_hourly records by text content
        """
        return db.query(DashboardMetricsHourly).filter(
            db.or_(
                DashboardMetricsHourly.pipeline_bottleneck.ilike(f'%{query}%'),
            )
        ).limit(limit).all()



class DataCorrectionsCRUD:
    """
    CRUD operations for data_corrections table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> DataCorrections:
        """
        Create a new data_corrections record
        """
        db_obj = DataCorrections(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, id: UUID) -> Optional[DataCorrections]:
        """
        Get data_corrections by ID
        """
        return db.query(DataCorrections).filter(DataCorrections.id == id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[DataCorrections]:
        """
        Get all data_corrections records with pagination
        """
        return db.query(DataCorrections).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, id: UUID, update_data: Dict[str, Any]) -> Optional[DataCorrections]:
        """
        Update data_corrections record
        """
        db_obj = db.query(DataCorrections).filter(DataCorrections.id == id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, id: UUID) -> bool:
        """
        Delete data_corrections record
        """
        db_obj = db.query(DataCorrections).filter(DataCorrections.id == id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[DataCorrections]:
        """
        Search data_corrections records by text content
        """
        return db.query(DataCorrections).filter(
            db.or_(
                DataCorrections.correction_type.ilike(f'%{query}%'),
                DataCorrections.affected_table.ilike(f'%{query}%'),
                DataCorrections.correction_sql.ilike(f'%{query}%'),
            )
        ).limit(limit).all()



class DocumentJobsCRUD:
    """
    CRUD operations for document_jobs table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> DocumentJobs:
        """
        Create a new document_jobs record
        """
        db_obj = DocumentJobs(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, job_id: UUID) -> Optional[DocumentJobs]:
        """
        Get document_jobs by ID
        """
        return db.query(DocumentJobs).filter(DocumentJobs.job_id == job_id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[DocumentJobs]:
        """
        Get all document_jobs records with pagination
        """
        return db.query(DocumentJobs).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, job_id: UUID, update_data: Dict[str, Any]) -> Optional[DocumentJobs]:
        """
        Update document_jobs record
        """
        db_obj = db.query(DocumentJobs).filter(DocumentJobs.job_id == job_id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, job_id: UUID) -> bool:
        """
        Delete document_jobs record
        """
        db_obj = db.query(DocumentJobs).filter(DocumentJobs.job_id == job_id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[DocumentJobs]:
        """
        Search document_jobs records by text content
        """
        return db.query(DocumentJobs).filter(
            db.or_(
                DocumentJobs.file_path.ilike(f'%{query}%'),
                DocumentJobs.filename.ilike(f'%{query}%'),
                DocumentJobs.title.ilike(f'%{query}%'),
            )
        ).limit(limit).all()

    @staticmethod
    def get_by_status(db: Session, status: str) -> List[DocumentJobs]:
        """
        Get document_jobs records by status
        """
        return db.query(DocumentJobs).filter(DocumentJobs.status == status).all()



class DocumentSentencesCRUD:
    """
    CRUD operations for document_sentences table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> DocumentSentences:
        """
        Create a new document_sentences record
        """
        db_obj = DocumentSentences(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, sentence_id: UUID) -> Optional[DocumentSentences]:
        """
        Get document_sentences by ID
        """
        return db.query(DocumentSentences).filter(DocumentSentences.sentence_id == sentence_id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[DocumentSentences]:
        """
        Get all document_sentences records with pagination
        """
        return db.query(DocumentSentences).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, sentence_id: UUID, update_data: Dict[str, Any]) -> Optional[DocumentSentences]:
        """
        Update document_sentences record
        """
        db_obj = db.query(DocumentSentences).filter(DocumentSentences.sentence_id == sentence_id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, sentence_id: UUID) -> bool:
        """
        Delete document_sentences record
        """
        db_obj = db.query(DocumentSentences).filter(DocumentSentences.sentence_id == sentence_id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[DocumentSentences]:
        """
        Search document_sentences records by text content
        """
        return db.query(DocumentSentences).filter(
            db.or_(
                DocumentSentences.sentence_text.ilike(f'%{query}%'),
                DocumentSentences.sentiment_category.ilike(f'%{query}%'),
            )
        ).limit(limit).all()



class DocumentTemplateMetadataCRUD:
    """
    CRUD operations for document_template_metadata table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> DocumentTemplateMetadata:
        """
        Create a new document_template_metadata record
        """
        db_obj = DocumentTemplateMetadata(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, id: UUID) -> Optional[DocumentTemplateMetadata]:
        """
        Get document_template_metadata by ID
        """
        return db.query(DocumentTemplateMetadata).filter(DocumentTemplateMetadata.id == id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[DocumentTemplateMetadata]:
        """
        Get all document_template_metadata records with pagination
        """
        return db.query(DocumentTemplateMetadata).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, id: UUID, update_data: Dict[str, Any]) -> Optional[DocumentTemplateMetadata]:
        """
        Update document_template_metadata record
        """
        db_obj = db.query(DocumentTemplateMetadata).filter(DocumentTemplateMetadata.id == id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, id: UUID) -> bool:
        """
        Delete document_template_metadata record
        """
        db_obj = db.query(DocumentTemplateMetadata).filter(DocumentTemplateMetadata.id == id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[DocumentTemplateMetadata]:
        """
        Search document_template_metadata records by text content
        """
        return db.query(DocumentTemplateMetadata).filter(
            db.or_(
                DocumentTemplateMetadata.document_type.ilike(f'%{query}%'),
                DocumentTemplateMetadata.template_file_path.ilike(f'%{query}%'),
            )
        ).limit(limit).all()



class DocumentToneAnalysisCRUD:
    """
    CRUD operations for document_tone_analysis table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> DocumentToneAnalysis:
        """
        Create a new document_tone_analysis record
        """
        db_obj = DocumentToneAnalysis(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, id: UUID) -> Optional[DocumentToneAnalysis]:
        """
        Get document_tone_analysis by ID
        """
        return db.query(DocumentToneAnalysis).filter(DocumentToneAnalysis.id == id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[DocumentToneAnalysis]:
        """
        Get all document_tone_analysis records with pagination
        """
        return db.query(DocumentToneAnalysis).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, id: UUID, update_data: Dict[str, Any]) -> Optional[DocumentToneAnalysis]:
        """
        Update document_tone_analysis record
        """
        db_obj = db.query(DocumentToneAnalysis).filter(DocumentToneAnalysis.id == id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, id: UUID) -> bool:
        """
        Delete document_tone_analysis record
        """
        db_obj = db.query(DocumentToneAnalysis).filter(DocumentToneAnalysis.id == id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[DocumentToneAnalysis]:
        """
        Search document_tone_analysis records by text content
        """
        return db.query(DocumentToneAnalysis).filter(
            db.or_(
                DocumentToneAnalysis.document_type.ilike(f'%{query}%'),
            )
        ).limit(limit).all()



class ErrorLogCRUD:
    """
    CRUD operations for error_log table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> ErrorLog:
        """
        Create a new error_log record
        """
        db_obj = ErrorLog(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, id: UUID) -> Optional[ErrorLog]:
        """
        Get error_log by ID
        """
        return db.query(ErrorLog).filter(ErrorLog.id == id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[ErrorLog]:
        """
        Get all error_log records with pagination
        """
        return db.query(ErrorLog).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, id: UUID, update_data: Dict[str, Any]) -> Optional[ErrorLog]:
        """
        Update error_log record
        """
        db_obj = db.query(ErrorLog).filter(ErrorLog.id == id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, id: UUID) -> bool:
        """
        Delete error_log record
        """
        db_obj = db.query(ErrorLog).filter(ErrorLog.id == id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[ErrorLog]:
        """
        Search error_log records by text content
        """
        return db.query(ErrorLog).filter(
            db.or_(
                ErrorLog.error_id.ilike(f'%{query}%'),
                ErrorLog.session_id.ilike(f'%{query}%'),
                ErrorLog.stage_name.ilike(f'%{query}%'),
            )
        ).limit(limit).all()



class FailureLogsCRUD:
    """
    CRUD operations for failure_logs table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> FailureLogs:
        """
        Create a new failure_logs record
        """
        db_obj = FailureLogs(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, id: UUID) -> Optional[FailureLogs]:
        """
        Get failure_logs by ID
        """
        return db.query(FailureLogs).filter(FailureLogs.id == id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[FailureLogs]:
        """
        Get all failure_logs records with pagination
        """
        return db.query(FailureLogs).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, id: UUID, update_data: Dict[str, Any]) -> Optional[FailureLogs]:
        """
        Update failure_logs record
        """
        db_obj = db.query(FailureLogs).filter(FailureLogs.id == id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, id: UUID) -> bool:
        """
        Delete failure_logs record
        """
        db_obj = db.query(FailureLogs).filter(FailureLogs.id == id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[FailureLogs]:
        """
        Search failure_logs records by text content
        """
        return db.query(FailureLogs).filter(
            db.or_(
                FailureLogs.failure_type.ilike(f'%{query}%'),
                FailureLogs.operation_name.ilike(f'%{query}%'),
                FailureLogs.error_message.ilike(f'%{query}%'),
            )
        ).limit(limit).all()



class JobAnalysisQueueCRUD:
    """
    CRUD operations for job_analysis_queue table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> JobAnalysisQueue:
        """
        Create a new job_analysis_queue record
        """
        db_obj = JobAnalysisQueue(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, id: UUID) -> Optional[JobAnalysisQueue]:
        """
        Get job_analysis_queue by ID
        """
        return db.query(JobAnalysisQueue).filter(JobAnalysisQueue.id == id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[JobAnalysisQueue]:
        """
        Get all job_analysis_queue records with pagination
        """
        return db.query(JobAnalysisQueue).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, id: UUID, update_data: Dict[str, Any]) -> Optional[JobAnalysisQueue]:
        """
        Update job_analysis_queue record
        """
        db_obj = db.query(JobAnalysisQueue).filter(JobAnalysisQueue.id == id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, id: UUID) -> bool:
        """
        Delete job_analysis_queue record
        """
        db_obj = db.query(JobAnalysisQueue).filter(JobAnalysisQueue.id == id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[JobAnalysisQueue]:
        """
        Search job_analysis_queue records by text content
        """
        return db.query(JobAnalysisQueue).filter(
            db.or_(
                JobAnalysisQueue.priority.ilike(f'%{query}%'),
                JobAnalysisQueue.error_message.ilike(f'%{query}%'),
                JobAnalysisQueue.status.ilike(f'%{query}%'),
            )
        ).limit(limit).all()

    @staticmethod
    def get_by_status(db: Session, status: str) -> List[JobAnalysisQueue]:
        """
        Get job_analysis_queue records by status
        """
        return db.query(JobAnalysisQueue).filter(JobAnalysisQueue.status == status).all()



class JobAnalysisTiersCRUD:
    """
    CRUD operations for job_analysis_tiers table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> JobAnalysisTiers:
        """
        Create a new job_analysis_tiers record
        """
        db_obj = JobAnalysisTiers(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, id: UUID) -> Optional[JobAnalysisTiers]:
        """
        Get job_analysis_tiers by ID
        """
        return db.query(JobAnalysisTiers).filter(JobAnalysisTiers.id == id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[JobAnalysisTiers]:
        """
        Get all job_analysis_tiers records with pagination
        """
        return db.query(JobAnalysisTiers).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, id: UUID, update_data: Dict[str, Any]) -> Optional[JobAnalysisTiers]:
        """
        Update job_analysis_tiers record
        """
        db_obj = db.query(JobAnalysisTiers).filter(JobAnalysisTiers.id == id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, id: UUID) -> bool:
        """
        Delete job_analysis_tiers record
        """
        db_obj = db.query(JobAnalysisTiers).filter(JobAnalysisTiers.id == id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[JobAnalysisTiers]:
        """
        Search job_analysis_tiers records by text content
        """
        return db.query(JobAnalysisTiers).filter(
            db.or_(
                JobAnalysisTiers.tier_1_model.ilike(f'%{query}%'),
                JobAnalysisTiers.tier_2_model.ilike(f'%{query}%'),
                JobAnalysisTiers.tier_3_model.ilike(f'%{query}%'),
            )
        ).limit(limit).all()



class JobApplicationTrackingCRUD:
    """
    CRUD operations for job_application_tracking table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> JobApplicationTracking:
        """
        Create a new job_application_tracking record
        """
        db_obj = JobApplicationTracking(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, tracking_id: UUID) -> Optional[JobApplicationTracking]:
        """
        Get job_application_tracking by ID
        """
        return db.query(JobApplicationTracking).filter(JobApplicationTracking.tracking_id == tracking_id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[JobApplicationTracking]:
        """
        Get all job_application_tracking records with pagination
        """
        return db.query(JobApplicationTracking).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, tracking_id: UUID, update_data: Dict[str, Any]) -> Optional[JobApplicationTracking]:
        """
        Update job_application_tracking record
        """
        db_obj = db.query(JobApplicationTracking).filter(JobApplicationTracking.tracking_id == tracking_id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, tracking_id: UUID) -> bool:
        """
        Delete job_application_tracking record
        """
        db_obj = db.query(JobApplicationTracking).filter(JobApplicationTracking.tracking_id == tracking_id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[JobApplicationTracking]:
        """
        Search job_application_tracking records by text content
        """
        return db.query(JobApplicationTracking).filter(
            db.or_(
                JobApplicationTracking.tracking_type.ilike(f'%{query}%'),
                JobApplicationTracking.tracking_event.ilike(f'%{query}%'),
                JobApplicationTracking.user_agent.ilike(f'%{query}%'),
            )
        ).limit(limit).all()



class JobApplicationsCRUD:
    """
    CRUD operations for job_applications table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> JobApplications:
        """
        Create a new job_applications record
        """
        db_obj = JobApplications(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, id: UUID) -> Optional[JobApplications]:
        """
        Get job_applications by ID
        """
        return db.query(JobApplications).filter(JobApplications.id == id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[JobApplications]:
        """
        Get all job_applications records with pagination
        """
        return db.query(JobApplications).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, id: UUID, update_data: Dict[str, Any]) -> Optional[JobApplications]:
        """
        Update job_applications record
        """
        db_obj = db.query(JobApplications).filter(JobApplications.id == id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, id: UUID) -> bool:
        """
        Delete job_applications record
        """
        db_obj = db.query(JobApplications).filter(JobApplications.id == id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[JobApplications]:
        """
        Search job_applications records by text content
        """
        return db.query(JobApplications).filter(
            db.or_(
                JobApplications.application_method.ilike(f'%{query}%'),
                JobApplications.application_status.ilike(f'%{query}%'),
                JobApplications.email_sent_to.ilike(f'%{query}%'),
            )
        ).limit(limit).all()

    @staticmethod
    def get_by_status(db: Session, status: str) -> List[JobApplications]:
        """
        Get job_applications records by status
        """
        return db.query(JobApplications).filter(JobApplications.application_status == status).all()



class JobAtsKeywordsCRUD:
    """
    CRUD operations for job_ats_keywords table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> JobAtsKeywords:
        """
        Create a new job_ats_keywords record
        """
        db_obj = JobAtsKeywords(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, id: UUID) -> Optional[JobAtsKeywords]:
        """
        Get job_ats_keywords by ID
        """
        return db.query(JobAtsKeywords).filter(JobAtsKeywords.id == id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[JobAtsKeywords]:
        """
        Get all job_ats_keywords records with pagination
        """
        return db.query(JobAtsKeywords).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, id: UUID, update_data: Dict[str, Any]) -> Optional[JobAtsKeywords]:
        """
        Update job_ats_keywords record
        """
        db_obj = db.query(JobAtsKeywords).filter(JobAtsKeywords.id == id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, id: UUID) -> bool:
        """
        Delete job_ats_keywords record
        """
        db_obj = db.query(JobAtsKeywords).filter(JobAtsKeywords.id == id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[JobAtsKeywords]:
        """
        Search job_ats_keywords records by text content
        """
        return db.query(JobAtsKeywords).filter(
            db.or_(
                JobAtsKeywords.keyword.ilike(f'%{query}%'),
                JobAtsKeywords.keyword_category.ilike(f'%{query}%'),
            )
        ).limit(limit).all()



class JobBenefitsCRUD:
    """
    CRUD operations for job_benefits table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> JobBenefits:
        """
        Create a new job_benefits record
        """
        db_obj = JobBenefits(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, benefit_id: UUID) -> Optional[JobBenefits]:
        """
        Get job_benefits by ID
        """
        return db.query(JobBenefits).filter(JobBenefits.benefit_id == benefit_id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[JobBenefits]:
        """
        Get all job_benefits records with pagination
        """
        return db.query(JobBenefits).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, benefit_id: UUID, update_data: Dict[str, Any]) -> Optional[JobBenefits]:
        """
        Update job_benefits record
        """
        db_obj = db.query(JobBenefits).filter(JobBenefits.benefit_id == benefit_id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, benefit_id: UUID) -> bool:
        """
        Delete job_benefits record
        """
        db_obj = db.query(JobBenefits).filter(JobBenefits.benefit_id == benefit_id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[JobBenefits]:
        """
        Search job_benefits records by text content
        """
        return db.query(JobBenefits).filter(
            db.or_(
                JobBenefits.benefit_type.ilike(f'%{query}%'),
                JobBenefits.benefit_description.ilike(f'%{query}%'),
                JobBenefits.benefit_value.ilike(f'%{query}%'),
            )
        ).limit(limit).all()



class JobCertificationsCRUD:
    """
    CRUD operations for job_certifications table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> JobCertifications:
        """
        Create a new job_certifications record
        """
        db_obj = JobCertifications(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, id: UUID) -> Optional[JobCertifications]:
        """
        Get job_certifications by ID
        """
        return db.query(JobCertifications).filter(JobCertifications.id == id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[JobCertifications]:
        """
        Get all job_certifications records with pagination
        """
        return db.query(JobCertifications).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, id: UUID, update_data: Dict[str, Any]) -> Optional[JobCertifications]:
        """
        Update job_certifications record
        """
        db_obj = db.query(JobCertifications).filter(JobCertifications.id == id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, id: UUID) -> bool:
        """
        Delete job_certifications record
        """
        db_obj = db.query(JobCertifications).filter(JobCertifications.id == id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[JobCertifications]:
        """
        Search job_certifications records by text content
        """
        return db.query(JobCertifications).filter(
            db.or_(
                JobCertifications.certification_name.ilike(f'%{query}%'),
            )
        ).limit(limit).all()



class JobEducationRequirementsCRUD:
    """
    CRUD operations for job_education_requirements table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> JobEducationRequirements:
        """
        Create a new job_education_requirements record
        """
        db_obj = JobEducationRequirements(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, id: UUID) -> Optional[JobEducationRequirements]:
        """
        Get job_education_requirements by ID
        """
        return db.query(JobEducationRequirements).filter(JobEducationRequirements.id == id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[JobEducationRequirements]:
        """
        Get all job_education_requirements records with pagination
        """
        return db.query(JobEducationRequirements).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, id: UUID, update_data: Dict[str, Any]) -> Optional[JobEducationRequirements]:
        """
        Update job_education_requirements record
        """
        db_obj = db.query(JobEducationRequirements).filter(JobEducationRequirements.id == id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, id: UUID) -> bool:
        """
        Delete job_education_requirements record
        """
        db_obj = db.query(JobEducationRequirements).filter(JobEducationRequirements.id == id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[JobEducationRequirements]:
        """
        Search job_education_requirements records by text content
        """
        return db.query(JobEducationRequirements).filter(
            db.or_(
                JobEducationRequirements.degree_level.ilike(f'%{query}%'),
                JobEducationRequirements.field_of_study.ilike(f'%{query}%'),
                JobEducationRequirements.institution_type.ilike(f'%{query}%'),
            )
        ).limit(limit).all()



class JobLogsCRUD:
    """
    CRUD operations for job_logs table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> JobLogs:
        """
        Create a new job_logs record
        """
        db_obj = JobLogs(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, log_id: UUID) -> Optional[JobLogs]:
        """
        Get job_logs by ID
        """
        return db.query(JobLogs).filter(JobLogs.log_id == log_id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[JobLogs]:
        """
        Get all job_logs records with pagination
        """
        return db.query(JobLogs).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, log_id: UUID, update_data: Dict[str, Any]) -> Optional[JobLogs]:
        """
        Update job_logs record
        """
        db_obj = db.query(JobLogs).filter(JobLogs.log_id == log_id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, log_id: UUID) -> bool:
        """
        Delete job_logs record
        """
        db_obj = db.query(JobLogs).filter(JobLogs.log_id == log_id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[JobLogs]:
        """
        Search job_logs records by text content
        """
        return db.query(JobLogs).filter(
            db.or_(
                JobLogs.log_level.ilike(f'%{query}%'),
                JobLogs.message.ilike(f'%{query}%'),
            )
        ).limit(limit).all()



class JobPlatformsFoundCRUD:
    """
    CRUD operations for job_platforms_found table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> JobPlatformsFound:
        """
        Create a new job_platforms_found record
        """
        db_obj = JobPlatformsFound(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, platform_id: UUID) -> Optional[JobPlatformsFound]:
        """
        Get job_platforms_found by ID
        """
        return db.query(JobPlatformsFound).filter(JobPlatformsFound.platform_id == platform_id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[JobPlatformsFound]:
        """
        Get all job_platforms_found records with pagination
        """
        return db.query(JobPlatformsFound).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, platform_id: UUID, update_data: Dict[str, Any]) -> Optional[JobPlatformsFound]:
        """
        Update job_platforms_found record
        """
        db_obj = db.query(JobPlatformsFound).filter(JobPlatformsFound.platform_id == platform_id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, platform_id: UUID) -> bool:
        """
        Delete job_platforms_found record
        """
        db_obj = db.query(JobPlatformsFound).filter(JobPlatformsFound.platform_id == platform_id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[JobPlatformsFound]:
        """
        Search job_platforms_found records by text content
        """
        return db.query(JobPlatformsFound).filter(
            db.or_(
                JobPlatformsFound.platform_name.ilike(f'%{query}%'),
                JobPlatformsFound.platform_url.ilike(f'%{query}%'),
            )
        ).limit(limit).all()



class JobRedFlagsDetailsCRUD:
    """
    CRUD operations for job_red_flags_details table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> JobRedFlagsDetails:
        """
        Create a new job_red_flags_details record
        """
        db_obj = JobRedFlagsDetails(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, id: UUID) -> Optional[JobRedFlagsDetails]:
        """
        Get job_red_flags_details by ID
        """
        return db.query(JobRedFlagsDetails).filter(JobRedFlagsDetails.id == id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[JobRedFlagsDetails]:
        """
        Get all job_red_flags_details records with pagination
        """
        return db.query(JobRedFlagsDetails).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, id: UUID, update_data: Dict[str, Any]) -> Optional[JobRedFlagsDetails]:
        """
        Update job_red_flags_details record
        """
        db_obj = db.query(JobRedFlagsDetails).filter(JobRedFlagsDetails.id == id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, id: UUID) -> bool:
        """
        Delete job_red_flags_details record
        """
        db_obj = db.query(JobRedFlagsDetails).filter(JobRedFlagsDetails.id == id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[JobRedFlagsDetails]:
        """
        Search job_red_flags_details records by text content
        """
        return db.query(JobRedFlagsDetails).filter(
            db.or_(
                JobRedFlagsDetails.flag_type.ilike(f'%{query}%'),
                JobRedFlagsDetails.details.ilike(f'%{query}%'),
            )
        ).limit(limit).all()



class JobRequiredDocumentsCRUD:
    """
    CRUD operations for job_required_documents table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> JobRequiredDocuments:
        """
        Create a new job_required_documents record
        """
        db_obj = JobRequiredDocuments(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, id: UUID) -> Optional[JobRequiredDocuments]:
        """
        Get job_required_documents by ID
        """
        return db.query(JobRequiredDocuments).filter(JobRequiredDocuments.id == id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[JobRequiredDocuments]:
        """
        Get all job_required_documents records with pagination
        """
        return db.query(JobRequiredDocuments).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, id: UUID, update_data: Dict[str, Any]) -> Optional[JobRequiredDocuments]:
        """
        Update job_required_documents record
        """
        db_obj = db.query(JobRequiredDocuments).filter(JobRequiredDocuments.id == id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, id: UUID) -> bool:
        """
        Delete job_required_documents record
        """
        db_obj = db.query(JobRequiredDocuments).filter(JobRequiredDocuments.id == id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[JobRequiredDocuments]:
        """
        Search job_required_documents records by text content
        """
        return db.query(JobRequiredDocuments).filter(
            db.or_(
                JobRequiredDocuments.document_type.ilike(f'%{query}%'),
            )
        ).limit(limit).all()



class JobRequiredSkillsCRUD:
    """
    CRUD operations for job_required_skills table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> JobRequiredSkills:
        """
        Create a new job_required_skills record
        """
        db_obj = JobRequiredSkills(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, skill_id: UUID) -> Optional[JobRequiredSkills]:
        """
        Get job_required_skills by ID
        """
        return db.query(JobRequiredSkills).filter(JobRequiredSkills.skill_id == skill_id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[JobRequiredSkills]:
        """
        Get all job_required_skills records with pagination
        """
        return db.query(JobRequiredSkills).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, skill_id: UUID, update_data: Dict[str, Any]) -> Optional[JobRequiredSkills]:
        """
        Update job_required_skills record
        """
        db_obj = db.query(JobRequiredSkills).filter(JobRequiredSkills.skill_id == skill_id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, skill_id: UUID) -> bool:
        """
        Delete job_required_skills record
        """
        db_obj = db.query(JobRequiredSkills).filter(JobRequiredSkills.skill_id == skill_id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[JobRequiredSkills]:
        """
        Search job_required_skills records by text content
        """
        return db.query(JobRequiredSkills).filter(
            db.or_(
                JobRequiredSkills.skill_name.ilike(f'%{query}%'),
                JobRequiredSkills.skill_level.ilike(f'%{query}%'),
            )
        ).limit(limit).all()



class JobSkillsCRUD:
    """
    CRUD operations for job_skills table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> JobSkills:
        """
        Create a new job_skills record
        """
        db_obj = JobSkills(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, skill_id: UUID) -> Optional[JobSkills]:
        """
        Get job_skills by ID
        """
        return db.query(JobSkills).filter(JobSkills.skill_id == skill_id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[JobSkills]:
        """
        Get all job_skills records with pagination
        """
        return db.query(JobSkills).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, skill_id: UUID, update_data: Dict[str, Any]) -> Optional[JobSkills]:
        """
        Update job_skills record
        """
        db_obj = db.query(JobSkills).filter(JobSkills.skill_id == skill_id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, skill_id: UUID) -> bool:
        """
        Delete job_skills record
        """
        db_obj = db.query(JobSkills).filter(JobSkills.skill_id == skill_id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[JobSkills]:
        """
        Search job_skills records by text content
        """
        return db.query(JobSkills).filter(
            db.or_(
                JobSkills.skill_name.ilike(f'%{query}%'),
                JobSkills.reasoning.ilike(f'%{query}%'),
            )
        ).limit(limit).all()



class JobStressIndicatorsCRUD:
    """
    CRUD operations for job_stress_indicators table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> JobStressIndicators:
        """
        Create a new job_stress_indicators record
        """
        db_obj = JobStressIndicators(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, id: UUID) -> Optional[JobStressIndicators]:
        """
        Get job_stress_indicators by ID
        """
        return db.query(JobStressIndicators).filter(JobStressIndicators.id == id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[JobStressIndicators]:
        """
        Get all job_stress_indicators records with pagination
        """
        return db.query(JobStressIndicators).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, id: UUID, update_data: Dict[str, Any]) -> Optional[JobStressIndicators]:
        """
        Update job_stress_indicators record
        """
        db_obj = db.query(JobStressIndicators).filter(JobStressIndicators.id == id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, id: UUID) -> bool:
        """
        Delete job_stress_indicators record
        """
        db_obj = db.query(JobStressIndicators).filter(JobStressIndicators.id == id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[JobStressIndicators]:
        """
        Search job_stress_indicators records by text content
        """
        return db.query(JobStressIndicators).filter(
            db.or_(
                JobStressIndicators.indicator.ilike(f'%{query}%'),
                JobStressIndicators.description.ilike(f'%{query}%'),
            )
        ).limit(limit).all()



class JobsCRUD:
    """
    CRUD operations for jobs table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> Jobs:
        """
        Create a new jobs record
        """
        db_obj = Jobs(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, id: UUID) -> Optional[Jobs]:
        """
        Get jobs by ID
        """
        return db.query(Jobs).filter(Jobs.id == id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Jobs]:
        """
        Get all jobs records with pagination
        """
        return db.query(Jobs).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, id: UUID, update_data: Dict[str, Any]) -> Optional[Jobs]:
        """
        Update jobs record
        """
        db_obj = db.query(Jobs).filter(Jobs.id == id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, id: UUID) -> bool:
        """
        Delete jobs record
        """
        db_obj = db.query(Jobs).filter(Jobs.id == id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[Jobs]:
        """
        Search jobs records by text content
        """
        return db.query(Jobs).filter(
            db.or_(
                Jobs.job_title.ilike(f'%{query}%'),
                Jobs.job_description.ilike(f'%{query}%'),
                Jobs.job_number.ilike(f'%{query}%'),
            )
        ).limit(limit).all()

    @staticmethod
    def get_by_status(db: Session, status: str) -> List[Jobs]:
        """
        Get jobs records by status
        """
        return db.query(Jobs).filter(Jobs.application_status == status).all()



class KeywordFiltersCRUD:
    """
    CRUD operations for keyword_filters table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> KeywordFilters:
        """
        Create a new keyword_filters record
        """
        db_obj = KeywordFilters(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, id: UUID) -> Optional[KeywordFilters]:
        """
        Get keyword_filters by ID
        """
        return db.query(KeywordFilters).filter(KeywordFilters.id == id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[KeywordFilters]:
        """
        Get all keyword_filters records with pagination
        """
        return db.query(KeywordFilters).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, id: UUID, update_data: Dict[str, Any]) -> Optional[KeywordFilters]:
        """
        Update keyword_filters record
        """
        db_obj = db.query(KeywordFilters).filter(KeywordFilters.id == id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, id: UUID) -> bool:
        """
        Delete keyword_filters record
        """
        db_obj = db.query(KeywordFilters).filter(KeywordFilters.id == id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[KeywordFilters]:
        """
        Search keyword_filters records by text content
        """
        return db.query(KeywordFilters).filter(
            db.or_(
                KeywordFilters.keyword.ilike(f'%{query}%'),
                KeywordFilters.status.ilike(f'%{query}%'),
            )
        ).limit(limit).all()

    @staticmethod
    def get_by_status(db: Session, status: str) -> List[KeywordFilters]:
        """
        Get keyword_filters records by status
        """
        return db.query(KeywordFilters).filter(KeywordFilters.status == status).all()



class LinkClicksCRUD:
    """
    CRUD operations for link_clicks table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> LinkClicks:
        """
        Create a new link_clicks record
        """
        db_obj = LinkClicks(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, click_id: UUID) -> Optional[LinkClicks]:
        """
        Get link_clicks by ID
        """
        return db.query(LinkClicks).filter(LinkClicks.click_id == click_id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[LinkClicks]:
        """
        Get all link_clicks records with pagination
        """
        return db.query(LinkClicks).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, click_id: UUID, update_data: Dict[str, Any]) -> Optional[LinkClicks]:
        """
        Update link_clicks record
        """
        db_obj = db.query(LinkClicks).filter(LinkClicks.click_id == click_id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, click_id: UUID) -> bool:
        """
        Delete link_clicks record
        """
        db_obj = db.query(LinkClicks).filter(LinkClicks.click_id == click_id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[LinkClicks]:
        """
        Search link_clicks records by text content
        """
        return db.query(LinkClicks).filter(
            db.or_(
                LinkClicks.tracking_id.ilike(f'%{query}%'),
                LinkClicks.user_agent.ilike(f'%{query}%'),
                LinkClicks.referrer_url.ilike(f'%{query}%'),
            )
        ).limit(limit).all()



class LinkTrackingCRUD:
    """
    CRUD operations for link_tracking table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> LinkTracking:
        """
        Create a new link_tracking record
        """
        db_obj = LinkTracking(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, tracking_id: UUID) -> Optional[LinkTracking]:
        """
        Get link_tracking by ID
        """
        return db.query(LinkTracking).filter(LinkTracking.tracking_id == tracking_id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[LinkTracking]:
        """
        Get all link_tracking records with pagination
        """
        return db.query(LinkTracking).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, tracking_id: UUID, update_data: Dict[str, Any]) -> Optional[LinkTracking]:
        """
        Update link_tracking record
        """
        db_obj = db.query(LinkTracking).filter(LinkTracking.tracking_id == tracking_id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, tracking_id: UUID) -> bool:
        """
        Delete link_tracking record
        """
        db_obj = db.query(LinkTracking).filter(LinkTracking.tracking_id == tracking_id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[LinkTracking]:
        """
        Search link_tracking records by text content
        """
        return db.query(LinkTracking).filter(
            db.or_(
                LinkTracking.tracking_id.ilike(f'%{query}%'),
                LinkTracking.link_function.ilike(f'%{query}%'),
                LinkTracking.link_type.ilike(f'%{query}%'),
            )
        ).limit(limit).all()



class PerformanceMetricsCRUD:
    """
    CRUD operations for performance_metrics table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> PerformanceMetrics:
        """
        Create a new performance_metrics record
        """
        db_obj = PerformanceMetrics(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, id: UUID) -> Optional[PerformanceMetrics]:
        """
        Get performance_metrics by ID
        """
        return db.query(PerformanceMetrics).filter(PerformanceMetrics.id == id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[PerformanceMetrics]:
        """
        Get all performance_metrics records with pagination
        """
        return db.query(PerformanceMetrics).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, id: UUID, update_data: Dict[str, Any]) -> Optional[PerformanceMetrics]:
        """
        Update performance_metrics record
        """
        db_obj = db.query(PerformanceMetrics).filter(PerformanceMetrics.id == id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, id: UUID) -> bool:
        """
        Delete performance_metrics record
        """
        db_obj = db.query(PerformanceMetrics).filter(PerformanceMetrics.id == id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[PerformanceMetrics]:
        """
        Search performance_metrics records by text content
        """
        return db.query(PerformanceMetrics).filter(
            db.or_(
                PerformanceMetrics.stage_name.ilike(f'%{query}%'),
                PerformanceMetrics.api_call_type.ilike(f'%{query}%'),
                PerformanceMetrics.error_message.ilike(f'%{query}%'),
            )
        ).limit(limit).all()



class PreAnalyzedJobsCRUD:
    """
    CRUD operations for pre_analyzed_jobs table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> PreAnalyzedJobs:
        """
        Create a new pre_analyzed_jobs record
        """
        db_obj = PreAnalyzedJobs(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, id: UUID) -> Optional[PreAnalyzedJobs]:
        """
        Get pre_analyzed_jobs by ID
        """
        return db.query(PreAnalyzedJobs).filter(PreAnalyzedJobs.id == id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[PreAnalyzedJobs]:
        """
        Get all pre_analyzed_jobs records with pagination
        """
        return db.query(PreAnalyzedJobs).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, id: UUID, update_data: Dict[str, Any]) -> Optional[PreAnalyzedJobs]:
        """
        Update pre_analyzed_jobs record
        """
        db_obj = db.query(PreAnalyzedJobs).filter(PreAnalyzedJobs.id == id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, id: UUID) -> bool:
        """
        Delete pre_analyzed_jobs record
        """
        db_obj = db.query(PreAnalyzedJobs).filter(PreAnalyzedJobs.id == id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[PreAnalyzedJobs]:
        """
        Search pre_analyzed_jobs records by text content
        """
        return db.query(PreAnalyzedJobs).filter(
            db.or_(
                PreAnalyzedJobs.job_title.ilike(f'%{query}%'),
                PreAnalyzedJobs.company_name.ilike(f'%{query}%'),
                PreAnalyzedJobs.location_city.ilike(f'%{query}%'),
            )
        ).limit(limit).all()



class RawJobScrapesCRUD:
    """
    CRUD operations for raw_job_scrapes table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> RawJobScrapes:
        """
        Create a new raw_job_scrapes record
        """
        db_obj = RawJobScrapes(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, scrape_id: UUID) -> Optional[RawJobScrapes]:
        """
        Get raw_job_scrapes by ID
        """
        return db.query(RawJobScrapes).filter(RawJobScrapes.scrape_id == scrape_id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[RawJobScrapes]:
        """
        Get all raw_job_scrapes records with pagination
        """
        return db.query(RawJobScrapes).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, scrape_id: UUID, update_data: Dict[str, Any]) -> Optional[RawJobScrapes]:
        """
        Update raw_job_scrapes record
        """
        db_obj = db.query(RawJobScrapes).filter(RawJobScrapes.scrape_id == scrape_id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, scrape_id: UUID) -> bool:
        """
        Delete raw_job_scrapes record
        """
        db_obj = db.query(RawJobScrapes).filter(RawJobScrapes.scrape_id == scrape_id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[RawJobScrapes]:
        """
        Search raw_job_scrapes records by text content
        """
        return db.query(RawJobScrapes).filter(
            db.or_(
                RawJobScrapes.source_website.ilike(f'%{query}%'),
                RawJobScrapes.source_url.ilike(f'%{query}%'),
                RawJobScrapes.full_application_url.ilike(f'%{query}%'),
            )
        ).limit(limit).all()

    @staticmethod
    def get_by_status(db: Session, status: str) -> List[RawJobScrapes]:
        """
        Get raw_job_scrapes records by status
        """
        return db.query(RawJobScrapes).filter(RawJobScrapes.success_status == status).all()



class RecoveryStatisticsCRUD:
    """
    CRUD operations for recovery_statistics table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> RecoveryStatistics:
        """
        Create a new recovery_statistics record
        """
        db_obj = RecoveryStatistics(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, id: UUID) -> Optional[RecoveryStatistics]:
        """
        Get recovery_statistics by ID
        """
        return db.query(RecoveryStatistics).filter(RecoveryStatistics.id == id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[RecoveryStatistics]:
        """
        Get all recovery_statistics records with pagination
        """
        return db.query(RecoveryStatistics).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, id: UUID, update_data: Dict[str, Any]) -> Optional[RecoveryStatistics]:
        """
        Update recovery_statistics record
        """
        db_obj = db.query(RecoveryStatistics).filter(RecoveryStatistics.id == id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, id: UUID) -> bool:
        """
        Delete recovery_statistics record
        """
        db_obj = db.query(RecoveryStatistics).filter(RecoveryStatistics.id == id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[RecoveryStatistics]:
        """
        Search recovery_statistics records by text content
        """
        return db.query(RecoveryStatistics).filter(
            db.or_(
                RecoveryStatistics.failure_type.ilike(f'%{query}%'),
            )
        ).limit(limit).all()



class SecurityDetectionsCRUD:
    """
    CRUD operations for security_detections table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> SecurityDetections:
        """
        Create a new security_detections record
        """
        db_obj = SecurityDetections(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, id: UUID) -> Optional[SecurityDetections]:
        """
        Get security_detections by ID
        """
        return db.query(SecurityDetections).filter(SecurityDetections.id == id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[SecurityDetections]:
        """
        Get all security_detections records with pagination
        """
        return db.query(SecurityDetections).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, id: UUID, update_data: Dict[str, Any]) -> Optional[SecurityDetections]:
        """
        Update security_detections record
        """
        db_obj = db.query(SecurityDetections).filter(SecurityDetections.id == id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, id: UUID) -> bool:
        """
        Delete security_detections record
        """
        db_obj = db.query(SecurityDetections).filter(SecurityDetections.id == id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[SecurityDetections]:
        """
        Search security_detections records by text content
        """
        return db.query(SecurityDetections).filter(
            db.or_(
                SecurityDetections.detection_type.ilike(f'%{query}%'),
                SecurityDetections.severity.ilike(f'%{query}%'),
                SecurityDetections.pattern_matched.ilike(f'%{query}%'),
            )
        ).limit(limit).all()



class SecurityTestTableCRUD:
    """
    CRUD operations for security_test_table table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> SecurityTestTable:
        """
        Create a new security_test_table record
        """
        db_obj = SecurityTestTable(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[SecurityTestTable]:
        """
        Get all security_test_table records with pagination
        """
        return db.query(SecurityTestTable).offset(skip).limit(limit).all()



class SentenceBankCoverLetterCRUD:
    """
    CRUD operations for sentence_bank_cover_letter table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> SentenceBankCoverLetter:
        """
        Create a new sentence_bank_cover_letter record
        """
        db_obj = SentenceBankCoverLetter(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, id: UUID) -> Optional[SentenceBankCoverLetter]:
        """
        Get sentence_bank_cover_letter by ID
        """
        return db.query(SentenceBankCoverLetter).filter(SentenceBankCoverLetter.id == id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[SentenceBankCoverLetter]:
        """
        Get all sentence_bank_cover_letter records with pagination
        """
        return db.query(SentenceBankCoverLetter).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, id: UUID, update_data: Dict[str, Any]) -> Optional[SentenceBankCoverLetter]:
        """
        Update sentence_bank_cover_letter record
        """
        db_obj = db.query(SentenceBankCoverLetter).filter(SentenceBankCoverLetter.id == id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, id: UUID) -> bool:
        """
        Delete sentence_bank_cover_letter record
        """
        db_obj = db.query(SentenceBankCoverLetter).filter(SentenceBankCoverLetter.id == id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[SentenceBankCoverLetter]:
        """
        Search sentence_bank_cover_letter records by text content
        """
        return db.query(SentenceBankCoverLetter).filter(
            db.or_(
                SentenceBankCoverLetter.content_text.ilike(f'%{query}%'),
                SentenceBankCoverLetter.tone.ilike(f'%{query}%'),
                SentenceBankCoverLetter.status.ilike(f'%{query}%'),
            )
        ).limit(limit).all()

    @staticmethod
    def get_by_status(db: Session, status: str) -> List[SentenceBankCoverLetter]:
        """
        Get sentence_bank_cover_letter records by status
        """
        return db.query(SentenceBankCoverLetter).filter(SentenceBankCoverLetter.status == status).all()



class SentenceBankResumeCRUD:
    """
    CRUD operations for sentence_bank_resume table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> SentenceBankResume:
        """
        Create a new sentence_bank_resume record
        """
        db_obj = SentenceBankResume(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, id: UUID) -> Optional[SentenceBankResume]:
        """
        Get sentence_bank_resume by ID
        """
        return db.query(SentenceBankResume).filter(SentenceBankResume.id == id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[SentenceBankResume]:
        """
        Get all sentence_bank_resume records with pagination
        """
        return db.query(SentenceBankResume).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, id: UUID, update_data: Dict[str, Any]) -> Optional[SentenceBankResume]:
        """
        Update sentence_bank_resume record
        """
        db_obj = db.query(SentenceBankResume).filter(SentenceBankResume.id == id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, id: UUID) -> bool:
        """
        Delete sentence_bank_resume record
        """
        db_obj = db.query(SentenceBankResume).filter(SentenceBankResume.id == id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[SentenceBankResume]:
        """
        Search sentence_bank_resume records by text content
        """
        return db.query(SentenceBankResume).filter(
            db.or_(
                SentenceBankResume.content_text.ilike(f'%{query}%'),
                SentenceBankResume.body_section.ilike(f'%{query}%'),
                SentenceBankResume.tone.ilike(f'%{query}%'),
            )
        ).limit(limit).all()

    @staticmethod
    def get_by_status(db: Session, status: str) -> List[SentenceBankResume]:
        """
        Get sentence_bank_resume records by status
        """
        return db.query(SentenceBankResume).filter(SentenceBankResume.status == status).all()



class UserCandidateInfoCRUD:
    """
    CRUD operations for user_candidate_info table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> UserCandidateInfo:
        """
        Create a new user_candidate_info record
        """
        db_obj = UserCandidateInfo(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, id: UUID) -> Optional[UserCandidateInfo]:
        """
        Get user_candidate_info by ID
        """
        return db.query(UserCandidateInfo).filter(UserCandidateInfo.id == id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[UserCandidateInfo]:
        """
        Get all user_candidate_info records with pagination
        """
        return db.query(UserCandidateInfo).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, id: UUID, update_data: Dict[str, Any]) -> Optional[UserCandidateInfo]:
        """
        Update user_candidate_info record
        """
        db_obj = db.query(UserCandidateInfo).filter(UserCandidateInfo.id == id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, id: UUID) -> bool:
        """
        Delete user_candidate_info record
        """
        db_obj = db.query(UserCandidateInfo).filter(UserCandidateInfo.id == id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[UserCandidateInfo]:
        """
        Search user_candidate_info records by text content
        """
        return db.query(UserCandidateInfo).filter(
            db.or_(
                UserCandidateInfo.first_name.ilike(f'%{query}%'),
                UserCandidateInfo.last_name.ilike(f'%{query}%'),
                UserCandidateInfo.email.ilike(f'%{query}%'),
            )
        ).limit(limit).all()



class UserJobPreferencesCRUD:
    """
    CRUD operations for user_job_preferences table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> UserJobPreferences:
        """
        Create a new user_job_preferences record
        """
        db_obj = UserJobPreferences(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, id: UUID) -> Optional[UserJobPreferences]:
        """
        Get user_job_preferences by ID
        """
        return db.query(UserJobPreferences).filter(UserJobPreferences.id == id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[UserJobPreferences]:
        """
        Get all user_job_preferences records with pagination
        """
        return db.query(UserJobPreferences).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, id: UUID, update_data: Dict[str, Any]) -> Optional[UserJobPreferences]:
        """
        Update user_job_preferences record
        """
        db_obj = db.query(UserJobPreferences).filter(UserJobPreferences.id == id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, id: UUID) -> bool:
        """
        Delete user_job_preferences record
        """
        db_obj = db.query(UserJobPreferences).filter(UserJobPreferences.id == id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[UserJobPreferences]:
        """
        Search user_job_preferences records by text content
        """
        return db.query(UserJobPreferences).filter(
            db.or_(
                UserJobPreferences.work_arrangement.ilike(f'%{query}%'),
                UserJobPreferences.preferred_city.ilike(f'%{query}%'),
                UserJobPreferences.preferred_province_state.ilike(f'%{query}%'),
            )
        ).limit(limit).all()



class UserPreferencePackagesCRUD:
    """
    CRUD operations for user_preference_packages table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> UserPreferencePackages:
        """
        Create a new user_preference_packages record
        """
        db_obj = UserPreferencePackages(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, package_id: UUID) -> Optional[UserPreferencePackages]:
        """
        Get user_preference_packages by ID
        """
        return db.query(UserPreferencePackages).filter(UserPreferencePackages.package_id == package_id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[UserPreferencePackages]:
        """
        Get all user_preference_packages records with pagination
        """
        return db.query(UserPreferencePackages).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, package_id: UUID, update_data: Dict[str, Any]) -> Optional[UserPreferencePackages]:
        """
        Update user_preference_packages record
        """
        db_obj = db.query(UserPreferencePackages).filter(UserPreferencePackages.package_id == package_id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, package_id: UUID) -> bool:
        """
        Delete user_preference_packages record
        """
        db_obj = db.query(UserPreferencePackages).filter(UserPreferencePackages.package_id == package_id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[UserPreferencePackages]:
        """
        Search user_preference_packages records by text content
        """
        return db.query(UserPreferencePackages).filter(
            db.or_(
                UserPreferencePackages.package_name.ilike(f'%{query}%'),
                UserPreferencePackages.package_description.ilike(f'%{query}%'),
                UserPreferencePackages.location_priority.ilike(f'%{query}%'),
            )
        ).limit(limit).all()



class UserPreferredIndustriesCRUD:
    """
    CRUD operations for user_preferred_industries table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> UserPreferredIndustries:
        """
        Create a new user_preferred_industries record
        """
        db_obj = UserPreferredIndustries(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, preference_id: UUID) -> Optional[UserPreferredIndustries]:
        """
        Get user_preferred_industries by ID
        """
        return db.query(UserPreferredIndustries).filter(UserPreferredIndustries.preference_id == preference_id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[UserPreferredIndustries]:
        """
        Get all user_preferred_industries records with pagination
        """
        return db.query(UserPreferredIndustries).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, preference_id: UUID, update_data: Dict[str, Any]) -> Optional[UserPreferredIndustries]:
        """
        Update user_preferred_industries record
        """
        db_obj = db.query(UserPreferredIndustries).filter(UserPreferredIndustries.preference_id == preference_id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, preference_id: UUID) -> bool:
        """
        Delete user_preferred_industries record
        """
        db_obj = db.query(UserPreferredIndustries).filter(UserPreferredIndustries.preference_id == preference_id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[UserPreferredIndustries]:
        """
        Search user_preferred_industries records by text content
        """
        return db.query(UserPreferredIndustries).filter(
            db.or_(
                UserPreferredIndustries.industry_name.ilike(f'%{query}%'),
                UserPreferredIndustries.preference_type.ilike(f'%{query}%'),
            )
        ).limit(limit).all()



class WorkExperiencesCRUD:
    """
    CRUD operations for work_experiences table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> WorkExperiences:
        """
        Create a new work_experiences record
        """
        db_obj = WorkExperiences(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, id: UUID) -> Optional[WorkExperiences]:
        """
        Get work_experiences by ID
        """
        return db.query(WorkExperiences).filter(WorkExperiences.id == id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[WorkExperiences]:
        """
        Get all work_experiences records with pagination
        """
        return db.query(WorkExperiences).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, id: UUID, update_data: Dict[str, Any]) -> Optional[WorkExperiences]:
        """
        Update work_experiences record
        """
        db_obj = db.query(WorkExperiences).filter(WorkExperiences.id == id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, id: UUID) -> bool:
        """
        Delete work_experiences record
        """
        db_obj = db.query(WorkExperiences).filter(WorkExperiences.id == id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[WorkExperiences]:
        """
        Search work_experiences records by text content
        """
        return db.query(WorkExperiences).filter(
            db.or_(
                WorkExperiences.company_name.ilike(f'%{query}%'),
                WorkExperiences.job_title.ilike(f'%{query}%'),
                WorkExperiences.location.ilike(f'%{query}%'),
            )
        ).limit(limit).all()



class WorkflowCheckpointsCRUD:
    """
    CRUD operations for workflow_checkpoints table
    """

    @staticmethod
    def create(db: Session, obj_data: Dict[str, Any]) -> WorkflowCheckpoints:
        """
        Create a new workflow_checkpoints record
        """
        db_obj = WorkflowCheckpoints(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, id: UUID) -> Optional[WorkflowCheckpoints]:
        """
        Get workflow_checkpoints by ID
        """
        return db.query(WorkflowCheckpoints).filter(WorkflowCheckpoints.id == id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[WorkflowCheckpoints]:
        """
        Get all workflow_checkpoints records with pagination
        """
        return db.query(WorkflowCheckpoints).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, id: UUID, update_data: Dict[str, Any]) -> Optional[WorkflowCheckpoints]:
        """
        Update workflow_checkpoints record
        """
        db_obj = db.query(WorkflowCheckpoints).filter(WorkflowCheckpoints.id == id).first()
        if db_obj:
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, id: UUID) -> bool:
        """
        Delete workflow_checkpoints record
        """
        db_obj = db.query(WorkflowCheckpoints).filter(WorkflowCheckpoints.id == id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def search(db: Session, query: str, limit: int = 50) -> List[WorkflowCheckpoints]:
        """
        Search workflow_checkpoints records by text content
        """
        return db.query(WorkflowCheckpoints).filter(
            db.or_(
                WorkflowCheckpoints.checkpoint_id.ilike(f'%{query}%'),
                WorkflowCheckpoints.stage.ilike(f'%{query}%'),
            )
        ).limit(limit).all()



