"""Unit tests for the secure password generator module.

Tests cover password generation, entropy calculation, strength assessment,
and configuration validation.
"""

import pytest
from views.password_generator import (
    SecurePasswordVault,
    PasswordConfig,
    PasswordStrength,
    batch_generate,
)


class TestPasswordConfig:
    """Test password configuration validation and defaults."""
    
    def test_default_config(self) -> None:
        """Test that default config creates sane defaults."""
        config = PasswordConfig()
        assert config.length == 16
        assert config.include_uppercase is True
        assert config.include_lowercase is True
        assert config.include_digits is True
        assert config.include_special is True
    
    def test_config_validation_success(self) -> None:
        """Test that valid configurations pass validation."""
        config = PasswordConfig(length=12)
        is_valid, msg = config.validate()
        assert is_valid is True
        assert msg == ""
    
    def test_config_too_short(self) -> None:
        """Test that passwords shorter than 4 chars are rejected."""
        config = PasswordConfig(length=3)
        is_valid, msg = config.validate()
        assert is_valid is False
        assert "at least 4" in msg.lower()
    
    def test_config_too_long(self) -> None:
        """Test that passwords longer than 256 chars are rejected."""
        config = PasswordConfig(length=257)
        is_valid, msg = config.validate()
        assert is_valid is False
        assert "256" in msg
    
    def test_config_no_character_types(self) -> None:
        """Test that at least one character type must be selected."""
        config = PasswordConfig(
            include_uppercase=False,
            include_lowercase=False,
            include_digits=False,
            include_special=False,
        )
        is_valid, msg = config.validate()
        assert is_valid is False
        assert "at least one character type" in msg.lower()


class TestCharacterSetBuilding:
    """Test character set construction with various filters."""
    
    def test_all_character_types(self) -> None:
        """Test that all character types are included."""
        config = PasswordConfig(
            include_uppercase=True,
            include_lowercase=True,
            include_digits=True,
            include_special=True,
        )
        charset = SecurePasswordVault._build_character_set(config)
        
        # Should contain at least one from each type
        assert any(c.isupper() for c in charset)
        assert any(c.islower() for c in charset)
        assert any(c.isdigit() for c in charset)
        assert any(c in "!@#$%^&*()" for c in charset)
    
    def test_uppercase_only(self) -> None:
        """Test uppercase-only character set."""
        config = PasswordConfig(
            include_uppercase=True,
            include_lowercase=False,
            include_digits=False,
            include_special=False,
        )
        charset = SecurePasswordVault._build_character_set(config)
        assert charset == "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    def test_exclude_ambiguous(self) -> None:
        """Test that ambiguous characters are excluded."""
        config = PasswordConfig(exclude_ambiguous=True)
        charset = SecurePasswordVault._build_character_set(config)
        
        # These should not be in the charset
        ambiguous = "0O1lI|`"
        for char in ambiguous:
            assert char not in charset
    
    def test_exclude_similar(self) -> None:
        """Test that similar-looking characters are excluded."""
        config = PasswordConfig(
            include_uppercase=False,
            include_lowercase=True,
            include_digits=True,
            include_special=False,
            exclude_similar=True,
        )
        charset = SecurePasswordVault._build_character_set(config)
        
        # Similar pairs should be reduced
        # This is a basic check—the logic removes chars that look similar
        assert len(charset) > 0  # Should still have some characters


class TestPasswordGeneration:
    """Test password generation functionality."""
    
    def test_generate_default(self) -> None:
        """Test password generation with default config."""
        password = SecurePasswordVault.generate()
        assert len(password) == 16
        assert isinstance(password, str)
    
    def test_generate_custom_length(self) -> None:
        """Test password generation with custom length."""
        for length in [4, 8, 16, 32, 64]:
            password = SecurePasswordVault.generate(PasswordConfig(length=length))
            assert len(password) == length
    
    def test_generate_uniqueness(self) -> None:
        """Test that generated passwords are unique (extremely high probability)."""
        config = PasswordConfig()
        passwords = [SecurePasswordVault.generate(config) for _ in range(100)]
        
        # All passwords should be unique (with extremely high probability)
        assert len(set(passwords)) == len(passwords)
    
    def test_generate_includes_uppercase(self) -> None:
        """Test that uppercase characters appear when configured."""
        config = PasswordConfig(
            length=100,
            include_uppercase=True,
            include_lowercase=False,
            include_digits=False,
            include_special=False,
        )
        password = SecurePasswordVault.generate(config)
        assert all(c.isupper() for c in password)
    
    def test_generate_invalid_config_raises(self) -> None:
        """Test that invalid config raises ValueError."""
        config = PasswordConfig(length=1)
        with pytest.raises(ValueError):
            SecurePasswordVault.generate(config)
    
    def test_generate_no_character_types_raises(self) -> None:
        """Test that config with no character types raises ValueError."""
        config = PasswordConfig(
            include_uppercase=False,
            include_lowercase=False,
            include_digits=False,
            include_special=False,
        )
        with pytest.raises(ValueError):
            SecurePasswordVault.generate(config)


class TestEntropyCalculation:
    """Test Shannon entropy calculations."""
    
    def test_entropy_basic(self) -> None:
        """Test basic entropy calculation."""
        # With 26 letters, 1 character should have entropy = log2(26) ≈ 4.7
        entropy = SecurePasswordVault.calculate_entropy(1, 26)
        assert 4.5 < entropy < 5.0
    
    def test_entropy_doubles_with_length(self) -> None:
        """Test that entropy roughly doubles when length doubles (same charset)."""
        entropy_1 = SecurePasswordVault.calculate_entropy(10, 94)
        entropy_2 = SecurePasswordVault.calculate_entropy(20, 94)
        
        # entropy_2 should be approximately 2x entropy_1
        assert 1.9 < entropy_2 / entropy_1 < 2.1
    
    def test_entropy_zero_length(self) -> None:
        """Test that zero length returns zero entropy."""
        entropy = SecurePasswordVault.calculate_entropy(0, 94)
        assert entropy == 0.0
    
    def test_entropy_zero_charset(self) -> None:
        """Test that zero charset size returns zero entropy."""
        entropy = SecurePasswordVault.calculate_entropy(10, 0)
        assert entropy == 0.0


class TestStrengthAssessment:
    """Test password strength assessment."""
    
    def test_strength_weak(self) -> None:
        """Test weak password assessment."""
        config = PasswordConfig(length=4, include_special=False)
        password = SecurePasswordVault.generate(config)
        strength = SecurePasswordVault.assess_strength(password, config)
        assert strength == PasswordStrength.WEAK
    
    def test_strength_strong(self) -> None:
        """Test strong password assessment."""
        config = PasswordConfig(length=32)
        password = SecurePasswordVault.generate(config)
        strength = SecurePasswordVault.assess_strength(password, config)
        assert strength in [PasswordStrength.STRONG, PasswordStrength.LEGENDARY]
    
    def test_strength_legendary(self) -> None:
        """Test legendary password assessment."""
        config = PasswordConfig(length=64)
        password = SecurePasswordVault.generate(config)
        strength = SecurePasswordVault.assess_strength(password, config)
        assert strength == PasswordStrength.LEGENDARY


class TestBatchGeneration:
    """Test batch password generation."""
    
    def test_batch_generate_count(self) -> None:
        """Test that batch generation returns correct number of passwords."""
        for count in [1, 5, 10, 50]:
            passwords = batch_generate(count)
            assert len(passwords) == count
    
    def test_batch_generate_invalid_count(self) -> None:
        """Test that invalid count raises ValueError."""
        with pytest.raises(ValueError):
            batch_generate(0)
        
        with pytest.raises(ValueError):
            batch_generate(-1)
    
    def test_batch_generate_uniqueness(self) -> None:
        """Test that batch-generated passwords are unique."""
        passwords = batch_generate(100)
        assert len(set(passwords)) == len(passwords)
    
    def test_batch_generate_with_config(self) -> None:
        """Test batch generation with custom config."""
        config = PasswordConfig(length=20)
        passwords = batch_generate(5, config)
        
        assert len(passwords) == 5
        assert all(len(p) == 20 for p in passwords)
