# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

- `npm start` - Start development server at http://localhost:3000
- `npm build` - Build for production
- `npm test` - Run tests with React Testing Library
- `npm eject` - Eject from Create React App (not recommended)

## Architecture Overview
@docs/adr/0002-tech-stack.md

Key tech stack:
- Frontend: React 18+ TypeScript, @xyflow/react, shadcn/ui, Tailwind
- Backend: Python 3.10+, FastAPI, WebSockets
- Testing: Vitest, React Testing Library

## Repo Structure
@docs/adr/0001-adopt-monorepo-structure.md


## Specifications

The `/specs` folder contains detailed specifications that drive the implementation.

Always reference the specs when making changes to ensure consistency with the design intent.