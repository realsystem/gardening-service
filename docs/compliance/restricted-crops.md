# Restricted Crops Compliance Policy

## Purpose

This document describes the compliance system implemented to detect and block attempts to grow controlled or restricted plant species through the Gardening Helper Service platform.

**This is a risk mitigation and compliance feature, not agricultural guidance.**

## Policy Statement

The Gardening Helper Service **does not support** and **will not facilitate** the cultivation of controlled substances, including but not limited to cannabis/marijuana, regardless of local legal status.

This policy is implemented globally across all platform features.

## Enforcement Philosophy

### What We Block

The system blocks:

1. **Creation of planting events** for varieties identified as restricted
2. **Parameter-only optimization requests** (e.g., requesting nutrient optimization for empty gardens without any plantings)
3. **Varieties with restricted names** in common names, scientific names, species, genus, or notes fields

### What We Do NOT Do

- **We do not provide cultivation guidance** for any restricted species
- **We do not classify by legal jurisdiction** (enforcement is global, not locale-specific)
- **We do not use machine learning** - all detection is rule-based and deterministic
- **We do not automatically ban users** - violations result in flagging for admin review

## Technical Implementation

### Deny-List Approach

The system maintains a centralized deny-list (`app/compliance/deny_list.py`) containing:

- Scientific names (e.g., "Cannabis sativa", "Cannabis indica", "Cannabis ruderalis")
- Common names (e.g., "cannabis", "marijuana", "hemp")
- Slang terms (e.g., "pot", "weed", "ganja")
- Pattern-based detection (e.g., regex matching for variations)

**Version:** 1.0.0 (tracked for audit purposes)

### Enforcement Points

Restrictions are enforced at multiple API levels:

1. **Data Import** (`POST /export-import/import`) - **PRIMARY ENFORCEMENT**
   - Checks all plantings in import data before creating them
   - Validates plant_variety_id references are not restricted
   - Returns 403 Forbidden if any restricted variety detected
   - This prevents users from importing JSON with modified variety IDs

2. **Planting Event Creation** (`POST /planting-events`) - **DEFENSE IN DEPTH**
   - Checks variety name, scientific name before allowing planting
   - Returns 403 Forbidden if restricted
   - Safety net in case restricted variety enters database

3. **Nutrient Optimization** (`GET /gardens/{id}/nutrient-optimization`) - **PATTERN DETECTION**
   - Detects parameter-only optimization attempts (empty gardens)
   - Returns 403 Forbidden if suspicious pattern detected
   - Prevents reverse-engineering of cultivation parameters

### User Flagging

When a violation is detected:

1. Request is **immediately blocked** with generic error message
2. User profile is **flagged immutably** with:
   - `restricted_crop_flag` = true
   - `restricted_crop_count` incremented
   - `restricted_crop_first_violation` timestamp (set once)
   - `restricted_crop_last_violation` timestamp (updated)
   - `restricted_crop_reason` internal code (not user-visible)

**Immutability:** Flags cannot be cleared by users. Only admins can view flag status.

### Audit Logging

All violations are logged securely via application logger:

```json
{
  "timestamp": "2026-02-01T20:15:30Z",
  "user_id": 123,
  "user_email": "user@example.com",
  "violation_reason": "restricted_term_in_common_name",
  "deny_list_version": "1.0.0",
  "request_hash": "a1b2c3d4e5f6g7h8",
  "event": "RESTRICTED_PLANT_ATTEMPT"
}
```

**Security notes:**
- Logs do NOT contain plant parameters (to prevent reverse-engineering)
- Logs use request hashing (not full payload)
- Logs are admin-only (not accessible to users)

### User-Facing Messages

All blocked requests return the same generic message:

> "This request violates platform usage policies and cannot be completed."

**We never reveal:**
- What term triggered the block
- Whether detection was exact match or pattern match
- Specific reason codes

This prevents users from iteratively testing the deny-list.

## Admin Visibility

### Admin Endpoints

Admin-only endpoints provide compliance visibility:

1. **List Flagged Users**
   ```
   GET /admin/compliance/flagged-users
   ```
   Returns list of users sorted by most recent violation.

2. **User Details**
   ```
   GET /admin/compliance/flagged-users/{user_id}
   ```
   Returns detailed violation history for specific user.

3. **System Stats**
   ```
   GET /admin/compliance/stats
   ```
   Returns aggregated metrics:
   - Total flagged users
   - Total violations
   - Violations in last 30 days
   - Current deny-list version

### Access Control

- All `/admin/compliance/*` endpoints require admin role
- Returns 403 Forbidden for non-admin users
- Uses `get_current_admin_user` dependency

## Pattern Detection

### Parameter-Only Optimization

The system detects attempts to infer restricted plant parameters by:

- Requesting nutrient optimization for hydroponic gardens with **zero plantings**
- Rationale: Legitimate users plant first, then optimize; attempts to get parameters without crops are suspicious

**Action:** Block request, flag user, log event

### Future Patterns (Not Yet Implemented)

- Repeated EC/pH tuning cycles matching known growth stages
- Frequent garden edits with parameter changes
- Custom crop creation with missing taxonomy

## Known Limitations

### False Positives

The system may flag legitimate plants with overlapping terminology:

- **Canna Lily** (Canna indica) - genus "Canna" is different from "Cannabis", but species "indica" may trigger pattern match
- **Notes containing "pot"** - e.g., "Plant in 6-inch pot" may trigger slang detection

**Design decision:** Prefer security over convenience. False positives are acceptable to prevent evasion.

### Legitimate Use Cases Not Supported

- **Research institutions** - no exception mechanism currently exists
- **Legal cultivation jurisdictions** - policy is global, not locale-aware
- **Industrial hemp** - hemp is restricted even though it may be legal in some jurisdictions

### Bypass Opportunities

Potential evasion methods (documented for future hardening):

- **Visual circumvention** - using images/photos instead of text names (not detected)
- **Language variants** - non-English terms (not currently in deny-list)
- **Extreme misspellings** - e.g., "c4nn4b1s" with numbers (not pattern-matched)

## Legal Neutrality Disclaimer

**This system is not legal advice.**

- Compliance enforcement does not constitute legal judgment
- Local laws vary by jurisdiction
- Platform operator assumes no liability for user actions
- Users are responsible for compliance with local regulations

**We do not:**
- Determine what is legal in any jurisdiction
- Report violations to law enforcement
- Make claims about legality of any plant species

## Version History

- **v1.0.0** (2026-02-01) - Initial implementation
  - Basic deny-list with 40+ terms
  - API enforcement at planting/optimization endpoints
  - User flagging and admin visibility
  - Pattern detection for parameter-only optimization

## Testing

Compliance features are thoroughly tested:

- **Unit tests:** `tests/test_compliance_deny_list.py` (25+ tests)
- **Functional tests:** `tests/test_compliance_api.py` (15+ tests)
- **Marker:** `@pytest.mark.compliance`

Run compliance tests:
```bash
pytest -m compliance -v
```

## False-Positive Mitigation Notes

To reduce false positives while maintaining security:

1. **Exact matches** use case-insensitive comparison
2. **Pattern matches** use word boundaries (`\b`) to avoid partial matches
3. **Context-aware patterns** - e.g., "pot plant" vs "plant in pot"
4. **Species-level checking** - cross-reference multiple taxonomy fields

Despite mitigations, some false positives are expected and acceptable per security-first design.

## Suggested Future Extensions

(Do NOT implement - for future consideration only)

1. **Jurisdiction awareness** - detect user location, apply jurisdiction-specific rules
2. **Research exemptions** - verified research institution accounts with override capability
3. **Language expansion** - add Spanish, French, other language deny-list terms
4. **Image analysis** - detect restricted plants in uploaded photos (ML-based)
5. **Historical pattern analysis** - track request frequency, flag repeated optimization attempts
6. **Exportability** - deny-list export for third-party integration

---

**Document Owner:** Compliance Team
**Last Updated:** 2026-02-01
**Next Review:** 2026-08-01
