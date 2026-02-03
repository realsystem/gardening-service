# Feature Flags

## Overview

Feature flags allow runtime control of critical system features without requiring code deployment or service restart. This enables rapid incident response, gradual rollouts, and safe experimentation.

## Available Feature Flags

### `FEATURE_RULE_ENGINE_ENABLED`

**Default**: `True` (enabled)
**Controls**: Automatic task generation via rule engine
**Fail-Safe**: Enabled (tasks are generated)

**When Disabled**:
- Rule engine returns empty task lists
- No tasks are automatically created
- No errors or crashes
- Existing tasks remain unaffected
- Logs informational message

**Use Cases**:
- Disable during rule engine bugs
- Reduce load during high traffic
- Maintenance mode

**Example**:
```bash
# Disable rule engine
export FEATURE_RULE_ENGINE_ENABLED=false
```

---

### `FEATURE_COMPLIANCE_ENFORCEMENT_ENABLED`

**Default**: `True` (enabled)
**Controls**: Compliance violation blocking (403 responses)
**Fail-Safe**: Enabled (violations are blocked)

**When Disabled**:
- Violations are still detected and logged
- Users are still flagged for violations
- Metrics are still tracked
- **Requests are NOT blocked** (no 403 errors)
- System operates in "log-only" mode

**Use Cases**:
- Emergency disable during compliance service issues
- Allow legitimate requests during false positive spikes
- Testing compliance detection without blocking
- Graceful degradation during incidents

**Security Note**:
Disabling enforcement does not disable detection. All violations are logged and users are flagged for later review.

**Example**:
```bash
# Disable enforcement (log-only mode)
export FEATURE_COMPLIANCE_ENFORCEMENT_ENABLED=false
```

---

### `FEATURE_OPTIMIZATION_ENGINES_ENABLED`

**Default**: `True` (enabled)
**Controls**: Optimization features (companion planting, nutrient optimization, shading analysis)
**Fail-Safe**: Enabled (optimizations available)

**When Disabled**:
- Optimization endpoints return empty results
- No computational load from analysis
- Graceful degradation with informative message
- No errors or crashes

**Use Cases**:
- Disable during optimization service issues
- Reduce computational load during high traffic
- Maintenance on optimization algorithms

**Example**:
```bash
# Disable optimization engines
export FEATURE_OPTIMIZATION_ENGINES_ENABLED=false
```

## Runtime Management

### Viewing Feature Flags

**Endpoint**: `GET /admin/feature-flags`
**Auth**: Admin only
**Response**:
```json
{
  "flags": {
    "FEATURE_RULE_ENGINE_ENABLED": true,
    "FEATURE_COMPLIANCE_ENFORCEMENT_ENABLED": true,
    "FEATURE_OPTIMIZATION_ENGINES_ENABLED": true
  },
  "last_reload": "2024-01-15T10:30:00Z",
  "definitions": {
    "FEATURE_RULE_ENGINE_ENABLED": {
      "default": true,
      "description": "Enable automatic task generation via rule engine",
      "fail_safe": true
    },
    ...
  }
}
```

### Reloading Feature Flags

**Endpoint**: `POST /admin/feature-flags/reload`
**Auth**: Admin only
**Response**:
```json
{
  "message": "Feature flags reloaded successfully",
  "flags": {
    "FEATURE_RULE_ENGINE_ENABLED": false,
    "FEATURE_COMPLIANCE_ENFORCEMENT_ENABLED": true,
    "FEATURE_OPTIMIZATION_ENGINES_ENABLED": true
  },
  "reloaded_by": "admin@example.com",
  "reloaded_at": "2024-01-15T10:35:00Z"
}
```

## Configuration

### Environment Variables

Feature flags are configured via environment variables:

```bash
# .env or .env.production
FEATURE_RULE_ENGINE_ENABLED=true
FEATURE_COMPLIANCE_ENFORCEMENT_ENABLED=true
FEATURE_OPTIMIZATION_ENGINES_ENABLED=true
```

### Docker Compose

```yaml
services:
  api:
    environment:
      - FEATURE_RULE_ENGINE_ENABLED=true
      - FEATURE_COMPLIANCE_ENFORCEMENT_ENABLED=true
      - FEATURE_OPTIMIZATION_ENGINES_ENABLED=true
```

### Kubernetes

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: feature-flags
data:
  FEATURE_RULE_ENGINE_ENABLED: "true"
  FEATURE_COMPLIANCE_ENFORCEMENT_ENABLED: "true"
  FEATURE_OPTIMIZATION_ENGINES_ENABLED: "true"
```

## Incident Response Workflow

### Scenario: Rule Engine Bug Causing Service Degradation

1. **Identify Issue**: Rule engine is creating malformed tasks
2. **Disable Feature**:
   ```bash
   # Update environment variable
   export FEATURE_RULE_ENGINE_ENABLED=false

   # Reload flags without restart
   curl -X POST https://api.example.com/admin/feature-flags/reload \
     -H "Authorization: Bearer $ADMIN_TOKEN"
   ```
3. **Verify**: Check that new tasks are no longer being created
4. **Fix**: Deploy bug fix for rule engine
5. **Re-enable**:
   ```bash
   export FEATURE_RULE_ENGINE_ENABLED=true
   curl -X POST https://api.example.com/admin/feature-flags/reload \
     -H "Authorization: Bearer $ADMIN_TOKEN"
   ```

### Scenario: False Positive Compliance Alerts

1. **Identify Issue**: Legitimate users being blocked by compliance
2. **Switch to Log-Only Mode**:
   ```bash
   # Disable enforcement but keep detection
   export FEATURE_COMPLIANCE_ENFORCEMENT_ENABLED=false
   curl -X POST https://api.example.com/admin/feature-flags/reload \
     -H "Authorization: Bearer $ADMIN_TOKEN"
   ```
3. **Investigate**: Review logs to identify false positive pattern
4. **Fix**: Update deny list or detection logic
5. **Re-enable Enforcement**:
   ```bash
   export FEATURE_COMPLIANCE_ENFORCEMENT_ENABLED=true
   curl -X POST https://api.example.com/admin/feature-flags/reload \
     -H "Authorization: Bearer $ADMIN_TOKEN"
   ```

## Fail-Safe Behavior

All feature flags are designed with fail-safe defaults:

| Flag | Fail-Safe Default | Behavior on Disable |
|------|------------------|---------------------|
| Rule Engine | Enabled | Returns empty task list (graceful degradation) |
| Compliance Enforcement | Enabled | Logs violations but doesn't block (safety over security) |
| Optimization Engines | Enabled | Returns empty results with informative message |

**Design Principle**: Flags should disable features, not enable them. Default should be "feature working normally."

## Testing

Feature flags are comprehensively tested:

```bash
# Run feature flag tests
pytest tests/test_feature_flags.py -v

# Test categories:
# - Flag loading and reloading
# - Rule engine with flag disabled
# - Compliance log-only mode
# - Optimization engines disabled
# - Admin access control
# - Fail-safe behavior
```

All tests verify:
- ✅ Graceful degradation (no crashes)
- ✅ Proper logging
- ✅ Metrics tracking
- ✅ Admin-only access
- ✅ Runtime reload without restart

## Monitoring

### Metrics

Feature flag state changes are logged and can be monitored:

```promql
# Alert on flag changes
changes(feature_flag_reload_count[5m]) > 0

# Track disabled features
feature_flag_disabled{flag="FEATURE_RULE_ENGINE_ENABLED"} == 1
```

### Logs

Feature flag events are logged:

```json
{
  "timestamp": "2024-01-15T10:35:00Z",
  "level": "WARNING",
  "message": "FEATURE FLAGS RELOAD: Triggered by admin 5 (admin@example.com)",
  "flags": {
    "FEATURE_RULE_ENGINE_ENABLED": false,
    ...
  }
}
```

## Best Practices

### DO

✅ **Disable features during incidents** - Rapid response without deployment
✅ **Test disabled state** - Ensure graceful degradation works
✅ **Log flag changes** - Audit trail for compliance
✅ **Use reload endpoint** - Avoid service restarts
✅ **Monitor flag state** - Alert on unexpected changes

### DON'T

❌ **Use flags for long-term A/B testing** - Use dedicated A/B testing framework
❌ **Disable compliance without reason** - Security feature, use only in emergencies
❌ **Forget to re-enable** - Flags are for temporary disable, not permanent
❌ **Skip testing** - Always verify disabled state works correctly
❌ **Allow non-admins access** - Flag management is admin-only for security

## Architecture

### Flag Service

```
app/utils/feature_flags.py
├─ FeatureFlags class
│  ├─ reload() - Load from settings
│  ├─ get_flags() - Get cached flags
│  ├─ is_enabled() - Check specific flag
│  └─ get_status() - Full status info
│
└─ Convenience functions
   ├─ is_rule_engine_enabled()
   ├─ is_compliance_enforcement_enabled()
   └─ is_optimization_engines_enabled()
```

### Integration Points

1. **Rule Engine** (`app/rules/task_generator.py`)
   - Checks flag before generating tasks
   - Returns empty list if disabled

2. **Compliance Service** (`app/compliance/service.py`)
   - Checks flag before blocking requests
   - Logs but doesn't block if disabled

3. **Optimization APIs** (`app/api/companion_analysis.py`)
   - Checks flag before analysis
   - Returns empty results if disabled

4. **Admin Endpoints** (`app/api/admin.py`)
   - View flag status (GET)
   - Reload flags (POST)

## Security Considerations

### Access Control

- ✅ Feature flag management is admin-only
- ✅ Flag changes are audit logged
- ✅ Non-admins receive 403 Forbidden

### Compliance Impact

- ⚠️ Disabling compliance enforcement reduces security
- ✅ Violations still logged and tracked
- ✅ Users still flagged
- ✅ Metrics still collected
- 🔒 Use only in emergencies

### Fail-Safe Defaults

- ✅ All flags default to True (features enabled)
- ✅ Unknown flags use fail-safe default
- ✅ Corrupted values handled gracefully
- ✅ System remains functional with all flags disabled

## Troubleshooting

### Flag Changes Not Taking Effect

**Problem**: Changed environment variable but flag still shows old value

**Solution**: Reload flags via admin endpoint:
```bash
curl -X POST /admin/feature-flags/reload -H "Authorization: Bearer $TOKEN"
```

### Service Won't Start After Flag Change

**Problem**: Invalid flag value causing startup failure

**Solution**: Check environment variables for typos:
```bash
# Valid values: true, false, 1, 0, yes, no
export FEATURE_RULE_ENGINE_ENABLED=true  # NOT "True" or "TRUE"
```

### Flags Reverting to Default

**Problem**: Flags reset to default after reload

**Solution**: Environment variables not persisted:
```bash
# Ensure .env file has correct values
cat .env | grep FEATURE_

# Or set in shell profile for persistence
echo 'export FEATURE_RULE_ENGINE_ENABLED=false' >> ~/.bashrc
```

## Future Enhancements

Planned improvements for v2:

1. **Percentage Rollouts**: Enable features for X% of users
2. **User-Specific Flags**: Override flags for specific users
3. **Scheduled Toggles**: Auto-enable/disable at specific times
4. **Remote Config**: Integrate with LaunchDarkly or similar
5. **Flag Dependencies**: Ensure dependent flags are enabled
6. **Gradual Rollout**: Slowly increase percentage over time

## Related Documentation

- [Production Metrics](METRICS_DOCUMENTATION.md) - Monitoring flag changes
- [Security Audit](SECURITY_AUDIT_AUTHORIZATION.md) - Access control verification
- [Admin API](docs/api/admin.md) - Admin endpoint reference

## Questions?

For issues or questions about feature flags:
1. Check logs for flag state changes
2. Verify environment variables are set correctly
3. Use `/admin/feature-flags` endpoint to check current state
4. Review test suite for expected behavior
