# Phase 3: Resilience & Storage Testing Guide
**Timeline:** Week 4 (5-6 working days)
**Goal:** Test failure recovery systems and storage backends

---

## Overview

Phase 3 focuses on testing the resilience systems that keep the application running smoothly when things go wrong, and the storage backends that persist generated documents.

**Modules to Test:**
- `modules/resilience/failure_recovery.py` (260 lines, 0% coverage)
- `modules/resilience/retry_strategy_manager.py` (210 lines, 0% coverage)
- `modules/resilience/data_consistency_validator.py` (244 lines, 0% coverage)
- `modules/storage/local_storage.py` (104 lines, 22% coverage)
- `modules/storage/google_drive_storage.py` (207 lines, 14% coverage)
- `modules/storage/storage_factory.py` (71 lines, 38% coverage)

**Coverage Targets:**
- Resilience modules: 80% coverage
- Storage modules: 70% coverage

---

## Part A: Resilience System Testing (3 days)

### 1. Failure Recovery Manager Tests

**File:** `tests/unit/test_failure_recovery_manager.py`

**What to Test:**

#### Basic Recovery Operations
```python
def test_recovery_manager_initialization():
    """Test that recovery manager initializes correctly"""
    manager = FailureRecoveryManager()
    assert manager is not None
    assert manager.max_retries > 0

def test_classify_failure_type():
    """Test that different failures are classified correctly"""
    manager = FailureRecoveryManager()

    # Test network failure
    network_error = ConnectionError("Connection refused")
    failure_type = manager.classify_failure(network_error)
    assert failure_type == FailureType.CONNECTION_RESET

    # Test database failure
    db_error = Exception("Deadlock detected")
    failure_type = manager.classify_failure(db_error)
    assert failure_type == FailureType.DEADLOCK
```

#### Retry Logic
```python
def test_automatic_retry_on_transient_failure():
    """Test that transient failures trigger automatic retry"""
    manager = FailureRecoveryManager()
    attempts = []

    def failing_operation():
        attempts.append(1)
        if len(attempts) < 3:
            raise ConnectionError("Temporary failure")
        return "success"

    result = manager.execute_with_recovery(failing_operation)

    assert result == "success"
    assert len(attempts) == 3  # Failed twice, succeeded third time

def test_exponential_backoff():
    """Test that retry delays increase exponentially"""
    manager = FailureRecoveryManager()
    delays = manager.calculate_retry_delays(max_retries=3)

    assert delays[0] < delays[1] < delays[2]
    assert delays[1] / delays[0] >= 2  # At least 2x increase
```

#### Workflow Checkpoints
```python
def test_create_checkpoint():
    """Test creating workflow checkpoint"""
    manager = FailureRecoveryManager()

    checkpoint = manager.create_checkpoint(
        workflow_id="workflow_123",
        stage="document_generation",
        data={"job_id": 456, "template": "resume"}
    )

    assert checkpoint.workflow_id == "workflow_123"
    assert checkpoint.stage == "document_generation"
    assert "job_id" in checkpoint.data

def test_resume_from_checkpoint():
    """Test resuming workflow from checkpoint"""
    manager = FailureRecoveryManager()

    # Create checkpoint
    checkpoint = manager.create_checkpoint(
        workflow_id="workflow_123",
        stage="email_sending",
        data={"email_id": 789}
    )

    # Resume from checkpoint
    resumed_data = manager.resume_from_checkpoint(checkpoint.checkpoint_id)

    assert resumed_data["email_id"] == 789
    assert resumed_data["stage"] == "email_sending"
```

#### Error Categories
```python
def test_permanent_vs_transient_errors():
    """Test distinguishing permanent vs transient errors"""
    manager = FailureRecoveryManager()

    # Transient error (should retry)
    transient = ConnectionError("Connection timeout")
    assert manager.is_retryable(transient) is True

    # Permanent error (should not retry)
    permanent = ValueError("Invalid input data")
    assert manager.is_retryable(permanent) is False
```

**Key Assertions:**
- Retry attempts match configured strategy
- Backoff delays increase appropriately
- Checkpoints store/restore data correctly
- Error classification is accurate
- Recovery succeeds after retries

---

### 2. Retry Strategy Manager Tests

**File:** `tests/unit/test_retry_strategy_manager.py`

**What to Test:**

#### Strategy Configuration
```python
def test_default_retry_strategies():
    """Test default retry strategies for different operations"""
    manager = RetryStrategyManager()

    # Network operations get 3 retries with exponential backoff
    network_strategy = manager.get_strategy("network_operation")
    assert network_strategy.max_attempts == 3
    assert network_strategy.exponential_backoff is True

    # Database deadlocks get 5 retries with immediate retry
    deadlock_strategy = manager.get_strategy("database_deadlock")
    assert deadlock_strategy.max_attempts == 5
    assert deadlock_strategy.base_delay < 1.0  # Fast retry

def test_custom_retry_strategy():
    """Test creating custom retry strategy"""
    manager = RetryStrategyManager()

    custom_strategy = RetryStrategy(
        max_attempts=5,
        base_delay=2.0,
        exponential_backoff=True,
        max_delay=60.0
    )

    manager.register_strategy("custom_operation", custom_strategy)

    retrieved = manager.get_strategy("custom_operation")
    assert retrieved.max_attempts == 5
    assert retrieved.base_delay == 2.0
```

#### Delay Calculation
```python
def test_exponential_backoff_calculation():
    """Test exponential backoff delay calculation"""
    strategy = RetryStrategy(
        max_attempts=4,
        base_delay=1.0,
        exponential_backoff=True,
        max_delay=30.0
    )

    # Delays should be: 1s, 2s, 4s, 8s
    assert strategy.get_delay(1) == 1.0
    assert strategy.get_delay(2) == 2.0
    assert strategy.get_delay(3) == 4.0
    assert strategy.get_delay(4) == 8.0

def test_max_delay_cap():
    """Test that delay is capped at max_delay"""
    strategy = RetryStrategy(
        base_delay=10.0,
        exponential_backoff=True,
        max_delay=60.0
    )

    # Without cap, delay 5 would be 160s (10 * 2^4)
    # With cap, should be 60s
    delay = strategy.get_delay(5)
    assert delay == 60.0
```

#### Strategy Selection
```python
def test_strategy_for_error_type():
    """Test selecting strategy based on error type"""
    manager = RetryStrategyManager()

    # Rate limit error gets long delay
    rate_limit_error = Exception("429 Too Many Requests")
    strategy = manager.get_strategy_for_error(rate_limit_error)
    assert strategy.base_delay >= 60.0

    # Timeout error gets shorter delay
    timeout_error = TimeoutError("Operation timed out")
    strategy = manager.get_strategy_for_error(timeout_error)
    assert strategy.base_delay < 10.0
```

**Key Assertions:**
- Strategies configured correctly for different error types
- Delay calculations follow exponential pattern
- Max delay caps are enforced
- Custom strategies can be registered

---

### 3. Data Consistency Validator Tests

**File:** `tests/unit/test_data_consistency_validator.py`

**What to Test:**

#### Validation Rules
```python
def test_validate_job_record():
    """Test validation of job record consistency"""
    validator = DataConsistencyValidator()

    valid_job = {
        "id": 123,
        "title": "Python Developer",
        "company": "Tech Corp",
        "status": "open"
    }

    result = validator.validate_record("jobs", valid_job)
    assert result.is_valid is True
    assert len(result.errors) == 0

def test_detect_missing_required_fields():
    """Test detection of missing required fields"""
    validator = DataConsistencyValidator()

    invalid_job = {
        "id": 123,
        "title": "Python Developer"
        # Missing company and status
    }

    result = validator.validate_record("jobs", invalid_job)
    assert result.is_valid is False
    assert "company" in str(result.errors)
    assert "status" in str(result.errors)
```

#### Relationship Validation
```python
def test_validate_foreign_key_references():
    """Test validation of foreign key relationships"""
    validator = DataConsistencyValidator(db_session=mock_db)

    # Application references non-existent job
    application = {
        "id": 456,
        "job_id": 999999,  # Does not exist
        "status": "pending"
    }

    result = validator.validate_relationships("applications", application)
    assert result.is_valid is False
    assert "job_id" in str(result.errors)
    assert "not found" in str(result.errors).lower()
```

#### Data Correction
```python
def test_auto_correct_data_format():
    """Test automatic correction of data format issues"""
    validator = DataConsistencyValidator()

    job_with_issues = {
        "id": 123,
        "title": "  Python Developer  ",  # Extra whitespace
        "salary_min": "100000",  # String instead of int
        "created_at": "2025-01-15"  # String instead of datetime
    }

    corrected = validator.correct_data("jobs", job_with_issues)

    assert corrected["title"] == "Python Developer"  # Trimmed
    assert isinstance(corrected["salary_min"], int)
    assert isinstance(corrected["created_at"], datetime)
```

#### Batch Validation
```python
def test_validate_batch_of_records():
    """Test validating multiple records efficiently"""
    validator = DataConsistencyValidator()

    records = [
        {"id": 1, "title": "Job 1", "company": "Corp A"},
        {"id": 2, "title": "Job 2"},  # Missing company
        {"id": 3, "title": "Job 3", "company": "Corp C"}
    ]

    results = validator.validate_batch("jobs", records)

    assert results[0].is_valid is True
    assert results[1].is_valid is False
    assert results[2].is_valid is True
```

**Key Assertions:**
- Required fields are validated
- Data types are correct
- Foreign key relationships are valid
- Automatic corrections work
- Batch validation is efficient

---

## Part B: Storage Backend Testing (2-3 days)

### 4. Local Storage Tests

**File:** `tests/unit/test_local_storage.py`

**What to Test:**

#### File Operations
```python
def test_store_document(tmp_path):
    """Test storing document to local filesystem"""
    storage = LocalStorage(base_path=tmp_path)

    content = b"Resume content here"
    metadata = {"job_id": 123, "type": "resume"}

    file_id = storage.store(
        content=content,
        filename="resume.docx",
        metadata=metadata
    )

    assert file_id is not None
    assert (tmp_path / file_id / "resume.docx").exists()

def test_retrieve_document(tmp_path):
    """Test retrieving stored document"""
    storage = LocalStorage(base_path=tmp_path)

    # Store document
    content = b"Cover letter content"
    file_id = storage.store(content, "cover_letter.docx")

    # Retrieve document
    retrieved = storage.retrieve(file_id)

    assert retrieved == content

def test_delete_document(tmp_path):
    """Test deleting stored document"""
    storage = LocalStorage(base_path=tmp_path)

    # Store and delete
    file_id = storage.store(b"content", "file.docx")
    storage.delete(file_id)

    # Verify deleted
    assert not (tmp_path / file_id).exists()
```

#### Path Management
```python
def test_organize_by_date(tmp_path):
    """Test organizing files by date"""
    storage = LocalStorage(base_path=tmp_path, organize_by_date=True)

    file_id = storage.store(b"content", "document.docx")

    # File should be in YYYY/MM/DD structure
    today = datetime.now()
    expected_path = tmp_path / str(today.year) / f"{today.month:02d}" / f"{today.day:02d}"
    assert expected_path.exists()

def test_handle_duplicate_filenames(tmp_path):
    """Test handling duplicate filenames"""
    storage = LocalStorage(base_path=tmp_path)

    # Store same filename twice
    id1 = storage.store(b"content1", "resume.docx")
    id2 = storage.store(b"content2", "resume.docx")

    # Should have different IDs
    assert id1 != id2

    # Both should exist
    assert storage.exists(id1)
    assert storage.exists(id2)
```

#### Error Handling
```python
def test_handle_disk_full_error(tmp_path):
    """Test handling disk full error"""
    storage = LocalStorage(base_path=tmp_path)

    # Mock disk full error
    with patch('builtins.open', side_effect=OSError("No space left on device")):
        with pytest.raises(StorageError) as exc_info:
            storage.store(b"content", "file.docx")

        assert "disk" in str(exc_info.value).lower()
        assert "full" in str(exc_info.value).lower()

def test_handle_permission_denied(tmp_path):
    """Test handling permission denied error"""
    storage = LocalStorage(base_path=tmp_path)

    # Create read-only directory
    readonly_dir = tmp_path / "readonly"
    readonly_dir.mkdir()
    readonly_dir.chmod(0o444)

    with pytest.raises(StorageError) as exc_info:
        storage.store(b"content", "file.docx", path=readonly_dir)

    assert "permission" in str(exc_info.value).lower()
```

**Key Assertions:**
- Files are stored and retrieved correctly
- Directory structure is created automatically
- Duplicate filenames are handled
- Metadata is preserved
- Errors are handled gracefully

---

### 5. Google Drive Storage Tests

**File:** `tests/unit/test_google_drive_storage.py`

**What to Test:**

#### Authentication
```python
def test_authenticate_with_service_account(mock_credentials):
    """Test authentication with service account"""
    storage = GoogleDriveStorage(credentials=mock_credentials)

    assert storage.is_authenticated() is True
    assert storage.service is not None

def test_handle_invalid_credentials():
    """Test handling invalid credentials"""
    with pytest.raises(StorageError) as exc_info:
        GoogleDriveStorage(credentials="invalid")

    assert "authentication" in str(exc_info.value).lower()
```

#### Upload Operations
```python
def test_upload_document_to_drive(mock_drive_service):
    """Test uploading document to Google Drive"""
    storage = GoogleDriveStorage(service=mock_drive_service)

    content = b"Document content"
    file_id = storage.store(
        content=content,
        filename="document.docx",
        folder_id="folder_123"
    )

    # Verify upload was called
    assert mock_drive_service.files().create.called
    assert file_id is not None

def test_upload_with_metadata(mock_drive_service):
    """Test uploading with custom metadata"""
    storage = GoogleDriveStorage(service=mock_drive_service)

    metadata = {
        "job_id": 456,
        "application_type": "resume",
        "created_by": "system"
    }

    file_id = storage.store(
        content=b"content",
        filename="resume.docx",
        metadata=metadata
    )

    # Verify metadata was included
    call_args = mock_drive_service.files().create.call_args
    assert "properties" in call_args[1]["body"]
```

#### Download Operations
```python
def test_download_document_from_drive(mock_drive_service):
    """Test downloading document from Google Drive"""
    storage = GoogleDriveStorage(service=mock_drive_service)

    # Mock download response
    mock_drive_service.files().get_media().execute.return_value = b"content"

    content = storage.retrieve("file_123")

    assert content == b"content"
    assert mock_drive_service.files().get_media.called
```

#### Folder Management
```python
def test_create_folder_structure(mock_drive_service):
    """Test creating folder structure in Drive"""
    storage = GoogleDriveStorage(service=mock_drive_service)

    folder_id = storage.create_folder(
        name="Job Applications",
        parent_folder_id="root"
    )

    assert folder_id is not None
    assert mock_drive_service.files().create.called

def test_organize_by_job(mock_drive_service):
    """Test organizing documents by job"""
    storage = GoogleDriveStorage(service=mock_drive_service)

    # Upload document for specific job
    file_id = storage.store(
        content=b"resume",
        filename="resume.docx",
        metadata={"job_id": 789}
    )

    # Verify file was placed in job-specific folder
    # (Implementation details depend on your folder structure)
```

#### Error Handling
```python
def test_handle_quota_exceeded_error(mock_drive_service):
    """Test handling Google Drive quota exceeded"""
    storage = GoogleDriveStorage(service=mock_drive_service)

    # Mock quota exceeded error
    from googleapiclient.errors import HttpError
    mock_drive_service.files().create.side_effect = HttpError(
        resp=Mock(status=403),
        content=b'{"error": {"message": "User rate limit exceeded"}}'
    )

    with pytest.raises(StorageError) as exc_info:
        storage.store(b"content", "file.docx")

    assert "quota" in str(exc_info.value).lower()

def test_retry_on_network_error(mock_drive_service):
    """Test retry logic on network errors"""
    storage = GoogleDriveStorage(service=mock_drive_service)

    # Fail twice, succeed on third attempt
    mock_drive_service.files().create.side_effect = [
        ConnectionError("Network error"),
        ConnectionError("Network error"),
        {"id": "file_123"}
    ]

    file_id = storage.store(b"content", "file.docx")

    assert file_id == "file_123"
    assert mock_drive_service.files().create.call_count == 3
```

**Key Assertions:**
- Authentication works correctly
- Files upload/download successfully
- Metadata is preserved
- Folder structure is created
- Quota limits are handled
- Network errors trigger retries

---

### 6. Storage Factory Tests

**File:** `tests/unit/test_storage_factory.py`

**What to Test:**

#### Backend Selection
```python
def test_create_local_storage():
    """Test creating local storage backend"""
    factory = StorageFactory()

    storage = factory.create("local", base_path="/tmp/storage")

    assert isinstance(storage, LocalStorage)
    assert storage.base_path == Path("/tmp/storage")

def test_create_google_drive_storage():
    """Test creating Google Drive storage backend"""
    factory = StorageFactory()

    storage = factory.create(
        "google_drive",
        credentials_file="credentials.json"
    )

    assert isinstance(storage, GoogleDriveStorage)

def test_get_storage_from_env():
    """Test getting storage backend from environment variable"""
    with patch.dict(os.environ, {"STORAGE_BACKEND": "local"}):
        factory = StorageFactory()
        storage = factory.get_default_storage()

        assert isinstance(storage, LocalStorage)
```

#### Configuration
```python
def test_register_custom_backend():
    """Test registering custom storage backend"""
    factory = StorageFactory()

    class CustomStorage:
        pass

    factory.register("custom", CustomStorage)
    storage = factory.create("custom")

    assert isinstance(storage, CustomStorage)

def test_invalid_backend_raises_error():
    """Test that invalid backend raises error"""
    factory = StorageFactory()

    with pytest.raises(ValueError) as exc_info:
        factory.create("invalid_backend")

    assert "invalid_backend" in str(exc_info.value)
```

**Key Assertions:**
- Correct backend is instantiated
- Configuration is passed correctly
- Custom backends can be registered
- Invalid backends raise errors

---

## Integration Tests

**File:** `tests/integration/test_resilience_with_storage.py`

### End-to-End Recovery Scenarios

```python
def test_document_storage_with_retry():
    """Test storing document with automatic retry on failure"""
    recovery_manager = FailureRecoveryManager()
    storage = LocalStorage(base_path="/tmp/test_storage")

    # Simulate intermittent storage failure
    attempts = []
    def store_with_failure():
        attempts.append(1)
        if len(attempts) < 3:
            raise IOError("Temporary storage issue")
        return storage.store(b"content", "document.docx")

    file_id = recovery_manager.execute_with_recovery(store_with_failure)

    assert file_id is not None
    assert len(attempts) == 3
    assert storage.exists(file_id)

def test_workflow_checkpoint_with_storage_failure():
    """Test workflow checkpoint recovery from storage failure"""
    recovery_manager = FailureRecoveryManager()

    # Create checkpoint before risky operation
    checkpoint = recovery_manager.create_checkpoint(
        workflow_id="app_123",
        stage="document_generation",
        data={"job_id": 456, "attempt": 1}
    )

    # Simulate failure during storage
    try:
        raise IOError("Storage temporarily unavailable")
    except Exception:
        # Resume from checkpoint
        recovered_data = recovery_manager.resume_from_checkpoint(checkpoint.checkpoint_id)

        assert recovered_data["job_id"] == 456
        # Can retry the operation with recovered data
```

---

## Quick Implementation Checklist

### Day 1: Failure Recovery
- [ ] Create `test_failure_recovery_manager.py`
- [ ] Test basic recovery operations (3-4 tests)
- [ ] Test retry logic (3-4 tests)
- [ ] Test checkpoint creation/restoration (2-3 tests)
- [ ] Run tests, aim for 75%+ coverage

### Day 2: Retry Strategies
- [ ] Create `test_retry_strategy_manager.py`
- [ ] Test strategy configuration (2-3 tests)
- [ ] Test delay calculations (3-4 tests)
- [ ] Test strategy selection (2-3 tests)
- [ ] Run tests, aim for 80%+ coverage

### Day 3: Data Consistency
- [ ] Create `test_data_consistency_validator.py`
- [ ] Test validation rules (4-5 tests)
- [ ] Test relationship validation (2-3 tests)
- [ ] Test data correction (2-3 tests)
- [ ] Run tests, aim for 75%+ coverage

### Day 4: Local Storage
- [ ] Create `test_local_storage.py`
- [ ] Test basic file operations (4-5 tests)
- [ ] Test path management (2-3 tests)
- [ ] Test error handling (2-3 tests)
- [ ] Run tests, aim for 70%+ coverage

### Day 5: Google Drive Storage
- [ ] Create `test_google_drive_storage.py`
- [ ] Test authentication (2 tests)
- [ ] Test upload/download (3-4 tests)
- [ ] Test folder management (2-3 tests)
- [ ] Test error handling (2-3 tests)
- [ ] Run tests, aim for 65%+ coverage

### Day 6: Storage Factory & Integration
- [ ] Create `test_storage_factory.py`
- [ ] Test backend selection (3-4 tests)
- [ ] Create `test_resilience_with_storage.py`
- [ ] Test integration scenarios (2-3 tests)
- [ ] Run full test suite
- [ ] Fix any failures
- [ ] Verify coverage targets met

---

## Success Criteria

**Unit Tests:**
- [ ] All 6 test files created
- [ ] Minimum 50 tests written
- [ ] Resilience modules: ≥80% coverage
- [ ] Storage modules: ≥70% coverage
- [ ] All tests passing

**Integration Tests:**
- [ ] At least 2 integration scenarios tested
- [ ] Recovery + storage interaction verified
- [ ] Checkpoint + resume flow working

**Documentation:**
- [ ] All test files have clear docstrings
- [ ] Complex test scenarios documented
- [ ] Known limitations noted

---

## Common Pitfalls to Avoid

1. **Don't test external services directly** - Mock Google Drive API
2. **Don't use real credentials** - Use test credentials only
3. **Clean up temp files** - Use pytest fixtures with cleanup
4. **Don't test implementation details** - Focus on behavior
5. **Handle async operations** - Use proper async test utilities
6. **Mock time.sleep()** - Don't make tests slow
7. **Test edge cases** - Empty files, special characters in names

---

## Tips for Success

1. **Start with happy path** - Get basic functionality working first
2. **Then add edge cases** - Test error conditions thoroughly
3. **Use pytest fixtures** - Share setup code between tests
4. **Mock external dependencies** - Don't rely on network/filesystem
5. **Keep tests fast** - Under 1 second each
6. **Test one thing** - Each test should verify one behavior
7. **Use descriptive names** - Test names should explain what they test

---

**Estimated Time:** 5-6 days
**Difficulty:** Medium
**Dependencies:** Phase 1 & 2 complete
**Next:** Phase 4 (Dashboard & Analytics Testing)
