#!/usr/bin/env python3
"""
Quick system test for NodeFlow
"""
import sys
import subprocess
import time
import os
from pathlib import Path

def test_dependencies():
    """Test that all required dependencies are installed"""
    print("Testing dependencies...")
    required = [
        'aiohttp',
        'websockets',
        'websocket',  # websocket-client
        'PyQt6',
        'cv2',  # opencv-python
        'cryptography',
        'OpenSSL',
        'pytest'
    ]
    
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
            print(f"  OK  {pkg}")
        except ImportError:
            print(f"  BAD {pkg} (MISSING)")
            missing.append(pkg)
    
    if missing:
        print(f"\nMissing: {', '.join(missing)}")
        return False
    
    print("\nAll dependencies OK!\n")
    return True


def test_backend_files():
    """Test that backend files exist"""
    print("Testing backend files...")
    backend_path = Path(__file__).parent / 'backend' / 'src'
    
    required_files = [
        'run_dev.py',
        'receiver.py',
        'streaming/server_new.py',
        'templates/index.html',
        'server.crt',
        'server.key'
    ]
    
    all_exist = True
    for file in required_files:
        file_path = backend_path / file
        exists = file_path.exists()
        status = "OK " if exists else "BAD"
        print(f"  {status} {file}")
        if not exists:
            all_exist = False
    
    print()
    return all_exist


def test_frontend():
    """Test frontend files"""
    print("Testing frontend files...")
    frontend_path = Path(__file__).parent / 'frontend'
    
    required_files = [
        'src/components/App.jsx',
        'package.json'
    ]
    
    all_exist = True
    for file in required_files:
        file_path = frontend_path / file
        exists = file_path.exists()
        status = "OK " if exists else "BAD"
        print(f"  {status} {file}")
        if not exists:
            all_exist = False
    
    print()
    return all_exist


def test_receiver_gui():
    """Quick test that receiver GUI can be instantiated"""
    print("Testing receiver GUI import...")
    try:
        os.chdir(str(Path(__file__).parent / 'backend' / 'src'))
        sys.path.insert(0, str(Path(__file__).parent / 'backend' / 'src'))
        
        from receiver import ReceiverGUI
        print("✓ Receiver GUI imports successfully")
        print()
        return True
    except Exception as e:
        print(f"✗ Receiver GUI import failed: {e}")
        print()
        return False


def main():
    """Run all tests"""
    print("=" * 50)
    print("NodeFlow System Test")
    print("=" * 50)
    print()
    
    results = {
        'Dependencies': test_dependencies(),
        'Backend Files': test_backend_files(),
        'Frontend Files': test_frontend(),
        'Receiver GUI': test_receiver_gui()
    }
    
    print("=" * 50)
    print("Results")
    print("=" * 50)
    
    all_passed = True
    for test, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {status}: {test}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("All tests PASSED!")
        print("\nTo start the system:")
        print("1. Run: python backend/src/run_dev.py")
        print("2. Open https://<your-ip>:5000 on your phone")
        print("3. Run: python backend/src/receiver.py")
    else:
        print("Some tests FAILED. Please fix the issues above.")
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
