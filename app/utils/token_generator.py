"""Cryptographically secure token generation and verification"""
import secrets
import hashlib
from typing import Tuple


class TokenGenerator:
    """
    Secure token generation and hashing for password reset.

    Security considerations:
    - Uses secrets module (cryptographically strong random number generator)
    - Tokens are 32 bytes (256 bits) - URL-safe
    - Tokens are hashed using SHA-256 before storage
    - Raw tokens are never stored in the database
    """

    @staticmethod
    def generate_token() -> str:
        """
        Generate a cryptographically secure random token.

        Returns:
            URL-safe random token string (43 characters)

        Example:
            "3x7k9mQpR2nV8yB4cF6hJ1sL5tN0wPqE7uG2aD9zX5C"
        """
        # secrets.token_urlsafe generates a random URL-safe token
        # 32 bytes = 256 bits of entropy
        return secrets.token_urlsafe(32)

    @staticmethod
    def hash_token(token: str) -> str:
        """
        Hash a token using SHA-256 for secure storage.

        Args:
            token: The raw token to hash

        Returns:
            Hexadecimal string representation of the hash (64 characters)

        Security note:
            - One-way hash function (cannot reverse)
            - Same token always produces same hash (for verification)
            - Different tokens produce different hashes
        """
        return hashlib.sha256(token.encode('utf-8')).hexdigest()

    @staticmethod
    def generate_and_hash() -> Tuple[str, str]:
        """
        Generate a new token and return both raw and hashed versions.

        Returns:
            Tuple of (raw_token, hashed_token)
            - raw_token: Send to user (email/console)
            - hashed_token: Store in database

        Example:
            raw_token, token_hash = TokenGenerator.generate_and_hash()
            # Send raw_token in reset link
            # Store token_hash in database
        """
        raw_token = TokenGenerator.generate_token()
        token_hash = TokenGenerator.hash_token(raw_token)
        return raw_token, token_hash

    @staticmethod
    def verify_token(raw_token: str, stored_hash: str) -> bool:
        """
        Verify that a raw token matches the stored hash.

        Args:
            raw_token: The token provided by the user
            stored_hash: The hashed token from the database

        Returns:
            True if the token matches, False otherwise

        Example:
            if TokenGenerator.verify_token(user_provided_token, db_token.token_hash):
                # Token is valid
                reset_password()
        """
        computed_hash = TokenGenerator.hash_token(raw_token)
        # Use secrets.compare_digest to prevent timing attacks
        return secrets.compare_digest(computed_hash, stored_hash)
