"""Email service abstraction for password reset notifications"""
import logging
from abc import ABC, abstractmethod
from typing import Optional
from app.config import get_settings

logger = logging.getLogger(__name__)


class EmailProvider(ABC):
    """Abstract base class for email providers"""

    @abstractmethod
    def send_password_reset_email(self, to_email: str, reset_url: str) -> bool:
        """
        Send password reset email.

        Args:
            to_email: Recipient email address
            reset_url: Password reset URL with token

        Returns:
            True if email sent successfully

        Raises:
            Exception: If email sending fails
        """
        pass


class ConsoleEmailProvider(EmailProvider):
    """
    Development email provider that logs to console.

    Use this for local development - no SMTP configuration required.
    Reset links are printed to the console instead of being emailed.

    WARNING: This is for development only. Real emails are NOT sent.
    """

    def send_password_reset_email(self, to_email: str, reset_url: str) -> bool:
        """
        Log password reset URL to console (development mode).

        Args:
            to_email: Recipient email address
            reset_url: Password reset URL with token

        Returns:
            Always returns True (console logging never fails)
        """
        import sys

        # Print to stdout with immediate flush (visible in docker logs)
        print("\n" + "=" * 80, flush=True)
        print("📧 PASSWORD RESET EMAIL (DEVELOPMENT MODE)", flush=True)
        print("=" * 80, flush=True)
        print(f"To: {to_email}", flush=True)
        print(f"Subject: Reset Your Gardening Helper Password", flush=True)
        print("", flush=True)
        print("🔗 Reset Link (copy this entire URL):", flush=True)
        print(f"   {reset_url}", flush=True)
        print("", flush=True)
        print("⏰ Link expires in: 1 hour", flush=True)
        print("=" * 80 + "\n", flush=True)
        sys.stdout.flush()  # Force flush

        # Also log via logger for persistence
        logger.warning(f"[DEV MODE] Password reset requested for {to_email}")
        logger.warning(f"[DEV MODE] Reset URL: {reset_url}")

        return True


class SMTPEmailProvider(EmailProvider):
    """
    Production email provider using SMTP.

    Configure via environment variables:
    - SMTP_HOST: SMTP server hostname (required)
    - SMTP_PORT: SMTP server port (default: 587)
    - SMTP_USER: SMTP username (required)
    - SMTP_PASSWORD: SMTP password (required)
    - SMTP_FROM_EMAIL: Sender email address (default: noreply@gardeninghelper.com)
    - SMTP_FROM_NAME: Sender name (default: "Gardening Helper")

    Raises:
        ValueError: If required SMTP configuration is missing
    """

    def __init__(self):
        """
        Initialize SMTP provider with configuration from environment.

        Raises:
            ValueError: If SMTP_HOST, SMTP_USER, or SMTP_PASSWORD is missing
        """
        import os
        self.host = os.getenv('SMTP_HOST')
        self.port = int(os.getenv('SMTP_PORT', '587'))
        self.user = os.getenv('SMTP_USER')
        self.password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('SMTP_FROM_EMAIL', 'noreply@gardeninghelper.com')
        self.from_name = os.getenv('SMTP_FROM_NAME', 'Gardening Helper')

        if not all([self.host, self.user, self.password]):
            missing = []
            if not self.host:
                missing.append('SMTP_HOST')
            if not self.user:
                missing.append('SMTP_USER')
            if not self.password:
                missing.append('SMTP_PASSWORD')

            raise ValueError(
                f"SMTP configuration incomplete. Missing: {', '.join(missing)}. "
                "Set these environment variables or use DEBUG=True for development."
            )

        logger.info(f"SMTP configured: {self.host}:{self.port} (user: {self.user})")

    def send_password_reset_email(self, to_email: str, reset_url: str) -> bool:
        """
        Send password reset email via SMTP.

        Args:
            to_email: Recipient email address
            reset_url: Password reset URL with token

        Returns:
            True if email sent successfully

        Raises:
            Exception: If SMTP connection or sending fails (errors are NOT silently swallowed)
        """
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = 'Reset Your Gardening Helper Password'
            message['From'] = f"{self.from_name} <{self.from_email}>"
            message['To'] = to_email

            # Plain text version
            text = f"""
Hello,

You recently requested to reset your password for your Gardening Helper account.

Click the link below to reset your password:
{reset_url}

This link will expire in 1 hour.

If you didn't request this reset, please ignore this email. Your password will remain unchanged.

Best regards,
The Gardening Helper Team
            """.strip()

            # HTML version
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .button {{ display: inline-block; padding: 12px 24px; background-color: #4CAF50;
                   color: white; text-decoration: none; border-radius: 4px; margin: 20px 0; }}
        .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Reset Your Password</h2>
        <p>Hello,</p>
        <p>You recently requested to reset your password for your Gardening Helper account.</p>
        <p>Click the button below to reset your password:</p>
        <a href="{reset_url}" class="button">Reset Password</a>
        <p>Or copy and paste this link into your browser:</p>
        <p><a href="{reset_url}">{reset_url}</a></p>
        <p class="footer">
            This link will expire in 1 hour.<br>
            If you didn't request this reset, please ignore this email.
        </p>
    </div>
</body>
</html>
            """.strip()

            # Attach both versions
            part1 = MIMEText(text, 'plain')
            part2 = MIMEText(html, 'html')
            message.attach(part1)
            message.attach(part2)

            # Send email with detailed logging
            logger.info(f"Connecting to SMTP server {self.host}:{self.port}...")
            with smtplib.SMTP(self.host, self.port, timeout=10) as server:
                server.starttls()
                logger.info(f"Authenticating as {self.user}...")
                server.login(self.user, self.password)
                logger.info(f"Sending password reset email to {to_email}...")
                server.send_message(message)

            logger.info(f"✅ Password reset email sent successfully to {to_email}")
            return True

        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"SMTP authentication failed for {self.user}@{self.host}"
            logger.error(f"❌ {error_msg}: {e}")
            raise Exception(f"{error_msg}. Check SMTP_USER and SMTP_PASSWORD.") from e

        except smtplib.SMTPConnectError as e:
            error_msg = f"Cannot connect to SMTP server {self.host}:{self.port}"
            logger.error(f"❌ {error_msg}: {e}")
            raise Exception(f"{error_msg}. Check SMTP_HOST and SMTP_PORT.") from e

        except smtplib.SMTPException as e:
            error_msg = f"SMTP error while sending email to {to_email}"
            logger.error(f"❌ {error_msg}: {e}")
            raise Exception(f"{error_msg}: {str(e)}") from e

        except Exception as e:
            error_msg = f"Unexpected error sending email to {to_email}"
            logger.error(f"❌ {error_msg}: {e}")
            raise Exception(f"{error_msg}: {str(e)}") from e


class EmailService:
    """
    Email service factory that returns the appropriate provider.

    Modes:
    - Development (DEBUG=True): Uses ConsoleEmailProvider (no SMTP needed)
    - Production (DEBUG=False): Uses SMTPEmailProvider (requires SMTP config)
    """

    _provider: Optional[EmailProvider] = None
    _initialized: bool = False

    @classmethod
    def get_provider(cls) -> EmailProvider:
        """
        Get the configured email provider.

        Returns:
            EmailProvider instance (Console or SMTP based on DEBUG setting)

        Raises:
            ValueError: If production mode but SMTP is misconfigured

        Example:
            provider = EmailService.get_provider()
            success = provider.send_password_reset_email(email, reset_url)
        """
        if cls._provider is None:
            settings = get_settings()

            if settings.DEBUG:
                cls._provider = ConsoleEmailProvider()
                if not cls._initialized:
                    logger.warning("=" * 80)
                    logger.warning("⚠️  EMAIL DELIVERY: DEVELOPMENT MODE")
                    logger.warning("⚠️  Using ConsoleEmailProvider")
                    logger.warning("⚠️  Reset links will be printed to console/logs")
                    logger.warning("⚠️  NO REAL EMAILS WILL BE SENT")
                    logger.warning("=" * 80)
                    cls._initialized = True
            else:
                # Production mode - requires SMTP configuration
                try:
                    cls._provider = SMTPEmailProvider()
                    if not cls._initialized:
                        logger.info("=" * 80)
                        logger.info("✅ EMAIL DELIVERY: PRODUCTION MODE")
                        logger.info("✅ Using SMTPEmailProvider")
                        logger.info("✅ Real emails will be sent via SMTP")
                        logger.info("=" * 80)
                        cls._initialized = True
                except ValueError as e:
                    logger.error("=" * 80)
                    logger.error("❌ EMAIL DELIVERY: CONFIGURATION ERROR")
                    logger.error(f"❌ {str(e)}")
                    logger.error("=" * 80)
                    raise

        return cls._provider

    @classmethod
    def set_provider(cls, provider: EmailProvider) -> None:
        """
        Override the email provider (useful for testing).

        Args:
            provider: EmailProvider instance

        Example:
            EmailService.set_provider(MockEmailProvider())
        """
        cls._provider = provider

    @classmethod
    def reset_provider(cls) -> None:
        """Reset provider to None (force re-initialization)"""
        cls._provider = None
        cls._initialized = False
