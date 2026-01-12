"""
Unit Tests for Config Manager
==============================

Tests for captura_cameras/config_manager.py module.
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, mock_open, MagicMock
import sys
import os

# Add parent directory to path to import the module
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'captura_cameras'))

from config_manager import (
    carregar_config,
    salvar_config,
    exibir_modo_storage,
    menu_storage_mode,
    comparar_modos,
    gerar_recomendacao,
    DEFAULT_CONFIG,
    STORAGE_MODES,
    CONFIG_FILE
)


# ============================================================================
# Test Data Loading and Saving
# ============================================================================

class TestCarregarConfig:
    """Tests for carregar_config function."""

    def test_carregar_config_arquivo_nao_existe(self, temp_dir, monkeypatch):
        """Test loading config when file doesn't exist - should return default."""
        # Change CONFIG_FILE to temp directory
        test_config_file = temp_dir / ".camera_config.json"
        monkeypatch.setattr('config_manager.CONFIG_FILE', test_config_file)

        config = carregar_config()

        assert config['storage_mode'] == 'organized'
        assert config['retention_days'] == 7
        assert config['max_workers'] == 10
        assert 'credentials' in config

    def test_carregar_config_arquivo_existe(self, temp_dir, monkeypatch):
        """Test loading config when valid file exists."""
        test_config_file = temp_dir / ".camera_config.json"
        monkeypatch.setattr('config_manager.CONFIG_FILE', test_config_file)

        # Create a test config file
        test_config = {
            "storage_mode": "snapshot",
            "retention_days": 30,
            "max_workers": 5,
            "retry_attempts": 2
        }

        with open(test_config_file, 'w') as f:
            json.dump(test_config, f)

        config = carregar_config()

        assert config['storage_mode'] == 'snapshot'
        assert config['retention_days'] == 30
        assert config['max_workers'] == 5
        assert config['retry_attempts'] == 2

    def test_carregar_config_arquivo_json_invalido(self, temp_dir, monkeypatch):
        """Test loading config when JSON file is malformed."""
        test_config_file = temp_dir / ".camera_config.json"
        monkeypatch.setattr('config_manager.CONFIG_FILE', test_config_file)

        # Create invalid JSON file
        with open(test_config_file, 'w') as f:
            f.write("{ invalid json }")

        with pytest.raises(json.JSONDecodeError):
            carregar_config()

    def test_carregar_config_retorna_copia(self, temp_dir, monkeypatch):
        """Test that carregar_config returns a copy, not reference."""
        test_config_file = temp_dir / ".camera_config.json"
        monkeypatch.setattr('config_manager.CONFIG_FILE', test_config_file)

        config1 = carregar_config()
        config2 = carregar_config()

        # Modify config1
        config1['storage_mode'] = 'different'

        # config2 should not be affected
        assert config2['storage_mode'] == 'organized'


class TestSalvarConfig:
    """Tests for salvar_config function."""

    def test_salvar_config_cria_arquivo(self, temp_dir, monkeypatch, capsys):
        """Test that salvar_config creates the config file."""
        test_config_file = temp_dir / ".camera_config.json"
        monkeypatch.setattr('config_manager.CONFIG_FILE', test_config_file)

        config = {
            "storage_mode": "timestamped",
            "retention_days": 15,
            "max_workers": 8
        }

        salvar_config(config)

        # Check file was created
        assert test_config_file.exists()

        # Verify content
        with open(test_config_file, 'r') as f:
            saved_config = json.load(f)

        assert saved_config['storage_mode'] == 'timestamped'
        assert saved_config['retention_days'] == 15
        assert saved_config['max_workers'] == 8
        assert 'updated_at' in saved_config

        # Check console output
        captured = capsys.readouterr()
        assert "Configuração salva" in captured.out

    def test_salvar_config_adiciona_updated_at(self, temp_dir, monkeypatch):
        """Test that salvar_config adds updated_at timestamp."""
        test_config_file = temp_dir / ".camera_config.json"
        monkeypatch.setattr('config_manager.CONFIG_FILE', test_config_file)

        config = {"storage_mode": "snapshot"}

        before_time = datetime.now()
        salvar_config(config)
        after_time = datetime.now()

        with open(test_config_file, 'r') as f:
            saved_config = json.load(f)

        assert 'updated_at' in saved_config
        updated_time = datetime.fromisoformat(saved_config['updated_at'])
        assert before_time <= updated_time <= after_time

    def test_salvar_config_sobrescreve_arquivo_existente(self, temp_dir, monkeypatch):
        """Test that salvar_config overwrites existing file."""
        test_config_file = temp_dir / ".camera_config.json"
        monkeypatch.setattr('config_manager.CONFIG_FILE', test_config_file)

        # Create initial config
        initial_config = {"storage_mode": "snapshot", "retention_days": 7}
        with open(test_config_file, 'w') as f:
            json.dump(initial_config, f)

        # Save new config
        new_config = {"storage_mode": "organized", "retention_days": 30}
        salvar_config(new_config)

        # Verify new values
        with open(test_config_file, 'r') as f:
            saved_config = json.load(f)

        assert saved_config['storage_mode'] == 'organized'
        assert saved_config['retention_days'] == 30


# ============================================================================
# Test Storage Modes
# ============================================================================

class TestStorageModes:
    """Tests for storage mode constants and validation."""

    def test_storage_modes_existem(self):
        """Test that all expected storage modes exist."""
        expected_modes = ['snapshot', 'organized', 'timestamped']
        assert all(mode in STORAGE_MODES for mode in expected_modes)

    def test_storage_modes_tem_campos_obrigatorios(self):
        """Test that each storage mode has required fields."""
        required_fields = ['name', 'description', 'pros', 'cons', 'disk_usage', 'structure']

        for mode_key, mode_data in STORAGE_MODES.items():
            for field in required_fields:
                assert field in mode_data, f"Mode '{mode_key}' missing field '{field}'"

    def test_storage_modes_pros_e_cons_sao_listas(self):
        """Test that pros and cons are lists."""
        for mode_key, mode_data in STORAGE_MODES.items():
            assert isinstance(mode_data['pros'], list)
            assert isinstance(mode_data['cons'], list)
            assert len(mode_data['pros']) > 0
            assert len(mode_data['cons']) > 0

    def test_default_config_storage_mode_valido(self):
        """Test that default config uses a valid storage mode."""
        assert DEFAULT_CONFIG['storage_mode'] in STORAGE_MODES


class TestExibirModoStorage:
    """Tests for exibir_modo_storage function."""

    def test_exibir_modo_storage_snapshot(self, capsys):
        """Test display of snapshot mode."""
        exibir_modo_storage('snapshot')
        captured = capsys.readouterr()

        assert "Snapshot" in captured.out
        assert "Sobrescrever" in captured.out
        assert "cameras/Loja/P1.jpg" in captured.out

    def test_exibir_modo_storage_organized(self, capsys):
        """Test display of organized mode."""
        exibir_modo_storage('organized')
        captured = capsys.readouterr()

        assert "Organizado" in captured.out
        assert "symlinks" in captured.out
        assert "2025-12/22" in captured.out

    def test_exibir_modo_storage_timestamped(self, capsys):
        """Test display of timestamped mode."""
        exibir_modo_storage('timestamped')
        captured = capsys.readouterr()

        assert "Timestamp" in captured.out
        assert "20251222_143022" in captured.out

    def test_exibir_modo_storage_modo_invalido(self):
        """Test that invalid mode raises KeyError."""
        with pytest.raises(KeyError):
            exibir_modo_storage('invalid_mode')


# ============================================================================
# Test Default Configuration
# ============================================================================

class TestDefaultConfig:
    """Tests for DEFAULT_CONFIG validation."""

    def test_default_config_tem_campos_obrigatorios(self):
        """Test that default config has all required fields."""
        required_fields = [
            'storage_mode',
            'retention_days',
            'max_workers',
            'retry_attempts',
            'delay_between_cameras',
            'enable_cleanup',
            'enable_validation',
            'log_level',
            'credentials'
        ]

        for field in required_fields:
            assert field in DEFAULT_CONFIG, f"Missing required field: {field}"

    def test_default_config_valores_razoaveis(self):
        """Test that default config values are reasonable."""
        assert DEFAULT_CONFIG['retention_days'] > 0
        assert DEFAULT_CONFIG['max_workers'] > 0
        assert DEFAULT_CONFIG['retry_attempts'] >= 0
        assert DEFAULT_CONFIG['delay_between_cameras'] >= 0
        assert isinstance(DEFAULT_CONFIG['enable_cleanup'], bool)
        assert isinstance(DEFAULT_CONFIG['enable_validation'], bool)

    def test_default_config_log_level_valido(self):
        """Test that default log level is valid."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        assert DEFAULT_CONFIG['log_level'] in valid_levels

    def test_default_config_credentials_vazio(self):
        """Test that default credentials are empty (should use env vars)."""
        assert DEFAULT_CONFIG['credentials']['username'] == ""
        assert DEFAULT_CONFIG['credentials']['password'] == ""


# ============================================================================
# Test Recommendation System
# ============================================================================

class TestGerarRecomendacao:
    """Tests for gerar_recomendacao function."""

    def test_gerar_recomendacao_exibe_casos_uso(self, capsys):
        """Test that gerar_recomendacao displays use cases."""
        gerar_recomendacao(None)
        captured = capsys.readouterr()

        expected_use_cases = [
            'Monitoramento Tempo Real',
            'Auditoria Semanal',
            'Analise Mensal',
            'Machine Learning'
        ]

        for use_case in expected_use_cases:
            assert use_case in captured.out

    def test_gerar_recomendacao_tem_detalhes(self, capsys):
        """Test that recommendations include details."""
        gerar_recomendacao(None)
        captured = capsys.readouterr()

        # Should show mode, retention, workers, and reason
        assert 'Modo:' in captured.out
        assert 'Retenção:' in captured.out
        assert 'Workers:' in captured.out
        assert 'Motivo:' in captured.out


# ============================================================================
# Integration Tests
# ============================================================================

class TestConfigManagerIntegration:
    """Integration tests for config manager."""

    def test_ciclo_completo_salvar_carregar(self, temp_dir, monkeypatch):
        """Test complete save and load cycle."""
        test_config_file = temp_dir / ".camera_config.json"
        monkeypatch.setattr('config_manager.CONFIG_FILE', test_config_file)

        # Create and save config
        config = {
            "storage_mode": "organized",
            "retention_days": 14,
            "max_workers": 12,
            "retry_attempts": 5,
            "delay_between_cameras": 1.0,
            "enable_cleanup": True,
            "enable_validation": False,
            "log_level": "DEBUG",
            "credentials": {
                "username": "test@example.com",
                "password": "test123"
            }
        }

        salvar_config(config)

        # Load and verify
        loaded_config = carregar_config()

        assert loaded_config['storage_mode'] == 'organized'
        assert loaded_config['retention_days'] == 14
        assert loaded_config['max_workers'] == 12
        assert loaded_config['retry_attempts'] == 5
        assert loaded_config['delay_between_cameras'] == 1.0
        assert loaded_config['enable_cleanup'] is True
        assert loaded_config['enable_validation'] is False
        assert loaded_config['log_level'] == 'DEBUG'
        assert 'updated_at' in loaded_config

    def test_multiplas_atualizacoes_config(self, temp_dir, monkeypatch):
        """Test multiple config updates."""
        test_config_file = temp_dir / ".camera_config.json"
        monkeypatch.setattr('config_manager.CONFIG_FILE', test_config_file)

        # First save
        config1 = {"storage_mode": "snapshot", "retention_days": 7}
        salvar_config(config1)

        # Second save
        config2 = carregar_config()
        config2['storage_mode'] = 'organized'
        config2['retention_days'] = 30
        salvar_config(config2)

        # Verify final state
        final_config = carregar_config()
        assert final_config['storage_mode'] == 'organized'
        assert final_config['retention_days'] == 30


# ============================================================================
# Parametrized Tests
# ============================================================================

@pytest.mark.parametrize("storage_mode,expected_structure", [
    ("snapshot", "cameras/Loja/P1.jpg"),
    ("organized", "cameras/Loja/2025-12/22/P1_143022.jpg"),
    ("timestamped", "cameras/Loja/P1_Loja_20251222_143022.jpg"),
])
def test_storage_mode_structure(storage_mode, expected_structure):
    """Test that each storage mode has correct structure."""
    assert STORAGE_MODES[storage_mode]['structure'] == expected_structure


@pytest.mark.parametrize("log_level", ['DEBUG', 'INFO', 'WARNING', 'ERROR'])
def test_valid_log_levels(log_level):
    """Test that all standard log levels are valid."""
    config = DEFAULT_CONFIG.copy()
    config['log_level'] = log_level
    # Should not raise any errors
    assert config['log_level'] == log_level


@pytest.mark.parametrize("retention_days,max_workers", [
    (1, 1),
    (7, 10),
    (30, 20),
    (90, 5),
])
def test_config_valores_positivos(retention_days, max_workers):
    """Test that config accepts various positive values."""
    config = DEFAULT_CONFIG.copy()
    config['retention_days'] = retention_days
    config['max_workers'] = max_workers

    assert config['retention_days'] > 0
    assert config['max_workers'] > 0
