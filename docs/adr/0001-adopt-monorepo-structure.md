# 0001 - Adopt Monorepo Structure

**Status:** Accepted  
**Date:** 2025-08-05

## Context

Our application includes frontend, backend, QA and DevOps components. Team members span multiple roles (UX, QA, Devs, etc.). We've observed friction when syncing changes across separate repos.

## Decision

We will use a **monorepo** to unify all components of the application into a single repository. It will include `frontend/`, `backend/`, `test/`, `docs/`, `specs/`, and shared tooling in `scripts/`.

## Alternatives considered

- **Multi-repo**: More separation, but added complexity in CI/CD, branching, and coordinating releases.
- **Polyrepo with submodules**: Complex and error-prone in practice.
- **Monorepo** ✅: Simplifies coordination, aligns well with our team setup and deployment model.

## Consequences

- We need clear folder structure and ownership conventions.
- CI/CD pipelines must be optimized to avoid triggering unnecessary jobs.
- Onboarding improves due to unified codebase.

### Repo Structure
mindflow/
├── frontend/              # React 18+ + @xyflow/react
│   ├── src/
│   ├── public/
│   └── vite.config.ts
│
├── backend/               # Python + FastAPI + Executor
│   ├── src/
│   │   ├── models/        # Custom node implementations
│   │   ├── core/          # 
│   │   ├── services/          # 
│   │   ├── plugins/       # DAG execution logic
│   │   ├── api/           # FastAPI routes
│   │   ├── websocket/           # FWebSockets
│   │   └── main.py
│   └── tests
│
├── shared/                # (Optional) Shared schema/types
│   ├── schemas/           # WebSocket/REST schema (JSON Schema or Pydantic)
│   ├── types/             # Common structures
│   └── utils/             # Any reusable tools across front/back
│
├── docker/                # Dockerfiles, compose setup
│   ├── frontend.Dockerfile
│   ├── backend.Dockerfile
│   └── docker-compose.yml
│
│
├── .gitignore
├── README.md
├── package.json         # For frontend + shared dev tooling
│
└── specs/               # Contains requirements, specifications
    ├── ontology/        # Description about Entities and Domain
    ├── functional/      # User stories and behavior requirements
    ├── features/        # Cross-cutting requirements
    └── ui/              # Component specifications and design requirements


