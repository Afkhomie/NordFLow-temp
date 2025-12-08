"""
NodeFlow Application Factory
Main entry point for the application
"""

import logging
from pathlib import Path


def create_app():
    """Create and configure the Flask/Aiohttp application"""
    logger = logging.getLogger(__name__)
    logger.info("Creating NodeFlow application")
    
    # Setup logging
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    return {
        "version": "1.0.0",
        "name": "NodeFlow",
        "description": "Real-time audio/video streaming application",
    }


if __name__ == "__main__":
    app = create_app()
    print(f"NodeFlow {app['version']} - {app['description']}")
