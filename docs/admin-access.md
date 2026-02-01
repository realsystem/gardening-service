# Admin Access Control

This document describes the admin role system, security model, and procedures for managing admin access.

## Table of Contents

- [Overview](#overview)
- [Role Definition](#role-definition)
- [Security Model](#security-model)
- [Admin Assignment Procedure](#admin-assignment-procedure)
- [Admin API Endpoints](#admin-api-endpoints)
- [Security Warnings](#security-warnings)
- [Testing](#testing)

## Overview

The Gardening Service implements a simple role-based access control (RBAC) system with two roles:
- **Regular User**: Standard user with access to their own data
- **Admin**: Privileged user with access to system-level operations and user management

The admin system follows a **deny-by-default** security model where:
- All users are non-admin by default
- Admin privileges cannot be granted through normal API operations
- Admin assignment requires direct database access or use of the secure admin script
- All admin privilege changes are audit-logged

## Role Definition

### Regular User

Regular users can:
- Register and manage their own account
- Create and manage gardens, plantings, tasks, etc.
- Access their own data and resources
- Update their profile (excluding admin status)

Regular users **cannot**:
- View system statistics
- Promote or demote other users
- Access admin-only endpoints
- Set their own admin status

### Admin User

Admin users have all regular user capabilities plus:
- View system-wide statistics (total users, gardens, active users, etc.)
- Promote regular users to admin status
- Revoke admin privileges from other users (except themselves)
- Access admin-only API endpoints

Admin users **cannot**:
- Revoke their own admin privileges (prevents accidental lockout)
- Bulk-promote or bulk-revoke users (prevents mass privilege escalation)

## Security Model

### Privilege Escalation Prevention

The system implements multiple layers of protection against privilege escalation:

#### 1. Registration Protection
```python
# User registration explicitly ignores is_admin field
POST /users
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "is_admin": true  // ⚠️ IGNORED - has no effect
}
```
Result: User is created with `is_admin=false` regardless of request body.

#### 2. Profile Update Protection
```python
# Profile updates explicitly filter out is_admin field
PUT /users/me
{
  "display_name": "New Name",
  "is_admin": true  // ⚠️ IGNORED - has no effect
}
```
Result: Profile is updated, but `is_admin` remains unchanged.

#### 3. Repository-Level Filtering
The `UserRepository` class explicitly removes `is_admin` from all create and update operations:
```python
def create(self, email: str, hashed_password: str, **kwargs) -> User:
    # Explicitly exclude is_admin from kwargs for security
    kwargs.pop('is_admin', None)
    user = User(email=email, hashed_password=hashed_password, **kwargs)
    # ...
```

#### 4. Admin Guard Dependency
All admin-only endpoints use the `get_current_admin_user` dependency:
```python
from app.api.dependencies import get_current_admin_user

@router.get("/stats")
def get_system_stats(
    admin: User = Depends(get_current_admin_user),  # ✅ Admin required
    db: Session = Depends(get_db)
):
    # Only accessible to admin users
```

This guard returns **403 Forbidden** for non-admin users.

### Frontend Protection

The frontend conditionally renders admin features based on `user.is_admin`:

```typescript
// Admin footer only rendered for admin users
{user.is_admin && systemStats && (
  <AdminFooter stats={systemStats} />
)}
```

Additionally:
- System stats API is only called if `user.is_admin` is true
- No network request is made for non-admin users
- Admin UI components are not rendered at all for non-admin users

### Audit Logging

All admin privilege changes are logged with:
- Timestamp (UTC)
- Admin user who performed the action
- Target user email and ID
- Action type (promotion or revocation)

Logs are written at WARNING level for visibility:
```
[2026-01-31T12:34:56] ADMIN PROMOTION: User 42 (user@example.com) promoted to admin by admin 1 (admin@example.com)
```

## Admin Assignment Procedure

### ⚠️ CRITICAL SECURITY WARNING

**Admin privileges can ONLY be assigned through direct database access.**

There are two approved methods:

### Method 1: Direct Database Script (Recommended)

Use the `assign_admin.py` script (kept outside version control):

```bash
# Assign admin privileges
python3 assign_admin.py user@example.com

# Revoke admin privileges
python3 assign_admin.py --revoke user@example.com

# List all admins
python3 assign_admin.py --list
```

The script:
- ✅ Requires confirmation before granting admin access
- ✅ Validates the user exists
- ✅ Logs all operations with timestamps
- ✅ Is idempotent (safe to run multiple times)
- ✅ Cannot be committed to Git (in .gitignore)

### Method 2: Direct Database Update

For advanced users only:

```sql
-- Grant admin privileges
UPDATE users SET is_admin = TRUE WHERE email = 'user@example.com';

-- Revoke admin privileges
UPDATE users SET is_admin = FALSE WHERE email = 'user@example.com';
```

**WARNING**: Manual SQL updates bypass audit logging.

### Method 3: Admin API Endpoint (Existing Admin Required)

Once you have at least one admin user, admins can promote other users via the API:

```bash
# Get admin token by logging in as an admin
curl -X POST http://localhost:8080/users/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"AdminPass123!"}'

# Promote a user (requires admin token)
curl -X POST http://localhost:8080/admin/users/42/promote \
  -H "Authorization: Bearer <admin_token>"

# Revoke admin (requires admin token)
curl -X POST http://localhost:8080/admin/users/42/revoke \
  -H "Authorization: Bearer <admin_token>"
```

## Admin API Endpoints

### GET /system/stats
**Admin Only** - Retrieve system-wide statistics

**Response:**
```json
{
  "total_users": 150,
  "active_users_24h": 42,
  "total_gardens": 238,
  "total_lands": 85,
  "timestamp": "2026-01-31T12:34:56.789Z"
}
```

**Errors:**
- `403 Forbidden`: Current user is not an admin

### POST /admin/users/{user_id}/promote
**Admin Only** - Promote a user to admin status

**Response:**
```json
{
  "message": "User user@example.com promoted to admin successfully",
  "user_id": 42,
  "email": "user@example.com",
  "is_admin": true,
  "promoted_by": "admin@example.com",
  "promoted_at": "2026-01-31T12:34:56.789Z"
}
```

**Idempotency**: Promoting an already-admin user returns success with message indicating they're already admin.

**Errors:**
- `403 Forbidden`: Current user is not an admin
- `404 Not Found`: Target user does not exist

### POST /admin/users/{user_id}/revoke
**Admin Only** - Revoke admin privileges from a user

**Response:**
```json
{
  "message": "Admin privileges revoked from user@example.com",
  "user_id": 42,
  "email": "user@example.com",
  "is_admin": false,
  "revoked_by": "admin@example.com",
  "revoked_at": "2026-01-31T12:34:56.789Z"
}
```

**Idempotency**: Revoking from a non-admin user returns success with message indicating they're not admin.

**Errors:**
- `400 Bad Request`: Attempting to revoke own admin privileges
- `403 Forbidden`: Current user is not an admin
- `404 Not Found`: Target user does not exist

## Security Warnings

### 🚨 CRITICAL WARNINGS

1. **Never commit `assign_admin.py` to version control**
   - The script is in `.gitignore`
   - Committing it could expose admin assignment capabilities

2. **Admin privileges grant full system access**
   - Admins can view all system statistics
   - Admins can promote/demote other admins
   - Only grant admin to fully trusted users

3. **No hidden admin paths**
   - There are no backdoors or hidden ways to become admin
   - All admin operations are logged
   - Privilege escalation is impossible by design

4. **First admin must be assigned via database**
   - Bootstrap problem: You need database access to create the first admin
   - Use `assign_admin.py` script in a secure environment
   - After first admin exists, they can promote others via API

5. **Protect the database**
   - Anyone with database write access can grant admin privileges
   - Use strong database credentials
   - Limit database access to trusted systems only

6. **Self-demotion prevention**
   - Admins cannot revoke their own privileges
   - This prevents accidental lockout
   - Always maintain at least 2 admin users

## Testing

### Running Admin Tests

Admin-specific tests are marked with `@pytest.mark.admin_access`:

```bash
# Run all admin tests
pytest -m admin_access

# Run all admin tests with verbose output
pytest -m admin_access -v

# Run specific admin test file
pytest tests/functional/test_admin_access.py -v
```

### Test Coverage

The test suite includes:

1. **Unit Tests** (`tests/unit/test_admin_guard.py`):
   - Admin guard allows admin users
   - Admin guard blocks non-admin users
   - Default is_admin value is False

2. **Functional Tests** (`tests/functional/test_admin_access.py`):
   - Registration cannot set admin (privilege escalation prevention)
   - Profile update cannot set admin (privilege escalation prevention)
   - Admin endpoints require admin privileges
   - Admins can access system stats
   - Admins can promote users
   - Admins can revoke privileges (except their own)
   - Operations are idempotent
   - Proper error handling (404 for missing users, etc.)

### Test Fixtures

Functional tests use an `admin_user` fixture that creates admin users directly in the database (simulating the secure admin assignment process).

## Implementation Files

Key files in the admin system:

- `app/models/user.py` - User model with `is_admin` field
- `app/api/dependencies.py` - `get_current_admin_user` guard
- `app/api/admin.py` - Admin promotion/revocation endpoints
- `app/api/system.py` - System statistics endpoint
- `app/repositories/user_repository.py` - Security filtering for user operations
- `migrations/versions/*_add_is_admin_to_users.py` - Database migration
- `frontend/src/components/Dashboard.tsx` - Admin footer rendering
- `tests/unit/test_admin_guard.py` - Unit tests
- `tests/functional/test_admin_access.py` - Functional tests
- `assign_admin.py` - Admin assignment script (**NOT IN GIT**)

## Best Practices

1. **Always use the admin script** for initial admin assignment
2. **Maintain at least 2 admin users** to prevent lockout
3. **Review admin audit logs regularly** for suspicious activity
4. **Use strong passwords** for admin accounts
5. **Never share admin credentials**
6. **Revoke admin access** when no longer needed
7. **Test in development** before granting production admin access
8. **Document** when and why admin access was granted

## Questions?

For questions or issues with admin access:
- Review this documentation
- Check the test suite for examples
- Verify database permissions
- Check application logs for audit entries
