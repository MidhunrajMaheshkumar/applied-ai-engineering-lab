# Applied AI & Backend Systems Engineering Lab

A structured monorepo tracking the implementation of scalable backend services, asynchronous pipelines, and enterprise-grade applied AI systems (RAG, Agentic Workflows, MCP, and Evals).

## Repository Architecture

### Foundational Modules (`/modules`)
- **[01-backend-core](./modules/01-backend-core):** Production FastAPI microservice, Pydantic V2 schema validation, dependency injection, and asynchronous database modeling.
- **02-rag-vector-search:** High-precision hybrid document retrieval with `pgvector`, reciprocal rank fusion (RRF), and cross-encoder reranking.
- **03-agentic-workflows:** Deterministic state machines via LangGraph, Model Context Protocol (MCP) integrations, and human-in-the-loop safeguards.
- **04-evals-and-mlops:** Automated CI/CD assertion test suites (DeepEval), token cost tracking, and observability with Langfuse.

### Flagship Projects (`/projects`)
1. **Autonomous Lead Triage Engine:** Event-driven inbound qualification agent connecting webhook inputs, Pydantic extraction contracts, and PostgreSQL CRM storage.
2. **Enterprise Document & Text-to-SQL Assistant:** Hybrid RAG pipeline with schema-aware SQL generation and read-only database execution constraints.

## Shared Infrastructure
Run all supporting services (PostgreSQL 16 with pgvector + Redis 7):
```bash
docker compose up -d