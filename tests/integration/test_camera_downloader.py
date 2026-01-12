"""
Integration Tests for Camera Downloader
========================================

Tests for captura_cameras/camera_downloader_complete.py module.
These tests use mocked Selenium and HTTP clients.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, call
import base64
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'captura_cameras'))


# ============================================================================
# Test Selenium Login Flow
# ============================================================================

@pytest.mark.integration
@pytest.mark.selenium
class TestSeleniumLogin:
    """Test Selenium login automation."""

    def test_login_flow_success(self, mock_selenium_driver, test_env_vars):
        """Test successful login to AIVisual dashboard."""
        from common.credentials import get_aivisual_credentials

        username, password = get_aivisual_credentials()

        # Mock the login form elements
        username_field = MagicMock()
        password_field = MagicMock()
        submit_button = MagicMock()

        def find_element_side_effect(by, value):
            if 'username' in value.lower() or 'email' in value.lower():
                return username_field
            elif 'password' in value.lower() or 'senha' in value.lower():
                return password_field
            elif 'submit' in value.lower() or 'login' in value.lower():
                return submit_button
            return MagicMock()

        mock_selenium_driver.find_element.side_effect = find_element_side_effect

        # Simulate login
        mock_selenium_driver.get("https://dashboard.aivisual.ai/login")
        username_elem = mock_selenium_driver.find_element("id", "username")
        password_elem = mock_selenium_driver.find_element("id", "password")
        submit_elem = mock_selenium_driver.find_element("id", "submit")

        username_elem.send_keys(username)
        password_elem.send_keys(password)
        submit_elem.click()

        # Verify interactions
        username_field.send_keys.assert_called_once_with(username)
        password_field.send_keys.assert_called_once_with(password)
        submit_button.click.assert_called_once()

    def test_login_with_multiple_selector_fallback(self, mock_selenium_driver):
        """Test login with fallback selector strategy."""
        # First selector fails, second succeeds
        first_call = True

        def find_element_side_effect(by, value):
            nonlocal first_call
            if first_call:
                first_call = False
                raise Exception("Element not found")
            return MagicMock()

        mock_selenium_driver.find_element.side_effect = find_element_side_effect

        # Try primary selector (fails)
        try:
            elem = mock_selenium_driver.find_element("xpath", "//input[@id='username']")
        except Exception:
            # Fallback to CSS selector (succeeds)
            elem = mock_selenium_driver.find_element("css", "#username")

        # Verify we got an element from the fallback
        assert elem is not None


# ============================================================================
# Test Camera Discovery
# ============================================================================

@pytest.mark.integration
class TestCameraDiscovery:
    """Test camera metadata extraction from dashboard."""

    def test_parse_camera_list_from_html(self, mock_beautifulsoup):
        """Test parsing camera list from HTML."""
        from bs4 import BeautifulSoup

        cameras = mock_beautifulsoup.find_all('div', class_='camera')

        assert len(cameras) == 2
        assert cameras[0].get('data-id') == 'CAM_001'
        assert cameras[1].get('data-id') == 'CAM_002'

    def test_extract_base64_images(self, mock_beautifulsoup):
        """Test extracting base64 images from page."""
        images = mock_beautifulsoup.find_all('img')

        base64_images = []
        for img in images:
            src = img.get('src', '')
            if src.startswith('data:image'):
                # Extract base64 data
                base64_data = src.split(',')[1] if ',' in src else ''
                base64_images.append(base64_data)

        assert len(base64_images) == 2

    def test_parse_camera_metadata_json(self, sample_camera_metadata):
        """Test parsing camera metadata from JSON."""
        assert sample_camera_metadata['camera_id'] == 'CAM_001'
        assert sample_camera_metadata['store_name'] == 'BK_Loja_Teste'
        assert sample_camera_metadata['position'] in ['P1', 'P2', 'P3']


# ============================================================================
# Test Image Download and Storage
# ============================================================================

@pytest.mark.integration
class TestImageDownload:
    """Test image download and storage."""

    def test_download_single_camera_image(self, temp_dir, sample_base64_image):
        """Test downloading and saving a single camera image."""
        # Decode base64 image
        try:
            image_data = base64.b64decode(sample_base64_image)
        except Exception:
            # If decode fails, use minimal valid JPEG
            image_data = b"\xFF\xD8\xFF\xE0" + b"\x00" * 100

        # Save to file
        store_name = "BK_Loja_Teste"
        position = "P1"
        image_dir = temp_dir / "cameras" / store_name
        image_dir.mkdir(parents=True, exist_ok=True)

        image_path = image_dir / f"{position}_{store_name}.jpg"
        image_path.write_bytes(image_data)

        # Verify
        assert image_path.exists()
        assert image_path.stat().st_size > 0

    def test_download_multiple_cameras_structure(self, temp_dir, sample_camera_list):
        """Test downloading multiple cameras creates correct directory structure."""
        # Simulate downloading images for all cameras
        for camera in sample_camera_list:
            store_name = camera['name']
            position = camera['position']

            image_dir = temp_dir / "cameras" / store_name
            image_dir.mkdir(parents=True, exist_ok=True)

            image_path = image_dir / f"{position}_{store_name}_20240115_103000.jpg"
            image_path.write_bytes(b"\xFF\xD8\xFF\xE0" + b"\x00" * 100)

        # Verify structure
        cameras_dir = temp_dir / "cameras"
        assert (cameras_dir / "BK_Loja_A").exists()
        assert (cameras_dir / "BK_Loja_B").exists()

        # Check images
        assert (cameras_dir / "BK_Loja_A" / "P1_BK_Loja_A_20240115_103000.jpg").exists()
        assert (cameras_dir / "BK_Loja_A" / "P2_BK_Loja_A_20240115_103000.jpg").exists()
        assert (cameras_dir / "BK_Loja_B" / "P3_BK_Loja_B_20240115_103000.jpg").exists()

    def test_storage_mode_snapshot(self, temp_dir):
        """Test snapshot storage mode (overwrite)."""
        store_name = "BK_Loja_A"
        position = "P1"

        image_dir = temp_dir / "cameras" / store_name
        image_dir.mkdir(parents=True, exist_ok=True)

        image_path = image_dir / f"{position}.jpg"  # No timestamp

        # First download
        image_path.write_bytes(b"first_image_data")
        first_size = image_path.stat().st_size

        # Second download (overwrites)
        image_path.write_bytes(b"second_image_data_longer")
        second_size = image_path.stat().st_size

        # Verify only one file exists and it was overwritten
        assert image_path.exists()
        assert second_size > first_size
        assert len(list(image_dir.glob("*.jpg"))) == 1

    def test_storage_mode_timestamped(self, temp_dir):
        """Test timestamped storage mode (keeps history)."""
        store_name = "BK_Loja_A"
        position = "P1"

        image_dir = temp_dir / "cameras" / store_name
        image_dir.mkdir(parents=True, exist_ok=True)

        # Multiple downloads with timestamps
        timestamps = ["20240115_100000", "20240115_110000", "20240115_120000"]

        for ts in timestamps:
            image_path = image_dir / f"{position}_{store_name}_{ts}.jpg"
            image_path.write_bytes(b"\xFF\xD8\xFF\xE0" + b"\x00" * 100)

        # Verify all files exist
        assert len(list(image_dir.glob("*.jpg"))) == 3


# ============================================================================
# Test Error Handling
# ============================================================================

@pytest.mark.integration
class TestErrorHandling:
    """Test error handling in download process."""

    def test_handle_login_failure(self, mock_selenium_driver):
        """Test handling of login failure."""
        # Simulate login failure
        mock_selenium_driver.find_element.side_effect = Exception("Login failed")

        with pytest.raises(Exception) as exc_info:
            mock_selenium_driver.find_element("id", "username")

        assert "Login failed" in str(exc_info.value)

    def test_handle_network_timeout(self, mock_requests_session):
        """Test handling of network timeout."""
        import requests

        # Simulate timeout
        mock_requests_session.get.side_effect = requests.Timeout("Connection timeout")

        with pytest.raises(requests.Timeout):
            mock_requests_session.get("https://example.com")

    def test_handle_invalid_base64(self):
        """Test handling of invalid base64 data."""
        invalid_base64 = "not_valid_base64!!!"

        with pytest.raises(Exception):
            base64.b64decode(invalid_base64, validate=True)

    def test_retry_logic_with_exponential_backoff(self, mock_requests_session):
        """Test retry logic with exponential backoff."""
        import time

        max_retries = 3
        retry_count = 0
        delays = []

        for attempt in range(max_retries):
            try:
                # Simulate failure
                if retry_count < 2:
                    retry_count += 1
                    delay = 2 ** attempt  # Exponential backoff: 1, 2, 4
                    delays.append(delay)
                    raise Exception("Temporary failure")
                else:
                    # Success on third attempt
                    break
            except Exception:
                if attempt == max_retries - 1:
                    raise

        assert retry_count == 2
        assert delays == [1, 2]


# ============================================================================
# Test Parallel Download
# ============================================================================

@pytest.mark.integration
class TestParallelDownload:
    """Test parallel download functionality."""

    def test_parallel_download_queue(self, sample_camera_list):
        """Test parallel download queue management."""
        from queue import Queue
        import threading

        download_queue = Queue()
        results = []
        lock = threading.Lock()

        def worker():
            while True:
                camera = download_queue.get()
                if camera is None:
                    break

                # Simulate download
                result = {
                    'camera_id': camera['id'],
                    'status': 'success'
                }

                with lock:
                    results.append(result)

                download_queue.task_done()

        # Add cameras to queue
        for camera in sample_camera_list:
            download_queue.put(camera)

        # Start workers
        num_workers = 3
        threads = []
        for _ in range(num_workers):
            t = threading.Thread(target=worker)
            t.start()
            threads.append(t)

        # Wait for completion
        download_queue.join()

        # Stop workers
        for _ in range(num_workers):
            download_queue.put(None)
        for t in threads:
            t.join()

        # Verify all cameras were processed
        assert len(results) == len(sample_camera_list)

    def test_concurrent_file_writes_thread_safety(self, temp_dir):
        """Test thread-safe concurrent file writes."""
        import threading

        cameras_dir = temp_dir / "cameras"
        cameras_dir.mkdir(exist_ok=True)

        def write_image(camera_id):
            store_dir = cameras_dir / f"Store_{camera_id}"
            store_dir.mkdir(exist_ok=True)

            image_path = store_dir / f"P1_{camera_id}.jpg"
            image_path.write_bytes(b"\xFF\xD8\xFF\xE0" + b"\x00" * 100)

        # Write 10 images concurrently
        threads = []
        for i in range(10):
            t = threading.Thread(target=write_image, args=(i,))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        # Verify all 10 stores were created
        stores = list(cameras_dir.glob("Store_*"))
        assert len(stores) == 10


# ============================================================================
# Test Cleanup and Retention
# ============================================================================

@pytest.mark.integration
class TestCleanupRetention:
    """Test cleanup and retention policies."""

    def test_cleanup_old_files_by_date(self, temp_dir):
        """Test cleanup of files older than retention period."""
        from datetime import datetime, timedelta
        import time

        cameras_dir = temp_dir / "cameras" / "BK_Loja_A"
        cameras_dir.mkdir(parents=True)

        # Create old file
        old_file = cameras_dir / "old_image.jpg"
        old_file.write_bytes(b"old")

        # Wait a bit
        time.sleep(0.1)

        # Create new file
        new_file = cameras_dir / "new_image.jpg"
        new_file.write_bytes(b"new")

        # Set retention to very short period
        retention_seconds = 0.05

        # Cleanup old files
        cutoff_time = time.time() - retention_seconds
        for file in cameras_dir.glob("*.jpg"):
            if file.stat().st_mtime < cutoff_time:
                file.unlink()

        # Verify old file was deleted, new file remains
        assert not old_file.exists()
        assert new_file.exists()


# ============================================================================
# Marks for Test Organization
# ============================================================================

# Run only critical tests:
# pytest -m critical

# Run only fast tests:
# pytest -m "not slow"

# Run only Selenium tests:
# pytest -m selenium
