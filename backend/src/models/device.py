from enum import Enum

class DeviceType(Enum):
    WEBCAM = "webcam"
    MICROPHONE = "microphone"
    SPEAKER = "speaker"

class DeviceStatus(Enum):
    INACTIVE = "inactive"
    ACTIVE = "active"
    ERROR = "error"

class Device:
    def __init__(self, device_type: DeviceType):
        self.device_type = device_type
        self.status = DeviceStatus.INACTIVE
        self.error_message = None
        
    def activate(self):
        """Activate the device"""
        self.status = DeviceStatus.ACTIVE
        self.error_message = None
        
    def deactivate(self):
        """Deactivate the device"""
        self.status = DeviceStatus.INACTIVE
        self.error_message = None
        
    def set_error(self, message: str):
        """Set device to error state with message"""
        self.status = DeviceStatus.ERROR
        self.error_message = message
        
    @property
    def is_active(self):
        """Check if device is currently active"""
        return self.status == DeviceStatus.ACTIVE
        
    def to_dict(self):
        """Convert device state to dictionary"""
        return {
            'type': self.device_type.value,
            'status': self.status.value,
            'error_message': self.error_message
        }
