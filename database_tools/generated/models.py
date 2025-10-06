"""
Auto-generated SQLAlchemy Models
Generated from database schema on 2025-09-12 13:08:25
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Date, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, date
from typing import Dict, Any, List, Optional
import uuid

Base = declarative_base()

class AnalyzedJobs(Base):
    __tablename__ = "analyzed_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    pre_analyzed_job_id = Column(UUID(as_uuid=True))
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id'))
    job_title = Column(String(None), nullable=False)
    job_description = Column(Text)
    job_number = Column(String(None))
    salary_low = Column(Integer)
    salary_high = Column(Integer)
    salary_period = Column(String(None))
    compensation_currency = Column(String(None))
    equity_stock_options = Column(Boolean)
    commission_or_performance_incentive = Column(Text)
    est_total_compensation = Column(Text)
    remote_options = Column(String(None))
    job_type = Column(String(None))
    in_office_requirements = Column(String(None))
    office_address = Column(Text)
    office_city = Column(String(None))
    office_province = Column(String(None))
    office_country = Column(String(None))
    working_hours_per_week = Column(Integer)
    work_schedule = Column(Text)
    specific_schedule = Column(Text)
    travel_requirements = Column(Text)
    is_supervisor = Column(Boolean)
    department = Column(String(None))
    industry = Column(String(None))
    sub_industry = Column(String(None))
    job_function = Column(String(None))
    seniority_level = Column(String(None))
    supervision_count = Column(Integer)
    budget_size_category = Column(String(None))
    company_size_category = Column(String(None))
    application_deadline = Column(Date)
    application_email = Column(String(None))
    application_method = Column(String(None))
    special_instructions = Column(Text)
    primary_source_url = Column(String(None))
    posted_date = Column(Date)
    ai_analysis_completed = Column(Boolean)
    primary_industry = Column(String(None))
    authenticity_score = Column(Float)
    deduplication_key = Column(String(None), unique=True)
    application_status = Column(String(None))
    last_application_attempt = Column(DateTime)
    eligibility_flag = Column(Boolean)
    prestige_factor = Column(Integer)
    prestige_reasoning = Column(Text)
    estimated_stress_level = Column(Integer)
    stress_reasoning = Column(Text)
    analysis_date = Column(DateTime)
    gemini_model_used = Column(String(None))
    analysis_tokens_used = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    job_id = Column(UUID(as_uuid=True), ForeignKey('jobs.id'))
    hiring_manager = Column(String(100))
    reporting_to = Column(String(100))
    job_title_extracted = Column(String(200))
    company_name_extracted = Column(String(100))
    additional_insights = Column(Text)
    companies = relationship('Companies', back_populates='analyzed_jobs')
    jobs = relationship('Jobs', back_populates='analyzed_jobs')

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "pre_analyzed_job_id": self.pre_analyzed_job_id,
            "company_id": self.company_id,
            "job_title": self.job_title,
            "job_description": self.job_description,
            "job_number": self.job_number,
            "salary_low": self.salary_low,
            "salary_high": self.salary_high,
            "salary_period": self.salary_period,
            "compensation_currency": self.compensation_currency,
            "equity_stock_options": self.equity_stock_options,
            "commission_or_performance_incentive": self.commission_or_performance_incentive,
            "est_total_compensation": self.est_total_compensation,
            "remote_options": self.remote_options,
            "job_type": self.job_type,
            "in_office_requirements": self.in_office_requirements,
            "office_address": self.office_address,
            "office_city": self.office_city,
            "office_province": self.office_province,
            "office_country": self.office_country,
            "working_hours_per_week": self.working_hours_per_week,
            "work_schedule": self.work_schedule,
            "specific_schedule": self.specific_schedule,
            "travel_requirements": self.travel_requirements,
            "is_supervisor": self.is_supervisor,
            "department": self.department,
            "industry": self.industry,
            "sub_industry": self.sub_industry,
            "job_function": self.job_function,
            "seniority_level": self.seniority_level,
            "supervision_count": self.supervision_count,
            "budget_size_category": self.budget_size_category,
            "company_size_category": self.company_size_category,
            "application_deadline": self.application_deadline,
            "application_email": self.application_email,
            "application_method": self.application_method,
            "special_instructions": self.special_instructions,
            "primary_source_url": self.primary_source_url,
            "posted_date": self.posted_date,
            "ai_analysis_completed": self.ai_analysis_completed,
            "primary_industry": self.primary_industry,
            "authenticity_score": self.authenticity_score,
            "deduplication_key": self.deduplication_key,
            "application_status": self.application_status,
            "last_application_attempt": self.last_application_attempt,
            "eligibility_flag": self.eligibility_flag,
            "prestige_factor": self.prestige_factor,
            "prestige_reasoning": self.prestige_reasoning,
            "estimated_stress_level": self.estimated_stress_level,
            "stress_reasoning": self.stress_reasoning,
            "analysis_date": self.analysis_date,
            "gemini_model_used": self.gemini_model_used,
            "analysis_tokens_used": self.analysis_tokens_used,
            "created_at": self.created_at,
            "job_id": self.job_id,
            "hiring_manager": self.hiring_manager,
            "reporting_to": self.reporting_to,
            "job_title_extracted": self.job_title_extracted,
            "company_name_extracted": self.company_name_extracted,
            "additional_insights": self.additional_insights,
        }

    def __repr__(self) -> str:
        return f"<AnalyzedJobs({self.id})>"


class ApplicationDocuments(Base):
    __tablename__ = "application_documents"

    document_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    job_application_id = Column(UUID(as_uuid=True), ForeignKey('job_applications.id'), unique=True, unique=True, unique=True)
    document_type = Column(String(30), unique=True, unique=True, unique=True, nullable=False)
    document_name = Column(String(255), unique=True, unique=True, unique=True, nullable=False)
    file_path = Column(Text)
    file_size = Column(Integer)
    sent_timestamp = Column(DateTime, nullable=False)
    jobapplications = relationship('JobApplications', back_populates='application_documents')

    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_id": self.document_id,
            "job_application_id": self.job_application_id,
            "document_type": self.document_type,
            "document_name": self.document_name,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "sent_timestamp": self.sent_timestamp,
        }

    def __repr__(self) -> str:
        return f"<ApplicationDocuments({self.document_id})>"


class ApplicationSettings(Base):
    __tablename__ = "application_settings"

    setting_key = Column(String(100), primary_key=True, nullable=False)
    setting_value = Column(Text)
    setting_type = Column(String(20))
    description = Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "setting_key": self.setting_key,
            "setting_value": self.setting_value,
            "setting_type": self.setting_type,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def __repr__(self) -> str:
        return f"<ApplicationSettings({self.setting_key})>"


class CanadianSpellings(Base):
    __tablename__ = "canadian_spellings"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    american_spelling = Column(String(None), nullable=False)
    canadian_spelling = Column(String(None), nullable=False)
    status = Column(String(None))
    created_date = Column(Date)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "american_spelling": self.american_spelling,
            "canadian_spelling": self.canadian_spelling,
            "status": self.status,
            "created_date": self.created_date,
        }

    def __repr__(self) -> str:
        return f"<CanadianSpellings({self.id})>"


class CleanedJobScrapeSources(Base):
    __tablename__ = "cleaned_job_scrape_sources"

    source_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    cleaned_job_id = Column(UUID(as_uuid=True), ForeignKey('cleaned_job_scrapes.cleaned_job_id'), unique=True, unique=True)
    original_scrape_id = Column(UUID(as_uuid=True), unique=True, unique=True, nullable=False)
    source_priority = Column(Integer)
    merge_timestamp = Column(DateTime, default=datetime.utcnow)
    processed_to_jobs = Column(Boolean)
    job_id = Column(UUID(as_uuid=True), ForeignKey('jobs.id'))
    processed_at = Column(DateTime)
    cleanedjobscrapes = relationship('CleanedJobScrapes', back_populates='cleaned_job_scrape_sources')
    jobs = relationship('Jobs', back_populates='cleaned_job_scrape_sources')

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "cleaned_job_id": self.cleaned_job_id,
            "original_scrape_id": self.original_scrape_id,
            "source_priority": self.source_priority,
            "merge_timestamp": self.merge_timestamp,
            "processed_to_jobs": self.processed_to_jobs,
            "job_id": self.job_id,
            "processed_at": self.processed_at,
        }

    def __repr__(self) -> str:
        return f"<CleanedJobScrapeSources({self.source_id})>"


class CleanedJobScrapes(Base):
    __tablename__ = "cleaned_job_scrapes"

    cleaned_job_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    job_title = Column(String(500))
    company_name = Column(String(300))
    location_city = Column(String(100))
    location_province = Column(String(100))
    location_country = Column(String(100))
    work_arrangement = Column(String(50))
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    salary_currency = Column(String(10))
    salary_period = Column(String(20))
    job_description = Column(Text)
    requirements = Column(Text)
    benefits = Column(Text)
    industry = Column(String(100))
    job_type = Column(String(50))
    experience_level = Column(String(50))
    posting_date = Column(Date)
    application_deadline = Column(Date)
    external_job_id = Column(String(255))
    source_website = Column(String(255), nullable=False)
    application_url = Column(Text)
    is_expired = Column(Boolean)
    cleaned_timestamp = Column(DateTime, default=datetime.utcnow)
    last_seen_timestamp = Column(DateTime, default=datetime.utcnow)
    processing_notes = Column(Text)
    location_street_address = Column(Text)
    application_email = Column(Text)
    confidence_score = Column(Float)
    duplicates_count = Column(Integer)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cleaned_job_id": self.cleaned_job_id,
            "job_title": self.job_title,
            "company_name": self.company_name,
            "location_city": self.location_city,
            "location_province": self.location_province,
            "location_country": self.location_country,
            "work_arrangement": self.work_arrangement,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "salary_currency": self.salary_currency,
            "salary_period": self.salary_period,
            "job_description": self.job_description,
            "requirements": self.requirements,
            "benefits": self.benefits,
            "industry": self.industry,
            "job_type": self.job_type,
            "experience_level": self.experience_level,
            "posting_date": self.posting_date,
            "application_deadline": self.application_deadline,
            "external_job_id": self.external_job_id,
            "source_website": self.source_website,
            "application_url": self.application_url,
            "is_expired": self.is_expired,
            "cleaned_timestamp": self.cleaned_timestamp,
            "last_seen_timestamp": self.last_seen_timestamp,
            "processing_notes": self.processing_notes,
            "location_street_address": self.location_street_address,
            "application_email": self.application_email,
            "confidence_score": self.confidence_score,
            "duplicates_count": self.duplicates_count,
        }

    def __repr__(self) -> str:
        return f"<CleanedJobScrapes({self.cleaned_job_id})>"


class Companies(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    domain = Column(String(255))
    industry = Column(String(100))
    sub_industry = Column(String(100))
    size_range = Column(String(50))
    employee_count_min = Column(Integer)
    employee_count_max = Column(Integer)
    headquarters_location = Column(String(255))
    founded_year = Column(Integer)
    company_type = Column(String(50))
    company_url = Column(String(500))
    linkedin_url = Column(String(500))
    glassdoor_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    company_description = Column(Text)
    strategic_mission = Column(Text)
    strategic_values = Column(Text)
    recent_news = Column(Text)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "domain": self.domain,
            "industry": self.industry,
            "sub_industry": self.sub_industry,
            "size_range": self.size_range,
            "employee_count_min": self.employee_count_min,
            "employee_count_max": self.employee_count_max,
            "headquarters_location": self.headquarters_location,
            "founded_year": self.founded_year,
            "company_type": self.company_type,
            "company_url": self.company_url,
            "linkedin_url": self.linkedin_url,
            "glassdoor_url": self.glassdoor_url,
            "created_at": self.created_at,
            "company_description": self.company_description,
            "strategic_mission": self.strategic_mission,
            "strategic_values": self.strategic_values,
            "recent_news": self.recent_news,
        }

    def __repr__(self) -> str:
        return f"<Companies({self.id})>"


class ConsistencyValidationLogs(Base):
    __tablename__ = "consistency_validation_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    validation_run_id = Column(UUID(as_uuid=True), nullable=False)
    issue_type = Column(String(100))
    severity = Column(String(20))
    description = Column(Text)
    affected_record_count = Column(Integer)
    correctable = Column(Boolean)
    correction_applied = Column(Boolean)
    created_at = Column(DateTime)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "validation_run_id": self.validation_run_id,
            "issue_type": self.issue_type,
            "severity": self.severity,
            "description": self.description,
            "affected_record_count": self.affected_record_count,
            "correctable": self.correctable,
            "correction_applied": self.correction_applied,
            "created_at": self.created_at,
        }

    def __repr__(self) -> str:
        return f"<ConsistencyValidationLogs({self.id})>"


class DataCorrections(Base):
    __tablename__ = "data_corrections"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    validation_run_id = Column(UUID(as_uuid=True), nullable=False)
    correction_type = Column(String(100))
    affected_table = Column(String(100))
    affected_records = Column(JSON)
    correction_sql = Column(Text)
    applied_at = Column(DateTime)
    success = Column(Boolean)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "validation_run_id": self.validation_run_id,
            "correction_type": self.correction_type,
            "affected_table": self.affected_table,
            "affected_records": self.affected_records,
            "correction_sql": self.correction_sql,
            "applied_at": self.applied_at,
            "success": self.success,
        }

    def __repr__(self) -> str:
        return f"<DataCorrections({self.id})>"


class DocumentJobs(Base):
    __tablename__ = "document_jobs"

    job_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False)
    file_path = Column(String(500))
    filename = Column(String(255))
    file_size = Column(Integer)
    title = Column(String(255))
    author = Column(String(255))
    document_type = Column(String(50), nullable=False)
    status = Column(String(50))
    created_at = Column(DateTime)
    completed_at = Column(DateTime)
    webhook_data = Column(JSON)
    has_error = Column(Boolean)
    error_code = Column(String(100))
    error_message = Column(Text)
    error_details = Column(JSON)
    storage_type = Column(String(50))
    object_storage_path = Column(String(500))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "file_path": self.file_path,
            "filename": self.filename,
            "file_size": self.file_size,
            "title": self.title,
            "author": self.author,
            "document_type": self.document_type,
            "status": self.status,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "webhook_data": self.webhook_data,
            "has_error": self.has_error,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "error_details": self.error_details,
            "storage_type": self.storage_type,
            "object_storage_path": self.object_storage_path,
        }

    def __repr__(self) -> str:
        return f"<DocumentJobs({self.job_id})>"


class DocumentSentences(Base):
    __tablename__ = "document_sentences"

    sentence_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    document_job_id = Column(UUID(as_uuid=True), ForeignKey('document_jobs.job_id'), unique=True, unique=True)
    sentence_text = Column(Text, nullable=False)
    tone_score = Column(Float)
    sentiment_category = Column(String(20))
    confidence_score = Column(Float)
    word_count = Column(Integer)
    sentence_order = Column(Integer, unique=True, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    documentjobs = relationship('DocumentJobs', back_populates='document_sentences')

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sentence_id": self.sentence_id,
            "document_job_id": self.document_job_id,
            "sentence_text": self.sentence_text,
            "tone_score": self.tone_score,
            "sentiment_category": self.sentiment_category,
            "confidence_score": self.confidence_score,
            "word_count": self.word_count,
            "sentence_order": self.sentence_order,
            "created_at": self.created_at,
        }

    def __repr__(self) -> str:
        return f"<DocumentSentences({self.sentence_id})>"


class DocumentTemplateMetadata(Base):
    __tablename__ = "document_template_metadata"

    document_type = Column(String(20), nullable=False)
    resume_general_section_count = Column(Integer)
    resume_constituent_section_count = Column(Integer)
    cover_par_one = Column(Integer)
    cover_par_two = Column(Integer)
    cover_par_three = Column(Integer)
    count = Column(Integer)
    template_file_path = Column(String(255))
    id = Column(Integer, primary_key=True, nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_type": self.document_type,
            "resume_general_section_count": self.resume_general_section_count,
            "resume_constituent_section_count": self.resume_constituent_section_count,
            "cover_par_one": self.cover_par_one,
            "cover_par_two": self.cover_par_two,
            "cover_par_three": self.cover_par_three,
            "count": self.count,
            "template_file_path": self.template_file_path,
            "id": self.id,
        }

    def __repr__(self) -> str:
        return f"<DocumentTemplateMetadata({self.id})>"


class DocumentToneAnalysis(Base):
    __tablename__ = "document_tone_analysis"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    document_type = Column(String(50), nullable=False)
    sentences = Column(JSON, nullable=False)
    tone_jump_score = Column(Float)
    tone_coherence_score = Column(Float)
    total_tone_travel = Column(Float)
    average_tone_jump = Column(Float)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "document_type": self.document_type,
            "sentences": self.sentences,
            "tone_jump_score": self.tone_jump_score,
            "tone_coherence_score": self.tone_coherence_score,
            "total_tone_travel": self.total_tone_travel,
            "average_tone_jump": self.average_tone_jump,
        }

    def __repr__(self) -> str:
        return f"<DocumentToneAnalysis({self.id})>"


class ErrorLog(Base):
    __tablename__ = "error_log"

    id = Column(Integer, primary_key=True, nullable=False)
    error_id = Column(String(36), unique=True, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    session_id = Column(String(36))
    stage_name = Column(String(50))
    error_category = Column(String(30), nullable=False)
    severity = Column(String(20), nullable=False)
    error_message = Column(Text, nullable=False)
    error_details = Column(Text)
    exception_type = Column(String(100))
    stack_trace = Column(Text)
    context_data = Column(JSON)
    retry_count = Column(Integer)
    resolved = Column(Boolean)
    resolution_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "error_id": self.error_id,
            "timestamp": self.timestamp,
            "session_id": self.session_id,
            "stage_name": self.stage_name,
            "error_category": self.error_category,
            "severity": self.severity,
            "error_message": self.error_message,
            "error_details": self.error_details,
            "exception_type": self.exception_type,
            "stack_trace": self.stack_trace,
            "context_data": self.context_data,
            "retry_count": self.retry_count,
            "resolved": self.resolved,
            "resolution_notes": self.resolution_notes,
            "created_at": self.created_at,
        }

    def __repr__(self) -> str:
        return f"<ErrorLog({self.id})>"


class FailureLogs(Base):
    __tablename__ = "failure_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    failure_type = Column(String(100), nullable=False)
    operation_name = Column(String(200), nullable=False)
    workflow_id = Column(UUID(as_uuid=True))
    error_message = Column(Text)
    error_details = Column(JSON)
    recovery_attempts = Column(Integer)
    recovery_successful = Column(Boolean)
    created_at = Column(DateTime)
    resolved_at = Column(DateTime)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "failure_type": self.failure_type,
            "operation_name": self.operation_name,
            "workflow_id": self.workflow_id,
            "error_message": self.error_message,
            "error_details": self.error_details,
            "recovery_attempts": self.recovery_attempts,
            "recovery_successful": self.recovery_successful,
            "created_at": self.created_at,
            "resolved_at": self.resolved_at,
        }

    def __repr__(self) -> str:
        return f"<FailureLogs({self.id})>"


class JobAnalysisQueue(Base):
    __tablename__ = "job_analysis_queue"

    id = Column(Integer, primary_key=True, nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey('jobs.id'), unique=True, nullable=False)
    priority = Column(String(20))
    queued_at = Column(DateTime, default=datetime.utcnow)
    attempts = Column(Integer)
    last_attempt_at = Column(DateTime)
    error_message = Column(Text)
    status = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    jobs = relationship('Jobs', back_populates='job_analysis_queue')

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "job_id": self.job_id,
            "priority": self.priority,
            "queued_at": self.queued_at,
            "attempts": self.attempts,
            "last_attempt_at": self.last_attempt_at,
            "error_message": self.error_message,
            "status": self.status,
            "created_at": self.created_at,
        }

    def __repr__(self) -> str:
        return f"<JobAnalysisQueue({self.id})>"


class JobApplicationTracking(Base):
    __tablename__ = "job_application_tracking"

    tracking_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    job_application_id = Column(UUID(as_uuid=True), ForeignKey('job_applications.id'))
    tracking_type = Column(String(50), nullable=False)
    tracking_event = Column(String(100), nullable=False)
    event_timestamp = Column(DateTime, nullable=False)
    event_data = Column(JSON)
    ip_address = Column(String)
    user_agent = Column(Text)
    jobapplications = relationship('JobApplications', back_populates='job_application_tracking')

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tracking_id": self.tracking_id,
            "job_application_id": self.job_application_id,
            "tracking_type": self.tracking_type,
            "tracking_event": self.tracking_event,
            "event_timestamp": self.event_timestamp,
            "event_data": self.event_data,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
        }

    def __repr__(self) -> str:
        return f"<JobApplicationTracking({self.tracking_id})>"


class JobApplications(Base):
    __tablename__ = "job_applications"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey('jobs.id'))
    application_date = Column(DateTime, default=datetime.utcnow)
    application_method = Column(String(50))
    application_status = Column(String(50))
    email_sent_to = Column(String(255))
    documents_sent = Column(ARRAY(String))
    tracking_data = Column(JSON)
    first_response_received_at = Column(DateTime)
    response_type = Column(String(50))
    notes = Column(Text)
    tone_jump_score = Column(Float)
    tone_coherence_score = Column(Float)
    total_tone_travel = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_response_received_at = Column(DateTime)
    jobs = relationship('Jobs', back_populates='job_applications')

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "job_id": self.job_id,
            "application_date": self.application_date,
            "application_method": self.application_method,
            "application_status": self.application_status,
            "email_sent_to": self.email_sent_to,
            "documents_sent": self.documents_sent,
            "tracking_data": self.tracking_data,
            "first_response_received_at": self.first_response_received_at,
            "response_type": self.response_type,
            "notes": self.notes,
            "tone_jump_score": self.tone_jump_score,
            "tone_coherence_score": self.tone_coherence_score,
            "total_tone_travel": self.total_tone_travel,
            "created_at": self.created_at,
            "last_response_received_at": self.last_response_received_at,
        }

    def __repr__(self) -> str:
        return f"<JobApplications({self.id})>"


class JobAtsKeywords(Base):
    __tablename__ = "job_ats_keywords"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), unique=True, unique=True)
    keyword = Column(String(100), unique=True, unique=True, nullable=False)
    keyword_category = Column(String(30))
    frequency_in_posting = Column(Integer)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "job_id": self.job_id,
            "keyword": self.keyword,
            "keyword_category": self.keyword_category,
            "frequency_in_posting": self.frequency_in_posting,
        }

    def __repr__(self) -> str:
        return f"<JobAtsKeywords({self.id})>"


class JobBenefits(Base):
    __tablename__ = "job_benefits"

    benefit_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey('jobs.id'), unique=True, unique=True)
    benefit_type = Column(String(50), unique=True, unique=True, nullable=False)
    benefit_description = Column(Text)
    benefit_value = Column(String(100))
    jobs = relationship('Jobs', back_populates='job_benefits')

    def to_dict(self) -> Dict[str, Any]:
        return {
            "benefit_id": self.benefit_id,
            "job_id": self.job_id,
            "benefit_type": self.benefit_type,
            "benefit_description": self.benefit_description,
            "benefit_value": self.benefit_value,
        }

    def __repr__(self) -> str:
        return f"<JobBenefits({self.benefit_id})>"


class JobCertifications(Base):
    __tablename__ = "job_certifications"

    id = Column(Integer, primary_key=True, nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey('jobs.id'))
    certification_name = Column(String(100), nullable=False)
    is_required = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)
    jobs = relationship('Jobs', back_populates='job_certifications')

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "job_id": self.job_id,
            "certification_name": self.certification_name,
            "is_required": self.is_required,
            "created_at": self.created_at,
        }

    def __repr__(self) -> str:
        return f"<JobCertifications({self.id})>"


class JobEducationRequirements(Base):
    __tablename__ = "job_education_requirements"

    id = Column(Integer, primary_key=True, nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey('jobs.id'), nullable=False)
    degree_level = Column(String(100))
    field_of_study = Column(String(200))
    institution_type = Column(String(100))
    years_required = Column(Integer)
    is_required = Column(Boolean)
    alternative_experience = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    jobs = relationship('Jobs', back_populates='job_education_requirements')

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "job_id": self.job_id,
            "degree_level": self.degree_level,
            "field_of_study": self.field_of_study,
            "institution_type": self.institution_type,
            "years_required": self.years_required,
            "is_required": self.is_required,
            "alternative_experience": self.alternative_experience,
            "created_at": self.created_at,
        }

    def __repr__(self) -> str:
        return f"<JobEducationRequirements({self.id})>"


class JobLogs(Base):
    __tablename__ = "job_logs"

    log_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False)
    job_id = Column(UUID(as_uuid=True), nullable=False)
    timestamp = Column(DateTime)
    log_level = Column(String(20))
    message = Column(Text, nullable=False)
    details = Column(JSON)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "log_id": self.log_id,
            "job_id": self.job_id,
            "timestamp": self.timestamp,
            "log_level": self.log_level,
            "message": self.message,
            "details": self.details,
        }

    def __repr__(self) -> str:
        return f"<JobLogs({self.log_id})>"


class JobPlatformsFound(Base):
    __tablename__ = "job_platforms_found"

    platform_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey('jobs.id'), unique=True, unique=True)
    platform_name = Column(String(100), unique=True, unique=True, nullable=False)
    platform_url = Column(Text)
    first_found_at = Column(DateTime, default=datetime.utcnow)
    jobs = relationship('Jobs', back_populates='job_platforms_found')

    def to_dict(self) -> Dict[str, Any]:
        return {
            "platform_id": self.platform_id,
            "job_id": self.job_id,
            "platform_name": self.platform_name,
            "platform_url": self.platform_url,
            "first_found_at": self.first_found_at,
        }

    def __repr__(self) -> str:
        return f"<JobPlatformsFound({self.platform_id})>"


class JobRedFlagsDetails(Base):
    __tablename__ = "job_red_flags_details"

    id = Column(Integer, primary_key=True, nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey('jobs.id'))
    flag_type = Column(String(50), nullable=False)
    detected = Column(Boolean)
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    jobs = relationship('Jobs', back_populates='job_red_flags_details')

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "job_id": self.job_id,
            "flag_type": self.flag_type,
            "detected": self.detected,
            "details": self.details,
            "created_at": self.created_at,
        }

    def __repr__(self) -> str:
        return f"<JobRedFlagsDetails({self.id})>"


class JobRequiredDocuments(Base):
    __tablename__ = "job_required_documents"

    id = Column(Integer, primary_key=True, nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey('jobs.id'))
    document_type = Column(String(50), nullable=False)
    is_required = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)
    jobs = relationship('Jobs', back_populates='job_required_documents')

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "job_id": self.job_id,
            "document_type": self.document_type,
            "is_required": self.is_required,
            "created_at": self.created_at,
        }

    def __repr__(self) -> str:
        return f"<JobRequiredDocuments({self.id})>"


class JobRequiredSkills(Base):
    __tablename__ = "job_required_skills"

    skill_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey('jobs.id'), unique=True, unique=True)
    skill_name = Column(String(100), unique=True, unique=True, nullable=False)
    skill_level = Column(String(20))
    is_required = Column(Boolean)
    jobs = relationship('Jobs', back_populates='job_required_skills')

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "job_id": self.job_id,
            "skill_name": self.skill_name,
            "skill_level": self.skill_level,
            "is_required": self.is_required,
        }

    def __repr__(self) -> str:
        return f"<JobRequiredSkills({self.skill_id})>"


class JobSkills(Base):
    __tablename__ = "job_skills"

    skill_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), unique=True, unique=True)
    skill_name = Column(String(100), unique=True, unique=True, nullable=False)
    importance_rating = Column(Integer)
    is_required = Column(Boolean)
    reasoning = Column(Text)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "job_id": self.job_id,
            "skill_name": self.skill_name,
            "importance_rating": self.importance_rating,
            "is_required": self.is_required,
            "reasoning": self.reasoning,
        }

    def __repr__(self) -> str:
        return f"<JobSkills({self.skill_id})>"


class JobStressIndicators(Base):
    __tablename__ = "job_stress_indicators"

    id = Column(Integer, primary_key=True, nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey('jobs.id'))
    indicator = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    jobs = relationship('Jobs', back_populates='job_stress_indicators')

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "job_id": self.job_id,
            "indicator": self.indicator,
            "description": self.description,
            "created_at": self.created_at,
        }

    def __repr__(self) -> str:
        return f"<JobStressIndicators({self.id})>"


class Jobs(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id'))
    job_title = Column(String(255), nullable=False)
    job_description = Column(Text)
    job_number = Column(String(100))
    salary_low = Column(Integer)
    salary_high = Column(Integer)
    salary_period = Column(String(20))
    remote_options = Column(String(50))
    job_type = Column(String(50))
    is_supervisor = Column(Boolean)
    department = Column(String(100))
    industry = Column(String(100))
    seniority_level = Column(String(50))
    application_deadline = Column(Date)
    is_active = Column(Boolean)
    application_status = Column(String(50))
    last_application_attempt = Column(DateTime)
    application_method = Column(String(50))
    analysis_completed = Column(Boolean)
    consolidation_confidence = Column(Float)
    primary_source_url = Column(String(500))
    posted_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    title_matches_role = Column(Boolean)
    mismatch_explanation = Column(Text)
    is_authentic = Column(Boolean)
    authenticity_reasoning = Column(Text)
    sub_industry = Column(String(100))
    job_function = Column(String(100))
    in_office_requirements = Column(String(50))
    office_address = Column(Text)
    office_city = Column(String(100))
    office_province = Column(String(100))
    office_country = Column(String(100))
    working_hours_per_week = Column(Integer)
    work_schedule = Column(Text)
    specific_schedule = Column(Text)
    travel_requirements = Column(Text)
    salary_mentioned = Column(Boolean)
    equity_stock_options = Column(Boolean)
    commission_or_performance_incentive = Column(Text)
    est_total_compensation = Column(Text)
    compensation_currency = Column(String(10))
    application_email = Column(String(255))
    special_instructions = Column(Text)
    estimated_stress_level = Column(Integer)
    stress_reasoning = Column(Text)
    education_requirements = Column(Text)
    overall_red_flag_reasoning = Column(Text)
    cover_letter_pain_point = Column(Text)
    cover_letter_evidence = Column(Text)
    cover_letter_solution_angle = Column(Text)
    eligibility_flag = Column(Boolean)
    prestige_factor = Column(Integer)
    prestige_reasoning = Column(Text)
    supervision_count = Column(Integer)
    budget_size_category = Column(String(20))
    company_size_category = Column(String(20))
    companies = relationship('Companies', back_populates='jobs')

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "company_id": self.company_id,
            "job_title": self.job_title,
            "job_description": self.job_description,
            "job_number": self.job_number,
            "salary_low": self.salary_low,
            "salary_high": self.salary_high,
            "salary_period": self.salary_period,
            "remote_options": self.remote_options,
            "job_type": self.job_type,
            "is_supervisor": self.is_supervisor,
            "department": self.department,
            "industry": self.industry,
            "seniority_level": self.seniority_level,
            "application_deadline": self.application_deadline,
            "is_active": self.is_active,
            "application_status": self.application_status,
            "last_application_attempt": self.last_application_attempt,
            "application_method": self.application_method,
            "analysis_completed": self.analysis_completed,
            "consolidation_confidence": self.consolidation_confidence,
            "primary_source_url": self.primary_source_url,
            "posted_date": self.posted_date,
            "created_at": self.created_at,
            "title_matches_role": self.title_matches_role,
            "mismatch_explanation": self.mismatch_explanation,
            "is_authentic": self.is_authentic,
            "authenticity_reasoning": self.authenticity_reasoning,
            "sub_industry": self.sub_industry,
            "job_function": self.job_function,
            "in_office_requirements": self.in_office_requirements,
            "office_address": self.office_address,
            "office_city": self.office_city,
            "office_province": self.office_province,
            "office_country": self.office_country,
            "working_hours_per_week": self.working_hours_per_week,
            "work_schedule": self.work_schedule,
            "specific_schedule": self.specific_schedule,
            "travel_requirements": self.travel_requirements,
            "salary_mentioned": self.salary_mentioned,
            "equity_stock_options": self.equity_stock_options,
            "commission_or_performance_incentive": self.commission_or_performance_incentive,
            "est_total_compensation": self.est_total_compensation,
            "compensation_currency": self.compensation_currency,
            "application_email": self.application_email,
            "special_instructions": self.special_instructions,
            "estimated_stress_level": self.estimated_stress_level,
            "stress_reasoning": self.stress_reasoning,
            "education_requirements": self.education_requirements,
            "overall_red_flag_reasoning": self.overall_red_flag_reasoning,
            "cover_letter_pain_point": self.cover_letter_pain_point,
            "cover_letter_evidence": self.cover_letter_evidence,
            "cover_letter_solution_angle": self.cover_letter_solution_angle,
            "eligibility_flag": self.eligibility_flag,
            "prestige_factor": self.prestige_factor,
            "prestige_reasoning": self.prestige_reasoning,
            "supervision_count": self.supervision_count,
            "budget_size_category": self.budget_size_category,
            "company_size_category": self.company_size_category,
        }

    def __repr__(self) -> str:
        return f"<Jobs({self.id})>"


class KeywordFilters(Base):
    __tablename__ = "keyword_filters"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    keyword = Column(String(None), nullable=False)
    status = Column(String(None))
    created_date = Column(Date)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "keyword": self.keyword,
            "status": self.status,
            "created_date": self.created_date,
        }

    def __repr__(self) -> str:
        return f"<KeywordFilters({self.id})>"


class LinkClicks(Base):
    __tablename__ = "link_clicks"

    click_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    tracking_id = Column(String(100), ForeignKey('link_tracking.tracking_id'), nullable=False)
    clicked_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String)
    user_agent = Column(Text)
    referrer_url = Column(String(1000))
    session_id = Column(String(100))
    click_source = Column(String(50))
    metadata = Column(JSON)
    linktracking = relationship('LinkTracking', back_populates='link_clicks')

    def to_dict(self) -> Dict[str, Any]:
        return {
            "click_id": self.click_id,
            "tracking_id": self.tracking_id,
            "clicked_at": self.clicked_at,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "referrer_url": self.referrer_url,
            "session_id": self.session_id,
            "click_source": self.click_source,
            "metadata": self.metadata,
        }

    def __repr__(self) -> str:
        return f"<LinkClicks({self.click_id})>"


class LinkTracking(Base):
    __tablename__ = "link_tracking"

    tracking_id = Column(String(100), primary_key=True, nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey('jobs.id'))
    application_id = Column(UUID(as_uuid=True), ForeignKey('job_applications.id'))
    link_function = Column(String(50), nullable=False)
    link_type = Column(String(50), nullable=False)
    original_url = Column(String(1000), nullable=False)
    redirect_url = Column(String(1000), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100))
    is_active = Column(Boolean)
    description = Column(Text)
    jobs = relationship('Jobs', back_populates='link_tracking')
    jobapplications = relationship('JobApplications', back_populates='link_tracking')

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tracking_id": self.tracking_id,
            "job_id": self.job_id,
            "application_id": self.application_id,
            "link_function": self.link_function,
            "link_type": self.link_type,
            "original_url": self.original_url,
            "redirect_url": self.redirect_url,
            "created_at": self.created_at,
            "created_by": self.created_by,
            "is_active": self.is_active,
            "description": self.description,
        }

    def __repr__(self) -> str:
        return f"<LinkTracking({self.tracking_id})>"


class PerformanceMetrics(Base):
    __tablename__ = "performance_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    stage_name = Column(String(None), nullable=False)
    api_call_type = Column(String(None), nullable=False)
    response_time_ms = Column(Integer)
    success = Column(Boolean, nullable=False)
    error_message = Column(Text)
    cost_estimate = Column(Float)
    batch_size = Column(Integer)
    sentences_processed = Column(Integer)
    processing_date = Column(DateTime, default=datetime.utcnow)
    model_used = Column(String(None))
    session_id = Column(String(None))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "stage_name": self.stage_name,
            "api_call_type": self.api_call_type,
            "response_time_ms": self.response_time_ms,
            "success": self.success,
            "error_message": self.error_message,
            "cost_estimate": self.cost_estimate,
            "batch_size": self.batch_size,
            "sentences_processed": self.sentences_processed,
            "processing_date": self.processing_date,
            "model_used": self.model_used,
            "session_id": self.session_id,
        }

    def __repr__(self) -> str:
        return f"<PerformanceMetrics({self.id})>"


class PreAnalyzedJobs(Base):
    __tablename__ = "pre_analyzed_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    cleaned_scrape_id = Column(UUID(as_uuid=True), ForeignKey('cleaned_job_scrapes.cleaned_job_id'))
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id'))
    job_title = Column(String(None), nullable=False)
    company_name = Column(String(None))
    location_city = Column(String(None))
    location_province = Column(String(None))
    location_country = Column(String(None))
    work_arrangement = Column(String(None))
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    salary_currency = Column(String(None))
    salary_period = Column(String(None))
    job_description = Column(Text)
    requirements = Column(Text)
    benefits = Column(Text)
    industry = Column(String(None))
    job_type = Column(String(None))
    experience_level = Column(String(None))
    posting_date = Column(Date)
    application_deadline = Column(Date)
    external_job_id = Column(String(None))
    source_website = Column(String(None))
    application_url = Column(String(None))
    application_email = Column(String(None))
    confidence_score = Column(Float)
    duplicates_count = Column(Integer)
    deduplication_key = Column(String(None))
    is_active = Column(Boolean)
    queued_for_analysis = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    cleanedjobscrapes = relationship('CleanedJobScrapes', back_populates='pre_analyzed_jobs')
    companies = relationship('Companies', back_populates='pre_analyzed_jobs')

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "cleaned_scrape_id": self.cleaned_scrape_id,
            "company_id": self.company_id,
            "job_title": self.job_title,
            "company_name": self.company_name,
            "location_city": self.location_city,
            "location_province": self.location_province,
            "location_country": self.location_country,
            "work_arrangement": self.work_arrangement,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "salary_currency": self.salary_currency,
            "salary_period": self.salary_period,
            "job_description": self.job_description,
            "requirements": self.requirements,
            "benefits": self.benefits,
            "industry": self.industry,
            "job_type": self.job_type,
            "experience_level": self.experience_level,
            "posting_date": self.posting_date,
            "application_deadline": self.application_deadline,
            "external_job_id": self.external_job_id,
            "source_website": self.source_website,
            "application_url": self.application_url,
            "application_email": self.application_email,
            "confidence_score": self.confidence_score,
            "duplicates_count": self.duplicates_count,
            "deduplication_key": self.deduplication_key,
            "is_active": self.is_active,
            "queued_for_analysis": self.queued_for_analysis,
            "created_at": self.created_at,
            "processed_at": self.processed_at,
        }

    def __repr__(self) -> str:
        return f"<PreAnalyzedJobs({self.id})>"


class RawJobScrapes(Base):
    __tablename__ = "raw_job_scrapes"

    scrape_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    source_website = Column(String(255), nullable=False)
    source_url = Column(Text, nullable=False)
    full_application_url = Column(Text)
    scrape_timestamp = Column(DateTime, default=datetime.utcnow)
    raw_data = Column(JSON, nullable=False)
    scraper_used = Column(String(100))
    scraper_run_id = Column(String(255))
    user_agent = Column(Text)
    ip_address = Column(String(45))
    success_status = Column(Boolean)
    error_message = Column(Text)
    response_time_ms = Column(Integer)
    data_size_bytes = Column(Integer)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scrape_id": self.scrape_id,
            "source_website": self.source_website,
            "source_url": self.source_url,
            "full_application_url": self.full_application_url,
            "scrape_timestamp": self.scrape_timestamp,
            "raw_data": self.raw_data,
            "scraper_used": self.scraper_used,
            "scraper_run_id": self.scraper_run_id,
            "user_agent": self.user_agent,
            "ip_address": self.ip_address,
            "success_status": self.success_status,
            "error_message": self.error_message,
            "response_time_ms": self.response_time_ms,
            "data_size_bytes": self.data_size_bytes,
        }

    def __repr__(self) -> str:
        return f"<RawJobScrapes({self.scrape_id})>"


class RecoveryStatistics(Base):
    __tablename__ = "recovery_statistics"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    date = Column(Date, unique=True, unique=True)
    failure_type = Column(String(100), unique=True, unique=True)
    total_failures = Column(Integer)
    successful_recoveries = Column(Integer)
    failed_recoveries = Column(Integer)
    average_recovery_time = Column(Float)
    created_at = Column(DateTime)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "date": self.date,
            "failure_type": self.failure_type,
            "total_failures": self.total_failures,
            "successful_recoveries": self.successful_recoveries,
            "failed_recoveries": self.failed_recoveries,
            "average_recovery_time": self.average_recovery_time,
            "created_at": self.created_at,
        }

    def __repr__(self) -> str:
        return f"<RecoveryStatistics({self.id})>"


class SecurityTestTable(Base):
    __tablename__ = "security_test_table"

    id = Column(Integer)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
        }

    def __repr__(self) -> str:
        return f"<SecurityTestTable>"


class SentenceBankCoverLetter(Base):
    __tablename__ = "sentence_bank_cover_letter"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    content_text = Column(Text, nullable=False)
    tone = Column(String(100))
    tone_strength = Column(Float)
    status = Column(String(20))
    position_label = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    matches_job_skill = Column(String(100))
    variable = Column(Boolean)
    keyword_filter_status = Column(String(None))
    keyword_filter_date = Column(Date)
    keyword_filter_error_message = Column(Text)
    truthfulness_status = Column(String(None))
    truthfulness_date = Column(Date)
    truthfulness_model = Column(String(None))
    truthfulness_error_message = Column(Text)
    canadian_spelling_status = Column(String(None))
    canadian_spelling_date = Column(Date)
    tone_analysis_status = Column(String(None))
    tone_analysis_date = Column(Date)
    tone_analysis_model = Column(String(None))
    tone_analysis_error_message = Column(Text)
    skill_analysis_status = Column(String(None))
    skill_analysis_date = Column(Date)
    skill_analysis_model = Column(String(None))
    skill_analysis_error_message = Column(Text)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content_text": self.content_text,
            "tone": self.tone,
            "tone_strength": self.tone_strength,
            "status": self.status,
            "position_label": self.position_label,
            "created_at": self.created_at,
            "matches_job_skill": self.matches_job_skill,
            "variable": self.variable,
            "keyword_filter_status": self.keyword_filter_status,
            "keyword_filter_date": self.keyword_filter_date,
            "keyword_filter_error_message": self.keyword_filter_error_message,
            "truthfulness_status": self.truthfulness_status,
            "truthfulness_date": self.truthfulness_date,
            "truthfulness_model": self.truthfulness_model,
            "truthfulness_error_message": self.truthfulness_error_message,
            "canadian_spelling_status": self.canadian_spelling_status,
            "canadian_spelling_date": self.canadian_spelling_date,
            "tone_analysis_status": self.tone_analysis_status,
            "tone_analysis_date": self.tone_analysis_date,
            "tone_analysis_model": self.tone_analysis_model,
            "tone_analysis_error_message": self.tone_analysis_error_message,
            "skill_analysis_status": self.skill_analysis_status,
            "skill_analysis_date": self.skill_analysis_date,
            "skill_analysis_model": self.skill_analysis_model,
            "skill_analysis_error_message": self.skill_analysis_error_message,
        }

    def __repr__(self) -> str:
        return f"<SentenceBankCoverLetter({self.id})>"


class SentenceBankResume(Base):
    __tablename__ = "sentence_bank_resume"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    content_text = Column(Text, nullable=False)
    body_section = Column(String(100))
    tone = Column(String(100))
    tone_strength = Column(Float)
    status = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    matches_job_skill = Column(String(100))
    experience_id = Column(UUID(as_uuid=True), ForeignKey('job_applications.id'))
    keyword_filter_status = Column(String(None))
    keyword_filter_date = Column(Date)
    keyword_filter_error_message = Column(Text)
    truthfulness_status = Column(String(None))
    truthfulness_date = Column(Date)
    truthfulness_model = Column(String(None))
    truthfulness_error_message = Column(Text)
    canadian_spelling_status = Column(String(None))
    canadian_spelling_date = Column(Date)
    tone_analysis_status = Column(String(None))
    tone_analysis_date = Column(Date)
    tone_analysis_model = Column(String(None))
    tone_analysis_error_message = Column(Text)
    skill_analysis_status = Column(String(None))
    skill_analysis_date = Column(Date)
    skill_analysis_model = Column(String(None))
    skill_analysis_error_message = Column(Text)
    jobapplications = relationship('JobApplications', back_populates='sentence_bank_resume')

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content_text": self.content_text,
            "body_section": self.body_section,
            "tone": self.tone,
            "tone_strength": self.tone_strength,
            "status": self.status,
            "created_at": self.created_at,
            "matches_job_skill": self.matches_job_skill,
            "experience_id": self.experience_id,
            "keyword_filter_status": self.keyword_filter_status,
            "keyword_filter_date": self.keyword_filter_date,
            "keyword_filter_error_message": self.keyword_filter_error_message,
            "truthfulness_status": self.truthfulness_status,
            "truthfulness_date": self.truthfulness_date,
            "truthfulness_model": self.truthfulness_model,
            "truthfulness_error_message": self.truthfulness_error_message,
            "canadian_spelling_status": self.canadian_spelling_status,
            "canadian_spelling_date": self.canadian_spelling_date,
            "tone_analysis_status": self.tone_analysis_status,
            "tone_analysis_date": self.tone_analysis_date,
            "tone_analysis_model": self.tone_analysis_model,
            "tone_analysis_error_message": self.tone_analysis_error_message,
            "skill_analysis_status": self.skill_analysis_status,
            "skill_analysis_date": self.skill_analysis_date,
            "skill_analysis_model": self.skill_analysis_model,
            "skill_analysis_error_message": self.skill_analysis_error_message,
        }

    def __repr__(self) -> str:
        return f"<SentenceBankResume({self.id})>"


class UserCandidateInfo(Base):
    __tablename__ = "user_candidate_info"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), unique=True, nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(255))
    phone = Column(String(20))
    mailing_address = Column(Text)
    linkedin_url = Column(String(500))
    portfolio_url = Column(String(500))
    calendly_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "mailing_address": self.mailing_address,
            "linkedin_url": self.linkedin_url,
            "portfolio_url": self.portfolio_url,
            "calendly_url": self.calendly_url,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def __repr__(self) -> str:
        return f"<UserCandidateInfo({self.id})>"


class UserJobPreferences(Base):
    __tablename__ = "user_job_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4)
    salary_minimum = Column(Integer)
    hourly_rate_minimum = Column(Float)
    bonus_expected = Column(Boolean)
    stock_options_preferred = Column(Boolean)
    hours_per_week_minimum = Column(Integer)
    hours_per_week_maximum = Column(Integer)
    flexible_hours_required = Column(Boolean)
    overtime_acceptable = Column(Boolean)
    work_arrangement = Column(String(20))
    travel_percentage_maximum = Column(Integer)
    preferred_city = Column(String(100))
    preferred_province_state = Column(String(100))
    preferred_country = Column(String(100))
    commute_time_maximum = Column(Integer)
    relocation_acceptable = Column(Boolean)
    health_insurance_required = Column(Boolean)
    dental_insurance_required = Column(Boolean)
    vision_insurance_preferred = Column(Boolean)
    health_benefits_dollar_value = Column(Integer)
    retirement_matching_minimum = Column(Float)
    vacation_days_minimum = Column(Integer)
    sick_days_minimum = Column(Integer)
    parental_leave_required = Column(Boolean)
    parental_leave_weeks_minimum = Column(Integer)
    training_budget_minimum = Column(Integer)
    conference_attendance_preferred = Column(Boolean)
    certification_support_required = Column(Boolean)
    mentorship_program_preferred = Column(Boolean)
    career_advancement_timeline = Column(Integer)
    company_size_minimum = Column(Integer)
    company_size_maximum = Column(Integer)
    startup_acceptable = Column(Boolean)
    public_company_preferred = Column(Boolean)
    industry_prestige_importance = Column(Integer)
    company_mission_alignment_importance = Column(Integer)
    acceptable_stress = Column(Integer)
    experience_level_minimum = Column(String(20))
    experience_level_maximum = Column(String(20))
    management_responsibility_acceptable = Column(Boolean)
    individual_contributor_preferred = Column(Boolean)
    drug_testing_acceptable = Column(Boolean)
    background_check_acceptable = Column(Boolean)
    security_clearance_required = Column(Boolean)
    is_active = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    street_address = Column(Text)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey('user_candidate_info.id'))
    usercandidateinfo = relationship('UserCandidateInfo', back_populates='user_job_preferences')

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "salary_minimum": self.salary_minimum,
            "hourly_rate_minimum": self.hourly_rate_minimum,
            "bonus_expected": self.bonus_expected,
            "stock_options_preferred": self.stock_options_preferred,
            "hours_per_week_minimum": self.hours_per_week_minimum,
            "hours_per_week_maximum": self.hours_per_week_maximum,
            "flexible_hours_required": self.flexible_hours_required,
            "overtime_acceptable": self.overtime_acceptable,
            "work_arrangement": self.work_arrangement,
            "travel_percentage_maximum": self.travel_percentage_maximum,
            "preferred_city": self.preferred_city,
            "preferred_province_state": self.preferred_province_state,
            "preferred_country": self.preferred_country,
            "commute_time_maximum": self.commute_time_maximum,
            "relocation_acceptable": self.relocation_acceptable,
            "health_insurance_required": self.health_insurance_required,
            "dental_insurance_required": self.dental_insurance_required,
            "vision_insurance_preferred": self.vision_insurance_preferred,
            "health_benefits_dollar_value": self.health_benefits_dollar_value,
            "retirement_matching_minimum": self.retirement_matching_minimum,
            "vacation_days_minimum": self.vacation_days_minimum,
            "sick_days_minimum": self.sick_days_minimum,
            "parental_leave_required": self.parental_leave_required,
            "parental_leave_weeks_minimum": self.parental_leave_weeks_minimum,
            "training_budget_minimum": self.training_budget_minimum,
            "conference_attendance_preferred": self.conference_attendance_preferred,
            "certification_support_required": self.certification_support_required,
            "mentorship_program_preferred": self.mentorship_program_preferred,
            "career_advancement_timeline": self.career_advancement_timeline,
            "company_size_minimum": self.company_size_minimum,
            "company_size_maximum": self.company_size_maximum,
            "startup_acceptable": self.startup_acceptable,
            "public_company_preferred": self.public_company_preferred,
            "industry_prestige_importance": self.industry_prestige_importance,
            "company_mission_alignment_importance": self.company_mission_alignment_importance,
            "acceptable_stress": self.acceptable_stress,
            "experience_level_minimum": self.experience_level_minimum,
            "experience_level_maximum": self.experience_level_maximum,
            "management_responsibility_acceptable": self.management_responsibility_acceptable,
            "individual_contributor_preferred": self.individual_contributor_preferred,
            "drug_testing_acceptable": self.drug_testing_acceptable,
            "background_check_acceptable": self.background_check_acceptable,
            "security_clearance_required": self.security_clearance_required,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "street_address": self.street_address,
            "candidate_id": self.candidate_id,
        }

    def __repr__(self) -> str:
        return f"<UserJobPreferences({self.id})>"


class UserPreferencePackages(Base):
    __tablename__ = "user_preference_packages"

    package_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('user_candidate_info.id'), nullable=False)
    package_name = Column(String(100), nullable=False)
    package_description = Column(Text)
    salary_minimum = Column(Integer)
    salary_maximum = Column(Integer)
    location_priority = Column(String(200))
    work_arrangement = Column(String(50))
    commute_time_maximum = Column(Integer)
    travel_percentage_maximum = Column(Integer)
    is_active = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    usercandidateinfo = relationship('UserCandidateInfo', back_populates='user_preference_packages')

    def to_dict(self) -> Dict[str, Any]:
        return {
            "package_id": self.package_id,
            "user_id": self.user_id,
            "package_name": self.package_name,
            "package_description": self.package_description,
            "salary_minimum": self.salary_minimum,
            "salary_maximum": self.salary_maximum,
            "location_priority": self.location_priority,
            "work_arrangement": self.work_arrangement,
            "commute_time_maximum": self.commute_time_maximum,
            "travel_percentage_maximum": self.travel_percentage_maximum,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def __repr__(self) -> str:
        return f"<UserPreferencePackages({self.package_id})>"


class UserPreferredIndustries(Base):
    __tablename__ = "user_preferred_industries"

    preference_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('user_candidate_info.id'), unique=True, unique=True, unique=True)
    industry_name = Column(String(100), unique=True, unique=True, unique=True, nullable=False)
    preference_type = Column(String(20), unique=True, unique=True, unique=True, nullable=False)
    priority_level = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    usercandidateinfo = relationship('UserCandidateInfo', back_populates='user_preferred_industries')

    def to_dict(self) -> Dict[str, Any]:
        return {
            "preference_id": self.preference_id,
            "user_id": self.user_id,
            "industry_name": self.industry_name,
            "preference_type": self.preference_type,
            "priority_level": self.priority_level,
            "created_at": self.created_at,
        }

    def __repr__(self) -> str:
        return f"<UserPreferredIndustries({self.preference_id})>"


class WorkExperiences(Base):
    __tablename__ = "work_experiences"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('user_candidate_info.id'), unique=True, unique=True, nullable=False)
    company_name = Column(String(200), nullable=False)
    job_title = Column(String(200), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    is_current = Column(Boolean)
    location = Column(String(200))
    description = Column(Text)
    display_order = Column(Integer, unique=True, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    usercandidateinfo = relationship('UserCandidateInfo', back_populates='work_experiences')

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "company_name": self.company_name,
            "job_title": self.job_title,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "is_current": self.is_current,
            "location": self.location,
            "description": self.description,
            "display_order": self.display_order,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def __repr__(self) -> str:
        return f"<WorkExperiences({self.id})>"


class WorkflowCheckpoints(Base):
    __tablename__ = "workflow_checkpoints"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    checkpoint_id = Column(String(100), unique=True, nullable=False)
    workflow_id = Column(UUID(as_uuid=True), nullable=False)
    stage = Column(String(100), nullable=False)
    checkpoint_data = Column(JSON, nullable=False)
    created_at = Column(DateTime)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "checkpoint_id": self.checkpoint_id,
            "workflow_id": self.workflow_id,
            "stage": self.stage,
            "checkpoint_data": self.checkpoint_data,
            "created_at": self.created_at,
        }

    def __repr__(self) -> str:
        return f"<WorkflowCheckpoints({self.id})>"


