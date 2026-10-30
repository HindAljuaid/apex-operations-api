# Apex Operations API — Operational Runbook

## 1. Overview

A containerized FastAPI application backed by PostgreSQL.

- API: FastAPI, served by Uvicorn on port 8000.
- Database: PostgreSQL 16.
- Orchestration: Docker Compose.
- Health endpoints: `/health/live` and `/health/ready`.
- Metrics endpoint: `/metrics`.
- Container security: API runs as a non-root user.
- CI: GitHub Actions runs linting, automated tests, Docker build, and Trivy scanning.

This runbook describes the local assessment environment. It does not represent a production cloud deployment.

## 2. Prerequisites

- Docker Desktop installed and running.
- Docker Compose v2.
- Git.
- A local `.env` file.

Create the environment file if it does not exist:

`cp .env.example .env`

Review `.env` and set appropriate local database credentials. Never commit `.env` or use its development credentials in production.

## 3. Start and Stop the Application

Start the application using the default image version:

`docker compose up -d`

To select a specific locally available release:

`export APP_VERSION=1.0.3`

`docker compose up -d`

Check container status:

`docker compose ps`

Stop the application without deleting database data:

`docker compose down`

**Important:** Do not use `docker compose down -v` unless you intentionally want to delete the persistent database volume.

## 4. Health Checks

Check application liveness:

`curl http://localhost:8000/health/live`

Expected response:

`{"status":"alive"}`

Check application readiness:

`curl http://localhost:8000/health/ready`

Expected response:

`{"status":"ready"}`

Check the API root and reported application version:

`curl http://localhost:8000/`

Check the API documentation at:

`http://localhost:8000/docs`

The API container also has a Docker health check that periodically calls the liveness endpoint.

## 5. Logs and Metrics

View API logs:

`docker compose logs --tail=100 api`

Follow API logs continuously:

`docker compose logs -f api`

View database logs:

`docker compose logs --tail=100 db`

Inspect application metrics:

`curl -s http://localhost:8000/metrics`

Relevant metrics include:

- `apex_http_requests_total`: HTTP request count.
- `apex_http_request_duration_seconds`: HTTP request duration histogram.

The application exposes Prometheus-format metrics. A Prometheus server and alerting system are not currently deployed or configured.

## 6. Troubleshooting

### API container is unhealthy

1. Check container status using `docker compose ps`.
2. Inspect API logs using `docker compose logs --tail=100 api`.
3. Check liveness and readiness endpoints.
4. Confirm port 8000 is not already being used by another process.
5. Restart the API using `docker compose restart api`.

### Database connection or readiness failure

1. Check database status using `docker compose ps db`.
2. Inspect database logs using `docker compose logs --tail=100 db`.
3. Confirm the database variables in `.env` match the application connection URL.
4. Confirm PostgreSQL reports that it is ready to accept connections.
5. Restart the services if necessary using `docker compose up -d`.

Do not delete the database volume as a routine troubleshooting step.

### API returns HTTP 500

1. Inspect API logs for the error and timestamp.
2. Check database health and connectivity.
3. Reproduce the request using the API documentation or `curl`.
4. Review recent code or configuration changes.
5. If the issue started after a release, consider rolling back.

### Port 8000 is already in use

Identify the process using the port:

`lsof -i :8000`

Stop the conflicting process if appropriate, or change the host-side port mapping in `compose.yaml`.

## 7. Release and Rollback

The API image is versioned using the `APP_VERSION` environment variable.

Check which image version is selected:

`docker compose config | grep 'image:'`

Deploy a locally available version:

`export APP_VERSION=1.0.3`

`docker compose up -d`

Verify the deployed version:

`curl http://localhost:8000/`

`docker compose ps`

To roll back to the previous locally available release:

`export APP_VERSION=1.0.0`

`docker compose up -d`

Verify the application version and health endpoints after rollback.

**Rollback limitation:** This assessment demonstrates application image rollback. Database schema migrations are not versioned or automatically reversed. Production database changes require a separate migration and recovery strategy.

## 8. Security and Operational Notes

- The API container runs as a non-root user.
- Database credentials are supplied through environment variables.
- The PostgreSQL port is not published to the host in the Compose configuration.
- The database uses a named volume for persistence.
- GitHub Actions blocks the Docker build job when linting or tests fail.
- Trivy scans the built image for HIGH and CRITICAL vulnerabilities.
- The latest local Trivy scan found no HIGH or CRITICAL findings with available fixes when using `--ignore-unfixed`. Unfixed OS findings remain and must not be treated as resolved.
- Production deployments should use a secrets manager, immutable image tags, dependency updates, database migrations, and a monitored backup and restore process.

## 9. Suggested Monitoring and Alert Rules

These are proposed monitoring rules, not currently configured alerts. They assume Prometheus is deployed and scraping the API metrics.

| Condition | Suggested alert |
|---|---|
| API unavailable | Liveness or readiness probe fails for 2 minutes |
| High HTTP 5xx rate | More than 5% of requests return 5xx over 5 minutes |
| High latency | API p95 request duration exceeds 1 second for 5 minutes |
| Database unavailable | PostgreSQL health check fails for 2 minutes |
| Container restart loop | More than 3 restarts within 10 minutes |

Example PromQL for the HTTP 5xx rate:

`sum(rate(apex_http_requests_total{http_status=~"5.."}[5m])) / clamp_min(sum(rate(apex_http_requests_total[5m])), 1) > 0.05`

Example PromQL for API p95 latency:

`histogram_quantile(0.95, sum by (le) (rate(apex_http_request_duration_seconds_bucket[5m]))) > 1`

These expressions require the corresponding metrics to be scraped by Prometheus.