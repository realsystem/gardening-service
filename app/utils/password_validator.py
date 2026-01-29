"""Password strength validation"""
import re
from typing import List, Optional


class PasswordValidator:
    """
    Password strength validation with configurable rules.

    Default requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """

    # Minimum password length
    MIN_LENGTH = 8

    # Password patterns
    UPPERCASE_PATTERN = re.compile(r'[A-Z]')
    LOWERCASE_PATTERN = re.compile(r'[a-z]')
    DIGIT_PATTERN = re.compile(r'\d')
    SPECIAL_CHAR_PATTERN = re.compile(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\;/`~]')

    @classmethod
    def validate(cls, password: str) -> tuple[bool, Optional[List[str]]]:
        """
        Validate password strength.

        Args:
            password: The password to validate

        Returns:
            Tuple of (is_valid, error_messages)
            - is_valid: True if password meets all requirements
            - error_messages: List of validation errors (None if valid)

        Example:
            is_valid, errors = PasswordValidator.validate("weak")
            if not is_valid:
                print(errors)  # ['Password must be at least 8 characters', ...]
        """
        errors = []

        if not password:
            return False, ["Password is required"]

        # Check length
        if len(password) < cls.MIN_LENGTH:
            errors.append(f"Password must be at least {cls.MIN_LENGTH} characters")

        # Check for uppercase letter
        if not cls.UPPERCASE_PATTERN.search(password):
            errors.append("Password must contain at least one uppercase letter")

        # Check for lowercase letter
        if not cls.LOWERCASE_PATTERN.search(password):
            errors.append("Password must contain at least one lowercase letter")

        # Check for digit
        if not cls.DIGIT_PATTERN.search(password):
            errors.append("Password must contain at least one digit")

        # Check for special character
        if not cls.SPECIAL_CHAR_PATTERN.search(password):
            errors.append("Password must contain at least one special character (!@#$%^&*...)")

        if errors:
            return False, errors

        return True, None

    @classmethod
    def get_requirements(cls) -> List[str]:
        """
        Get list of password requirements for display to users.

        Returns:
            List of requirement strings

        Example:
            requirements = PasswordValidator.get_requirements()
            for req in requirements:
                print(f"- {req}")
        """
        return [
            f"At least {cls.MIN_LENGTH} characters",
            "At least one uppercase letter (A-Z)",
            "At least one lowercase letter (a-z)",
            "At least one digit (0-9)",
            "At least one special character (!@#$%^&*...)"
        ]

    @classmethod
    def validate_or_raise(cls, password: str) -> None:
        """
        Validate password and raise ValueError if invalid.

        Args:
            password: The password to validate

        Raises:
            ValueError: If password doesn't meet requirements

        Example:
            try:
                PasswordValidator.validate_or_raise(user_password)
            except ValueError as e:
                return {"error": str(e)}
        """
        is_valid, errors = cls.validate(password)
        if not is_valid:
            raise ValueError("; ".join(errors))
