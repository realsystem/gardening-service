# Password Reset - Development Mode Improvements

## Overview

The password reset flow now provides helpful error messages in **development mode** while maintaining security in production.

## Behavior by Environment

### 🔧 Development Mode (DEBUG=True)

**When email doesn't exist:**
- ❌ Returns **404 Not Found** error
- 📝 Error message: `"No account found with email 'user@example.com'. Please check the email address or register a new account."`
- 📋 Log message: `"Password reset requested for non-existent email: user@example.com"`

**When email exists:**
- ✅ Returns **200 OK** success
- 📧 Email link printed to console/logs
- 📋 Log message: `"Password reset requested for user: {user_id}"`

**Example Console Output:**
```
================================================================================
📧 PASSWORD RESET EMAIL (DEVELOPMENT MODE)
================================================================================
To: user@example.com
Subject: Reset Your Gardening Helper Password

🔗 Reset Link (copy this entire URL):
   http://localhost:3000/reset-password?token=abc123...

⏰ Link expires in: 1 hour
================================================================================
```

### 🔒 Production Mode (DEBUG=False)

**When email doesn't OR doesn't exist:**
- ✅ Always returns **200 OK** (prevents email enumeration)
- 📝 Same message: `"If the email exists, a password reset link has been sent"`
- 🔐 Attackers cannot determine if email is registered

**Why this matters:**
- Prevents malicious actors from discovering which emails are in your system
- Standard security best practice for authentication systems

## Testing the New Behavior

### Test with Non-Existent User (Development)

1. **Ensure database is empty or email doesn't exist:**
   ```bash
   docker-compose exec api python -c "
   from app.database import get_db
   from app.models.user import User
   db = next(get_db())
   users = db.query(User).all()
   print(f'Total users: {len(users)}')
   "
   ```

2. **Trigger password reset via UI:**
   - Go to http://localhost:3000/forgot-password
   - Enter a non-existent email (e.g., `test@example.com`)
   - Click "Send Reset Link"

3. **Expected result:**
   - UI shows: `"No account found with email 'test@example.com'. Please check the email address or register a new account."`
   - HTTP status: 404 Not Found

### Test with Existing User (Development)

1. **Create a test user:**
   - Go to http://localhost:3000/register
   - Register with email `user@example.com`

2. **Watch logs in real-time:**
   ```bash
   docker-compose logs api -f
   ```

3. **Trigger password reset:**
   - Go to http://localhost:3000/forgot-password
   - Enter `user@example.com`
   - Click "Send Reset Link"

4. **Expected result:**
   - UI shows: `"Password reset email sent! Please check your email (or backend console in dev mode) for the reset link."`
   - HTTP status: 200 OK
   - Console shows full email with reset link
   - Log shows: `"Password reset requested for user: 1"`

## Implementation Details

### Code Changes

**File:** `app/api/password_reset.py`

```python
if user:
    # Generate and send reset token
    # ... (existing code)
    logger.info(f"Password reset requested for user: {user.id}")
else:
    # User not found
    logger.warning(f"Password reset requested for non-existent email: {email}")

    # In development mode, return helpful error message
    # In production, don't reveal that the email doesn't exist (security)
    if settings.DEBUG:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No account found with email '{email}'. Please check the email address or register a new account."
        )

# Production mode: Always return success (prevent email enumeration)
return PasswordResetResponse(
    message="If the email exists, a password reset link has been sent",
    success=True
)
```

### Why This Approach?

✅ **Developer Experience:**
- Clear error messages during development
- No confusion when testing with non-existent emails
- Faster debugging and testing

✅ **Security:**
- Production mode maintains email enumeration protection
- Standard OWASP best practices
- No security compromises

## Troubleshooting

### "I don't see the email link in dev mode"

**Check these in order:**

1. **Verify user exists:**
   ```bash
   docker-compose exec api python -c "
   from app.database import get_db
   from app.repositories.user_repository import UserRepository
   db = next(get_db())
   user_repo = UserRepository(db)
   user = user_repo.get_by_email('your-email@example.com')
   print('User found!' if user else 'User NOT found - register first!')
   "
   ```

2. **Check DEBUG mode:**
   ```bash
   docker-compose exec api python -c "
   from app.config import get_settings
   settings = get_settings()
   print(f'DEBUG={settings.DEBUG}')
   "
   ```

3. **Verify email provider:**
   ```bash
   docker-compose exec api python -c "
   from app.services.email_service import EmailService
   provider = EmailService.get_provider()
   print(f'Provider: {type(provider).__name__}')
   "
   ```

4. **Watch logs:**
   ```bash
   docker-compose logs api -f
   ```

### "I get 404 error but I have an account"

Possible causes:
- Email case mismatch (system converts to lowercase)
- User registered with different email
- Database was reset/recreated

**Solution:**
- Check exact email in database
- Try re-registering
- Verify `.env.docker` DATABASE_URL

## Related Files

- [`app/api/password_reset.py`](app/api/password_reset.py) - Password reset endpoints
- [`app/services/email_service.py`](app/services/email_service.py) - Email providers (Console vs SMTP)
- [`.env.docker`](.env.docker) - Docker environment configuration
- [`pytest.ini`](pytest.ini) - Test environment configuration

## Summary

| Environment | Email Exists | HTTP Status | Response Message | Email Sent |
|-------------|--------------|-------------|------------------|------------|
| Development | ✅ Yes | 200 OK | "Password reset email sent..." | Console |
| Development | ❌ No | 404 Not Found | "No account found with email..." | None |
| Production | ✅ Yes | 200 OK | "If the email exists..." | Via SMTP |
| Production | ❌ No | 200 OK | "If the email exists..." | None |

This provides the best of both worlds: helpful developer experience and secure production behavior.
