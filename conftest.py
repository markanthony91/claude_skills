"""
Pytest Configuration and Shared Fixtures
=========================================

This file contains shared pytest fixtures and configuration for all test modules.
Fixtures defined here are automatically available to all tests.
"""

import pytest
import os
import tempfile
import shutil
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
from typing import Generator, Dict, Any


# ============================================================================
# Environment Setup Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def test_env_vars():
    """Set up test environment variables."""
    test_vars = {
        'AIVISUAL_USER': 'test@example.com',
        'AIVISUAL_PASS': 'test_password_123',
        'FILE_SERVER_USER': 'test@example.com',
        'FILE_SERVER_PASS': 'test_password_456',
        'ALPHAVILLE_USER': 'test_user',
        'ALPHAVILLE_PASS': 'test_password_789',
    }

    # Store original values
    original_values = {}
    for key in test_vars:
        original_values[key] = os.environ.get(key)
        os.environ[key] = test_vars[key]

    yield test_vars

    # Restore original values
    for key, value in original_values.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    tmp_dir = tempfile.mkdtemp()
    yield Path(tmp_dir)
    shutil.rmtree(tmp_dir, ignore_errors=True)


@pytest.fixture
def sample_image_path(temp_dir: Path) -> Path:
    """Create a sample image file for testing."""
    # Create a minimal valid JPEG file (1x1 pixel)
    jpeg_header = bytes([
        0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46,
        0x49, 0x46, 0x00, 0x01, 0x01, 0x00, 0x00, 0x01,
        0x00, 0x01, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43,
        0x00, 0x08, 0x06, 0x06, 0x07, 0x06, 0x05, 0x08,
        0x07, 0x07, 0x07, 0x09, 0x09, 0x08, 0x0A, 0x0C,
        0x14, 0x0D, 0x0C, 0x0B, 0x0B, 0x0C, 0x19, 0x12,
        0x13, 0x0F, 0x14, 0x1D, 0x1A, 0x1F, 0x1E, 0x1D,
        0x1A, 0x1C, 0x1C, 0x20, 0x24, 0x2E, 0x27, 0x20,
        0x22, 0x2C, 0x23, 0x1C, 0x1C, 0x28, 0x37, 0x29,
        0x2C, 0x30, 0x31, 0x34, 0x34, 0x34, 0x1F, 0x27,
        0x39, 0x3D, 0x38, 0x32, 0x3C, 0x2E, 0x33, 0x34,
        0x32, 0xFF, 0xC0, 0x00, 0x0B, 0x08, 0x00, 0x01,
        0x00, 0x01, 0x01, 0x01, 0x11, 0x00, 0xFF, 0xC4,
        0x00, 0x14, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0xFF, 0xDA, 0x00, 0x08,
        0x01, 0x01, 0x00, 0x00, 0x3F, 0x00, 0xD2, 0xCF,
        0x20, 0xFF, 0xD9
    ])

    image_path = temp_dir / "test_image.jpg"
    image_path.write_bytes(jpeg_header)
    return image_path


# ============================================================================
# Selenium Mocks
# ============================================================================

@pytest.fixture
def mock_selenium_driver():
    """Create a mock Selenium WebDriver."""
    driver = MagicMock()

    # Mock common methods
    driver.get.return_value = None
    driver.quit.return_value = None
    driver.close.return_value = None
    driver.refresh.return_value = None

    # Mock element finding
    mock_element = MagicMock()
    mock_element.click.return_value = None
    mock_element.send_keys.return_value = None
    mock_element.get_attribute.return_value = "mock_attribute"
    mock_element.text = "Mock Element Text"

    driver.find_element.return_value = mock_element
    driver.find_elements.return_value = [mock_element]

    # Mock page source
    driver.page_source = "<html><body>Mock Page</body></html>"

    # Mock screenshot
    driver.get_screenshot_as_file.return_value = True
    driver.save_screenshot.return_value = True

    return driver


@pytest.fixture
def mock_selenium_wait():
    """Create a mock Selenium WebDriverWait."""
    wait = MagicMock()
    mock_element = MagicMock()
    mock_element.click.return_value = None
    wait.until.return_value = mock_element
    return wait


@pytest.fixture
def selenium_test_env(mock_selenium_driver, mock_selenium_wait):
    """Complete Selenium test environment."""
    with patch('selenium.webdriver.Chrome', return_value=mock_selenium_driver):
        with patch('selenium.webdriver.support.ui.WebDriverWait', return_value=mock_selenium_wait):
            yield {
                'driver': mock_selenium_driver,
                'wait': mock_selenium_wait
            }


# ============================================================================
# HTTP Mocks
# ============================================================================

@pytest.fixture
def mock_requests_session():
    """Create a mock requests Session."""
    session = MagicMock()

    # Mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html><body>Mock Response</body></html>"
    mock_response.content = b"Mock Content"
    mock_response.json.return_value = {"status": "success"}
    mock_response.headers = {"Content-Type": "text/html"}

    session.get.return_value = mock_response
    session.post.return_value = mock_response

    return session


@pytest.fixture
def mock_http_response():
    """Create a mock HTTP response."""
    response = MagicMock()
    response.status_code = 200
    response.text = "<html><body>Mock Page</body></html>"
    response.content = b"Mock binary content"
    response.headers = {"Content-Type": "text/html; charset=utf-8"}
    response.json.return_value = {"data": "mock_data"}
    return response


# ============================================================================
# Configuration Fixtures
# ============================================================================

@pytest.fixture
def sample_config_dict() -> Dict[str, Any]:
    """Sample configuration dictionary for testing."""
    return {
        "storage_mode": "snapshot",
        "retention_days": 30,
        "cameras_directory": "cameras",
        "parallel_downloads": 5,
        "download_timeout": 60,
        "base_url": "https://dashboard.aivisual.ai",
        "enable_logging": True,
        "log_level": "INFO"
    }


@pytest.fixture
def sample_config_file(temp_dir: Path, sample_config_dict: Dict[str, Any]) -> Path:
    """Create a sample configuration JSON file."""
    import json
    config_path = temp_dir / "config.json"
    with open(config_path, 'w') as f:
        json.dump(sample_config_dict, f, indent=2)
    return config_path


# ============================================================================
# Camera Data Fixtures
# ============================================================================

@pytest.fixture
def sample_camera_metadata() -> Dict[str, Any]:
    """Sample camera metadata for testing."""
    return {
        "camera_id": "CAM_001",
        "store_name": "BK_Loja_Teste",
        "position": "P1",
        "url": "https://example.com/camera/CAM_001",
        "status": "active",
        "last_image": "2024-01-15T10:30:00Z"
    }


@pytest.fixture
def sample_camera_list() -> list:
    """Sample list of cameras for testing."""
    return [
        {"id": "CAM_001", "name": "BK_Loja_A", "position": "P1"},
        {"id": "CAM_002", "name": "BK_Loja_A", "position": "P2"},
        {"id": "CAM_003", "name": "BK_Loja_B", "position": "P1"},
        {"id": "CAM_004", "name": "BK_Loja_B", "position": "P2"},
        {"id": "CAM_005", "name": "BK_Loja_B", "position": "P3"},
    ]


@pytest.fixture
def sample_base64_image() -> str:
    """Sample base64-encoded image for testing."""
    # Minimal 1x1 red GIF
    return "R0lGODlhAQABAPAAAP8AAP///yH5BAAAAAAALAAAAAA"


# ============================================================================
# BeautifulSoup Fixtures
# ============================================================================

@pytest.fixture
def sample_html_page() -> str:
    """Sample HTML page for parsing tests."""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Test Page</title></head>
    <body>
        <div id="main-content">
            <form id="login-form" action="/login" method="post">
                <input type="text" name="username" id="username" />
                <input type="password" name="password" id="password" />
                <button type="submit">Login</button>
            </form>
            <div class="camera-list">
                <div class="camera" data-id="CAM_001">
                    <span class="camera-name">Camera 1</span>
                    <img src="data:image/jpeg;base64,/9j/4AAQ..." />
                </div>
                <div class="camera" data-id="CAM_002">
                    <span class="camera-name">Camera 2</span>
                    <img src="data:image/jpeg;base64,/9j/4AAQ..." />
                </div>
            </div>
        </div>
    </body>
    </html>
    """


@pytest.fixture
def mock_beautifulsoup(sample_html_page):
    """Create a BeautifulSoup object from sample HTML."""
    from bs4 import BeautifulSoup
    return BeautifulSoup(sample_html_page, 'html.parser')


# ============================================================================
# Machine Learning Fixtures
# ============================================================================

@pytest.fixture
def sample_feature_data():
    """Sample feature data for ML testing."""
    import numpy as np
    # Create sample data: 100 samples, 5 features
    return np.random.randn(100, 5)


@pytest.fixture
def sample_labeled_data():
    """Sample labeled dataset for ML testing."""
    import numpy as np
    X = np.random.randn(100, 5)
    y = np.random.randint(0, 2, 100)  # Binary labels
    return X, y


@pytest.fixture
def mock_isolation_forest():
    """Mock IsolationForest model."""
    model = MagicMock()
    model.fit.return_value = model
    model.predict.return_value = [1, -1, 1, 1]  # 1=normal, -1=anomaly
    model.score_samples.return_value = [0.5, -0.3, 0.6, 0.4]
    return model


# ============================================================================
# File System Fixtures
# ============================================================================

@pytest.fixture
def sample_camera_directory_structure(temp_dir: Path):
    """Create a sample camera directory structure."""
    stores = ["BK_Loja_A", "BK_Loja_B", "BK_Loja_C"]
    positions = ["P1", "P2", "P3"]

    for store in stores:
        store_dir = temp_dir / "cameras" / store
        store_dir.mkdir(parents=True)

        for position in positions:
            # Create sample image files
            image_name = f"{position}_{store}_20240115_103000.jpg"
            image_path = store_dir / image_name
            image_path.write_bytes(b"\xFF\xD8\xFF\xE0" + b"\x00" * 100)  # Minimal JPEG header

    return temp_dir / "cameras"


# ============================================================================
# Pytest Hooks
# ============================================================================

def pytest_configure(config):
    """Pytest configuration hook."""
    # Add custom markers
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection."""
    # Add marker to integration tests automatically
    for item in items:
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        if "test_selenium" in item.nodeid:
            item.add_marker(pytest.mark.selenium)


# ============================================================================
# Utility Functions for Tests
# ============================================================================

@pytest.fixture
def create_mock_file():
    """Factory fixture to create mock files."""
    def _create_file(path: Path, content: str = ""):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path
    return _create_file


@pytest.fixture
def assert_file_exists():
    """Helper to assert file existence."""
    def _assert(path: Path, should_exist: bool = True):
        if should_exist:
            assert path.exists(), f"File should exist: {path}"
        else:
            assert not path.exists(), f"File should not exist: {path}"
    return _assert
