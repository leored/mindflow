# Documentation Change Detection & Knowledge DB Sync System

A Python-based system that monitors changes in documentation files within a Git repository and automatically synchronizes those changes with a LightRAG-based Knowledge Database. This system can be deployed as a CLI tool, Git hook, GitHub Action, or background service.

## Features

- **Git Integration**: Detects changes in documentation files across commits
- **Flexible Configuration**: Customizable file patterns, directories, and exclusions
- **LightRAG Integration**: Seamless synchronization with LightRAG Knowledge Database
- **Multiple Deployment Options**: CLI, hooks, GitHub Actions, Docker, systemd
- **Change Type Detection**: Handles added, modified, deleted, and renamed files
- **Dry Run Mode**: Test changes without affecting the Knowledge DB
- **Comprehensive Logging**: Detailed logging with configurable levels

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Git Repo      │    │   DocSync        │    │   LightRAG      │
│                 │    │   System         │    │   Knowledge DB  │
│  ┌─────────────┐│    │                  │    │                 │
│  │ .md files   ││───▶│ GitAnalyzer      │───▶│ API Endpoints   │
│  │ changes     ││    │ DocumentProcessor │    │ /insert         │
│  └─────────────┘│    │ LightRAGClient   │    │ /update         │
│                 │    │                  │    │ /delete         │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Installation

1. **Clone or download the system files**:
   ```bash
   # Download the main script and configuration
   curl -O https://raw.githubusercontent.com/your-repo/docsync.py
   curl -O https://raw.githubusercontent.com/your-repo/docsync.yaml
   ```

2. **Install Python dependencies**:
   ```bash
   pip install requests PyYAML
   ```

3. **Create configuration file**:
   ```bash
   python docsync.py --create-config
   ```

4. **Edit configuration** to match your setup