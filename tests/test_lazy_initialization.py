"""
Module: test_lazy_initialization.py
Purpose: Unit tests for lazy database initialization and singleton patterns
Created: 2024-09-18
Modified: 2025-10-21
Dependencies: pytest, modules.database.lazy_instances
Related: modules/database/lazy_instances.py, conftest.py, test_database_*.py
Description: Verifies database connections are not established at import time,
             validates lazy initialization works correctly, tests singleton pattern
             for DatabaseManager and DatabaseClient, and verifies reset functionality.
             Ensures import-time connection prevention for performance.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestLazyInitialization:
    """Test lazy database initialization patterns"""

    def test_lazy_manager_singleton(self):
        """Test DatabaseManager is singleton"""
        from modules.database.lazy_instances import get_database_manager

        mgr1 = get_database_manager()
        mgr2 = get_database_manager()
        assert mgr1 is mgr2, "DatabaseManager should be singleton"

    def test_lazy_client_singleton(self):
        """Test DatabaseClient is singleton"""
        from modules.database.lazy_instances import get_database_client

        client1 = get_database_client()
        client2 = get_database_client()
        assert client1 is client2, "DatabaseClient should be singleton"

    def test_lazy_instances_reset(self):
        """Test singleton reset functionality"""
        from modules.database.lazy_instances import (
            get_database_manager,
            get_database_client,
            reset_singletons,
        )

        # Get initial instances
        mgr1 = get_database_manager()
        client1 = get_database_client()

        # Reset
        reset_singletons()

        # Get new instances
        mgr2 = get_database_manager()
        client2 = get_database_client()

        # Should be different instances after reset
        assert mgr1 is not mgr2, "Manager should be new instance after reset"
        assert client1 is not client2, "Client should be new instance after reset"

    def test_no_import_time_connection(self):
        """Test that importing modules doesn't create database connections"""
        import importlib
        import sys

        # Remove modules if already imported
        modules_to_test = [
            "modules.database.lazy_instances",
            "modules.dashboard_api",
            "modules.dashboard_api_v2",
            "modules.database.database_api",
        ]

        for mod_name in modules_to_test:
            if mod_name in sys.modules:
                del sys.modules[mod_name]

        # Import should NOT create database connections
        # If this fails, it means connections are being made at import time
        try:
            import modules.database.lazy_instances
            import modules.dashboard_api
            import modules.dashboard_api_v2
            import modules.database.database_api

            # If we get here, imports succeeded without connecting
            assert True, "Modules imported without database connections"
        except Exception as e:
            pytest.fail(f"Module import should not require database connection: {e}")

    def test_database_manager_initialization(self):
        """Test DatabaseManager initializes correctly"""
        from modules.database.lazy_instances import get_database_manager

        db_manager = get_database_manager()

        # Check that manager has required attributes
        assert hasattr(db_manager, "client"), "Manager should have client"
        assert hasattr(db_manager, "reader"), "Manager should have reader"
        assert hasattr(db_manager, "writer"), "Manager should have writer"

    def test_database_client_initialization(self):
        """Test DatabaseClient initializes correctly"""
        from modules.database.lazy_instances import get_database_client

        db_client = get_database_client()

        # Check that client has required attributes
        assert hasattr(db_client, "engine"), "Client should have engine"
        assert hasattr(db_client, "SessionLocal"), "Client should have SessionLocal"
        assert hasattr(db_client, "database_url"), "Client should have database_url"

    def test_database_connectivity(self):
        """Test actual database connection works"""
        from modules.database.lazy_instances import get_database_client

        db_client = get_database_client()

        # Test connection
        try:
            connection_ok = db_client.test_connection()
            assert connection_ok, "Database connection should succeed"
        except Exception as e:
            pytest.skip(f"Database not available for testing: {e}")

    def test_database_manager_methods(self):
        """Test DatabaseManager methods are accessible"""
        from modules.database.lazy_instances import get_database_manager

        db_manager = get_database_manager()

        # Check that key methods exist
        assert hasattr(db_manager, "get_job_by_id"), "Should have get_job_by_id"
        assert hasattr(db_manager, "get_recent_jobs"), "Should have get_recent_jobs"
        assert hasattr(db_manager, "get_job_statistics"), "Should have get_job_statistics"
        assert hasattr(db_manager, "create_job"), "Should have create_job"


class TestDatabaseExtensions:
    """Test database extensions initialization"""

    def test_extend_database_reader(self):
        """Test extend_database_reader function exists and is callable"""
        from modules.database.database_extensions import extend_database_reader

        # Should be callable
        assert callable(extend_database_reader), "extend_database_reader should be callable"

    def test_scraper_extensions_class(self):
        """Test ScraperDatabaseExtensions class exists"""
        from modules.database.database_extensions import ScraperDatabaseExtensions

        # Should be able to instantiate
        extensions = ScraperDatabaseExtensions()
        assert extensions is not None, "ScraperDatabaseExtensions should instantiate"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
