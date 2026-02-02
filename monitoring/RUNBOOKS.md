# Alert Runbooks

Response procedures for Prometheus alerts in the Gardening Service.

## Table of Contents
- [Critical Alerts](#critical-alerts)
- [Warning Alerts](#warning-alerts)
- [Info Alerts](#info-alerts)

---

## Critical Alerts

### APIDown

**Severity**: Critical
**Description**: The Gardening Service API is unreachable.

**Impact**:
- All API endpoints unavailable
- Users cannot access the application
- Data operations blocked

**Response Steps**:
1. **Verify the alert**:
   ```bash
   curl http://api:8080/health
   # If fails, check:
   docker-compose ps api
   ```

2. **Check logs**:
   ```bash
   docker-compose logs --tail=100 api
   ```

3. **Common causes**:
   - Database connection failure → Check `docker-compose ps db`
   - Application crash → Review logs for stack traces
   - Port conflict → Check if port 8080 is in use
   - Out of memory → Check container resources

4. **Immediate mitigation**:
   ```bash
   # Restart API service
   docker-compose restart api

   # If database issue
   docker-compose restart db api
   ```

5. **Escalation**: If restart doesn't resolve within 5 minutes, page on-call engineer.

**Prevention**:
- Monitor resource usage trends
- Set up health checks in load balancer
- Implement automatic restart policies

---

### CriticalErrorRate

**Severity**: Critical
**Description**: API error rate exceeds 10% over 2 minutes.

**Impact**:
- Degraded user experience
- Potential data integrity issues
- Risk of cascading failures

**Response Steps**:
1. **Identify error patterns**:
   ```bash
   # View Grafana dashboard for error breakdown by endpoint
   # Or query Prometheus:
   rate(http_requests_total{status=~"5.."}[5m])
   ```

2. **Check recent deployments**:
   ```bash
   git log --oneline -5
   # If recent deploy, consider rollback
   ```

3. **Review logs for errors**:
   ```bash
   docker-compose logs --tail=200 api | grep -i error
   ```

4. **Common causes**:
   - Database connection pool exhausted
   - External API dependency down
   - Recent code deployment bug
   - Database migration issue

5. **Immediate mitigation**:
   - If recent deployment: Rollback
   - If database issue: Restart database
   - If external dependency: Implement circuit breaker

6. **Escalation**: Page on-call if error rate doesn't drop within 5 minutes.

---

### VeryHighLatency

**Severity**: Critical
**Description**: p95 latency exceeds 3 seconds for 2 minutes.

**Impact**:
- Poor user experience
- Timeout errors
- Potential request queueing

**Response Steps**:
1. **Check current latency**:
   ```promql
   histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
   ```

2. **Identify slow endpoints**:
   - Review Grafana dashboard "Response Time" panel
   - Check database query duration

3. **Check database performance**:
   ```bash
   docker-compose exec db psql -U gardener -d gardening_db -c \
     "SELECT pid, now() - query_start AS duration, query \
      FROM pg_stat_activity \
      WHERE state = 'active' ORDER BY duration DESC LIMIT 10;"
   ```

4. **Common causes**:
   - Slow database queries → Check query plans
   - High load → Check request rate
   - Resource constraints → Check CPU/memory
   - Lock contention → Check database locks

5. **Immediate mitigation**:
   - Kill slow queries if necessary
   - Scale horizontally if traffic spike
   - Add database indexes if missing
   - Implement caching for slow endpoints

---

### PossibleDDoSAttack

**Severity**: Critical
**Description**: Very high rate of rate-limited requests (>100 req/s).

**Impact**:
- Service degradation for legitimate users
- Resource exhaustion risk
- Potential security breach

**Response Steps**:
1. **Verify attack pattern**:
   ```promql
   rate(http_requests_total{status="429"}[1m])
   ```

2. **Identify source IPs**:
   ```bash
   docker-compose logs api | grep "429" | tail -100
   ```

3. **Check for patterns**:
   - Single IP or distributed?
   - Specific endpoint targeted?
   - Time of day correlation?

4. **Immediate mitigation**:
   - Lower rate limits temporarily
   - Block offending IPs at firewall/load balancer
   - Enable CAPTCHA for affected endpoints
   - Contact hosting provider if distributed

5. **Escalation**:
   - Notify security team immediately
   - Consider enabling DDoS protection (Cloudflare, AWS Shield)
   - Document attack for postmortem

**Prevention**:
- Implement CAPTCHA on sensitive endpoints
- Use CDN with DDoS protection
- Set up IP-based blocking automation

---

### PossibleBruteForceAttack

**Severity**: Critical
**Description**: High rate of authentication failures (>5 failures/second).

**Impact**:
- Risk of account compromise
- Service degradation
- Security breach

**Response Steps**:
1. **Verify attack**:
   ```promql
   rate(http_requests_total{path="/token",status="401"}[1m])
   ```

2. **Identify targeted accounts**:
   ```bash
   docker-compose logs api | grep "401" | grep "/token" | tail -100
   ```

3. **Check for patterns**:
   - Single account or multiple?
   - Source IPs?
   - Credential stuffing or brute force?

4. **Immediate mitigation**:
   - Temporarily lock targeted accounts
   - Lower auth endpoint rate limit (already at 5/min)
   - Block offending IPs
   - Enable 2FA if not already enabled

5. **User notification**:
   - Email affected users about suspicious activity
   - Force password reset if breach suspected

6. **Escalation**:
   - Notify security team immediately
   - Consider temporary auth endpoint disable
   - Report to authorities if criminal activity

**Prevention**:
- Implement account lockout after N failures
- Require strong passwords
- Enable 2FA for all accounts
- Monitor for leaked credentials

---

## Warning Alerts

### HighErrorRate

**Severity**: Warning
**Description**: API error rate exceeds 5% over 5 minutes.

**Response Steps**:
1. **Monitor trend**: Check if increasing toward critical threshold
2. **Identify root cause**: Review logs and error patterns
3. **Communicate**: Alert team in Slack
4. **Prepare**: Have rollback plan ready if approaching critical

**Common causes**:
- Partial service degradation
- Specific endpoint issues
- Data validation failures

---

### HighLatency

**Severity**: Warning
**Description**: p95 latency exceeds 1 second for 5 minutes.

**Response Steps**:
1. **Monitor trend**: Check if increasing
2. **Identify slow endpoints**: Review dashboard
3. **Check load**: Verify request rate is normal
4. **Optimize**: Add caching or optimize queries if pattern persists

**Common causes**:
- Database query performance
- External API latency
- Resource constraints
- Missing database indexes

---

### SlowDatabaseQueries

**Severity**: Warning
**Description**: p95 database query time exceeds 0.5 seconds.

**Response Steps**:
1. **Identify slow queries**:
   ```sql
   SELECT query, mean_exec_time, calls
   FROM pg_stat_statements
   ORDER BY mean_exec_time DESC LIMIT 10;
   ```

2. **Check for missing indexes**:
   ```sql
   SELECT schemaname, tablename, indexname
   FROM pg_indexes
   WHERE schemaname = 'public';
   ```

3. **Analyze query plans**: Use EXPLAIN ANALYZE on slow queries

4. **Mitigation**:
   - Add missing indexes
   - Optimize query structure
   - Implement query result caching
   - Consider database connection pooling tuning

---

### HighRateLimitHitRate

**Severity**: Warning
**Description**: Rate limiting blocking >10 requests/second.

**Response Steps**:
1. **Verify if legitimate traffic**:
   - Check request patterns
   - Review source IPs
   - Identify affected endpoints

2. **If legitimate**:
   - Consider increasing rate limits
   - Implement tiered rate limiting
   - Contact high-volume users

3. **If malicious**:
   - Monitor for escalation to DDoS
   - Consider IP blocking
   - Review security measures

---

### HighAuthenticationFailureRate

**Severity**: Warning
**Description**: Authentication failure rate exceeds 20%.

**Response Steps**:
1. **Determine if attack or user error**:
   - Check if widespread or specific accounts
   - Review IP patterns
   - Check for recent password policy changes

2. **If user error**:
   - Improve error messages
   - Add "forgot password" visibility
   - Check for UI issues

3. **If attack**:
   - Monitor for escalation
   - Prepare for brute force response
   - Consider additional security measures

---

## Info Alerts

### NoRecentActivity

**Severity**: Info
**Description**: No HTTP requests received in 15 minutes.

**Response Steps**:
1. **Verify if expected** (e.g., scheduled maintenance)
2. **Check external access**:
   ```bash
   curl http://api:8080/health
   ```
3. **Review load balancer/proxy logs**
4. **Check DNS resolution**

**Common causes**:
- Scheduled maintenance
- Load balancer configuration issue
- DNS propagation delay
- Network connectivity problem

---

### UnusualTrafficPattern

**Severity**: Info
**Description**: Request rate is 2x higher than 1-hour average.

**Response Steps**:
1. **Verify if expected** (marketing campaign, viral content, etc.)
2. **Monitor resource usage**
3. **Check for traffic quality** (bots vs. humans)
4. **Prepare for scaling** if sustained

**Common causes**:
- Legitimate traffic spike
- Marketing campaign
- Viral social media post
- Bot traffic
- DDoS attack beginning

---

## General Response Protocol

### 1. Acknowledge
- Acknowledge alert within 5 minutes
- Update incident channel

### 2. Assess
- Determine severity and impact
- Identify affected users/systems

### 3. Mitigate
- Apply immediate fixes
- Restore service if down

### 4. Communicate
- Update status page
- Notify affected users
- Keep team informed

### 5. Resolve
- Fix root cause
- Verify resolution
- Close incident

### 6. Learn
- Write postmortem
- Update runbooks
- Implement prevention

## Contact Information

- **On-call Engineer**: PagerDuty
- **Security Team**: security@example.com
- **Database Admin**: dba@example.com
- **DevOps Team**: #devops Slack channel

## Related Documentation

- [Monitoring Setup](./README.md)
- [Production Deployment Guide](../docs/deployment.md)
- [Security Incident Response](../docs/security.md)
