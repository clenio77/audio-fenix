"""
Tests - processing watchdog (stale PROCESSING recovery)
"""
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from application.processing_watchdog import (
    STALE_PROCESSING_AFTER,
    STALE_PROCESSING_MESSAGE,
    is_stale_processing,
)
from domain.models.project import Project, ProjectStatus


class TestIsStaleProcessing:
    def test_fresh_processing_is_not_stale(self):
        now = datetime(2026, 9, 19, 12, 0, 0)
        updated = now - timedelta(minutes=5)
        assert is_stale_processing(updated, now=now) is False

    def test_processing_past_limit_is_stale(self):
        now = datetime(2026, 9, 19, 12, 0, 0)
        updated = now - STALE_PROCESSING_AFTER - timedelta(seconds=1)
        assert is_stale_processing(updated, now=now) is True

    def test_none_updated_at_is_not_stale(self):
        assert is_stale_processing(None) is False

    def test_exactly_at_limit_is_not_stale(self):
        now = datetime(2026, 9, 19, 12, 0, 0)
        updated = now - STALE_PROCESSING_AFTER
        assert is_stale_processing(updated, now=now) is False


class TestStatusStaleProcessingRecovery:
    def test_stale_processing_marked_failed(
        self, client: TestClient, db_session
    ):
        project_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
        stale_time = datetime.utcnow() - STALE_PROCESSING_AFTER - timedelta(minutes=1)
        project = Project(
            id=project_id,
            original_filename="stuck.wav",
            original_file_path="/tmp/stuck.wav",
            file_size_mb=1,
            status=ProjectStatus.PROCESSING,
            created_at=stale_time,
            updated_at=stale_time,
        )
        db_session.add(project)
        db_session.commit()

        # Bypass SQLAlchemy onupdate so updated_at stays stale after insert.
        db_session.execute(
            Project.__table__.update()
            .where(Project.id == project_id)
            .values(updated_at=stale_time)
        )
        db_session.commit()

        response = client.get(f"/api/status/{project_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failed"
        assert data["error"] == STALE_PROCESSING_MESSAGE

        db_session.refresh(project)
        assert project.status == ProjectStatus.FAILED
        assert project.error_message == STALE_PROCESSING_MESSAGE

    def test_fresh_processing_unchanged(
        self, client: TestClient, db_session
    ):
        project_id = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
        project = Project(
            id=project_id,
            original_filename="active.wav",
            original_file_path="/tmp/active.wav",
            file_size_mb=1,
            status=ProjectStatus.PROCESSING,
        )
        db_session.add(project)
        db_session.commit()

        response = client.get(f"/api/status/{project_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processing"
        assert data["progress"] == 50

        db_session.refresh(project)
        assert project.status == ProjectStatus.PROCESSING
