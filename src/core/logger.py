import logging
import os
import sys
from typing import Optional

class Logger:
    """Global Log Management Class
    
    A log manager implemented using the singleton pattern, providing a unified log recording interface.
    This class can be used to record logs from any location in the application.
    """
    
    _instance: Optional['Logger'] = None
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls) -> 'Logger':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._setup_logger()
        return cls._instance
    
    @classmethod
    def get_instance(cls) -> 'Logger':
        """Gets the Logger singleton instance
        
        Returns:
            The Logger instance
        """
        if cls._instance is None:
            cls._instance = Logger()
        return cls._instance
    
    @classmethod
    def _setup_logger(cls):
        """Sets up the logger
        
        Configures the logger's output format, log level, and output file.
        """
        if cls._logger is None:
            cls._logger = logging.getLogger('TUNL.VolumeControl')
            cls._logger.setLevel(logging.INFO)
            
            # Get the log directory path
            if getattr(sys, 'frozen', False):
                # If it's a bundled executable
                base_path = os.path.join(os.path.dirname(sys.executable), 'logs')
            else:
                # If it's a development environment
                base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
            
            # Ensure the log directory exists
            try:
                os.makedirs(base_path, exist_ok=True)
                
                # Set the log file path
                log_file = os.path.join(base_path, 'plugin.log')
                
                # Create a file handler
                handler = logging.FileHandler(log_file, encoding='utf-8')
                handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
                cls._logger.addHandler(handler)
                
                # Add console output
                console_handler = logging.StreamHandler()
                console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
                cls._logger.addHandler(console_handler)
            except Exception as e:
                print(f"Failed to setup file handler: {e}")
                # If the file handler setup fails, at least ensure console output works correctly
                console_handler = logging.StreamHandler()
                console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
                cls._logger.addHandler(console_handler)
    
    @classmethod
    def get_logger(cls) -> logging.Logger:
        """Gets the logger instance
        
        Returns:
            The configured logger instance
        """
        if cls._logger is None:
            cls._setup_logger()
        return cls._logger
    
    @classmethod
    def info(cls, message: str):
        """Logs a message at INFO level
        
        Args:
            message: The log message
        """
        cls.get_instance().get_logger().info(message)
    
    @classmethod
    def error(cls, message: str):
        """Logs a message at ERROR level
        
        Args:
            message: The log message
        """
        cls.get_instance().get_logger().error(message)
    
    @classmethod
    def warning(cls, message: str):
        """Logs a message at WARNING level
        
        Args:
            message: The log message
        """
        cls.get_instance().get_logger().warning(message)
    
    @classmethod
    def debug(cls, message: str):
        """Logs a message at DEBUG level
        
        Args:
            message: The log message
        """
        cls.get_instance().get_logger().debug(message)