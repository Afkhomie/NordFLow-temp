from setuptools import setup, find_packages

setup(
    name="nodeflow",
    version="1.0.0",
    author="Afkhomie",
    description="Real-time audio/video streaming with WebSocket support",
    packages=find_packages(),
    install_requires=[
        'aiohttp>=3.8.0',
        'cryptography>=3.4.7',
        'opencv-python>=4.8.0',
        'pillow>=10.0.0',
        'pyaudio>=0.2.13',
        'websockets>=10.0',
        'numpy>=2.2.0',
        'sounddevice>=0.5.3'
    ],
    entry_points={
        'console_scripts': [
            'nodeflow-server=backend.src.main:main',
            'nodeflow-gui=backend.src.gui:main',
        ],
    },
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
