# Password Reset Feature Documentation

## Overview

The Gardening Helper service includes a secure, production-ready password reset feature that allows users to reset their passwords via email.

## Security Features

### Token Security
- **Cryptographically Secure**: Uses Python's `secrets` module (256-bit tokens)
- **Hashed Storage**: Tokens are hashed with SHA-256 before database storage
- **Time-Limited**: Tokens expire after 1 hour
- **Single-Use**: Tokens can only be used once
- **One Active Token**: Creating a new token invalidates previous ones

### Password Requirements
- Minimum 8 characters
- At least one uppercase letter (A-Z)
- At least one lowercase letter (a-z)
- At least one digit (0-9)
- At least one special character (!@#$%^&*...)

### Rate Limiting
- Maximum 3 reset requests per email per 15 minutes
- Prevents abuse and brute-force attempts
- Returns HTTP 429 (Too Many Requests) when exceeded

### Anti-Enumeration
- Always returns success message regardless of email existence
- Prevents attackers from discovering valid email addresses

## API Endpoints

### 1. Request Password Reset

**Endpoint:** `POST /auth/password-reset/request`

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:** (Always successful to prevent email enumeration)
```json
{
  "message": "If the email exists, a password reset link has been sent",
  "success": true
}
```

**Status Codes:**
- `200` - Request processed (doesn't reveal if email exists)
- `429` - Too many requests (rate limited)
- `422` - Invalid email format

### 2. Confirm Password Reset

**Endpoint:** `POST /auth/password-reset/confirm`

**Request Body:**
```json
{
  "token": "3x7k9mQpR2nV8yB4cF6hJ1sL5tN0wPqE7uG2aD9zX5C",
  "new_password": "NewStrongPassword123!"
}
```

**Response:**
```json
{
  "message": "Password has been reset successfully. You can now log in with your new password",
  "success": true
}
```

**Status Codes:**
- `200` - Password reset successful
- `400` - Invalid/expired/used token
- `400` - User not found
- `422` - Weak password (doesn't meet requirements)

### 3. Get Password Requirements

**Endpoint:** `GET /auth/password-reset/requirements`

**Response:**
```json
{
  "requirements": [
    "At least 8 characters",
    "At least one uppercase letter (A-Z)",
    "At least one lowercase letter (a-z)",
    "At least one digit (0-9)",
    "At least one special character (!@#$%^&*...)"
  ]
}
```

## User Flow

### Development Mode (Local Testing)

1. User clicks "Forgot Password?" on login page
2. User enters email address
3. Backend logs reset URL to console (visible in docker logs):
   ```
   ================================================================================
   📧 PASSWORD RESET EMAIL (DEVELOPMENT MODE)
   ================================================================================
   To: user@example.com
   Subject: Reset Your Gardening Helper Password

   🔗 Reset Link (copy this entire URL):
      http://localhost:3000/reset-password?token=ABC123...

   ⏰ Link expires in: 1 hour
   ================================================================================
   ```
4. User copies URL from backend logs and opens in browser
5. User enters and confirms new password
6. User is redirected to login with new password

### Production Mode

1. User clicks "Forgot Password?" on login page
2. User enters email address
3. User receives email with reset link
4. User clicks link in email (opens reset page)
5. User enters and confirms new password
6. User is redirected to login with new password

## Local Development Setup

### Prerequisites
- Docker and Docker Compose installed
- Services running: `docker-compose up -d`

### Testing Password Reset

1. **Start the services:**
   ```bash
   cd gardening-service
   docker-compose up -d
   ```

2. **Access the frontend:**
   Open http://localhost:3000 in your browser

3. **Request a password reset:**
   - Click "Forgot password?" on the login page
   - Enter an email address (e.g., demo@test.com)
   - Click "Send Reset Link"

4. **Get the reset token:**
   Check the backend logs:
   ```bash
   docker-compose logs -f api
   ```

   Look for the prominent password reset email output with emoji markers:
   ```
   ================================================================================
   📧 PASSWORD RESET EMAIL (DEVELOPMENT MODE)
   ================================================================================
   ...
   🔗 Reset Link (copy this entire URL):
      http://localhost:3000/reset-password?token=ABC123...
   ...
   ================================================================================
   ```

5. **Copy and open the reset URL:**
   - Copy the entire URL from the logs
   - Paste it into your browser
   - The reset password page will load with the token

6. **Reset your password:**
   - Enter a new password that meets the requirements
   - Confirm the password
   - Click "Reset Password"

7. **Login with new password:**
   - You'll be redirected to the login page
   - Login with your email and new password

## Production Deployment

### Environment Variables

For production, configure SMTP email settings:

```bash
# SMTP Configuration (required for production)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@yourdomain.com
SMTP_FROM_NAME=Gardening Helper

# Application Settings
DEBUG=False  # Must be False to use SMTP instead of console
```

### SMTP Provider Setup Examples

#### Gmail
1. Enable 2-Factor Authentication
2. Generate an App Password
3. Use `smtp.gmail.com:587`

#### SendGrid
1. Create API Key
2. Use `smtp.sendgrid.net:587`
3. Username: `apikey`
4. Password: Your SendGrid API key

#### AWS SES
1. Verify sender email
2. Get SMTP credentials
3. Use regional endpoint (e.g., `email-smtp.us-east-1.amazonaws.com:587`)

### Frontend URL Configuration

Update the reset URL to match your production frontend:

In `app/api/password_reset.py`, modify:
```python
frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
reset_url = f"{frontend_url}/reset-password?token={raw_token}"
```

Then set in environment:
```bash
FRONTEND_URL=https://your-production-domain.com
```

## Database Schema

### password_reset_tokens Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| user_id | Integer | Foreign key to users table |
| token_hash | String(255) | SHA-256 hash of the token |
| expires_at | DateTime | Token expiration time |
| used_at | DateTime | When token was used (NULL if unused) |
| created_at | DateTime | Token creation time |

**Indexes:**
- `ix_password_reset_tokens_token_hash` (unique) - Fast token lookups
- `idx_user_active_tokens` (user_id, used_at, expires_at) - Query active tokens

## Testing

### Backend Tests

Run the password reset test suite:

```bash
# In Docker
docker exec gardening-service-api-1 pytest tests/test_password_reset.py -v

# Locally
cd gardening-service
pytest tests/test_password_reset.py -v
```

**Test Coverage:**
- ✅ Request reset for existing email
- ✅ Request reset for non-existent email (no enumeration)
- ✅ Invalid email format
- ✅ Rate limiting (3 requests max)
- ✅ Confirm reset with valid token
- ✅ Invalid token rejection
- ✅ Expired token rejection
- ✅ Used token rejection (single-use)
- ✅ Token reuse attempt
- ✅ Weak password rejection
- ✅ Password validator tests
- ✅ Token generator tests
- ✅ Rate limiter tests
- ✅ Repository operations

### Manual Testing Checklist

- [ ] Request reset for existing user
- [ ] Request reset for non-existent user (same response)
- [ ] Trigger rate limit (4+ requests in 15 minutes)
- [ ] Use reset link from logs/email
- [ ] Try expired token (wait 1+ hour)
- [ ] Try already-used token
- [ ] Set weak password (should fail)
- [ ] Set strong password (should succeed)
- [ ] Login with new password
- [ ] Verify old password no longer works

## Security Considerations

### What's Secure

✅ Tokens use cryptographically secure random generation
✅ Tokens are hashed before storage (SHA-256)
✅ Tokens expire after 1 hour
✅ Tokens are single-use only
✅ Rate limiting prevents abuse
✅ No email enumeration
✅ Password strength enforcement
✅ HTTPS recommended for production

### Recommendations

1. **Use HTTPS in production** - Never send tokens over HTTP
2. **Configure SMTP properly** - Use app passwords or API keys
3. **Monitor rate limit hits** - Alert on potential attacks
4. **Regular token cleanup** - Run maintenance to delete old tokens:
   ```python
   from app.repositories.password_reset_repository import PasswordResetRepository
   repo = PasswordResetRepository(db)
   deleted = repo.cleanup_expired_tokens(days_old=7)
   ```
5. **Session invalidation** - Consider invalidating existing sessions after password reset

## Troubleshooting

### Problem: Reset link not appearing in logs

**Solution:**
- Check that `DEBUG=True` in development
- Look for `PASSWORD RESET EMAIL (DEVELOPMENT MODE)` in backend logs
- Ensure the API container is running: `docker ps`

### Problem: "Invalid or expired reset token"

**Solutions:**
- Token may have expired (1 hour limit)
- Token may have already been used
- Request a new reset link

### Problem: "Too many password reset requests"

**Solutions:**
- Wait 15 minutes before trying again
- Rate limit is per-email, try different email
- In development, restart the API container to reset rate limiter

### Problem: Password reset email not sent in production

**Solutions:**
- Verify `DEBUG=False` in environment
- Check SMTP credentials are correct
- Verify SMTP_HOST, SMTP_USER, SMTP_PASSWORD are set
- Check firewall allows outbound SMTP (port 587)
- Review API logs for email errors

### Problem: "Password must contain..." errors

**Solution:**
- Review password requirements
- Ensure password includes:
  - At least 8 characters
  - Uppercase and lowercase letters
  - At least one digit
  - At least one special character

## File Structure

```
app/
├── models/
│   └── password_reset_token.py          # Database model
├── schemas/
│   └── password_reset.py                # Pydantic schemas
├── repositories/
│   └── password_reset_repository.py     # Database operations
├── services/
│   └── email_service.py                 # Email abstraction (Console/SMTP)
├── api/
│   └── password_reset.py                # API endpoints
├── utils/
│   ├── token_generator.py               # Secure token generation
│   ├── password_validator.py            # Password strength validation
│   └── rate_limiter.py                  # Rate limiting

frontend/src/
├── components/
│   ├── ForgotPassword.tsx               # Request reset page
│   ├── ResetPassword.tsx                # Confirm reset page
│   └── Auth.tsx                         # Updated with "Forgot?" link
├── services/
│   └── api.ts                           # API client methods
└── App.tsx                              # Routing logic

migrations/versions/
└── 20260129_0845_add_password_reset_tokens.py

tests/
└── test_password_reset.py               # Comprehensive test suite
```

## Support

For issues or questions:
- Check logs: `docker-compose logs -f api`
- Review this documentation
- Check API docs: http://localhost:8080/docs
- File an issue in the repository

## License

Part of the Gardening Helper Service - See main README for license information.
