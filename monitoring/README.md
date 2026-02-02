# Monitoring Setup - Prometheus & Grafana

Production-grade monitoring configuration for the Gardening Service API.

## Overview

This monitoring stack provides:
- **Prometheus**: Metrics collection and alerting
- **Grafana**: Visual dashboards and analytics
- **Pre-configured dashboards**: API performance, errors, rate limiting, authentication
- **Alerting rules**: Automated alerts for critical conditions

## Quick Start

### 1. Start Monitoring Stack

```bash
# Start all services including monitoring
docker-compose up

# Or start monitoring only
docker-compose up prometheus grafana
```

### 2. Access Dashboards

- **Grafana**: http://localhost:3001
  - Username: `admin`
  - Password: `admin` (change in production!)

- **Prometheus**: http://localhost:9090

- **API Metrics**: http://localhost:8080/metrics

### 3. View Pre-configured Dashboard

1. Open Grafana at http://localhost:3001
2. Login with admin/admin
3. Navigate to Dashboards → Gardening Service API - Overview
4. Explore real-time metrics

## Architecture

```
┌─────────────┐
│   API       │ ─── /metrics endpoint
│   (8080)    │     (Prometheus format)
└─────────────┘
       │
       │ scrapes every 15s
       ▼
┌─────────────┐
│  Prometheus │ ─── Stores metrics
│   (9090)    │     Evaluates alerts
└─────────────┘
       │
       │ datasource
       ▼
┌─────────────┐
│   Grafana   │ ─── Visualizes data
│   (3001)    │     Shows dashboards
└─────────────┘
```

## Metrics Collected

### HTTP Metrics (from API)
- `http_requests_total` - Total HTTP requests by method, path, status
- `http_request_duration_seconds` - Request latency histogram
- `http_requests_in_progress` - Current active requests

### Database Metrics
- `db_query_duration_seconds` - Database query latency
- `db_connections_active` - Active database connections
- `db_connections_idle` - Idle database connections

### Rate Limiting Metrics
- `http_requests_total{status="429"}` - Rate-limited requests
- `X-RateLimit-Remaining` - Available rate limit budget

### Custom Business Metrics
- Authentication success/failure rates
- Endpoint usage patterns
- Error rates by endpoint

## Alerting Rules

### Critical Alerts (PagerDuty/Email)

| Alert | Condition | Threshold |
|-------|-----------|-----------|
| **APIDown** | Service unreachable | 1 minute down |
| **CriticalErrorRate** | 5xx errors | >10% for 2 minutes |
| **VeryHighLatency** | p95 latency | >3s for 2 minutes |
| **PossibleDDoSAttack** | Rate limit hits | >100 req/s for 2 minutes |
| **PossibleBruteForceAttack** | Auth failures | >5 failures/s for 3 minutes |

### Warning Alerts (Slack/Email)

| Alert | Condition | Threshold |
|-------|-----------|-----------|
| **HighErrorRate** | 5xx errors | >5% for 5 minutes |
| **HighLatency** | p95 latency | >1s for 5 minutes |
| **SlowDatabaseQueries** | p95 query time | >0.5s for 5 minutes |
| **HighRateLimitHitRate** | Rate limiting | >10 req/s for 5 minutes |
| **HighAuthenticationFailureRate** | Failed logins | >20% for 5 minutes |

### Info Alerts (Monitoring Dashboard)

| Alert | Condition | Threshold |
|-------|-----------|-----------|
| **NoRecentActivity** | Zero requests | 15 minutes |
| **UnusualTrafficPattern** | Traffic spike | 2x normal for 10 minutes |

## Dashboards

### API Overview Dashboard
**File**: `monitoring/grafana/dashboards/api_overview.json`

**Panels**:
1. **Request Rate** - Requests/second by endpoint
2. **Error Rate** - 4xx and 5xx errors over time
3. **Response Time (p95)** - Latency percentiles
4. **Rate Limiting** - 429 responses
5. **Active Requests** - Current in-flight requests
6. **Total Requests** - 5-minute request volume
7. **Error Rate %** - Error percentage with color thresholds
8. **API Uptime** - Service health status
9. **Requests by Endpoint** - Table view of endpoint traffic
10. **Status Code Distribution** - Pie chart of response codes
11. **Database Query Duration** - Database performance
12. **Authentication Failures** - Security monitoring

## Configuration

### Prometheus Configuration
**File**: `monitoring/prometheus/prometheus.yml`

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'gardening-api'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['api:8080']
```

### Alert Rules
**File**: `monitoring/prometheus/alerts/api_alerts.yml`

Organized by category:
- `api_availability` - Service health
- `api_performance` - Latency and performance
- `rate_limiting` - Rate limit monitoring
- `business_metrics` - Traffic patterns
- `authentication` - Security monitoring

## Production Deployment

### 1. Change Default Credentials

Edit `docker-compose.yml`:
```yaml
environment:
  - GF_SECURITY_ADMIN_PASSWORD=<strong-password>
```

### 2. Enable Alertmanager

Uncomment in `prometheus.yml`:
```yaml
alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - alertmanager:9093
```

Create `docker-compose.override.yml`:
```yaml
services:
  alertmanager:
    image: prom/alertmanager:latest
    ports:
      - "9093:9093"
    volumes:
      - ./monitoring/alertmanager:/etc/alertmanager
    command:
      - '--config.file=/etc/alertmanager/config.yml'
```

### 3. Configure Alert Routing

Create `monitoring/alertmanager/config.yml`:
```yaml
route:
  receiver: 'default'
  group_by: ['alertname', 'severity']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 12h
  routes:
    - match:
        severity: critical
      receiver: 'pagerduty'
    - match:
        severity: warning
      receiver: 'slack'

receivers:
  - name: 'default'
    email_configs:
      - to: 'team@example.com'

  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: '<pagerduty-key>'

  - name: 'slack'
    slack_configs:
      - api_url: '<slack-webhook-url>'
        channel: '#alerts'
```

### 4. Enable HTTPS

Use a reverse proxy (nginx/Traefik) with Let's Encrypt:
```yaml
services:
  grafana:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.grafana.rule=Host(`grafana.example.com`)"
      - "traefik.http.routers.grafana.tls=true"
      - "traefik.http.routers.grafana.tls.certresolver=letsencrypt"
```

### 5. Persistent Storage

Volumes are already configured in `docker-compose.yml`:
- `prometheus-data` - 30 days of metrics
- `grafana-data` - Dashboard configurations

Backup these volumes regularly:
```bash
docker run --rm -v prometheus-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/prometheus-backup.tar.gz -C /data .
```

## Maintenance

### View Prometheus Targets
http://localhost:9090/targets

Verify all targets are `UP`:
- prometheus (self-monitoring)
- gardening-api

### Check Alert Rules
http://localhost:9090/alerts

View active alerts and their status.

### Query Metrics
http://localhost:9090/graph

Example queries:
```promql
# Request rate
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m])

# p95 latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Rate limited requests
rate(http_requests_total{status="429"}[5m])
```

### Reload Configuration
```bash
# Reload Prometheus config without downtime
curl -X POST http://localhost:9090/-/reload

# Restart services
docker-compose restart prometheus grafana
```

## Troubleshooting

### Prometheus Not Scraping
1. Check targets: http://localhost:9090/targets
2. Verify API is accessible: `curl http://api:8080/metrics`
3. Check Prometheus logs: `docker-compose logs prometheus`

### Grafana Shows No Data
1. Verify Prometheus datasource: Configuration → Data Sources
2. Test connection in datasource settings
3. Check dashboard time range (default: last 1 hour)
4. Verify metrics exist: http://localhost:9090/graph

### Alerts Not Firing
1. Check alert rules: http://localhost:9090/alerts
2. Verify evaluation interval in `prometheus.yml`
3. Check alert conditions match actual metrics
4. Review Prometheus logs for evaluation errors

## Monitoring Best Practices

### 1. Set Up Baselines
- Run load tests to establish normal traffic patterns
- Document expected latency ranges
- Define acceptable error rates

### 2. Create Runbooks
- Document response procedures for each alert
- Include troubleshooting steps
- Link to relevant documentation

### 3. Regular Review
- Weekly: Review dashboards for trends
- Monthly: Adjust alert thresholds based on patterns
- Quarterly: Archive old metrics, update retention policy

### 4. Continuous Improvement
- Add custom metrics for business logic
- Create dashboards for specific use cases
- Refine alerts to reduce false positives

## Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [PromQL Query Language](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Grafana Dashboard Best Practices](https://grafana.com/docs/grafana/latest/best-practices/best-practices-for-creating-dashboards/)

## Support

For issues or questions:
1. Check logs: `docker-compose logs prometheus grafana`
2. Review configuration files
3. Consult Prometheus/Grafana documentation
4. Open an issue in the project repository
