import logging
import os
import json
from datetime import datetime, timedelta
import hashlib
import platform
import getpass


class SecurityManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.device_permissions = {}
        self.session_file = os.path.join(
            os.path.expanduser("~"), ".nodeflow", "permissions.json"
        )
        self._load_permissions()

    def _load_permissions(self):
        """Load saved device permissions"""
        try:
            os.makedirs(os.path.dirname(self.session_file), exist_ok=True)
            if os.path.exists(self.session_file):
                with open(self.session_file, "r") as f:
                    self.device_permissions = json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading permissions: {e}")
            self.device_permissions = {}

    def _save_permissions(self):
        """Save device permissions to file"""
        try:
            with open(self.session_file, "w") as f:
                json.dump(self.device_permissions, f)
        except Exception as e:
            self.logger.error(f"Error saving permissions: {e}")

    def get_system_info(self):
        """Get system identification info"""
        system_info = {
            "hostname": platform.node(),
            "platform": platform.system(),
            "username": getpass.getuser(),
            "machine_id": self._get_machine_id(),
        }
        return system_info

    def _get_machine_id(self):
        """Generate a unique machine identifier"""
        system_info = f"{platform.node()}-{platform.system()}-{getpass.getuser()}"
        return hashlib.sha256(system_info.encode()).hexdigest()

    def check_permission(self, device_type):
        """Check if device access is permitted"""
        if device_type not in self.device_permissions:
            return False

        permission = self.device_permissions[device_type]
        if not permission.get("granted", False):
            return False

        # Check if permission has expired
        expiry = permission.get("expiry")
        if expiry and datetime.fromisoformat(expiry) < datetime.now():
            return False

        return True

    def grant_permission(self, device_type, duration_hours=1):
        """Grant permission for device access"""
        self.device_permissions[device_type] = {
            "granted": True,
            "granted_at": datetime.now().isoformat(),
            "expiry": (datetime.now() + timedelta(hours=duration_hours)).isoformat(),
            "system_info": self.get_system_info(),
        }
        self._save_permissions()

    def revoke_permission(self, device_type):
        """Revoke device access permission"""
        if device_type in self.device_permissions:
            self.device_permissions[device_type]["granted"] = False
            self._save_permissions()

    def validate_command(self, command, device_type):
        """Validate if a command is allowed for the given device"""
        if not self.check_permission(device_type):
            return False

        valid_commands = {"start", "stop"}
        valid_devices = {"webcam", "microphone", "speaker"}

        return command in valid_commands and device_type in valid_devices
