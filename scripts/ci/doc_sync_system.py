#!/usr/bin/env python3
"""
Documentation Change Detection & Knowledge DB Sync System

A system to detect changes in documentation files (MD) within a Git repository
and synchronize those changes with a LightRAG-based Knowledge Database.

Author: AI Assistant
License: MIT
"""

import os
import sys
import json
import logging
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import requests
from urllib.parse import urljoin
import hashlib
import yaml


class ChangeType(Enum):
    """Types of file changes detected"""
    ADDED = "added"
    MODIFIED = "modified"
    DELETED = "deleted"
    RENAMED = "renamed"


@dataclass
class FileChange:
    """Represents a change to a documentation file"""
    path: str
    change_type: ChangeType
    old_path: Optional[str] = None  # For renamed files
    content: Optional[str] = None
    content_hash: Optional[str] = None


@dataclass
class Config:
    """Configuration for the documentation sync system"""
    # Git settings
    watch_directories: List[str]
    file_extensions: List[str]
    exclude_patterns: List[str]
    
    # LightRAG API settings
    api_base_url: str
    api_timeout: int
    
    # Processing settings
    batch_size: int
    dry_run: bool
    
    # Logging
    log_level: str
    log_file: Optional[str]
    
    @classmethod
    def from_file(cls, config_path: str) -> 'Config':
        """Load configuration from YAML file"""
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
        return cls(**data)
    
    @classmethod
    def default(cls) -> 'Config':
        """Return default configuration"""
        return cls(
            watch_directories=["docs/", "documentation/"],
            file_extensions=[".md", ".markdown"],
            exclude_patterns=["**/node_modules/**", "**/.git/**", "**/build/**"],
            api_base_url="http://localhost:8020",
            api_timeout=30,
            batch_size=10,
            dry_run=False,
            log_level="INFO",
            log_file=None
        )


class GitAnalyzer:
    """Analyzes Git repository changes for documentation files"""
    
    def __init__(self, config: Config, repo_path: str = "."):
        self.config = config
        self.repo_path = Path(repo_path).resolve()
        self.logger = logging.getLogger(__name__)
    
    def get_changes_since_commit(self, commit_hash: str) -> List[FileChange]:
        """Get changes since a specific commit"""
        try:
            # Get the diff with file status
            cmd = ["git", "diff", "--name-status", commit_hash, "HEAD"]
            result = subprocess.run(
                cmd, 
                cwd=self.repo_path, 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            changes = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                parts = line.split('\t')
                if len(parts) < 2:
                    continue
                
                status = parts[0]
                file_path = parts[1]
                
                # Check if file matches our criteria
                if not self._should_process_file(file_path):
                    continue
                
                change = self._parse_git_status(status, file_path, parts)
                if change:
                    changes.append(change)
            
            return changes
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git command failed: {e}")
            return []
    
    def get_changes_between_commits(self, from_commit: str, to_commit: str) -> List[FileChange]:
        """Get changes between two commits"""
        try:
            cmd = ["git", "diff", "--name-status", from_commit, to_commit]
            result = subprocess.run(
                cmd, 
                cwd=self.repo_path, 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            changes = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                parts = line.split('\t')
                if len(parts) < 2:
                    continue
                
                status = parts[0]
                file_path = parts[1]
                
                if not self._should_process_file(file_path):
                    continue
                
                change = self._parse_git_status(status, file_path, parts)
                if change:
                    changes.append(change)
            
            return changes
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git command failed: {e}")
            return []
    
    def get_staged_changes(self) -> List[FileChange]:
        """Get currently staged changes"""
        try:
            cmd = ["git", "diff", "--cached", "--name-status"]
            result = subprocess.run(
                cmd, 
                cwd=self.repo_path, 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            changes = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                parts = line.split('\t')
                if len(parts) < 2:
                    continue
                
                status = parts[0]
                file_path = parts[1]
                
                if not self._should_process_file(file_path):
                    continue
                
                change = self._parse_git_status(status, file_path, parts)
                if change:
                    changes.append(change)
            
            return changes
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git command failed: {e}")
            return []
    
    def _should_process_file(self, file_path: str) -> bool:
        """Check if file should be processed based on configuration"""
        path = Path(file_path)
        
        # Check if file is in watched directories
        in_watched_dir = any(
            str(path).startswith(watch_dir.rstrip('/'))
            for watch_dir in self.config.watch_directories
        )
        
        if not in_watched_dir:
            return False
        
        # Check file extension
        if path.suffix not in self.config.file_extensions:
            return False
        
        # Check exclude patterns
        for pattern in self.config.exclude_patterns:
            if path.match(pattern):
                return False
        
        return True
    
    def _parse_git_status(self, status: str, file_path: str, parts: List[str]) -> Optional[FileChange]:
        """Parse git status and create FileChange object"""
        change_type = None
        old_path = None
        
        if status.startswith('A'):
            change_type = ChangeType.ADDED
        elif status.startswith('M'):
            change_type = ChangeType.MODIFIED
        elif status.startswith('D'):
            change_type = ChangeType.DELETED
        elif status.startswith('R'):
            change_type = ChangeType.RENAMED
            if len(parts) >= 3:
                old_path = parts[1]
                file_path = parts[2]
        
        if not change_type:
            return None
        
        # Get file content if file exists and wasn't deleted
        content = None
        content_hash = None
        
        if change_type != ChangeType.DELETED:
            full_path = self.repo_path / file_path
            if full_path.exists():
                try:
                    content = full_path.read_text(encoding='utf-8')
                    content_hash = hashlib.md5(content.encode()).hexdigest()
                except Exception as e:
                    self.logger.warning(f"Could not read file {file_path}: {e}")
        
        return FileChange(
            path=file_path,
            change_type=change_type,
            old_path=old_path,
            content=content,
            content_hash=content_hash
        )


class LightRAGClient:
    """Client for interacting with LightRAG API"""
    
    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.api_base_url.rstrip('/')
        self.timeout = config.api_timeout
        self.logger = logging.getLogger(__name__)
    
    def health_check(self) -> bool:
        """Check if the LightRAG API is accessible"""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=self.timeout
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
    
    def insert_document(self, content: str, metadata: Optional[Dict] = None) -> bool:
        """Insert a new document into the knowledge base"""
        try:
            payload = {"input": content}
            if metadata:
                payload["metadata"] = metadata
            
            response = requests.post(
                f"{self.base_url}/insert",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                self.logger.info(f"Document inserted successfully")
                return True
            else:
                self.logger.error(f"Insert failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Insert request failed: {e}")
            return False
    
    def update_document(self, doc_id: str, content: str, metadata: Optional[Dict] = None) -> bool:
        """Update an existing document"""
        try:
            payload = {"input": content}
            if metadata:
                payload["metadata"] = metadata
            
            response = requests.put(
                f"{self.base_url}/update/{doc_id}",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                self.logger.info(f"Document {doc_id} updated successfully")
                return True
            else:
                self.logger.error(f"Update failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Update request failed: {e}")
            return False
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document from the knowledge base"""
        try:
            response = requests.delete(
                f"{self.base_url}/delete/{doc_id}",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                self.logger.info(f"Document {doc_id} deleted successfully")
                return True
            else:
                self.logger.error(f"Delete failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Delete request failed: {e}")
            return False
    
    def search_documents(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for documents in the knowledge base"""
        try:
            payload = {"query": query, "limit": limit}
            response = requests.post(
                f"{self.base_url}/search",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json().get("results", [])
            else:
                self.logger.error(f"Search failed: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            self.logger.error(f"Search request failed: {e}")
            return []


class DocumentProcessor:
    """Processes document changes and synchronizes with Knowledge DB"""
    
    def __init__(self, config: Config, lightrag_client: LightRAGClient):
        self.config = config
        self.client = lightrag_client
        self.logger = logging.getLogger(__name__)
    
    def process_changes(self, changes: List[FileChange]) -> Dict[str, int]:
        """Process a list of file changes"""
        results = {
            "processed": 0,
            "failed": 0,
            "skipped": 0
        }
        
        for change in changes:
            try:
                if self.config.dry_run:
                    self.logger.info(f"DRY RUN: Would process {change.change_type.value} for {change.path}")
                    results["processed"] += 1
                    continue
                
                success = self._process_single_change(change)
                if success:
                    results["processed"] += 1
                else:
                    results["failed"] += 1
                    
            except Exception as e:
                self.logger.error(f"Error processing change for {change.path}: {e}")
                results["failed"] += 1
        
        return results
    
    def _process_single_change(self, change: FileChange) -> bool:
        """Process a single file change"""
        doc_id = self._get_document_id(change.path)
        
        if change.change_type == ChangeType.ADDED:
            return self._handle_added_file(change, doc_id)
        elif change.change_type == ChangeType.MODIFIED:
            return self._handle_modified_file(change, doc_id)
        elif change.change_type == ChangeType.DELETED:
            return self._handle_deleted_file(change, doc_id)
        elif change.change_type == ChangeType.RENAMED:
            return self._handle_renamed_file(change, doc_id)
        
        return False
    
    def _handle_added_file(self, change: FileChange, doc_id: str) -> bool:
        """Handle newly added file"""
        if not change.content:
            self.logger.warning(f"No content available for added file: {change.path}")
            return False
        
        metadata = {
            "file_path": change.path,
            "change_type": change.change_type.value,
            "content_hash": change.content_hash
        }
        
        return self.client.insert_document(change.content, metadata)
    
    def _handle_modified_file(self, change: FileChange, doc_id: str) -> bool:
        """Handle modified file"""
        if not change.content:
            self.logger.warning(f"No content available for modified file: {change.path}")
            return False
        
        metadata = {
            "file_path": change.path,
            "change_type": change.change_type.value,
            "content_hash": change.content_hash
        }
        
        # Try to update first, if that fails, insert as new
        success = self.client.update_document(doc_id, change.content, metadata)
        if not success:
            self.logger.info(f"Update failed for {change.path}, trying insert")
            success = self.client.insert_document(change.content, metadata)
        
        return success
    
    def _handle_deleted_file(self, change: FileChange, doc_id: str) -> bool:
        """Handle deleted file"""
        return self.client.delete_document(doc_id)
    
    def _handle_renamed_file(self, change: FileChange, doc_id: str) -> bool:
        """Handle renamed file"""
        # Delete the old document and insert the new one
        old_doc_id = self._get_document_id(change.old_path) if change.old_path else None
        
        success = True
        if old_doc_id:
            success = self.client.delete_document(old_doc_id)
        
        if success and change.content:
            metadata = {
                "file_path": change.path,
                "change_type": change.change_type.value,
                "old_path": change.old_path,
                "content_hash": change.content_hash
            }
            success = self.client.insert_document(change.content, metadata)
        
        return success
    
    def _get_document_id(self, file_path: str) -> str:
        """Generate a consistent document ID from file path"""
        return hashlib.md5(file_path.encode()).hexdigest()


class DocSyncSystem:
    """Main system coordinator"""
    
    def __init__(self, config: Config, repo_path: str = "."):
        self.config = config
        self.git_analyzer = GitAnalyzer(config, repo_path)
        self.lightrag_client = LightRAGClient(config)
        self.processor = DocumentProcessor(config, self.lightrag_client)
        self.logger = logging.getLogger(__name__)
    
    def sync_since_commit(self, commit_hash: str) -> Dict[str, int]:
        """Sync changes since a specific commit"""
        self.logger.info(f"Analyzing changes since commit: {commit_hash}")
        
        # Check API health
        if not self.lightrag_client.health_check():
            raise RuntimeError("LightRAG API is not accessible")
        
        changes = self.git_analyzer.get_changes_since_commit(commit_hash)
        self.logger.info(f"Found {len(changes)} documentation changes")
        
        return self.processor.process_changes(changes)
    
    def sync_between_commits(self, from_commit: str, to_commit: str) -> Dict[str, int]:
        """Sync changes between two commits"""
        self.logger.info(f"Analyzing changes between {from_commit} and {to_commit}")
        
        if not self.lightrag_client.health_check():
            raise RuntimeError("LightRAG API is not accessible")
        
        changes = self.git_analyzer.get_changes_between_commits(from_commit, to_commit)
        self.logger.info(f"Found {len(changes)} documentation changes")
        
        return self.processor.process_changes(changes)
    
    def sync_staged_changes(self) -> Dict[str, int]:
        """Sync currently staged changes"""
        self.logger.info("Analyzing staged changes")
        
        if not self.lightrag_client.health_check():
            raise RuntimeError("LightRAG API is not accessible")
        
        changes = self.git_analyzer.get_staged_changes()
        self.logger.info(f"Found {len(changes)} staged documentation changes")
        
        return self.processor.process_changes(changes)


def setup_logging(config: Config):
    """Setup logging configuration"""
    log_level = getattr(logging, config.log_level.upper())
    
    handlers = [logging.StreamHandler(sys.stdout)]
    if config.log_file:
        handlers.append(logging.FileHandler(config.log_file))
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )


def create_default_config_file(config_path: str):
    """Create a default configuration file"""
    config = Config.default()
    config_dict = asdict(config)
    
    with open(config_path, 'w') as f:
        yaml.safe_dump(config_dict, f, default_flow_style=False)
    
    print(f"Default configuration created at: {config_path}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Documentation Change Detection & Knowledge DB Sync System"
    )
    
    parser.add_argument(
        "--config", 
        type=str, 
        default="docsync.yaml",
        help="Configuration file path"
    )
    
    parser.add_argument(
        "--create-config",
        action="store_true",
        help="Create a default configuration file"
    )
    
    parser.add_argument(
        "--repo-path",
        type=str,
        default=".",
        help="Path to Git repository"
    )
    
    # Operation modes
    mode_group = parser.add_mutually_exclusive_group(required=False)
    mode_group.add_argument(
        "--since-commit",
        type=str,
        help="Sync changes since a specific commit"
    )
    
    mode_group.add_argument(
        "--between-commits",
        nargs=2,
        metavar=("FROM", "TO"),
        help="Sync changes between two commits"
    )
    
    mode_group.add_argument(
        "--staged",
        action="store_true",
        help="Sync staged changes"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    
    args = parser.parse_args()
    
    # Create default config if requested
    if args.create_config:
        create_default_config_file(args.config)
        return 0
    
    # Load configuration
    try:
        if os.path.exists(args.config):
            config = Config.from_file(args.config)
        else:
            print(f"Configuration file not found: {args.config}")
            print("Use --create-config to create a default configuration file")
            return 1
        
        # Override dry-run from command line
        if args.dry_run:
            config.dry_run = True
        
        setup_logging(config)
        
        # Initialize the system
        system = DocSyncSystem(config, args.repo_path)
        
        # Execute based on mode
        results = None
        if args.since_commit:
            results = system.sync_since_commit(args.since_commit)
        elif args.between_commits:
            results = system.sync_between_commits(args.between_commits[0], args.between_commits[1])
        elif args.staged:
            results = system.sync_staged_changes()
        else:
            # Default: sync staged changes
            results = system.sync_staged_changes()
        
        # Print results
        if results:
            print(f"\nResults:")
            print(f"  Processed: {results['processed']}")
            print(f"  Failed: {results['failed']}")
            print(f"  Skipped: {results['skipped']}")
            
            return 0 if results['failed'] == 0 else 1
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
