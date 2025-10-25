"""
Auto-generated Pydantic Schemas
Generated from database schema on 2025-10-24 02:33:15
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, date
from typing import Dict, Any, List, Optional
from uuid import UUID

class AnalyzedJobsBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pre_analyzed_job_id: Optional[str] = None
    company_id: Optional[str] = None
    job_title: str
    job_description: Optional[str] = None
    job_number: Optional[str] = None
    salary_low: Optional[int] = None
    salary_high: Optional[int] = None
    salary_period: Optional[str] = None
    compensation_currency: Optional[str] = None
    equity_stock_options: Optional[bool] = None
    commission_or_performance_incentive: Optional[str] = None
    est_total_compensation: Optional[str] = None
    remote_options: Optional[str] = None
    job_type: Optional[str] = None
    in_office_requirements: Optional[str] = None
    office_address: Optional[str] = None
    office_city: Optional[str] = None
    office_province: Optional[str] = None
    office_country: Optional[str] = None
    working_hours_per_week: Optional[int] = None
    work_schedule: Optional[str] = None
    specific_schedule: Optional[str] = None
    travel_requirements: Optional[str] = None
    is_supervisor: Optional[bool] = None
    department: Optional[str] = None
    industry: Optional[str] = None
    sub_industry: Optional[str] = None
    job_function: Optional[str] = None
    seniority_level: Optional[str] = None
    supervision_count: Optional[int] = None
    budget_size_category: Optional[str] = None
    company_size_category: Optional[str] = None
    application_deadline: Optional[date] = None
    application_email: Optional[str] = None
    application_method: Optional[str] = None
    special_instructions: Optional[str] = None
    primary_source_url: Optional[str] = None
    posted_date: Optional[date] = None
    ai_analysis_completed: Optional[bool] = None
    primary_industry: Optional[str] = None
    authenticity_score: Optional[float] = None
    deduplication_key: Optional[str] = None
    application_status: Optional[str] = None
    last_application_attempt: Optional[datetime] = None
    eligibility_flag: Optional[bool] = None
    prestige_factor: Optional[int] = None
    prestige_reasoning: Optional[str] = None
    estimated_stress_level: Optional[int] = None
    stress_reasoning: Optional[str] = None
    analysis_date: Optional[datetime] = None
    gemini_model_used: Optional[str] = None
    analysis_tokens_used: Optional[int] = None
    job_id: Optional[str] = None
    hiring_manager: Optional[str] = None
    reporting_to: Optional[str] = None
    job_title_extracted: Optional[str] = None
    company_name_extracted: Optional[str] = None
    additional_insights: Optional[str] = None


class AnalyzedJobsCreate(AnalyzedJobsBase):
    pass


class AnalyzedJobsUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pre_analyzed_job_id: Optional[str] = None
    company_id: Optional[str] = None
    job_title: Optional[str] = None
    job_description: Optional[str] = None
    job_number: Optional[str] = None
    salary_low: Optional[int] = None
    salary_high: Optional[int] = None
    salary_period: Optional[str] = None
    compensation_currency: Optional[str] = None
    equity_stock_options: Optional[bool] = None
    commission_or_performance_incentive: Optional[str] = None
    est_total_compensation: Optional[str] = None
    remote_options: Optional[str] = None
    job_type: Optional[str] = None
    in_office_requirements: Optional[str] = None
    office_address: Optional[str] = None
    office_city: Optional[str] = None
    office_province: Optional[str] = None
    office_country: Optional[str] = None
    working_hours_per_week: Optional[int] = None
    work_schedule: Optional[str] = None
    specific_schedule: Optional[str] = None
    travel_requirements: Optional[str] = None
    is_supervisor: Optional[bool] = None
    department: Optional[str] = None
    industry: Optional[str] = None
    sub_industry: Optional[str] = None
    job_function: Optional[str] = None
    seniority_level: Optional[str] = None
    supervision_count: Optional[int] = None
    budget_size_category: Optional[str] = None
    company_size_category: Optional[str] = None
    application_deadline: Optional[date] = None
    application_email: Optional[str] = None
    application_method: Optional[str] = None
    special_instructions: Optional[str] = None
    primary_source_url: Optional[str] = None
    posted_date: Optional[date] = None
    ai_analysis_completed: Optional[bool] = None
    primary_industry: Optional[str] = None
    authenticity_score: Optional[float] = None
    deduplication_key: Optional[str] = None
    application_status: Optional[str] = None
    last_application_attempt: Optional[datetime] = None
    eligibility_flag: Optional[bool] = None
    prestige_factor: Optional[int] = None
    prestige_reasoning: Optional[str] = None
    estimated_stress_level: Optional[int] = None
    stress_reasoning: Optional[str] = None
    analysis_date: Optional[datetime] = None
    gemini_model_used: Optional[str] = None
    analysis_tokens_used: Optional[int] = None
    job_id: Optional[str] = None
    hiring_manager: Optional[str] = None
    reporting_to: Optional[str] = None
    job_title_extracted: Optional[str] = None
    company_name_extracted: Optional[str] = None
    additional_insights: Optional[str] = None


class AnalyzedJobsResponse(AnalyzedJobsBase):
    id: str
    created_at: Optional[datetime] = None


class ApifyApplicationSubmissionsBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    submission_id: str
    application_id: Optional[str] = None
    job_id: str
    actor_run_id: Optional[str] = None
    status: str
    form_platform: str
    form_type: Optional[str] = None
    fields_filled: Optional[Dict[str, Any]] = None
    submission_confirmed: Optional[bool] = None
    confirmation_message: Optional[str] = None
    screenshot_urls: Optional[Dict[str, Any]] = None
    screenshot_metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    submitted_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None
    review_notes: Optional[str] = None


class ApifyApplicationSubmissionsCreate(ApifyApplicationSubmissionsBase):
    pass


class ApifyApplicationSubmissionsUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    submission_id: Optional[str] = None
    application_id: Optional[str] = None
    job_id: Optional[str] = None
    actor_run_id: Optional[str] = None
    status: Optional[str] = None
    form_platform: Optional[str] = None
    form_type: Optional[str] = None
    fields_filled: Optional[Dict[str, Any]] = None
    submission_confirmed: Optional[bool] = None
    confirmation_message: Optional[str] = None
    screenshot_urls: Optional[Dict[str, Any]] = None
    screenshot_metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    submitted_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None
    review_notes: Optional[str] = None


class ApifyApplicationSubmissionsResponse(ApifyApplicationSubmissionsBase):
    created_at: datetime
    updated_at: datetime


class ApplicationDocumentsBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document_id: str
    job_application_id: Optional[str] = None
    document_type: str
    document_name: str
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    sent_timestamp: datetime


class ApplicationDocumentsCreate(ApplicationDocumentsBase):
    pass


class ApplicationDocumentsUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document_id: Optional[str] = None
    job_application_id: Optional[str] = None
    document_type: Optional[str] = None
    document_name: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    sent_timestamp: Optional[datetime] = None


class ApplicationDocumentsResponse(ApplicationDocumentsBase):


class ApplicationSettingsBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    setting_key: str
    setting_value: Optional[str] = None
    setting_type: Optional[str] = None
    description: Optional[str] = None


class ApplicationSettingsCreate(ApplicationSettingsBase):
    pass


class ApplicationSettingsUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    setting_key: Optional[str] = None
    setting_value: Optional[str] = None
    setting_type: Optional[str] = None
    description: Optional[str] = None
    updated_at: Optional[datetime] = None


class ApplicationSettingsResponse(ApplicationSettingsBase):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CanadianSpellingsBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    american_spelling: str
    canadian_spelling: str
    status: Optional[str] = None
    created_date: Optional[date] = None


class CanadianSpellingsCreate(CanadianSpellingsBase):
    pass


class CanadianSpellingsUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    american_spelling: Optional[str] = None
    canadian_spelling: Optional[str] = None
    status: Optional[str] = None
    created_date: Optional[date] = None


class CanadianSpellingsResponse(CanadianSpellingsBase):
    id: str


class CleanedJobScrapeSourcesBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    source_id: str
    cleaned_job_id: Optional[str] = None
    original_scrape_id: str
    source_priority: Optional[int] = None
    merge_timestamp: Optional[datetime] = None
    processed_to_jobs: Optional[bool] = None
    job_id: Optional[str] = None
    processed_at: Optional[datetime] = None


class CleanedJobScrapeSourcesCreate(CleanedJobScrapeSourcesBase):
    pass


class CleanedJobScrapeSourcesUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    source_id: Optional[str] = None
    cleaned_job_id: Optional[str] = None
    original_scrape_id: Optional[str] = None
    source_priority: Optional[int] = None
    merge_timestamp: Optional[datetime] = None
    processed_to_jobs: Optional[bool] = None
    job_id: Optional[str] = None
    processed_at: Optional[datetime] = None


class CleanedJobScrapeSourcesResponse(CleanedJobScrapeSourcesBase):


class CleanedJobScrapesBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    cleaned_job_id: str
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    location_city: Optional[str] = None
    location_province: Optional[str] = None
    location_country: Optional[str] = None
    work_arrangement: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = None
    salary_period: Optional[str] = None
    job_description: Optional[str] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    industry: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    posting_date: Optional[date] = None
    application_deadline: Optional[date] = None
    external_job_id: Optional[str] = None
    source_website: str
    application_url: Optional[str] = None
    is_expired: Optional[bool] = None
    cleaned_timestamp: Optional[datetime] = None
    last_seen_timestamp: Optional[datetime] = None
    processing_notes: Optional[str] = None
    location_street_address: Optional[str] = None
    application_email: Optional[str] = None
    confidence_score: Optional[float] = None
    duplicates_count: Optional[int] = None


class CleanedJobScrapesCreate(CleanedJobScrapesBase):
    pass


class CleanedJobScrapesUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    cleaned_job_id: Optional[str] = None
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    location_city: Optional[str] = None
    location_province: Optional[str] = None
    location_country: Optional[str] = None
    work_arrangement: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = None
    salary_period: Optional[str] = None
    job_description: Optional[str] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    industry: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    posting_date: Optional[date] = None
    application_deadline: Optional[date] = None
    external_job_id: Optional[str] = None
    source_website: Optional[str] = None
    application_url: Optional[str] = None
    is_expired: Optional[bool] = None
    cleaned_timestamp: Optional[datetime] = None
    last_seen_timestamp: Optional[datetime] = None
    processing_notes: Optional[str] = None
    location_street_address: Optional[str] = None
    application_email: Optional[str] = None
    confidence_score: Optional[float] = None
    duplicates_count: Optional[int] = None


class CleanedJobScrapesResponse(CleanedJobScrapesBase):


class CompaniesBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    domain: Optional[str] = None
    industry: Optional[str] = None
    sub_industry: Optional[str] = None
    size_range: Optional[str] = None
    employee_count_min: Optional[int] = None
    employee_count_max: Optional[int] = None
    headquarters_location: Optional[str] = None
    founded_year: Optional[int] = None
    company_type: Optional[str] = None
    company_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    glassdoor_url: Optional[str] = None
    company_description: Optional[str] = None
    strategic_mission: Optional[str] = None
    strategic_values: Optional[str] = None
    recent_news: Optional[str] = None


class CompaniesCreate(CompaniesBase):
    pass


class CompaniesUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: Optional[str] = None
    domain: Optional[str] = None
    industry: Optional[str] = None
    sub_industry: Optional[str] = None
    size_range: Optional[str] = None
    employee_count_min: Optional[int] = None
    employee_count_max: Optional[int] = None
    headquarters_location: Optional[str] = None
    founded_year: Optional[int] = None
    company_type: Optional[str] = None
    company_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    glassdoor_url: Optional[str] = None
    company_description: Optional[str] = None
    strategic_mission: Optional[str] = None
    strategic_values: Optional[str] = None
    recent_news: Optional[str] = None


class CompaniesResponse(CompaniesBase):
    id: str
    created_at: Optional[datetime] = None


class ConsistencyValidationLogsBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    validation_run_id: str
    issue_type: Optional[str] = None
    severity: Optional[str] = None
    description: Optional[str] = None
    affected_record_count: Optional[int] = None
    correctable: Optional[bool] = None
    correction_applied: Optional[bool] = None


class ConsistencyValidationLogsCreate(ConsistencyValidationLogsBase):
    pass


class ConsistencyValidationLogsUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    validation_run_id: Optional[str] = None
    issue_type: Optional[str] = None
    severity: Optional[str] = None
    description: Optional[str] = None
    affected_record_count: Optional[int] = None
    correctable: Optional[bool] = None
    correction_applied: Optional[bool] = None


class ConsistencyValidationLogsResponse(ConsistencyValidationLogsBase):
    id: str
    created_at: Optional[datetime] = None


class DashboardMetricsDailyBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    metric_date: date
    jobs_scraped_count: Optional[int] = None
    jobs_cleaned_count: Optional[int] = None
    jobs_deduplicated_count: Optional[int] = None
    scraping_errors_count: Optional[int] = None
    scraping_avg_duration_ms: Optional[int] = None
    scraping_peak_hour: Optional[int] = None
    jobs_analyzed_count: Optional[int] = None
    ai_requests_sent: Optional[int] = None
    ai_tokens_input: Optional[int] = None
    ai_tokens_output: Optional[int] = None
    ai_cost_incurred: Optional[float] = None
    ai_avg_duration_ms: Optional[int] = None
    ai_model_used: Optional[str] = None
    applications_sent_count: Optional[int] = None
    applications_success_count: Optional[int] = None
    applications_failed_count: Optional[int] = None
    documents_generated_count: Optional[int] = None
    application_avg_duration_ms: Optional[int] = None
    success_rate: Optional[float] = None
    pipeline_conversion_rate: Optional[float] = None
    pipeline_bottleneck: Optional[str] = None
    total_pipeline_jobs: Optional[int] = None
    jobs_trend_pct: Optional[float] = None
    applications_trend_pct: Optional[float] = None


class DashboardMetricsDailyCreate(DashboardMetricsDailyBase):
    pass


class DashboardMetricsDailyUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    metric_date: Optional[date] = None
    jobs_scraped_count: Optional[int] = None
    jobs_cleaned_count: Optional[int] = None
    jobs_deduplicated_count: Optional[int] = None
    scraping_errors_count: Optional[int] = None
    scraping_avg_duration_ms: Optional[int] = None
    scraping_peak_hour: Optional[int] = None
    jobs_analyzed_count: Optional[int] = None
    ai_requests_sent: Optional[int] = None
    ai_tokens_input: Optional[int] = None
    ai_tokens_output: Optional[int] = None
    ai_cost_incurred: Optional[float] = None
    ai_avg_duration_ms: Optional[int] = None
    ai_model_used: Optional[str] = None
    applications_sent_count: Optional[int] = None
    applications_success_count: Optional[int] = None
    applications_failed_count: Optional[int] = None
    documents_generated_count: Optional[int] = None
    application_avg_duration_ms: Optional[int] = None
    success_rate: Optional[float] = None
    pipeline_conversion_rate: Optional[float] = None
    pipeline_bottleneck: Optional[str] = None
    total_pipeline_jobs: Optional[int] = None
    jobs_trend_pct: Optional[float] = None
    applications_trend_pct: Optional[float] = None
    updated_at: Optional[datetime] = None


class DashboardMetricsDailyResponse(DashboardMetricsDailyBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class DashboardMetricsHourlyBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    metric_hour: datetime
    jobs_scraped_count: Optional[int] = None
    jobs_cleaned_count: Optional[int] = None
    jobs_deduplicated_count: Optional[int] = None
    scraping_errors_count: Optional[int] = None
    scraping_avg_duration_ms: Optional[int] = None
    jobs_analyzed_count: Optional[int] = None
    ai_requests_sent: Optional[int] = None
    ai_tokens_input: Optional[int] = None
    ai_tokens_output: Optional[int] = None
    ai_cost_incurred: Optional[float] = None
    ai_avg_duration_ms: Optional[int] = None
    applications_sent_count: Optional[int] = None
    applications_success_count: Optional[int] = None
    applications_failed_count: Optional[int] = None
    documents_generated_count: Optional[int] = None
    application_avg_duration_ms: Optional[int] = None
    pipeline_conversion_rate: Optional[float] = None
    pipeline_bottleneck: Optional[str] = None


class DashboardMetricsHourlyCreate(DashboardMetricsHourlyBase):
    pass


class DashboardMetricsHourlyUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    metric_hour: Optional[datetime] = None
    jobs_scraped_count: Optional[int] = None
    jobs_cleaned_count: Optional[int] = None
    jobs_deduplicated_count: Optional[int] = None
    scraping_errors_count: Optional[int] = None
    scraping_avg_duration_ms: Optional[int] = None
    jobs_analyzed_count: Optional[int] = None
    ai_requests_sent: Optional[int] = None
    ai_tokens_input: Optional[int] = None
    ai_tokens_output: Optional[int] = None
    ai_cost_incurred: Optional[float] = None
    ai_avg_duration_ms: Optional[int] = None
    applications_sent_count: Optional[int] = None
    applications_success_count: Optional[int] = None
    applications_failed_count: Optional[int] = None
    documents_generated_count: Optional[int] = None
    application_avg_duration_ms: Optional[int] = None
    pipeline_conversion_rate: Optional[float] = None
    pipeline_bottleneck: Optional[str] = None
    updated_at: Optional[datetime] = None


class DashboardMetricsHourlyResponse(DashboardMetricsHourlyBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class DataCorrectionsBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    validation_run_id: str
    correction_type: Optional[str] = None
    affected_table: Optional[str] = None
    affected_records: Optional[Dict[str, Any]] = None
    correction_sql: Optional[str] = None
    applied_at: Optional[datetime] = None
    success: Optional[bool] = None


class DataCorrectionsCreate(DataCorrectionsBase):
    pass


class DataCorrectionsUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    validation_run_id: Optional[str] = None
    correction_type: Optional[str] = None
    affected_table: Optional[str] = None
    affected_records: Optional[Dict[str, Any]] = None
    correction_sql: Optional[str] = None
    applied_at: Optional[datetime] = None
    success: Optional[bool] = None


class DataCorrectionsResponse(DataCorrectionsBase):
    id: str


class DocumentJobsBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: str
    file_path: Optional[str] = None
    filename: Optional[str] = None
    file_size: Optional[int] = None
    title: Optional[str] = None
    author: Optional[str] = None
    document_type: str
    status: Optional[str] = None
    completed_at: Optional[datetime] = None
    webhook_data: Optional[Dict[str, Any]] = None
    has_error: Optional[bool] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    storage_type: Optional[str] = None
    object_storage_path: Optional[str] = None


class DocumentJobsCreate(DocumentJobsBase):
    pass


class DocumentJobsUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: Optional[str] = None
    file_path: Optional[str] = None
    filename: Optional[str] = None
    file_size: Optional[int] = None
    title: Optional[str] = None
    author: Optional[str] = None
    document_type: Optional[str] = None
    status: Optional[str] = None
    completed_at: Optional[datetime] = None
    webhook_data: Optional[Dict[str, Any]] = None
    has_error: Optional[bool] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    storage_type: Optional[str] = None
    object_storage_path: Optional[str] = None


class DocumentJobsResponse(DocumentJobsBase):
    created_at: Optional[datetime] = None


class DocumentSentencesBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sentence_id: str
    document_job_id: Optional[str] = None
    sentence_text: str
    tone_score: Optional[float] = None
    sentiment_category: Optional[str] = None
    confidence_score: Optional[float] = None
    word_count: Optional[int] = None
    sentence_order: Optional[int] = None


class DocumentSentencesCreate(DocumentSentencesBase):
    pass


class DocumentSentencesUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sentence_id: Optional[str] = None
    document_job_id: Optional[str] = None
    sentence_text: Optional[str] = None
    tone_score: Optional[float] = None
    sentiment_category: Optional[str] = None
    confidence_score: Optional[float] = None
    word_count: Optional[int] = None
    sentence_order: Optional[int] = None


class DocumentSentencesResponse(DocumentSentencesBase):
    created_at: Optional[datetime] = None


class DocumentTemplateMetadataBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document_type: str
    resume_general_section_count: Optional[int] = None
    resume_constituent_section_count: Optional[int] = None
    cover_par_one: Optional[int] = None
    cover_par_two: Optional[int] = None
    cover_par_three: Optional[int] = None
    count: Optional[int] = None
    template_file_path: Optional[str] = None


class DocumentTemplateMetadataCreate(DocumentTemplateMetadataBase):
    pass


class DocumentTemplateMetadataUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document_type: Optional[str] = None
    resume_general_section_count: Optional[int] = None
    resume_constituent_section_count: Optional[int] = None
    cover_par_one: Optional[int] = None
    cover_par_two: Optional[int] = None
    cover_par_three: Optional[int] = None
    count: Optional[int] = None
    template_file_path: Optional[str] = None


class DocumentTemplateMetadataResponse(DocumentTemplateMetadataBase):
    id: int


class DocumentToneAnalysisBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document_type: str
    sentences: Dict[str, Any]
    tone_jump_score: Optional[float] = None
    tone_coherence_score: Optional[float] = None
    total_tone_travel: Optional[float] = None
    average_tone_jump: Optional[float] = None


class DocumentToneAnalysisCreate(DocumentToneAnalysisBase):
    pass


class DocumentToneAnalysisUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document_type: Optional[str] = None
    sentences: Optional[Dict[str, Any]] = None
    tone_jump_score: Optional[float] = None
    tone_coherence_score: Optional[float] = None
    total_tone_travel: Optional[float] = None
    average_tone_jump: Optional[float] = None


class DocumentToneAnalysisResponse(DocumentToneAnalysisBase):
    id: str


class ErrorLogBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    error_id: str
    timestamp: datetime
    session_id: Optional[str] = None
    stage_name: Optional[str] = None
    error_category: str
    severity: str
    error_message: str
    error_details: Optional[str] = None
    exception_type: Optional[str] = None
    stack_trace: Optional[str] = None
    context_data: Optional[Dict[str, Any]] = None
    retry_count: Optional[int] = None
    resolved: Optional[bool] = None
    resolution_notes: Optional[str] = None


class ErrorLogCreate(ErrorLogBase):
    pass


class ErrorLogUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    error_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    session_id: Optional[str] = None
    stage_name: Optional[str] = None
    error_category: Optional[str] = None
    severity: Optional[str] = None
    error_message: Optional[str] = None
    error_details: Optional[str] = None
    exception_type: Optional[str] = None
    stack_trace: Optional[str] = None
    context_data: Optional[Dict[str, Any]] = None
    retry_count: Optional[int] = None
    resolved: Optional[bool] = None
    resolution_notes: Optional[str] = None


class ErrorLogResponse(ErrorLogBase):
    id: int
    created_at: Optional[datetime] = None


class FailureLogsBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    failure_type: str
    operation_name: str
    workflow_id: Optional[str] = None
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    recovery_attempts: Optional[int] = None
    recovery_successful: Optional[bool] = None
    resolved_at: Optional[datetime] = None


class FailureLogsCreate(FailureLogsBase):
    pass


class FailureLogsUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    failure_type: Optional[str] = None
    operation_name: Optional[str] = None
    workflow_id: Optional[str] = None
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    recovery_attempts: Optional[int] = None
    recovery_successful: Optional[bool] = None
    resolved_at: Optional[datetime] = None


class FailureLogsResponse(FailureLogsBase):
    id: str
    created_at: Optional[datetime] = None


class JobAnalysisQueueBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: str
    priority: Optional[str] = None
    queued_at: Optional[datetime] = None
    attempts: Optional[int] = None
    last_attempt_at: Optional[datetime] = None
    error_message: Optional[str] = None
    status: Optional[str] = None


class JobAnalysisQueueCreate(JobAnalysisQueueBase):
    pass


class JobAnalysisQueueUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: Optional[str] = None
    priority: Optional[str] = None
    queued_at: Optional[datetime] = None
    attempts: Optional[int] = None
    last_attempt_at: Optional[datetime] = None
    error_message: Optional[str] = None
    status: Optional[str] = None


class JobAnalysisQueueResponse(JobAnalysisQueueBase):
    id: int
    created_at: Optional[datetime] = None


class JobAnalysisTiersBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: str
    tier_1_completed: Optional[bool] = None
    tier_1_timestamp: Optional[datetime] = None
    tier_1_tokens_used: Optional[int] = None
    tier_1_model: Optional[str] = None
    tier_1_response_time_ms: Optional[int] = None
    tier_2_completed: Optional[bool] = None
    tier_2_timestamp: Optional[datetime] = None
    tier_2_tokens_used: Optional[int] = None
    tier_2_model: Optional[str] = None
    tier_2_response_time_ms: Optional[int] = None
    tier_3_completed: Optional[bool] = None
    tier_3_timestamp: Optional[datetime] = None
    tier_3_tokens_used: Optional[int] = None
    tier_3_model: Optional[str] = None
    tier_3_response_time_ms: Optional[int] = None


class JobAnalysisTiersCreate(JobAnalysisTiersBase):
    pass


class JobAnalysisTiersUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: Optional[str] = None
    tier_1_completed: Optional[bool] = None
    tier_1_timestamp: Optional[datetime] = None
    tier_1_tokens_used: Optional[int] = None
    tier_1_model: Optional[str] = None
    tier_1_response_time_ms: Optional[int] = None
    tier_2_completed: Optional[bool] = None
    tier_2_timestamp: Optional[datetime] = None
    tier_2_tokens_used: Optional[int] = None
    tier_2_model: Optional[str] = None
    tier_2_response_time_ms: Optional[int] = None
    tier_3_completed: Optional[bool] = None
    tier_3_timestamp: Optional[datetime] = None
    tier_3_tokens_used: Optional[int] = None
    tier_3_model: Optional[str] = None
    tier_3_response_time_ms: Optional[int] = None
    updated_at: Optional[datetime] = None


class JobAnalysisTiersResponse(JobAnalysisTiersBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class JobApplicationTrackingBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tracking_id: str
    job_application_id: Optional[str] = None
    tracking_type: str
    tracking_event: str
    event_timestamp: datetime
    event_data: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class JobApplicationTrackingCreate(JobApplicationTrackingBase):
    pass


class JobApplicationTrackingUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tracking_id: Optional[str] = None
    job_application_id: Optional[str] = None
    tracking_type: Optional[str] = None
    tracking_event: Optional[str] = None
    event_timestamp: Optional[datetime] = None
    event_data: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class JobApplicationTrackingResponse(JobApplicationTrackingBase):


class JobApplicationsBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: Optional[str] = None
    application_date: Optional[datetime] = None
    application_method: Optional[str] = None
    application_status: Optional[str] = None
    email_sent_to: Optional[str] = None
    documents_sent: Optional[List[str]] = None
    tracking_data: Optional[Dict[str, Any]] = None
    first_response_received_at: Optional[datetime] = None
    response_type: Optional[str] = None
    notes: Optional[str] = None
    tone_jump_score: Optional[float] = None
    tone_coherence_score: Optional[float] = None
    total_tone_travel: Optional[float] = None
    last_response_received_at: Optional[datetime] = None


class JobApplicationsCreate(JobApplicationsBase):
    pass


class JobApplicationsUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: Optional[str] = None
    application_date: Optional[datetime] = None
    application_method: Optional[str] = None
    application_status: Optional[str] = None
    email_sent_to: Optional[str] = None
    documents_sent: Optional[List[str]] = None
    tracking_data: Optional[Dict[str, Any]] = None
    first_response_received_at: Optional[datetime] = None
    response_type: Optional[str] = None
    notes: Optional[str] = None
    tone_jump_score: Optional[float] = None
    tone_coherence_score: Optional[float] = None
    total_tone_travel: Optional[float] = None
    last_response_received_at: Optional[datetime] = None


class JobApplicationsResponse(JobApplicationsBase):
    id: str
    created_at: Optional[datetime] = None


class JobAtsKeywordsBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: Optional[str] = None
    keyword: str
    keyword_category: Optional[str] = None
    frequency_in_posting: Optional[int] = None


class JobAtsKeywordsCreate(JobAtsKeywordsBase):
    pass


class JobAtsKeywordsUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: Optional[str] = None
    keyword: Optional[str] = None
    keyword_category: Optional[str] = None
    frequency_in_posting: Optional[int] = None


class JobAtsKeywordsResponse(JobAtsKeywordsBase):
    id: str


class JobBenefitsBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    benefit_id: str
    job_id: Optional[str] = None
    benefit_type: str
    benefit_description: Optional[str] = None
    benefit_value: Optional[str] = None


class JobBenefitsCreate(JobBenefitsBase):
    pass


class JobBenefitsUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    benefit_id: Optional[str] = None
    job_id: Optional[str] = None
    benefit_type: Optional[str] = None
    benefit_description: Optional[str] = None
    benefit_value: Optional[str] = None


class JobBenefitsResponse(JobBenefitsBase):


class JobCertificationsBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: Optional[str] = None
    certification_name: str
    is_required: Optional[bool] = None


class JobCertificationsCreate(JobCertificationsBase):
    pass


class JobCertificationsUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: Optional[str] = None
    certification_name: Optional[str] = None
    is_required: Optional[bool] = None


class JobCertificationsResponse(JobCertificationsBase):
    id: int
    created_at: Optional[datetime] = None


class JobEducationRequirementsBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: str
    degree_level: Optional[str] = None
    field_of_study: Optional[str] = None
    institution_type: Optional[str] = None
    years_required: Optional[int] = None
    is_required: Optional[bool] = None
    alternative_experience: Optional[str] = None


class JobEducationRequirementsCreate(JobEducationRequirementsBase):
    pass


class JobEducationRequirementsUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: Optional[str] = None
    degree_level: Optional[str] = None
    field_of_study: Optional[str] = None
    institution_type: Optional[str] = None
    years_required: Optional[int] = None
    is_required: Optional[bool] = None
    alternative_experience: Optional[str] = None


class JobEducationRequirementsResponse(JobEducationRequirementsBase):
    id: int
    created_at: Optional[datetime] = None


class JobLogsBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    log_id: str
    job_id: str
    timestamp: Optional[datetime] = None
    log_level: Optional[str] = None
    message: str
    details: Optional[Dict[str, Any]] = None


class JobLogsCreate(JobLogsBase):
    pass


class JobLogsUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    log_id: Optional[str] = None
    job_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    log_level: Optional[str] = None
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class JobLogsResponse(JobLogsBase):


class JobPlatformsFoundBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    platform_id: str
    job_id: Optional[str] = None
    platform_name: str
    platform_url: Optional[str] = None
    first_found_at: Optional[datetime] = None


class JobPlatformsFoundCreate(JobPlatformsFoundBase):
    pass


class JobPlatformsFoundUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    platform_id: Optional[str] = None
    job_id: Optional[str] = None
    platform_name: Optional[str] = None
    platform_url: Optional[str] = None
    first_found_at: Optional[datetime] = None


class JobPlatformsFoundResponse(JobPlatformsFoundBase):


class JobRedFlagsDetailsBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: Optional[str] = None
    flag_type: str
    detected: Optional[bool] = None
    details: Optional[str] = None


class JobRedFlagsDetailsCreate(JobRedFlagsDetailsBase):
    pass


class JobRedFlagsDetailsUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: Optional[str] = None
    flag_type: Optional[str] = None
    detected: Optional[bool] = None
    details: Optional[str] = None


class JobRedFlagsDetailsResponse(JobRedFlagsDetailsBase):
    id: int
    created_at: Optional[datetime] = None


class JobRequiredDocumentsBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: Optional[str] = None
    document_type: str
    is_required: Optional[bool] = None


class JobRequiredDocumentsCreate(JobRequiredDocumentsBase):
    pass


class JobRequiredDocumentsUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: Optional[str] = None
    document_type: Optional[str] = None
    is_required: Optional[bool] = None


class JobRequiredDocumentsResponse(JobRequiredDocumentsBase):
    id: int
    created_at: Optional[datetime] = None


class JobRequiredSkillsBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    skill_id: str
    job_id: Optional[str] = None
    skill_name: str
    skill_level: Optional[str] = None
    is_required: Optional[bool] = None


class JobRequiredSkillsCreate(JobRequiredSkillsBase):
    pass


class JobRequiredSkillsUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    skill_id: Optional[str] = None
    job_id: Optional[str] = None
    skill_name: Optional[str] = None
    skill_level: Optional[str] = None
    is_required: Optional[bool] = None


class JobRequiredSkillsResponse(JobRequiredSkillsBase):


class JobSkillsBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    skill_id: str
    job_id: Optional[str] = None
    skill_name: str
    importance_rating: Optional[int] = None
    is_required: Optional[bool] = None
    reasoning: Optional[str] = None


class JobSkillsCreate(JobSkillsBase):
    pass


class JobSkillsUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    skill_id: Optional[str] = None
    job_id: Optional[str] = None
    skill_name: Optional[str] = None
    importance_rating: Optional[int] = None
    is_required: Optional[bool] = None
    reasoning: Optional[str] = None


class JobSkillsResponse(JobSkillsBase):


class JobStressIndicatorsBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: Optional[str] = None
    indicator: str
    description: Optional[str] = None


class JobStressIndicatorsCreate(JobStressIndicatorsBase):
    pass


class JobStressIndicatorsUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: Optional[str] = None
    indicator: Optional[str] = None
    description: Optional[str] = None


class JobStressIndicatorsResponse(JobStressIndicatorsBase):
    id: int
    created_at: Optional[datetime] = None


class JobsBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    company_id: Optional[str] = None
    job_title: str
    job_description: Optional[str] = None
    job_number: Optional[str] = None
    salary_low: Optional[int] = None
    salary_high: Optional[int] = None
    salary_period: Optional[str] = None
    remote_options: Optional[str] = None
    job_type: Optional[str] = None
    is_supervisor: Optional[bool] = None
    department: Optional[str] = None
    industry: Optional[str] = None
    seniority_level: Optional[str] = None
    application_deadline: Optional[date] = None
    is_active: Optional[bool] = None
    application_status: Optional[str] = None
    last_application_attempt: Optional[datetime] = None
    application_method: Optional[str] = None
    analysis_completed: Optional[bool] = None
    consolidation_confidence: Optional[float] = None
    primary_source_url: Optional[str] = None
    posted_date: Optional[date] = None
    title_matches_role: Optional[bool] = None
    mismatch_explanation: Optional[str] = None
    is_authentic: Optional[bool] = None
    authenticity_reasoning: Optional[str] = None
    sub_industry: Optional[str] = None
    job_function: Optional[str] = None
    in_office_requirements: Optional[str] = None
    office_address: Optional[str] = None
    office_city: Optional[str] = None
    office_province: Optional[str] = None
    office_country: Optional[str] = None
    working_hours_per_week: Optional[int] = None
    work_schedule: Optional[str] = None
    specific_schedule: Optional[str] = None
    travel_requirements: Optional[str] = None
    salary_mentioned: Optional[bool] = None
    equity_stock_options: Optional[bool] = None
    commission_or_performance_incentive: Optional[str] = None
    est_total_compensation: Optional[str] = None
    compensation_currency: Optional[str] = None
    application_email: Optional[str] = None
    special_instructions: Optional[str] = None
    estimated_stress_level: Optional[int] = None
    stress_reasoning: Optional[str] = None
    education_requirements: Optional[str] = None
    overall_red_flag_reasoning: Optional[str] = None
    cover_letter_pain_point: Optional[str] = None
    cover_letter_evidence: Optional[str] = None
    cover_letter_solution_angle: Optional[str] = None
    eligibility_flag: Optional[bool] = None
    prestige_factor: Optional[int] = None
    prestige_reasoning: Optional[str] = None
    supervision_count: Optional[int] = None
    budget_size_category: Optional[str] = None
    company_size_category: Optional[str] = None


class JobsCreate(JobsBase):
    pass


class JobsUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    company_id: Optional[str] = None
    job_title: Optional[str] = None
    job_description: Optional[str] = None
    job_number: Optional[str] = None
    salary_low: Optional[int] = None
    salary_high: Optional[int] = None
    salary_period: Optional[str] = None
    remote_options: Optional[str] = None
    job_type: Optional[str] = None
    is_supervisor: Optional[bool] = None
    department: Optional[str] = None
    industry: Optional[str] = None
    seniority_level: Optional[str] = None
    application_deadline: Optional[date] = None
    is_active: Optional[bool] = None
    application_status: Optional[str] = None
    last_application_attempt: Optional[datetime] = None
    application_method: Optional[str] = None
    analysis_completed: Optional[bool] = None
    consolidation_confidence: Optional[float] = None
    primary_source_url: Optional[str] = None
    posted_date: Optional[date] = None
    title_matches_role: Optional[bool] = None
    mismatch_explanation: Optional[str] = None
    is_authentic: Optional[bool] = None
    authenticity_reasoning: Optional[str] = None
    sub_industry: Optional[str] = None
    job_function: Optional[str] = None
    in_office_requirements: Optional[str] = None
    office_address: Optional[str] = None
    office_city: Optional[str] = None
    office_province: Optional[str] = None
    office_country: Optional[str] = None
    working_hours_per_week: Optional[int] = None
    work_schedule: Optional[str] = None
    specific_schedule: Optional[str] = None
    travel_requirements: Optional[str] = None
    salary_mentioned: Optional[bool] = None
    equity_stock_options: Optional[bool] = None
    commission_or_performance_incentive: Optional[str] = None
    est_total_compensation: Optional[str] = None
    compensation_currency: Optional[str] = None
    application_email: Optional[str] = None
    special_instructions: Optional[str] = None
    estimated_stress_level: Optional[int] = None
    stress_reasoning: Optional[str] = None
    education_requirements: Optional[str] = None
    overall_red_flag_reasoning: Optional[str] = None
    cover_letter_pain_point: Optional[str] = None
    cover_letter_evidence: Optional[str] = None
    cover_letter_solution_angle: Optional[str] = None
    eligibility_flag: Optional[bool] = None
    prestige_factor: Optional[int] = None
    prestige_reasoning: Optional[str] = None
    supervision_count: Optional[int] = None
    budget_size_category: Optional[str] = None
    company_size_category: Optional[str] = None


class JobsResponse(JobsBase):
    id: str
    created_at: Optional[datetime] = None


class KeywordFiltersBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    keyword: str
    status: Optional[str] = None
    created_date: Optional[date] = None


class KeywordFiltersCreate(KeywordFiltersBase):
    pass


class KeywordFiltersUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    keyword: Optional[str] = None
    status: Optional[str] = None
    created_date: Optional[date] = None


class KeywordFiltersResponse(KeywordFiltersBase):
    id: str


class LinkClicksBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    click_id: str
    tracking_id: str
    clicked_at: Optional[datetime] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referrer_url: Optional[str] = None
    session_id: Optional[str] = None
    click_source: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class LinkClicksCreate(LinkClicksBase):
    pass


class LinkClicksUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    click_id: Optional[str] = None
    tracking_id: Optional[str] = None
    clicked_at: Optional[datetime] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referrer_url: Optional[str] = None
    session_id: Optional[str] = None
    click_source: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class LinkClicksResponse(LinkClicksBase):


class LinkTrackingBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tracking_id: str
    job_id: Optional[str] = None
    application_id: Optional[str] = None
    link_function: str
    link_type: str
    original_url: str
    redirect_url: str
    created_by: Optional[str] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None


class LinkTrackingCreate(LinkTrackingBase):
    pass


class LinkTrackingUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tracking_id: Optional[str] = None
    job_id: Optional[str] = None
    application_id: Optional[str] = None
    link_function: Optional[str] = None
    link_type: Optional[str] = None
    original_url: Optional[str] = None
    redirect_url: Optional[str] = None
    created_by: Optional[str] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None


class LinkTrackingResponse(LinkTrackingBase):
    created_at: Optional[datetime] = None


class PerformanceMetricsBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    stage_name: str
    api_call_type: str
    response_time_ms: Optional[int] = None
    success: bool
    error_message: Optional[str] = None
    cost_estimate: Optional[float] = None
    batch_size: Optional[int] = None
    sentences_processed: Optional[int] = None
    processing_date: Optional[datetime] = None
    model_used: Optional[str] = None
    session_id: Optional[str] = None


class PerformanceMetricsCreate(PerformanceMetricsBase):
    pass


class PerformanceMetricsUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    stage_name: Optional[str] = None
    api_call_type: Optional[str] = None
    response_time_ms: Optional[int] = None
    success: Optional[bool] = None
    error_message: Optional[str] = None
    cost_estimate: Optional[float] = None
    batch_size: Optional[int] = None
    sentences_processed: Optional[int] = None
    processing_date: Optional[datetime] = None
    model_used: Optional[str] = None
    session_id: Optional[str] = None


class PerformanceMetricsResponse(PerformanceMetricsBase):
    id: str


class PreAnalyzedJobsBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    cleaned_scrape_id: Optional[str] = None
    company_id: Optional[str] = None
    job_title: str
    company_name: Optional[str] = None
    location_city: Optional[str] = None
    location_province: Optional[str] = None
    location_country: Optional[str] = None
    work_arrangement: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = None
    salary_period: Optional[str] = None
    job_description: Optional[str] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    industry: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    posting_date: Optional[date] = None
    application_deadline: Optional[date] = None
    external_job_id: Optional[str] = None
    source_website: Optional[str] = None
    application_url: Optional[str] = None
    application_email: Optional[str] = None
    confidence_score: Optional[float] = None
    duplicates_count: Optional[int] = None
    deduplication_key: Optional[str] = None
    is_active: Optional[bool] = None
    queued_for_analysis: Optional[bool] = None
    processed_at: Optional[datetime] = None


class PreAnalyzedJobsCreate(PreAnalyzedJobsBase):
    pass


class PreAnalyzedJobsUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    cleaned_scrape_id: Optional[str] = None
    company_id: Optional[str] = None
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    location_city: Optional[str] = None
    location_province: Optional[str] = None
    location_country: Optional[str] = None
    work_arrangement: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = None
    salary_period: Optional[str] = None
    job_description: Optional[str] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    industry: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    posting_date: Optional[date] = None
    application_deadline: Optional[date] = None
    external_job_id: Optional[str] = None
    source_website: Optional[str] = None
    application_url: Optional[str] = None
    application_email: Optional[str] = None
    confidence_score: Optional[float] = None
    duplicates_count: Optional[int] = None
    deduplication_key: Optional[str] = None
    is_active: Optional[bool] = None
    queued_for_analysis: Optional[bool] = None
    processed_at: Optional[datetime] = None


class PreAnalyzedJobsResponse(PreAnalyzedJobsBase):
    id: str
    created_at: Optional[datetime] = None


class RawJobScrapesBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    scrape_id: str
    source_website: str
    source_url: str
    full_application_url: Optional[str] = None
    scrape_timestamp: Optional[datetime] = None
    raw_data: Dict[str, Any]
    scraper_used: Optional[str] = None
    scraper_run_id: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    success_status: Optional[bool] = None
    error_message: Optional[str] = None
    response_time_ms: Optional[int] = None
    data_size_bytes: Optional[int] = None


class RawJobScrapesCreate(RawJobScrapesBase):
    pass


class RawJobScrapesUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    scrape_id: Optional[str] = None
    source_website: Optional[str] = None
    source_url: Optional[str] = None
    full_application_url: Optional[str] = None
    scrape_timestamp: Optional[datetime] = None
    raw_data: Optional[Dict[str, Any]] = None
    scraper_used: Optional[str] = None
    scraper_run_id: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    success_status: Optional[bool] = None
    error_message: Optional[str] = None
    response_time_ms: Optional[int] = None
    data_size_bytes: Optional[int] = None


class RawJobScrapesResponse(RawJobScrapesBase):


class RecoveryStatisticsBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    date: Optional[date] = None
    failure_type: Optional[str] = None
    total_failures: Optional[int] = None
    successful_recoveries: Optional[int] = None
    failed_recoveries: Optional[int] = None
    average_recovery_time: Optional[float] = None


class RecoveryStatisticsCreate(RecoveryStatisticsBase):
    pass


class RecoveryStatisticsUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    date: Optional[date] = None
    failure_type: Optional[str] = None
    total_failures: Optional[int] = None
    successful_recoveries: Optional[int] = None
    failed_recoveries: Optional[int] = None
    average_recovery_time: Optional[float] = None


class RecoveryStatisticsResponse(RecoveryStatisticsBase):
    id: str
    created_at: Optional[datetime] = None


class SecurityDetectionsBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: Optional[str] = None
    detection_type: str
    severity: str
    pattern_matched: Optional[str] = None
    text_sample: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    detected_at: Optional[datetime] = None
    handled: Optional[bool] = None
    action_taken: Optional[str] = None


class SecurityDetectionsCreate(SecurityDetectionsBase):
    pass


class SecurityDetectionsUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: Optional[str] = None
    detection_type: Optional[str] = None
    severity: Optional[str] = None
    pattern_matched: Optional[str] = None
    text_sample: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    detected_at: Optional[datetime] = None
    handled: Optional[bool] = None
    action_taken: Optional[str] = None


class SecurityDetectionsResponse(SecurityDetectionsBase):
    id: str


class SecurityTestTableBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)



class SecurityTestTableCreate(SecurityTestTableBase):
    pass


class SecurityTestTableUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)



class SecurityTestTableResponse(SecurityTestTableBase):
    id: Optional[int] = None


class SentenceBankCoverLetterBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    content_text: str
    tone: Optional[str] = None
    tone_strength: Optional[float] = None
    status: Optional[str] = None
    position_label: Optional[str] = None
    matches_job_skill: Optional[str] = None
    variable: Optional[bool] = None
    keyword_filter_status: Optional[str] = None
    keyword_filter_date: Optional[date] = None
    keyword_filter_error_message: Optional[str] = None
    truthfulness_status: Optional[str] = None
    truthfulness_date: Optional[date] = None
    truthfulness_model: Optional[str] = None
    truthfulness_error_message: Optional[str] = None
    canadian_spelling_status: Optional[str] = None
    canadian_spelling_date: Optional[date] = None
    tone_analysis_status: Optional[str] = None
    tone_analysis_date: Optional[date] = None
    tone_analysis_model: Optional[str] = None
    tone_analysis_error_message: Optional[str] = None
    skill_analysis_status: Optional[str] = None
    skill_analysis_date: Optional[date] = None
    skill_analysis_model: Optional[str] = None
    skill_analysis_error_message: Optional[str] = None


class SentenceBankCoverLetterCreate(SentenceBankCoverLetterBase):
    pass


class SentenceBankCoverLetterUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    content_text: Optional[str] = None
    tone: Optional[str] = None
    tone_strength: Optional[float] = None
    status: Optional[str] = None
    position_label: Optional[str] = None
    matches_job_skill: Optional[str] = None
    variable: Optional[bool] = None
    keyword_filter_status: Optional[str] = None
    keyword_filter_date: Optional[date] = None
    keyword_filter_error_message: Optional[str] = None
    truthfulness_status: Optional[str] = None
    truthfulness_date: Optional[date] = None
    truthfulness_model: Optional[str] = None
    truthfulness_error_message: Optional[str] = None
    canadian_spelling_status: Optional[str] = None
    canadian_spelling_date: Optional[date] = None
    tone_analysis_status: Optional[str] = None
    tone_analysis_date: Optional[date] = None
    tone_analysis_model: Optional[str] = None
    tone_analysis_error_message: Optional[str] = None
    skill_analysis_status: Optional[str] = None
    skill_analysis_date: Optional[date] = None
    skill_analysis_model: Optional[str] = None
    skill_analysis_error_message: Optional[str] = None


class SentenceBankCoverLetterResponse(SentenceBankCoverLetterBase):
    id: str
    created_at: Optional[datetime] = None


class SentenceBankResumeBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    content_text: str
    body_section: Optional[str] = None
    tone: Optional[str] = None
    tone_strength: Optional[float] = None
    status: Optional[str] = None
    matches_job_skill: Optional[str] = None
    experience_id: Optional[str] = None
    keyword_filter_status: Optional[str] = None
    keyword_filter_date: Optional[date] = None
    keyword_filter_error_message: Optional[str] = None
    truthfulness_status: Optional[str] = None
    truthfulness_date: Optional[date] = None
    truthfulness_model: Optional[str] = None
    truthfulness_error_message: Optional[str] = None
    canadian_spelling_status: Optional[str] = None
    canadian_spelling_date: Optional[date] = None
    tone_analysis_status: Optional[str] = None
    tone_analysis_date: Optional[date] = None
    tone_analysis_model: Optional[str] = None
    tone_analysis_error_message: Optional[str] = None
    skill_analysis_status: Optional[str] = None
    skill_analysis_date: Optional[date] = None
    skill_analysis_model: Optional[str] = None
    skill_analysis_error_message: Optional[str] = None


class SentenceBankResumeCreate(SentenceBankResumeBase):
    pass


class SentenceBankResumeUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    content_text: Optional[str] = None
    body_section: Optional[str] = None
    tone: Optional[str] = None
    tone_strength: Optional[float] = None
    status: Optional[str] = None
    matches_job_skill: Optional[str] = None
    experience_id: Optional[str] = None
    keyword_filter_status: Optional[str] = None
    keyword_filter_date: Optional[date] = None
    keyword_filter_error_message: Optional[str] = None
    truthfulness_status: Optional[str] = None
    truthfulness_date: Optional[date] = None
    truthfulness_model: Optional[str] = None
    truthfulness_error_message: Optional[str] = None
    canadian_spelling_status: Optional[str] = None
    canadian_spelling_date: Optional[date] = None
    tone_analysis_status: Optional[str] = None
    tone_analysis_date: Optional[date] = None
    tone_analysis_model: Optional[str] = None
    tone_analysis_error_message: Optional[str] = None
    skill_analysis_status: Optional[str] = None
    skill_analysis_date: Optional[date] = None
    skill_analysis_model: Optional[str] = None
    skill_analysis_error_message: Optional[str] = None


class SentenceBankResumeResponse(SentenceBankResumeBase):
    id: str
    created_at: Optional[datetime] = None


class UserCandidateInfoBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    mailing_address: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    calendly_url: Optional[str] = None


class UserCandidateInfoCreate(UserCandidateInfoBase):
    pass


class UserCandidateInfoUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    mailing_address: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    calendly_url: Optional[str] = None
    updated_at: Optional[datetime] = None


class UserCandidateInfoResponse(UserCandidateInfoBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserJobPreferencesBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: Optional[str] = None
    salary_minimum: Optional[int] = None
    hourly_rate_minimum: Optional[float] = None
    bonus_expected: Optional[bool] = None
    stock_options_preferred: Optional[bool] = None
    hours_per_week_minimum: Optional[int] = None
    hours_per_week_maximum: Optional[int] = None
    flexible_hours_required: Optional[bool] = None
    overtime_acceptable: Optional[bool] = None
    work_arrangement: Optional[str] = None
    travel_percentage_maximum: Optional[int] = None
    preferred_city: Optional[str] = None
    preferred_province_state: Optional[str] = None
    preferred_country: Optional[str] = None
    commute_time_maximum: Optional[int] = None
    relocation_acceptable: Optional[bool] = None
    health_insurance_required: Optional[bool] = None
    dental_insurance_required: Optional[bool] = None
    vision_insurance_preferred: Optional[bool] = None
    health_benefits_dollar_value: Optional[int] = None
    retirement_matching_minimum: Optional[float] = None
    vacation_days_minimum: Optional[int] = None
    sick_days_minimum: Optional[int] = None
    parental_leave_required: Optional[bool] = None
    parental_leave_weeks_minimum: Optional[int] = None
    training_budget_minimum: Optional[int] = None
    conference_attendance_preferred: Optional[bool] = None
    certification_support_required: Optional[bool] = None
    mentorship_program_preferred: Optional[bool] = None
    career_advancement_timeline: Optional[int] = None
    company_size_minimum: Optional[int] = None
    company_size_maximum: Optional[int] = None
    startup_acceptable: Optional[bool] = None
    public_company_preferred: Optional[bool] = None
    industry_prestige_importance: Optional[int] = None
    company_mission_alignment_importance: Optional[int] = None
    acceptable_stress: Optional[int] = None
    experience_level_minimum: Optional[str] = None
    experience_level_maximum: Optional[str] = None
    management_responsibility_acceptable: Optional[bool] = None
    individual_contributor_preferred: Optional[bool] = None
    drug_testing_acceptable: Optional[bool] = None
    background_check_acceptable: Optional[bool] = None
    security_clearance_required: Optional[bool] = None
    is_active: Optional[bool] = None
    street_address: Optional[str] = None
    candidate_id: Optional[str] = None


class UserJobPreferencesCreate(UserJobPreferencesBase):
    pass


class UserJobPreferencesUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: Optional[str] = None
    salary_minimum: Optional[int] = None
    hourly_rate_minimum: Optional[float] = None
    bonus_expected: Optional[bool] = None
    stock_options_preferred: Optional[bool] = None
    hours_per_week_minimum: Optional[int] = None
    hours_per_week_maximum: Optional[int] = None
    flexible_hours_required: Optional[bool] = None
    overtime_acceptable: Optional[bool] = None
    work_arrangement: Optional[str] = None
    travel_percentage_maximum: Optional[int] = None
    preferred_city: Optional[str] = None
    preferred_province_state: Optional[str] = None
    preferred_country: Optional[str] = None
    commute_time_maximum: Optional[int] = None
    relocation_acceptable: Optional[bool] = None
    health_insurance_required: Optional[bool] = None
    dental_insurance_required: Optional[bool] = None
    vision_insurance_preferred: Optional[bool] = None
    health_benefits_dollar_value: Optional[int] = None
    retirement_matching_minimum: Optional[float] = None
    vacation_days_minimum: Optional[int] = None
    sick_days_minimum: Optional[int] = None
    parental_leave_required: Optional[bool] = None
    parental_leave_weeks_minimum: Optional[int] = None
    training_budget_minimum: Optional[int] = None
    conference_attendance_preferred: Optional[bool] = None
    certification_support_required: Optional[bool] = None
    mentorship_program_preferred: Optional[bool] = None
    career_advancement_timeline: Optional[int] = None
    company_size_minimum: Optional[int] = None
    company_size_maximum: Optional[int] = None
    startup_acceptable: Optional[bool] = None
    public_company_preferred: Optional[bool] = None
    industry_prestige_importance: Optional[int] = None
    company_mission_alignment_importance: Optional[int] = None
    acceptable_stress: Optional[int] = None
    experience_level_minimum: Optional[str] = None
    experience_level_maximum: Optional[str] = None
    management_responsibility_acceptable: Optional[bool] = None
    individual_contributor_preferred: Optional[bool] = None
    drug_testing_acceptable: Optional[bool] = None
    background_check_acceptable: Optional[bool] = None
    security_clearance_required: Optional[bool] = None
    is_active: Optional[bool] = None
    updated_at: Optional[datetime] = None
    street_address: Optional[str] = None
    candidate_id: Optional[str] = None


class UserJobPreferencesResponse(UserJobPreferencesBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserPreferencePackagesBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    package_id: str
    user_id: str
    package_name: str
    package_description: Optional[str] = None
    salary_minimum: Optional[int] = None
    salary_maximum: Optional[int] = None
    location_priority: Optional[str] = None
    work_arrangement: Optional[str] = None
    commute_time_maximum: Optional[int] = None
    travel_percentage_maximum: Optional[int] = None
    is_active: Optional[bool] = None


class UserPreferencePackagesCreate(UserPreferencePackagesBase):
    pass


class UserPreferencePackagesUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    package_id: Optional[str] = None
    user_id: Optional[str] = None
    package_name: Optional[str] = None
    package_description: Optional[str] = None
    salary_minimum: Optional[int] = None
    salary_maximum: Optional[int] = None
    location_priority: Optional[str] = None
    work_arrangement: Optional[str] = None
    commute_time_maximum: Optional[int] = None
    travel_percentage_maximum: Optional[int] = None
    is_active: Optional[bool] = None
    updated_at: Optional[datetime] = None


class UserPreferencePackagesResponse(UserPreferencePackagesBase):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserPreferredIndustriesBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    preference_id: str
    user_id: Optional[str] = None
    industry_name: str
    preference_type: str
    priority_level: Optional[int] = None


class UserPreferredIndustriesCreate(UserPreferredIndustriesBase):
    pass


class UserPreferredIndustriesUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    preference_id: Optional[str] = None
    user_id: Optional[str] = None
    industry_name: Optional[str] = None
    preference_type: Optional[str] = None
    priority_level: Optional[int] = None


class UserPreferredIndustriesResponse(UserPreferredIndustriesBase):
    created_at: Optional[datetime] = None


class WorkExperiencesBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    company_name: str
    job_title: str
    start_date: date
    end_date: Optional[date] = None
    is_current: Optional[bool] = None
    location: Optional[str] = None
    description: Optional[str] = None
    display_order: Optional[int] = None


class WorkExperiencesCreate(WorkExperiencesBase):
    pass


class WorkExperiencesUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: Optional[str] = None
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: Optional[bool] = None
    location: Optional[str] = None
    description: Optional[str] = None
    display_order: Optional[int] = None
    updated_at: Optional[datetime] = None


class WorkExperiencesResponse(WorkExperiencesBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class WorkflowCheckpointsBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    checkpoint_id: str
    workflow_id: str
    stage: str
    checkpoint_data: Dict[str, Any]


class WorkflowCheckpointsCreate(WorkflowCheckpointsBase):
    pass


class WorkflowCheckpointsUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    checkpoint_id: Optional[str] = None
    workflow_id: Optional[str] = None
    stage: Optional[str] = None
    checkpoint_data: Optional[Dict[str, Any]] = None


class WorkflowCheckpointsResponse(WorkflowCheckpointsBase):
    id: str
    created_at: Optional[datetime] = None


