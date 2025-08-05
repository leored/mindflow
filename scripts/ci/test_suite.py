#!/usr/bin/env python3
"""
Test Suite for Documentation Change Detection & Knowledge DB Sync System

This test suite provides comprehensive testing for all components of the
documentation synchronization system.

Run with: python -m pytest test_docsync.py -v
"""

import os
import tempfile
import shutil
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest
import json
import hashlib

# Import the main modules (assuming they're in the same directory)
from docsync import (
    Config, GitAnalyzer, LightRAGClient, DocumentProcessor, 
    DocSyncSystem, FileChange, ChangeType
)


class TestConfig:
    """Test configuration management"""
    
    def test_default_config(self):
        """Test default configuration creation"""
        config = Config.default()
        
        assert config.watch_directories == ["docs/", "documentation/"]
        assert ".md" in config.file_extensions
        assert config.api_base_url == "http://localhost:8020"
        assert config.batch_size == 10
        assert not config.dry_run
    
    def test_config_from_file(self):
        """Test loading configuration from YAML file"""
        config_data = {
            "watch_directories": ["test/"],
            "file_extensions": [".txt"],
            "exclude_patterns": ["**/temp/**"],
            "api_base_url": "http://test:8080",
            "api_timeout": 60,
            "batch_size": 5,
            "dry_run": True,
            "log_level": "DEBUG",
            "log_file": "test.log"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            import yaml
            yaml.safe_dump(config_data, f)
            config_path = f.name
        
        try:
            config = Config.from_file(config_path)
            assert config.watch_directories == ["test/"]
            assert config.file_extensions == [".txt"]
            assert config.api_base_url == "http://test:8080"
            assert config.api_timeout == 60
            assert config.dry_run is True
        finally:
            os.unlink(config_path)


class TestGitAnalyzer:
    """Test Git repository analysis functionality"""
    
    @pytest.fixture
    def temp_repo(self):
        """Create a temporary Git repository for testing"""
        temp_dir = tempfile.mkdtemp()
        repo_path = Path(temp_dir)
        
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_path, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_path, check=True)
        
        # Create initial structure
        docs_dir = repo_path / "docs"
        docs_dir.mkdir()
        
        # Create initial file
        (docs_dir / "readme.md").write_text("# Initial content")
        
        # Initial commit
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path, check=True)
        
        yield repo_path
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_should_process_file(self, temp_repo):
        """Test file filtering logic"""
        config = Config.default()
        analyzer = GitAnalyzer(config, str(temp_repo))
        
        # Should process MD files in docs/
        assert analyzer._should_process_file("docs/test.md")
        assert analyzer._should_process_file("documentation/guide.markdown")
        
        # Should not process other extensions
        assert not analyzer._should_process_file("docs/test.txt")
        assert not analyzer._should_process_file("docs/image.png")
        
        # Should not process excluded patterns
        assert not analyzer._should_process_file("docs/node_modules/test.md")
        assert not analyzer._should_process_file(".git/test.md")
        
        # Should not process files outside watched directories
        assert not analyzer._should_process_file("src/test.md")
    
    def test_get_changes_since_commit(self, temp_repo):
        """Test detecting changes since a specific commit"""
        config = Config.default()
        analyzer = GitAnalyzer(config, str(temp_repo))
        
        # Get initial commit hash
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"], 
            cwd=temp_repo, 
            capture_output=True, 
            text=True, 
            check=True
        )
        initial_commit = result.stdout.strip()
        
        # Make changes
        docs_dir = temp_repo / "docs"
        (docs_dir / "new.md").write_text("# New document")
        (docs_dir / "readme.md").write_text("# Updated content")
        (docs_repo / "not_docs.md").write_text("# Should be ignored")
        
        subprocess.run(["git", "add", "."], cwd=temp_repo, check=True)
        subprocess.run(["git", "commit", "-m", "Add changes"], cwd=temp_repo, check=True)
        
        # Test change detection
        changes = analyzer.get_changes_since_commit(initial_commit)
        
        # Should detect changes in docs/ but not root
        doc_changes = [c for c in changes if c.path.startswith("docs/")]
        assert len(doc_changes) == 2
        
        # Check change types
        change_paths = {c.path: c.change_type for c in doc_changes}
        assert change_paths["docs/new.md"] == ChangeType.ADDED
        assert change_paths["docs/readme.md"] == ChangeType.MODIFIED
    
    def test_get_staged_changes(self, temp_repo):
        """Test detecting staged changes"""
        config = Config.default()
        analyzer = GitAnalyzer(config, str(temp_repo))
        
        # Make changes and stage them
        docs_dir = temp_repo / "docs"
        (docs_dir / "staged.md").write_text("# Staged document")
        
        subprocess.run(["git", "add", "docs/staged.md"], cwd=temp_repo, check=True)
        
        # Test staged change detection
        changes = analyzer.get_staged_changes()
        
        assert len(changes) == 1
        assert changes[0].path == "docs/staged.md"
        assert changes[0].change_type == ChangeType.ADDED
        assert changes[0].content == "# Staged document"


class TestLightRAGClient:
    """Test LightRAG API client functionality"""
    
    @pytest.fixture
    def mock_client(self):
        """Create a LightRAG client with mocked requests"""
        config = Config.default()
        return LightRAGClient(config)
    
    @patch('requests.get')
    def test_health_check_success(self, mock_get, mock_client):
        """Test successful health check"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        assert mock_client.health_check() is True
        mock_get.assert_called_once_with(
            "http://localhost:8020/health",
            timeout=30
        )
    
    @patch('requests.get')
    def test_health_check_failure(self, mock_get, mock_client):
        """Test failed health check"""
        mock_get.side_effect = Exception("Connection error")
        
        assert mock_client.health_check() is False
    
    @patch('requests.post')
    def test_insert_document_success(self, mock_post, mock_client):
        """Test successful document insertion"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = mock_client.insert_document(
            "Test content", 
            {"file_path": "test.md"}
        )
        
        assert result is True
        mock_post.assert_called_once_with(
            "http://localhost:8020/insert",
            json={"input": "Test content", "metadata": {"file_path": "test.md"}},
            timeout=30
        )
    
    @patch('requests.post')
    def test_insert_document_failure(self, mock_post, mock_client):
        """Test failed document insertion"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
        mock_post.return_value = mock_response
        
        result = mock_client.insert_document("Test content")
        
        assert result is False
    
    @patch('requests.put')
    def test_update_document(self, mock_put, mock_client):
        """Test document update"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_put.return_value = mock_response
        
        result = mock_client.update_document("doc123", "Updated content")
        
        assert result is True
        mock_put.assert_called_once_with(
            "http://localhost:8020/update/doc123",
            json={"input": "Updated content"},
            timeout=30
        )
    
    @patch('requests.delete')
    def test_delete_document(self, mock_delete, mock_client):
        """Test document deletion"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_delete.return_value = mock_response
        
        result = mock_client.delete_document("doc123")
        
        assert result is True
        mock_delete.assert_called_once_with(
            "http://localhost:8020/delete/doc123",
            timeout=30
        )
    
    @patch('requests.post')
    def test_search_documents(self, mock_post, mock_client):
        """Test document search"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {"id": "doc1", "content": "Result 1"},
                {"id": "doc2", "content": "Result 2"}
            ]
        }
        mock_post.return_value = mock_response
        
        results = mock_client.search_documents("test query", 5)
        
        assert len(results) == 2
        assert results[0]["id"] == "doc1"
        mock_post.assert_called_once_with(
            "http://localhost:8020/search",
            json={"query": "test query", "limit": 5},
            timeout=30
        )


class TestDocumentProcessor:
    """Test document processing functionality"""
    
    @pytest.fixture
    def mock_processor(self):
        """Create a document processor with mocked client"""
        config = Config.default()
        mock_client = Mock(spec=LightRAGClient)
        return DocumentProcessor(config, mock_client)
    
    def test_get_document_id(self, mock_processor):
        """Test document ID generation"""
        doc_id = mock_processor._get_document_id("docs/test.md")
        expected_id = hashlib.md5("docs/test.md".encode()).hexdigest()
        assert doc_id == expected_id
    
    def test_handle_added_file(self, mock_processor):
        """Test handling of added files"""
        change = FileChange(
            path="docs/new.md",
            change_type=ChangeType.ADDED,
            content="# New document",
            content_hash="abc123"
        )
        
        mock_processor.client.insert_document.return_value = True
        
        result = mock_processor._handle_added_file(
            change, 
            "doc123"
        )
        
        assert result is True
        mock_processor.client.insert_document.assert_called_once()
        
        # Check the call arguments
        args, kwargs = mock_processor.client.insert_document.call_args
        assert args[0] == "# New document"
        assert kwargs["metadata"]["file_path"] == "docs/new.md"
        assert kwargs["metadata"]["change_type"] == "added"
    
    def test_handle_modified_file(self, mock_processor):
        """Test handling of modified files"""
        change = FileChange(
            path="docs/updated.md",
            change_type=ChangeType.MODIFIED,
            content="# Updated document",
            content_hash="def456"
        )
        
        mock_processor.client.update_document.return_value = True
        
        result = mock_processor._handle_modified_file(
            change, 
            "doc123"
        )
        
        assert result is True
        mock_processor.client.update_document.assert_called_once_with(
            "doc123",
            "# Updated document",
            {
                "file_path": "docs/updated.md",
                "change_type": "modified",
                "content_hash": "def456"
            }
        )
    
    def test_handle_deleted_file(self, mock_processor):
        """Test handling of deleted files"""
        change = FileChange(
            path="docs/deleted.md",
            change_type=ChangeType.DELETED
        )
        
        mock_processor.client.delete_document.return_value = True
        
        result = mock_processor._handle_deleted_file(
            change, 
            "doc123"
        )
        
        assert result is True
        mock_processor.client.delete_document.assert_called_once_with("doc123")
    
    def test_handle_renamed_file(self, mock_processor):
        """Test handling of renamed files"""
        change = FileChange(
            path="docs/new_name.md",
            change_type=ChangeType.RENAMED,
            old_path="docs/old_name.md",
            content="# Renamed document",
            content_hash="ghi789"
        )
        
        mock_processor.client.delete_document.return_value = True
        mock_processor.client.insert_document.return_value = True
        
        result = mock_processor._handle_renamed_file(
            change, 
            "new_doc_id"
        )
        
        assert result is True
        
        # Should delete old document
        old_doc_id = mock_processor._get_document_id("docs/old_name.md")
        mock_processor.client.delete_document.assert_called_once_with(old_doc_id)
        
        # Should insert new document
        mock_processor.client.insert_document.assert_called_once()
    
    def test_process_changes_dry_run(self, mock_processor):
        """Test processing changes in dry run mode"""
        mock_processor.config.dry_run = True
        
        changes = [
            FileChange("docs/test.md", ChangeType.ADDED, content="Test"),
            FileChange("docs/other.md", ChangeType.MODIFIED, content="Other")
        ]
        
        results = mock_processor.process_changes(changes)
        
        assert results["processed"] == 2
        assert results["failed"] == 0
        assert results["skipped"] == 0
        
        # Should not call API methods in dry run
        assert not mock_processor.client.insert_document.called
        assert not mock_processor.client.update_document.called


class TestDocSyncSystem:
    """Test the main system coordinator"""
    
    @pytest.fixture
    def mock_system(self):
        """Create a system with all mocked dependencies"""
        config = Config.default()
        
        with patch('docsync.GitAnalyzer') as mock_git, \
             patch('docsync.LightRAGClient') as mock_client, \
             patch('docsync.DocumentProcessor') as mock_processor:
            
            system = DocSyncSystem(config)
            system.git_analyzer = mock_git.return_value
            system.lightrag_client = mock_client.return_value
            system.processor = mock_processor.return_value
            
            return system
    
    def test_sync_since_commit(self, mock_system):
        """Test syncing changes since a commit"""
        # Mock API health check
        mock_system.lightrag_client.health_check.return_value = True
        
        # Mock change detection
        mock_changes = [
            FileChange("docs/test.md", ChangeType.ADDED, content="Test")
        ]
        mock_system.git_analyzer.get_changes_since_commit.return_value = mock_changes
        
        # Mock processing results
        mock_system.processor.process_changes.return_value = {
            "processed": 1, "failed": 0, "skipped": 0
        }
        
        results = mock_system.sync_since_commit("abc123")
        
        # Verify calls
        mock_system.lightrag_client.health_check.assert_called_once()
        mock_system.git_analyzer.get_changes_since_commit.assert_called_once_with("abc123")
        mock_system.processor.process_changes.assert_called_once_with(mock_changes)
        
        assert results["processed"] == 1
    
    def test_sync_api_unavailable(self, mock_system):
        """Test behavior when API is unavailable"""
        mock_system.lightrag_client.health_check.return_value = False
        
        with pytest.raises(RuntimeError, match="LightRAG API is not accessible"):
            mock_system.sync_since_commit("abc123")


class TestIntegration:
    """Integration tests using real Git repository"""
    
    @pytest.fixture
    def integration_repo(self):
        """Create a more complex test repository"""
        temp_dir = tempfile.mkdtemp()
        repo_path = Path(temp_dir)
        
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_path, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_path, check=True)
        
        # Create directory structure
        (repo_path / "docs").mkdir()
        (repo_path / "docs" / "api").mkdir()
        (repo_path / "src").mkdir()
        
        # Create various files
        files = {
            "docs/readme.md": "# Main Documentation",
            "docs/api/auth.md": "# Authentication",
            "docs/guide.markdown": "# User Guide",
            "src/main.py": "# Python source",
            "docs/temp/cache.md": "# Temp file"
        }
        
        for file_path, content in files.items():
            full_path = repo_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
        
        # Initial commit
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path, check=True)
        
        yield repo_path
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @patch('docsync.LightRAGClient')
    def test_end_to_end_workflow(self, mock_client_class, integration_repo):
        """Test complete end-to-end workflow"""
        # Setup config
        config = Config.default()
        config.exclude_patterns.append("**/temp/**")
        
        # Mock LightRAG client
        mock_client = Mock()
        mock_client.health_check.return_value = True
        mock_client.insert_document.return_value = True
        mock_client.update_document.return_value = True
        mock_client.delete_document.return_value = True
        mock_client_class.return_value = mock_client
        
        # Create system
        system = DocSyncSystem(config, str(integration_repo))
        
        # Get initial commit
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"], 
            cwd=integration_repo, 
            capture_output=True, 
            text=True, 
            check=True
        )
        initial_commit = result.stdout.strip()
        
        # Make various changes
        (integration_repo / "docs" / "new.md").write_text("# New Document")
        (integration_repo / "docs" / "readme.md").write_text("# Updated Main Documentation")
        (integration_repo / "docs" / "api" / "auth.md").unlink()  # Delete file
        
        # Move file (simulate rename)
        (integration_repo / "docs" / "guide.markdown").rename(
            integration_repo / "docs" / "user-guide.md"
        )
        
        # Add changes to git
        subprocess.run(["git", "add", "."], cwd=integration_repo, check=True)
        subprocess.run(["git", "commit", "-m", "