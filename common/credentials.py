#!/usr/bin/env python3
"""
Credentials Manager
===================

Secure credential management using environment variables.
This module provides a centralized way to load credentials from environment
variables instead of hardcoding them in source code.

Usage:
    from common.credentials import get_aivisual_credentials, get_file_server_credentials

    # Get AIVisual credentials
    username, password = get_aivisual_credentials()

    # Get File Server credentials
    user, passwd, url = get_file_server_credentials()
"""

import os
import sys
from pathlib import Path
from typing import Tuple, Optional


def load_env_file(env_file: str = '.env') -> None:
    """
    Load environment variables from .env file if it exists.

    Args:
        env_file: Path to .env file (default: '.env')
    """
    try:
        from dotenv import load_dotenv

        # Try to find .env in current directory or parent directories
        current_dir = Path.cwd()
        for parent in [current_dir] + list(current_dir.parents):
            env_path = parent / env_file
            if env_path.exists():
                load_dotenv(env_path)
                print(f"✅ Loaded environment variables from: {env_path}")
                return

        print(f"⚠️  No .env file found. Using system environment variables.")

    except ImportError:
        print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")
        print("    Using system environment variables only.")


def get_env_var(var_name: str, default: Optional[str] = None, required: bool = True) -> str:
    """
    Get environment variable with error handling.

    Args:
        var_name: Name of the environment variable
        default: Default value if not found
        required: If True, raise error when variable not found

    Returns:
        Value of the environment variable

    Raises:
        ValueError: If variable not found and required=True
    """
    value = os.getenv(var_name, default)

    if value is None and required:
        raise ValueError(
            f"❌ Environment variable '{var_name}' not found!\n"
            f"   Please set it in your .env file or export it:\n"
            f"   export {var_name}=your_value\n"
            f"   Or copy .env.example to .env and fill in your credentials."
        )

    return value


def get_aivisual_credentials() -> Tuple[str, str]:
    """
    Get AIVisual dashboard credentials from environment variables.

    Returns:
        Tuple of (username, password)

    Raises:
        ValueError: If credentials not found in environment

    Environment Variables:
        AIVISUAL_USER: Email for AIVisual login
        AIVISUAL_PASS: Password for AIVisual login
    """
    load_env_file()

    username = get_env_var('AIVISUAL_USER', required=True)
    password = get_env_var('AIVISUAL_PASS', required=True)

    return username, password


def get_file_server_credentials() -> Tuple[str, str, str]:
    """
    Get file server credentials from environment variables.

    Returns:
        Tuple of (username, password, server_url)

    Raises:
        ValueError: If credentials not found in environment

    Environment Variables:
        FILE_SERVER_USER: Email for file server login
        FILE_SERVER_PASS: Password for file server login
        FILE_SERVER_URL: URL of the file server (default: http://35.209.243.66:11967)
    """
    load_env_file()

    username = get_env_var('FILE_SERVER_USER', required=True)
    password = get_env_var('FILE_SERVER_PASS', required=True)
    url = get_env_var('FILE_SERVER_URL', default='http://35.209.243.66:11967', required=False)

    return username, password, url


def get_alphaville_credentials() -> Tuple[str, str, str]:
    """
    Get Alphaville Recupera credentials from environment variables.

    Returns:
        Tuple of (username, password, url)

    Raises:
        ValueError: If credentials not found in environment

    Environment Variables:
        ALPHAVILLE_USER: Username for Alphaville login
        ALPHAVILLE_PASS: Password for Alphaville login
        ALPHAVILLE_URL: URL of Alphaville system (default: https://recupera.alphaville.com.br/Recupera/login/login.aspx)
    """
    load_env_file()

    username = get_env_var('ALPHAVILLE_USER', required=True)
    password = get_env_var('ALPHAVILLE_PASS', required=True)
    url = get_env_var(
        'ALPHAVILLE_URL',
        default='https://recupera.alphaville.com.br/Recupera/login/login.aspx',
        required=False
    )

    return username, password, url


def get_selenium_config() -> dict:
    """
    Get Selenium configuration from environment variables.

    Returns:
        Dictionary with Selenium configuration

    Environment Variables:
        SELENIUM_HEADLESS: Run browser in headless mode (default: true)
        SELENIUM_TIMEOUT: Default timeout in seconds (default: 30)
    """
    load_env_file()

    headless_str = get_env_var('SELENIUM_HEADLESS', default='true', required=False)
    timeout_str = get_env_var('SELENIUM_TIMEOUT', default='30', required=False)

    return {
        'headless': headless_str.lower() in ('true', '1', 'yes', 'on'),
        'timeout': int(timeout_str)
    }


def get_logging_config() -> dict:
    """
    Get logging configuration from environment variables.

    Returns:
        Dictionary with logging configuration

    Environment Variables:
        LOG_LEVEL: Logging level (default: INFO)
        LOG_FILE: Log file path (default: logs/application.log)
    """
    load_env_file()

    level = get_env_var('LOG_LEVEL', default='INFO', required=False)
    log_file = get_env_var('LOG_FILE', default='logs/application.log', required=False)

    return {
        'level': level.upper(),
        'file': log_file
    }


def validate_credentials() -> bool:
    """
    Validate that all required credentials are available.

    Returns:
        True if all credentials are valid, False otherwise
    """
    try:
        print("🔍 Validating credentials...")

        # Check AIVisual credentials
        user, passwd = get_aivisual_credentials()
        print(f"✅ AIVisual credentials: {user[:3]}...@{user.split('@')[1] if '@' in user else 'unknown'}")

        # Check File Server credentials
        user, passwd, url = get_file_server_credentials()
        print(f"✅ File Server credentials: {user[:3]}...@{user.split('@')[1] if '@' in user else 'unknown'}")
        print(f"   Server URL: {url}")

        # Check Alphaville credentials
        user, passwd, url = get_alphaville_credentials()
        print(f"✅ Alphaville credentials: {user[:3]}...")
        print(f"   System URL: {url}")

        print("\n✅ All credentials validated successfully!")
        return True

    except ValueError as e:
        print(f"\n❌ Credential validation failed: {e}")
        return False


if __name__ == "__main__":
    """
    Run credential validation when script is executed directly.
    """
    print("="*80)
    print("Credential Validation Tool")
    print("="*80)

    if validate_credentials():
        sys.exit(0)
    else:
        print("\n💡 Quick Setup:")
        print("   1. Copy .env.example to .env")
        print("   2. Edit .env and add your credentials")
        print("   3. Run this script again to validate")
        sys.exit(1)
