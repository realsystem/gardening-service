# Production Metrics Documentation

## Overview

This document describes all production metrics collected by the Gardening Helper Service, their meanings, and recommended alert thresholds.

All metrics are exposed at the `/metrics` endpoint in Prometheus text format for scraping.

## Metrics Collection Strategy

- **Minimal Performance Impact**: Metrics use efficient Prometheus counters and histograms
- **No Blocking Operations**: All metric collection is non-blocking
- **Memory Efficient**: Uses histogram buckets instead of storing all values
- **Security**: No sensitive data (passwords, tokens, plant names) is included in metrics

## HTTP Request Metrics

### `http_requests_total`

**Type**: Counter
**Labels**: `method`, `endpoint`, `status_code`
**Description**: Total number of HTTP requests received by the service.

**Example**:
```
http_requests_total{method="GET",endpoint="/gardens",status_code="200"} 1523
http_requests_total{method="POST",endpoint="/planting-events",status_code="403"} 12
```

**Use Cases**:
- Track request volume by endpoint
- Monitor HTTP status code distribution
- Identify popular endpoints

**Alert Thresholds**:
- **High 5xx Rate**: `rate(http_requests_total{status_code=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05` (5% error rate)
- **High 4xx Rate**: `rate(http_requests_total{status_code=~"4.."}[5m]) / rate(http_requests_total[5m]) > 0.20` (20% client error rate)

---

### `http_request_duration_seconds`

**Type**: Histogram
**Labels**: `method`, `endpoint`
**Buckets**: `[0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0]`
**Description**: HTTP request latency in seconds.

**Quantiles**:
- `p50`: Median response time
- `p95`: 95th percentile (most users experience this or better)
- `p99`: 99th percentile (worst case for most requests)

**Example Queries**:
```promql
# p95 latency for all requests
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))

# p99 latency by endpoint
histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (endpoint, le))
```

**Alert Thresholds**:
- **High p95 Latency**: `histogram_quantile(0.95, ...) > 1.0` (p95 > 1 second)
- **High p99 Latency**: `histogram_quantile(0.99, ...) > 5.0` (p99 > 5 seconds)

---

### `http_requests_in_progress`

**Type**: Gauge
**Labels**: `method`, `endpoint`
**Description**: Number of HTTP requests currently being processed (concurrent requests).

**Use Cases**:
- Monitor concurrent load
- Detect resource exhaustion
- Capacity planning

**Alert Thresholds**:
- **High Concurrency**: `http_requests_in_progress > 100` (more than 100 concurrent requests)

---

### `http_errors_total`

**Type**: Counter
**Labels**: `method`, `endpoint`, `error_type`
**Description**: Total HTTP errors (4xx and 5xx responses).

**Error Types**:
- `client_error`: 4xx status codes
- `server_error`: 5xx status codes

**Alert Thresholds**:
- **High Server Errors**: `rate(http_errors_total{error_type="server_error"}[5m]) > 1` (more than 1 error/sec)

## Rule Engine Metrics

### `rule_evaluations_total`

**Type**: Counter
**Labels**: `rule_id`, `triggered`
**Description**: Total number of rule evaluations performed.

**Example**:
```
rule_evaluations_total{rule_id="Harvest Task Generator",triggered="True"} 523
rule_evaluations_total{rule_id="Watering Task Generator",triggered="False"} 89
```

**Use Cases**:
- Track rule execution frequency
- Monitor rule triggering rate
- Identify frequently triggered rules

**Alert Thresholds**:
- **Low Trigger Rate**: `rate(rule_evaluations_total{triggered="True"}[1h]) < 0.1` (rules rarely triggering - possible bug)

---

### `rule_execution_duration_seconds`

**Type**: Histogram
**Labels**: `rule_id`
**Buckets**: `[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]`
**Description**: Rule execution time in seconds.

**Use Cases**:
- Identify slow rules
- Optimize rule performance
- Detect performance regressions

**Example Query**:
```promql
# p95 rule execution time
histogram_quantile(0.95, sum(rate(rule_execution_duration_seconds_bucket[5m])) by (rule_id, le))
```

**Alert Thresholds**:
- **Slow Rule**: `histogram_quantile(0.95, rate(rule_execution_duration_seconds_bucket[5m])) > 0.1` (p95 > 100ms)

---

### `rule_engine_batch_duration_seconds`

**Type**: Histogram
**Buckets**: `[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]`
**Description**: Total time to execute all rules for a single context (batch execution).

**Alert Thresholds**:
- **Slow Batch**: `histogram_quantile(0.95, ...) > 1.0` (batch taking > 1 second)

---

### `rules_triggered_total`

**Type**: Counter
**Labels**: `rule_id`, `severity`
**Description**: Total number of rules that triggered (resulted in task/alert).

**Severity Levels**:
- `info`: Informational triggers
- `warning`: Warning-level triggers
- `critical`: Critical triggers

**Use Cases**:
- Track actionable rule results
- Monitor system health through rule triggers

## Compliance Metrics

### `compliance_checks_total`

**Type**: Counter
**Labels**: `check_type`, `result`
**Description**: Total compliance checks performed.

**Check Types**:
- `plant_restriction`: Plant name restriction checks

**Results**:
- `allowed`: Check passed, request allowed
- `blocked`: Check failed, request blocked

**Example**:
```
compliance_checks_total{check_type="plant_restriction",result="allowed"} 9823
compliance_checks_total{check_type="plant_restriction",result="blocked"} 47
```

**Use Cases**:
- Monitor compliance enforcement activity
- Track block rate
- Identify compliance check volume

---

### `compliance_violations_total`

**Type**: Counter
**Labels**: `violation_type`, `endpoint`
**Description**: Total compliance violations detected.

**Violation Types**:
- `restricted_term_in_common_name`: Restricted plant name in common_name field
- `restricted_term_in_scientific_name`: Restricted plant name in scientific_name field
- `restricted_term_in_notes`: Restricted plant name in notes field
- `restricted_term_in_species`: Restricted plant name in species field
- `parameter_only_optimization_attempt`: Suspicious optimization attempt

**Example**:
```
compliance_violations_total{violation_type="restricted_term_in_common_name",endpoint="/planting-events"} 23
```

**Use Cases**:
- Track violation patterns
- Identify attack vectors
- Monitor evasion attempts

**Alert Thresholds**:
- **High Violation Rate**: `rate(compliance_violations_total[5m]) > 5` (more than 5 violations/min)
- **Spike in Violations**: `rate(compliance_violations_total[5m]) > 4 * avg_over_time(rate(compliance_violations_total[1h])[1d:1h])` (4x above historical average)

---

### `compliance_users_flagged_total`

**Type**: Counter
**Description**: Total number of users flagged for compliance violations.

**Use Cases**:
- Monitor user flagging rate
- Track compliance enforcement
- Identify repeat offenders (via logs)

**Alert Thresholds**:
- **High Flagging Rate**: `rate(compliance_users_flagged_total[1h]) > 10` (more than 10 users flagged per hour)

---

### `compliance_blocks_total`

**Type**: Counter
**Labels**: `endpoint`
**Description**: Total requests blocked by compliance (403 Forbidden responses).

**Example**:
```
compliance_blocks_total{endpoint="/planting-events"} 34
compliance_blocks_total{endpoint="/plant-varieties"} 12
```

**Use Cases**:
- Track enforcement effectiveness
- Identify targeted endpoints
- Monitor block distribution

**Alert Thresholds**:
- **High Block Rate**: `rate(compliance_blocks_total[5m]) > 2` (more than 2 blocks/min)

## Database Metrics

### `db_queries_total`

**Type**: Counter
**Labels**: `operation`
**Description**: Total database queries executed.

**Operations**:
- `SELECT`: Read queries
- `INSERT`: Insert queries
- `UPDATE`: Update queries
- `DELETE`: Delete queries

**Use Cases**:
- Monitor database load
- Track query patterns
- Identify heavy read/write operations

---

### `db_query_duration_seconds`

**Type**: Histogram
**Labels**: `operation`
**Buckets**: `[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]`
**Description**: Database query execution time in seconds.

**Alert Thresholds**:
- **Slow Queries**: `histogram_quantile(0.95, ...) > 0.5` (p95 query time > 500ms)

## Authentication Metrics

### `auth_attempts_total`

**Type**: Counter
**Labels**: `result`
**Description**: Total authentication attempts.

**Results**:
- `success`: Authentication succeeded
- `failure`: Authentication failed

**Use Cases**:
- Monitor login activity
- Detect brute force attacks
- Track authentication success rate

**Alert Thresholds**:
- **High Failure Rate**: `rate(auth_attempts_total{result="failure"}[5m]) / rate(auth_attempts_total[5m]) > 0.30` (30% failure rate)
- **Brute Force**: `rate(auth_attempts_total{result="failure"}[1m]) > 10` (more than 10 failures/min)

---

### `token_validations_total`

**Type**: Counter
**Labels**: `result`
**Description**: Total token validations performed.

**Results**:
- `valid`: Token is valid
- `invalid`: Token is malformed or invalid
- `expired`: Token has expired

**Use Cases**:
- Monitor token validation patterns
- Track token expiration rates
- Identify token issues

**Alert Thresholds**:
- **High Invalid Rate**: `rate(token_validations_total{result="invalid"}[5m]) > 1` (more than 1 invalid token/sec)

## Prometheus Configuration Example

```yaml
scrape_configs:
  - job_name: 'gardening-service'
    scrape_interval: 15s
    scrape_timeout: 10s
    metrics_path: /metrics
    static_configs:
      - targets: ['localhost:8000']
```

## Grafana Dashboard Queries

### Request Rate (requests/sec)
```promql
rate(http_requests_total[5m])
```

### Error Rate (%)
```promql
100 * (
  rate(http_requests_total{status_code=~"5.."}[5m])
  /
  rate(http_requests_total[5m])
)
```

### p95 Latency
```promql
histogram_quantile(0.95,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (endpoint, le)
)
```

### Compliance Violation Rate
```promql
rate(compliance_violations_total[5m])
```

### Rule Engine Performance
```promql
histogram_quantile(0.95,
  sum(rate(rule_engine_batch_duration_seconds_bucket[5m])) by (le)
)
```

## Performance Impact

Metrics collection is designed for minimal performance impact:

- **Request Overhead**: < 1ms per request
- **Rule Evaluation Overhead**: < 0.1ms per rule
- **Memory Usage**: ~1MB for metric storage (histograms with predefined buckets)
- **CPU Impact**: < 1% CPU overhead under normal load

## Security Considerations

Metrics do NOT contain:
- ❌ Passwords or tokens
- ❌ Email addresses
- ❌ Plant names or scientific names
- ❌ User-generated content
- ❌ API keys or secrets

Metrics DO contain:
- ✅ HTTP methods and status codes
- ✅ Endpoint paths (without IDs)
- ✅ Timing information
- ✅ Count aggregates
- ✅ Rule identifiers
- ✅ Violation types (generic codes)

## Recommended Alerts

### Critical Alerts (PagerDuty)

1. **High 5xx Rate**: Server errors affecting > 5% of requests
2. **High p99 Latency**: Response time > 5 seconds for 99th percentile
3. **High Concurrency**: More than 100 concurrent requests (resource exhaustion risk)

### Warning Alerts (Slack)

1. **High 4xx Rate**: Client errors > 20% (possible API misuse)
2. **High Violation Spike**: 4x above historical average (possible attack)
3. **Slow Rules**: Rule execution p95 > 100ms (performance issue)
4. **High Flagging Rate**: More than 10 users flagged/hour (compliance activity)

### Info Alerts (Dashboard Only)

1. **Authentication Patterns**: Track login success/failure rates
2. **Endpoint Popularity**: Identify most-used endpoints
3. **Rule Trigger Distribution**: Monitor which rules trigger most

## Monitoring Tools Integration

### Prometheus
- Scrape `/metrics` endpoint every 15 seconds
- Store metrics for 15 days
- Use recording rules for complex queries

### Grafana
- Import dashboard from `grafana-dashboard.json` (to be created)
- Set up alert notifications to Slack/PagerDuty
- Create panels for key metrics

### DataDog (Optional)
- Use Prometheus integration to import metrics
- Create custom dashboards
- Set up anomaly detection

## Troubleshooting

### Metric Not Appearing
1. Check that the code path is being executed
2. Verify labels match exactly (case-sensitive)
3. Check `/metrics` endpoint directly in browser

### High Cardinality Warning
- Avoid using user IDs or unique identifiers as labels
- Use endpoint patterns (e.g., `/users/{id}`) instead of full paths
- Limit label values to predefined sets

### Performance Issues
- Reduce scrape frequency if metrics endpoint is slow
- Check histogram bucket configuration
- Consider sampling for very high-volume metrics

## Future Enhancements (v2)

Planned improvements:
1. **Custom Business Metrics**: Track garden creation rate, harvest frequency, etc.
2. **SLI/SLO Tracking**: Define and track Service Level Indicators
3. **Trace Integration**: Connect metrics with distributed tracing
4. **Cost Metrics**: Track database query costs, API usage costs
5. **User Journey Metrics**: Track user flows through the application
