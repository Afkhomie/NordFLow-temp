import pytest
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.config import Config, ConfigManager, NetworkConfig, StreamConfig
from models.device import Device, DeviceType, DeviceStatus
from utils.security import SecurityManager


class TestConfig:
    def test_default_config(self):
        config = Config()
        assert config.network.host == "0.0.0.0"
        assert config.network.port == 5000
        assert config.stream.video_width == 640

    def test_network_config(self):
        net = NetworkConfig(host="127.0.0.1", port=8000)
        assert net.host == "127.0.0.1"
        assert net.port == 8000


class TestDevice:
    def test_device_creation(self):
        device = Device(DeviceType.WEBCAM)
        assert device.device_type == DeviceType.WEBCAM
        assert device.status == DeviceStatus.INACTIVE

    def test_device_activation(self):
        device = Device(DeviceType.MICROPHONE)
        device.activate()
        assert device.is_active
        assert device.status == DeviceStatus.ACTIVE

    def test_device_error(self):
        device = Device(DeviceType.SPEAKER)
        device.set_error("Test error")
        assert device.status == DeviceStatus.ERROR
        assert device.error_message == "Test error"

    def test_device_to_dict(self):
        device = Device(DeviceType.WEBCAM)
        device.activate()
        result = device.to_dict()
        assert result['type'] == 'webcam'
        assert result['status'] == 'active'


class TestSecurityManager:
    def test_security_manager_init(self):
        manager = SecurityManager()
        assert isinstance(manager.device_permissions, dict)

    def test_system_info(self):
        manager = SecurityManager()
        info = manager.get_system_info()
        assert 'hostname' in info
        assert 'platform' in info
        assert 'username' in info
        assert 'machine_id' in info

    def test_permission_grant_and_check(self):
        manager = SecurityManager()
        manager.grant_permission('webcam', duration_hours=1)
        assert manager.check_permission('webcam')

    def test_permission_revoke(self):
        manager = SecurityManager()
        manager.grant_permission('microphone', duration_hours=1)
        manager.revoke_permission('microphone')
        assert not manager.check_permission('microphone')

    def test_validate_command(self):
        manager = SecurityManager()
        manager.grant_permission('webcam', duration_hours=1)
        assert manager.validate_command('start', 'webcam')
        assert manager.validate_command('stop', 'webcam')
        assert not manager.validate_command('invalid', 'webcam')
        assert not manager.validate_command('start', 'invalid_device')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
