"""
Unit Tests for Credentials Module
==================================

Tests for common/credentials.py module.
"""

import pytest
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from common.credentials import (
    get_env_var,
    get_aivisual_credentials,
    get_file_server_credentials,
    get_alphaville_credentials,
    get_selenium_config,
    get_logging_config,
    validate_credentials
)


# ============================================================================
# Test get_env_var
# ============================================================================

class TestGetEnvVar:
    """Tests for get_env_var function."""

    def test_get_existing_env_var(self, monkeypatch):
        """Test getting an existing environment variable."""
        monkeypatch.setenv('TEST_VAR', 'test_value')

        value = get_env_var('TEST_VAR')

        assert value == 'test_value'

    def test_get_missing_required_env_var_raises(self, monkeypatch):
        """Test that missing required env var raises ValueError."""
        monkeypatch.delenv('MISSING_VAR', raising=False)

        with pytest.raises(ValueError) as exc_info:
            get_env_var('MISSING_VAR', required=True)

        assert 'MISSING_VAR' in str(exc_info.value)
        assert 'not found' in str(exc_info.value)

    def test_get_missing_optional_env_var_returns_default(self, monkeypatch):
        """Test that missing optional env var returns default."""
        monkeypatch.delenv('OPTIONAL_VAR', raising=False)

        value = get_env_var('OPTIONAL_VAR', default='default_value', required=False)

        assert value == 'default_value'

    def test_get_missing_optional_env_var_returns_none(self, monkeypatch):
        """Test that missing optional env var returns None if no default."""
        monkeypatch.delenv('OPTIONAL_VAR', raising=False)

        value = get_env_var('OPTIONAL_VAR', required=False)

        assert value is None


# ============================================================================
# Test AIVisual Credentials
# ============================================================================

@pytest.mark.security
class TestGetAIVisualCredentials:
    """Tests for get_aivisual_credentials function."""

    def test_get_aivisual_credentials_success(self, test_env_vars):
        """Test successful retrieval of AIVisual credentials."""
        username, password = get_aivisual_credentials()

        assert username == 'test@example.com'
        assert password == 'test_password_123'

    def test_get_aivisual_credentials_missing_user(self, monkeypatch):
        """Test error when AIVISUAL_USER is missing."""
        monkeypatch.delenv('AIVISUAL_USER', raising=False)
        monkeypatch.setenv('AIVISUAL_PASS', 'test_pass')

        with pytest.raises(ValueError) as exc_info:
            get_aivisual_credentials()

        assert 'AIVISUAL_USER' in str(exc_info.value)

    def test_get_aivisual_credentials_missing_password(self, monkeypatch):
        """Test error when AIVISUAL_PASS is missing."""
        monkeypatch.setenv('AIVISUAL_USER', 'test@example.com')
        monkeypatch.delenv('AIVISUAL_PASS', raising=False)

        with pytest.raises(ValueError) as exc_info:
            get_aivisual_credentials()

        assert 'AIVISUAL_PASS' in str(exc_info.value)


# ============================================================================
# Test File Server Credentials
# ============================================================================

@pytest.mark.security
class TestGetFileServerCredentials:
    """Tests for get_file_server_credentials function."""

    def test_get_file_server_credentials_success(self, test_env_vars, monkeypatch):
        """Test successful retrieval of file server credentials."""
        monkeypatch.setenv('FILE_SERVER_URL', 'http://test.server.com:8080')

        username, password, url = get_file_server_credentials()

        assert username == 'test@example.com'
        assert password == 'test_password_456'
        assert url == 'http://test.server.com:8080'

    def test_get_file_server_credentials_default_url(self, test_env_vars, monkeypatch):
        """Test that default URL is used when not specified."""
        monkeypatch.delenv('FILE_SERVER_URL', raising=False)

        username, password, url = get_file_server_credentials()

        assert url == 'http://35.209.243.66:11967'

    def test_get_file_server_credentials_missing_user(self, monkeypatch):
        """Test error when FILE_SERVER_USER is missing."""
        monkeypatch.delenv('FILE_SERVER_USER', raising=False)
        monkeypatch.setenv('FILE_SERVER_PASS', 'test_pass')

        with pytest.raises(ValueError) as exc_info:
            get_file_server_credentials()

        assert 'FILE_SERVER_USER' in str(exc_info.value)


# ============================================================================
# Test Alphaville Credentials
# ============================================================================

@pytest.mark.security
class TestGetAlphavilleCredentials:
    """Tests for get_alphaville_credentials function."""

    def test_get_alphaville_credentials_success(self, test_env_vars, monkeypatch):
        """Test successful retrieval of Alphaville credentials."""
        monkeypatch.setenv('ALPHAVILLE_URL', 'https://custom.alphaville.com')

        username, password, url = get_alphaville_credentials()

        assert username == 'test_user'
        assert password == 'test_password_789'
        assert url == 'https://custom.alphaville.com'

    def test_get_alphaville_credentials_default_url(self, test_env_vars, monkeypatch):
        """Test that default URL is used when not specified."""
        monkeypatch.delenv('ALPHAVILLE_URL', raising=False)

        username, password, url = get_alphaville_credentials()

        expected_url = 'https://recupera.alphaville.com.br/Recupera/login/login.aspx'
        assert url == expected_url

    def test_get_alphaville_credentials_missing_password(self, monkeypatch):
        """Test error when ALPHAVILLE_PASS is missing."""
        monkeypatch.setenv('ALPHAVILLE_USER', 'test_user')
        monkeypatch.delenv('ALPHAVILLE_PASS', raising=False)

        with pytest.raises(ValueError) as exc_info:
            get_alphaville_credentials()

        assert 'ALPHAVILLE_PASS' in str(exc_info.value)


# ============================================================================
# Test Selenium Configuration
# ============================================================================

class TestGetSeleniumConfig:
    """Tests for get_selenium_config function."""

    def test_get_selenium_config_defaults(self, monkeypatch):
        """Test default Selenium configuration."""
        monkeypatch.delenv('SELENIUM_HEADLESS', raising=False)
        monkeypatch.delenv('SELENIUM_TIMEOUT', raising=False)

        config = get_selenium_config()

        assert config['headless'] is True
        assert config['timeout'] == 30

    def test_get_selenium_config_custom(self, monkeypatch):
        """Test custom Selenium configuration."""
        monkeypatch.setenv('SELENIUM_HEADLESS', 'false')
        monkeypatch.setenv('SELENIUM_TIMEOUT', '60')

        config = get_selenium_config()

        assert config['headless'] is False
        assert config['timeout'] == 60

    @pytest.mark.parametrize("headless_value,expected", [
        ('true', True),
        ('True', True),
        ('1', True),
        ('yes', True),
        ('on', True),
        ('false', False),
        ('False', False),
        ('0', False),
        ('no', False),
        ('off', False),
    ])
    def test_selenium_headless_boolean_parsing(self, monkeypatch, headless_value, expected):
        """Test parsing of various boolean values for headless mode."""
        monkeypatch.setenv('SELENIUM_HEADLESS', headless_value)

        config = get_selenium_config()

        assert config['headless'] == expected


# ============================================================================
# Test Logging Configuration
# ============================================================================

class TestGetLoggingConfig:
    """Tests for get_logging_config function."""

    def test_get_logging_config_defaults(self, monkeypatch):
        """Test default logging configuration."""
        monkeypatch.delenv('LOG_LEVEL', raising=False)
        monkeypatch.delenv('LOG_FILE', raising=False)

        config = get_logging_config()

        assert config['level'] == 'INFO'
        assert config['file'] == 'logs/application.log'

    def test_get_logging_config_custom(self, monkeypatch):
        """Test custom logging configuration."""
        monkeypatch.setenv('LOG_LEVEL', 'debug')
        monkeypatch.setenv('LOG_FILE', '/var/log/myapp.log')

        config = get_logging_config()

        assert config['level'] == 'DEBUG'  # Should be uppercase
        assert config['file'] == '/var/log/myapp.log'

    @pytest.mark.parametrize("log_level", ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
    def test_logging_valid_levels(self, monkeypatch, log_level):
        """Test all valid logging levels."""
        monkeypatch.setenv('LOG_LEVEL', log_level.lower())

        config = get_logging_config()

        assert config['level'] == log_level.upper()


# ============================================================================
# Test Validation
# ============================================================================

@pytest.mark.security
class TestValidateCredentials:
    """Tests for validate_credentials function."""

    def test_validate_credentials_success(self, test_env_vars, monkeypatch, capsys):
        """Test successful credential validation."""
        # Set all required env vars
        monkeypatch.setenv('AIVISUAL_USER', 'test@example.com')
        monkeypatch.setenv('AIVISUAL_PASS', 'password123')
        monkeypatch.setenv('FILE_SERVER_USER', 'test@example.com')
        monkeypatch.setenv('FILE_SERVER_PASS', 'password456')
        monkeypatch.setenv('ALPHAVILLE_USER', 'testuser')
        monkeypatch.setenv('ALPHAVILLE_PASS', 'password789')

        result = validate_credentials()

        assert result is True

        captured = capsys.readouterr()
        assert 'Validating credentials' in captured.out
        assert 'validated successfully' in captured.out

    def test_validate_credentials_missing(self, monkeypatch, capsys):
        """Test credential validation with missing values."""
        # Clear all credentials
        for var in ['AIVISUAL_USER', 'AIVISUAL_PASS', 'FILE_SERVER_USER',
                    'FILE_SERVER_PASS', 'ALPHAVILLE_USER', 'ALPHAVILLE_PASS']:
            monkeypatch.delenv(var, raising=False)

        result = validate_credentials()

        assert result is False

        captured = capsys.readouterr()
        assert 'Credential validation failed' in captured.out


# ============================================================================
# Integration Tests
# ============================================================================

class TestCredentialsIntegration:
    """Integration tests for credentials module."""

    def test_all_credentials_from_env_file(self, temp_dir, monkeypatch):
        """Test loading all credentials from .env file."""
        # Create a .env file
        env_file = temp_dir / '.env'
        env_content = """
AIVISUAL_USER=user@example.com
AIVISUAL_PASS=pass123
FILE_SERVER_USER=server@example.com
FILE_SERVER_PASS=pass456
FILE_SERVER_URL=http://custom.server.com
ALPHAVILLE_USER=alphauser
ALPHAVILLE_PASS=pass789
ALPHAVILLE_URL=https://custom.alphaville.com
SELENIUM_HEADLESS=false
SELENIUM_TIMEOUT=45
LOG_LEVEL=DEBUG
LOG_FILE=/tmp/test.log
"""
        env_file.write_text(env_content.strip())

        # Change to temp directory
        monkeypatch.chdir(temp_dir)

        # Load from .env file
        from common.credentials import load_env_file
        load_env_file('.env')

        # Verify all values
        aiv_user, aiv_pass = get_aivisual_credentials()
        assert aiv_user == 'user@example.com'
        assert aiv_pass == 'pass123'

        fs_user, fs_pass, fs_url = get_file_server_credentials()
        assert fs_user == 'server@example.com'
        assert fs_pass == 'pass456'
        assert fs_url == 'http://custom.server.com'

        alpha_user, alpha_pass, alpha_url = get_alphaville_credentials()
        assert alpha_user == 'alphauser'
        assert alpha_pass == 'pass789'

        selenium_config = get_selenium_config()
        assert selenium_config['headless'] is False
        assert selenium_config['timeout'] == 45

        log_config = get_logging_config()
        assert log_config['level'] == 'DEBUG'
        assert log_config['file'] == '/tmp/test.log'


# ============================================================================
# Security Tests
# ============================================================================

@pytest.mark.security
class TestCredentialsSecurity:
    """Security-related tests for credentials."""

    def test_credentials_not_logged(self, test_env_vars, capsys):
        """Test that actual credentials are not printed in validation."""
        validate_credentials()

        captured = capsys.readouterr()

        # Should NOT contain full credentials
        assert 'test_password_123' not in captured.out
        assert 'test_password_456' not in captured.out
        assert 'test_password_789' not in captured.out

        # Should contain masked versions
        assert '...' in captured.out

    def test_error_messages_dont_reveal_credentials(self, monkeypatch):
        """Test that error messages don't reveal credential values."""
        monkeypatch.setenv('AIVISUAL_USER', 'secret_user')
        monkeypatch.delenv('AIVISUAL_PASS', raising=False)

        try:
            get_aivisual_credentials()
        except ValueError as e:
            error_msg = str(e)

            # Should NOT contain the username
            assert 'secret_user' not in error_msg

            # Should contain the variable name
            assert 'AIVISUAL_PASS' in error_msg
