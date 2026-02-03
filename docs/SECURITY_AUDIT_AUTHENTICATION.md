# Authentication & Session Security Audit

**Date:** 2026-02-01
**Auditor:** Security Review
**Scope:** Authentication, password hashing, token management, rate limiting, CSRF protection
**Status:** 🔴 **CRITICAL FINDINGS** - Immediate action required

---

## Executive Summary

This audit examines the authentication and session handling security of the Gardening Service application. **CRITICAL vulnerabilities** were identified that expose the application to brute force attacks and token hijacking.

### Risk Rating: **HIGH** 🔴

| Component | Status | Risk Level |
|-----------|--------|------------|
| Password Hashing | ⚠️ Partially Secure | MEDIUM |
| Token Expiration | 🔴 Vulnerable | HIGH |
| Token Rotation | ❌ Not Implemented | HIGH |
| CSRF Protection | ✅ Not Applicable | LOW |
| Rate Limiting (Login) | ❌ Not Implemented | **CRITICAL** |
| Rate Limiting (Registration) | ❌ Not Implemented | HIGH |
| Rate Limiting (Password Reset) | ✅ Implemented | LOW |

### Critical Findings

1. **🔴 CRITICAL: No Rate Limiting on Login** - Enables unlimited brute force attacks
2. **🔴 HIGH: Token Expiration Too Long** - 1 week (10,080 minutes) enables long-lived token hijacking
3. **🔴 HIGH: No Token Rotation** - Compromised tokens remain valid indefinitely
4. **🔴 HIGH: No Rate Limiting on Registration** - Enables spam account creation
5. **⚠️ MEDIUM: Bcrypt Cost Factor Not Configurable** - Uses default (rounds=12), should be tunable

---

## 1. Password Hashing Security

### Current Implementation

**File:** `app/services/auth_service.py:34-38`

```python
@staticmethod
def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    prepared_password = AuthService._prepare_password(password)
    hashed = bcrypt.hashpw(prepared_password, bcrypt.gensalt())  # ⚠️ Default cost
    return hashed.decode('utf-8')
```

#### Analysis

**✅ Strengths:**

1. **Uses bcrypt** - Industry standard, designed for password hashing
2. **SHA-256 Pre-hashing** - Avoids bcrypt's 72-byte limit
   ```python
   hashlib.sha256(password.encode('utf-8')).hexdigest().encode('utf-8')
   ```
3. **Automatic salt generation** - `bcrypt.gensalt()` generates unique salt per password
4. **Constant-time verification** - `bcrypt.checkpw()` prevents timing attacks

**⚠️ Weaknesses:**

1. **Default Cost Factor (12 rounds)** - Not configurable
   - Current: ~0.3 seconds per hash (on modern CPU)
   - Recommended: 12-14 rounds minimum, configurable via environment variable
   - Future-proofing: Should increase as hardware improves

2. **No Cost Factor Monitoring** - No visibility into actual cost
   - Should log hashing time to verify sufficient slowdown

**Risk:** MEDIUM
**Impact:** Offline brute force attacks slightly easier than optimal

### Password Strength Validation

**File:** `app/utils/password_validator.py`

**✅ Comprehensive Requirements:**
- Minimum 8 characters
- Uppercase, lowercase, digit, special character
- Regex validation with clear error messages

**Recommendation:** Consider increasing minimum to 10-12 characters.

---

## 2. Token Expiration & Rotation

### Current Implementation

**File:** `app/config.py:19`

```python
ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 1 week
```

**File:** `app/services/auth_service.py:51-65`

```python
@staticmethod
def create_access_token(user_id: int, email: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": str(user_id),
        "email": email,
        "exp": expire
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
```

### Critical Issues

#### 🔴 Issue #1: Excessive Token Lifetime

**Current:** 10,080 minutes (7 days)
**Recommended:** 15-60 minutes for access tokens

**Attack Scenario:**
1. Attacker steals token (XSS, network sniffing, malware)
2. Token remains valid for **7 days**
3. Attacker has full account access for a week
4. Legitimate user has no way to revoke the token

**Impact:** HIGH - Extended window for token hijacking attacks

#### 🔴 Issue #2: No Token Rotation

**Problem:** Once issued, tokens cannot be revoked or rotated

**Missing Features:**
- No refresh token mechanism
- No token blacklist/revocation
- No session management
- No "logout all devices" capability

**Attack Scenario:**
1. User's device is compromised
2. Attacker extracts JWT token
3. User logs out on their device
4. Attacker's token **still works** - logout is client-side only

**Impact:** HIGH - Compromised tokens cannot be revoked

#### 🔴 Issue #3: No Token Versioning

**Problem:** No way to invalidate all tokens for a user

**Missing:** Token version/generation number in payload
```python
# Current payload
{"sub": "123", "email": "user@example.com", "exp": 1234567890}

# Recommended payload
{"sub": "123", "email": "user@example.com", "exp": 1234567890, "ver": 5}
```

### Recommendations

#### Short-Term (Critical)

1. **Reduce access token lifetime to 15 minutes**
   ```python
   ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
   ```

2. **Implement refresh token pattern**
   - Access token: 15 minutes
   - Refresh token: 7 days (stored in database)
   - Refresh endpoint: `/auth/refresh`

3. **Add token versioning**
   ```python
   # User model
   token_version = Column(Integer, default=1)

   # In create_access_token
   to_encode = {
       "sub": str(user_id),
       "email": email,
       "exp": expire,
       "ver": user.token_version  # Invalidate all tokens by incrementing
   }
   ```

#### Long-Term (High Priority)

1. **Implement refresh token rotation**
   - Each refresh issues new access + refresh token
   - Old refresh token is invalidated
   - Detects token theft (reuse of revoked refresh token)

2. **Add token blacklist for early revocation**
   - Redis-based with TTL = remaining token lifetime
   - Check on each request if token is blacklisted

3. **Session management UI**
   - "Active Sessions" page showing all devices
   - "Logout All Devices" button (increment token_version)

---

## 3. CSRF Protection

### Current Implementation

**Status:** ✅ **Not Applicable** (JWT-based stateless authentication)

### Analysis

**Why CSRF Protection is Not Required:**

1. **Stateless Authentication** - No cookies, no session state
2. **Bearer Token Auth** - Tokens in Authorization header, not cookies
3. **SOP Protection** - JavaScript cannot access cross-origin tokens
4. **No Automatic Credential Submission** - Unlike cookies, tokens must be explicitly included

**Attack Vector Analysis:**

Traditional CSRF attack:
```html
<!-- Attacker's site -->
<form action="https://victim-site.com/api/transfer" method="POST">
  <input name="amount" value="1000">
  <input name="to" value="attacker_account">
</form>
<script>document.forms[0].submit();</script>
```

**Why this doesn't work here:**
- Browser automatically sends cookies ❌ (app doesn't use cookies)
- Browser automatically includes JWT token ❌ (tokens in header, not cookie)
- JavaScript can forge request ❌ (SOP prevents cross-origin token access)

**Verdict:** ✅ CSRF protection not needed for JWT-based API

**⚠️ EXCEPTION:** If cookies are added in the future, CSRF protection becomes **MANDATORY**.

---

## 4. Rate Limiting

### Current Implementation

#### ✅ Password Reset: Implemented

**File:** `app/utils/rate_limiter.py`

**Configuration:**
```python
password_reset_rate_limiter = RateLimiter(max_attempts=3, window_minutes=15)
```

**Features:**
- ✅ Per-email rate limiting
- ✅ Thread-safe (mutex lock)
- ✅ Automatic cleanup
- ✅ Applied to `/auth/password-reset/request`

**Quality:** **Excellent** - Well-designed, properly enforced

#### 🔴 Login: NOT IMPLEMENTED

**File:** `app/api/users.py:64-80` (login endpoint)

**Current Code:**
```python
@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    # ⚠️ NO RATE LIMITING
    user = AuthService.authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, ...)
    access_token = AuthService.create_access_token(user.id, user.email)
    return Token(access_token=access_token)
```

**Attack Scenario:**

```python
# Attacker script (unlimited brute force)
import requests

target = "https://gardening-service.com/users/login"
emails = ["user@example.com", "admin@example.com", ...]
passwords = load_common_passwords()  # 10M+ passwords

for email in emails:
    for password in passwords:
        r = requests.post(target, json={"email": email, "password": password})
        if r.status_code == 200:
            print(f"[PWNED] {email}:{password}")
            break
```

**Current Defense:** ❌ **NONE**

**Consequences:**
- Unlimited login attempts per second
- No account lockout
- No IP-based blocking
- Credential stuffing attacks trivial
- Brute force attacks undetected

**Risk:** **CRITICAL** 🔴
**Severity:** **P0 - Immediate Fix Required**

#### 🔴 Registration: NOT IMPLEMENTED

**File:** `app/api/users.py:17-61` (create_user endpoint)

**Attack Scenario:**

```python
# Spam account creation
for i in range(1000000):
    requests.post("/users", json={
        "email": f"spam{i}@fake.com",
        "password": "Spam123!"
    })
```

**Consequences:**
- Database flooding
- Resource exhaustion
- Email verification spam (if added)
- No cost to attacker

**Risk:** **HIGH** 🔴

---

## 5. Security Vulnerability Summary

### Critical (P0 - Fix Immediately)

| ID | Vulnerability | CVSS | Exploitability | Impact |
|----|---------------|------|----------------|--------|
| **AUTH-001** | No rate limiting on login | 9.1 | Trivial | Account takeover via brute force |
| **AUTH-002** | Token lifetime 7 days | 7.5 | Easy | Extended window for token hijacking |
| **AUTH-003** | No token rotation/revocation | 8.2 | Easy | Compromised tokens remain valid |

### High (P1 - Fix Within 1 Week)

| ID | Vulnerability | CVSS | Exploitability | Impact |
|----|---------------|------|----------------|--------|
| **AUTH-004** | No rate limiting on registration | 6.5 | Trivial | Spam account creation, resource exhaustion |
| **AUTH-005** | No session management | 5.8 | Medium | Cannot revoke access from stolen devices |

### Medium (P2 - Fix Within 1 Month)

| ID | Vulnerability | CVSS | Exploitability | Impact |
|----|---------------|------|----------------|--------|
| **AUTH-006** | Bcrypt cost not configurable | 4.2 | Hard | Slightly faster offline brute force |
| **AUTH-007** | No account lockout policy | 5.1 | Easy | Persistent brute force attempts |

---

## 6. Recommended Security Enhancements

### Phase 1: Critical (Immediate - Week 1)

#### 1. Add Rate Limiting to Login

**Create:** `app/api/users.py` (modify login endpoint)

```python
from app.utils.rate_limiter import RateLimiter

# Global rate limiter for login
login_rate_limiter = RateLimiter(max_attempts=5, window_minutes=15)

@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    email = credentials.email.lower()

    # Rate limiting
    is_allowed, remaining = login_rate_limiter.is_allowed(email)
    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Try again in 15 minutes."
        )

    # Authenticate
    user = AuthService.authenticate_user(db, email, credentials.password)

    if not user:
        # Record failed attempt
        login_rate_limiter.record_attempt(email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Success - reset rate limit
    login_rate_limiter.reset(email)

    access_token = AuthService.create_access_token(user.id, user.email)
    return Token(access_token=access_token)
```

#### 2. Reduce Token Lifetime

**File:** `app/config.py`

```python
# Before
ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 1 week

# After
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1 hour (or 15 min with refresh tokens)
```

**⚠️ UX Impact:** Users will need to log in more frequently

**Mitigation:** Implement refresh tokens (Phase 2)

#### 3. Add Token Versioning

**Migration:**
```sql
ALTER TABLE users ADD COLUMN token_version INTEGER NOT NULL DEFAULT 1;
```

**Code:**
```python
# app/services/auth_service.py
@staticmethod
def create_access_token(user_id: int, email: str, token_version: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": str(user_id),
        "email": email,
        "ver": token_version,  # NEW
        "exp": expire
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# app/api/dependencies.py
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = None) -> User:
    payload = AuthService.decode_token(credentials.credentials)
    user = UserRepository(db).get_by_id(int(payload["sub"]))

    # Verify token version
    if payload.get("ver") != user.token_version:
        raise HTTPException(401, "Token has been revoked")

    return user
```

### Phase 2: High Priority (Week 2)

#### 4. Add Rate Limiting to Registration

```python
registration_rate_limiter = RateLimiter(max_attempts=3, window_minutes=60)

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    email = user_data.email.lower()

    # Rate limiting
    is_allowed, remaining = registration_rate_limiter.is_allowed(email)
    if not is_allowed:
        raise HTTPException(429, "Too many registration attempts")

    registration_rate_limiter.record_attempt(email)

    # ... rest of registration logic
```

#### 5. Implement Refresh Tokens

**New Model:**
```python
# app/models/refresh_token.py
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    token_hash = Column(String, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    revoked = Column(Boolean, default=False)

    user = relationship("User", back_populates="refresh_tokens")
```

**New Endpoint:**
```python
@router.post("/auth/refresh", response_model=Token)
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    # Validate refresh token
    # Issue new access token + new refresh token
    # Revoke old refresh token
    pass
```

### Phase 3: Medium Priority (Month 1)

#### 6. Make Bcrypt Cost Configurable

```python
# app/config.py
BCRYPT_ROUNDS: int = 12  # Default, should be 12-14

# app/services/auth_service.py
@staticmethod
def hash_password(password: str) -> str:
    prepared_password = AuthService._prepare_password(password)
    rounds = get_settings().BCRYPT_ROUNDS
    hashed = bcrypt.hashpw(prepared_password, bcrypt.gensalt(rounds=rounds))
    return hashed.decode('utf-8')
```

#### 7. Add Account Lockout

```python
# After N failed attempts (e.g., 10), lock account for 1 hour
# Requires new fields: failed_login_attempts, locked_until
```

#### 8. Add Logout Endpoint

```python
@router.post("/auth/logout")
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Increment token_version to invalidate all tokens
    current_user.token_version += 1
    db.commit()
    return {"message": "Logged out successfully"}
```

---

## 7. Testing Requirements

### Security Tests to Add

Create `tests/test_auth_security.py`:

```python
class TestLoginRateLimiting:
    """Verify login endpoint is protected against brute force"""

    def test_login_rate_limit_enforced(self):
        """Should block after 5 failed attempts"""
        for i in range(5):
            response = client.post("/users/login", json={
                "email": "victim@example.com",
                "password": "wrong_password"
            })
            assert response.status_code == 401

        # 6th attempt should be rate limited
        response = client.post("/users/login", json={
            "email": "victim@example.com",
            "password": "wrong_password"
        })
        assert response.status_code == 429

    def test_login_rate_limit_resets_on_success(self):
        """Successful login should reset rate limit"""
        # 4 failed attempts
        for i in range(4):
            client.post("/users/login", json={
                "email": "user@example.com",
                "password": "wrong"
            })

        # Successful login
        client.post("/users/login", json={
            "email": "user@example.com",
            "password": "correct_password"
        })

        # Should be able to attempt again
        response = client.post("/users/login", json={
            "email": "user@example.com",
            "password": "wrong"
        })
        assert response.status_code == 401  # Not 429

class TestTokenSecurity:
    """Verify JWT token security"""

    def test_token_expires_after_configured_time(self):
        """Token should be rejected after expiration"""
        # Set short expiration in test config
        # Wait for expiration
        # Verify token is rejected
        pass

    def test_token_version_mismatch_rejected(self):
        """Old tokens should be rejected after version increment"""
        # Get token
        # Increment user.token_version
        # Verify token is rejected
        pass

    def test_token_cannot_be_forged(self):
        """Tokens with incorrect signature should be rejected"""
        # Create token with wrong secret
        # Verify rejection
        pass

class TestPasswordHashing:
    """Verify password hashing security"""

    def test_bcrypt_cost_factor_applied(self):
        """Verify bcrypt cost factor is sufficient"""
        import time
        start = time.time()
        AuthService.hash_password("TestPassword123!")
        duration = time.time() - start

        # Should take at least 100ms (cost=12)
        assert duration > 0.1

    def test_same_password_different_hashes(self):
        """Same password should produce different hashes (salt)"""
        hash1 = AuthService.hash_password("TestPassword123!")
        hash2 = AuthService.hash_password("TestPassword123!")
        assert hash1 != hash2
```

---

## 8. Security Assumptions

### Current Assumptions

1. **HTTPS in Production** ✅ ASSUMED (not verified in code)
   - JWTs transmitted in Authorization header
   - **Risk if HTTP:** Tokens visible in plaintext

2. **Secret Key Rotation** ❌ NOT IMPLEMENTED
   - `SECRET_KEY` in config never changes
   - Compromised key = all tokens compromised

3. **Secret Key Strength** ⚠️ DEFAULT WEAK
   ```python
   SECRET_KEY: str = "dev-secret-key-change-in-production"
   ```
   - **Risk:** Default key in production = total compromise

4. **No Token Storage Client-Side** ✅ ASSUMED
   - Frontend should use memory/secure storage
   - **Risk if localStorage:** XSS can steal tokens

5. **Single Server Deployment** ⚠️ ASSUMED
   - RateLimiter uses in-memory storage
   - **Risk in multi-server:** Rate limits not shared

### Required for Production

| Requirement | Current | Needed |
|-------------|---------|--------|
| HTTPS enforced | ❌ | ✅ Add middleware |
| Strong SECRET_KEY | ❌ (default) | ✅ Generate random 256-bit |
| SECRET_KEY in env vars | ✅ | ✅ Already supported |
| Redis for rate limiting | ❌ | ✅ For multi-server |
| Refresh token DB table | ❌ | ✅ For token rotation |

---

## 9. Compliance Considerations

### OWASP Top 10 (2021)

| Vulnerability | Status | Notes |
|---------------|--------|-------|
| A01: Broken Access Control | ⚠️ Partial | No token revocation |
| A02: Cryptographic Failures | ✅ OK | Bcrypt for passwords, JWT for tokens |
| A03: Injection | ✅ OK | SQLAlchemy ORM prevents SQL injection |
| A04: Insecure Design | 🔴 Vulnerable | No rate limiting on login |
| A05: Security Misconfiguration | 🔴 Vulnerable | Default SECRET_KEY, no HTTPS enforcement |
| A07: Identification and Authentication Failures | 🔴 Vulnerable | No rate limiting, long token lifetime |

### PCI DSS (if handling payments)

- **Requirement 8.2.4:** Password minimum 7 chars ✅ (using 8)
- **Requirement 8.2.3:** Strong password policy ✅
- **Requirement 8.2.5:** Account lockout ❌ NOT IMPLEMENTED

---

## 10. Immediate Action Items

### Week 1 (Critical)

- [ ] **AUTH-001:** Add rate limiting to login endpoint
- [ ] **AUTH-002:** Reduce token lifetime to 1 hour
- [ ] **AUTH-003:** Add token versioning for revocation
- [ ] **AUTH-008:** Enforce HTTPS in production (middleware)
- [ ] **AUTH-009:** Rotate SECRET_KEY to strong random value

### Week 2 (High)

- [ ] **AUTH-004:** Add rate limiting to registration
- [ ] **AUTH-005:** Implement refresh token pattern
- [ ] **AUTH-010:** Create comprehensive security tests

### Month 1 (Medium)

- [ ] **AUTH-006:** Make bcrypt cost configurable
- [ ] **AUTH-007:** Implement account lockout policy
- [ ] **AUTH-011:** Add session management UI
- [ ] **AUTH-012:** Implement Redis-based rate limiting

---

## 11. Conclusion

The authentication system has a **solid foundation** (bcrypt, JWT, password validation) but has **critical gaps** that make it vulnerable to common attacks:

🔴 **CRITICAL:** Brute force attacks are trivial (no rate limiting on login)
🔴 **HIGH:** Token hijacking window is excessive (7-day lifetime)
🔴 **HIGH:** Compromised tokens cannot be revoked

**Recommendation:** Implement Phase 1 changes **immediately** before deploying to production.

**Estimated Effort:**
- Phase 1 (Critical): 8-12 hours
- Phase 2 (High): 16-24 hours
- Phase 3 (Medium): 24-32 hours

**Total:** 2-3 days of focused development

---

**Document Version:** 1.0
**Last Updated:** 2026-02-01
**Next Review:** After Phase 1 implementation
