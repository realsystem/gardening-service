# Grafana Dashboards Guide

## 🎯 Quick Access

Open Grafana: **http://localhost:3001**
- Login: `admin` / `admin`

---

## 📊 Available Dashboards (4 Total)

### 1. **API Overview** - Main Dashboard
**URL**: http://localhost:3001/d/gardening-api-overview

**Purpose**: High-level overview of API health and performance

**Panels** (12 total):
1. **Request Rate** - Requests/second by endpoint (line graph)
2. **Error Rate** - 4xx and 5xx errors over time
3. **Response Time (p95)** - 95th percentile latency
4. **Rate Limiting** - 429 responses tracking
5. **Active Requests** - Current in-flight requests
6. **Total Requests** - 5-minute request volume
7. **Error Rate %** - Error percentage with color thresholds
8. **API Uptime** - Service health (UP/DOWN)
9. **Requests by Endpoint** - Table showing traffic per endpoint
10. **Status Code Distribution** - Pie chart of HTTP status codes
11. **Database Query Duration** - p95 database performance
12. **Authentication Failures** - Failed login attempts

**Best for**:
- Quick health checks
- Daily monitoring
- Spotting immediate issues

---

### 2. **Performance Detailed** - Deep Dive
**URL**: http://localhost:3001/d/performance-detailed

**Purpose**: Detailed performance analysis and optimization

**Panels** (10 total):
1. **Request Rate by Endpoint** - Traffic breakdown per endpoint
2. **Response Time Distribution** - p99, p95, p50 latencies
3. **Slowest Endpoints** - Table of endpoints with highest avg latency
4. **Request Duration Heatmap** - Visual distribution of response times
5. **Database Query Performance** - p95 query time + queries/sec
6. **Database Connections** - Active vs idle connections
7. **Throughput** - Requests per minute (single stat)
8. **Avg Response Time** - Overall average latency
9. **Active Requests** - Current concurrent requests
10. **Cache Hit Rate** - Cache effectiveness (if available)

**Best for**:
- Performance optimization
- Identifying slow endpoints
- Database performance tuning
- Capacity planning

---

### 3. **Security Monitoring** - Security Dashboard
**URL**: http://localhost:3001/d/security-monitoring

**Purpose**: Track security events and authentication

**Panels** (10 total):
1. **Authentication Success Rate** - Successful vs failed logins
2. **Rate Limited Requests** - Requests blocked by rate limiting
3. **Failed Authentication by IP** - Top IPs with failed logins
4. **Rate Limited IPs** - Top IPs hitting rate limits
5. **HTTP Status Codes Over Time** - Status code trends (stacked)
6. **Security Events Timeline** - 401, 403, 429 events
7. **Total Failed Logins (1h)** - Count with color thresholds
8. **Rate Limited Requests (1h)** - Total rate-limited requests
9. **Auth Failure Rate %** - Percentage of failed authentications
10. **Unique IPs (1h)** - Number of unique client IPs

**Best for**:
- Detecting brute force attacks
- Monitoring rate limiting effectiveness
- Identifying suspicious IPs
- Security auditing

**Alert Thresholds**:
- 🟢 Green: Normal activity
- 🟡 Yellow: Elevated activity (monitor)
- 🔴 Red: Critical (investigate immediately)

---

### 4. **Error Tracking** - Debugging Dashboard
**URL**: http://localhost:3001/d/error-tracking

**Purpose**: Track and debug errors

**Panels** (11 total):
1. **Error Rate by Status Code** - Errors broken down by HTTP status
2. **Error Rate % (5xx)** - Server error percentage
3. **Errors by Endpoint** - Table of endpoints with most errors
4. **Error Distribution** - Pie chart of error types
5. **500 Internal Server Errors** - Server errors by endpoint
6. **404 Not Found** - Missing endpoints/resources
7. **Request Success Rate** - Gauge showing % of successful requests
8. **Total 5xx Errors (1h)** - Server error count
9. **Total 4xx Errors (1h)** - Client error count
10. **Error Spike Detector** - Detects sudden error rate increases
11. **Most Common Error Paths** - Bar chart of error-prone endpoints

**Best for**:
- Debugging production issues
- Tracking error patterns
- Finding broken endpoints
- Incident response

---

## 🔍 How to Use the Dashboards

### Navigation
1. **Access Grafana**: Open http://localhost:3001
2. **Login**: admin / admin
3. **Find Dashboards**:
   - Click hamburger menu (☰) → "Dashboards"
   - Or use the search bar at top
   - All dashboards are in the root folder

### Time Range Selection
- Default: Last 1 hour
- Change: Click time range in top-right corner
- Options: Last 5m, 15m, 1h, 6h, 24h, 7d, or custom

### Refresh Rate
- Auto-refresh: 10-30 seconds (varies by dashboard)
- Manual refresh: Click refresh icon (🔄)
- Change refresh rate: Dropdown next to refresh icon

### Panel Interaction
- **Zoom**: Click and drag on graph
- **Legend**: Click series name to toggle visibility
- **Details**: Hover over graph for detailed values
- **Full Screen**: Click panel title → View
- **Edit**: Click panel title → Edit (advanced)

---

## 📈 What to Look For

### Healthy Metrics
✅ **Request Rate**: Steady or gradually increasing
✅ **Error Rate**: <1% (mostly 4xx, minimal 5xx)
✅ **Latency**: p95 <500ms, p99 <1s
✅ **Success Rate**: >99%
✅ **Rate Limiting**: Minimal 429s (only for abuse)
✅ **Auth Failures**: <10% failure rate

### Warning Signs
⚠️ **Request Rate**: Sudden spikes or drops
⚠️ **Error Rate**: 1-5% errors
⚠️ **Latency**: p95 >1s, p99 >3s
⚠️ **Success Rate**: 95-99%
⚠️ **Rate Limiting**: Increased 429s
⚠️ **Auth Failures**: 10-20% failure rate

### Critical Issues
🚨 **Request Rate**: Zero requests or extreme spike
🚨 **Error Rate**: >5% errors
🚨 **Latency**: p95 >3s, p99 >10s
🚨 **Success Rate**: <95%
🚨 **Rate Limiting**: Massive 429s (potential DDoS)
🚨 **Auth Failures**: >20% or high volume (brute force)

---

## 🎨 Dashboard Customization

### Create Your Own Panel
1. Click "+ Add panel" in any dashboard
2. Choose visualization type (graph, table, stat, etc.)
3. Write PromQL query (see examples below)
4. Configure display options
5. Save dashboard

### Example PromQL Queries

```promql
# Total requests per second
rate(http_requests_total[5m])

# Error rate percentage
(sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))) * 100

# p95 latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Requests by endpoint
sum by (path) (rate(http_requests_total[5m]))

# Top 10 slowest endpoints
topk(10, avg by (path) (rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])))

# Rate limited requests
rate(http_requests_total{status="429"}[5m])

# Failed authentication rate
rate(http_requests_total{path="/token",status="401"}[5m])

# Active database connections
db_connections_active

# Database query p95 latency
histogram_quantile(0.95, rate(db_query_duration_seconds_bucket[5m]))
```

---

## 🔔 Setting Up Alerts (Optional)

### Enable Email Alerts
1. Go to Configuration → Alert Notification Channels
2. Click "New channel"
3. Choose type: Email, Slack, PagerDuty, etc.
4. Configure settings
5. Test notification

### Alert Rules Already Configured
- High Error Rate (>5%)
- High Rate Limit Activity (>10 req/s)

### Add Custom Alerts
1. Edit any panel
2. Click "Alert" tab
3. Configure conditions
4. Set notification channel
5. Save

---

## 🎯 Dashboard Scenarios

### Scenario 1: "Is the API healthy?"
→ **Dashboard**: API Overview
- Check "API Uptime" panel (should be green/UP)
- Check "Error Rate %" (should be <1%)
- Check "Response Time" (p95 should be <500ms)

### Scenario 2: "Why is the API slow?"
→ **Dashboard**: Performance Detailed
- Check "Slowest Endpoints" table
- Look at "Request Duration Heatmap"
- Check "Database Query Performance"
- Review "Database Connections"

### Scenario 3: "Are we under attack?"
→ **Dashboard**: Security Monitoring
- Check "Rate Limited Requests" (high = possible DDoS)
- Check "Failed Authentication by IP" (high = brute force)
- Check "Authentication Success Rate"
- Check "Security Events Timeline"

### Scenario 4: "What's causing errors?"
→ **Dashboard**: Error Tracking
- Check "Errors by Endpoint" table
- Look at "Error Distribution" pie chart
- Check "500 Internal Server Errors" graph
- Review "Most Common Error Paths"

### Scenario 5: "How much traffic are we getting?"
→ **Dashboard**: API Overview or Performance Detailed
- Check "Request Rate" graph
- Check "Throughput (Requests/min)" stat
- Review "Requests by Endpoint" table

---

## 🚀 Pro Tips

### Tip 1: Use Variables
Create dashboard variables for dynamic filtering:
- Environment (dev, staging, prod)
- Endpoint (specific path)
- Time range presets

### Tip 2: Create Playlists
Rotate between dashboards automatically:
1. Dashboards → Playlists → New
2. Add dashboards
3. Set rotation interval
4. Use for TV displays/monitoring walls

### Tip 3: Share Snapshots
1. Click "Share" icon on dashboard
2. Create snapshot
3. Set expiration
4. Share URL with team

### Tip 4: Export/Import
- **Export**: Dashboard settings → JSON Model → Copy
- **Import**: Create Dashboard → Import → Paste JSON

### Tip 5: Template Dashboards
Save dashboards as templates for reuse:
1. Configure perfect dashboard
2. Export JSON
3. Replace hard-coded values with variables
4. Import with new data source

---

## 📚 Related Resources

- [Prometheus Query Language](http://localhost:9090/graph) - Test queries
- [Monitoring README](./README.md) - Full monitoring setup guide
- [Alert Runbooks](./RUNBOOKS.md) - Incident response procedures
- [Grafana Docs](https://grafana.com/docs/) - Official documentation

---

## 🆘 Troubleshooting

### Dashboard shows "No Data"
**Fix**:
1. Check time range (try "Last 5 minutes")
2. Generate traffic: `curl http://localhost:8080/health`
3. Verify Prometheus is scraping: http://localhost:9090/targets
4. Check API is running: `docker-compose ps api`

### Panels are empty
**Fix**:
1. Check data source: Configuration → Data Sources
2. Test Prometheus connection
3. Verify metric names in queries
4. Check Prometheus has data: http://localhost:9090/graph

### Dashboard not appearing
**Fix**:
1. Restart Grafana: `docker-compose restart grafana`
2. Check file exists: `ls monitoring/grafana/dashboards/`
3. Verify provisioning: `docker-compose exec grafana ls /etc/grafana/provisioning/dashboards/`

### Metrics are delayed
**Normal behavior**: Metrics update every 15-30 seconds
- Prometheus scrapes every 15s
- Grafana refreshes based on dashboard setting
- Some queries use 5m averages (inherent delay)

---

**Happy Monitoring!** 📊

For questions or issues, consult the main [Monitoring README](./README.md).
