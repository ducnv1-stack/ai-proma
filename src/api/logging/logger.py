import logging
import sys
from datetime import datetime
import os
from typing import Optional

class ProjectLogger:
    """
    Singleton logger configuration for console output only
    """
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ProjectLogger, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._setup_logger()
            ProjectLogger._initialized = True
    
    def _setup_logger(self):
        """Setup the main project logger for console only"""
        # Configure root logger
        self.logger = logging.getLogger("MyProject")
        self.logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Create console formatter with detailed information
        self.console_formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(filename)s:%(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Setup console handler only
        self._setup_console_handler()
    
    def _setup_console_handler(self):
        """Setup console logging"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.console_formatter)
        console_handler.setLevel(logging.DEBUG)  # Show all levels in console
        self.logger.addHandler(console_handler)
    
    def get_logger(self, name: str = None):
        """Get a logger instance for a specific module"""
        if name:
            return logging.getLogger(f"MyProject.{name}")
        return self.logger
    
    def set_level(self, level: str):
        """Set logging level for the entire project"""
        self.logger.setLevel(getattr(logging, level.upper()))
        # Also update the console handler level
        for handler in self.logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.setLevel(getattr(logging, level.upper()))
    
    def log_startup_info(self):
        """Log application startup information"""
        self.logger.info("="*60)
        self.logger.info("APPLICATION STARTUP")
        self.logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"Python Version: {sys.version}")
        self.logger.info(f"Working Directory: {os.getcwd()}")
        self.logger.info(f"Process ID: {os.getpid()}")
        self.logger.info("="*60)


# Convenience function to get logger
def get_logger(module_name: str = None):
    """
    Get a logger instance for a module
    
    Usage:
        logger = get_logger(__name__)
        logger = get_logger("database")
    """
    project_logger = ProjectLogger()
    if module_name:
        # Extract just the module name from full path
        clean_name = module_name.split('.')[-1] if '.' in module_name else module_name
        return project_logger.get_logger(clean_name)
    return project_logger.get_logger()

