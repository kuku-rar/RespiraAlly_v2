# RespiraAlly Observability

**Observability Phase 1: Prometheus Metrics Integration**

This directory contains monitoring and observability configuration for RespiraAlly V2.0, implementing the Linus "Good Taste" philosophy: measure what matters, keep it simple, eliminate special cases.

## 📊 Components

### 1. **Prometheus** (Metrics Collection & Storage)
- **Web UI**: http://localhost:9090
- **Purpose**: Collects and stores time-series metrics from the FastAPI backend
- **Metrics Exposed**: Request latency, request count, error rates, active requests

### 2. **Grafana** (Metrics Visualization)
- **Web UI**: http://localhost:13000
- **Credentials**: admin / admin (change on first login)
- **Purpose**: Visualizes metrics with pre-configured dashboards

## 🚀 Quick Start

### Start Observability Stack

```bash
# From project root
docker-compose --profile observability up -d prometheus grafana

# Verify services are running
docker-compose ps
```

### Access Dashboards

1. **Prometheus**: http://localhost:9090
   - Query metrics using PromQL
   - Example: `rate(http_requests_total[5m])`

2. **Grafana**: http://localhost:13000
   - Login: admin / admin
   - Pre-configured dashboard: "RespiraAlly API Metrics"

### Start Backend with Metrics

```bash
# Terminal 1: Start dependencies (PostgreSQL, Redis, RabbitMQ)
docker-compose up -d postgres redis rabbitmq

# Terminal 2: Start observability stack
docker-compose --profile observability up -d prometheus grafana

# Terminal 3: Start backend (from backend directory)
cd backend
uv run uvicorn respira_ally.main:app --reload --host 127.0.0.1 --port 8000
```

### Verify Metrics Collection

1. **Check /metrics endpoint**:
   ```bash
   curl http://localhost:8000/metrics
   ```

2. **Generate some traffic**:
   ```bash
   # Health check
   curl http://localhost:8000/health

   # API requests (will generate metrics)
   curl http://localhost:8000/api/v1/auth/login
   curl http://localhost:8000/api/v1/patients
   ```

3. **View metrics in Prometheus**:
   - Open http://localhost:9090
   - Query: `http_requests_total`
   - Click "Graph" tab to visualize

4. **View dashboard in Grafana**:
   - Open http://localhost:13000
   - Navigate to "RespiraAlly API Metrics" dashboard

## 📈 Metrics Collected

### HTTP Request Metrics

| Metric | Type | Description | Labels |
|--------|------|-------------|--------|
| `http_request_duration_seconds` | Histogram | Request latency distribution | method, endpoint, status_code |
| `http_requests_total` | Counter | Total HTTP requests | method, endpoint, status_code |
| `http_errors_total` | Counter | Total HTTP errors (4xx, 5xx) | method, endpoint, status_code, error_type |
| `http_requests_in_progress` | Gauge | Active requests being processed | method, endpoint |

### Example PromQL Queries

```promql
# Request rate (requests per second)
rate(http_requests_total[5m])

# P95 latency (95th percentile)
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Error rate
rate(http_errors_total[5m])

# Active requests
http_requests_in_progress

# Request rate by endpoint
sum by (endpoint) (rate(http_requests_total[5m]))

# Error rate by status code
sum by (status_code) (rate(http_errors_total[5m]))
```

## 🗂️ Directory Structure

```
observability/
├── README.md                          # This file
├── prometheus/
│   └── prometheus.yml                 # Prometheus configuration
└── grafana/
    └── provisioning/
        ├── datasources/
        │   └── prometheus.yml         # Auto-provision Prometheus datasource
        └── dashboards/
            ├── dashboard.yml          # Dashboard provisioning config
            └── respirally-api.json    # Pre-configured API metrics dashboard
```

## 🔧 Configuration

### Prometheus (`prometheus/prometheus.yml`)

- **Scrape Interval**: 15 seconds
- **Targets**:
  - `backend:8000` - RespiraAlly FastAPI backend
  - `localhost:9090` - Prometheus self-monitoring

### Grafana Dashboards

Pre-configured dashboard includes:
1. **Request Rate**: requests/sec by endpoint
2. **Request Duration (P95)**: 95th percentile latency
3. **Error Rate**: 4xx and 5xx errors
4. **Active Requests**: Current in-flight requests
5. **Request Summary**: Table view of all endpoints

## 🎯 Linus "Good Taste" Principles Applied

1. **Eliminates Special Cases**: All endpoints tracked uniformly, no special handling
2. **Single Source of Truth**: Metrics in one place (Prometheus middleware)
3. **No Nested Complexity**: Clean, linear metric collection path
4. **Minimal Overhead**: < 1ms latency impact per request

## 🛡️ Production Considerations

### Security

1. **Grafana**:
   - Change default admin password immediately
   - Consider enabling authentication via OAuth2/LDAP
   - Restrict network access to monitoring UIs

2. **Prometheus**:
   - Enable authentication for remote_write
   - Use HTTPS for external access
   - Implement proper RBAC (Role-Based Access Control)

### Performance

- **Metrics Cardinality**: Monitor label combinations to avoid explosion
- **Retention**: Default 15 days, adjust based on disk space
- **Query Performance**: Use recording rules for expensive queries

### Scaling

- **Prometheus**: Consider federation or remote storage for multi-instance setups
- **Grafana**: Use separate instance for production with HA setup

## 🔄 Observability Roadmap

- ✅ **Phase 1**: Prometheus Metrics (Current)
  - HTTP request metrics
  - Basic Grafana dashboards

- 🔜 **Phase 2**: Structured Logging (Next)
  - structlog integration
  - Correlation ID middleware
  - Centralized log aggregation

- 📋 **Phase 3**: Distributed Tracing (Future)
  - OpenTelemetry integration
  - Jaeger tracing backend
  - Request flow visualization

- 📋 **Phase 4**: Alert Rules (Future)
  - Critical error rate alerts
  - High latency alerts
  - Service availability monitors

## 📚 Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [FastAPI Metrics Best Practices](https://fastapi.tiangolo.com/advanced/metrics/)
- [PromQL Cheat Sheet](https://promlabs.com/promql-cheat-sheet/)

## 🐛 Troubleshooting

### Prometheus can't scrape backend

```bash
# Check if backend is accessible from Prometheus container
docker exec respirally-prometheus wget -qO- http://backend:8000/metrics

# Check Prometheus targets
# Open http://localhost:9090/targets
```

### Grafana dashboard shows "No Data"

1. Check Prometheus datasource: Configuration > Data Sources > Prometheus
2. Verify Prometheus is scraping: http://localhost:9090/targets
3. Check if backend is generating metrics: `curl http://localhost:8000/metrics`

### Metrics endpoint returns 500 error

```bash
# Check backend logs
docker-compose logs backend

# Test metrics import
cd backend
uv run python -c "from respira_ally.infrastructure.observability import PrometheusMetricsMiddleware; print('OK')"
```

## 👥 Support

For issues or questions:
1. Check [docs/dev_logs/CHANGELOG_*.md](../docs/dev_logs/) for recent changes
2. Review [docs/16-1_wbs_development_plan_sprint4-8.md](../docs/16-1_wbs_development_plan_sprint4-8.md)
3. Open an issue in the project repository

---

**Version**: 1.0.0
**Last Updated**: 2025-11-01
**Maintained by**: RespiraAlly Team
