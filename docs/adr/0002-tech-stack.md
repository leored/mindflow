# 0002 - Tech Stack

**Status:** Accepted  
**Date:** 2025-08-05

## Context

Our application includes frontend in Javascript and a backend in Python. 

## Decision


MindFlow is a React TypeScript application for creating and editing visual flows with nodes and connections. The app follows a clean architecture pattern with centralized state management.

The tech stack is described below:
### Frontend Stack (User Interface & Node Graph)
#### Core UI Framework
* React 18+ with TypeScript
* Modern hooks and functional components for reactivity and modularity
* Full type safety across all components
* Component composition patterns following React best practices

#### Node Graph Engine
@xyflow/react (React Flow v12)
* Browser-based canvas engine for rendering interactive node graphs
* Highly customizable and extensible
* Integrated via React components (FlowEditor, CustomNode)

#### UI Libraries
* shadcn/ui with Radix UI primitives
* Tailwind CSS for utility-first styling and rapid prototyping
* Lucide React for consistent iconography
* Responsive design with dark/light theme support

#### State Management
* React hooks (useState, useCallback, useContext)
* @xyflow/react built-in state management for node graph
* LocalStorage for flow persistence
* Future: Consider Zustand or Redux Toolkit for complex state

#### Testing
* Vitest for unit tests with React Testing Library
* JSDOM for DOM simulation
* Optional: Playwright or Cypress for end-to-end testing

### Backend Stack (Execution Engine & Graph Computation)

#### Core Runtime Engine
* Python 3.10+
* Executes the graph nodes in a computation pipeline.
* Each node is a Python class or function, often modular.

#### Node System
* Custom plugin architecture:
* Each node is a Python module exposing metadata (inputs, outputs, behavior).
* Nodes register themselves into a global registry (like a node catalog).

#### Execution Controller
* Orchestrates the directed acyclic graph (DAG) of nodes:
** Resolves dependencies.
** Manages state (e.g., input/output blobs).
** Supports async execution, batching, caching, etc.

#### Sandboxing/Execution Isolation
* Optional: Docker or multiprocessing to isolate risky operations or long-running tasks.

### Communication Layer (Client ↔ Backend)
#### WebSocket Server
* FastAPI + WebSockets (Starlette)
* Bi-directional communication:
** From UI: Node manipulations, pipeline triggers.
** From backend: Real-time status, logs, execution results.

#### REST API (Optional)
For static interactions: loading/saving pipelines, uploading images, managing sessions, etc.

### Storage & File Handling
#### Pipeline & Workflow Serialization
* JSON-based format for saving node graphs.
* Each node includes ID, type, position, parameters, and connections.

#### Blob / Cache Storage
* Local disk for performance and simplicity.
* Optionally mount persistent storage (e.g., AWS S3, GCS).

### DevOps & Tooling
#### Dev Environment
* Vite 7+ for frontend development with React Fast Refresh
* Python virtualenv or Poetry for backend dependencies
* TypeScript 5+ with strict mode for type checking

#### Packaging / Deployment
* Docker:
** One container for the backend (Python FastAPI)
** One for the frontend (React app via Nginx or Node)
** GitHub Actions or GitLab CI for CI/CD pipelines

### Extensibility Framework
* For Custom Nodes (Python Plugins)
* Plugin discovery via importlib or explicit folder scan
* Hot-reloading or restart-on-change to load new nodes
* For Custom UI Widgets (React Components)
* Dynamic component loading with React.lazy
* Hooks into React Flow node types and custom components

#### Alternatives considered

- **Multi-repo**: More separation, but added complexity in CI/CD, branching, and coordinating releases.
- **Polyrepo with submodules**: Complex and error-prone in practice.
- **Monorepo** ✅: Simplifies coordination, aligns well with our team setup and deployment model.

## Consequences



