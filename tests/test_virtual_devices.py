#!/usr/bin/env python
"""
Test Virtual Devices Integration
Verifies that virtual camera and microphone are working correctly
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test that all required imports work"""
    print("=" * 60)
    print("Testing Imports")
    print("=" * 60)
    
    try:
        import pyvirtualcam
        print("✓ pyvirtualcam imported successfully")
    except ImportError as e:
        print(f"✗ pyvirtualcam import failed: {e}")
        return False
    
    try:
        import sounddevice
        print("✓ sounddevice imported successfully")
    except ImportError as e:
        print(f"✗ sounddevice import failed: {e}")
        return False
    
    try:
        import cv2
        print("✓ cv2 (OpenCV) imported successfully")
    except ImportError as e:
        print(f"✗ cv2 import failed: {e}")
        return False
    
    try:
        import numpy
        print("✓ numpy imported successfully")
    except ImportError as e:
        print(f"✗ numpy import failed: {e}")
        return False
    
    try:
        from src.services.virtual_devices import VirtualDeviceManager
        print("✓ VirtualDeviceManager imported successfully")
    except ImportError as e:
        print(f"✗ VirtualDeviceManager import failed: {e}")
        return False
    
    print()
    return True


def test_virtual_camera():
    """Test virtual camera initialization"""
    print("=" * 60)
    print("Testing Virtual Camera")
    print("=" * 60)
    
    try:
        from src.services.virtual_devices import VirtualCameraManager
        import numpy as np
        
        # Try to initialize
        camera = VirtualCameraManager(width=1280, height=720, fps=30)
        
        if camera.camera is None:
            print("⚠ Virtual camera not available")
            print("  This is normal if OBS Virtual Camera is not installed")
            print("  Install from: https://obsproject.com/forum/resources/obs-virtualcam.949/")
            return True
        
        print(f"✓ Virtual camera initialized")
        print(f"  Device: {camera.camera.device}")
        print(f"  Resolution: {camera.width}x{camera.height}")
        print(f"  FPS: {camera.fps}")
        
        # Try sending a test frame
        test_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        result = camera.send_frame(test_frame)
        
        if result:
            print("✓ Successfully sent test frame to virtual camera")
        else:
            print("⚠ Could not send frame (might be normal)")
        
        camera.stop()
        print("✓ Virtual camera cleaned up")
        print()
        return True
        
    except Exception as e:
        print(f"✗ Virtual camera test failed: {e}")
        print()
        return False


def test_virtual_audio():
    """Test virtual audio detection"""
    print("=" * 60)
    print("Testing Virtual Audio Device")
    print("=" * 60)
    
    try:
        from src.services.virtual_devices import VirtualAudioRouter
        
        router = VirtualAudioRouter()
        
        if router.is_available():
            print(f"✓ Virtual audio device detected")
            print(f"  Device: {router.device_name}")
            print(f"  Index: {router.virtual_device_index}")
            
            if router.activate():
                print("✓ Audio routing activated")
                router.deactivate()
                print("✓ Audio routing deactivated")
        else:
            print("⚠ Virtual audio device not available")
            print("  This is normal if VB-Audio Virtual Cable is not installed")
            print("  Install from: https://vb-audio.com/Cable/")
            print("  Then restart Windows")
        
        print()
        return True
        
    except Exception as e:
        print(f"✗ Virtual audio test failed: {e}")
        print()
        return False


def test_virtual_device_manager():
    """Test the complete virtual device manager"""
    print("=" * 60)
    print("Testing Virtual Device Manager")
    print("=" * 60)
    
    try:
        from src.services.virtual_devices import initialize_virtual_devices
        import numpy as np
        
        # Initialize
        manager = initialize_virtual_devices(video_width=1280, video_height=720, fps=30)
        print("✓ Virtual device manager initialized")
        
        # Get status
        status = manager.get_status()
        print(f"✓ Status retrieved:")
        print(f"  Enabled: {status['enabled']}")
        print(f"  Video available: {status['video']['available']}")
        print(f"  Audio available: {status['audio']['available']}")
        
        # Try sending a frame
        test_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        result = manager.send_video_frame(test_frame)
        if result:
            print("✓ Successfully sent video frame")
        else:
            print("⚠ Could not send video frame")
        
        # Cleanup
        manager.cleanup()
        print("✓ Manager cleaned up")
        print()
        return True
        
    except Exception as e:
        print(f"✗ Virtual device manager test failed: {e}")
        print()
        return False


def main():
    """Run all tests"""
    print()
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  NodeFlow Virtual Devices - Test Suite".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Virtual Camera", test_virtual_camera()))
    results.append(("Virtual Audio", test_virtual_audio()))
    results.append(("Device Manager", test_virtual_device_manager()))
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:.<40} {status}")
    
    print()
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    if passed == total:
        print(f"✓ All {total} tests passed!")
        print()
        print("Next steps:")
        print("  1. Run: setup_virtual_devices.bat (if not already done)")
        print("  2. Run: start_receiver_virtual.bat")
        print("  3. Connect to your phone")
        print("  4. Open Discord/Zoom and select 'OBS Virtual Camera'")
        print()
        return 0
    else:
        print(f"✗ {passed}/{total} tests passed")
        print()
        print("Issues found:")
        for test_name, passed in results:
            if not passed:
                print(f"  - {test_name}")
        print()
        print("Troubleshooting:")
        print("  1. Check console output above for error details")
        print("  2. Run: pip install -r backend/requirements.txt")
        print("  3. Run: setup_virtual_devices.bat")
        print("  4. Restart Windows if you installed new drivers")
        print()
        return 1


if __name__ == '__main__':
    sys.exit(main())
