# Technical Decision Memo — Apex Operations API

## 1. Purpose

This memo documents the main technical decisions made while building the Apex Operations API for the Junior DevOps Engineer practical assessment.

The goal was to create a maintainable, testable, and secure containerized application while keeping the implementation simple enough to run locally without requiring paid cloud infrastructure.

## 2. Technology Decisions

### FastAPI for the REST API

**Decision:** Use FastAPI with Uvicorn.

**Reasoning:**
- Provides a lightweight Python framework for building REST APIs.
- Supports automatic OpenAPI documentation.
- Includes request validation and dependency injection.
- Integrates well with SQLAlchemy and automated testing.

**Trade-off:** FastAPI is Python-based, so application performance and concurrency must be considered when scaling to high workloads.

### PostgreSQL for Persistent Storage

**Decision:** Use PostgreSQL 16 as the application database.

**Reasoning:**
- Provides reliable relational data storage.
- Supports transactions and structured queries.
- Is suitable for a containerized application.
- Docker volumes allow data to persist across container restarts.

**Trade-off:** Running a separate database service adds configuration and operational overhead compared with an embedded database.

### Docker for Containerization

**Decision:** Package the API in a Docker image and use Docker Compose to run the API and database together.

**Reasoning:**
- Provides a consistent application runtime.
- Simplifies local setup and deployment.
- Separates application and database services.
- Supports image versioning and rollback.

**Security considerations:**
- The API runs as a non-root user.
- The PostgreSQL port is not exposed to the host.
- Database credentials are provided through environment variables.
- The final runtime image does not retain pip and its bundled packages.

**Trade-off:** Docker images require maintenance, security scanning, and periodic base-image updates.

### GitHub Actions for Continuous Integration

**Decision:** Use GitHub Actions to automate code quality checks, testing, image building, and vulnerability scanning.

**Pipeline order:**

1. Checkout source code.
2. Run Ruff linting.
3. Execute automated Pytest tests.
4. Build the Docker image.
5. Scan the image with Trivy.

The Docker build job depends on the successful completion of the quality job. This prevents an image build when linting or testing fails.

**Trade-off:** The current pipeline validates the application and builds an image but does not publish it to a registry or deploy it to a cloud environment.

### Trivy for Vulnerability Scanning

**Decision:** Use Trivy to scan the Docker image for operating-system and application-library vulnerabilities.

**Reasoning:**
- Identifies known vulnerabilities in image dependencies.
- Integrates with GitHub Actions.
- Can block the pipeline when HIGH or CRITICAL findings with available fixes are detected.

**Trade-off:** Some operating-system vulnerabilities may remain without an available fix. These findings must be reviewed and addressed when updates become available.

## 3. Deployment Strategy

**Decision:** Use local Docker Compose deployment instead of deploying to a paid cloud environment.

**Reasoning:**
- The assessment can be demonstrated without cloud infrastructure costs.
- Docker Compose provides a reproducible local environment.
- The application and database can be validated together.
- Versioned Docker images demonstrate release selection and rollback.

**Limitation:** This is a local deployment demonstration, not a production cloud deployment or a fully automated continuous delivery system.

## 4. Release and Rollback Strategy

**Decision:** Use versioned Docker image tags controlled through the `APP_VERSION` environment variable.

**Reasoning:**
- Allows the application to run a selected image version.
- Supports rollback to a previously built image.
- Makes the deployed application version easy to identify.

**Limitation:** Application image rollback does not automatically reverse database schema changes. A production implementation should use a database migration tool such as Alembic and define a separate database recovery strategy.

## 5. Health Checks and Observability

**Decision:** Provide application liveness and readiness endpoints, Docker health checks, structured metric instrumentation, and container logs.

**Reasoning:**
- Liveness helps identify whether the application process is responding.
- Readiness provides an application readiness check.
- Request counters and duration histograms provide basic monitoring data.
- Container logs support operational troubleshooting.

**Limitation:** Prometheus metrics are exposed by the API, but a Prometheus server, Grafana dashboard, and active alerting system are not configured in this assessment.

## 6. Testing Strategy

**Decision:** Use Pytest for automated application tests and Ruff for static code-quality checks.

The test suite includes checks for:
- Application health endpoints.
- Task creation and retrieval.
- Task updates and deletion.
- Metrics exposure.

An intentional failing test was also used to verify that the CI quality gate blocks the subsequent Docker build job.

**Limitation:** The automated tests use an isolated SQLite test database. Additional integration tests against PostgreSQL would improve confidence in the production database configuration.

## 7. Known Limitations and Future Improvements

The following improvements would be considered before production deployment:

1. Deploy the application to a managed cloud environment.
2. Add automated deployment after successful CI validation.
3. Introduce Alembic database migrations.
4. Configure Prometheus and Grafana for monitoring.
5. Implement active alerting for service availability, latency, and error rates.
6. Add automated database backups and restore testing.
7. Use a cloud secrets manager.
8. Establish a regular base-image and dependency update process.
9. Add PostgreSQL integration tests.

## 8. Final Decision

The selected architecture provides a practical balance between simplicity, maintainability, security, and demonstrability.

FastAPI, PostgreSQL, Docker Compose, GitHub Actions, Pytest, Ruff, and Trivy provide the core components needed to demonstrate the requested DevOps practices without introducing unnecessary infrastructure or cloud costs.

The current implementation is suitable as a local assessment demonstration and provides a foundation for future production-oriented improvements.