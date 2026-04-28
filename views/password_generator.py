"""Secure password generation module following NIST and industry best practices.

This module provides cryptographically secure password generation with
configurable character sets and lengths. It's designed to produce passwords
with high entropy that meet modern security standards.

References:
  - NIST SP 800-63B: https://pages.nist.gov/800-63-3/sp800-63b.html
  - OWASP Password Guidelines: https://cheatsheetseries.owasp.org/
"""

import secrets
import string
from dataclasses import dataclass
from enum import Enum


class PasswordStrength(Enum):
    """The one... to rule them all. Password strength levels."""
    WEAK = "weak"
    FAIR = "fair"
    GOOD = "good"
    STRONG = "strong"
    LEGENDARY = "legendary"


@dataclass
class PasswordConfig:
    """Configuration for the Matrix-breaking password generator.
    
    Think of this as your exit pill—customize your escape route.
    """
    length: int = 16
    """Password length in characters. NIST recommends 12+ for user-created passwords."""
    
    include_uppercase: bool = True
    """Include A-Z. The red pill always comes first."""
    
    include_lowercase: bool = True
    """Include a-z. The blue pill is always an option."""
    
    include_digits: bool = True
    """Include 0-9. Let's count all the ones and zeros."""
    
    include_special: bool = True
    """Include !@#$%^&*. Go full Thanos snap."""
    
    exclude_ambiguous: bool = False
    """Exclude ambiguous characters (0/O, 1/l/I, etc.). For the colorblind in spirit."""
    
    exclude_similar: bool = False
    """Exclude visually similar characters (i/l/1, o/0/O, etc.)."""
    
    def validate(self) -> tuple[bool, str]:
        """Validate configuration. Return (is_valid, error_message)."""
        # Welcome to the real world, Neo
        if self.length < 4:
            return False, "Password length must be at least 4 characters. Choose the red pill."
        
        if self.length > 256:
            return False, "Password length cannot exceed 256 characters. Even the Matrix has limits."
        
        if not any([
            self.include_uppercase,
            self.include_lowercase,
            self.include_digits,
            self.include_special,
        ]):
            return False, "At least one character type must be included. You must choose something."
        
        return True, ""


class SecurePasswordVault:
    """The Avengers of password generation. Assemble!
    
    This class handles cryptographically secure password generation
    using Python's secrets module for high entropy.
    """
    
    # Character sets - building our arsenal
    UPPERCASE = string.ascii_uppercase
    LOWERCASE = string.ascii_lowercase
    DIGITS = string.digits
    SPECIAL = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    # The ambiguous characters we might want to dodge, like bullets in slow-mo
    AMBIGUOUS_CHARS = set("0O1lI|`")
    SIMILAR_PAIRS = {
        '0': set('O'),
        'O': set('0'),
        '1': set('il|'),
        'i': set('1l|'),
        'l': set('1i|'),
        '|': set('1il'),
    }
    
    @staticmethod
    def _build_character_set(config: PasswordConfig) -> str:
        """Resurrect the character set from dead code and make it whole again."""
        charset = ""
        
        if config.include_uppercase:
            charset += SecurePasswordVault.UPPERCASE
        
        if config.include_lowercase:
            charset += SecurePasswordVault.LOWERCASE
        
        if config.include_digits:
            charset += SecurePasswordVault.DIGITS
        
        if config.include_special:
            charset += SecurePasswordVault.SPECIAL
        
        # Apply the filters - dodge what we don't need
        if config.exclude_ambiguous:
            charset = "".join(c for c in charset if c not in SecurePasswordVault.AMBIGUOUS_CHARS)
        
        if config.exclude_similar:
            charset = "".join(
                c for c in charset
                if c not in SecurePasswordVault.SIMILAR_PAIRS.get(c, set())
            )
        
        return charset
    
    @staticmethod
    def generate(config: PasswordConfig | None = None) -> str:
        """Generate a cryptographically secure password.
        
        This is your One. Your ticket out of here.
        
        Args:
            config: PasswordConfig instance. Defaults to recommended settings.
            
        Returns:
            A secure, random password string.
            
        Raises:
            ValueError: If configuration is invalid.
        """
        if config is None:
            config = PasswordConfig()
        
        is_valid, error_msg = config.validate()
        if not is_valid:
            raise ValueError(error_msg)
        
        charset = SecurePasswordVault._build_character_set(config)
        
        if not charset:
            raise ValueError("Character set is empty after filtering. Something went wrong.")
        
        # Use secrets for cryptographically secure randomness
        # Hello, entropy. We've been expecting you.
        password = "".join(secrets.choice(charset) for _ in range(config.length))
        
        return password
    
    @staticmethod
    def calculate_entropy(password_length: int, charset_size: int) -> float:
        """Calculate Shannon entropy of a password in bits.
        
        Entropy = log2(charset_size ^ length)
        Higher entropy = harder to crack. It's that simple.
        """
        import math
        if charset_size <= 0 or password_length <= 0:
            return 0.0
        return math.log2(charset_size ** password_length)
    
    @staticmethod
    def assess_strength(password: str, config: PasswordConfig | None = None) -> PasswordStrength:
        """Assess password strength based on entropy and composition.
        
        Uses NIST and industry-standard criteria to determine strength.
        """
        if config is None:
            config = PasswordConfig()
        
        charset_size = len(SecurePasswordVault._build_character_set(config))
        entropy = SecurePasswordVault.calculate_entropy(len(password), charset_size)
        
        # Entropy thresholds (in bits) - the power tiers of password strength
        if entropy < 30:
            return PasswordStrength.WEAK
        elif entropy < 50:
            return PasswordStrength.FAIR
        elif entropy < 70:
            return PasswordStrength.GOOD
        elif entropy < 90:
            return PasswordStrength.STRONG
        else:
            return PasswordStrength.LEGENDARY


def batch_generate(
    count: int,
    config: PasswordConfig | None = None,
) -> list[str]:
    """Generate multiple passwords at once. Assemble the squad!
    
    Args:
        count: Number of passwords to generate.
        config: PasswordConfig instance. Defaults to recommended settings.
        
    Returns:
        A list of secure passwords.
        
    Raises:
        ValueError: If count < 1 or configuration is invalid.
    """
    if count < 1:
        raise ValueError("Count must be at least 1. You must generate at least one password.")
    
    if config is None:
        config = PasswordConfig()
    
    return [SecurePasswordVault.generate(config) for _ in range(count)]
